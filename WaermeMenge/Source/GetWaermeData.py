#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# #################################################################################################
##  \brief       Main zur Abfrage des Vrm mqtt Brokers in der CCGX/VenusGX
#   \details     Sortiert die Werte dann in die InfluxDatenbank ein
#   \file        GetWaermeData.py
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
##          /usr/bin/python3 /mnt/dietpi_userdata/WaermeMenge/GetWaermeData.py
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
    from configuration import Global as _conf, Waerme
    from influxHandler import influxIO, _SensorData as SensorData
    import SunRiseSet

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
    #result = influxHdlrLong.influxdb_client.query(Forward_Day)

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
                sensor_data = SensorData(device, instance, [searchFor,], [round(newVal, 2),], timestampSET)
                print(sensor_data)
                #influxHdlr._send_sensor_data_to_influxdb(sensor_data, "GetWaermeData")
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
# #  Funktion: '_getVal2 '
## 	\details    -
#   \param[in] 	myVal
#   \return 	myVal
# #################################################################################################
def _getVal2(influxHandler, strQUERY, Instance, DayTimeStamp, where, vari, callee):

    dayCnt = 0
    locDayTimeStamp = DayTimeStamp
    resultVar = 0.0
    try:
        while (True):
            QUERY = strQUERY.format(locDayTimeStamp)
            tmp = influxHandler._Query_influxDb([QUERY,], Instance, where, f'{callee}_getVal2')
            print(tmp)
            if ("Zero" in  str(tmp)):
                print(f'{where} {vari}: {tmp}; DayTimeStamp: {locDayTimeStamp}; QUERY: {QUERY}')

                #self.log.info(f'DayTimeStamp-1: {locDayTimeStamp}')
                objDateTime = datetime.strptime(locDayTimeStamp, "'%Y-%m-%dT%H:%M:%S.0Z'")
                #self.log.info(f'DayTimeStamp-2: {objDateTime.year}-{objDateTime.month}-{objDateTime.day}')
                objDateTime = (objDateTime - timedelta(days=1))
                #self.log.info(f'DayTimeStamp-3: {objDateTime.year}-{objDateTime.month}-{objDateTime.day}')
                locDayTimeStamp = _conf.DAYTIMESTAMP.format(objDateTime.year, objDateTime.month, objDateTime.day)
                #self.log.info(f'DayTimeStamp-4: {locDayTimeStamp}')
                dayCnt += 1
                tmp[0] = 0.0
                if (dayCnt >= 5):
                    break

                continue

            elif ("NoConnecion" in str(tmp)) or ("Error" in str(tmp)):
                self.log.warning("_getVal2: Fehler beim lesen von {}".format(QUERY))
                ## Database initialisieren
                influxHandler._close_connection(influxHandler.database, 'WaermeMenge')
                time.sleep(_conf.INLFUXDB_SHORT_DELAY)
                influxHandler._init_influxdb_database(influxHandler.database, 'WaermeMenge')
                tmp[0] = 0.0

            print(str(tmp))
            break

        resultVar = float(tmp[0])
        print(resultVar)

    except Exception as e:
        print(f"_getVal2: {e} from {callee}")

    except:
        print("_getVal2: {}".format(errLog))
        for info in sys.exc_info():
            print("{}".format(info))

    return resultVar

    # # Ende Funktion: '_getVal2 ' ############################################################

# #################################################################################################
# #  Funktion: '_getVal '
## 	\details    -
#   \param[in] 	myVal
#   \return 	myVal
# #################################################################################################
def _getVal(influxHandler, QUERY, Instance, where, callee):

    tmp = influxHandler._Query_influxDb([QUERY,], Instance, where, f'{callee}_getVal')
    if ("Zero" in  str(tmp)):
        tmp[0] = 0.0

    elif ("NoConnecion" in str(tmp)) or ("Error" in str(tmp)):
        print("_getVal: Fehler beim lesen von {}".format(QUERY))
        ## Database initialisieren
        influxHandler._close_connection(influxHandler.database, 'WaermeMenge')
        time.sleep(_conf.INLFUXDB_SHORT_DELAY)
        influxHandler._init_influxdb_database(influxHandler.database, 'WaermeMenge')
        tmp[0] = 0.0

    return tmp[0]

# # Ende Funktion: '_getVal ' #####################################################################

# #################################################################################################
# #  Funktion: ' _main '
## \details         Die Einsprungsfunktion, ruft alle Funktionen und Klassen auf.
#   \param[in]    argv
#   \return            -
# #################################################################################################
def _main(argv):
    global influxHdlr, influxHdlrLong
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
        influxHdlrLong = influxIO(_host = _conf.INFLUXDB_ADDRESS, _port = _conf.INFLUXDB_PORT, _username = _conf.INFLUXDB_USER, _password = _conf.INFLUXDB_PASSWORD, _database = None, _gzip = _conf.INFLUXDB_ZIPPED, logger = logging)
################################################
################################################
################################################
################################################

        AMh, AMm, UMh, UMm, lt_tag, lt_monat, lt_jahr, lt_h, lt_m, lt_s = SunRiseSet.get_Info([])
        influxHdlr._init_influxdb_database(_conf.INFLUXDB_DATABASE_WAERME, 'WaermeMenge')
        influxHdlrLong._init_influxdb_database(_conf.INFLUXDB_DATABASE_WAERME_LONG, 'WaermeMengeMonth')
################################################
################################################
################################################
################################################
################################################
################################################
################################################

###########################################################
        ## Gestrige Werte abspeichern
        _Now = datetime.utcnow()
        _YesterDay = _Now
        YesterDayTimeStamp = _conf.DAYTIMESTAMP.format(2023,3,1)

        locDayTimeStamp  = "'{}-{:02}-{:02}T00:30:00'"
        timestampSearch =  "'2023-04-04T01:00:00.0Z'"

        #DayTimeStampBack = locDayTimeStamp.format(lt_jahr, lt_monat, lt_tag)
        #objDateTime = datetime.strptime(DayTimeStampBack, "'%Y-%m-%dT%H:%M:%S'")
        #objDateTime = (objDateTime - timedelta(days=1))
        #LastMonthTimeStamp = _conf.MONTHTIMESTAMP.format(objDateTime.year, objDateTime.month)
        #print(LastMonthTimeStamp)

        #tmpVal = "SELECT last(GasForwardDaySoFar_cbm) FROM heizung where instance='PUFFER' and time >= {}"
        #GasForwardDaySoFar_cbm = _getVal2(influxHdlr, tmpVal, Waerme.RegEx, YesterDayTimeStamp, 'last', 'GasForwardDaySoFar_cbm','_calcDailyHeatQuantitySoFar')
        #tmpVal = "SELECT last(GasForwardDaySoFar_kWh) FROM heizung where instance='PUFFER' and time >= {}"
        #GasForwardDaySoFar_kWh = _getVal2(influxHdlr, tmpVal, Waerme.RegEx, YesterDayTimeStamp, 'last', 'GasForwardDaySoFar_kWh','_calcDailyHeatQuantitySoFar')
        #datStream = (f'TimeStamp: {_YesterDay.day:02d}.{_YesterDay.month:02d}.{_YesterDay.year:4d} {lt_h:02d}:{lt_m:02d}:{lt_s:02d} Verbrauch: {GasForwardDaySoFar_cbm:9.2f} cbm; {GasForwardDaySoFar_kWh:9.2f} kWh\n')
        #print(datStream)

        tmpVal = "SELECT (GasForwardDaySoFar_cbm) FROM heizung where instance='PUFFER' and time >= {}".format(timestampSearch)
        _Forward_Day(tmpVal, Waerme.RegEx, Waerme.Label1, 7.20, 'GasForwardDaySoFar_cbm', timestampSearch)
        tmpVal = "SELECT (GasForwardDaySoFar_kWh) FROM heizung where instance='PUFFER' and time >= {}".format(timestampSearch)
        _Forward_Day(tmpVal, Waerme.RegEx, Waerme.Label1, 79.20, 'GasForwardDaySoFar_kWh', timestampSearch)

        tmpVal = "SELECT (WasserForwardDaySoFar_Lit) FROM heizung where instance='PUFFER' and time >= {}".format(timestampSearch)
        #_Forward_Day(tmpVal, Waerme.RegEx, Waerme.Label1, 260, 'WasserForwardDaySoFar_Lit', timestampSearch)
        tmpVal = "SELECT (WasserForwardDaySoFar_cbm) FROM heizung where instance='PUFFER' and time >= {}".format(timestampSearch)
        #_Forward_Day(tmpVal, Waerme.RegEx, Waerme.Label1, 0.260, 'WasserForwardDaySoFar_cbm', timestampSearch)


        #tmpVal = "SELECT last(GasForwardMonth_cbm) FROM heizung where instance='PUFFER' and time >= {}"
        #GasForwardMonth_cbm = _getVal2(influxHdlrLong, tmpVal, Waerme.RegEx, YesterDayTimeStamp, 'last', 'GasForwardMonth_cbm','_calcDailyHeatQuantitySoFar')
        #print(GasForwardMonth_cbm)

        #tmpVal = "SELECT (GasForwardMonthSoFar_cbm) FROM heizung where instance='PUFFER' and time >= {}".format(timestampSearch)
        #_Forward_Day(tmpVal, Waerme.RegEx, Waerme.Label1, 0.0, 'GasForwardMonthSoFar_cbm', timestampSearch)

        #tmpVal = "SELECT (GasForwardMonthSoFar_cbm) FROM heizung where instance='PUFFER' and time >= {}".format(LastMonthTimeStamp)
        #GasForwardMonthSoFar_cbm = _getVal(influxHdlrLong, tmpVal, Waerme.RegEx, 'GasForwardMonthSoFar_cbm', '_calcMonthlyHeatQuantitySoFar')

        #tmpVal = "SELECT first(GasForwardMonthSoFar_cbm) FROM heizung where instance='PUFFER' and time >= {}"
        #GasForwardMonthSoFar_cbm = _getVal2(influxHdlrLong, tmpVal, Waerme.RegEx, LastMonthTimeStamp, 'first', 'GasForwardMonthSoFar_cbm','_calcMonthlyHeatQuantitySoFar')
        #print(GasForwardMonthSoFar_cbm)
        #tmpVal = "SELECT last(GasForwardMonthSoFar_kWh) FROM heizung where instance='PUFFER' and time >= {}"
        #GasForwardMonthSoFar_kWh = _getVal2(influxHdlrLong, tmpVal, Waerme.RegEx, YesterDayTimeStamp, 'last', 'GasForwardMonthSoFar_kWh','_calcDailyHeatQuantitySoFar')
        #datStream = (f'TimeStamp: {_YesterDay.day:02d}.{_YesterDay.month:02d}.{_YesterDay.year:4d} {lt_h:02d}:{lt_m:02d}:{lt_s:02d} Verbrauch: {GasForwardMonthSoFar_cbm:9.2f} cbm; {GasForwardMonthSoFar_kWh:9.2f} kWh\n')
        #print(datStream)

        #~ tmpVal = "SELECT last(GasForwardMonth_cbm) FROM heizung where instance='PUFFER' and time >= {}"
        #~ GasForwardMonth_cbm = _getVal2(influxHdlrLong, tmpVal, Waerme.RegEx, YesterDayTimeStamp, 'last', 'GasForwardMonth_cbm','_calcDailyHeatQuantitySoFar')
        #~ tmpVal = "SELECT last(GasForwardMonth_kWh) FROM heizung where instance='PUFFER' and time >= {}"
        #~ GasForwardMonth_kWh = _getVal2(influxHdlrLong, tmpVal, Waerme.RegEx, YesterDayTimeStamp, 'last', 'GasForwardMonth_kWh','_calcDailyHeatQuantitySoFar')
        #~ datStream = (f'TimeStamp: {_YesterDay.day:02d}.{_YesterDay.month:02d}.{_YesterDay.year:4d} {lt_h:02d}:{lt_m:02d}:{lt_s:02d} Verbrauch: {GasForwardMonth_cbm:9.2f} cbm; {GasForwardMonth_kWh:9.2f} kWh\n')
        #~ print(datStream)




#        tmpVal = "SELECT (WasserForwardDay_Lit) FROM heizung where instance='PUFFER' and time >= {}"
#        WasserForwardDay_Lit = self._getVal2(self.influxHdlrDaily, tmpVal, Waerme.RegEx, YesterDayTimeStamp, 'last', 'WasserForwardDay_Lit','_calcDailyHeatQuantitySoFar')
#        tmpVal = "SELECT (WasserForwardDay_Lit) FROM heizung where instance='PUFFER' and time >= {}"
#        WasserForwardDay_cbm = self._getVal2(self.influxHdlrDaily, tmpVal, Waerme.RegEx, YesterDayTimeStamp, 'last', 'WasserForwardDay_cbm','_calcDailyHeatQuantitySoFar')
#        datStream = (f'TimeStamp: {_YesterDay.day:02d}.{_YesterDay.month:02d}.{_YesterDay.year:4d} {lt_h:02d}:{lt_m:02d}:{lt_s:02d} Verbrauch: {WasserForwardDay_Lit:9.0f} l; {WasserForwardDay_cbm:9.2f} cbm\n')
#        print(datStream)

        ###########################################################

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

