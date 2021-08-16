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
import importlib
import logging


def load_drivers(enabled_backends):
    form_module = lambda fp: fp + '.main'  # noqa: E731
    file_names = os.listdir(os.path.dirname(__file__))
    driver_files = []
    for driver in enabled_backends:
        if driver in file_names:
            driver_files.append("san_exporter.drivers." + driver)
        else:
            logging.error('Can not find driver for backend: ' + driver)

    drivers = map(form_module, driver_files)

    modules = {}
    for driver in drivers:
        try:
            modules[driver.split('.')[2]] = importlib.import_module(driver, )
        except ModuleNotFoundError:
            logging.error("Can not load the driver: " + driver, exc_info=True)

    return modules


if __name__ == '__main__':
    enabled_backends = ['hpe3par']
    load_drivers(enabled_backends)
