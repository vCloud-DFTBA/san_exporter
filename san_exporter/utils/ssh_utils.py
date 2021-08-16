# Copyright 2015 IBM Corp.
# Copyright 2021 Viettel Networks.
# All Rights Reserved.
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
import six

import logging
import paramiko


class SSHConnection:
    def __init__(self, ip, port, user, conn_timeout=None, password=None, private_key=None):
        self.ip = ip
        self.port = port
        self.user = user
        self.password = password
        self.conn_timeout = conn_timeout if conn_timeout else None
        self.private_key = private_key
        self.hosts_key_file = None
        self.current_size = 0
        self.ssh_client = self._create_ssh_client()

    def _create_ssh_client(self):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if self.hosts_key_file:
                if ',' in self.hosts_key_file:
                    files = self.hosts_key_file.split(',')
                    for f in files:
                        ssh.load_host_keys(f)
                else:
                    ssh.load_host_keys(self.hosts_key_file)
            if self.password:
                ssh.connect(self.ip,
                            port=self.port,
                            username=self.user,
                            password=self.password,
                            timeout=self.conn_timeout)
            elif self.private_key:
                pkfile = os.path.expanduser(self.private_key)
                privatekey = paramiko.RSAKey.from_private_key_file(pkfile)
                ssh.connect(self.ip,
                            port=self.port,
                            username=self.user,
                            pkey=privatekey,
                            timeout=self.conn_timeout)
            else:
                msg = "Specify a password or private_key"
                logging.error(msg)

            if self.conn_timeout:
                transport = ssh.get_transport()
                transport.set_keepalive(self.conn_timeout)
            return ssh
        except:
            logging.error('SSH Error: ', exc_info=True)

    def execute(self, command):
        # TODO: implement the regex that replace the special character
        #       that allow for extra commands to be added instead of a
        #       parameter by a malicious user, to eliminate many security concerns
        # Example: command = command.replace(/\`|\||\&<|>|;/g, '');
        try:
            (stdin, stdout, stderr) = self.ssh_client.exec_command(command)
            return CLIResponse((stdout, stderr), ssh_cmd=command)
        except Exception as e:
            logging.error('CLI exception has occurred: %s', e)


class CLIResponse(object):

    def __init__(self, raw, ssh_cmd=None, delim='!', with_header=True):
        super(CLIResponse, self).__init__()
        if ssh_cmd:
            self.ssh_cmd = ' '.join(ssh_cmd)
        else:
            self.ssh_cmd = 'None'
        self.raw = raw
        self.delim = delim
        self.with_header = with_header
        self.result = self._parse()

    def select(self, *keys):
        for a in self.result:
            vs = []
            for k in keys:
                v = a.get(k, None)
                if isinstance(v, six.string_types) or v is None:
                    v = [v]
                if isinstance(v, list):
                    vs.append(v)
            for item in zip(*vs):
                if len(item) == 1:
                    yield item[0]
                else:
                    yield item

    def __getitem__(self, key):
        try:
            return self.result[key]
        except KeyError:
            msg = ('Did not find the expected key %(key)s in %(fun)s: '
                   '%(raw)s.' % {'key': key, 'fun': self.ssh_cmd, 'raw': self.raw})
            logging.info(msg)

    def __iter__(self):
        for a in self.result:
            yield a

    def __len__(self):
        return len(self.result)

    def _parse(self):
        def get_reader(content, delim):
            for line in content.readlines():
                line = line.strip()
                if line:
                    yield line.split(delim)
                else:
                    yield []

        if isinstance(self.raw, six.string_types):
            stdout, stderr = self.raw, ''
        else:
            stdout, stderr = self.raw
        reader = get_reader(stdout, self.delim)
        result = []

        if self.with_header:
            hds = tuple()
            for row in reader:
                hds = row
                break
            for row in reader:
                cur = dict()
                if len(hds) != len(row):
                    msg = ('Unexpected CLI response: header/row mismatch. '
                           'header: %(header)s, row: %(row)s.' % {'header': hds, 'row': row})
                    logging.info(msg)
                for k, v in zip(hds, row):
                    CLIResponse.append_dict(cur, k, v)
                result.append(cur)
        else:
            cur = dict()
            for row in reader:
                if row:
                    CLIResponse.append_dict(cur, row[0], ' '.join(row[1:]))
                elif cur:  # start new section
                    result.append(cur)
                    cur = dict()
            if cur:
                result.append(cur)
        return result

    @staticmethod
    def append_dict(dict_, key, value):
        key, value = key.strip(), value.strip()
        obj = dict_.get(key, None)
        if obj is None:
            dict_[key] = value
        elif isinstance(obj, list):
            obj.append(value)
            dict_[key] = obj
        else:
            dict_[key] = [obj, value]
        return dict_
