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

import datetime
import logging
from time import sleep, time
import json
import requests

from san_exporter.utils.utils import cache_data
from san_exporter.drivers import base_driver
from san_exporter.drivers.sc8000 import prometheus_metrics


class SC8000_Exporter(base_driver.ExporterDriver):

    def __init__(self, config=None, interval=10):
        super().__init__(config, interval)
        self.DSM_api_ip = config['DSM_api_ip']
        self.DSM_api_port = config['DSM_api_port']
        self.DSM_username = config['DSM_username']
        self.DSM_password = config['DSM_password']
        self.backend_name = config['name']
        self.sc8000_ip = config['sc8000_ip']
        self.verify_cert = config['verify_cert']
        self.apiversion = config['apiversion']
        self.baseURL = 'https://%s:%s/api/rest/' % (self.DSM_api_ip,
                                                    self.DSM_api_port)
        # define HTTP content headers
        now = datetime.datetime.now() - datetime.timedelta(minutes=15)
        dt_string = now.strftime('%Y-%m-%dT%H:%M:%S')
        self.payload = {'HistoricalFilter': {'FilterTime': 'Other',
                        'StartTime': dt_string, 'UseCurrent': True}}
        self.header = {}
        self.header['Content-Type'] = 'application/json; charset=utf-8'
        self.header['Accept'] = 'application/json'
        self.header['x-dell-api-version'] = self.apiversion
        if not self.verify_cert:
            requests.packages.urllib3.disable_warnings()
        # define the connection session
        self.session = requests.Session()
        self.session.auth = (self.DSM_username, self.DSM_password)

    def login(self):
        REST = '/ApiConnection/Login'
        completeURL = '%s%s' % (self.baseURL, (REST if REST[0] != '/'
                                               else REST[1:]))
        self.session.post(completeURL, headers=self.header,
                          verify=self.verify_cert)

    def logout(self):
        REST = '/ApiConnection/Logout'
        completeURL = '%s%s' % (self.baseURL, (REST if REST[0] != '/'
                                               else REST[1:]))
        self.session.post(completeURL, headers=self.header,
                          verify=self.verify_cert)

    def get_info_DSM(self):
        REST = '/ApiConnection/ApiConnection'
        completeURL = '%s%s' % (self.baseURL, (REST if REST[0] != '/'
                                               else REST[1:]))
        json_data = self.session.get(completeURL, headers=self.header,
                                     verify=self.verify_cert)
        DSM_info = json.loads(json_data.text)
        return DSM_info

    def get_info_SC(self, instanceId_DSM):
        REST = '/ApiConnection/ApiConnection/%s/StorageCenterList' \
            % instanceId_DSM
        completeURL = '%s%s' % (self.baseURL, (REST if REST[0] != '/'
                                               else REST[1:]))
        json_data = self.session.get(completeURL, headers=self.header,
                                     verify=self.verify_cert)
        SC_info = json.loads(json_data.text)
        return SC_info

    def get_info_controller(self, instanceId_SC):
        REST = '/StorageCenter/StorageCenter/%s/ControllerList' \
            % instanceId_SC
        completeURL = '%s%s' % (self.baseURL, (REST if REST[0] != '/'
                                               else REST[1:]))
        json_data = self.session.get(completeURL, headers=self.header,
                                     verify=self.verify_cert)
        info_controller = json.loads(json_data.text)
        return info_controller

    def get_instanceId_SC(self, SC_info):
        list_instanceId_sc = []
        if self.sc8000_ip == 'all':
            for element in SC_info:
                list_instanceId_sc.append(
                    {element['name']: [element['instanceId'], element['hostOrIpAddress']]})
            return list_instanceId_sc
        else:
            for ip in self.sc8000_ip:
                for element in SC_info:
                    if ip == element['hostOrIpAddress']:
                        list_instanceId_sc.append(
                            {element['name']: [element['instanceId'], element['hostOrIpAddress']]})
            return list_instanceId_sc

    def get_IOUsage_controller(self, instanceId_controller):
        REST = '/StorageCenter/ScController/%s/GetHistoricalIoUsage' \
            % instanceId_controller
        completeURL = '%s%s' % (self.baseURL, (REST if REST[0] != '/'
                                               else REST[1:]))
        json_data = self.session.post(completeURL,
                                      data=json.dumps(self.payload,
                                                      ensure_ascii=False).encode('utf-8'),
                                      headers=self.header, verify=self.verify_cert)
        return json.loads(json_data.text)

    def get_info_port(self, ID_SC):
        REST = '/StorageCenter/StorageCenter/%s/ControllerPortList' \
            % ID_SC
        completeURL = '%s%s' % (self.baseURL, (REST if REST[0] != '/'
                                               else REST[1:]))
        json_data = self.session.get(completeURL, headers=self.header,
                                     verify=self.verify_cert)
        return json.loads(json_data.text)

    def get_IOUsage_port(self, instanceId_port):
        REST = \
            '/StorageCenter/ScControllerPort/%s/GetHistoricalIoUsage' \
            % instanceId_port
        completeURL = '%s%s' % (self.baseURL, (REST if REST[0] != '/'
                                               else REST[1:]))
        json_data = self.session.post(completeURL,
                                      data=json.dumps(self.payload,
                                                      ensure_ascii=False).encode('utf-8'),
                                      headers=self.header, verify=self.verify_cert)
        return json.loads(json_data.text)

    def get_diskfolder(self, instanceId_SC):
        REST = \
            '/StorageCenter/StorageCenter/%s/StorageTypeStorageUsage' \
            % instanceId_SC
        completeURL = '%s%s' % (self.baseURL, (REST if REST[0] != '/'
                                               else REST[1:]))
        json_data = self.session.get(completeURL, headers=self.header,
                                     verify=self.verify_cert)
        return json.loads(json_data.text)

    def get_IOUsage_volume(self, instanceId_sc):
        REST = '/StorageCenter/StorageCenter/%s/GetLatestVolumeIoUsage' \
            % instanceId_sc
        completeURL = '%s%s' % (self.baseURL, (REST if REST[0] != '/'
                                               else REST[1:]))
        json_data = self.session.post(completeURL, headers=self.header,
                                      verify=self.verify_cert)
        return json.loads(json_data.text)

    def get_alert(self, instanceId_SC):
        REST = '/StorageCenter/StorageCenter/%s/AlertList' \
            % instanceId_SC
        completeURL = '%s%s' % (self.baseURL, (REST if REST[0] != '/'
                                               else REST[1:]))
        json_data = self.session.get(completeURL, headers=self.header,
                                     verify=self.verify_cert)
        return json.loads(json_data.text)

    def get_space_sc(self, instanceId_SC):
        REST = '/StorageCenter/StorageCenter/%s/StorageUsage' \
            % instanceId_SC
        completeURL = '%s%s' % (self.baseURL, (REST if REST[0] != '/'
                                               else REST[1:]))
        json_data = self.session.get(completeURL, headers=self.header,
                                     verify=self.verify_cert)
        return json.loads(json_data.text)

    def get_server_sc(self, instanceId_SC):
        REST = '/StorageCenter/StorageCenter/%s/ServerList' \
            % instanceId_SC
        completeURL = '%s%s' % (self.baseURL, (REST if REST[0] != '/'
                                               else REST[1:]))
        json_data = self.session.get(completeURL, headers=self.header,
                                     verify=self.verify_cert)
        return json.loads(json_data.text)

    def get_alert(self, instanceId_SC):
        REST = '/StorageCenter/StorageCenter/%s/AlertList' \
            % instanceId_SC
        completeURL = '%s%s' % (self.baseURL, (REST if REST[0] != '/'
                                               else REST[1:]))
        json_data = self.session.get(completeURL, headers=self.header,
                                     verify=self.verify_cert)
        return json.loads(json_data.text)

    def run(self):
        while True:
            try:
                if time() - self.time_last_request > self.timeout:
                    sleep(self.interval)
                    continue
                self.login()
                data = {}
                DSM_info = self.get_info_DSM()
                data['DSM_info'] = DSM_info
                # get info SC
                SC_info = self.get_info_SC(DSM_info['instanceId'])
                data['SC_info'] = SC_info
                # map san_name to san_ip and san_id
                list_instanceId_SC = self.get_instanceId_SC(SC_info)
                data['SCmap_name_ip'] = list_instanceId_SC
                info_controller = []
                info_port = []
                info_disk = []
                list_instanceId_controller = []
                map_IdtoIp_controller = {}
                list_instanceId_port = []
                iousage_volume = []
                parse_alert = []
                space_SC = []
                server_sc = []
                id_sc = []
                SCmap_name_ip = {}
                SCmap_serial_ip = {}
                for ID in list_instanceId_SC:
                    SCmap_name_ip.update(ID)
                    SCmap_serial_ip.update(
                        {list(ID.values())[0][0]: list(ID.values())[0][1]})
                    id_sc.append(list(ID.values())[0][0])
                    get_controller = \
                        self.get_info_controller(list(ID.values())[0][0])
                    get_port = \
                        self.get_info_port(list(ID.values())[0][0])
                    info_disk.append(self.get_diskfolder(
                        list(ID.values())[0][0]))
                    info_controller.append(
                        {list(ID.keys())[0]: get_controller})
                    info_port.append({list(ID.keys())[0]: get_port})
                    iousage_volume.append(
                        self.get_IOUsage_volume(list(ID.values())[0][0]))
                    parse_alert.append(self.get_alert(list(ID.values())[0][0]))
                    space_SC.append(self.get_space_sc(list(ID.values())[0][0]))
                    server_sc.append(self.get_server_sc(
                        list(ID.values())[0][0]))
                    for k in get_controller:
                        map_IdtoIp_controller.update(
                            {k['instanceId']: k['ipAddress']})
                        list_instanceId_controller.append(k['instanceId'])
                    for j in get_port:
                        list_instanceId_port.append(j['instanceId'])
                data['SCmap_name_ip'] = SCmap_name_ip
                data['SCmap_serial_ip'] = SCmap_serial_ip
                data['id_sc'] = id_sc
                data['info_controller'] = info_controller
                data['info_port'] = info_port
                data['info_disk'] = info_disk
                data['iousage_volume'] = iousage_volume
                data['get_alert'] = parse_alert
                data['space_sc'] = space_SC
                data['server_sc'] = server_sc
                # get IOUsage SCcontroller
                IOUsage_controller = []
                for instanceId_controller in list_instanceId_controller:
                    IOUsage_controller.append(
                        self.get_IOUsage_controller(instanceId_controller))
                data['IOUsage_controller'] = IOUsage_controller
                data['map_ipsccontroller'] = map_IdtoIp_controller
                # get IOUsage port
                IOUsage_port = []
                for ID_port in list_instanceId_port:
                    IOUsage_port.append(self.get_IOUsage_port(ID_port))
                data['IOUsage_port'] = IOUsage_port
                cache_data(self.cache_file, data)
            except:
                logging.error('Error: ', exc_info=True)
            finally:
                self.logout()
            sleep(self.interval)


def main(config, interval):
    SC8000_metrics = prometheus_metrics.SC8000_Metrics(config=config)
    SC8000_exporter = SC8000_Exporter(config, interval)
    SC8000_exporter.start()
    return (SC8000_exporter, SC8000_metrics)
