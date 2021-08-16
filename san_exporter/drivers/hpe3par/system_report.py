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

from hpe3parclient import exceptions
from hpe3parclient.client import HPE3ParClient


class HPE3ParClientCustom(HPE3ParClient):

    def __init__(self, api_url, debug=False, secure=False, timeout=None, suppress_ssl_warnings=False):
        super().__init__(api_url, debug, secure, timeout, suppress_ssl_warnings)

    def _generate_systemreporter_url(self, api, samplefreq, is_at_time, report_identifier=None, query=None):
        if samplefreq not in ['daily', 'hourly', 'hires']:
            raise exceptions.ClientException("Input interval not valid")
        url = "/systemreporter"
        if is_at_time:
            url += "/attime/" + api + "/" + samplefreq
        else:
            url += "/vstime/" + api + "/" + samplefreq
        if report_identifier:
            url += ";" + report_identifier
        if query:
            url += "?query=\"" + query + "\""
        return url

    # At Time APIs

    def getCPGStatisticsAtTime(self, cpg_name=None, samplefreq='daily', report_identifier="groupby:name,domain",
                               query=None):
        """
        :param cpg_name:
        :param samplefreq:
        :param report_identifier:
        :param query:
        :return:
            "members": [
                {
                    "name": "CPG_SAS_RAID6",
                    "IO": {
                        "read": 0.2,
                        "write": 74.7,
                        "total": 74.9
                    },
                    "KBytes": {
                        "read": 26.7,
                        "write": 6211.0,
                        "total": 6237.6
                    },
                    "serviceTimeMS": {
                        "read": 11.24,
                        "write": 66.65,
                        "total": 66.53
                    },
                    "IOSizeKB": {
                        "read": 174.4,
                        "write": 83.1,
                        "total": 83.3
                    },
                    "queueLength": 0,
                    "busyPct": 3.7
                },
                ...
            ]
        """
        url = self._generate_systemreporter_url(api="cpgstatistics", samplefreq=samplefreq,
                                                is_at_time=True, query=query, report_identifier=report_identifier)

        response, body = self.http.get(url)
        return body

    def getCPUStatisticsAtTime(self, samplefreq='daily', node=None, report_identifier="groupby:node,cpu", query=None):
        """
        :param samplefreq: The parameter indicates how often to generate the performance sample data
        :type samplefreq: str
        Only accept:
            hires: based on 5 minutes (high resolution)
            hourly: based on 1 hour
            daily: based on 1 day

        :param report_identifier: groupby:<groupby>;compareby:<compareby>;summary:<summary_keywords>
        :type report_identifier: str

        :return:
             "members": [
                {
                    "node": 0,
                    "cpu": 0,
                    "userPct": 0.5,
                    "systemPct": 2.0,
                    "idlePct": 97.5,
                    "interruptsPerSec": 33420.8,
                    "contextSwitchesPerSec": 25690.6
                },
                {
                    "node": 0,
                    "cpu": 1,
                    "userPct": 0.3,
                    "systemPct": 2.5,
                    "idlePct": 97.2,
                    "interruptsPerSec": 0.0,
                    "contextSwitchesPerSec": 0.0
                },
                ...
             ]
        """
        _query = ""
        if node:
            _query = "node EQ " + node
        if query:
            _query += " AND " + query
        url = self._generate_systemreporter_url(api="cpustatistics", samplefreq=samplefreq,
                                                is_at_time=True, query=query, report_identifier=report_identifier)

        response, body = self.http.get(url)
        return body

    def getPhysicalDiskCapacityAtTime(self, samplefreq='daily',
                                      report_identifier="groupby:id,cageID,cageSide,mag,diskPos,type,RPM",
                                      query=None):
        url = self._generate_systemreporter_url(api="physicaldiskcapacity", samplefreq=samplefreq,
                                                is_at_time=True, query=query, report_identifier=report_identifier)

        response, body = self.http.get(url)
        return body

    def getPhysicalDiskSpaceDataAtTime(self, samplefreq='daily',
                                       report_identifier="groupby:id,cageID,cageSide,mag,diskPos,type,RPM",
                                       query=None):
        url = self._generate_systemreporter_url(api="physicaldiskspacedata", samplefreq=samplefreq,
                                                is_at_time=True, query=query, report_identifier=report_identifier)

        response, body = self.http.get(url)
        return body

    def getPhysicalDiskStatisticsAtTime(self, samplefreq='daily',
                                        report_identifier="groupby:id,cageID,cageSide,mag,diskPos,type,RPM",
                                        query=None):
        url = self._generate_systemreporter_url(api="physicaldiskstatistics", samplefreq=samplefreq,
                                                is_at_time=True, query=query, report_identifier=report_identifier)

        response, body = self.http.get(url)
        return body

    def getPortStatisticsAtTime(self, samplefreq='daily',
                                report_identifier="groupby:node,slot,cardPort,type,speed",
                                query=None):
        url = self._generate_systemreporter_url(api="portstatistics", samplefreq=samplefreq,
                                                is_at_time=True, query=query, report_identifier=report_identifier)

        response, body = self.http.get(url)
        return body

    def getQoSStatisticsAtTime(self, samplefreq='daily',
                               report_identifier="groupby:domain,type,name,ioLimit",
                               query=None):
        url = self._generate_systemreporter_url(api="qosstatistics", samplefreq=samplefreq,
                                                is_at_time=True, query=query, report_identifier=report_identifier)

        response, body = self.http.get(url)
        return body

    def getRemoteCopyStatisticsAtTime(self, samplefreq='daily',
                                      report_identifier="groupby:targetName,linkId,linkAddr,node,slotPort,cardPort",
                                      query=None):
        url = self._generate_systemreporter_url(api="remotecopystatistics", samplefreq=samplefreq,
                                                is_at_time=True, query=query, report_identifier=report_identifier)

        response, body = self.http.get(url)
        return body

    def getRemoteCopyVolumesStatisticsAtTime(self, samplefreq='daily',
                                             report_identifier="groupby:volumeName,volumeSetName,domain,targetName,"
                                                               "mode,remoteCopyGroup,remoteCopyGroupRole,node,slot,"
                                                               "cardPort,portType",
                                             query=None):
        if not report_identifier:
            report_identifier = "groupby:volumeName,volumeSetName,domain,targetName," \
                                "mode,remoteCopyGroup,remoteCopyGroupRole,node,slot," \
                                "cardPort,portType"
        url = self._generate_systemreporter_url(api="remotecopyvolumestatistics", samplefreq=samplefreq,
                                                is_at_time=True, query=query, report_identifier=report_identifier)
        response, body = self.http.get(url)
        return body

    def getVlunsStatisticsAtTime(self, samplefreq='daily',
                                 report_identifier="groupby:domain,volumeName,hostname,lun,hostWWN,"
                                                   "node,slot,cardPort,vvsetName,hostsetName",
                                 query=None):

        if not report_identifier:
            report_identifier = "groupby:domain,volumeName,hostname,lun,hostWWN,node," \
                                "slot,cardPort,vvsetName,hostsetName"
        url = self._generate_systemreporter_url(api="vlunstatistics", samplefreq=samplefreq,
                                                is_at_time=True, query=query, report_identifier=report_identifier)
        response, body = self.http.get(url)
        return body

    #  Versus Time APIs

    def getCPGStatisticsVsTime(self, cpg_name=None, samplefreq='daily', report_identifier="groupby:name,domain",
                               query=None):
        if not report_identifier:
            report_identifier = "groupby:name,domain"
        if cpg_name:
            report_identifier = "name:" + cpg_name + ";" + report_identifier
        url = self._generate_systemreporter_url(api="cpgstatistics", samplefreq=samplefreq,
                                                is_at_time=False, query=query, report_identifier=report_identifier)

        response, body = self.http.get(url)
        return body

    def getCPUStatisticsVsTime(self, samplefreq='daily', node=None, report_identifier="groupby:node,cpu", query=None):
        """
        :param samplefreq: The parameter indicates how often to generate the performance sample data
        :type samplefreq: str
        Only accept:
            hires: based on 5 minutes (high resolution)
            hourly: based on 1 hour
            daily: based on 1 day

        :param report_identifier: groupby:<groupby>;compareby:<compareby>;summary:<summary_keywords>
        :type report_identifier: str

        :return:
            {
                "sampleTime": "2019-09-27T17:00:00+07:00",
                "sampleTimeSec": 1569578400,
                "total": 80,
                "members": [
                    {
                        "cpu": 0,
                        "node": 0,
                        "userPct": 0.3,
                        "systemPct": 1.3,
                        "idlePct": 98.3,
                        "interruptsPerSec": 23010.2,
                        "contextSwitchesPerSec": 18520.2
                    },
                    {
                        "cpu": 0,
                        "node": 1,
                        "userPct": 0.7,
                        "systemPct": 1.6,
                        "idlePct": 97.6,
                        "interruptsPerSec": 22727.3,
                        "contextSwitchesPerSec": 19492.3
                    },
        """
        if not report_identifier:
            report_identifier = "groupby:node,cpu"
        if node:
            report_identifier = "node:" + node + ";" + report_identifier
        url = self._generate_systemreporter_url(api="cpustatistics", samplefreq=samplefreq,
                                                is_at_time=False, query=query, report_identifier=report_identifier)

        response, body = self.http.get(url)
        return body

    def getPhysicalDiskCapacityVsTime(self, samplefreq='daily', id=None, type=None, rpm=None,
                                      report_identifier="groupby:id,cageID,cageSide,mag,diskPos,type,RPM",
                                      query=None):
        if not report_identifier:
            report_identifier = "groupby:id,cageID,cageSide,mag,diskPos,type,RPM"
        if id:
            report_identifier = "id:" + id + ";" + report_identifier
        if type:
            report_identifier = "type:" + type + ";" + report_identifier
        if rpm:
            report_identifier = "rpm:" + rpm + ";" + report_identifier
        url = self._generate_systemreporter_url(api="physicaldiskcapacity", samplefreq=samplefreq,
                                                is_at_time=False, query=query, report_identifier=report_identifier)

        response, body = self.http.get(url)
        return body

    def getPhysicalDiskSpaceDataVsTime(self, samplefreq='daily', id=None, type=None, rpm=None,
                                       report_identifier="groupby:id,cageID,cageSide,mag,diskPos,type,RPM",
                                       query=None):
        if not report_identifier:
            report_identifier = "groupby:id,cageID,cageSide,mag,diskPos,type,RPM"
        if id:
            report_identifier = "id:" + id + ";" + report_identifier
        if type:
            report_identifier = "type:" + type + ";" + report_identifier
        if rpm:
            report_identifier = "rpm:" + rpm + ";" + report_identifier
        url = self._generate_systemreporter_url(api="physicaldiskspacedata", samplefreq=samplefreq,
                                                is_at_time=False, query=query, report_identifier=report_identifier)

        response, body = self.http.get(url)
        return body

    def getPhysicalDiskStatisticsVsTime(self, samplefreq='daily', id=None, type=None, rpm=None,
                                        report_identifier="groupby:id,cageID,cageSide,mag,diskPos,type,RPM",
                                        query=None):
        if not report_identifier:
            report_identifier = "groupby:id,cageID,cageSide,mag,diskPos,type,RPM"
        if id:
            report_identifier = "id:" + id + ";" + report_identifier
        if type:
            report_identifier = "type:" + type + ";" + report_identifier
        if rpm:
            report_identifier = "rpm:" + rpm + ";" + report_identifier
        url = self._generate_systemreporter_url(api="physicaldiskstatistics", samplefreq=samplefreq,
                                                is_at_time=False, query=query, report_identifier=report_identifier)

        response, body = self.http.get(url)
        return body

    def getPortStatisticsVsTime(self, samplefreq='daily', portPos=None, type=None,
                                report_identifier="groupby:node,slot,cardPort,type,speed",
                                query=None):
        if not report_identifier:
            report_identifier = "groupby:node,slot,cardPort,type,speed"
        if portPos:
            report_identifier = "portPos:" + portPos + ";" + report_identifier
        if type:
            report_identifier = "type:" + type + ";" + report_identifier
        url = self._generate_systemreporter_url(api="portstatistics", samplefreq=samplefreq,
                                                is_at_time=False, query=query, report_identifier=report_identifier)

        response, body = self.http.get(url)
        return body

    def getQoSStatisticsVsTime(self, samplefreq='daily', vvset=None, domain=None, sys=None,
                               report_identifier="groupby:domain,type,name,ioLimit",
                               query=None):
        if not report_identifier:
            report_identifier = "groupby:domain,type,name,ioLimit"
        if vvset:
            report_identifier = "vvset:" + vvset + ";" + report_identifier
        if domain:
            report_identifier = "domain:" + domain + ";" + report_identifier
        if sys:
            report_identifier = "sys:" + sys + ";" + report_identifier
        url = self._generate_systemreporter_url(api="qosstatistics", samplefreq=samplefreq,
                                                is_at_time=False, query=query, report_identifier=report_identifier)

        response, body = self.http.get(url)
        return body

    def getRemoteCopyStatisticsVsTime(self, samplefreq='daily', targetName=None, portPos=None,
                                      report_identifier="groupby:targetName,linkId,linkAddr,node,slotPort,cardPort",
                                      query=None):
        if not report_identifier:
            report_identifier = "groupby:targetName,linkId,linkAddr,node,slotPort,cardPort"
        if targetName:
            report_identifier = "targetName:" + targetName + ";" + report_identifier
        if portPos:
            report_identifier = "portPos:" + portPos + ";" + report_identifier
        url = self._generate_systemreporter_url(api="remotecopystatistics", samplefreq=samplefreq,
                                                is_at_time=False, query=query, report_identifier=report_identifier)

        response, body = self.http.get(url)
        return body

    def getRemoteCopyVolumesStatisticsVsTime(self, samplefreq='daily', volumeName=None, targetName=None, portPos=None,
                                             report_identifier="groupby:volumeName,volumeSetName,domain,targetName,"
                                                               "mode,remoteCopyGroup,remoteCopyGroupRole,node,slot,"
                                                               "cardPort,portType",
                                             query=None):
        if not report_identifier:
            report_identifier = "groupby:volumeName,volumeSetName,domain,targetName," \
                                "mode,remoteCopyGroup,remoteCopyGroupRole,node,slot,cardPort,portType"
        if volumeName:
            report_identifier = "volumeName:" + volumeName + ";" + report_identifier
        if targetName:
            report_identifier = "targetName:" + targetName + ";" + report_identifier
        if portPos:
            report_identifier = "portPos:" + portPos + ";" + report_identifier
        url = self._generate_systemreporter_url(api="remotecopyvolumestatistics", samplefreq=samplefreq,
                                                is_at_time=False, query=query, report_identifier=report_identifier)
        response, body = self.http.get(url)
        return body

    def getVlunsStatisticsVsTime(self, samplefreq='daily',
                                 report_identifier="groupby:domain,volumeName,hostname,lun,hostWWN,"
                                                   "node,slot,cardPort,vvsetName,hostsetName",
                                 vlunid=None, vlun_expresstion=None, volumename=None,
                                 hostname=None, vvset_name=None, hostset_name=None, portPos=None,
                                 query=None):

        if not report_identifier:
            report_identifier = "groupby:domain,volumeName,hostname,lun,hostWWN," \
                                "node,slot,cardPort,vvsetName,hostsetName"
        if vlun_expresstion:
            report_identifier = "vlun:" + report_identifier + ";" + report_identifier
        elif vlunid:
            report_identifier = "lun:" + vlunid + ";" + report_identifier
        elif volumename:
            report_identifier = "volumeName:" + volumename + ";" + report_identifier
        elif hostname:
            report_identifier = "hostname:" + hostname + ";" + report_identifier
        elif portPos:
            report_identifier = "portPos:" + portPos + ";" + report_identifier

        if vvset_name:
            report_identifier = "volumeName:set:" + vvset_name + ";" + report_identifier
        if hostset_name:
            report_identifier = "hostname:set:" + vvset_name + ";" + report_identifier

        url = self._generate_systemreporter_url(api="vlunstatistics", samplefreq=samplefreq,
                                                is_at_time=False, query=query, report_identifier=report_identifier)
        response, body = self.http.get(url)
        return body
