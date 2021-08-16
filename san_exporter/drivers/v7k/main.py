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
import requests
import operator

from san_exporter.utils.utils import cache_data
from san_exporter.utils.ssh_utils import SSHConnection

from san_exporter.drivers import base_driver
from san_exporter.drivers.v7k import prometheus_metrics

# Fix requests.exceptions.SSLError - dh key too small
requests.packages.urllib3.disable_warnings()
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += 'HIGH:!DH:!aNULL'
try:
    requests.packages.urllib3.contrib.pyopenssl.DEFAULT_SSL_CIPHER_LIST += 'HIGH:!DH:!aNULL'
except AttributeError:
    # no pyopenssl support used / needed / available
    pass

OPS = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": operator.truediv,
}

POOL_STATISTIC_METRICS = {
    803: {
        "name": "san_pool_number_read_io",
        "description": "Read I/O Rate - ops/s",
        "type": "gauge"
    },
    806: {
        "name": "san_pool_number_write_io",
        "description": "Write I/O Rate - ops/s",
        "type": "gauge"
    },
    812: {
        "name": "san_pool_read_cache_hit",
        "description": "Read Cache Hits - %",
        "type": "gauge"
    },
    815: {
        "name": "san_pool_write_cache_hit",
        "description": "Write Cache Hits - %",
        "type": "gauge"
    },
    819: {
        "name": "san_pool_read_kb",
        "description": "Read Data Rate - KiB/s",
        "type": "gauge",
        "opt": {
            "*": 1024
        }
    },
    820: {
        "name": "san_pool_write_kb",
        "description": "Write Data Rate - KiB/s",
        "type": "gauge",
        "opt": {
            "*": 1024
        }
    },
    822: {
        "name": "san_pool_read_service_time_ms",
        "description": "Read Response Time - ms/op",
        "type": "gauge"
    },
    823: {
        "name": "san_pool_write_service_time_ms",
        "description": "Write Response Time - ms/op",
        "type": "gauge"
    },
    825: {
        "name": "san_pool_read_IOSize_kb",
        "description": "Read Transfer Size - KiB/op",
        "type": "gauge"
    },
    826: {
        "name": "san_pool_write_IOSize_kb",
        "description": "Write Transfer Size - KiB/op",
        "type": "gauge"
    },
}

NODE_STATISTIC_METRICS = {
    852: {
        "name": "san_port_number_read_io",
        "description": "Port Send I/O Rate - ops/s",
        "type": "gauge"
    },
    853: {
        "name": "san_port_number_write_io",
        "description": "Port Receive I/O Rate - ops/s",
        "type": "gauge"
    },
    858: {
        "name": "san_port_read_kb",
        "description": "Port Send Data Rate - KiB/s",
        "type": "gauge",
        "opt": {
            "*": 1024
        }
    },
    859: {
        "name": "san_port_write_kb",
        "description": "Port Receive Data Rate - KiB/s",
        "type": "gauge",
        "opt": {
            "*": 1024
        }
    },
    900: {
        "name": "san_cpu_system_utilization",
        "description": "The average percentage of time that the processors on nodes are busy doing system I/O tasks",
        "type": "gauge"
    },
    1087: {
        "name": "san_cpu_compression_utilization",
        "description": "The approximate percentage of time that the processor core was busy with data compression tasks",
        "type": "gauge"
    }
}


class HPEStorwizeV7kExporter(base_driver.ExporterDriver):

    def __init__(self, config=None, interval=300):
        super().__init__(config, interval)
        self.ibm_spectrum_control = config['ibm_spectrum_control']
        self._setup_spectrum_control_url()
        self.target_v7000 = []
        self.v7k_backend_ip = config['v7k_backend_ip']
        self.v7k_backend_port = config['v7k_backend_port']
        self.backend_name = config['name']
        self.client = None
        self.ssh_client = None
        for v in config['v7000_ip']:
            self.target_v7000.append({
                'IP Address': v
            })

    def client_v7k_ssh_login(self, username, password):
        try:
            logging.debug("Connecting to HPE Storwize V7000 Storage")
            self.ssh_client = SSHConnection(ip=self.v7k_backend_ip, port=self.v7k_backend_port,
                                            user=username, password=password)
            logging.info("Logged in to HPE Storwize V7000 Storage at: " + self.v7k_backend_ip)
        except Exception as ex:
            msg = ("Failed to Login to HPE Storwize V7000 Storage at (%(url)s) because %(err)s" %
                   {'url': self.v7k_backend_ip, 'err': ex})
            logging.error(msg)

    def _setup_spectrum_control_url(self):
        # This is setup for IBM Spectrum Control v5.2
        self.ibm_spectrum_control['auth_url'] = self.ibm_spectrum_control['url'] + "/srm/j_security_check"
        self.ibm_spectrum_control['api_base_url'] = self.ibm_spectrum_control['url'] + "/srm/REST/api/v1/StorageSystems"

    def client_spectrum_control_login(self):
        try:
            logging.debug("Connecting to IBM Spectrum control")
            self.client = requests.session()
            # TODO: check login failed here
            self.client.post(self.ibm_spectrum_control['auth_url'],
                             data={'j_username': self.ibm_spectrum_control['username'],
                                   'j_password': self.ibm_spectrum_control['password']},
                             verify=False)
            logging.info("Logged in to IBM Spectrum control at: " + self.ibm_spectrum_control['url'])
        except Exception as ex:
            msg = ("Failed to Login to IBM Spectrum control at (%(url)s) because %(err)s" %
                   {'url': self.ibm_spectrum_control['url'], 'err': ex})
            logging.error(msg)

    def _get_system_info(self):
        data_info = []
        storage_list = self.client.get(self.ibm_spectrum_control['api_base_url'])
        for storage in storage_list.json():
            for v in self.target_v7000:
                if storage['IP Address'] == v['IP Address']:
                    v['id'] = storage['id']
                    target_storage = {
                        'IP Address': v['IP Address'],
                        'id': storage['id'],
                        'system_info': storage
                    }
                    nodes_response = self.client.get(self.ibm_spectrum_control['api_base_url'] + "/" +
                                                     storage['id'] + "/Nodes")
                    target_storage['nodes'] = nodes_response.json()
                    data_info.append(target_storage)
        return data_info

    def _get_pools_info(self):
        storage_pools = []
        for v in self.target_v7000:
            if 'id' not in v:
                logging.warning('Storage IBM V7000 {} did not have enough information'.format(v))
                self.target_v7000.remove(v)
            else:
                pool_data = {
                    'IP Address': v['IP Address']
                }
                pools_response = self.client.get(self.ibm_spectrum_control['api_base_url'] + "/" +
                                                 v['id'] + "/Pools")
                pool_data['pools'] = pools_response.json()
                storage_pools.append(pool_data)
        return storage_pools

    def _get_alert(self):
        cmd = "lseventlog -filtervalue 'error_code>=1' -delim !"
        raw_alert = self.ssh_client.execute(cmd)
        alerts = self._parse_alert(raw_alert)
        return alerts

    def _parse_alert(self, raw_alert):
        for alert in raw_alert:
            del alert['event_id']

            del alert['error_code']
            del alert['last_timestamp']
            del alert['status']

            alert['log_content'] = alert['description'] + " at " + alert['object_name']
            del alert['description']
            del alert['object_name']
            del alert['object_type']
            del alert['object_id']
            del alert['copy_id']
            del alert['fixed']
            del alert['sequence_number']

            alert['backend_name'] = self.backend_name
            alert['instance'] = self.v7k_backend_ip
        return raw_alert

    def _get_resource_perf(self, resource, metrics_list, storage_id, storage_ip):
        current_epoch_time = time()
        current_epoch_time = int(current_epoch_time) * 1000
        # Due to system report ech 5m, so we minus 7.5m here to make sure get only the latest value.
        last_7m_ago_epoch_time = current_epoch_time - 500000
        metrics = ','.join(map(str, metrics_list.keys()))
        api = self.ibm_spectrum_control['api_base_url'] + '/' + storage_id + "/" + resource \
              + "/Performance?metrics=" + metrics + "&startTime=" + str(last_7m_ago_epoch_time)
        req = self.client.get(api)
        res = req.json()
        res = res[1:]
        resource_perf = []
        for item in res:
            metric = metrics_list[item['metricId']]
            labels = {
                'san_ip': storage_ip,
                'backend_name': self.backend_name
            }
            if resource == 'Pools':
                labels['pool_name'] = item['deviceName'].split('<')[0]
            elif resource == 'Nodes':
                labels['node_name'] = item['deviceName'].split('<')[0]
            if metric.get('opt'):
                value = OPS[list(metric['opt'].keys())[0]](item['maxValue'], list(metric['opt'].values())[0])
            else:
                value = item['maxValue']
            metric_converted = {
                'name': metric['name'],
                'labels': labels,
                'type': metric.get('type', 'gauge'),
                'description': metric['description'],
                'value': value
            }
            resource_perf.append(metric_converted)
        return resource_perf

    def run(self):
        while True:
            try:
                if time() - self.time_last_request > self.timeout:
                    logging.debug('Backend {} is sleeping for {}'.format(self.ibm_spectrum_control, self.interval))
                    sleep(self.interval)
                    continue
                self.client_spectrum_control_login()
                data = {}
                system_info = self._get_system_info()
                data['system_info'] = system_info

                pools_info = self._get_pools_info()
                data['pools_info'] = pools_info

                if self.optional_metrics.get('cpg_statics'):
                    data['pool_perf'] = []
                    for v in self.target_v7000:
                        perf = self._get_resource_perf('Pools', POOL_STATISTIC_METRICS, v['id'], v['IP Address'])
                        data['pool_perf'] += perf

                if self.optional_metrics.get('port'):
                    data['node_perf'] = []
                    for v in self.target_v7000:
                        perf = self._get_resource_perf('Nodes', NODE_STATISTIC_METRICS, v['id'], v['IP Address'])
                        data['node_perf'] = perf

                # if self.optional_metrics.get('alert'):
                #     self.client_v7k_ssh_login()
                #     alerts = self._get_alert()
                #     data['alerts'] = alerts

                # caching data to file using pickle
                cache_data(self.cache_file, data)
            except:
                logging.error('Error: ', exc_info=True)

            sleep(self.interval)


def main(config, interval):
    v7k_metrics = prometheus_metrics.HPEStorwizeV7kMetrics(config=config)
    v7k_exporter = HPEStorwizeV7kExporter(config, interval)
    v7k_exporter.start()
    return v7k_exporter, v7k_metrics
