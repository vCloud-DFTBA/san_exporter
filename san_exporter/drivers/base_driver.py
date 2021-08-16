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

"""Base driver module used to create compatible driver for specific SAN storage."""

from time import time
from san_exporter.main import load_config
from threading import Thread

from prometheus_client import CollectorRegistry


class ExporterDriver(Thread):
    """
    Basic class implementation that connect to SAN storage and collect info to metrics
    """

    def __init__(self, config=None, interval=10):
        super().__init__()
        config_global = load_config()
        self.config = config
        self.client = None
        self.interval = interval
        self.cache_file = config['name'] + ".data"
        self.optional_metrics = config.get('optional_metrics', {})
        self.time_last_request = time()
        self.timeout = config_global.get('timeout', 600)
        self.timeout = config.get('timeout', self.timeout)
        if config.get('pools'):
            pools = config['pools'].split(',')
            if pools[0].strip().lower() == 'all':
                self.get_all_pools = True
            else:
                self.get_all_pools = False
        else:
            self.get_all_pools = True

    def run(self):
        pass


class Metrics:
    def __init__(self, config=None, labels=None):
        if labels:
            _labels = labels
        else:
            # Every metrics must have a label "backend_name": name of backend
            # Other information like: storage name, version, serial, .. should
            # be put to the INFO metric
            _labels = ["backend_name"]  # noqa: F841

        self.optional_metrics = config.get('optional_metrics', {})

        self.registry = CollectorRegistry()

        # NOTE:
        # Some SAN storage using several terminology for group of disks, physical disk, virtual disk.
        # For example with IBM v7000, Dell sc8000, ... they're using Pool -> Disk -> LUN
        # or with HPE MSA, 3Par, ... they're using CPG -> Disk -> Volume
        #
        # We uniformly use the terminology Pool -> Disk -> LUN for the related metrics.
        # These general metrics must be prefixed with "san_"

    def define_pool_metrics(self):
        # Pool metrics should have these labels:
        #   backend_name: backend name
        #   pool_name: pool/CPG name
        pool_labels = ["backend_name", "pool_name"]  # noqa: F841
