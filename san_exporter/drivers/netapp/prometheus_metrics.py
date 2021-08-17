#!/usr/bin/python
# -*- coding: utf-8 -*-
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

from prometheus_client import Gauge, generate_latest

from san_exporter.drivers import base_driver


class NetAppMetrics(base_driver.Metrics):
    def __init__(self, config):
        super().__init__(config=config)
        labels = ['backend_name', 'san_ip']
        self.backend_name = config['name']
        self.san_ip = config['netapp_api_ip']
        self.define_cluster_info()
        if self.optional_metrics.get('cluster'):
            self.define_cluster_metric()
        if self.optional_metrics.get('pool'):
            self.define_pool_info_metrics()
        if self.optional_metrics.get('node'):
            self.define_node_metrics()
        if self.optional_metrics.get('disk'):
            self.define_disk_metrics()

    def define_cluster_info(self):
        cluster_labels = ["name",
                          "backend_name",
                          "san_ip",
                          "version"]
        self.gauge_san_cluster_info = Gauge(
            'san_storage_info',
            'Basic information',
            cluster_labels,
            registry=self.registry)

    def parse_cluster_info(self, cluster):
        self.gauge_san_cluster_info.labels(
            backend_name=self.backend_name,
            name=cluster['name'],
            san_ip=cluster['san_ip'],
            version=cluster['version']).set(1)

    def define_cluster_metric(self):
        cluster_labels = ["backend_name",
                          "san_ip",
                          "cluster_name"]
        self.gauge_san_cluster_block_read_iops = Gauge(
            'san_cluster_number_read_io',
            'Cluster Read IOPS',
            cluster_labels,
            registry=self.registry)
        self.gauge_san_cluster_block_write_iops = Gauge(
            'san_cluster_number_write_io',
            'Cluster Write IOPS',
            cluster_labels,
            registry=self.registry)
        self.gauge_san_cluster_block_read_iops = \
            Gauge('san_cluster_number_read_io', 'Cluster Read IOPS',
                  cluster_labels, registry=self.registry)
        self.gauge_san_cluster_block_write_iops = \
            Gauge('san_cluster_number_write_io', 'Cluster Write IOPS',
                  cluster_labels, registry=self.registry)
        self.gauge_san_cluster_block_other_iops = \
            Gauge('san_cluster_number_other_io', 'Cluster Other IOPS',
                  cluster_labels, registry=self.registry)
        self.gauge_san_cluster_block_read_latency = \
            Gauge('san_cluster_number_read_latency',
                  'Cluster Read Latency', cluster_labels,
                  registry=self.registry)
        self.gauge_san_cluster_block_write_latency = \
            Gauge('san_cluster_number_write_latency',
                  'Cluster Write Latency', cluster_labels,
                  registry=self.registry)
        self.gauge_san_cluster_block_other_latency = \
            Gauge('san_cluster_number_other_latency',
                  'Cluster Other Latency', cluster_labels,
                  registry=self.registry)
        self.gauge_san_cluster_block_read_byte_rate = \
            Gauge('san_cluster_number_read_by_rate',
                  'Cluster Read Throughput - KiB/s', cluster_labels,
                  registry=self.registry)
        self.gauge_san_cluster_block_write_byte_rate = \
            Gauge('san_cluster_number_write_byte_rate',
                  'Cluster Write Throughput - KiB/s', cluster_labels,
                  registry=self.registry)
        self.gauge_san_cluster_block_other_byte_rate = \
            Gauge('san_cluster_number_other_by_rate',
                  'Cluster Other Throughput - KiB/s', cluster_labels,
                  registry=self.registry)

    def parse_cluster_metric(self, cluster):
        read_iops = cluster['read_iops']
        write_iops = cluster['write_iops']
        other_iops = cluster['other_iops']
        read_latency = cluster['read_latency']
        write_latency = cluster['write_latency']
        other_latency = cluster['other_latency']
        read_throughput = cluster['read_throughput']
        write_throughput = cluster['write_throughput']
        other_throughput = cluster['other_throughput']

        self.gauge_san_cluster_block_read_iops.labels(
            backend_name=self.backend_name,
            cluster_name=cluster['name'],
            san_ip=self.san_ip).set(read_iops)

        self.gauge_san_cluster_block_write_iops.labels(
            backend_name=self.backend_name,
            cluster_name=cluster['name'],
            san_ip=self.san_ip).set(write_iops)

        self.gauge_san_cluster_block_other_iops.labels(
            backend_name=self.backend_name,
            cluster_name=cluster['name'],
            san_ip=self.san_ip).set(other_iops)

        self.gauge_san_cluster_block_read_latency.labels(
            backend_name=self.backend_name,
            cluster_name=cluster['name'],
            san_ip=self.san_ip).set(read_latency)

        self.gauge_san_cluster_block_read_latency.labels(
            backend_name=self.backend_name,
            cluster_name=cluster['name'],
            san_ip=self.san_ip).set(write_latency)

        self.gauge_san_cluster_block_read_latency.labels(
            backend_name=self.backend_name,
            cluster_name=cluster['name'],
            san_ip=self.san_ip).set(other_latency)

        self.gauge_san_cluster_block_read_byte_rate.labels(
            backend_name=self.backend_name,
            cluster_name=cluster['name'],
            san_ip=self.san_ip).set(read_throughput / 1024)

        self.gauge_san_cluster_block_write_byte_rate.labels(
            backend_name=self.backend_name,
            cluster_name=cluster['name'],
            san_ip=self.san_ip).set(write_throughput / 1024)

        self.gauge_san_cluster_block_other_byte_rate.labels(
            backend_name=self.backend_name,
            cluster_name=cluster['name'],
            san_ip=self.san_ip).set(other_throughput / 1024)

    def define_pool_info_metrics(self):
        pool_labels = ['backend_name', 'san_ip', 'pool_name']
        self.gauge_san_pool_total_capacity = \
            Gauge('san_pool_total_capacity_mib',
                  'Total capacity of pool in MiB', pool_labels,
                  registry=self.registry)
        self.gauge_san_pool_used_capacity = \
            Gauge('san_pool_used_capacity_mib',
                  'Used capacity of pool in MiB', pool_labels,
                  registry=self.registry)
        self.gauge_san_pool_free_capacity = \
            Gauge('san_pool_free_capacity_mib',
                  'Free capacity of pool in MiB', pool_labels,
                  registry=self.registry)
        self.gauge_san_pool_block_read_iops = \
            Gauge('san_pool_number_read_io', 'Pool Read IOPS',
                  pool_labels, registry=self.registry)
        self.gauge_san_pool_block_write_iops = \
            Gauge('san_pool_number_write_io', 'Pool Write IOPS',
                  pool_labels, registry=self.registry)
        self.gauge_san_pool_block_other_iops = \
            Gauge('san_pool_number_other_io', 'Pool Other IOPS',
                  pool_labels, registry=self.registry)
        self.gauge_san_pool_block_read_latency = \
            Gauge('san_pool_number_read_latency', 'Pool Read Latency',
                  pool_labels, registry=self.registry)
        self.gauge_san_pool_block_write_latency = \
            Gauge('san_pool_number_write_latency', 'Pool Write Latency',
                  pool_labels, registry=self.registry)
        self.gauge_san_pool_block_other_latency = \
            Gauge('san_pool_number_other_latency', 'Pool Other Latency',
                  pool_labels, registry=self.registry)
        self.gauge_san_pool_block_read_byte_rate = \
            Gauge('san_pool_number_read_by_rate',
                  'Pool Read Throughput - KiB/s', pool_labels,
                  registry=self.registry)
        self.gauge_san_pool_block_write_byte_rate = \
            Gauge('san_pool_number_write_byte_rate',
                  'Pool Write Throughput - KiB/s', pool_labels,
                  registry=self.registry)
        self.gauge_san_pool_block_other_byte_rate = \
            Gauge('san_pool_number_other_by_rate',
                  'Pool Other Throughput - KiB/s', pool_labels,
                  registry=self.registry)

    def parse_pool_info(self, pool_info):
        total_capacity = pool_info['size_total']
        used_capacity = pool_info['size_used']
        read_iops = pool_info['read_iops']
        write_iops = pool_info['write_iops']
        other_iops = pool_info['other_iops']
        read_latency = pool_info['read_latency']
        write_latency = pool_info['write_latency']
        other_latency = pool_info['other_latency']
        read_throughput = pool_info['read_throughput']
        write_throughput = pool_info['write_throughput']
        other_throughput = pool_info['other_throughput']

        self.gauge_san_pool_total_capacity.labels(
            backend_name=self.backend_name,
            pool_name=pool_info['name'],
            san_ip=self.san_ip).set(total_capacity / 1024 / 1024)

        self.gauge_san_pool_used_capacity.labels(
            backend_name=self.backend_name,
            pool_name=pool_info['name'],
            san_ip=self.san_ip).set(used_capacity / 1024 / 1024)

        self.gauge_san_pool_block_read_iops.labels(
            backend_name=self.backend_name,
            pool_name=pool_info['name'],
            san_ip=self.san_ip).set(read_iops)

        self.gauge_san_pool_block_write_iops.labels(
            backend_name=self.backend_name,
            pool_name=pool_info['name'],
            san_ip=self.san_ip).set(write_iops)

        self.gauge_san_pool_block_other_iops.labels(
            backend_name=self.backend_name,
            pool_name=pool_info['name'],
            san_ip=self.san_ip).set(other_iops)

        self.gauge_san_pool_block_read_latency.labels(
            backend_name=self.backend_name,
            pool_name=pool_info['name'],
            san_ip=self.san_ip).set(read_latency)

        self.gauge_san_pool_block_read_latency.labels(
            backend_name=self.backend_name,
            pool_name=pool_info['name'],
            san_ip=self.san_ip).set(write_latency)

        self.gauge_san_pool_block_read_latency.labels(
            backend_name=self.backend_name,
            pool_name=pool_info['name'],
            san_ip=self.san_ip).set(other_latency)

        self.gauge_san_pool_block_read_byte_rate.labels(
            backend_name=self.backend_name,
            pool_name=pool_info['name'],
            san_ip=self.san_ip).set(read_throughput / 1024)

        self.gauge_san_pool_block_write_byte_rate.labels(
            backend_name=self.backend_name,
            pool_name=pool_info['name'],
            san_ip=self.san_ip).set(write_throughput / 1024)

        self.gauge_san_pool_block_other_byte_rate.labels(
            backend_name=self.backend_name,
            pool_name=pool_info['name'],
            san_ip=self.san_ip).set(other_throughput / 1024)

    def define_node_metrics(self):
        node_labels = ['backend_name',
                       'san_ip',
                       'node_name',
                       'serial_number']
        self.gauge_san_node_state = Gauge('san_node_state',
                                          'State Node',
                                          node_labels,
                                          registry=self.registry)

    def parse_node_metrics(self, node):
        name = node['name']
        serial = node['serial_number']
        san_ip = node['san_ip']
        state = node['state']
        if state == 'up':
            state = 1
        else:
            state = 0
        self.gauge_san_node_state.labels(
            backend_name=self.backend_name,
            san_ip=san_ip, node_name=name,
            serial_number=serial).set(state)

    def define_disk_metrics(self):
        disk_labels = ['backend_name', 'san_ip', 'name']
        self.gauge_san_disk_state = Gauge('san_disk_state', 'State Disk',
                                          disk_labels,
                                          registry=self.registry)

    def parse_disk_metrics(self, disk):
        name = disk['name']
        state = disk['state']
        if state == 'present':
            state = 1
        else:
            state = 0
        self.gauge_san_disk_state.labels(
            backend_name=self.backend_name,
            san_ip=disk['san_ip'],
            name=name).set(state)

    def parse_metrics(self, data):
        for data_cluster in data['cluster']:
            self.parse_cluster_info(data_cluster)
        if self.optional_metrics.get('cluster'):
            for i in data['cluster']:
                self.parse_cluster_metric(i)
        if self.optional_metrics.get('pool'):
            if len(data['pool']):
                for pool_info in data['pool']:
                    self.parse_pool_info(pool_info)
        if self.optional_metrics.get('node'):
            if len(data['node']):
                for i in data['node']:
                    self.parse_node_metrics(i)
        if self.optional_metrics.get('disk'):
            if len(data['disk']):
                for i in data['disk']:
                    self.parse_disk_metrics(i)

    def get_metrics(self):
        metrics = generate_latest(self.registry)
        return metrics
