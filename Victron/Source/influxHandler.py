#!/usr/bin/env python3
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
    ImportError = None
    import sys
    import json
    import time
    from collections import namedtuple as NamedTuple
    from itertools import zip_longest
    from influxdb import InfluxDBClient
    from influxdb import exceptions as DbException
    from requests import exceptions as requestException

except Exception as e:
    ImportError = e

# #################################################################################################
# # UmgebungsVariablen / Globals
# #################################################################################################
_SensorData = NamedTuple('SensorData', 'device instance type value timestamp')

# #################################################################################################
# # private Imports
# #################################################################################################
try:
    PrivateImportError = None
    import Error
    import Utils
    from configuration import Global as _conf, PvInverter as PvInv, Grid, Battery, VeBus, System

except Exception as e:
    PrivateImportError = e

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

    try:
        ## Import fehlgeschlagen
        if (PrivateImportError):
            raise IOError(PrivateImportError)

        if (ImportError):
            raise IOError(ImportError)
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

            self.host = _host
            self.port = _port
            self.username = _username
            self.password = _password
            self.database = _database
            self.gzip = _gzip
            self.influxdb_client = None

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
        def _init_influxdb_database(self, _database, callee):

             # close connection if reload
            if self.influxdb_client is not None:
                self.influxdb_client.close()
                time.sleep(1)   #Login

            ver = None
            try:
                self.influxdb_client = InfluxDBClient(host = self.host, port = self.port, username =self.username, password = self.password, database = _database, gzip = self.gzip)
                ver = self.influxdb_client.ping()
                self.log.info("InfluxDB Version: {}".format(ver))

                databases = self.influxdb_client.get_list_database()
                if (len(list(filter(lambda x: x['name'] == _database, databases))) == 0):
                    self.log.info("Erstelle Datenbank: {}".format(_database))
                    self.influxdb_client.create_database(_database)

                if (callee == 'VrmGetData'):
                    self.log.info("Setzte VrmGetData Retention Policy: {}".format(_database))
                    #self.influxdb_client.alter_retention_policy('daily', database = self.database, duration = '52w', replication = 0, default = True)
                    #self.influxdb_client.create_retention_policy('sechs_monate', database = _database, duration = '26w', replication = 1, default = True)
                    self.influxdb_client.create_retention_policy('daily', database = _database, duration = '52w', replication = 1, default = True)

                    #self.log.info("Setzte Continuous query: {}".format(_database))
                    #select_clause = 'SELECT mean("AcPvOnGridPower") INTO "PvInvertersAcEnergyForwardDay" FROM "system" WHERE ("instance" = "Gateway") GROUP BY time(1d)'
                    #self.influxdb_client.create_continuous_query('PvDay', select_clause, _database, 'EVERY 10s FOR 1d')

                #if (callee == 'CalculationsMonth'):
                #    self.log.info("Setzte CalculationsMonth Retention Policy: {}".format(_database))
                    #self.influxdb_client.alter_retention_policy('daily', database = self.database, duration = '52w', replication = 0, default = True)
                    #self.influxdb_client.create_retention_policy('sechs_monate', database = _database, duration = '26w', replication = 1, default = True)
                    self.influxdb_client.create_retention_policy('daily', database = _database, duration = '52w', replication = 1, default = True)

                    #self.log.info("Setzte Continuous query: {}".format(_database))
                    #select_clause = 'SELECT mean("AcPvOnGridPower") INTO "PvInvertersAcEnergyForwardDay" FROM "system" WHERE ("instance" = "Gateway") GROUP BY time(1d)'
                    #self.influxdb_client.create_continuous_query('PvDay', select_clause, _database, 'EVERY 10s FOR 1d')

                self.influxdb_client.switch_database(_database)
                self.log.info("{} initialisiert die Datenbank: {}".format(callee, _database))

                if (callee == 'VrmGetData'):
                    policyList = self.influxdb_client.get_list_retention_policies(database = _database)
                    self.log.info("VrmGetData {} Retention Policies: {}".format(_database, policyList))
                    queryList = self.influxdb_client.get_list_continuous_queries()
                    self.log.info("VrmGetData {} Continuous query: {}".format(_database, queryList))

                if (callee == 'CalculationsMonth'):
                    policyList = self.influxdb_client.get_list_retention_policies(database = _database)
                    self.log.info("CalculationsMonth {} Retention Policies: {}".format(_database, policyList))
                    queryList = self.influxdb_client.get_list_continuous_queries()
                    self.log.info("CalculationsMonth {} Continuous query: {}".format(_database, queryList))

            except requestException.ConnectionError as e:
                self.log.error("ConnectionError (Init) : {}".format(e))
                #for info in sys.exc_info():
                 #   self.log.error("{}".format(info))

            except:
                self.log.error("Start Sequenz  (Init)")
                for info in sys.exc_info():
                    self.log.error("{}".format(info))
                self.log.error("Ende Sequenz\nSonstiger Error")

            return ver

    #        ping()  tested die verbindung und gibt die influx version zurück.
    # close() schließt den http Socket,

    # influx startet die console
    # DROP DATABASE EnergyAnzeige löscht diese

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
                print(query)
                result1 = self.influxdb_client.query(query)
                print(result1)

            except:
                for info in sys.exc_info():
                    self.log.error("{}".format(info))

            return False

    # # Ende Funktion: ' _isEmpty_influxdb_database ' ####################################################

    # #################################################################################################
    # #  Funktion: '_send_sensor_data_to_influxdb '
    ## \details
    #   \param[in]     sensor_data
    #   \return          -
    # #################################################################################################
        def _send_sensor_data_to_influxdb(self, sensor_data):

            json.json_body = [
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
            strFields = ''
            valueCnt = 0
            for type, value in zip_longest(sensor_data.type, sensor_data.value):
                jsDict.update( {type:value} )
                strFields = strFields + " " + str(type) + "=" + str(value)
                valueCnt += 1

            json.json_body[0]["fields"] = jsDict
            self.log.debug("json_body: {}".format(json.json_body[0], valueCnt))

            retVal = False
            try:
                retVal = self.influxdb_client.write_points(json.json_body)

            except requestException.ChunkedEncodingError as e:
                self.log.error("ChunkedEncodingError (Write): {}\nAnzahl Daten: {} e: {}".format(json.json_body, valueCnt, e))
                #for info in sys.exc_info():
                #    self.log.error("{}".format(info))

            except DbException.InfluxDBServerError as e:
                self.log.error("ServerError (Write): {}\nAnzahl Daten: {} e: {}".format(json.json_body, valueCnt, e))
                #for info in sys.exc_info():
                #    self.log.error("{}".format(info))

            except DbException.InfluxDBClientError as e:
                self.log.error("CientError (Write): {}\nAnzahl Daten: {} e: {}".format(json.json_body, valueCnt, e))
                #for info in sys.exc_info():
                #    self.log.error("{}".format(info))

            except requestException.ConnectionError as e:
                self.log.error("ConnectionError (Write): {}\nAnzahl Daten: {} e: {}".format(json.json_body, valueCnt, e))
                #for info in sys.exc_info():
                #    self.log.error("{}".format(info))

            except:
                self.log.error("Start Sequenz")
                for info in sys.exc_info():
                    self.log.error("{}".format(info))
                self.log.error("Ende Sequenz\nSonstiger Error (Write): {}\nAnzahl Daten: {}".format(json.json_body, valueCnt))

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

##### Fehlerbehandlung #####################################################
    except IOError as e:
        print('Eine der Bibliotheken konnte nicht geladen werden!\n{}!\n'.format(e))

    except:
        for info in sys.exc_info():
            print ("Fehler: {}".format(info))

# # Ende Klasse: ' influxIO ' ####################################################################

# # DateiEnde #####################################################################################

