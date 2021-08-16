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

from prometheus_client import Gauge, Info, generate_latest

from san_exporter.drivers import base_driver


class SC8000_Metrics(base_driver.Metrics):

    def __init__(self, config):
        labels = ['backend_name']
        super().__init__(config=config)
        self.backend_name = config['name']
        self.san_ip = {}
        self.choice_severity_alert = config['severity_alert']
        self.info_san_DSM = Info('san_dsm_info', 'Basic DSM information',
                                 registry=self.registry)
        self.info_sum_controller = \
            Gauge('san_totalNodes',
                  'Summary controller in SC',
                  ['san_name', 'backend_name', 'san_ip'],
                  registry=self.registry)
        self.info_sum_port = \
            Gauge('san_port_total', 'Total port in SC',
                  ['san_name', 'backend_name', 'san_ip'],
                  registry=self.registry)
        self.define_SC_info()
        self.define_controller_info()
        self.define_IOUsage_controller()
        self.define_info_port()
        self.define_IOUsage_port()
        self.define_space_disk()
        self.define_iousage_volume_disk()
        self.define_alert()
        self.define_space_sc()
        self.define_server_sc()

    def define_info_port(self):
        labels = [
            'instanceid_sccontroller',
            'backend_name',
            'instanceid',
            'status',
            'san_name',
            'san_ip',
        ]
        self.info_san_port = Gauge('san_port_sc', 'Info port in SC',
                                   labels, registry=self.registry)

    def define_controller_info(self):
        labels = [
            'ip_controller',
            'status',
            'instanceid',
            'san_name',
            'backend_name',
            'san_ip',
        ]
        self.info_san_controller = \
            Gauge('san_controller_availableMemoryMib',
                  'Info and availableMemory in Mib of controller ',
                  labels, registry=self.registry)

    def define_SC_info(self):
        labels = [
            'san_ip',
            'backend_name',
            'sc_serialnumber',
            'instanceid',
            'san_name',
            'status',
        ]
        self.info_san_SC = Gauge('san_sc_info',
                                 'SC information by DSM managed',
                                 labels, registry=self.registry)

    def define_IOUsage_controller(self):
        labels = ['ip_controller', 'san_name', 'backend_name', 'san_ip']
        self.ReadLatency_san_controller = \
            Gauge('san_controller_read_service_time_ms',
                  'Controller Read Response Time - ms/op', labels,
                  registry=self.registry)
        self.WriteLatency_san_controller = \
            Gauge('san_controller_write_service_time_ms',
                  'Controller Write Response Time - ms/op', labels,
                  registry=self.registry)
        self.ReadKbPerSecond_san_controller = \
            Gauge('san_controller_read_kb',
                  'Controller Read Data Rate - KiB/s', labels,
                  registry=self.registry)
        self.AverageKbPerIo_san_controller = \
            Gauge('san_controller_average_IOSize_kb',
                  'Controller Average Transfer Size - KiB/op', labels,
                  registry=self.registry)
        self.WriteKbPerSecond_san_controller = \
            Gauge('san_controller_write_kb',
                  'Controller Write Data Rate - KiB/s', labels,
                  registry=self.registry)
        self.TotalKbPerSecond_san_controller = \
            Gauge('san_controller_total_kb',
                  'Controller Total Data Rate - KiB/s', labels,
                  registry=self.registry)
        self.writeIops_san_controller = \
            Gauge('san_controller_number_write_io',
                  'Controller Write I/O Rate - ops/s', labels,
                  registry=self.registry)
        self.readIops_san_controller = \
            Gauge('san_controller_number_read_io',
                  'Controller Read I/O Rate - ops/s ', labels,
                  registry=self.registry)
        self.totalIops_san_controller = \
            Gauge('san_controller_number_total_io',
                  'Controller Total I/O Rate - ops/s ', labels,
                  registry=self.registry)
        self.cpuPercentUsage_san_controller = \
            Gauge('san_cpu_percent_usage',
                  'Controller The percent usage of the CPU', labels,
                  registry=self.registry)
        self.memoryPercentUsage_san_controller = \
            Gauge('san_memory_percent_usage',
                  'Controller The percent usage of the memory', labels,
                  registry=self.registry)

    def define_IOUsage_port(self):
        labels = ['instanceid_port', 'san_name', 'backend_name',
                  'san_ip']
        self.ReadLatency_san_port = \
            Gauge('san_port_read_service_time_ms',
                  'Port Read Response Time - ms/op', labels,
                  registry=self.registry)
        self.WriteLatency_san_port = \
            Gauge('san_port_write_service_time_ms',
                  'Port Write Response Time - ms/op', labels,
                  registry=self.registry)
        self.ReadKbPerSecond_san_port = \
            Gauge('san_port_read_kb',
                  'Port Read Data Rate - KiB/s', labels,
                  registry=self.registry)
        self.AverageKbPerIo_san_port = \
            Gauge('san_port_average_IOSize',
                  'Port Average Transfer Size - KiB/op', labels,
                  registry=self.registry)
        self.WriteKbPerSecond_san_port = \
            Gauge('san_port_write_kb',
                  'Port Write Data Rate - KiB/s', labels,
                  registry=self.registry)
        self.TotalKbPerSecond_san_port = \
            Gauge('san_port_total_kb',
                  'Port Total Data Rate - KiB/s', labels,
                  registry=self.registry)
        self.writeIops_san_port = \
            Gauge('san_port_number_write_io',
                  'Port Write I/O Rate - ops/s', labels,
                  registry=self.registry)
        self.readIops_san_port = \
            Gauge('san_port_number_read_io',
                  'Port Read I/O Rate - ops/s', labels,
                  registry=self.registry)
        self.totalIops_san_port = \
            Gauge('san_port_number_total_io',
                  'Port Total I/O Rate - ops/s', labels,
                  registry=self.registry)

    def define_space_disk(self):
        labels = ['san_name', 'backend_name', 'pool_name', 'san_ip']
        self.freeSpace_san_disk = Gauge('san_pool_free_capacity_mib',
                                        'Free of pool in MiB', labels,
                                        registry=self.registry)
        self.useSpace_san_disk = Gauge('san_pool_use_capacity_mib',
                                       'Use of pool in MiB', labels,
                                       registry=self.registry)
        self.allocatedSpace_san_disk = \
            Gauge('san_pool_total_capacity_mib',
                  'Total capacity of pool in MiB', labels,
                  registry=self.registry)

    def define_iousage_volume_disk(self):
        labels = ['name_volume', 'san_name', 'backend_name', 'san_ip']
        self.ReadLatency_san_volume = \
            Gauge('san_volume_read_service_time_ms',
                  'Volume Read Response Time - ms/op', labels,
                  registry=self.registry)
        self.WriteLatency_san_volume = \
            Gauge('san_volume_write_service_time_ms',
                  'Volume Write Response Time - ms/op', labels,
                  registry=self.registry)
        self.ReadKbPerSecond_san_volume = \
            Gauge('san_volume_read_kb',
                  'Volume Read Data Rate - KiB/s', labels,
                  registry=self.registry)
        self.AverageKbPerIo_san_volume = \
            Gauge('san_volume_average_IOSize',
                  'Volume The Average Transfer Size - KiB/op', labels,
                  registry=self.registry)
        self.WriteKbPerSecond_san_volume = \
            Gauge('san_volume_write_kb',
                  'Volume Write Data Rate - KiB/s', labels,
                  registry=self.registry)
        self.TotalKbPerSecond_san_volume = \
            Gauge('san_volume_total_kb',
                  'Volume Total Data Rate - KiB/s', labels,
                  registry=self.registry)
        self.writeIops_san_volume = \
            Gauge('san_volume_number_write_io',
                  'Volume Write I/O Rate - ops/s', labels,
                  registry=self.registry)
        self.readIops_san_volume = \
            Gauge('san_volume_number_read_io',
                  'Volume Read I/O Rate - ops/s', labels,
                  registry=self.registry)
        self.totalIops_san_volume = \
            Gauge('san_volume_number_total_io',
                  'Volume Total I/O Rate - ops/s', labels,
                  registry=self.registry)

    def define_alert(self):
        labels = [
            'log_content',
            'backend_name',
            'ip_controller',
            'status',
            'scname',
            'san_ip',
        ]
        self.san_alert = Gauge('san_alert', 'SAN alert', labels,
                               registry=self.registry)

    def define_space_sc(self):
        labels = ['backend_name', 'san_name', 'san_ip']
        self.availablespace_san_sc = \
            Gauge('san_sc_total_capacity_mib',
                  'Total capacity of SC in MiB', labels,
                  registry=self.registry)
        self.usespace_san_sc = \
            Gauge('san_sc_use_capacity_mib',
                  'Use of SC in MiB', labels, registry=self.registry)
        self.freespace_san_sc = \
            Gauge('san_sc_free_capacity_mib',
                  'Free of SC in MiB', labels, registry=self.registry)

    def define_server_sc(self):
        labels = [
            'backend_name',
            'status',
            'server',
            'san_name',
            'connectivity',
            'san_ip',
        ]
        self.server_san_sc = \
            Gauge('san_sc_server',
                  'Info servers for the Storage Center', labels,
                  registry=self.registry)

    def parse_IOUsage_volume(self, IOUsage_volume, sanmap):
        for p in IOUsage_volume:
            for element in p:
                san_name = element['scName']
                self.ReadLatency_san_volume.labels(
                    san_ip=sanmap[san_name][1],
                    san_name=san_name,
                    backend_name=self.backend_name,
                    name_volume=element['instanceName'])\
                    .set(element['readLatency'] / 1000)
                self.WriteLatency_san_volume.labels(
                    san_ip=sanmap[san_name][1],
                    san_name=san_name,
                    backend_name=self.backend_name,
                    name_volume=element['instanceName'])\
                    .set(element['writeLatency'] / 1000)
                self.ReadKbPerSecond_san_volume.labels(
                    san_ip=sanmap[san_name][1],
                    san_name=san_name,
                    backend_name=self.backend_name,
                    name_volume=element['instanceName'])\
                    .set(element['readKbPerSecond'])
                self.AverageKbPerIo_san_volume.labels(
                    san_ip=sanmap[san_name][1],
                    san_name=san_name,
                    backend_name=self.backend_name,
                    name_volume=element['instanceName'])\
                    .set(element['averageKbPerIo'])
                self.WriteKbPerSecond_san_volume.labels(
                    san_ip=sanmap[san_name][1],
                    san_name=san_name,
                    backend_name=self.backend_name,
                    name_volume=element['instanceName'])\
                    .set(element['writeKbPerSecond'])
                self.TotalKbPerSecond_san_volume.labels(
                    san_ip=sanmap[san_name][1],
                    san_name=san_name,
                    backend_name=self.backend_name,
                    name_volume=element['instanceName'])\
                    .set(element['totalKbPerSecond'])
                self.writeIops_san_volume.labels(
                    san_ip=sanmap[san_name][1],
                    san_name=san_name,
                    backend_name=self.backend_name,
                    name_volume=element['instanceName'])\
                    .set(element['writeIops'])
                self.readIops_san_volume.labels(
                    san_ip=sanmap[san_name][1],
                    san_name=san_name,
                    backend_name=self.backend_name,
                    name_volume=element['instanceName'])\
                    .set(element['readIops'])
                self.totalIops_san_volume.labels(
                    san_ip=sanmap[san_name][1],
                    san_name=san_name,
                    backend_name=self.backend_name,
                    name_volume=element['instanceName'])\
                    .set(element['totalIops'])

    def parse_DSM_info(self, DSM_info):
        self.info_san_DSM.info({
            'dsm_ip': DSM_info['hostName'],
            'backend_name': self.backend_name,
            'provider': DSM_info['provider'],
            'instanceid': DSM_info['instanceId'],
            'apiVerison': DSM_info['apiVersion'],
        })

    def parse_SC_info(self, SC_info):
        for p in SC_info:
            self.info_san_SC.labels(
                san_ip=p['hostOrIpAddress'],
                backend_name=self.backend_name,
                sc_serialnumber=p['scSerialNumber'],
                instanceid=p['instanceId'],
                status=p['status'],
                san_name=p['scName'],
            )

    def parse_controller_info(self, info_controller, sanmap):
        for p in info_controller:
            San_name = list(p.keys())[0]
            info_SCcontroller = list(p.values())[0]

            self.info_sum_controller.labels(
                san_ip=sanmap[San_name][1],
                san_name=San_name,
                backend_name=self.backend_name)\
                .set(len(info_SCcontroller))
            for info in info_SCcontroller:
                self.info_san_controller.labels(
                    san_ip=sanmap[San_name][1],
                    san_name=San_name,
                    instanceid=info['instanceId'],
                    ip_controller=info['ipAddress'],
                    status=info['status'],
                    backend_name=self.backend_name)\
                    .set(int(info['availableMemory'].split()[0]) / (1024 * 1024))

    def parse_IOUsage_controller(
        self,
        IOUsage_controller,
        map_ip,
        sanmap,
    ):
        for p in IOUsage_controller:
            for element in p:
                san_name = element['scName']
                self.san_ip.update(
                    {map_ip[str(element['instanceId'])]: sanmap[san_name][1]})
                self.ReadLatency_san_controller.labels(
                    san_ip=sanmap[san_name][1],
                    san_name=san_name,
                    backend_name=self.backend_name,
                    ip_controller=map_ip[str(element['instanceId'])])\
                    .set(element['readLatency'] / 1000)
                self.WriteLatency_san_controller.labels(
                    san_ip=sanmap[san_name][1],
                    san_name=san_name,
                    backend_name=self.backend_name,
                    ip_controller=map_ip[str(element['instanceId'])])\
                    .set(element['writeLatency'] / 1000)
                self.ReadKbPerSecond_san_controller.labels(
                    san_ip=sanmap[san_name][1],
                    san_name=san_name,
                    backend_name=self.backend_name,
                    ip_controller=map_ip[str(element['instanceId'])])\
                    .set(element['readKbPerSecond'])
                self.AverageKbPerIo_san_controller.labels(
                    san_ip=sanmap[san_name][1],
                    san_name=san_name,
                    backend_name=self.backend_name,
                    ip_controller=map_ip[str(element['instanceId'])])\
                    .set(element['averageKbPerIo'])
                self.WriteKbPerSecond_san_controller.labels(
                    san_ip=sanmap[san_name][1],
                    san_name=san_name,
                    backend_name=self.backend_name,
                    ip_controller=map_ip[str(element['instanceId'])])\
                    .set(element['writeKbPerSecond'])
                self.TotalKbPerSecond_san_controller.labels(
                    san_ip=sanmap[san_name][1],
                    san_name=san_name,
                    backend_name=self.backend_name,
                    ip_controller=map_ip[str(element['instanceId'])])\
                    .set(element['totalKbPerSecond'])
                self.writeIops_san_controller.labels(
                    san_ip=sanmap[san_name][1],
                    san_name=san_name,
                    backend_name=self.backend_name,
                    ip_controller=map_ip[str(element['instanceId'])])\
                    .set(element['writeIops'])
                self.readIops_san_controller.labels(
                    san_ip=sanmap[san_name][1],
                    san_name=san_name,
                    backend_name=self.backend_name,
                    ip_controller=map_ip[str(element['instanceId'])])\
                    .set(element['readIops'])
                self.totalIops_san_controller.labels(
                    san_ip=sanmap[san_name][1],
                    san_name=san_name,
                    backend_name=self.backend_name,
                    ip_controller=map_ip[str(element['instanceId'])])\
                    .set(element['totalIops'])
                self.cpuPercentUsage_san_controller.labels(
                    san_ip=sanmap[san_name][1],
                    san_name=san_name,
                    backend_name=self.backend_name,
                    ip_controller=map_ip[str(element['instanceId'])])\
                    .set(element['cpuPercentUsage'])
                self.memoryPercentUsage_san_controller.labels(
                    san_ip=sanmap[san_name][1],
                    san_name=san_name,
                    backend_name=self.backend_name,
                    ip_controller=map_ip[str(element['instanceId'])])\
                    .set(element['memoryPercentUsage'])

    def parse_info_port(self, info_port, sanmap):
        for p in info_port:
            San_name = list(p.keys())[0]
            info_element_port = list(p.values())[0]
            self.info_sum_port.labels(
                san_ip=sanmap[San_name][1],
                san_name=San_name,
                backend_name=self.backend_name).set(len(info_element_port))
            for element in info_element_port:
                self.info_san_port.labels(
                    san_ip=sanmap[San_name][1],
                    backend_name=self.backend_name,
                    status=element['status'],
                    instanceid=element['instanceId'],
                    instanceid_sccontroller=element['controller']['instanceId'],
                    san_name=San_name
                )

    def parse_IOUsage_port(self, IOUsage_port, sanmap):
        for p in IOUsage_port:
            for element in p:
                san_name = element['scName']
                self.ReadLatency_san_port.labels(
                    san_ip=sanmap[san_name][1],
                    san_name=san_name,
                    backend_name=self.backend_name,
                    instanceid_port=element['instanceName'])\
                    .set(element['readLatency'] / 1000)
                self.WriteLatency_san_port.labels(
                    san_ip=sanmap[san_name][1],
                    san_name=san_name,
                    backend_name=self.backend_name,
                    instanceid_port=element['instanceName'])\
                    .set(element['writeLatency'] / 1000)
                self.ReadKbPerSecond_san_port.labels(
                    san_ip=sanmap[san_name][1],
                    san_name=san_name,
                    backend_name=self.backend_name,
                    instanceid_port=element['instanceName'])\
                    .set(element['readKbPerSecond'])
                self.AverageKbPerIo_san_port.labels(
                    san_ip=sanmap[san_name][1],
                    san_name=san_name,
                    backend_name=self.backend_name,
                    instanceid_port=element['instanceName'])\
                    .set(element['averageKbPerIo'])
                self.WriteKbPerSecond_san_port.labels(
                    san_ip=sanmap[san_name][1],
                    san_name=san_name,
                    backend_name=self.backend_name,
                    instanceid_port=element['instanceName'])\
                    .set(element['writeKbPerSecond'])
                self.TotalKbPerSecond_san_port.labels(
                    san_ip=sanmap[san_name][1],
                    san_name=san_name,
                    backend_name=self.backend_name,
                    instanceid_port=element['instanceName'])\
                    .set(element['totalKbPerSecond'])
                self.writeIops_san_port.labels(
                    san_ip=sanmap[san_name][1],
                    san_name=san_name,
                    backend_name=self.backend_name,
                    instanceid_port=element['instanceName'])\
                    .set(element['writeIops'])
                self.readIops_san_port.labels(
                    san_ip=sanmap[san_name][1],
                    san_name=san_name,
                    backend_name=self.backend_name,
                    instanceid_port=element['instanceName'])\
                    .set(element['readIops'])
                self.totalIops_san_port.labels(
                    san_ip=sanmap[san_name][1],
                    san_name=san_name,
                    backend_name=self.backend_name,
                    instanceid_port=element['instanceName'])\
                    .set(element['totalIops'])

    def parse_space_disk(self, space_disk, sanmap):
        for i in space_disk:
            for element in i:
                san_name = element['scName']
                self.freeSpace_san_disk.labels(
                    san_ip=sanmap[san_name][1],
                    san_name=san_name,
                    backend_name=self.backend_name,
                    pool_name=element['instanceName'])\
                    .set(int(element['freeSpace'].split()[0]) / (1024 * 1024))
                self.useSpace_san_disk.labels(
                    san_ip=sanmap[san_name][1],
                    san_name=san_name,
                    backend_name=self.backend_name,
                    pool_name=element['instanceName'])\
                    .set(int(element['usedSpace'].split()[0]) / (1024 * 1024))
                self.allocatedSpace_san_disk.labels(
                    san_ip=sanmap[san_name][1],
                    san_name=san_name,
                    backend_name=self.backend_name,
                    pool_name=element['instanceName'])\
                    .set(int(element['allocatedSpace'].split()[0]) / (1024 * 1024))

    def parse_alert(self, get_alert, map_ip):
        self.san_alert._metrics.clear()
        for p in get_alert:
            for element in p:
                if element['status'] in self.choice_severity_alert:
                    if not element['acknowledged']:
                        ip_controller = map_ip[str(
                            element['controller']['instanceId'])]
                        self.san_alert.labels(
                            scname=element['scName'],
                            log_content=element['message'],
                            status=element['status'],
                            backend_name=self.backend_name,
                            ip_controller=ip_controller,
                            san_ip=self.san_ip[ip_controller],
                        ).set(1)

    def parse_space_sc(self, space_sc, sanmap):
        for element in space_sc:
            san_name = element['scName']
            self.freespace_san_sc.labels(
                san_ip=sanmap[san_name][1],
                san_name=san_name,
                backend_name=self.backend_name)\
                .set(int(element['freeSpace'].split()[0]) / (1024 * 1024))
            self.usespace_san_sc.labels(
                san_ip=sanmap[san_name][1],
                san_name=san_name,
                backend_name=self.backend_name)\
                .set(int(element['usedSpace'].split()[0]) / (1024 * 1024))
            self.availablespace_san_sc.labels(
                san_ip=sanmap[san_name][1],
                san_name=san_name,
                backend_name=self.backend_name)\
                .set(int(element['availableSpace'].split()[0]) / (1024 * 1024))

    def parse_server_sc(self, server_sc, sanmap):
        for p in server_sc:
            for element in p:
                san_name = element['scName']
                if element['status'] == 'Down':
                    self.server_san_sc.labels(
                        san_ip=sanmap[san_name][1],
                        san_name=san_name,
                        server=element['name'],
                        status=element['status'],
                        backend_name=self.backend_name,
                        connectivity=element['connectivity'],
                    ).set(2)
                elif element['status'] == 'Degraded':
                    self.server_san_sc.labels(
                        san_ip=sanmap[san_name][1],
                        san_name=san_name,
                        server=element['name'],
                        status=element['status'],
                        backend_name=self.backend_name,
                        connectivity=element['connectivity'],
                    ).set(1)
                else:
                    self.server_san_sc.labels(
                        san_ip=sanmap[san_name][1],
                        san_name=san_name,
                        server=element['name'],
                        status=element['status'],
                        backend_name=self.backend_name,
                        connectivity=element['connectivity'],
                    )

    def parse_metrics(self, data):
        self.parse_DSM_info(data['DSM_info'])
        self.parse_SC_info(data['SC_info'])
        self.parse_controller_info(data['info_controller'],
                                   data['SCmap_name_ip'])
        self.parse_IOUsage_controller(data['IOUsage_controller'],
                                      data['map_ipsccontroller'],
                                      data['SCmap_name_ip'])
        self.parse_info_port(data['info_port'], data['SCmap_name_ip'])
        self.parse_IOUsage_port(data['IOUsage_port'],
                                data['SCmap_name_ip'])
        self.parse_space_disk(data['info_disk'], data['SCmap_name_ip'])
        self.parse_IOUsage_volume(data['iousage_volume'],
                                  data['SCmap_name_ip'])
        self.parse_alert(data['get_alert'], data['map_ipsccontroller'])
        self.parse_space_sc(data['space_sc'], data['SCmap_name_ip'])
        self.parse_server_sc(data['server_sc'], data['SCmap_name_ip'])

    def get_metrics(self):
        metrics = generate_latest(self.registry)
        return metrics
