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

"""
All driver must have this file and must define two classes:

    class StorageNameExporter(base_driver.ExporterDriver):
        # define the apis connect and get data from storage

    class StorageMetrics(base_driver.Metrics):
        # define the metrics and parse data from cache file to metrics
"""

import logging
from time import sleep, time

from san_exporter.utils.utils import cache_data

from san_exporter.drivers import base_driver
from san_exporter.drivers.dummy import prometheus_metrics


class DummyExporter(base_driver.ExporterDriver):

    def __init__(self, config=None, interval=300):
        super().__init__(config, interval)
        self.dummy_backend_url = config['dummy_backend_url']
        self.dummy_backend_username = config['dummy_backend_username']
        self.dummy_backend_password = config['dummy_backend_password']
        self.backend_name = config['name']
        self.client = None

    def _create_client(self):
        return None

    def client_login(self):
        try:
            logging.debug("Connecting to Dummy Storage")
            self.client.login(
                self.dummy_backend_username,
                self.dummy_backend_password)
            logging.info("Logged in to: " + self.dummy_backend_url)
        except Exception as ex:
            msg = (
                "Failed to Login to Dummy Storage at (%(url)s) because %(err)s" % {
                    'url': self.dummy_backend_url,
                    'err': ex})
            logging.error(msg)

    def client_logout(self):
        logging.debug("Logout from Dummy Storage: %s", self.backend_name)
        # self.client.logout()

    def run(self):
        self.client = self._create_client()
        while True:
            try:
                if time() - self.time_last_request > self.timeout:
                    sleep(self.interval)
                    continue
                # self.client_login()
                data = {}
                # system_info = self.client.getStorageSystemInfo()
                system_info = {
                    "name": "dummy_storage",
                    "model": "dummy_storage 9999",
                    "serialNumber": "9999",
                    "systemVersion": "9.9.9.9"
                }
                data['system_info'] = system_info

                pool_stats = [
                    {
                        "name": "pool_1",
                        "totalCapacityMiB": "9999",
                        "allocatedCapacityMiB": "5555",
                        "freeCapacityMiB": "4444"
                    },
                    {
                        "name": "pool_2",
                        "totalCapacityMiB": "8888",
                        "allocatedCapacityMiB": "4444",
                        "freeCapacityMiB": "4444"
                    }
                ]

                data['pools'] = pool_stats
                if self.optional_metrics.get('cpu_statistics'):
                    cpu_statistics = [
                        {
                            "node": 0,
                            "cpu": 0,
                            "userPct": 1.3,
                            "systemPct": 1.8,
                            "idlePct": 96.9,
                            "interruptsPerSec": 0.0,
                            "contextSwitchesPerSec": 0.0
                        },
                        {
                            "node": 0,
                            "cpu": 1,
                            "userPct": 1.3,
                            "systemPct": 1.8,
                            "idlePct": 96.9,
                            "interruptsPerSec": 0.0,
                            "contextSwitchesPerSec": 0.0
                        },
                    ]
                    data['cpu_statistics'] = cpu_statistics
                # caching data to file using pickle
                cache_data(self.cache_file, data)
            except BaseException:
                logging.error('Error: ', exc_info=True)
            finally:
                self.client_logout()

            sleep(self.interval)


"""
This main func must always return two instances of two object with the order: StorageNameExporter, StorageMetrics
"""


def main(config, interval):
    dummy_metrics = prometheus_metrics.DummyMetrics(config)
    dummy_exporter = DummyExporter(config, interval)
    dummy_exporter.start()
    return dummy_exporter, dummy_metrics
