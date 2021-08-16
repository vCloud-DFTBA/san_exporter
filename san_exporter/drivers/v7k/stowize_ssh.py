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

import logging

from san_exporter.utils.ssh_utils import SSHConnection


class StorwizeSSH(SSHConnection):
    """SSH interface to IBM Storwize family and SVC storage systems."""

    def __init__(self, ip, port, user, conn_timeout=None, password=None, private_key=None):
        super().__init__(ip, port, user, conn_timeout, password, private_key)

    #     """Run an SSH command and return parsed output."""
    #     raw = self._run_ssh(ssh_cmd)
    #     return CLIResponse(raw, ssh_cmd=ssh_cmd, delim=delim,

    def lsnode(self, node_id=None):
        ssh_cmd = ['svcinfo', 'lsnode', '-delim', '!']
        if node_id:
            ssh_cmd.append(node_id)
        return self.execute(ssh_cmd)

    def lslicense(self):
        ssh_cmd = ['svcinfo', 'lslicense', '-delim', '!']
        return self.execute(ssh_cmd)

    def lsguicapabilities(self):
        ssh_cmd = ['svcinfo', 'lsguicapabilities', '-delim', '!']
        return self.execute(ssh_cmd)

    def lssystem(self):
        ssh_cmd = ['svcinfo', 'lssystem', '-delim', '!']
        return self.execute(ssh_cmd)

    def lsmdiskgrp(self, pool):
        ssh_cmd = ['svcinfo', 'lsmdiskgrp', '-bytes', '-delim', '!',
                   '"%s"' % pool]
        try:
            return self.execute(ssh_cmd)
        except Exception as ex:
            logging.warning("Failed to get pool %(pool)s info. "
                            "Exception: %(ex)s.", {'pool': pool, 'ex': ex})
            return None

    def lsiogrp(self):
        ssh_cmd = ['svcinfo', 'lsiogrp', '-delim', '!']
        return self.execute(ssh_cmd)

    def lsportip(self):
        ssh_cmd = ['svcinfo', 'lsportip', '-delim', '!']
        return self.execute(ssh_cmd)

    @staticmethod
    def _create_port_arg(port_type, port_name):
        if port_type == 'initiator':
            port = ['-iscsiname']
        else:
            port = ['-hbawwpn']
        port.append(port_name)
        return port

    def lshost(self, host=None):
        ssh_cmd = ['svcinfo', 'lshost', '-delim', '!']
        if host:
            ssh_cmd.append('"%s"' % host)
        return self.execute(ssh_cmd)

    def lsiscsiauth(self):
        ssh_cmd = ['svcinfo', 'lsiscsiauth', '-delim', '!']
        return self.execute(ssh_cmd)

    def lsfabric(self, wwpn=None, host=None):
        ssh_cmd = ['svcinfo', 'lsfabric', '-delim', '!']
        if wwpn:
            ssh_cmd.extend(['-wwpn', wwpn])
        elif host:
            ssh_cmd.extend(['-host', '"%s"' % host])
        else:
            msg = 'Must pass wwpn or host to lsfabric.'
            logging.error(msg)
        return self.execute(ssh_cmd)

    def lsrcrelationship(self, rc_rel):
        ssh_cmd = ['svcinfo', 'lsrcrelationship', '-delim', '!', rc_rel]
        return self.execute(ssh_cmd)

    def lsrcconsistgrp(self, rccg):
        ssh_cmd = ['svcinfo', 'lsrcconsistgrp', '-delim', '!', rccg]
        try:
            return self.execute(ssh_cmd)[0]
        except Exception as ex:
            logging.warning("Failed to get rcconsistgrp %(rccg)s info. "
                            "Exception: %(ex)s.", {'rccg': rccg, 'ex': ex})
            return None

    def lspartnership(self, system_name):
        key_value = 'name=%s' % system_name
        ssh_cmd = ['svcinfo', 'lspartnership', '-filtervalue', key_value, '-delim', '!']
        return self.execute(ssh_cmd)

    def lspartnershipcandidate(self):
        ssh_cmd = ['svcinfo', 'lspartnershipcandidate', '-delim', '!']
        return self.execute(ssh_cmd)

    def lsvdiskhostmap(self, vdisk):
        ssh_cmd = ['svcinfo', 'lsvdiskhostmap', '-delim', '!', '"%s"' % vdisk]
        return self.execute(ssh_cmd)

    def lshostvdiskmap(self, host):
        ssh_cmd = ['svcinfo', 'lshostvdiskmap', '-delim', '!', '"%s"' % host]
        return self.execute(ssh_cmd)

    def get_vdiskhostmapid(self, vdisk, host):
        resp = self.lsvdiskhostmap(vdisk)
        for mapping_info in resp:
            if mapping_info['host_name'] == host:
                lun_id = mapping_info['SCSI_id']
                return lun_id
        return None

    def lsvdisk(self, vdisk):
        """Return vdisk attributes or None if it doesn't exist."""
        ssh_cmd = ['svcinfo', 'lsvdisk', '-bytes', '-delim', '!',
                   '"%s"' % vdisk]
        return self.execute(ssh_cmd)

    def lsvdisks_from_filter(self, filter_name, value):
        """Performs an lsvdisk command, filtering the results as specified.
        Returns an iterable for all matching vdisks.
        """
        ssh_cmd = ['svcinfo', 'lsvdisk', '-bytes', '-delim', '!',
                   '-filtervalue', '%s=%s' % (filter_name, value)]
        return self.execute(ssh_cmd)

    def lsvdiskfcmappings(self, vdisk):
        ssh_cmd = ['svcinfo', 'lsvdiskfcmappings', '-delim', '!',
                   '"%s"' % vdisk]
        return self.execute(ssh_cmd)

    def lsfcmap(self, fc_map_id):
        ssh_cmd = ['svcinfo', 'lsfcmap', '-filtervalue',
                   'id=%s' % fc_map_id, '-delim', '!']
        return self.execute(ssh_cmd)

    def lsfcconsistgrp(self, fc_consistgrp):
        ssh_cmd = ['svcinfo', 'lsfcconsistgrp', '-delim', '!', fc_consistgrp]
        return self.execute(ssh_cmd)

    def lsvdiskcopy(self, vdisk, copy_id=None):
        ssh_cmd = ['svcinfo', 'lsvdiskcopy', '-delim', '!']
        if copy_id:
            ssh_cmd += ['-copy', copy_id]
        ssh_cmd += ['"%s"' % vdisk]
        return self.execute(ssh_cmd)

    def lsvdisksyncprogress(self, vdisk, copy_id):
        ssh_cmd = ['svcinfo', 'lsvdisksyncprogress', '-delim', '!',
                   '-copy', copy_id, '"%s"' % vdisk]
        return self.execute(ssh_cmd)[0]

    def lsportfc(self, node_id):
        ssh_cmd = ['svcinfo', 'lsportfc', '-delim', '!',
                   '-filtervalue', 'node_id=%s' % node_id]
        return self.execute(ssh_cmd)

    def lstargetportfc(self, current_node_id=None, host_io_permitted=None):
        ssh_cmd = ['svcinfo', 'lstargetportfc', '-delim', '!']
        if current_node_id and host_io_permitted:
            ssh_cmd += ['-filtervalue', '%s:%s' % (
                'current_node_id=%s' % current_node_id,
                'host_io_permitted=%s' % host_io_permitted)]
        elif current_node_id:
            ssh_cmd += ['-filtervalue', 'current_node_id=%s' % current_node_id]
        return self.execute(ssh_cmd)
