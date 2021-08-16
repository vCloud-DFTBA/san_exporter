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
This snippet was saved for debugging purpose.
"""

__author__ = "daikk115"

import hashlib
import requests

import xml.etree.ElementTree as ET


host = "10.11.12.13"
user = "manage"
password = "***"
session = requests.Session()
session.verify = False

creds = hashlib.md5(
    b'%s_%s' %
    ("manage".encode('utf8'),
     password.encode('utf8'))).hexdigest()
response = session.get('https://%s/api/login/%s' % (host, creds))
response.raise_for_status()
session_key = ET.fromstring(response.content)[0][2].text

session.headers['sessionKey'] = session_key
session.cookies['wbisessionkey'] = session_key
session.cookies['wbiusername'] = user

response = session.get('https://%s/api/show/%s' % (host, "volumes"))
# response = session.get('https://%s/api/show/system' % (host))
print(response.text)
