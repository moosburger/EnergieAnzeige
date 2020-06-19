#!/usr/bin/env python
# -*- coding: utf-8 -*-

# #################################################################################################
## \brief     Main zur Abfrage des Vrm mqtt Brokers in der CCGX/VenusGX
#  \details   Sortiert die Werte dann in die InfluxDatenbank ein
#  \file      influxHandler.py
#
#  \date      Erstellt am: 26.05.2020
#  \author    moosburger
#
# <History\> ######################################################################################
# Version     Datum      Ticket#     Beschreibung
# 1.0         26.05.2020
#
# #################################################################################################

# #################################################################################################
# # Python Imports (Standard Library)
# #################################################################################################
import sys
import logging
import json
from collections import namedtuple as NamedTuple
from influxdb import InfluxDBClient

reload(sys)
sys.setdefaultencoding("utf-8")

# #################################################################################################
# # UmgebungsVariablen / Globals
# #################################################################################################
_SensorData = NamedTuple('SensorData', 'device instance type value timestamp')

# #################################################################################################
# # private Imports
# #################################################################################################
try:
    PrivateImport = True
    import Error
    import Utils
    from configuration import Global as _conf, PvInverter as PvInv, Grid, Battery, VeBus, System
except:
    PrivateImport = False

# #################################################################################################
# # UmgebungsVariablen
# #################################################################################################

# #################################################################################################
# # Logging
# #################################################################################################
log = logging.getLogger('influxHandles')
log.setLevel(_conf.LOG_LEVEL)
fh = logging.FileHandler(_conf.LOG_FILEPATH)
fh.setLevel(logging.DEBUG)
log.addHandler(fh)
formatter = logging.Formatter(_conf.LOG_FORMAT)
fh.setFormatter(formatter)
log.addHandler(fh)

#log.debug('Debug-Nachricht')
#log.info('Info-Nachricht')
#log.warning('Warnhinweis')
#log.error('Fehlermeldung')
#log.critical('Schwerer Fehler')
# #################################################################################################
# # Classes: influxHandler
## \details Alles rund um die Datenbank
# #################################################################################################
class influxIO(object):

# #################################################################################################
# # Funktion: ' Constructor '
## \details Die Initialisierung der Klasse KeepAlive
#   \param[in]  self der Objectpointer
#   \param[in]  interval
#   \param[in]  mqttClient
#   \param[in] portal_id
#   \return -
# #################################################################################################
    def __init__(self, _host, _port, _username, _password, _database, _gzip):

        #self.influxdb_client = self
        self.influxdb_client = InfluxDBClient(host = _host, port = _port, username =_username, password = _password, database = _database, gzip = _gzip)

# # Ende Funktion: ' Constructor ' ################################################################

# #################################################################################################
# # Funktion: ' Destructor '
# #################################################################################################
    #def __del__(self):

# # Ende Funktion: ' Destructor ' #################################################################

# #################################################################################################
# # Funktionen
# # Prototypen
# # if __name__ == '__main__':
# #################################################################################################

# #################################################################################################
# #  Funktion: '_init_influxdb_database '
## \details     Initialisiert die vorhandene Database, bzw. erzeugt eine neue.
#   \param[in]     -
#   \return          -
# #################################################################################################
    def _init_influxdb_database(self, _database):
        databases = self.influxdb_client.get_list_database()
        #print databases

        if len(list(filter(lambda x: x['name'] == _database, databases))) == 0:
            self.influxdb_client.create_database(_database)

        self.influxdb_client.switch_database(_database)
        log.info("Initialisierte Datenbank: {}".format(_database))

# # Ende Funktion: ' _init_influxdb_database ' ####################################################

# #################################################################################################
# #  Funktion: '_isEmpty_influxdb_database '
## \details    leere DatenBank
#   \param[in]     -
#   \return          -
# #################################################################################################
    def _isEmpty_influxdb_database(self):

        try:
            query = "SELECT count(*) FROM {}./.*/".format(_conf.INFLUXDB_DATABASE)
            print query
            result1 = self.influxdb_client.query(query)
            print result1

        except:
            for info in sys.exc_info():
                log.error("Fehler: {}".format(info))

        return False

# # Ende Funktion: ' _init_influxdb_database ' ####################################################

# #################################################################################################
# #  Funktion: '_send_sensor_data_to_influxdb '
## \details
#   \param[in]     sensor_data
#   \return          -
# #################################################################################################
    def _send_sensor_data_to_influxdb(self, sensor_data):

        json_body = [
            {
                "measurement": sensor_data.device,
                "tags": {
                            "instance": sensor_data.instance
                },
                "fields": {
                },
                "time": sensor_data.timestamp
            }
        ]
        jsDict = {}
        for type, value in map(None, sensor_data.type, sensor_data.value):
            jsDict.update( {type:value} )

        json_body[0]["fields"] = jsDict
        log.debug(json_body)
        retVal = self.influxdb_client.write_points(json_body)
        if (retVal == False):
            retVal = self.influxdb_client.write_points(json_body)

        return retVal

# # Ende Funktion: ' _send_sensor_data_to_influxdb ' ##############################################

# #################################################################################################
# #  Funktion: '_Query_influxDb '
## \details     Abfrage der Datenbank
#   \param[in]     -
#   \return          -
# #################################################################################################
    def _Query_influxDb(self, queries, mesurement, what):

        results = []
        for query in queries:
            results.append(self.influxdb_client.query(query))

        points = []
        for result in results:
            points.append(list(result.get_points(mesurement)))

        retVal = []
        for point in points:
            if len(point) > 0:
                retVal.append(point[0][what])
            else:
                retVal.append(0)

        return retVal

# # Ende Funktion: ' _Query_influxDb ' ####################################################

# # DateiEnde #####################################################################################

