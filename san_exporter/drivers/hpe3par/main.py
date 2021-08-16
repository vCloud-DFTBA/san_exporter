#
#    Copyright (C) 2021 Viettel Networks
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#

import logging
from time import sleep, time
import json

import requests
from hpe3parclient import version
from hpe3parclient import exceptions as hpeexceptions

from san_exporter.drivers.hpe3par.system_report import HPE3ParClientCustom

from san_exporter.utils.utils import cache_data

from san_exporter.drivers import base_driver
from san_exporter.drivers.hpe3par import prometheus_metrics

MIN_CLIENT_VERSION = '4.2.0'


class HPE3ParExporter(base_driver.ExporterDriver):

    def __init__(self, config=None, interval=10):
        # TODO: check missing configs here
        super().__init__(config, interval)
        self.hpe3par_api_url = config['hpe3par_api_url']
        self.hpe3par_username = config['hpe3par_username']
        self.hpe3par_password = config['hpe3par_password']
        self.backend_name = config['name']
        self.san_ssh_ip = config['san_ssh_ip']
        self.san_ssh_user = config['san_ssh_user']
        self.san_ssh_pass = config['san_ssh_pass']
        self.san_ssh_port = config['san_ssh_port']

    def _create_client(self):
        cl = HPE3ParClientCustom(self.hpe3par_api_url)
        cl.setSSHOptions(self.san_ssh_ip, self.san_ssh_user, self.san_ssh_pass, self.san_ssh_port)
        client_version = version

        if client_version < MIN_CLIENT_VERSION:
            ex_msg = ('Invalid hpe3parclient version found (%(found)s). '
                      'Version %(minimum)s or greater required. Run "pip'
                      ' install --upgrade python-3parclient" to upgrade'
                      ' the hpe3parclient.'
                      % {'found': client_version,
                         'minimum': MIN_CLIENT_VERSION})
            logging.error(ex_msg)
            # TODO: implement raise the exception here.
            return None
        return cl

    def client_login(self):
        try:
            logging.debug("Connecting to 3PAR")
            self.client.login(self.hpe3par_username, self.hpe3par_password)
            logging.info("Logged in to: " + self.hpe3par_api_url)
        except hpeexceptions.HTTPUnauthorized as ex:
            msg = ("Failed to Login to 3PAR (%(url)s) because %(err)s" %
                   {'url': self.hpe3par_api_url, 'err': ex})
            logging.error(msg)

    def client_logout(self):
        logging.debug("Logout from 3PAR backend: %s", self.backend_name)
        self.client.logout()

    def _get_token_session(self):
        url = self.hpe3par_api_url + '/credentials'
        payload = {
            "user": self.hpe3par_username,
            "password": self.hpe3par_password
        }
        headers = {'content-type': 'application/json'}
        response = requests.post(url=url, data=json.dumps(payload), headers=headers)
        if response.status_code != 200:
            logging.warning(response.json())
            return None
        data = response.json()
        return data['key']

    def _get_pool_info(self, pool_object):
        if 'limitMiB' not in pool_object['SDGrowth']:
            pool_avail_space = self.client.getCPGAvailableSpace(pool_object['name'])
            pool_object['pool_avail_space'] = pool_avail_space
        return pool_object

    def _get_cpu_stats(self):
        # Get the cpu statistics data for last 5 minutes
        cpu_stats = self.client.getCPUStatisticsAtTime(samplefreq='hires')
        return cpu_stats['members']

    def _get_port_stats(self):
        # Get the cpu statistics data for last 5 minutes
        cpu_stats = self.client.getPortStatisticsAtTime(samplefreq='hires')
        return cpu_stats['members']

    def _get_pool_stats(self):
        # Get the cpgs statistics data for last 5 minutes
        if not self.get_all_pools:
            query = "name EQ "
            pool_name_list = self.config['pools'].split(',')
            for pool_name in pool_name_list:
                pool_name = pool_name.strip()
                query += pool_name + ","
        else:
            query = None
        cpu_stats = self.client.getCPGStatisticsAtTime(samplefreq='hires', query=query)
        return cpu_stats['members']

    """
    This func converts the alert format of HPE 3Par version 3.3.1.410
    """

    def _gen_alert_key(self, k):
        alert_key = {
            # "Id": 'alert_id',
            # "Message Code": 'message_code',
            # "Time": 'starts_at',
            # "Severity": 'extra_infor',
            "Message": 'log_content',
        }
        return alert_key.get(k, "Invalid key")

    def parse_alert(self, raw_alert, system_info):
        alert = []
        temp = {}
        for kv in raw_alert:
            kv_split = kv.split(':')
            if len(kv_split) > 1:
                k = kv_split[0].strip()
                k = self._gen_alert_key(k)
                v = kv_split[1].strip()
                if k == 'log_content':
                    temp['log_content'] = kv[14:]
                    temp['backend_name'] = self.backend_name
                    temp['san_ip'] = system_info['IPv4Addr']
                    alert.append(temp)
                    temp = {}
                elif k != 'Invalid key':
                    temp[k] = v
        return alert

    def run(self):  # noqa: C901
        self.client = self._create_client()
        while True:

            try:
                if time() - self.time_last_request > self.timeout:
                    sleep(self.interval)
                    continue
                self.client_login()
                data = {}
                system_info = self.client.getStorageSystemInfo()
                data['system_info'] = system_info

                data['pools'] = []

                if self.get_all_pools:
                    pools = self.client.getCPGs()
                    if len(pools['members']):
                        for p in pools['members']:
                            pool_stats = self._get_pool_info(p)
                            data['pools'].append(pool_stats)

                else:
                    pool_name_list = self.config['pools'].split(',')
                    for pool_name in pool_name_list:
                        pool_name = pool_name.strip()
                        self.client.getVolumes()
                        p = self.client.getCPG(pool_name)
                        pool_stats = self._get_pool_info(p)
                        data['pools'].append(pool_stats)
                if self.optional_metrics.get('cpu'):
                    cpu_statistics = self._get_cpu_stats()
                    data['cpu_statistics'] = cpu_statistics
                if self.optional_metrics.get('cpg'):
                    cpg_statistics = self._get_pool_stats()
                    data['cpg_statistics'] = cpg_statistics
                if self.optional_metrics.get('port'):
                    cpg_statistics = self._get_port_stats()
                    data['port_statistics'] = cpg_statistics

                # Get all new alerts
                if self.optional_metrics.get('alert'):
                    alert_raw = self.client._run(['showalert'])
                    alert_list = self.parse_alert(alert_raw, system_info)
                    data['alert_list'] = alert_list

                # Caching data to file using pickle
                cache_data(self.cache_file, data)

            except BaseException:
                logging.error('Error: ', exc_info=True)
            finally:
                self.client_logout()

            sleep(self.interval)


def main(config, interval):
    hpe3par_metrics = prometheus_metrics.HPE3ParMetrics(config=config)
    hpe3par_exporter = HPE3ParExporter(config, interval)
    hpe3par_exporter.start()
    return hpe3par_exporter, hpe3par_metrics
