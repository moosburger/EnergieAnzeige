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
try:
    import sys
    import json
    from collections import namedtuple as NamedTuple
    from influxdb import InfluxDBClient

except:
    raise

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
    import Error
    import Utils
    from configuration import Global as _conf, PvInverter as PvInv, Grid, Battery, VeBus, System

except:
    raise

# #################################################################################################
# # UmgebungsVariablen
# #################################################################################################

# #################################################################################################
# # Logging
# #################################################################################################

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
    def __init__(self, _host, _port, _username, _password, _database, _gzip, logger):

        self.log = logger.getLogger('InfluxHandler')
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

        if len(list(filter(lambda x: x['name'] == _database, databases))) == 0:
            self.influxdb_client.create_database(_database)

        self.influxdb_client.switch_database(_database)
        self.log.info("Initialisierte Datenbank: {}".format(_database))

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
                self.log.error("{}".format(info))

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
        self.log.debug(json_body)

        retVal = False
        try:
            retVal = self.influxdb_client.write_points(json_body)
            #if (retVal == False):
                #retVal = self.influxdb_client.write_points(json_body)

        except (InfluxDBServerError):
            self.log.error("ServerError mit: {}".format(json_body))

        except (InfluxDBClientError):
            self.log.error("CientError mit: {}".format(json_body))

        except (RequestException):
            self.log.error("RequestError mit: {}".format(json_body))

        except:
            for info in sys.exc_info():
                self.log.error("{}".format(info))
            self.log.error("Sonstiger Error mit : {}".format(json_body))

        return retVal

# # Ende Funktion: ' _send_sensor_data_to_influxdb ' ##############################################

# #################################################################################################
# #  Funktion: '_Query_influxDb '
## \details     Abfrage der Datenbank
#   \param[in]     -
#   \return          -
# #################################################################################################
    def _Query_influxDb(self, queries, measurement, searchFor):

        try:
            retVal = []
            points = []
            results = []
            errQuery = ''
            errPoint = ''
            errResult = ''

            for query in queries:
                errQuery = query
                result = self.influxdb_client.query(query)
                results.append(result)

            for result in results:
                errResult = result
                point = list(result.get_points(measurement))
                points.append(point)

            for point in points:
                errPoint = point
                if (len(point) > 1):
                    for k in range (0, len(point)):
                        retVal.append(point[k][searchFor])
                elif (len(point) > 0):
                    retVal.append(point[0][searchFor])
                else:
                    retVal.append(0)
        except:
            for info in sys.exc_info():
                self.log.error("{}".format(info))
            self.log.error("errQuery: {}".format(errQuery))
            self.log.error("errResult: {}".format(errResult))
            self.log.error("errPoint: {}".format(errPoint))

        return retVal

# # Ende Funktion: ' _Query_influxDb ' ####################################################

# # DateiEnde #####################################################################################

