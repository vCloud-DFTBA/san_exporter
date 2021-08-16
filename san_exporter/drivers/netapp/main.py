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

from time import sleep, time

import requests
from san_exporter.drivers import base_driver
from san_exporter.drivers.netapp import prometheus_metrics
from san_exporter.utils.utils import cache_data


class NetAppExporter(base_driver.ExporterDriver):

    def __init__(self, config=None, interval=10):
        super().__init__(config, interval)
        self.netapp_api_ip = config['netapp_api_ip']
        self.netapp_api_port = config['netapp_api_port']
        self.netapp_username = config['netapp_username']
        self.netapp_password = config['netapp_password']
        self.backend_name = config['name']
        self.baseURL = 'https://' + self.netapp_api_ip + '/api'
        self.auth = (self.netapp_username, self.netapp_password)
        self.headers = {'Accept': 'application/json',
                        'Content-Type': 'application/json'}

    def get_cluster_metrics(self):
        response = requests.get(self.baseURL + '/cluster',
                                headers=self.headers, auth=self.auth,
                                verify=False).json()
        cluster_data = {
            'name': response['name'],
            'version': response['version']['full'],
            'read_iops': response['metric']['iops']['read'],
            'write_iops': response['metric']['iops']['write'],
            'other_iops': response['metric']['iops']['other'],
            'read_latency': response['metric']['latency']['read'],
            'write_latency': response['metric']['latency']['write'],
            'other_latency': response['metric']['latency']['other'],
            'read_throughput': response['metric']['throughput']['read'],
            'write_throughput': response['metric']['throughput']['write'],
            'other_throughput': response['metric']['throughput']['other'],
            'status': response['metric']['status']}
        return cluster_data

    def get_node_info(self):
        response = requests.get(self.baseURL + '/cluster/nodes?fields=name,'
                                               'serial_number,'
                                               'state,model,'
                                               'version',
                                headers=self.headers, auth=self.auth,
                                verify=False).json()
        node_data = []
        for t in response['records']:
            data = {
                'name': t['name'],
                'state': t['state'],
                'model': t['model'],
                'serial_number': t['serial_number'],
                'version': t['version']['full'],
            }
            node_data.append(data)
        return node_data

    def get_pool_info(self):
        response = requests.get(
            self.baseURL + '/storage/volumes?fields=metric,'
                           'state,space',
            headers=self.headers,
            auth=self.auth,
            verify=False).json()
        pool_data = []
        for t in response['records']:
            if t['name'].startswith('agg'):
                data = {
                    'name': t['name'],
                    'size_total': t['space']['available'],
                    'size_used': t['space']['used'],
                    'read_iops': t['metric']['iops']['read'],
                    'write_iops': t['metric']['iops']['write'],
                    'other_iops': t['metric']['iops']['other'],
                    'read_latency': t['metric']['latency']['read'],
                    'write_latency': t['metric']['latency']['write'],
                    'other_latency': t['metric']['latency']['other'],
                    'read_throughput': t['metric']['throughput']['read'],
                    'write_throughput': t['metric']['throughput']['write'],
                    'other_throughput': t['metric']['throughput']['other'],
                    'status': t['metric']['status']}
                pool_data.append(data)
        return pool_data

    def get_disk_info(self):
        response = requests.get(
            self.baseURL + '/storage/disks?fields=name,'
                           'state,model,serial_number',
            headers=self.headers, auth=self.auth,
            verify=False).json()
        disk_data = []
        for t in response['records']:
            data = {
                'name': t['name'],
                'state': t['state'],
                'model': t['model'],
                'serial_number': t['serial_number'],
            }
            disk_data.append(data)
        return disk_data

    def run(self):
        while True:
            if time() - self.time_last_request > self.timeout:
                sleep(self.interval)
                continue
            data = {}
            data['cluster'] = self.get_cluster_metrics()
            data['node'] = self.get_node_info()
            data['pool'] = self.get_pool_info()
            data['disk'] = self.get_disk_info()
            cache_data(self.cache_file, data)
            sleep(self.interval)


def main(config, interval):
    netapp_metrics = prometheus_metrics.NetAppMetrics(config=config)
    netapp_exporter = NetAppExporter(config, interval)
    netapp_exporter.start()
    return (netapp_exporter, netapp_metrics)
