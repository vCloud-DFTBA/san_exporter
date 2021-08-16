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

from prometheus_client import Gauge, Info, generate_latest
from san_exporter.drivers import base_driver


class HitachiG700Metrics(base_driver.Metrics):
    def __init__(self, config):
        super().__init__(config=config)
        self.labels = ['backend_name', 'san_ip']
        self.backend_name = config['name']
        self.san_ip = config['VSP_api_ip']
        self.info_san = Info(
            'san_storage', 'Basic information', registry=self.registry)
        if self.optional_metrics.get('pool'):
            self.define_pool_metrics()
        if self.optional_metrics.get('node'):
            self.define_node_metrics()
        if self.optional_metrics.get('alert'):
            self.define_alert_metrics()

    def parse_system_info(self, system_info):
        self.info_san.info({
            'backend_name': self.backend_name,
            'san_ip': self.san_ip,
            'model': system_info['model'],
            'storageDeviceId': system_info['storageDeviceId'],
            'ctl1Ip': system_info['ctl1Ip'],
            'ctl2Ip': system_info['ctl2Ip'],
            'svpIp': system_info['svpIp'],
            'targetCtl': system_info['targetCtl']
        })

    def define_node_metrics(self):
        node_labels = ['backend_name', 'san_ip', 'node_name']
        self.gauge_san_node_temperature_value = Gauge(
            'san_node_temperature_value',
            'Node Temperature Value - degree Celcius', node_labels,
            registry=self.registry)
        self.gauge_san_node_temperature_status = Gauge(
            'san_node_temperature_status',
            'Node Temperature Status [0-Normal, 1-Warning, 2-Failed]',
            node_labels, registry=self.registry)
        self.gauge_san_total_nodes = Gauge(
            'san_totalNodes', 'Total Nodes', self.labels,
            registry=self.registry)
        self.gauge_san_online_nodes = Gauge(
            'san_onlineNodes', 'Online Nodes', self.labels,
            registry=self.registry)

    def parse_node_metrics(self, node):
        normal_nodes = node['normal_nodes']
        total_nodes = node['total_nodes']
        self.gauge_san_total_nodes.labels(
            backend_name=self.backend_name, san_ip=self.san_ip).set(
            total_nodes)
        self.gauge_san_online_nodes.labels(
            backend_name=self.backend_name, san_ip=self.san_ip).set(
            normal_nodes)
        for i in node['metrics']:
            name = i['location']
            temperature = i['temperature']
            temperature_status = i['temperatureStatus']  # Controller Status:
            # [0-Normal, 1-Warning, 2-Failed]
            if temperature_status == 'Normal':
                temperature_status = 0
            elif temperature_status == 'Warning':
                temperature_status = 1
            else:
                temperature_status = 2
            self.gauge_san_node_temperature_value.labels(
                backend_name=self.backend_name, san_ip=self.san_ip,
                node_name=name).set(temperature)
            self.gauge_san_node_temperature_status.labels(
                backend_name=self.backend_name, san_ip=self.san_ip,
                node_name=name).set(temperature_status)

    def define_pool_metrics(self):
        pool_labels = ['backend_name', 'san_ip', 'pool_name', 'pool_id']
        self.gauge_san_pool_total_capacity = Gauge(
            'san_pool_total_capacity_mib', 'Total capacity of pool in MiB',
            pool_labels, registry=self.registry)
        self.gauge_san_pool_free_capacity = Gauge(
            'san_pool_free_capacity_mib', 'Free capacity of pool in MiB',
            pool_labels, registry=self.registry)

    def parse_pool_metrics(self, pool):
        for i in pool:
            pool_name = i['poolName']
            pool_id = i['poolId']
            total_capacity = i['totalPhysicalCapacity']
            free_capacity = i['availablePhysicalVolumeCapacity']
            self.gauge_san_pool_total_capacity.labels(
                backend_name=self.backend_name, san_ip=self.san_ip,
                pool_name=pool_name, pool_id=pool_id).set(total_capacity)
            self.gauge_san_pool_free_capacity.labels(
                backend_name=self.backend_name, san_ip=self.san_ip,
                pool_name=pool_name, pool_id=pool_id).set(free_capacity)

    def define_alert_metrics(self):
        alert_labels = ['backend_name', 'san_ip', 'log_content']
        self.san_alert = Gauge(
            'san_alert', 'SAN alert', alert_labels, registry=self.registry)

    def parse_alert_metrics(self, alert):
        for i in alert:
            if i['errorLevel'] == 'Serious' or i['errorLevel'] == 'Acute':
                log_content = i['errorSection'] + '. ' + i['errorDetail'] \
                              + '. Location: ' + i['location']
                self.san_alert.labels(
                    backend_name=self.backend_name, san_ip=self.san_ip,
                    log_content=log_content).set(1)

    def parse_metrics(self, data):
        self.parse_system_info(data['system_info'])
        if self.optional_metrics.get('pool'):
            self.parse_pool_metrics(data['pool'])
        if self.optional_metrics.get('node'):
            self.parse_node_metrics(data['node'])
        if self.optional_metrics.get('alert'):
            self.san_alert._metrics.clear()
            self.parse_alert_metrics(data['alert'])

    def get_metrics(self):
        metrics = generate_latest(self.registry)
        return metrics
