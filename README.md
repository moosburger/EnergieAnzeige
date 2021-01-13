# EnergieAnzeige
Python Tools for energy vizalisation

Python scripts for collecting the data from victron mqtt broker. Data are written to the influx database and processed with grafana.
runs on Raspi with dietpi, influxdb and grafana.

More Info under
Dashboard
https://github.com/netzkind/telegraf-kostal-modbus

InfluxDB-Python Api
https://influxdb-python.readthedocs.io/en/latest/api-documentation.html#influxdbclient

InfluxDB Backup
https://github.com/eckardt/influxdb-backup
https://github.com/eckardt/influxdb-backup.sh

# PikoToModbus
Converter for the 'old' Piko inverters.
The reading takes over a customized version, which is called in the original piko.py (Piko Inverter communication software) and developed by Romuald Dufour.
The values are then loaded into a Modbus server.