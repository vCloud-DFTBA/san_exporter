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

"""An example parsing metrics module used to parse collected data to metrics."""

from prometheus_client import Gauge, Info
from prometheus_client import generate_latest

from san_exporter.drivers import base_driver


class DummyMetrics(base_driver.Metrics):

    def __init__(self, config):
        _labels = ["backend_name"]

        super().__init__(config=config, labels=_labels)

        self.backend_name = config['name']

        self.info_san = Info(
            'san_storage',
            'Basic information',
            registry=self.registry)

        self.gauge_san_total_capacity_mib = Gauge(
            'san_totalCapacityMiB',
            'Total system capacity in MiB',
            _labels,
            registry=self.registry)
        self.gauge_san_allocated_capacity_mib = Gauge(
            'san_allocatedCapacityMiB',
            'Total allowed capacity in MiB',
            _labels,
            registry=self.registry)
        self.gauge_san_free_capacity_mib = Gauge(
            'hpe3par_freeCapacityMiB',
            'Total free capacity in MiB',
            _labels,
            registry=self.registry)

        if self.optional_metrics.get('cpu_statistics'):
            self.define_cpu_metrics()

    def define_cpu_metrics(self):
        cpu_labels = ["backend_name", "node", "mode", "cpu"]
        self.gauge_san_cpu_total = Gauge(
            'san_cpu_total',
            'The cpus spent in each mode',
            cpu_labels,
            registry=self.registry)

    def parse_system_info(self, system_info):
        self.info_san.info({
            'name': system_info["name"],
            'backend_name': self.backend_name,
            'systemVersion': system_info['systemVersion'],
            'serialNumber': system_info['serialNumber'],
            'model': system_info['model']
        })

    def parse_pool_info(self, pool_info):
        for p in pool_info:
            self.gauge_san_total_capacity_mib .labels(
                backend_name=self.backend_name).set(
                p["totalCapacityMiB"])
            self.gauge_san_allocated_capacity_mib .labels(
                backend_name=self.backend_name).set(
                p["allocatedCapacityMiB"])
            self.gauge_san_free_capacity_mib .labels(
                backend_name=self.backend_name).set(
                p["freeCapacityMiB"])

    def parse_cpu_statistics(self, cpu_statistics):
        for cpu in cpu_statistics:
            node = cpu.get('node')
            cpu_id = cpu.get('cpu')
            self.gauge_san_cpu_total.labels(
                backend_name=self.backend_name,
                node=node,
                cpu=cpu_id,
                mode='userPct') .set(
                cpu.get('userPct'))
            self.gauge_san_cpu_total.labels(
                backend_name=self.backend_name,
                node=node,
                cpu=cpu_id,
                mode='systemPct') .set(
                cpu.get('systemPct'))
            self.gauge_san_cpu_total.labels(
                backend_name=self.backend_name,
                node=node,
                cpu=cpu_id,
                mode='idlePct') .set(
                cpu.get('idlePct'))
            self.gauge_san_cpu_total.labels(
                backend_name=self.backend_name,
                node=node,
                cpu=cpu_id,
                mode='interruptsPerSec') .set(
                cpu.get('interruptsPerSec'))
            self.gauge_san_cpu_total.labels(
                backend_name=self.backend_name,
                node=node,
                cpu=cpu_id,
                mode='contextSwitchesPerSec') .set(
                cpu.get('contextSwitchesPerSec'))

    def parse_metrics(self, data):
        self.parse_system_info(data['system_info'])
        self.parse_pool_info(data['pools'])
        if self.optional_metrics.get('cpu_statistics'):
            self.parse_cpu_statistics(data['cpu_statistics'])

    def get_metrics(self):
        metrics = generate_latest(self.registry)
        return metrics
