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

import requests
import logging
import json
from time import sleep, time
from san_exporter.drivers import base_driver
from san_exporter.drivers.hitachig700 import prometheus_metrics
from san_exporter.utils.utils import cache_data


class HitachiG700Exporter(base_driver.ExporterDriver):
    def __init__(self, config=None, interval=10):
        super().__init__(config, interval)
        self.g700_api_ip = config['VSP_api_ip']
        self.g700_api_port = config['VSP_api_port']
        self.g700_username = config['username']
        self.g700_password = config['password']
        self.backend_name = config['name']
        self.serial = config['serial']
        self.auth = (self.g700_username, self.g700_password)

    def check_connection_and_get_storage_id(self):
        try:
            logging.debug("Connecting to VSP %s" % self.g700_api_ip)
            self.baseURL = 'https://%s:%s/ConfigurationManager/v1/objects/' \
                           'storages' % (self.g700_api_ip, self.g700_api_port)
            self.headers = {'Accept': 'application/json',
                            "Content-Type": "application/json"}
            data = requests.get(
                self.baseURL, headers=self.headers, verify=False).json()
            logging.info("Connect to VSP %s successfully!" % self.g700_api_ip)
        except:
            logging.error("Fail to connect to VSP %s. Check the connection!!"
                          % self.g700_api_ip)
            return None
        storage_id = None
        for i in data['data']:
            if str(i['serialNumber']) == self.serial:
                storage_id = i['storageDeviceId']
                break
        if not storage_id:
            logging.error(
                "No Device was found with serial %s number at VSP %s !"
                % (self.serial, self.g700_api_ip))
        return storage_id

    def get_session_token(self):
        try:
            data = requests.post(
                self.baseURL + '/sessions', headers=self.headers,
                auth=self.auth, verify=False).json()
            return data['token']
        except:
            logging.error(
                "Can not get session token!! Permission denied by VSP %s. "
                "Check your account!!" % self.g700_api_ip)
            return None

    def get_system_info(self):
        system_info = requests.get(
            self.baseURL, headers=self.headers, verify=False).json()
        return system_info

    def get_hardware_status(self):
        url = self.baseURL + '/components/instance'
        rq_data = requests.get(url, headers=self.headers, verify=False).json()
        return rq_data

    def check_status_of_hardware(self, hw_name, data):
        not_normal_hw = []
        if hw_name == 'driveBoxes':
            for drb in data:
                for ps in drb.get('dbps'):
                    if ps['status'] != "Normal":
                        not_normal_hw.append(ps)
                for dr in drb.get('drives'):
                    if dr['status'] != "Normal":
                        not_normal_hw.append(dr)
        else:
            for i in data:
                if i['status'] != "Normal":
                    not_normal_hw.append(i)
        return not_normal_hw

    def get_unhealthy_hardware(self):
        hardware = self.get_hardware_status()
        # chbs: Channel Board
        # dkbs: Disk Board
        # bkmfs: Backup Module
        # lanbs: LAN Board
        # dkcpss: DKCPS - Controller Processor
        hw_monitored = ['chbs', 'dkbs', 'bkmfs', 'lanbs', 'dkcpss',
                        'cacheFlashMemories', 'cacheMemories', 'driveBoxes']
        unhealthy_hw = []
        for i in hw_monitored:
            not_normal_hw = self.check_status_of_hardware(i, hardware.get(i))
            if not_normal_hw:
                for hw in not_normal_hw:
                    unhealthy_hw.append(hw)
        return unhealthy_hw

    def get_node_metrics(self):
        url = self.baseURL + '/components/instance'
        rq_data = requests.get(url, headers=self.headers, verify=False).json()
        total_nodes = 0
        normal_nodes = 0
        for i in rq_data['ctls']:
            total_nodes += 1
            if i['status'] == "Normal":
                normal_nodes += 1
        node_data = {'normal_nodes': normal_nodes, 'total_nodes': total_nodes,
                     'metrics': rq_data['ctls']}
        return node_data

    def get_pool_metrics(self):
        url = self.baseURL + '/pools'
        rq_data = requests.get(url, headers=self.headers, verify=False).json()
        return rq_data['data']

    def get_disk_metrics(self):
        url = self.baseURL + '/drives'
        rq_data = requests.get(url, headers=self.headers, verify=False).json()
        return rq_data['data']

    def get_alert_info(self):
        url = self.baseURL + '/alerts?type=DKC&type=CTL1&type=CTL2'
        alert_data = requests.get(
            url, headers=self.headers, verify=False).json()
        return alert_data['data']

    def remove_dupe_dicts(self, list):
        list_of_strings = [
            json.dumps(d, sort_keys=True)
            for d in list
        ]
        list_of_strings = set(list_of_strings)
        return [
            json.loads(s)
            for s in list_of_strings
        ]

    def get_alert_metrics(self):
        alert_info = self.get_alert_info()
        unhealthy_hw = self.get_unhealthy_hardware()
        alert_metrics = []
        for al in alert_info:
            resolved = True
            for i in al['actionCodes']:
                for hw in unhealthy_hw:
                    if i['accLocation'] == hw['location']:
                        resolved = False
            if not resolved:
                alert = {'errorDetail': al['errorDetail'],
                         'errorLevel': 'Serious',
                         'errorSection': al['errorSection'],
                         'location': al['location']}
                alert_metrics.append(alert)
            else:
                alert = {'errorDetail': al['errorDetail'],
                         'errorLevel': al['errorLevel'],
                         'errorSection': al['errorSection'],
                         'location': al['location']}
                alert_metrics.append(alert)
        return self.remove_dupe_dicts(alert_metrics)

    def run(self):
        while True:
            sleep(self.interval)
            if time() - self.time_last_request > self.timeout:
                continue
            storage_id = self.check_connection_and_get_storage_id()
            if not storage_id:
                continue
            self.baseURL = 'https://%s:%s/ConfigurationManager/v1/objects/' \
                           'storages/%s' % (self.g700_api_ip,
                                            self.g700_api_port, storage_id)
            token = self.get_session_token()
            if not token:
                continue
            self.headers = {'Accept': 'application/json',
                            "Content-Type": "application/json",
                            'Authorization': 'Session ' + token}
            data = {}
            try:
                data['system_info'] = self.get_system_info()
                if self.optional_metrics.get('node'):
                    data['node'] = self.get_node_metrics()
                if self.optional_metrics.get('pool'):
                    data['pool'] = self.get_pool_metrics()
                if self.optional_metrics.get('disk'):
                    data['disk'] = self.get_disk_metrics()
                if self.optional_metrics.get('alert'):
                    data['alert'] = self.get_alert_metrics()
            except:
                logging.error("Somethings wrong when getting metrics! Retry "
                              "after sleep.")
                continue
            cache_data(self.cache_file, data)


def main(config, interval):
    hitachig700_metrics = prometheus_metrics.HitachiG700Metrics(config=config)
    hitachig700_exporter = HitachiG700Exporter(config, interval)
    hitachig700_exporter.start()
    return hitachig700_exporter, hitachig700_metrics
