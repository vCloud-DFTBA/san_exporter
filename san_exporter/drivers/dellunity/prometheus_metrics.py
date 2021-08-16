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


class DellUnityMetrics(base_driver.Metrics):
    def __init__(self, config):
        super().__init__(config=config)
        labels = ['backend_name', 'san_ip']
        self.backend_name = config['name']
        self.san_ip = config['dellunity_api_ip']
        self.info_san = Info(
            'san_storage', 'Basic information', registry=self.registry)
        self.gauge_san_total_capacity = Gauge(
            'san_totalCapacityMiB', 'Total Capacity in MiB', labels,
            registry=self.registry)
        self.gauge_san_used_capacity = Gauge(
            'san_usedCapacityMiB', 'Used Capacity in MiB', labels,
            registry=self.registry)
        self.gauge_san_free_capacity = Gauge(
            'san_freeCapacityMiB', 'Free Capacity in Mib', labels,
            registry=self.registry)
        self.gauge_san_provisioned_capacity = Gauge(
            'san_provisionedCapacityMiB', 'Provisioned Capacity in MiB',
            labels, registry=self.registry)
        self.gauge_san_total_nodes = Gauge(
            'san_totalNodes', 'Total Nodes', labels, registry=self.registry)
        self.gauge_san_unhealthy_nodes = Gauge(
            'san_unhealthyNodes', 'Unhealthy Nodes', labels,
            registry=self.registry)
        self.gauge_san_online_nodes = Gauge(
            'san_onlineNodes', 'Online Nodes', labels, registry=self.registry)
        if self.optional_metrics.get('pool'):
            self.define_pool_info_metrics()
        if self.optional_metrics.get('node'):
            self.define_node_metrics()
        if self.optional_metrics.get('fcport'):
            self.define_fcport_metrics()
        if self.optional_metrics.get('alert'):
            self.define_alert_metrics()
        if self.optional_metrics.get('lun'):
            self.define_lun_metrics()
        if self.optional_metrics.get('disk'):
            self.define_disk_metrics()

    def parse_system_info(self, system_info):
        self.info_san.info({
            'name': system_info['name'],
            'backend_name': self.backend_name,
            'san_ip': self.san_ip,
            'model': system_info['model'],
            'serial_number': system_info['serial_number'],
            'platform': system_info['platform'],
            'apiVersion': system_info['apiVersion'],
            'softwareVersion': system_info['softwareVersion']
        })
        self.gauge_san_total_capacity.labels(
            backend_name=self.backend_name, san_ip=self.san_ip).set(
            system_info['size_total'] / 1024 / 1024)
        self.gauge_san_used_capacity.labels(
            backend_name=self.backend_name, san_ip=self.san_ip).set(
            system_info['size_used'] / 1024 / 1024)
        self.gauge_san_free_capacity.labels(
            backend_name=self.backend_name, san_ip=self.san_ip).set(
            system_info['size_free'] / 1024 / 1024)
        self.gauge_san_provisioned_capacity.labels(
            backend_name=self.backend_name, san_ip=self.san_ip).set(
            system_info['size_subscribed'] / 1024 / 1024)
        self.gauge_san_total_nodes.labels(
            backend_name=self.backend_name, san_ip=self.san_ip).set(
            system_info['total_nodes'])
        self.gauge_san_online_nodes.labels(
            backend_name=self.backend_name, san_ip=self.san_ip).set(
            system_info['online_nodes'])
        self.gauge_san_unhealthy_nodes.labels(
            backend_name=self.backend_name, san_ip=self.san_ip).set(
            system_info['unhealthy_nodes'])

    def define_pool_info_metrics(self):
        pool_labels = ["backend_name", "san_ip", "pool_name"]
        self.gauge_san_pool_total_capacity = Gauge(
            'san_pool_total_capacity_mib',
            'Total capacity of pool in MiB', pool_labels,
            registry=self.registry)
        self.gauge_san_pool_used_capacity = Gauge(
            'san_pool_used_capacity_mib', 'Used capacity of pool in MiB',
            pool_labels, registry=self.registry)
        self.gauge_san_pool_free_capacity = Gauge(
            'san_pool_free_capacity_mib', 'Free capacity of pool in MiB',
            pool_labels, registry=self.registry)
        self.gauge_san_pool_provisioned_capacity = Gauge(
            'san_pool_provisioned_capacity_mib',
            'Provisioned capacity of pool in MiB', pool_labels,
            registry=self.registry)

    def parse_pool_info(self, pool_info):
        total_capacity = pool_info['size_total']
        used_capacity = pool_info['size_used']
        free_capacity = pool_info['size_free']
        provisioned_capacity = pool_info['size_subscribed']
        self.gauge_san_pool_total_capacity.labels(
            backend_name=self.backend_name, pool_name=pool_info['name'],
            san_ip=self.san_ip).set(total_capacity / 1024 / 1024)
        self.gauge_san_pool_used_capacity.labels(
            backend_name=self.backend_name, pool_name=pool_info['name'],
            san_ip=self.san_ip).set(used_capacity / 1024 / 1024)
        self.gauge_san_pool_free_capacity.labels(
            backend_name=self.backend_name, pool_name=pool_info['name'],
            san_ip=self.san_ip).set(free_capacity / 1024 / 1024)
        self.gauge_san_pool_provisioned_capacity.labels(
            backend_name=self.backend_name, pool_name=pool_info['name'],
            san_ip=self.san_ip).set(provisioned_capacity / 1024 / 1024)

    def define_node_metrics(self):
        node_labels = ['backend_name', 'san_ip', 'node_id']
        self.gauge_san_node_block_read_iops = Gauge(
            'san_node_number_read_io', 'Node Read IOPS', node_labels,
            registry=self.registry)
        self.gauge_san_node_block_write_iops = Gauge(
            'san_node_number_write_io', 'Node Write IOPS', node_labels,
            registry=self.registry)
        self.gauge_san_node_utilization = Gauge(
            'san_cpu_percent_usage', 'Total percentage usage of CPUs',
            node_labels, registry=self.registry)
        self.gauge_san_node_temperature = Gauge(
            'san_node_temperature', 'Node Temperature - degree Celcius',
            node_labels, registry=self.registry)
        self.gauge_san_node_read_data_rate = Gauge(
            'san_node_read_kb', 'Node Read Data Rate - KiB/s',
            node_labels, registry=self.registry)
        self.gauge_san_node_write_data_rate = Gauge(
            'san_node_write_kb', 'Node Write Data Rate - KiB/s',
            node_labels, registry=self.registry)

    def parse_node_metrics(self, node):
        block_read_iops = node['block_read_iops']
        block_write_iops = node['block_write_iops']
        utilization = node['utilization']
        temperature = node['temperature']
        write_byte_rate = node['write_byte_rate']
        read_byte_rate = node['read_byte_rate']
        self.gauge_san_node_block_read_iops.labels(
            backend_name=self.backend_name, san_ip=self.san_ip,
            node_id=node['id']).set(block_read_iops)
        self.gauge_san_node_block_write_iops.labels(
            backend_name=self.backend_name, san_ip=self.san_ip,
            node_id=node['id']).set(block_write_iops)
        self.gauge_san_node_read_data_rate.labels(
            backend_name=self.backend_name, san_ip=self.san_ip,
            node_id=node['id']).set(read_byte_rate / 1024)
        self.gauge_san_node_write_data_rate.labels(
            backend_name=self.backend_name, san_ip=self.san_ip,
            node_id=node['id']).set(write_byte_rate / 1024)
        self.gauge_san_node_utilization.labels(
            backend_name=self.backend_name, san_ip=self.san_ip,
            node_id=node['id']).set(utilization)
        self.gauge_san_node_temperature.labels(
            backend_name=self.backend_name, san_ip=self.san_ip,
            node_id=node['id']).set(temperature)

    def define_fcport_metrics(self):
        fcport_labels = ['backend_name', 'san_ip', 'id']
        self.gauge_san_fcport_read_iops = Gauge(
            'san_port_number_read_io', 'FC Port Read IOPS', fcport_labels,
            registry=self.registry)
        self.gauge_san_fcport_write_iops = Gauge(
            'san_port_number_write_io', 'FC Port Write IOPS', fcport_labels,
            registry=self.registry)
        self.gauge_san_fcport_read_data_rate = Gauge(
            'san_port_read_kb', 'FC Port Read Data Rate - KiB/s',
            fcport_labels, registry=self.registry)
        self.gauge_san_fcport_write_data_rate = Gauge(
            'san_port_write_kb', 'FC Port Write Data Rate - KiB/s',
            fcport_labels, registry=self.registry)

    def parse_fcport_metrics(self, fcport):
        read_iops = fcport['read_iops']
        write_iops = fcport['write_iops']
        read_byte_rate = fcport['read_byte_rate']
        write_byte_rate = fcport['write_byte_rate']
        self.gauge_san_fcport_read_iops.labels(
            backend_name=self.backend_name, san_ip=self.san_ip,
            id=fcport['id']).set(read_iops)
        self.gauge_san_fcport_write_iops.labels(
            backend_name=self.backend_name, san_ip=self.san_ip,
            id=fcport['id']).set(write_iops)
        self.gauge_san_fcport_read_data_rate.labels(
            backend_name=self.backend_name, san_ip=self.san_ip,
            id=fcport['id']).set(read_byte_rate / 1024)
        self.gauge_san_fcport_write_data_rate.labels(
            backend_name=self.backend_name, san_ip=self.san_ip,
            id=fcport['id']).set(write_byte_rate / 1024)

    def define_alert_metrics(self):
        alert_labels = ['backend_name', 'san_ip', 'alert_id', 'log_content']
        self.san_alert = Gauge(
            'san_alert', 'SAN alert', alert_labels, registry=self.registry)

    def parse_alert_metrics(self, alert):
        id = alert['id']
        message = alert['message']
        self.san_alert.labels(
            backend_name=self.backend_name, san_ip=self.san_ip, alert_id=id,
            log_content=message).set(1.0)

    def define_lun_metrics(self):
        lun_labels = ['backend_name', 'san_ip', 'name']
        self.gauge_san_lun_read_iops = Gauge(
            'san_lun_number_read_io', 'LUN Read IOPS', lun_labels,
            registry=self.registry)
        self.gauge_san_lun_write_iops = Gauge(
            'san_lun_number_write_io', 'LUN Write IOPS', lun_labels,
            registry=self.registry)
        self.gauge_san_lun_read_data_rate = Gauge(
            'san_lun_read_kb', 'LUN Read Data Rate - KiB/s', lun_labels,
            registry=self.registry)
        self.gauge_san_lun_write_data_rate = Gauge(
            'san_lun_write_kb', 'LUN Write Data Rate - KiB/s', lun_labels,
            registry=self.registry)
        self.gauge_san_lun_response_time = Gauge(
            'san_lun_response_time_ms', 'LUN Response Time - ms', lun_labels,
            registry=self.registry)

    def parse_lun_metrics(self, lun):
        name = lun['name']
        read_iops = lun['read_iops']
        write_iops = lun['write_iops']
        read_byte_rate = lun['read_byte_rate']
        write_byte_rate = lun['write_byte_rate']
        response_time = lun['response_time']
        self.gauge_san_lun_read_iops.labels(
            backend_name=self.backend_name, san_ip=self.san_ip, name=name).set(
            read_iops)
        self.gauge_san_lun_write_iops.labels(
            backend_name=self.backend_name, san_ip=self.san_ip, name=name).set(
            write_iops)
        self.gauge_san_lun_read_data_rate.labels(
            backend_name=self.backend_name, san_ip=self.san_ip, name=name).set(
            read_byte_rate / 1024)
        self.gauge_san_lun_write_data_rate.labels(
            backend_name=self.backend_name, san_ip=self.san_ip, name=name).set(
            write_byte_rate / 1024)
        self.gauge_san_lun_response_time.labels(
            backend_name=self.backend_name, san_ip=self.san_ip, name=name).set(
            response_time / 1000)

    def define_disk_metrics(self):
        disk_labels = ['backend_name', 'san_ip', 'name']
        self.gauge_san_disk_read_iops = Gauge(
            'san_disk_number_read_io', 'Disk Read IOPS', disk_labels,
            registry=self.registry)
        self.gauge_san_disk_write_iops = Gauge(
            'san_disk_number_write_io', 'Disk Write IOPS', disk_labels,
            registry=self.registry)
        self.gauge_san_disk_read_data_rate = Gauge(
            'san_disk_read_kb', 'Disk Read Data Rate - KiB/s', disk_labels,
            registry=self.registry)
        self.gauge_san_disk_write_data_rate = Gauge(
            'san_disk_write_kb', 'Disk Write Data Rate - KiB/s', disk_labels,
            registry=self.registry)
        self.gauge_san_disk_response_time = Gauge(
            'san_disk_response_time_ms', 'Disk Response Time - ms',
            disk_labels, registry=self.registry)

    def parse_disk_metrics(self, disk):
        name = disk['name']
        read_iops = disk['read_iops']
        write_iops = disk['write_iops']
        read_byte_rate = disk['read_byte_rate']
        write_byte_rate = disk['write_byte_rate']
        response_time = disk['response_time']
        self.gauge_san_disk_write_iops.labels(
            backend_name=self.backend_name, san_ip=self.san_ip, name=name).set(
            write_iops)
        self.gauge_san_disk_read_iops.labels(
            backend_name=self.backend_name, san_ip=self.san_ip, name=name).set(
            read_iops)
        self.gauge_san_disk_read_data_rate.labels(
            backend_name=self.backend_name, san_ip=self.san_ip, name=name).set(
            read_byte_rate / 1024)
        self.gauge_san_disk_write_data_rate.labels(
            backend_name=self.backend_name, san_ip=self.san_ip, name=name).set(
            write_byte_rate / 1024)
        self.gauge_san_disk_response_time.labels(
            backend_name=self.backend_name, san_ip=self.san_ip, name=name).set(
            response_time / 1000)

    def parse_metrics(self, data):
        self.parse_system_info(data['system_info'])
        if self.optional_metrics.get('pool'):
            if len(data['pools']):
                for pool_info in data['pools']:
                    self.parse_pool_info(pool_info)
        if self.optional_metrics.get('node'):
            if len(data['nodes']):
                for i in data['nodes']:
                    self.parse_node_metrics(i)
        if self.optional_metrics.get('fcport'):
            if len(data['fcport']):
                for i in data['fcport']:
                    self.parse_fcport_metrics(i)
        if self.optional_metrics.get('alert'):
            self.san_alert._metrics.clear()
            if len(data['alerts']):
                for i in data['alerts']:
                    self.parse_alert_metrics(i['content'])
        if self.optional_metrics.get('lun'):
            if len(data['luns']):
                for i in data['luns']:
                    self.parse_lun_metrics(i)
        if self.optional_metrics.get('disk'):
            if len(data['disks']):
                for i in data['disks']:
                    self.parse_disk_metrics(i)

    def get_metrics(self):
        metrics = generate_latest(self.registry)
        return metrics
