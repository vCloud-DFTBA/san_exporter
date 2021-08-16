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

from prometheus_client import Gauge
from prometheus_client import generate_latest

from san_exporter.drivers import base_driver


class HPEStorwizeV7kMetrics(base_driver.Metrics):

    def __init__(self, config):
        _labels = ["backend_name", "san_ip"]

        super().__init__(config=config, labels=_labels)

        self.backend_name = config['name']

        self.perf_metrics = {}

        _info_label = ["backend_name", "san_ip", "san_name", "systemVersion", "serialNumber", "model"]
        self.info_san = Gauge('san_storage_info', 'Basic information', _info_label, registry=self.registry)

        self.gauge_san_total_nodes = Gauge('san_totalNodes', 'Total nodes', _labels, registry=self.registry)
        self.gauge_san_master_nodes = Gauge('san_masterNodes', 'Master nodes', _labels, registry=self.registry)
        self.gauge_san_cluster_nodes = Gauge('san_clusterNodes', 'Cluster nodes',
                                             _labels, registry=self.registry)
        self.gauge_san_online_nodes = Gauge('san_onlineNodes', 'Online nodes', _labels, registry=self.registry)
        # self.gauge_san_qos_support = Gauge('san_qos_support', 'QoS support', _labels, registry=self.registry)
        # self.gauge_san_thin_provision_support = Gauge('san_thin_provision_support', 'Thin provision support',
        #                                               _labels, registry=self.registry)
        # self.gauge_san_system_reporter_support = Gauge('san_system_reporter_support', 'System reporter support',
        #                                                _labels, registry=self.registry)
        self.gauge_san_compress_support = Gauge('san_compress_support', 'Compress support',
                                                _labels, registry=self.registry)

        self.gauge_san_total_capacity_mib = Gauge('san_totalCapacityMiB', 'Total system capacity in MiB',
                                                  _labels, registry=self.registry)
        self.gauge_san_allocated_capacity_mib = Gauge('san_allocatedCapacityMiB',
                                                      'Total allowed capacity in MiB',
                                                      _labels, registry=self.registry)
        self.gauge_san_free_capacity_mib = Gauge('san_freeCapacityMiB', 'Total free capacity in MiB',
                                                 _labels, registry=self.registry)

        self.define_pool_info_metrics()

    def define_pool_info_metrics(self):
        pool_labels = ["backend_name", "pool_name", "san_ip"]
        self.gauge_san_pool_total_lun = Gauge('san_pool_totalLUNs', 'Total LUNs (or Volumes)',
                                              pool_labels, registry=self.registry)
        self.gauge_san_pool_total_capacity_mib = Gauge('san_pool_total_capacity_mib',
                                                       'Total capacity of pool in MiB',
                                                       pool_labels, registry=self.registry)
        self.gauge_san_pool_free_capacity_mib = Gauge('san_pool_free_capacity_mib',
                                                      'Free of pool in MiB',
                                                      pool_labels, registry=self.registry)
        self.gauge_san_pool_provisioned_capacity_mib = Gauge('san_pool_provisioned_capacity_mib',
                                                             'Provisioned of pool in MiB',
                                                             pool_labels, registry=self.registry)

    def define_cpu_metrics(self):
        cpu_labels = ["backend_name", "node", "mode", "cpu", "san_ip"]
        self.gauge_san_cpu_total = Gauge('san_cpu_total', 'The cpus spent in each mode',
                                         cpu_labels, registry=self.registry)

    def _convert_capacity(self, raw_capacity):
        raw_capacity = raw_capacity.replace(',', '')
        return float(raw_capacity) * 1024

    def parse_system_info(self, data_info):
        for storage in data_info:
            system_info = storage['system_info']
            nodes = storage['nodes']
            self.info_san.labels(san_name=system_info["Name"], san_ip=storage['IP Address'],
                                 backend_name=self.backend_name, systemVersion=system_info['Firmware'].split(" ")[0],
                                 serialNumber=system_info['Serial Number'], model=system_info['Model']
                                 ).set(1)

            compression_support = 1 if system_info['Compressed'] == 'Yes' else 0

            self.gauge_san_total_nodes \
                .labels(backend_name=self.backend_name, san_ip=storage['IP Address']).set(len(nodes))
            master_node_id = 0
            online_node = 0
            for node in nodes:
                if node['Configuration Node'] == 'Yes':
                    master_node_id = node['id']
                if node['Status'] != "Error":
                    online_node += 1
            self.gauge_san_master_nodes \
                .labels(backend_name=self.backend_name, san_ip=storage['IP Address']).set(master_node_id)
            self.gauge_san_cluster_nodes \
                .labels(backend_name=self.backend_name, san_ip=storage['IP Address']).set(len(nodes))
            self.gauge_san_online_nodes \
                .labels(backend_name=self.backend_name, san_ip=storage['IP Address']).set(online_node)

            self.gauge_san_compress_support.labels(backend_name=self.backend_name, san_ip=storage['IP Address']) \
                .set(compression_support)

            self.gauge_san_total_capacity_mib.labels(backend_name=self.backend_name, san_ip=storage['IP Address']) \
                .set(self._convert_capacity(system_info['Pool Capacity']))
            self.gauge_san_free_capacity_mib.labels(backend_name=self.backend_name, san_ip=storage['IP Address']) \
                .set(self._convert_capacity(system_info['Unreserved Pool Space']))
            if system_info.get('Allocated Space'):
                # For Spectrum version 5.3.6 and later
                allocated_capacity = system_info.get('Allocated Space')
            else:
                allocated_capacity = system_info.get('Used Pool Space')
            self.gauge_san_allocated_capacity_mib.labels(backend_name=self.backend_name, san_ip=storage['IP Address']) \
                .set(self._convert_capacity(allocated_capacity))

    def parse_pool_info(self, pools_data):
        for storage in pools_data:
            for p in storage['pools']:
                self.gauge_san_pool_total_lun.labels(backend_name=self.backend_name, san_ip=storage['IP Address'],
                                                     pool_name=p['Name']) \
                    .set(self._convert_capacity(p['Volumes']))
                self.gauge_san_pool_total_capacity_mib.labels(backend_name=self.backend_name,
                                                              san_ip=storage['IP Address'],
                                                              pool_name=p['Name']) \
                    .set(self._convert_capacity(p['Capacity']))
                self.gauge_san_pool_free_capacity_mib.labels(backend_name=self.backend_name,
                                                             san_ip=storage['IP Address'],
                                                             pool_name=p['Name']) \
                    .set(self._convert_capacity(p['Available Pool Space']))
                self.gauge_san_pool_provisioned_capacity_mib.labels(backend_name=self.backend_name,
                                                                    san_ip=storage['IP Address'],
                                                                    pool_name=p['Name']) \
                    .set(self._convert_capacity(p['Total Volume Capacity']))

    def parse_perf_metrics(self, data):
        for value in data:
            name = value['name']
            labels = value['labels']
            if name not in self.perf_metrics:
                metric = Gauge(name, value['description'], labels.keys(), registry=self.registry)
                self.perf_metrics[name] = metric
            self.perf_metrics[name].labels(**labels).set(value['value'])

    def parse_metrics(self, data):
        self.parse_system_info(data['system_info'])
        self.parse_pool_info(data['pools_info'])
        if self.optional_metrics.get('cpg_statics'):
            self.parse_perf_metrics(data['pool_perf'])
        if self.optional_metrics.get('port'):
            self.parse_perf_metrics(data['node_perf'])

    def get_metrics(self):
        metrics = generate_latest(self.registry)
        return metrics
