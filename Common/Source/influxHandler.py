#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
#   pip / pip3 freeze gibt die Versionen aller Libs zurück
#
#
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
# # Debug Einstellungen
# #################################################################################################
bDebug = True
bDebugOnLinux = True

# Damit kann aus einem andern Pfad importiert werden. Diejenigen die lokal verwendet werden, vor der Pfaderweiterung importieren
if (bDebug == False):
    importPath = '/mnt/dietpi_userdata/Common'

elif(bDebugOnLinux == True):
    importPath = '/home/users/Grafana/Common'

else:
    importPath = 'D:\\Users\\Download\\PvAnlage\\Common'

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

    sys.path.insert(0, importPath)
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
    ## \details Die Initialisierung der Klasse influxIO
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
            self.IsConnected = False
            self.influxdb_client = None
            self.callee = ''

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
    # #  Funktion: '_close_connection '
    ## \details     Initialisiert die vorhandene Database, bzw. erzeugt eine neue.
    #   \param[in]     -
    #   \return          -
    # #################################################################################################
        def _close_connection(self, _database, callee):

             # close connection if reload
            if (self.influxdb_client is not None) and (self.IsConnected == True):
                self.log.info("")
                self.log.info("{} schließt die Datenbank: {}".format(callee, _database))
                self.influxdb_client.close()
                self.influxdb_client = None
                self.IsConnected = False
                self.log.info("self-{} - {} (Close)".format(self.callee, callee))

    # #################################################################################################
    # #  Funktion: '_init_influxdb_database '
    ## \details     Initialisiert die vorhandene Database, bzw. erzeugt eine neue.
    #   \param[in]     -
    #   \return          -
    # #################################################################################################
        def _init_influxdb_database(self, _database, callee):

            self.callee = callee

             # close connection if reload
            if (self.influxdb_client is not None) and (self.IsConnected == True):
                self.influxdb_client.close()
                self.influxdb_client = None
                self.IsConnected = False
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
                    #self.influxdb_client.create_retention_policy('daily', database = _database, duration = '52w', replication = 1, default = True)

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

                self.IsConnected = True
                self.log.info("self.{} (Init)".format(self.callee))

            except requestException.ConnectionError as e:
                self.log.error("ConnectionError (Init) von {}: {}".format(callee, e))
                self.IsConnected = False
                #for info in sys.exc_info():
                 #   self.log.error("{}".format(info))

            except:
                self.log.error("Start Sequenz (Init)")
                for info in sys.exc_info():
                    self.log.error("{}".format(info))
                self.log.error("Ende Sequenz\nSonstiger Error")
                self.IsConnected = False

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
        def _send_sensor_data_to_influxdb(self, sensor_data, callee):

            json.json_body = [
                {
                    "measurement": sensor_data.device,          # pvinverter
                    "tags": {
                                "instance": sensor_data.instance # Piko, SMA
                    },
                    "fields": {                                 # AcEnergyForwardDaySoFar: 1000.0
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
            if (self.IsConnected == False):
                self.log.error("NoConnecion (Write) von self.{} - {}".format(self.callee, callee))
                return "NoConnecion"

            try:
                retVal = self.influxdb_client.write_points(json.json_body)

            except requestException.ChunkedEncodingError as e:
                self.log.error("ChunkedEncodingError (Write) von self.{} - {}: {}\nAnzahl Daten: {} e: {}".format(self.callee, callee, json.json_body, valueCnt, e))
                #for info in sys.exc_info():
                #    self.log.error("{}".format(info))

            except DbException.InfluxDBServerError as e:
                self.log.error("ServerError (Write) von self.{} - {}: {}\nAnzahl Daten: {} e: {}".format(self.callee, callee, json.json_body, valueCnt, e))
                #for info in sys.exc_info():
                #    self.log.error("{}".format(info))

            except DbException.InfluxDBClientError as e:
                self.log.error("CientError (Write) von self.{} - {}: {}\nAnzahl Daten: {} e: {}".format(self.callee, callee, json.json_body, valueCnt, e))
                #for info in sys.exc_info():
                #    self.log.error("{}".format(info))

            except requestException.ConnectionError as e:
                self.log.error("ConnectionError (Write) von self.{} - {}: {}\nAnzahl Daten: {} e: {}".format(self.callee, callee, json.json_body, valueCnt, e))
                #for info in sys.exc_info():
                #    self.log.error("{}".format(info))

            except:
                self.log.error("Start Sequenz (Write)")
                for info in sys.exc_info():
                    self.log.error("{}".format(info))
                self.log.error("Ende Sequenz\nSonstiger Error (Write) von self.{} - {}: {}\nAnzahl Daten: {} e: {}".format(self.callee, callee, json.json_body, valueCnt, e))

            return retVal

    # # Ende Funktion: ' _send_sensor_data_to_influxdb ' ##############################################

    # #################################################################################################
    # #  Funktion: '_Query_influxDb '
    ## \details     Abfrage der Datenbank
    #   \param[in]     -
    #   \return          -
    # #################################################################################################
        def _Query_influxDb(self, queries, measurement, searchFor, callee):

            try:
                retVal = []
                points = []
                results = []
                errQuery = ''
                errPoint = ''
                errResult = ''

                if (self.IsConnected == False):
                    # _Query_influxDb wird im Augenblick nur von der  CalcPercentage.py benutzt beim lesen für die berechneten Daten
                    self.log.error("NoConnecion (Query) von self.{} - {}".format(self.callee, callee))
                    retVal.append("NoConnecion")
                    return retVal

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

            except requestException.ChunkedEncodingError as e:
                if (errQuery != ''):
                    self.log.error("ChunkedEncodingError (Query) von self.{} - {}: {}\n e: {}".format(self.callee, callee, errQuery, e))

                # fraglich ob die Fehler hier auftreten
                if (errPoint != ''):
                    self.log.error("ChunkedEncodingError (Point) von self.{} - {}: {}\n e: {}".format(self.callee, callee, errPoint, e))
                if (errResult != ''):
                    self.log.error("ChunkedEncodingError (Result) von self.{} - {}: {}\n e: {}".format(self.callee, callee, errResult, e))

            except DbException.InfluxDBServerError as e:
                if (errQuery != ''):
                    self.log.error("ServerError (Query) von self.{} - {}: {}\n e: {}".format(self.callee, callee, errQuery, e))

                # fraglich ob die Fehler hier auftreten
                if (errPoint != ''):
                    self.log.error("ServerError (Point) von self.{} - {}: {}\n e: {}".format(self.callee, callee, errPoint, e))
                if (errResult != ''):
                    self.log.error("ServerError (Result) von self.{} - {}: {}\n e: {}".format(self.callee, callee, errResult, e))

            except DbException.InfluxDBClientError as e:
                if (errQuery != ''):
                    self.log.error("CientError (Query) von self.{} - {}: {}\n e: {}".format(self.callee, callee, errQuery, e))

                # fraglich ob die Fehler hier auftreten
                if (errPoint != ''):
                    self.log.error("CientError (Point) von self.{} - {}: {}\n e: {}".format(self.callee, callee, errPoint, e))
                if (errResult != ''):
                    self.log.error("CientError (Result) von self.{} - {}: {}\n e: {}".format(self.callee, callee, errResult, e))

            except requestException.ConnectionError as e:
                if (errQuery != ''):
                    self.log.error("ConnectionError (Query) von self.{} - {}: {}\n e: {}".format(self.callee, callee, errQuery, e))

                # fraglich ob die Fehler hier auftreten
                if (errPoint != ''):
                    self.log.error("ConnectionError (Point) von self.{} - {}: {}\n e: {}".format(self.callee, callee, errPoint, e))
                if (errResult != ''):
                    self.log.error("ConnectionError (Result) von self.{} - {}: {}\n e: {}".format(self.callee, callee, errResult, e))

            except:
                self.log.error("Start Sequenz (Read) von self.{} - {}".format(self.callee, callee))
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

