# Metrics for specific SAN

**Dell Unity**

| Metrics name              | Type  | Help                              |
| ------------------------- | ----- | --------------------------------- |
| san_lun_number_read_io    | gauge | LUN Read IOPS                     |
| san_lun_number_write_io   | gauge | LUN Write IOPS                    |
| san_lun_read_kb           | gauge | LUN Read Data Rate - KiB/s        |
| san_lun_write_kb          | gauge | LUN Write Data Rate - KiB/s       |
| san_lun_response_time_ms  | gauge | LUN Response Time - ms            |
| san_disk_number_read_io   | gauge | Disk Read IOPS                    |
| san_disk_number_write_io  | gauge | Disk Write IOPS                   |
| san_disk_read_kb          | gauge | Disk Read Data Rate - KiB/s       |
| san_disk_write_kb         | gauge | Disk Write Data Rate - KiB/s      |
| san_disk_response_time_ms | gauge | Disk Response Time - ms           |
| san_node_utilization      | gauge | Total percentage of CPUs          |
| san_node_temperature      | gauge | Node Temperature - degree Celcius |

**SC 8000**

| Metrics name                         | Type  | Help                                          |
| ------------------------------------ | ----- | --------------------------------------------- |
| san_controller_read_service_time_ms  | gauge | Controller Read Response Time - ms/op         |
| san_controller_write_service_time_ms | gauge | Controller Write Response Time - ms/op        |
| san_controller_average_IOSize_kb     | gauge | Controller Average Transfer Size - KiB/op     |
| san_controller_read_kb               | gauge | Controller Read Data Rate - KiB/s             |
| san_controller_write_kb              | gauge | Controller Write Data Rate - KiB/s            |
| san_controller_total_kb              | gauge | Controller Total Data Rate - KiB/s            |
| san_controller_number_write_io       | gauge | Controller Write I/O Rate - ops/s             |
| san_controller_number_read_io        | gauge | Controller Read I/O Rate - ops/s              |
| san_controller_number_total_io       | gauge | Controller Total I/O Rate - ops/s             |
| san_cpu_percent_usage                | gauge | Controller The percent usage of the CPU       |
| san_memory_percent_usage             | gauge | Controller The percent usage of the CPU       |
| san_volume_read_service_time_ms      | gauge | Volume Read Response Time - ms/op             |
| san_volume_write_service_time_ms     | gauge | Volume Write Response Time - ms/op            |
| san_volume_average_IOSize_kb         | gauge | Volume Average Transfer Size - KiB/op         |
| san_volume_read_kb                   | gauge | Volume Read Data Rate - KiB/s                 |
| san_volume_write_kb                  | gauge | Volume Write Data Rate - KiB/s                |
| san_volume_total_kb                  | gauge | Volume Total Data Rate - KiB/s                |
| san_volume_number_write_io           | gauge | Volume Write I/O Rate - ops/s                 |
| san_volume_number_read_io            | gauge | Volume Read I/O Rate - ops/s                  |
| san_volume_number_total_io           | gauge | Volume Total I/O Rate - ops/s                 |
| san_alert                            | gauge | SAN alert                                     |
| san_sc_total_capacity_mib            | gauge | Total capacity of SC in MiB                   |
| san_sc_use_capacity_mib              | gauge | Use of SC in MiB                              |
| san_sc_free_capacity_mib             | gauge | Free of SC in MiB                             |
| san_sc_server                        | gauge | Info servers for the Storage Center           |
| san_sc_info                          | gauge | SC information by DSM managed                 |
| san_port_sc                          | gauge | Info port in SC                               |
| san_controller_availableMemoryMib    | gauge | Info and availableMemory in Mib of controller |

**HP MSA**

| Metrics name     | Type  | Help                                                         |
| ---------------- | ----- | ------------------------------------------------------------ |
| san_node_iops    | gauge | The number of input/output operations per second in the node |
| san_node_bps     | gauge | Node throughput bytes per second                             |
| san_pool_volumes | gauge | Number of volumes in the pool                                |
| san_pool_bps     | gauge | Pool throughput byte per second                              |
| san_pool_iops    | gauge | The number of input/output operations per second in the pool |
| san_volume       | gauge | Volume size                                                  |

**Hitachi G700 (Through Ops Center)**

| **Metrics name**           | Type  | Help                             |
| -------------------------- | ----- | -------------------------------- |
| san_port_total_io          | gauge | Port total IO Rate - ops/s       |
| san_port_total_transfer    | gauge | Port total Transfer Rate - kb/s  |
| san_pool_read_transfer     | gauge | Pool read transfer rate - kb/s   |
| san_pool_write_transfer    | gauge | Pool write transfer rate - kb /s |
| san_pool_used_capacity_mib | gauge | Used capacity of pool in Mib     |
