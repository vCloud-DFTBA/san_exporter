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

import storops
import requests
import logging
from time import sleep, time
from san_exporter.drivers import base_driver
from san_exporter.drivers.dellunity import prometheus_metrics
from san_exporter.utils.utils import cache_data


class DellUnityExporter(base_driver.ExporterDriver):
    def __init__(self, config=None, interval=10):
        super().__init__(config, interval)
        self.dellunity_api_ip = config['dellunity_api_ip']
        self.dellunity_username = config['dellunity_username']
        self.dellunity_password = config['dellunity_password']
        self.backend_name = config['name']
        self.data = storops.UnitySystem(
            self.dellunity_api_ip, self.dellunity_username,
            self.dellunity_password)
        self.data.enable_perf_stats(interval=self.interval)

    def get_system_info(self):
        system_data = {}
        url = 'https://' + self.dellunity_api_ip \
              + '/api/types/basicSystemInfo/instances'
        try:
            response = requests.get(url, headers={
                'Accept': 'application/json'}, verify=False).json()[
                'entries'][0]['content']
            system_data.update({'softwareVersion': response['softwareVersion'],
                                'apiVersion': response['apiVersion']})
        except:
            logging.error("Can not get basic system info. Call the support"
                          "team!")
            return None
        system_info = self.data
        system_data.update({'name': system_info.name,
                            'model': system_info.model,
                            'serial_number': system_info.serial_number,
                            'platform': system_info.platform})
        system_capacity = self.data.get_system_capacity()
        system_data['size_total'] = system_capacity[0].size_total
        system_data['size_free'] = system_capacity[0].size_free
        system_data['size_used'] = system_capacity[0].size_used
        system_data['size_subscribed'] = system_capacity[0].size_subscribed
        node_object = self.data.get_sp()
        system_data['total_nodes'] = len(node_object)
        unhealthy_nodes = 0
        online_nodes = 0
        for i in node_object:
            if i.needs_replacement:
                unhealthy_nodes += 1
            if i.existed:
                online_nodes += 1
        system_data['online_nodes'] = online_nodes
        system_data['unhealthy_nodes'] = unhealthy_nodes
        return system_data

    def get_pool_info(self):
        pool_object = self.data.get_pool()
        pool_data = []
        for t in pool_object:
            data = {'name': t.name, 'id': t.id, 'size_total': t.size_total,
                    'size_subscribed': t.size_subscribed,
                    'size_used': t.size_used, 'size_free': t.size_free}
            pool_data.append(data)
        return pool_data

    def get_node_metrics(self):
        node_object = self.data.get_sp()
        node_data = []
        for t in node_object:
            data = {'id': t.id, 'temperature': t.temperature,
                    'read_byte_rate': t.read_byte_rate,
                    'write_byte_rate': t.write_byte_rate,
                    'block_read_iops': t.block_read_iops,
                    'block_write_iops': t.block_write_iops,
                    'utilization': t.utilization}
            node_data.append(data)
        return node_data

    def get_fcport_metrics(self):
        fcport_object = self.data.get_fc_port()
        fcport_data = []
        for t in fcport_object:
            data = {'id': t.id, 'slot_number': t.slot_number,
                    'read_iops': t.read_iops, 'write_iops': t.write_iops,
                    'read_byte_rate': t.read_byte_rate,
                    'write_byte_rate': t.write_byte_rate}
            fcport_data.append(data)
        return fcport_data

    def get_alert_metrics(self, software_version):
        # severity:
        #   6: information
        #   4: notice
        #   3: error
        # state: only can be seen if software version is 5.0.0 or later
        #   0: Active_Manual - Active alerts that must be manually cleared
        #   using the /event/alert/hist deactivate command after being resolved
        #   1: Active_Auto - Active alerts that will be automatically cleared
        #   once resolved
        #   2: Inactive - Alerts that are already resolved
        # Link: https://www.delltechnologies.com/en-vn/documentation/unity-family/unity-p-cli-user-guide/09-unity-cli-br-manage-events-and-alerts.htm
        if software_version >= '5.0.0':
            url = 'https://' + self.dellunity_api_ip \
                  + '/api/types/alert/instances?fields=message,severity&' \
                    'filter=severity ne 4 and severity ne 6 and state ne 2'
        else:
            logging.warning("Software version is {}, can not get alert state!"
                            .format(software_version))
            url = 'https://' + self.dellunity_api_ip \
                  + '/api/types/alert/instances?fields=message,severity&' \
                    'filter=severity ne 4 and severity ne 6'
        auth = (self.dellunity_username, self.dellunity_password)
        header = {'Content-type': 'application/json',
                  'Accept': 'application/json',
                  'X-EMC-REST-CLIENT': 'true'}
        response = requests.get(
            url, auth=auth, headers=header, verify=False).json()
        return response['entries']

    def get_lun_metrics(self):
        lun_object = self.data.get_lun()
        lun_data = []
        for t in lun_object:
            data = {'name': t.name, 'read_iops': t.read_iops,
                    'write_iops': t.write_iops,
                    'response_time': t.response_time,
                    'read_byte_rate': t.read_byte_rate,
                    'write_byte_rate': t.write_byte_rate}
            lun_data.append(data)
        return lun_data

    def get_disk_metrics(self):
        disk_object = self.data.get_disk()
        disk_data = []
        for t in disk_object:
            data = {'name': t.name, 'read_iops': t.read_iops,
                    'write_iops': t.write_iops,
                    'response_time': t.response_time,
                    'read_byte_rate': t.read_byte_rate,
                    'write_byte_rate': t.write_byte_rate}
            disk_data.append(data)
        return disk_data

    def run(self):
        while True:
            sleep(self.interval)
            if time() - self.time_last_request > self.timeout:
                continue
            data = {}
            try:
                data['system_info'] = self.get_system_info()
                if not data['system_info']:
                    continue
                if self.optional_metrics.get('node'):
                    data['nodes'] = self.get_node_metrics()
                if self.optional_metrics.get('pool'):
                    data['pools'] = self.get_pool_info()
                if self.optional_metrics.get('fcport'):
                    data['fcport'] = self.get_fcport_metrics()
                if self.optional_metrics.get('alert'):
                    data['alerts'] = self.get_alert_metrics(
                        data['system_info']['softwareVersion'])
                if self.optional_metrics.get('lun'):
                    data['luns'] = self.get_lun_metrics()
                if self.optional_metrics.get('disk'):
                    data['disks'] = self.get_disk_metrics()
            except:
                logging.error("Somethings wrong when getting metrics. Retry"
                              "after sleep!")
                continue
            cache_data(self.cache_file, data)


def main(config, interval):
    dellunity_metrics = prometheus_metrics.DellUnityMetrics(config=config)
    dellunity_exporter = DellUnityExporter(config, interval)
    dellunity_exporter.start()
    return dellunity_exporter, dellunity_metrics
