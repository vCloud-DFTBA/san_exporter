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
HPMSA Driver
Reference: https://github.com/enix/hpmsa_exporter
"""

__author__ = "daikk115"

import datetime
import hashlib
import logging
from time import sleep, time
import requests
import lxml.etree
import xml.etree.ElementTree as ET
from san_exporter.utils.utils import cache_data
from san_exporter.drivers import base_driver
from san_exporter.drivers.hpmsa import prometheus_metrics

PREFIX = 'san_'

CONTROLLER_PROPERTIES_AS_LABEL_MAPPING = {'durable-id': 'controller'}
SYSTEM_PROPERTIES_AS_LABEL_MAPPING = {'system-name': 'name'}
SYSTEMHEATH_PROPERTIES_AS_LABEL_MAPPING = {
    'system-name': 'name', 'health-reason': 'reason'
}
POOL_PROPERTIES_AS_LABEL_MAPPING = {
    'name': 'pool_name',
    'serial-number': 'serial'}
POOLSTATS_PROPERTIES_AS_LABEL_MAPPING = {
    'pool': 'pool_name', 'serial-number': 'serial'
}
VOLUME_PROPERTIES_AS_LABEL_MAPPING = {
    'volume-name': 'name', 'serial-number': 'serial'
}
ALERT_PROPERTIES_AS_LABEL_MAPPING = {

    'serial-number': 'serial', 'message': 'log_content'
}

# Fixed value for label
ALERT_FIXED_VALUE_LABEL = {}

METRICS = {
    # System
    'system_name': {
        'description': 'System Info',
        'sources': {
            'path': 'system',
            'object_selector': './OBJECT[@name="system-information"]',
            'property_selector': './PROPERTY[@name="system-information"]',
            'properties_as_label': SYSTEM_PROPERTIES_AS_LABEL_MAPPING
        }
    },
    'system_model': {
        'description': 'System Model',
        'sources': {
            'path': 'system',
            'object_selector': './OBJECT[@name="system-information"]',
            'property_selector': './PROPERTY[@name="product-id"]',
            'properties_as_label': SYSTEM_PROPERTIES_AS_LABEL_MAPPING
        }
    },
    'system_health': {
        'description': 'System Health 0: OK, 1: Degraded, 2: Fault, 3: Unknown, 4: N/A',
        'sources': {
            'path': 'system',
            'object_selector': './OBJECT[@name="system-information"]',
            'property_selector': './PROPERTY[@name="health-numeric"]',
            'properties_as_label': SYSTEMHEATH_PROPERTIES_AS_LABEL_MAPPING
        }
    },
    # Node
    'node_serial_number': {
        'description': 'Node Serial Number',
        'sources': {
            'path': 'controllers',
            'object_selector': './OBJECT[@name="controllers"]',
            'property_selector': './PROPERTY[@name="serial-number"]',
            'properties_as_label': CONTROLLER_PROPERTIES_AS_LABEL_MAPPING
        }
    },
    'node_hardware_version': {
        'description': 'Node Hardware Version',
        'sources': {
            'path': 'controllers',
            'object_selector': './OBJECT[@name="controllers"]',
            'property_selector': './PROPERTY[@name="hardware-version"]',
            'properties_as_label': CONTROLLER_PROPERTIES_AS_LABEL_MAPPING
        }
    },
    'totalNodes': {
        'description': 'Total nodes',
        'sources': {
            'path': 'controllers',
            'object_selector': './OBJECT[@name="controllers"]',
            'property_selector': './PROPERTY[@name="status-numeric"]',
            'properties_as_label': CONTROLLER_PROPERTIES_AS_LABEL_MAPPING
        }
    },
    # Node Statistics
    'cpu_total': {
        'description': 'The cpus spent in each node',
        'sources': {
            'path': 'controller-statistics',
            'object_selector': './OBJECT[@name="controller-statistics"]',
            'property_selector': './PROPERTY[@name="cpu-load"]',
            'properties_as_label': CONTROLLER_PROPERTIES_AS_LABEL_MAPPING
        }
    },
    'node_iops': {
        'description': 'The number of input/output operations per second in the node',
        'sources': {
            'path': 'controller-statistics',
            'object_selector': './OBJECT[@name="controller-statistics"]',
            'property_selector': './PROPERTY[@name="iops"]',
            'properties_as_label': CONTROLLER_PROPERTIES_AS_LABEL_MAPPING
        }
    },
    'node_bps': {
        'description': 'Node throughput bytes per second',
        'sources': {
            'path': 'controller-statistics',
            'object_selector': './OBJECT[@name="controller-statistics"]',
            'property_selector': './PROPERTY[@name="bytes-per-second-numeric"]',
            'properties_as_label': CONTROLLER_PROPERTIES_AS_LABEL_MAPPING
        }
    },
    # Pool
    'pool_total_capacity_mib': {
        'description': 'Total capacity of pool in Mib',
        'sources': {
            'path': 'pools',
            'object_selector': './OBJECT[@name="pools"]',
            'property_selector': './PROPERTY[@name="total-size-numeric"]',
            'properties_as_label': POOL_PROPERTIES_AS_LABEL_MAPPING,
            'multiple_with_property': './PROPERTY[@name="blocksize"]'
        }
    },
    'pool_free_capacity_mib': {
        'description': 'Free of pool in Mib',
        'sources': {
            'path': 'pools',
            'object_selector': './OBJECT[@name="pools"]',
            'property_selector': './PROPERTY[@name="total-avail-numeric"]',
            'properties_as_label': POOL_PROPERTIES_AS_LABEL_MAPPING,
            'multiple_with_property': './PROPERTY[@name="blocksize"]'
        }
    },
    'pool_volumes': {
        'description': 'Number of volumes in the pool',
        'sources': {
            'path': 'pools',
            'object_selector': './OBJECT[@name="pools"]',
            'property_selector': './PROPERTY[@name="volumes"]',
            'properties_as_label': POOL_PROPERTIES_AS_LABEL_MAPPING
        }
    },
    'pool_bps': {
        'description': 'Pool throughput byte per second',
        'sources': {
            'path': 'pool-statistics',
            'object_selector': './OBJECT[@name="pool-statistics"]',
            'property_selector': './/PROPERTY[@name="bytes-per-second-numeric"]',
            'properties_as_label': POOLSTATS_PROPERTIES_AS_LABEL_MAPPING
        }
    },
    'pool_iops': {
        'description': 'The number of input/output operations per second in the pool',
        'sources': {
            'path': 'pool-statistics',
            'object_selector': './OBJECT[@name="pool-statistics"]',
            'property_selector': './/PROPERTY[@name="iops"]',
            'properties_as_label': POOLSTATS_PROPERTIES_AS_LABEL_MAPPING
        }
    }
}

OPTIONAL_METRICS = {
    'volume': {
        # Volume
        'volume_size': {
            'description': 'Volume size',
            'sources': {
                'path': 'volumes',
                'object_selector': './OBJECT[@name="volume"]',
                'property_selector': './/PROPERTY[@name="total-size-numeric"]',
                'properties_as_label': VOLUME_PROPERTIES_AS_LABEL_MAPPING,
                'multiple_with_property': './PROPERTY[@name="blocksize"]'
            }
        }
    },
    'alert': {
        # Alert
        'alert': {
            'description': 'Shows Warning, Error, and Critical events',
            'sources': {
                'path': 'events/from/{}/to/{}/error',
                'object_selector': './OBJECT[@name="event"]',
                'fixed_value': '1',
                'properties_as_label': ALERT_PROPERTIES_AS_LABEL_MAPPING,
                'labels': ALERT_FIXED_VALUE_LABEL
            }
        }
    }
}


class HPMSAExporter(base_driver.ExporterDriver):

    def __init__(self, config=None, interval=300):
        super().__init__(config, interval)
        self.host = config['hpmsa_backend_host']
        self.login = config['hpmsa_backend_username']
        self.password = config['hpmsa_backend_password']
        self.backend_name = config['name']

        self.info_metrics = [
            'san_system_name',
            'san_system_model',
            'san_node_serial_number',
            'san_node_hardware_version'
        ]

    def run(self):  # noqa: C901
        # TODO: Inject auto reload optional metrics here!
        global METRICS, OPTIONAL_METRICS
        alert_path = OPTIONAL_METRICS['alert']['alert']['sources']['path']
        while True:
            if time() - self.time_last_request > self.timeout:
                sleep(self.interval)
                continue
            # Prepare the list of metrics which are we need to be collected
            # Firstly, we need some update for metric list
            timeto = datetime.datetime.now()
            timefrom = datetime.datetime.now() - datetime.timedelta(seconds=10000000)
            OPTIONAL_METRICS['alert']['alert']['sources']['path'] = alert_path.format(
                timefrom.strftime('%m%d%y%H%M%S'), timeto.strftime('%m%d%y%H%M%S'))
            logging.info(OPTIONAL_METRICS['alert']['alert']['sources']['path'])
            for opt, enabled in self.optional_metrics.items():
                if not enabled:
                    continue
                for k, v in OPTIONAL_METRICS[opt].items():
                    METRICS[k] = v
            try:
                session = requests.Session()
                session.verify = False

                creds = hashlib.md5(b'%s_%s' % (self.login.encode(
                    'utf8'), self.password.encode('utf8'))).hexdigest()
                response = session.get(
                    'https://%s/api/login/%s' %
                    (self.host, creds), timeout=self.interval)
                response.raise_for_status()
                session_key = ET.fromstring(response.content)[0][2].text

                session.headers['sessionKey'] = session_key
                session.cookies['wbisessionkey'] = session_key
                session.cookies['wbiusername'] = self.login

                path_cache = {}
                data_cache = {
                    'info_metrics': {},
                    'metrics': []
                }

                for name, metric in METRICS.items():
                    name = PREFIX + name
                    if isinstance(metric['sources'], dict):
                        sources = [metric['sources']]
                    else:
                        sources = metric['sources']

                    for source in sources:
                        if source['path'] not in path_cache:
                            response = session.get(
                                'https://%s/api/show/%s' %
                                (self.host, source['path']), timeout=self.interval)
                            response.raise_for_status()
                            path_cache[source['path']] = lxml.etree.fromstring(
                                response.content)

                        xml = path_cache[source['path']]

                        for obj in xml.xpath(source['object_selector']):
                            labels = {source['properties_as_label'][elem.get('name')]: elem.text for elem in obj
                                      if elem.get('name') in source.get('properties_as_label', {})}
                            labels.update(source.get('labels', {}))
                            if source.get('fixed_value', None):
                                value = source.get('fixed_value')
                            else:
                                value = obj.find(
                                    source['property_selector']).text

                            if source.get('multiple_with_property', None):
                                if obj.find(source['multiple_with_property']):
                                    # For HPMSA 2050
                                    value = int(value) * int(
                                        obj.find(source['multiple_with_property']).text)
                                else:
                                    # For HPMSA 2040
                                    blocksize = obj.find(
                                        source['property_selector']).attrib['units'].replace(
                                        "blocks", "")
                                    value = int(value) * int(blocksize)
                            labels.update({"san_ip": self.host})

                            if name in self.info_metrics:
                                data_cache['info_metrics'][name] = value
                            else:
                                data_cache['metrics'].append({
                                    'name': name,
                                    'labels': labels,
                                    'type': metric.get('type', 'gauge'),
                                    'description': metric['description'],
                                    'value': value
                                })
                cache_data(self.cache_file, data_cache)
            except BaseException:
                logging.error('Error: ', exc_info=True)

            sleep(self.interval)


def main(config, interval):
    hpmsa_metrics = prometheus_metrics.HPMSAMetrics(config)
    hpmsa_exporter = HPMSAExporter(config, interval)
    hpmsa_exporter.start()
    return hpmsa_exporter, hpmsa_metrics
