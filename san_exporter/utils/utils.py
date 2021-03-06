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

import pickle
import logging
from time import time


def cache_data(cache_file, data):
    with open(cache_file, "wb+") as f:
        pickle.dump((data, {'time': time()}), f, pickle.HIGHEST_PROTOCOL)
    logging.info("Done dumping stats to {}".format(cache_file))


def get_data(cache_file):
    with open(cache_file, 'rb') as f:
        return pickle.load(f)
