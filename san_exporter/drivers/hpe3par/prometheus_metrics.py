import logging

from prometheus_client import Gauge, Info
from prometheus_client import generate_latest

from san_exporter.drivers import base_driver


# Ref docs: https://support.hpe.com/hpsc/doc/public/display?docId=c03606339

class HPE3ParMetrics(base_driver.Metrics):
    # License values for reported capabilities
    PRIORITY_OPT_LIC = "Priority Optimization"
    THIN_PROV_LIC = "Thin Provisioning"
    SYSTEM_REPORTER_LIC = "System Reporter"
    COMPRESSION_LIC = "Compression"

    def __init__(self, config):

        _labels = ["backend_name", "san_ip"]

        super().__init__(config=config, labels=_labels)

        self.backend_name = config['name']
        self.san_ip = config['san_ssh_ip']

        self.info_san = Info('san_storage', 'Basic information', registry=self.registry)

        self.gauge_san_total_nodes = Gauge('san_totalNodes', 'Total nodes', _labels, registry=self.registry)
        self.gauge_san_master_nodes = Gauge('san_masterNodes', 'Master nodes', _labels, registry=self.registry)
        self.gauge_san_cluster_nodes = Gauge('san_clusterNodes', 'Cluster nodes',
                                             _labels, registry=self.registry)
        self.gauge_san_online_nodes = Gauge('san_onlineNodes', 'Online nodes', _labels, registry=self.registry)
        self.gauge_san_qos_support = Gauge('san_qos_support', 'QoS support', _labels, registry=self.registry)
        self.gauge_san_thin_provision_support = Gauge('san_thin_provision_support', 'Thin provision support',
                                                      _labels, registry=self.registry)
        self.gauge_san_system_reporter_support = Gauge('san_system_reporter_support', 'System reporter support',
                                                       _labels, registry=self.registry)
        self.gauge_san_compress_support = Gauge('san_compress_support', 'Compress support',
                                                _labels, registry=self.registry)

        self.gauge_san_total_capacity_mib = Gauge('san_totalCapacityMiB', 'Total system capacity in MiB',
                                                  _labels, registry=self.registry)
        self.gauge_san_allocated_capacity_mib = Gauge('san_allocatedCapacityMiB',
                                                      'Total allowed capacity in MiB',
                                                      _labels, registry=self.registry)
        self.gauge_san_free_capacity_mib = Gauge('san_freeCapacityMiB', 'Total free capacity in MiB',
                                                 _labels, registry=self.registry)
        self.gauge_san_failed_capacity_mib = Gauge('san_failedCapacityMiB', 'Total failed capacity in MiB',
                                                   _labels, registry=self.registry)
        self.define_pool_info_metrics()
        if self.optional_metrics.get('cpu'):
            self.define_cpu_metrics()
        if self.optional_metrics.get('cpg'):
            self.define_pool_statistics_metrics()
        if self.optional_metrics.get('port'):
            self.define_port_statistics_metrics()
        if self.optional_metrics.get('alert'):
            alert_labels = ['log_content', 'backend_name', 'san_ip']
            self.alert_metric = Gauge('san_alert', 'SAN Alert', alert_labels, registry=self.registry)


    def _check_license_enabled(self, valid_licenses, license_to_check, capability):
        """Check a license against valid licenses on the array."""
        if valid_licenses:
            for license in valid_licenses:
                if license_to_check in license.get('name'):
                    return 1
            logging.debug("'%(capability)s' requires a '%(license)s' license which is not installed.",
                          {'capability': capability, 'license': license_to_check})
        return 0

    def parse_system_info(self, system_info):
        self.info_san.info({
            'san_name': system_info["name"],
            'backend_name': self.backend_name,
            'systemVersion': system_info['systemVersion'],
            'serialNumber': system_info['serialNumber'],
            'san_ip': self.san_ip,
            'model': system_info['model']
        })

        qos_support = 0
        thin_support = 0
        compression_support = 0
        system_support = 0
        if 'licenseInfo' in system_info:
            if 'licenses' in system_info['licenseInfo']:
                valid_licenses = system_info['licenseInfo']['licenses']
                qos_support = self._check_license_enabled(
                    valid_licenses, self.PRIORITY_OPT_LIC, "QoS_support")
                thin_support = self._check_license_enabled(
                    valid_licenses, self.THIN_PROV_LIC, "Thin_provisioning_support")
                system_support = self._check_license_enabled(
                    valid_licenses, self.SYSTEM_REPORTER_LIC, "System_reporter_support")
                compression_support = self._check_license_enabled(
                    valid_licenses, self.COMPRESSION_LIC, "Compression")

        self.gauge_san_total_nodes \
            .labels(backend_name=self.backend_name, san_ip=self.san_ip).set(system_info["totalNodes"])
        self.gauge_san_master_nodes \
            .labels(backend_name=self.backend_name, san_ip=self.san_ip).set(system_info["masterNode"])
        self.gauge_san_cluster_nodes \
            .labels(backend_name=self.backend_name, san_ip=self.san_ip).set(len(system_info["clusterNodes"]))
        self.gauge_san_online_nodes \
            .labels(backend_name=self.backend_name, san_ip=self.san_ip).set(len(system_info["onlineNodes"]))

        self.gauge_san_qos_support.labels(backend_name=self.backend_name, san_ip=self.san_ip).set(qos_support)
        self.gauge_san_thin_provision_support.labels(backend_name=self.backend_name, san_ip=self.san_ip)\
            .set(thin_support)
        self.gauge_san_system_reporter_support.labels(backend_name=self.backend_name, san_ip=self.san_ip)\
            .set(system_support)
        self.gauge_san_compress_support.labels(backend_name=self.backend_name, san_ip=self.san_ip)\
            .set(compression_support)

        self.gauge_san_total_capacity_mib \
            .labels(backend_name=self.backend_name, san_ip=self.san_ip).set(system_info["totalCapacityMiB"])
        self.gauge_san_allocated_capacity_mib \
            .labels(backend_name=self.backend_name, san_ip=self.san_ip).set(system_info["allocatedCapacityMiB"])
        self.gauge_san_free_capacity_mib \
            .labels(backend_name=self.backend_name, san_ip=self.san_ip).set(system_info["freeCapacityMiB"])
        self.gauge_san_failed_capacity_mib \
            .labels(backend_name=self.backend_name, san_ip=self.san_ip).set(system_info["failedCapacityMiB"])

    def define_pool_info_metrics(self):
        pool_labels = ["backend_name", "pool_name", "san_ip"]
        self.gauge_san_pool_total_lun = Gauge('san_pool_totalLUNs', 'Total LUNs (or Volumes)',
                                              pool_labels, registry=self.registry)
        self.gauge_san_pool_total_capacity_mib = Gauge('san_pool_total_capacity_mib',
                                                       'Total capacity of pool in MiB',
                                                       pool_labels, registry=self.registry)
        self.gauge_san_pool_free_capacity_mib = Gauge('san_pool_free_capacity_mib',
                                                      'Free of pool in MiB',
                                                      pool_labels, registry=self.registry)
        self.gauge_san_pool_provisioned_capacity_mib = Gauge('san_pool_provisioned_capacity_mib',
                                                             'Provisioned of pool in MiB',
                                                             pool_labels, registry=self.registry)

    def parse_pool_info(self, pool_info):

        # Set total LUN = numFPVVs + numTPVVs + numTDVVs
        #   numFPVVs: Number of fully-provisioned virtual volumes allocated in the CPG (pool).
        #   numTPVVs: Number of thinly-provisioned virtual volumes allocated in the CPG (pool).
        #   numTDVVs: Number of thinly-deduplication virtual volumes allocated in the CPG (pool).
        # Ref: https://github.com/openstack/cinder/blob/master/cinder/volume/drivers/hpe/hpe_3par_common.py#L1589
        if 'numTDVVs' in pool_info:
            total_volumes = int(pool_info['numFPVVs'] + pool_info['numTPVVs'] + pool_info['numTDVVs'])
        else:
            total_volumes = int(pool_info['numFPVVs'] + pool_info['numTPVVs'])

        if 'limitMiB' not in pool_info['SDGrowth']:
            free_capacity = int(pool_info['pool_avail_space']['usableFreeMiB'])
            total_capacity = int(pool_info['SDUsage']['usedMiB'] +
                                 pool_info['UsrUsage']['usedMiB'] +
                                 pool_info['pool_avail_space']['usableFreeMiB'])
        else:
            total_capacity = pool_info['SDGrowth']['limitMiB']
            free_capacity = int(pool_info['SDGrowth']['limitMiB'] -
                                (pool_info['UsrUsage']['usedMiB'] +
                                 pool_info['SDUsage']['usedMiB']))
        provisioned_capacity = int(pool_info['UsrUsage']['totalMiB'] +
                                   pool_info['SAUsage']['totalMiB'] +
                                   pool_info['SDUsage']['totalMiB'])

        self.gauge_san_pool_total_lun.labels(backend_name=self.backend_name, san_ip=self.san_ip,
                                             pool_name=pool_info['name']).set(total_volumes)
        self.gauge_san_pool_total_capacity_mib.labels(backend_name=self.backend_name, san_ip=self.san_ip,
                                                      pool_name=pool_info['name']).set(total_capacity)
        self.gauge_san_pool_free_capacity_mib.labels(backend_name=self.backend_name, san_ip=self.san_ip,
                                                     pool_name=pool_info['name']).set(free_capacity)
        self.gauge_san_pool_provisioned_capacity_mib.labels(backend_name=self.backend_name,
                                                            pool_name=pool_info['name'], san_ip=self.san_ip) \
            .set(provisioned_capacity)

    def define_cpu_metrics(self):
        cpu_labels = ["backend_name", "node", "mode", "cpu", "san_ip"]
        self.gauge_san_cpu_total = Gauge('san_cpu_total', 'The cpus spent in each mode',
                                         cpu_labels, registry=self.registry)

    def parse_cpu_statistics(self, cpu_statistics):
        for cpu in cpu_statistics:
            node = cpu.get('node')
            cpu_id = cpu.get('cpu')
            self.gauge_san_cpu_total.labels(backend_name=self.backend_name, san_ip=self.san_ip,
                                            node=node, cpu=cpu_id, mode='userPct') \
                .set(cpu.get('userPct'))
            self.gauge_san_cpu_total.labels(backend_name=self.backend_name, san_ip=self.san_ip,
                                            node=node, cpu=cpu_id, mode='systemPct') \
                .set(cpu.get('systemPct'))
            self.gauge_san_cpu_total.labels(backend_name=self.backend_name, san_ip=self.san_ip,
                                            node=node, cpu=cpu_id, mode='idlePct') \
                .set(cpu.get('idlePct'))
            self.gauge_san_cpu_total.labels(backend_name=self.backend_name, san_ip=self.san_ip,
                                            node=node, cpu=cpu_id, mode='interruptsPerSec') \
                .set(cpu.get('interruptsPerSec'))
            self.gauge_san_cpu_total.labels(backend_name=self.backend_name, san_ip=self.san_ip,
                                            node=node, cpu=cpu_id, mode='contextSwitchesPerSec') \
                .set(cpu.get('contextSwitchesPerSec'))

    def define_pool_statistics_metrics(self):
        _pool_labels = ["backend_name", "pool_name", "san_ip"]
        self.gauge_san_pool_number_read_io = Gauge('san_pool_number_read_io',
                                                   'Number of Read IO per second of pool (cpg)',
                                                   _pool_labels, registry=self.registry)
        self.gauge_san_pool_number_write_io = Gauge('san_pool_number_write_io',
                                                    'Number of Write IO per second of pool (cpg)',
                                                    _pool_labels, registry=self.registry)
        self.gauge_san_pool_write_kb = Gauge('san_pool_write_kb',
                                             'Number of Write kilobytes per second of pool (cpg)',
                                             _pool_labels, registry=self.registry)
        self.gauge_san_pool_read_kb = Gauge('san_pool_read_kb',
                                            'Number of Read kilobytes per second of pool (cpg)',
                                            _pool_labels, registry=self.registry)
        self.gauge_san_pool_read_service_time_ms = Gauge('san_pool_read_service_time_ms',
                                                         'Read service time in millisecond of pool (cpg)',
                                                         _pool_labels, registry=self.registry)
        self.gauge_san_pool_write_service_time_ms = Gauge('san_pool_write_service_time_ms',
                                                          'Write service time in millisecond of pool (cpg)',
                                                          _pool_labels, registry=self.registry)
        self.gauge_san_pool_write_IOSize_kb = Gauge('san_pool_write_IOSize_kb',
                                                    'Write IO size in kilobytes statistic data of pool (cpg)',
                                                    _pool_labels, registry=self.registry)
        self.gauge_san_pool_read_IOSize_kb = Gauge('san_pool_read_IOSize_kb',
                                                   'Read IO size in kilobytes statistic data of pool (cpg)',
                                                   _pool_labels, registry=self.registry)
        self.gauge_san_pool_queue_length = Gauge('san_pool_queue_length',
                                                 'Queue length of pool (cpg)',
                                                 _pool_labels, registry=self.registry)

    def parse_pool_statistics(self, pool_statistics):
        for pool in pool_statistics:
            pool_name = pool.get('name')
            self.gauge_san_pool_number_read_io.labels(backend_name=self.backend_name, san_ip=self.san_ip,
                                                      pool_name=pool_name)\
                .set(pool['IO']['read'])
            self.gauge_san_pool_number_write_io.labels(backend_name=self.backend_name, san_ip=self.san_ip,
                                                       pool_name=pool_name)\
                .set(pool['IO']['write'])
            self.gauge_san_pool_read_kb.labels(backend_name=self.backend_name, san_ip=self.san_ip,
                                               pool_name=pool_name) \
                .set(pool['KBytes']['read'])
            self.gauge_san_pool_write_kb.labels(backend_name=self.backend_name, san_ip=self.san_ip,
                                                pool_name=pool_name) \
                .set(pool['KBytes']['write'])
            self.gauge_san_pool_read_service_time_ms.labels(backend_name=self.backend_name, san_ip=self.san_ip,
                                                            pool_name=pool_name) \
                .set(pool['serviceTimeMS']['read'])
            self.gauge_san_pool_write_service_time_ms.labels(backend_name=self.backend_name, san_ip=self.san_ip,
                                                             pool_name=pool_name) \
                .set(pool['serviceTimeMS']['write'])
            self.gauge_san_pool_read_IOSize_kb.labels(backend_name=self.backend_name, san_ip=self.san_ip,
                                                      pool_name=pool_name) \
                .set(pool['IOSizeKB']['read'])
            self.gauge_san_pool_write_IOSize_kb.labels(backend_name=self.backend_name, san_ip=self.san_ip,
                                                       pool_name=pool_name) \
                .set(pool['IOSizeKB']['write'])
            self.gauge_san_pool_queue_length.labels(backend_name=self.backend_name, san_ip=self.san_ip,
                                                    pool_name=pool_name) \
                .set(pool['queueLength'])

    def define_port_statistics_metrics(self):
        _port_labels = ["backend_name", "node", "slot", "card", "san_ip"]
        self.gauge_san_port_number_read_io = Gauge('san_port_number_read_io',
                                                   'Number of Read IO per second of port',
                                                   _port_labels, registry=self.registry)
        self.gauge_san_port_number_write_io = Gauge('san_port_number_write_io',
                                                    'Number of Write IO per second of port',
                                                    _port_labels, registry=self.registry)
        self.gauge_san_port_write_kb = Gauge('san_port_write_kb',
                                             'Number of Write kilobytes per second of port',
                                             _port_labels, registry=self.registry)
        self.gauge_san_port_read_kb = Gauge('san_port_read_kb',
                                            'Number of Read kilobytes per second of port',
                                            _port_labels, registry=self.registry)
        self.gauge_san_port_read_service_time_ms = Gauge('san_port_read_service_time_ms',
                                                         'Read service time in millisecond of port',
                                                         _port_labels, registry=self.registry)
        self.gauge_san_port_write_service_time_ms = Gauge('san_port_write_service_time_ms',
                                                          'Write service time in millisecond of port',
                                                          _port_labels, registry=self.registry)
        self.gauge_san_port_write_IOSize_kb = Gauge('san_port_write_IOSize_kb',
                                                    'Write IO size in kilobytes statistic data of port',
                                                    _port_labels, registry=self.registry)
        self.gauge_san_port_read_IOSize_kb = Gauge('san_port_read_IOSize_kb',
                                                   'Read IO size in kilobytes statistic data of port',
                                                   _port_labels, registry=self.registry)
        self.gauge_san_port_queue_length = Gauge('san_port_queue_length',
                                                 'Queue length of port',
                                                 _port_labels, registry=self.registry)

    def parse_port_statistics(self, port_statistics):
        for port in port_statistics:
            node = port.get('node')
            slot = port.get('slot')
            card = port.get('cardPort')
            self.gauge_san_port_number_read_io.labels(backend_name=self.backend_name, san_ip=self.san_ip, node=node,
                                                      slot=slot, card=card) \
                .set(port['IO']['read'])
            self.gauge_san_port_number_write_io.labels(backend_name=self.backend_name, san_ip=self.san_ip, node=node,
                                                       slot=slot, card=card) \
                .set(port['IO']['write'])
            self.gauge_san_port_read_kb.labels(backend_name=self.backend_name, san_ip=self.san_ip, node=node,
                                               slot=slot, card=card) \
                .set(port['KBytes']['read'])
            self.gauge_san_port_write_kb.labels(backend_name=self.backend_name, san_ip=self.san_ip, node=node,
                                                slot=slot, card=card) \
                .set(port['KBytes']['write'])
            self.gauge_san_port_read_service_time_ms.labels(backend_name=self.backend_name, san_ip=self.san_ip,
                                                            node=node, slot=slot, card=card) \
                .set(port['serviceTimeMS']['read'])
            self.gauge_san_port_write_service_time_ms.labels(backend_name=self.backend_name, san_ip=self.san_ip,
                                                             node=node, slot=slot, card=card) \
                .set(port['serviceTimeMS']['write'])
            self.gauge_san_port_read_IOSize_kb.labels(backend_name=self.backend_name, san_ip=self.san_ip, node=node,
                                                      slot=slot, card=card) \
                .set(port['IOSizeKB']['read'])
            self.gauge_san_port_write_IOSize_kb.labels(backend_name=self.backend_name, san_ip=self.san_ip, node=node,
                                                       slot=slot, card=card) \
                .set(port['IOSizeKB']['write'])
            self.gauge_san_port_queue_length.labels(backend_name=self.backend_name, san_ip=self.san_ip, node=node,
                                                    slot=slot, card=card) \
                .set(port['queueLength'])

    def parse_alert_metric(self, alert_list):
        for alert in alert_list:
            labels = alert
            self.alert_metric.labels(**labels).set(1)

    def parse_metrics(self, data):
        self.parse_system_info(data['system_info'])
        if len(data['pools']):
            for pool_info in data['pools']:
                self.parse_pool_info(pool_info)
        if self.optional_metrics.get('cpu'):
            self.parse_cpu_statistics(data['cpu_statistics'])
        if self.optional_metrics.get('cpg'):
            self.parse_pool_statistics(data['cpg_statistics'])
        if self.optional_metrics.get('port'):
            self.parse_port_statistics(data['port_statistics'])
        if self.optional_metrics.get('alert'):
            self.alert_metric._metrics.clear()
            self.parse_alert_metric(data['alert_list'])

    def get_metrics(self):
        metrics = generate_latest(self.registry)
        return metrics
