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

import os
import logging
from time import time

import yaml
from yaml.scanner import ScannerError
from flask import Flask, Response, render_template
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from san_exporter.drivers import load_driver
from san_exporter.utils.utils import get_data

app = Flask(__name__)
CONFIG_FILE = "../config.yml"
LOG_FILE = '/var/log/san_exporter.log'
config = {}
running_backends = {}


def load_config():
    # load yaml config
    config_file_path = os.path.join(os.path.dirname(__file__), CONFIG_FILE)
    if os.path.isfile(config_file_path):
        with open(config_file_path, "r") as f:
            try:
                yaml_config = yaml.safe_load(f)
                f.close()
            except ScannerError:
                print("Can not load the file config.yml!")
            finally:
                f.close()
            return yaml_config
    else:
        print("Can not find the file config.yml!")
        exit(0)


def config_logging(log_file):
    if config['debug']:
        logging.basicConfig(filename=log_file, filemode='a', format='%(asctime)s   %(levelname)s   %(message)s',
                            level=logging.DEBUG)
    else:
        logging.basicConfig(filename=log_file, filemode='a', format='%(asctime)s   %(levelname)s   %(message)s',
                            level=logging.INFO)


# Entry point of app
def create_app():
    global config
    global running_backends
    config = load_config()
    if config.get('log_file'):
        log_file = config['log_file']
    else:
        log_file = LOG_FILE
    config_logging(log_file)
    logging.info('Starting app...')

    enabled_backends = config['enabled_backends']
    if len(enabled_backends) == 0:
        logging.warning('Having no backend enabled!')
        logging.info('Stopping exporter...')
        exit(0)

    enabled_drivers = []
    for b in config['backends']:
        if b['name'] in enabled_backends:
            enabled_drivers.append(b['driver'])
    # drivers = {'hpe3par': main_module}
    drivers = load_driver.load_drivers(enabled_drivers)
    running_backends = {}
    for backend_config in config['backends']:
        if backend_config['name'] in enabled_backends:
            interval = 10
            if config.get('interval'):
                interval = config['interval']
            if backend_config.get('interval'):
                interval = backend_config['interval']
            rb = drivers[backend_config['driver']].main(backend_config, interval)
            running_backends[backend_config['name']] = rb
            # running_backends = {'3par1111': (HPE3ParExporter, HPE3ParMetrics), ...}
    return app


@app.route('/')
def index():
    return render_template('index.html', enabled_backends=config['enabled_backends'])


@app.route('/<backend_name>')
def do_get(backend_name):
    global running_backends
    if backend_name in config['enabled_backends']:
        cache_file = backend_name + '.data'
        timeout = 600
        if config.get('timeout'):
            timeout = config['timeout']
        for backend in config['backends']:
            if backend_name == backend['name']:
                if backend.get('timeout'):
                    timeout = backend['timeout']
        cached = get_data(cache_file)
        running_backends[backend_name][0].time_last_request = time()
        if (running_backends[backend_name][0].time_last_request - cached[1]['time']) > timeout:
            message = 'Data timeout in cache file of storage backend: ' + backend_name
            logging.warning(message)
            return message
        data = cached[0]
        backend = running_backends[backend_name][1]
        backend.parse_metrics(data)
        metrics = backend.get_metrics()
        return Response(
            metrics,
            headers={
                "Content-Type": "text/plain"
            }
        )
    else:
        return render_template('index.html', enabled_backends=config['enabled_backends'])


if __name__ == '__main__':
    app = create_app()
    app.run()
