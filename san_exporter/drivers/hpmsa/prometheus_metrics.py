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

__author__ = "daikk115"

from prometheus_client import Gauge, Info
from prometheus_client import generate_latest

from san_exporter.drivers import base_driver


class HPMSAMetrics(base_driver.Metrics):

    def __init__(self, config):
        super().__init__(config=config)

        self.backend_name = config['name']
        self.info_san = Info(
            'san_storage',
            'Basic information',
            registry=self.registry)
        self.metrics = {}
        self.san_ip = config['hpmsa_backend_host']

    def parse_system_info(self, info_metrics):
        self.info_san.info({
            'name': info_metrics['san_system_name'],
            'backend_name': self.backend_name,
            'systemVersion': info_metrics['san_node_hardware_version'],
            'serialNumber': info_metrics['san_node_serial_number'],
            'model': info_metrics['san_system_model'],
            'san_ip': self.san_ip
        })

    def parse_metrics(self, data):
        self.parse_system_info(data['info_metrics'])
        for value in data['metrics']:
            name = value['name']
            labels = value['labels']
            labels['backend_name'] = self.backend_name
            if name not in self.metrics:
                metric = Gauge(
                    name,
                    value['description'],
                    labels.keys(),
                    registry=self.registry)
                self.metrics[name] = metric
            self.metrics[name]._metrics.clear()
            if name in {
                'san_pool_free_capacity_mib',
                    'san_pool_total_capacity_mib'}:
                self.metrics[name].labels(**labels).set(value['value'] / 1024)
            else:
                self.metrics[name].labels(**labels).set(value['value'])

    def get_metrics(self):
        metrics = generate_latest(self.registry)
        return metrics
