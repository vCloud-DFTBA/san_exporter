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

from san_exporter import main
from san_exporter.main import load_config

PORT = 8888
HOST = '0.0.0.0'

if __name__ == '__main__':
    config = load_config()
    if config.get('port'):
        port = config['port']
    else:
        port = PORT
    if config.get('host'):
        host = config['host']
    else:
        host = HOST
    app = main.create_app()
    app.run(host=host, port=port)
