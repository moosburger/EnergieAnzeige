#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# #################################################################################################
##  \brief       Main zur Abfrage des Vrm mqtt Brokers in der CCGX/VenusGX
#   \details     Sortiert die Werte dann in die InfluxDatenbank ein
#   \file        SetDailyEnergy.py
#
#  \date        Erstellt am: 26.05.2020
#  \author     moosburger
#
# <History\> ######################################################################################
# Version     Datum      Ticket#     Beschreibung
# 1.0         26.05.2020
#
# #################################################################################################

# #################################################################################################
# # Debug Einstellungen
# #################################################################################################
bDebug = False
bDebugOnLinux = False

# Damit kann aus einem andern Pfad importiert werden. Diejenigen die lokal verwendet werden, vor der Pfaderweiterung importieren
if (bDebug == False):
    importPath = '/mnt/dietpi_userdata/Common'

elif(bDebugOnLinux == True):
    importPath = '/home/gerhard/Grafana/Common'

else:
    importPath = 'D:\\Users\\Download\\PvAnlage\\Common'

#
#
#
#
#/usr/bin/python3 /mnt/dietpi_userdata/EnergieAnzeige/SetDailyEnergy.py
#
#
#
#
#

# #################################################################################################
# # Python Imports (Standard Library)
# #################################################################################################
try:
    ImportError = None
    import sys
    import os
    from datetime import datetime
    from datetime import timedelta
    import logging

except Exception as e:
    ImportError = e

# #################################################################################################
# # private Imports
# #################################################################################################
try:
    PrivateImportError = None

    sys.path.insert(0, importPath)
    from configuration import Global as _conf, PvInverter as PvInv, Grid, Battery, VeBus, System
    from influxHandler import influxIO, _SensorData as SensorData

except Exception as e:
    PrivateImportError = e

# #################################################################################################
# # UmgebungsVariablen / Globals
# #################################################################################################

# #################################################################################################
# # Funktionen
# # Prototypen
# # if __name__ == '__main__':
# #################################################################################################

# #################################################################################################
# #  Funktion: '_Forward_Day '
## \details
#   \param[in]     -
#   \return          -
# #################################################################################################
def _Forward_Day(Forward_Day, device, instance, newVal, searchFor, timestampSET):

    iCnt = 0
    result = influxHdlr.influxdb_client.query(Forward_Day)
    points = (list(result.get_points(device)))
    for point in points:
        if len(point) > 0:
            myVal = point[searchFor]
            date_time_str = point['time']

            if (myVal != 0.0):
                datStream = ("{:>8}:{:>38} {:10.3f}  {}".format(instance, searchFor, myVal, date_time_str))
                print(datStream)

                #_write_File("/mnt/dietpi_userdata/SolarExport/TotalEnergy11.log" , datStream + '\n', "a")
                #logging.warning("{:>8}-TOTAL:     {:10.3f}        {}".format(instance, myVal, date_time_str))

                #if (newVal > -1):
                #sensor_data = SensorData(device, instance, [searchFor,], [round(newVal, 2),], timestampSET)
                #print(sensor_data)
                #influxHdlr._send_sensor_data_to_influxdb(sensor_data, "SetDailyEnergy")
                #iCnt = iCnt + 1
                #if (iCnt > 3):
                break

# #################################################################################################
# #  Funktion: '_Query_influxDb '
## \details     Abfrage der Datenbank
#   \param[in]     -
#   \return          -
# #################################################################################################
def _Query_influxDb(queries, measurement, searchFor, callee):

    bIsPoint = False
    bIsQuery = False
    bIsResult = False
    retVal = []
    points = []
    results = []
    errQuery = ''
    errPoint = ''
    errPointLen = 0
    errResult = ''

    try:
            for query in queries:
                bIsQuery = True
                errQuery = query
                result = influxHdlr.influxdb_client.query(query)
                results.append(result)

            for result in results:
                bIsResult = True
                errResult = result
                point = list(result.get_points(measurement))
                points.append(point)

            for point in points:
                bIsPoint = True
                errPoint = point
                errPointLen = len(point)
                if (searchFor not in str(point)):
                    print("Key '{}' existiert nicht. {} -{}-".format(searchFor, callee, point[0]))
                    retVal.append(point[0])

                elif (len(point) > 1):
                    for k in range (0, len(point)):
                        retVal.append(float(point[k][searchFor]))
                elif (len(point) > 0):
                    retVal.append(float(point[0][searchFor]))
                else:
                    retVal.append(0.0)

    except:
        for info in sys.exc_info():
            print("{}".format(info))
        print("errQuery: {} {}".format(errQuery, bIsQuery))
        print("errResult: {} {}".format(errResult, bIsResult))
        print("errPoint: {} {}".format(errPoint, bIsPoint))
        if (bIsPoint):
            print("errPointLen: {}".format(errPointLen))
            print("searchFor: {}".format(searchFor))

        retVal.append("Error")

    return retVal

    # # Ende Funktion: ' _Query_influxDb ' ####################################################

# #################################################################################################
# #  Funktion: ' _main '
## \details         Die Einsprungsfunktion, ruft alle Funktionen und Klassen auf.
#   \param[in]    argv
#   \return            -
# #################################################################################################
def _main(argv):
    global influxHdlr
#########
## history -c
## /mnt/dietpi_userdata/EnergieAnzeige
## /mnt/dietpi_userdata/SolarExport
#########

##Piko AcEnergyForwardDay
##Sma AcEnergyForwardDay
##PvInvertersAcEnergyForwardTotal
##Piko AcEnergyForwardTotal
##Sma AcEnergyForwardTotal

##PvInvertersAcEnergyForwardDay

##Piko AcEnergyForwardMonth
##Sma AcEnergyForwardMonth
##PvInvertersAcEnergyForwardMonth

##Piko AcEnergyForwardYear
##Sma AcEnergyForwardYear
##PvInvertersAcEnergyForwardYear

##PvInvertersAcEnergyForwardMonthSoFar
##PvInvertersAcEnergyForwardYearSoFar

    try:
        ## Import fehlgeschlagen
        if (PrivateImportError):
            raise ModuleNotFoundError(PrivateImportError)
        if (ImportError):
            raise ModuleNotFoundError(ImportError)

################################################
        ## Database initialisieren
        influxHdlr = influxIO(_host = _conf.INFLUXDB_ADDRESS, _port = _conf.INFLUXDB_PORT, _username = _conf.INFLUXDB_USER, _password = _conf.INFLUXDB_PASSWORD, _database = None, _gzip = _conf.INFLUXDB_ZIPPED, logger = logging)
################################################
################################################
################################################
################################################
        #influxHdlr._init_influxdb_database(_conf.INFLUXDB_DATABASE, 'SetDailyEnergy')
        influxHdlr._init_influxdb_database(_conf.INFLUXDB_DATABASE_LONG, 'SetDailyEnergy')
################################################
################################################
################################################
################################################
################################################
################################################
################################################
        timestampSearch =   "'2021-11-14T00:30:00.000000Z'"
        #timestampSearch1 =  "'2021-03-26T00:30:00.000000Z'"
        SMAFORWARD_DAY = "SELECT (AcEnergyForwardDaySoFar) FROM pvinverter where instance='SMA' and time >= {}".format(timestampSearch)
        PIKOFORWARD_DAY = "SELECT (AcEnergyForwardDaySoFar) FROM pvinverter where instance='PIKO' and time >= {}".format(timestampSearch)
        FORWARD_DAY = "SELECT (PvInvertersAcEnergyForwardDaySoFar) FROM system where instance='Gateway' and time >= {}".format(timestampSearch)

        setPIKOval = 0.0
        setSMAval = 0.0

        #_Forward_Day(SMAFORWARD_DAY, PvInv.RegEx, PvInv.Label1, setSMAval,'AcEnergyForwardDaySoFar', timestampSearch)
        #_Forward_Day(PIKOFORWARD_DAY, PvInv.RegEx, PvInv.Label2, setPIKOval,'AcEnergyForwardDaySoFar', timestampSearch)
        #_Forward_Day(FORWARD_DAY, System.RegEx, System.Label1, setSMAval + setPIKOval ,'PvInvertersAcEnergyForwardDaySoFar',timestampSearch)

#################################################
        timestampSearch =   "'2021-11-01T01:00:00.000000Z'"
        #timestampSearch1 =  "'2021-11-14T00:30:00.000000Z'"

        #timestampPer = "'2021-01-01T00:00:00.0Z'"
        SMAFORWARD_DAY = "SELECT (AcEnergyForwardMonthSoFar) FROM pvinverter where instance='SMA' and time >= {}".format(timestampSearch)
        PIKOFORWARD_DAY = "SELECT (AcEnergyForwardMonthSoFar) FROM pvinverter where instance='PIKO' and time >= {}".format(timestampSearch)
        FORWARD_DAY = "SELECT (PvInvertersAcEnergyForwardMonthSoFar) FROM system where instance='Gateway' and time >= {}".format(timestampSearch)

        setPIKOval = 0.0
        setSMAval = 0.0

        #_Forward_Day(SMAFORWARD_DAY, PvInv.RegEx, PvInv.Label1, setSMAval, 'AcEnergyForwardMonthSoFar', timestampSearch)
        #_Forward_Day(PIKOFORWARD_DAY, PvInv.RegEx, PvInv.Label2, setPIKOval, 'AcEnergyForwardMonthSoFar', timestampSearch)
        #_Forward_Day(FORWARD_DAY, System.RegEx, System.Label1, setPIKOval + setSMAval, 'PvInvertersAcEnergyForwardMonthSoFar', timestampSearch)

#################################################
        timestampSearch =   "'2021-01-01T01:00:00.000000Z'"
        timestampSearch1 =  "'2021-01-01T00:30:00.000000Z'"

        SMAFORWARD_DAY = "SELECT (AcEnergyForwardYearSoFar) FROM pvinverter where instance='SMA' and time >= {}".format(timestampSearch)
        PIKOFORWARD_DAY = "SELECT (AcEnergyForwardYearSoFar) FROM pvinverter where instance='PIKO' and time >= {}".format(timestampSearch)
        FORWARD_DAY = "SELECT (PvInvertersAcEnergyForwardYearSoFar) FROM system where instance='Gateway' and time >= {}".format(timestampSearch)

        setPIKOval = 0.0
        setSMAval = 0.0

        #_Forward_Day(SMAFORWARD_DAY, PvInv.RegEx, PvInv.Label1, setSMAval, 'AcEnergyForwardYearSoFar', timestampSearch)
        #_Forward_Day(PIKOFORWARD_DAY, PvInv.RegEx, PvInv.Label2, setPIKOval, 'AcEnergyForwardYearSoFar', timestampSearch)
        #_Forward_Day(FORWARD_DAY, System.RegEx, System.Label1, setPIKOval + setSMAval, 'PvInvertersAcEnergyForwardYearSoFar', timestampSearch)


        SMAFORWARD_DAY = "SELECT (AcEnergyForwardYear) FROM pvinverter where instance='SMA' and time >= {}".format(timestampSearch1)
        PIKOFORWARD_DAY = "SELECT (AcEnergyForwardYear) FROM pvinverter where instance='PIKO' and time >= {}".format(timestampSearch1)
        FORWARD_DAY = "SELECT (PvInvertersAcEnergyForwardYear) FROM system where instance='Gateway' and time >= {}".format(timestampSearch1)

        setPIKOval = 0.0
        setSMAval = 0.0

        #_Forward_Day(SMAFORWARD_DAY, PvInv.RegEx, PvInv.Label1, setSMAval, 'AcEnergyForwardYear', timestampSearch1)
        #_Forward_Day(PIKOFORWARD_DAY, PvInv.RegEx, PvInv.Label2, setPIKOval, 'AcEnergyForwardYear', timestampSearch1)
        #_Forward_Day(FORWARD_DAY, System.RegEx, System.Label1, setPIKOval + setSMAval, 'PvInvertersAcEnergyForwardYear', timestampSearch1)

    ##### Fehlerbehandlung #####################################################
    except ImportError as e:
        print('Eine der Bibliotheken konnte nicht geladen werden!\n{}!\n'.format(e))

#    except:
#        for info in sys.exc_info():
#            print ("Fehler: {}".format(info))

# # Ende Funktion: ' _main' #######################################################################

# #################################################################################################
# #  Funktion: 'Einsprung beim Aufruf  '
# #################################################################################################
if __name__ == '__main__':

    _main(sys.argv)

# # DateiEnde #####################################################################################

