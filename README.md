# SAN Exporter
Prometheus exporter for Storage Area Network (SAN)

## Architecture overview
![SAN exporter architecture](docs/images/architecture.png)

## Quick start

- Start with a dummy driver

```
$ git clone git@github.com:vCloud-DFTBA/san_exporter.git
$ cd san_exporter/
$ cp examples/dummy_config.yml config.yml
$ sudo apt-get install libxml2-dev libxslt1-dev python3.7-dev
$ pip3 install -r requirements.txt
$ python3.7 manage.py
$ curl http://10.0.2.15:8888/dummy_backend
```

- [Start with with a HPE 3PAR api simulator](docs/quickstart_with_simulator.md)

## Installation
#TODO

## Matrix of driver's metrics
#TODO

## Metrics

We all know that each SAN Storage vendor has their own glossary of terms and health/performance metrics.
But form
All metrics are prefixed with "san_" and has at least 2 labels: `backend_name` and `san_ip`

### Info metrics:
| Metrics name     | Type  | Help                                    |
| ---------------- | ----- | --------------------------------------- |
| san_storage_info | gauge | Basic information: serial, version, ... |

### Controller metrics:
| Metrics name                    | Type  | Help                                                                                            |
| ------------------------------- | ----- | ----------------------------------------------------------------------------------------------- |
| san_totalNodes                  | gauge | Total nodes                                                                                     |
| san_masterNodes                 | gauge | Master nodes                                                                                    |
| san_onlineNodes                 | gauge | Online nodes                                                                                    |
| san_compress_support            | gauge | Compress support, 1 = Yes, 0 = No                                                               |
| san_thin_provision_support      | gauge | Thin provision support, 1 = Yes, 0 = No                                                         |
| san_system_reporter_support     | gauge | System reporter support, 1 = Yes, 0 = No                                                        |
| san_qos_support                 | gauge | QoS support, 1 = Yes, 0 = No                                                                    |
| san_totalCapacityMiB            | gauge | Total system capacity in MiB                                                                    |
| san_allocatedCapacityMiB        | gauge | Total allocated capacity in MiB                                                                 |
| san_freeCapacityMiB             | gauge | Total free capacity in MiB                                                                      |
| san_cpu_system_utilization      | gauge | The average percentage of time that the processors on nodes are busy doing system I/O tasks     |
| san_cpu_compression_utilization | gauge | The approximate percentage of time that the processor core was busy with data compression tasks |
| san_cpu_total                   | gauge | The cpus spent in each mode                                                                     |

### Pool metrics:
| Metrics name                      | Type  | Help                          |
| --------------------------------- | ----- | ----------------------------- |
| san_pool_totalLUNs                | gauge | Total LUNs (or Volumes)       |
| san_pool_total_capacity_mib       | gauge | Total capacity of pool in MiB |
| san_pool_free_capacity_mib        | gauge | Free of pool in MiB           |
| san_pool_provisioned_capacity_mib | gauge | Provisioned of pool in MiB    |
| san_pool_number_read_io           | gauge | Read I/O Rate - ops/s         |
| san_pool_number_write_io          | gauge | Write I/O Rate - ops/s        |
| san_pool_read_cache_hit           | gauge | Read Cache Hits - %           |
| san_pool_write_cache_hit          | gauge | Write Cache Hits - %          |
| san_pool_read_kb gauge            | gauge | Read Data Rate - KiB/s        |
| san_pool_write_kb                 | gauge | Write Data Rate - KiB/s       |
| san_pool_read_service_time_ms     | gauge | Read Response Time - ms/op    |
| san_pool_write_service_time_ms    | gauge | Write Response Time - ms/op   |
| san_pool_read_IOSize_kb           | gauge | Read Transfer Size - KiB/op   |
| san_pool_write_IOSize_kb          | gauge | Write Transfer Size - KiB/op  |
| san_pool_queue_length             | gauge | Queue length of pool          |

### Port metrics:
| Metrics name             | Type  | Help                              |
| ------------------------ | ----- | --------------------------------- |
| san_port_number_read_io  | gauge | Port Read I/O Rate - ops/s        |
| san_port_number_write_io | gauge | Port Write I/O Rate - ops/s       |
| san_port_write_kb        | gauge | Port Write Data Rate - KiB/s      |
| san_port_read_kb         | gauge | Port Read Data Rate - KiB/s       |
| san_port_write_IOSize_kb | gauge | Port Write Transfer Size - KiB/op |
| san_port_read_IOSize_kb  | gauge | Port Read Transfer Size - KiB/op  |
| san_port_queue_length    | gauge | Queue length of port              |

For more information about specific metrics of SANs, see [Specific SAN Metrics](docs/specific_san_metrics.md)

## Integrate with Prometheus, Alertmanager and Grafana

- [Example prometheus alert rules](examples/rules)
- [Example alertmanager alerts](examples/alerts)
- [Example grafana dashboard](examples/dashboards)
