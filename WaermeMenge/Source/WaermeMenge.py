#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# #################################################################################################
## \brief     Berechnet die prozentuale Verteilung
#  \details
#  \file      WaermeMenge.py
#
#  \date      Erstellt am: 07.02.2023
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
bDebug = False
bDebugOnLinux = False

# Damit kann aus einem andern Pfad importiert werden. Diejenigen die lokal verwendet werden, vor der Pfaderweiterung importieren
if(bDebug == False):
    importPath = '/mnt/dietpi_userdata/Common'

elif(bDebugOnLinux == True):
    importPath = '/home/gerhard/Grafana/Common'

else:
    importPath = 'D:\\Users\\Download\\PvAnlage\\Common'

# #################################################################################################
# # Python Imports (Standard Library)
# #################################################################################################
try:
    ImportError = None
    import os
    from logging.config import fileConfig
    import logging
    import asyncio
    import sys
    import threading
    import time
    import configparser
    import shutil
    from datetime import datetime, timedelta

except Exception as e:
    ImportError = e

# #################################################################################################
# # private Imports
# #################################################################################################
try:
    PrivateImportError = None
    from GetModbus import ModBusHandler

    sys.path.insert(0, importPath)
    import Error
    import Utils
    import SunRiseSet
    from configuration import Global as _conf, Waerme
    from influxHandler import influxIO, _SensorData as SensorData

except Exception as e:
    PrivateImportError = e

# #################################################################################################
# # UmgebungsVariablen / Globals
# #################################################################################################

# #################################################################################################
# # Logging
# #################################################################################################
fileConfig('/mnt/dietpi_userdata/WaermeMenge/logging_config.ini')

# #################################################################################################
# # Funktionen
# # Prototypen
# #################################################################################################

# #################################################################################################
# # Classes: CalcWaermeMenge
#
# #################################################################################################
class CalcWaermeMenge(object):

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
    #   \param[in] CallBack
    #   \return -
    # #################################################################################################
        def __init__(self, interval, logger):

            try:
                self.log = logger.getLogger('WaermeMenge')
                self.influxHdlrDaily = influxIO(_host = _conf.INFLUXDB_ADDRESS, _port = _conf.INFLUXDB_PORT, _username = _conf.INFLUXDB_USER, _password = _conf.INFLUXDB_PASSWORD, _database = None, _gzip = _conf.INFLUXDB_ZIPPED, logger = logger)
                self.influxHdlrLong = influxIO(_host = _conf.INFLUXDB_ADDRESS, _port = _conf.INFLUXDB_PORT, _username = _conf.INFLUXDB_USER, _password = _conf.INFLUXDB_PASSWORD, _database = None, _gzip = _conf.INFLUXDB_ZIPPED, logger = logger)

                self.bufferList = []
                self.WriteEnergyToDbDelay = 0

                self.Interval_sek = interval

                ####
                ## Modbus Initialisieren
                self.mdbHdlr = ModBusHandler(logger = logger)
                self.WaermeMenge = {}
                self.IsNewDay = True

                self.TKollektor = float(-127.0)
                self.TSpeicherOben = float(-127.0)
                self.TSpeicherUnten = float(-127.0)
                self.TPufferOben = float(-127.0)
                self.TPufferUnten = float(-127.0)
                self.TFestStoffKessel = float(-127.0)
                self.TInternal = float(-127.0)
                self.TWasser = float(-127.0)

                self.GasImpuls = int(0)
                self.Gas_cbm = float(0.0)
                self.Gas_kWh = float(0.0)
                self.WasserImpuls = int(0)
                self.Wasser_Lit = int(0)
                self.Wasser_cbm = float(0.0)

                self.Last_TKollektor = float(-127.0)
                self.Last_TSpeicherOben = float(-127.0)
                self.Last_TSpeicherUnten = float(-127.0)
                self.Last_TPufferOben = float(-127.0)
                self.Last_TPufferUnten = float(-127.0)
                self.Last_TFestStoffKessel = float(-127.0)
                self.Last_TInternal = float(-127.0)
                self.Last_TWasser = float(-127.0)

                self.Last_GasImpuls = int(0)
                self.Last_WasserImpuls = int(0)
                self.Last_totWasser_Lit = int(0)
                self.Last_totGas_cbm = float(0.0)
                self.Last_GasForwardMonthSoFar_cbm = float(0.0)
                self.Last_GasForwardMonthSoFar_kWh = float(0.0)
                self.Last_WasserForwardMonthSoFar_Lit = int(0)
                self.Last_WasserForwardMonthSoFar_cbm = float(0.0)
                self.Last_GasForwardYearSoFar_cbm = float(0.0)
                self.Last_WasserForwardYearSoFar_Lit = int(0)

                self.Last_eBusTimeStamp = int(-127)

                self.IsNewDay2 = False
                self.IsNewMonth = False
                self.IsInitWritten2 = False

                self.IsNewDay3 = False
                self.IsNewYear = False
                self.IsInitWritten3 = False

                thread = threading.Thread(target=self.run, args=(interval, ))
                thread.daemon = True
                thread.start()

            except Exception as e:
                self.log.error("CalcWaermeMenge __init__: {}".format(e))

    # # Ende Funktion: ' Constructor ' ################################################################

    # #################################################################################################
    # # Funktion: ' Destructor '
    # #################################################################################################
        #def __del__(self):

    # # Ende Funktion: ' Destructor ' #################################################################

    # #################################################################################################
    # # Anfang Funktion: ' run '
    ## \details  Prozentuale Aufteilung des Verbrauches und des Solarertrages
    #   \param[in]  -
    #   \return Temperatur
    # #################################################################################################
        def run(self, interval):

            divide = 3

            try:
                self.log.info("Starte Berechnungen mit Intervall {} sek.".format(interval))
                ## Database initialisieren
                for i in range(10):
                    ver = self.influxHdlrDaily._init_influxdb_database(_conf.INFLUXDB_DATABASE_WAERME, 'WaermeMenge')
                    if (ver != None):
                        self.log.info('Daily influxdb Version: {}'.format(ver))
                        break

                    self.influxHdlrDaily._close_connection(_conf.INFLUXDB_DATABASE_WAERME, 'WaermeMenge')
                    time.sleep(_conf.INLFUXDB_DELAY)

                for i in range(10):
                    ver = self.influxHdlrLong._init_influxdb_database(_conf.INFLUXDB_DATABASE_WAERME_LONG, 'WaermeMengeMonth')
                    if (ver != None):
                        self.log.info('Monthly influxdb Version: {}'.format(ver))
                        break

                    self.influxHdlrLong._close_connection(_conf.INFLUXDB_DATABASE_WAERME_LONG, 'WaermeMengeMonth')
                    time.sleep(_conf.INLFUXDB_DELAY)

                # Beim Init verzögern, da kommen viele Daten vom mqtt Broker
                #time.sleep(interval)
                self.log.info('waiting')
                time.sleep(interval)
                self.log.info('running')

                while True:
                    time.sleep(interval / divide)
                    self.WaermeMenge = self.mdbHdlr.FetchWaermeEnergieData()
                    #self.log.info('WaermeMenge: {}'.format(self.WaermeMenge))
                    self._calcDailyHeatQuantitySoFar()

                    time.sleep(interval / divide)
                    self._calcMonthlyHeatQuantitySoFar()

                    time.sleep(interval / divide)
                    self._calcYearlyHeatQuantitySoFar()

            except:
                for info in sys.exc_info():
                    self.log.error("Fehler: {}".format(info))
                    print("Fehler: {}".format(info))

    # # Ende Funktion: ' run ' ########################################################################

    # #################################################################################################
    # #  Funktion: '_prepareData '
    ## 	\details    -
    #   \param[in] 	myVal
    #   \return 	myVal
    # #################################################################################################
        def _prepareData(self, influxHandler, QUERY, Instance, Unit, where, TargetVar, timestamp, callee):

            tmp = influxHandler._Query_influxDb([QUERY,], Instance, where, f'{callee}_prepareData')
            if ("Zero" in  str(tmp)):
                tmp[0] = 0.0

            elif ("NoConnecion" in str(tmp)) or ("Error" in str(tmp)):
                self.log.warning("_prepareData: Fehler beim lesen von {}".format(QUERY))
                ## Database initialisieren
                influxHandler._close_connection(influxHandler.database, 'WaermeMenge')
                time.sleep(_conf.INLFUXDB_SHORT_DELAY)
                influxHandler._init_influxdb_database(influxHandler.database, 'WaermeMenge')
                tmp[0] = 0

            resultVar, typ, length = Utils._check_Data_Type(tmp[0], Utils.toFloat)
            return(SensorData(Instance, Unit, [TargetVar,], [resultVar,], timestamp))

    # # Ende Funktion: '_prepareData ' ################################################################

    # #################################################################################################
    # #  Funktion: '_getVal '
    ## 	\details    -
    #   \param[in] 	myVal
    #   \return 	myVal
    # #################################################################################################
        def _getVal(self, influxHandler, QUERY, Instance, where, callee):

            tmp = influxHandler._Query_influxDb([QUERY,], Instance, where, f'{callee}_getVal')
            if ("Zero" in  str(tmp)):
                tmp[0] = 0.0

            elif ("NoConnecion" in str(tmp)) or ("Error" in str(tmp)):
                self.log.warning("_getVal: Fehler beim lesen von {}".format(QUERY))
                ## Database initialisieren
                influxHandler._close_connection(influxHandler.database, 'WaermeMenge')
                time.sleep(_conf.INLFUXDB_SHORT_DELAY)
                influxHandler._init_influxdb_database(influxHandler.database, 'WaermeMenge')
                tmp[0] = 0.0

            resultVar, typ, length = Utils._check_Data_Type(tmp[0], Utils.toFloat)
            return resultVar

    # # Ende Funktion: '_getVal ' #####################################################################

    # #################################################################################################
    # #  Funktion: '_getVal2 '
    ## 	\details    -
    #   \param[in] 	myVal
    #   \return 	myVal
    # #################################################################################################
        def _getVal2(self, influxHandler, strQUERY, Instance, DayTimeStamp, where, vari, callee):

            dayCnt = 0
            locDayTimeStamp = DayTimeStamp
            try:
                while (True):
                    QUERY = strQUERY.format(locDayTimeStamp)
                    tmp = influxHandler._Query_influxDb([QUERY,], Instance, where, f'{callee}_getVal2')
                    if ("Zero" in  str(tmp)):
                        #self.log.info(f'{where} {vari}: {tmp}; DayTimeStamp: {locDayTimeStamp}; QUERY: {QUERY}')

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
                        #break
                    break

                resultVar, typ, length = Utils._check_Data_Type(tmp[0], Utils.toFloat)

            except Exception as e:
                self.log.error(f"_getVal2: {e} from {callee}")

            except:
                self.log.error("_getVal2: {}".format(errLog))
                for info in sys.exc_info():
                    self.log.error("{}".format(info))

            return resultVar

    # # Ende Funktion: '_getVal2 ' ############################################################

    # #################################################################################################
    # #  Funktion: '_writeEnergyToDb '
    ## 	\details    Abhaengig von den Parametern die Summe des letzten monats oder des letzten Jahres
    #   \param[in] 	sensor_data_day_list
    #   \return 	-
    # #################################################################################################
        def _writeEnergyToDb(self, influxHandler, sensor_data_day_list, callee):

            if (time.time() - self.WriteEnergyToDbDelay < 60):
                return True

            if (influxHandler.IsConnected == False):
                for sensor_data in sensor_data_day_list:
                    self.bufferList.append(sensor_data)
                return "NoConnecion";

            if (len(self.bufferList) > 0):
                for sensor_data in self.bufferList:
                    sensor_data_day_list.append(sensor_data)
                self.bufferList.clear()

            retVal = True
            errLog = ''
            errLen = 0
            errLenStr = 0
            try:
                for sensor_data in sensor_data_day_list:
                    errLog = sensor_data
                    errLen = len(sensor_data)
                    errLenStr = len(str(sensor_data))

                    if (len(str(sensor_data)) > 0):
                        retVal = influxHandler._send_sensor_data_to_influxdb(sensor_data, 'WaermeMenge')

            except Exception as e:
                self.log.error(f"writeEnergyToDb: {e} from {callee}")

            except:
                self.log.error("{}".format(errLog))
                for info in sys.exc_info():
                    self.log.error("{}".format(info))
                    #print ("Fehler: {}".format(info))

            if (retVal != True):
                #self.log.warning(f"_writeEnergyToDb - Fehler beim schreiben von: {errLog}; Länge: {errLen}; LängeString: {errLenStr}; Aufrufer: {callee}")
                self.WriteEnergyToDbDelay = time.time()

                ## Database initialisieren
                influxHandler._close_connection(influxHandler.database, 'WaermeMenge')
                time.sleep(_conf.INLFUXDB_SHORT_DELAY)
                influxHandler._init_influxdb_database(influxHandler.database, 'WaermeMenge')

    # # Ende Funktion: '_writeEnergyToDb ' ############################################################

    # #################################################################################################
    # #  Funktion: '_getTemperature '
    ## 	\details
    #   \param[in]	-
    #   \return     -
    # #################################################################################################
        def _getTemperature(self, tSource, lastSource, strQuery, ofsVal, toFloat):

            tSource, typ, length = Utils._check_Data_Type(self.WaermeMenge[strQuery], toFloat)
            delta = abs(lastSource -  tSource)
            if (delta > ofsVal) and (lastSource > -127.0):
                tSource = lastSource

            lastSource = tSource
            return tSource, lastSource

    # # Ende Funktion: '_getTemperature ' #############################################################

    # #################################################################################################
    # #  Funktion: '_calcDailyHeatQuantitySoFar '
    ## 	\details
    #   \param[in]	-
    #   \return     -
    # #################################################################################################
        def _calcDailyHeatQuantitySoFar(self):

            try:
                sensor_data = []
                bIsNight = False

                AMh, AMm, UMh, UMm, lt_tag, lt_monat, lt_jahr, lt_h, lt_m, lt_s = SunRiseSet.get_Info([])
                sunRise = AMh  * 60 + AMm
                sunSet  = UMh  * 60 + UMm
                localNow  = lt_h * 60 + lt_m

                # Gas/Wasser Gesamtwerte
                strFolder = "{}{}".format(_conf.EXPORT_FILEPATH, lt_jahr)
                GasWasserIniFile = "{}/GasWasserTotal.log".format(strFolder)
                fileGas = "{}/GasTagesVerbrauch.txt".format(strFolder)
                fileWasser = "{}/WasserTagesVerbrauch.txt".format(strFolder)
                if (not os.path.exists(strFolder)):
                    os.mkdir(strFolder)
                    os.chmod(strFolder, 0o777)

                GasWasserTotal =  configparser.ConfigParser()
                GasWasserTotal.read(GasWasserIniFile)

                DayTimeStamp = _conf.DAYTIMESTAMP.format(lt_jahr, lt_monat, lt_tag)
                DaySoFarTimeStamp = _conf.DAYSOFARTIMESTAMP.format(lt_jahr, lt_monat, lt_tag)
                timestamp = datetime.utcnow()
                timestamp = ("'{0}-{1:02}-{2:02}T{3:02}:{4:02}:{5:02}.{6}Z'").format(timestamp.year, timestamp.month, timestamp.day, timestamp.hour, timestamp.minute, timestamp.second, timestamp.microsecond)

                #self.log.info(f'sunRise: {sunRise}; localNow: {localNow}; sunSet: {sunSet}')
                if (localNow > sunSet):     #Zeit <= Mitternacht
                    self.IsNewDay = False
                    bIsNight = True

                if (localNow < sunRise) and (bIsNight == False):    # Zeit < Sonnenaufgang und Zeit > Mitternacht -> Unmittelbar nach Mitternacht
                    try:
                        if (self.IsNewDay == False):
                            self.IsNewDay = True

                            ###########################################################
                            ## Gestrige Werte abspeichern
                            _YesterDay = datetime.utcnow()
                            if (int(lt_tag) == 1):
                                _Now = datetime.utcnow()
                                _YesterDay = _Now - datetime.timedelta(days=1)

                            YesterDayTimeStamp = _conf.DAYTIMESTAMP.format(_YesterDay.year, _YesterDay.month, _YesterDay.day)

                            tmpVal = "SELECT (WasserForwardDay_Lit) FROM heizung where instance='PUFFER' and time >= {}".format(YesterDayTimeStamp)
                            WasserForwardDay_Lit = self._getVal2(self.influxHdlrLong, tmpVal, Waerme.RegEx, YesterDayTimeStamp, 'last', 'WasserForwardDay_Lit','_calcMonthlyHeatQuantitySoFar')
                            tmpVal = "SELECT (WasserForwardDay_Lit) FROM heizung where instance='PUFFER' and time >= {}".format(YesterDayTimeStamp)
                            WasserForwardDay_cbm = self._getVal2(self.influxHdlrLong, tmpVal, Waerme.RegEx, DayTimeStamp, 'last', 'WasserForwardDay_cbm','_calcMonthlyHeatQuantitySoFar')
                            datStream = (f'TimeStamp: {_YesterDay.day:02d}.{_YesterDay.month:02d}.{_YesterDay.year:4d} {lt_h:02d}:{lt_m:02d}:{lt_s:02d} Verbrauch: {WasserForwardDay_Lit:9.0f} l; {WasserForwardDay_cbm:9.2f} cbm\n')
                            Utils._write_File(fileWasser, datStream, "a")

                            tmpVal = "SELECT (GasForwardDay_cbm) FROM heizung where instance='PUFFER' and time >= {}".format(YesterDayTimeStamp)
                            GasForwardDay_cbm = self._getVal2(self.influxHdlrLong, tmpVal, Waerme.RegEx, DayTimeStamp, 'last', 'GasForwardDaySoFar_cbm','_calcMonthlyHeatQuantitySoFar')
                            tmpVal = "SELECT (GasForwardDay_kWh) FROM heizung where instance='PUFFER' and time >= {}".format(YesterDayTimeStamp)
                            GasForwardDay_kWh = self._getVal2(self.influxHdlrLong, tmpVal, Waerme.RegEx, DayTimeStamp, 'last', 'GasForwardDay_kWh','_calcMonthlyHeatQuantitySoFar')
                            datStream = (f'TimeStamp: {_YesterDay.day:02d}.{_YesterDay.month:02d}.{_YesterDay.year:4d} {lt_h:02d}:{lt_m:02d}:{lt_s:02d} Verbrauch: {GasForwardDay_cbm:9.2f} cbm; {GasForwardDay_kWh:9.2f} kWh\n')
                            Utils._write_File(fileGas, datStream, "a")
                            ###########################################################

                            ## Gas und Wasser Verbrauch initialisieren
                            sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["GasForwardDaySoFar_Imp",], [int(0),], DaySoFarTimeStamp))
                            sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["GasForwardDaySoFar_cbm",], [float(0.0),], DaySoFarTimeStamp))
                            sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["GasForwardDaySoFar_kWh",], [float(0.0),], DaySoFarTimeStamp))

                            sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["WasserForwardDaySoFar_Imp",], [int(0),], DaySoFarTimeStamp))
                            sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["WasserForwardDaySoFar_Lit",], [int(0),], DaySoFarTimeStamp))
                            sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["WasserForwardDaySoFar_cbm",], [float(0.0),], DaySoFarTimeStamp))

                            sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["eBusTimeStamp",], ["",], timestamp))

                            self.TKollektor = 0.0
                            sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["TKollektor",], [self.TKollektor,], timestamp))
                            self.TSpeicherOben = 0.0
                            sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["TSpeicherOben",], [self.TSpeicherOben,], timestamp))
                            self.TSpeicherUnten = 0.0
                            sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["TSpeicherUnten",], [self.TSpeicherUnten,], timestamp))
                            self.TPufferOben = 0.0
                            sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["TPufferOben",], [self.TPufferOben,], timestamp))
                            self.TPufferUnten = 0.0
                            sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["TPufferUnten",], [self.TPufferUnten,], timestamp))
                            self.TFestStoffKessel = 0.0
                            sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["TFestStoffKessel",], [self.TFestStoffKessel,], timestamp))
                            self.TInternal = 0.0
                            sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["TInternal",], [self.TInternal ,], timestamp))
                            self.GasImpuls = 0
                            sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["GasImpuls",], [self.GasImpuls,], timestamp))
                            self.WasserImpuls = 0
                            sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["WasserImpuls",], [self.WasserImpuls,], timestamp))
                            ###########################################################
                            self.log.info("_calcDailyHeatQuantitySoFar-1 NEW DAY: {}".format(sensor_data))
                            ###########################################################
                            self._writeEnergyToDb(self.influxHdlrLong, sensor_data, '_calcDailyHeatQuantitySoFar-1')

                    except Exception as e:
                        self.log.error("_calcDailyHeatQuantitySoFar-1: {}".format(e))

                try:
                    ## TimeStamp von der WrSOL
                    Weekday = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
                    eBusTimeStamp, typ, length = Utils._check_Data_Type(self.WaermeMenge['timeStamp'], Utils.toInt)

                    ## 10079 = So, 23:59
                    ## 0 = Mo, 00:00
                    loweBustimeStamp = self.Last_eBusTimeStamp - 5
                    higheBustimeStamp = self.Last_eBusTimeStamp + 5

                    if (loweBustimeStamp < 0) and (self.Last_eBusTimeStamp > -127):
                        loweBustimeStamp = 10075    ## Sonntag 23:55

                    if (higheBustimeStamp > 10079):
                        loweBustimeStamp = 4    ## Montag 00:04

                    if (self.Last_eBusTimeStamp > -127) and ((higheBustimeStamp < eBusTimeStamp) or (loweBustimeStamp > eBusTimeStamp)):
                        eBusTimeStamp = self.Last_eBusTimeStamp + self.Interval_sek / 60
                    self.Last_eBusTimeStamp = eBusTimeStamp

                    weekH = int(eBusTimeStamp) / 60
                    DayOfWeek = int(weekH / 24)
                    rTime = (weekH - (DayOfWeek * 24))
                    Hour = int(rTime)
                    fMin = (rTime - Hour) * 60;
                    Min = int(fMin)
                    fSek = (fMin - Min) * 60;
                    Sec = int(fSek)
                    if(Sec >= 30):
                        Sec = 0
                        Min += 1
                    if(Min >= 60):
                        Min = Min - 60
                        Hour += 1

                    sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["eBusTimeStamp",], [f"{Weekday[DayOfWeek]}; {Hour:02}:{Min:02}",], DaySoFarTimeStamp))

                except Exception as e:
                    self.log.error("_calcDailyHeatQuantitySoFar-2: {}".format(e))

                try:
                    ## Gas Verbrauch
                    totGasImpuls = int(GasWasserTotal.get('Gas', 'Impuls'))
                    self.Last_GasImpuls = int(GasWasserTotal.get('Gas', 'LastImpuls'))
                    totGas_cbm = float(GasWasserTotal.get('Gas', 'KubikMeter'))
                    totGas_kWh = float(GasWasserTotal.get('Gas', 'kWh'))

                    self.GasImpuls, typ, length = Utils._check_Data_Type(self.WaermeMenge['Gas'], Utils.toInt)
                    if (self.GasImpuls == 0): ## Neustart Teensy
                        self.Last_GasImpuls = 0

                    totGasImpuls = abs(self.Last_GasImpuls - self.GasImpuls) + totGasImpuls
                    sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["GasForwardDaySoFar_Imp",], [self.GasImpuls,], DaySoFarTimeStamp))
                    ## in KubikMetern
                    self.Gas_cbm = abs(self.Last_GasImpuls - self.GasImpuls) * _conf.GAS_KONSTANTE
                    totGas_cbm = self.Gas_cbm + totGas_cbm
                    sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["GasForwardDaySoFar_cbm",], [float(self.Gas_cbm),], DaySoFarTimeStamp))
                    ## in kWh
                    self.Gas_kWh = self.Gas_cbm * _conf.GAS_ENERGIE
                    totGas_kWh = self.Gas_kWh + totGas_kWh
                    sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["GasForwardDaySoFar_kWh",], [float(self.Gas_kWh),], DaySoFarTimeStamp))
                    ## Historie
                    self.Last_GasImpuls = self.GasImpuls

                    GasWasserTotal.set('Gas', 'Impuls', str(totGasImpuls))
                    GasWasserTotal.set('Gas', 'LastImpuls', str( self.Last_GasImpuls))
                    GasWasserTotal.set('Gas', 'KubikMeter', (f'{totGas_cbm:9.2f}').strip())
                    GasWasserTotal.set('Gas', 'kWh', (f'{totGas_kWh:9.2f}').strip())

                    ## WasserVerbrauch
                    totWasserImpuls = int(GasWasserTotal.get('Wasser', 'Impuls'))
                    self.Last_WasserImpuls = int(GasWasserTotal.get('Wasser', 'LastImpuls'))
                    totWasser_cbm = float(GasWasserTotal.get('Wasser', 'KubikMeter'))
                    totWasser_Lit = int(GasWasserTotal.get('Wasser', 'Liter'))

                    self.WasserImpuls, typ, length = Utils._check_Data_Type(self.WaermeMenge['Wasser'], Utils.toInt)
                    if (self.WasserImpuls == 0): ## Neustart Teensy
                        self.Last_WasserImpuls = 0

                    totWasserImpuls = abs(self.Last_WasserImpuls - self.WasserImpuls) + totWasserImpuls
                    sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["WasserForwardDaySoFar_Imp",], [self.WasserImpuls,], DaySoFarTimeStamp))
                    ## in Litern
                    self.Wasser_Lit = abs(self.Last_WasserImpuls - self.WasserImpuls) * _conf.WASSER_KONSTANTE
                    totWasser_Lit = self.Wasser_Lit + totWasser_Lit
                    sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["WasserForwardDaySoFar_Lit",], [self.Wasser_Lit,], DaySoFarTimeStamp))
                    ## in KubikMetern
                    self.Wasser_cbm = self.Wasser_Lit / 1000
                    totWasser_cbm = self.Wasser_cbm + totWasser_cbm
                    sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["WasserForwardDaySoFar_cbm",], [float(self.Wasser_cbm),], DaySoFarTimeStamp))
                    ## Historie
                    self.Last_WasserImpuls = self.WasserImpuls

                    GasWasserTotal.set('Wasser', 'Impuls', str(totWasserImpuls))
                    GasWasserTotal.set('Wasser', 'LastImpuls', str(self.Last_WasserImpuls))
                    GasWasserTotal.set('Wasser', 'KubikMeter', (f'{totWasser_cbm:9.2f}').strip())
                    GasWasserTotal.set('Wasser', 'Liter', str(totWasser_Lit))

                    ## Verbrauchswerte speichern
                    with open(GasWasserIniFile, 'w') as configfile:    # save
                        GasWasserTotal.write(configfile)

                    #TimeStamp: 13.02.2023 16:10:46    Wasser:    26525 l
                    logTimestamp = datetime.utcnow()
                    logTimestamp = f"{logTimestamp.day:02}.{logTimestamp.month:02}.{logTimestamp.year:04} {logTimestamp.hour:02}:{logTimestamp.minute:02}:{logTimestamp.second:02}"
                    datStream = f"TimeStamp: {logTimestamp}    Wasser: {totWasser_Lit:9.0f} l\n"
                    fileName = "{}/WasserVerbrauch.log".format(strFolder)
                    if (self.Last_totWasser_Lit < totWasser_Lit):
                        Utils._write_File(fileName, datStream, "a")
                    self.Last_totWasser_Lit = totWasser_Lit

                    #TimeStamp: 13.02.2023 16:10:46    Gas: 26525.23 cbm
                    datStream = f"TimeStamp: {logTimestamp}    Gas: {totGas_cbm:9.2f} cbm\n"
                    fileName = "{}/GasVerbrauch.log".format(strFolder)
                    if (self.Last_totGas_cbm < totGas_cbm):
                        Utils._write_File(fileName, datStream, "a")
                    self.Last_totGas_cbm = totGas_cbm

                except Exception as e:
                    self.log.error("_calcDailyHeatQuantitySoFar-3: {}".format(e))

                ## Temperaturen
                ## Kollektor
                #self.log.info("Ofset TKO: {}".format(GasWasserTotal.get('Offset', 'TKO')))
                self.TKollektor, self.Last_TKollektor = self._getTemperature(self.TKollektor, self.Last_TKollektor, 'TKO', int(GasWasserTotal.get('Offset', 'TKO')), Utils.toFloat)
                sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["TKollektor",], [self.TKollektor,], timestamp))
                ## Speicher Oben
                self.TSpeicherOben, self.Last_TSpeicherOben = self._getTemperature(self.TSpeicherOben, self.Last_TSpeicherOben, 'TSO', int(GasWasserTotal.get('Offset', 'TSO')), Utils.toFloat)
                sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["TSpeicherOben",], [self.TSpeicherOben,], timestamp))
                ## Speicher Unten
                self.TSpeicherUnten, self.Last_TSpeicherUnten = self._getTemperature(self.TSpeicherUnten, self.Last_TSpeicherUnten, 'TSU', int(GasWasserTotal.get('Offset', 'TSU')), Utils.toFloat)
                sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["TSpeicherUnten",], [self.TSpeicherUnten,], timestamp))
                ## Puffer Oben
                self.TPufferOben, self.Last_TPufferOben = self._getTemperature(self.TPufferOben, self.Last_TPufferOben, 'TPO', int(GasWasserTotal.get('Offset', 'TPO')), Utils.toFloat)
                # Korrektur
                self.TPufferOben = self.TPufferOben * float(GasWasserTotal.get('Korrektur', 'TPO'))
                sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["TPufferOben",], [self.TPufferOben,], timestamp))
                ## Puffer Unten
                self.TPufferUnten, self.Last_TPufferUnten = self._getTemperature(self.TPufferUnten, self.Last_TPufferUnten, 'TPU', int(GasWasserTotal.get('Offset', 'TPU')), Utils.toFloat)
                sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["TPufferUnten",], [self.TPufferUnten,], timestamp))
                ## FestStoffOgen
                self.TFestStoffKessel, self.Last_TFestStoffKessel = self._getTemperature(self.TFestStoffKessel, self.Last_TFestStoffKessel, 'TFK', int(GasWasserTotal.get('Offset', 'TFK')), Utils.toFloat)
                sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["TFestStoffKessel",], [self.TFestStoffKessel,], timestamp))
                ## KaltWasser
                self.TWasser, self.Last_TWasser = self._getTemperature(self.TWasser, self.Last_TWasser, 'TWasser', int(GasWasserTotal.get('Offset', 'TWasser')), Utils.toInt)
                sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["TWasser",], [self.TWasser,], timestamp))
                ## Teensy
                self.TInternal, self.Last_TInternal = self._getTemperature(self.TInternal, self.Last_TInternal, 'TInternal', int(GasWasserTotal.get('Offset', 'TInternal')), Utils.toInt)
                sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["TInternal",], [self.TInternal,], timestamp))
                ###########################################################
                #self.log.info(f'TKO: {self.TKollektor:5.2f} TSO: {self.TSpeicherOben:5.2f} TSU: {self.TSpeicherUnten:5.2f} TPO: {self.TPufferOben:5.2f} TPU: {self.TPufferUnten:5.2f} TFK: {self.TFestStoffKessel:5.2f} Teensy: {self.TInternal:5.2f}')
                #self.log.info(f'eBusTime: {Weekday[DayOfWeek]}; {Hour:02}:{Min:02}\t{eBusTimeStamp} Gas: {self.GasImpuls:5.2f} Wasser: {self.WasserImpuls:5.2f}')
                ###########################################################
                #self.log.info("_calcDailyHeatQuantitySoFar-4: {}".format(sensor_data))
                ###########################################################

                self._writeEnergyToDb(self.influxHdlrDaily, sensor_data, '_calcDailyHeatQuantitySoFar-4')

            except Exception as e:
                self.log.error("_calcDailyHeatQuantitySoFar-4: {}".format(e))

            except:
                self.log.error("_calcDailyHeatQuantitySoFar-5: {}".format(errLog))
                for info in sys.exc_info():
                    self.log.error("{}".format(info))

    # # Ende Funktion: ' _calcDailyHeatQuantitySoFar ' #####################################################

    # #################################################################################################
    # #  Funktion: '_calcMonthlyHeatQuantitySoFar '
    ## 	\details  am 1. des Monats mit 0 beginnen abspeichern in der AcEnergyForwardMonth, den täglichen zuwachs in der AcEnergyForwardMonthSoFar.
    ##   Um Mitternacht umspeichern dieses Wertes.
    #   \param[in]	-
    #   \return     -
    # #################################################################################################
        def _calcMonthlyHeatQuantitySoFar(self):

            try:
                sensor_data = []
                if (datetime.day == 1) and (self.IsInitWritten2 == False):
                    self.IsNewMonth = True
                    ###########################################################
                    self.log.info("_calcMonthlyHeatQuantitySoFar First Day of MONTH")
                    ###########################################################

                if (datetime.day == 2):
                    self.IsInitWritten2 = False
                    ###########################################################
                    self.log.info("_calcMonthlyHeatQuantitySoFar Second Day of MONTH")
                    ###########################################################

                bIsNight = False

                AMh, AMm, UMh, UMm, lt_tag, lt_monat, lt_jahr, lt_h, lt_m, lt_s = SunRiseSet.get_Info([])
                sunRise = AMh  * 60 + AMm
                sunSet  = UMh  * 60 + UMm
                localNow  = lt_h * 60 + lt_m

                strFolder = "{}{}".format(_conf.EXPORT_FILEPATH, lt_jahr)
                fileGas = "{}/GasMonatsVerbrauch.txt".format(strFolder)
                fileWasser = "{}/WasserMonatsVerbrauch.txt".format(strFolder)

                DayTimeStamp = _conf.DAYTIMESTAMP.format(lt_jahr, lt_monat, lt_tag)
                MonthTimeStamp = _conf.MONTHTIMESTAMP.format(lt_jahr, lt_monat)
                MonthSoFarTimeStamp = _conf.MONTHSOFARTIMESTAMP.format(lt_jahr, lt_monat)

                if (localNow > sunSet):     #Zeit <= Mitternacht
                    self.IsNewDay2 = False
                    bIsNight = True

                if (localNow < sunRise) and (bIsNight == False):    # Zeit < Sonnenaufgang und Zeit > Mitternacht -> Unmittelbar nach Mitternacht
                    try:
                        if (self.IsNewMonth == True):
                            self.IsNewMonth = False
                            self.IsInitWritten2 = True

                            ###########################################################
                            ## Werte vom letzten Monat abspeichern
                            _YesterDay = datetime.utcnow()
                            if (int(lt_tag) == 1) and (int(lt_monat) == 1):
                                _Now = datetime.utcnow()
                                _YesterDay = _Now - datetime.timedelta(days=1)

                            LastMonthTimeStamp = _conf.MONTHTIMESTAMP.format(_YesterDay.year, _YesterDay.month)

                            tmpVal = "SELECT (GasForwardMonth_cbm) FROM heizung where instance='PUFFER' and time >= {}".format(LastMonthTimeStamp)
                            GasForwardMonth_cbm = self._getVal2(self.influxHdlrLong, tmpVal, Waerme.RegEx, YesterDayTimeStamp, 'last', 'GasForwardMonth_cbm','_calcMonthlyHeatQuantitySoFar')
                            tmpVal = "SELECT (GasForwardMonth_kWh) FROM heizung where instance='PUFFER' and time >= {}".format(LastMonthTimeStamp)
                            GasForwardMonth_kWh = self._getVal2(self.influxHdlrLong, tmpVal, Waerme.RegEx, DayTimeStamp, 'last', 'GasForwardMonth_kWh','_calcMonthlyHeatQuantitySoFar')
                            datStream = (f'{_YesterDay.year:02d}.{_YesterDay.month:02d}.{_YesterDay.year:4d}; {GasForwardMonth_cbm:9.2f} cbm; {GasForwardMonth_kWh:9.2f} kWh\n')
                            Utils._write_File(fileGas, datStream, "a")

                            tmpVal = "SELECT (WasserForwardMonth_cbm) FROM heizung where instance='PUFFER' and time >= {}".format(LastMonthTimeStamp)
                            WasserForwardMonth_cbm = self._getVal2(self.influxHdlrLong, tmpVal, Waerme.RegEx, YesterDayTimeStamp, 'last', 'WasserForwardMonth_cbm','_calcMonthlyHeatQuantitySoFar')
                            tmpVal = "SELECT (WasserForwardMonth_Lit) FROM heizung where instance='PUFFER' and time >= {}".format(LastMonthTimeStamp)
                            WasserForwardMonth_Lit = self._getVal2(self.influxHdlrLong, tmpVal, Waerme.RegEx, DayTimeStamp, 'last', 'WasserForwardMonth_Lit','_calcMonthlyHeatQuantitySoFar')
                            datStream = (f'{_YesterDay.year:02d}.{_YesterDay.month:02d}.{_YesterDay.year:4d}; {WasserForwardMonth_Lit:9.0f} l; {WasserForwardMonth_cbm:9.2f} cbm\n')
                            Utils._write_File(fileWasser, datStream, "a")
                            ###########################################################

                            sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["GasForwardMonth_cbm",], [int(0),], MonthTimeStamp))
                            sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["GasForwardMonth_kWh",], [int(0),], MonthTimeStamp))
                            sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["GasForwardMonthSoFar_cbm",], [int(0),], MonthTimeStamp))
                            sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["GasForwardMonthSoFar_kWh",], [int(0),], MonthTimeStamp))
                            sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["WasserForwardMonth_Lit",], [int(0),], MonthTimeStamp))
                            sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["WasserForwardMonth_cbm",], [int(0),], MonthTimeStamp))
                            sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["WasserForwardMonthSoFar_Lit",], [int(0),], MonthTimeStamp))
                            sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["WasserForwardMonthSoFar_cbm",], [int(0),], MonthTimeStamp))
                            ###########################################################
                            self.log.info("_calcMonthlyHeatQuantitySoFar-1 NEW MONTH: {}".format(sensor_data))
                            ###########################################################
                            self._writeEnergyToDb(self.influxHdlrLong, sensor_data, '_calcMonthlyHeatQuantitySoFar-1')

                        if (self.IsNewDay2 == True) and (self.IsNewMonth == False):
                            self.IsNewDay2 = False

                            GAS = "SELECT (GasForwardMonthSoFar_cbm) FROM heizung where instance='PUFFER' and time >= {}".format(MonthSoFarTimeStamp)
                            sensor_data.append(self._prepareData(self.influxHdlrLong, GAS, Waerme.RegEx, Waerme.Label1, 'GasForwardMonthSoFar_cbm', 'GasForwardMonth_cbm', MonthTimeStamp, '_calcMonthlyHeatQuantitySoFar'))
                            GAS = "SELECT (GasForwardMonthSoFar_kWh) FROM heizung where instance='PUFFER' and time >= {}".format(MonthSoFarTimeStamp)
                            sensor_data.append(self._prepareData(self.influxHdlrLong, GAS, Waerme.RegEx, Waerme.Label1, 'GasForwardMonthSoFar_kWh', 'GasForwardMonth_kWh', MonthTimeStamp, '_calcMonthlyHeatQuantitySoFar'))

                            WASSER = "SELECT (WasserForwardMonthSoFar_Lit) FROM heizung where instance='PUFFER' and time >= {}".format(MonthSoFarTimeStamp)
                            sensor_data.append(self._prepareData(self.influxHdlrLong, WASSER, Waerme.RegEx, Waerme.Label1, 'WasserForwardMonthSoFar_Lit', 'WasserForwardMonth_Lit', MonthTimeStamp, '_calcMonthlyHeatQuantitySoFar'))
                            WASSER = "SELECT (WasserForwardMonthSoFar_cbm) FROM heizung where instance='PUFFER' and time >= {}".format(MonthSoFarTimeStamp)
                            sensor_data.append(self._prepareData(self.influxHdlrLong, WASSER, Waerme.RegEx, Waerme.Label1, 'WasserForwardMonthSoFar_cbm', 'WasserForwardMonth_cbm', MonthTimeStamp, '_calcMonthlyHeatQuantitySoFar'))
                            ###########################################################
                            self.log.info("_calcMonthlyHeatQuantitySoFar-1 NEW DAY: {}".format(sensor_data))
                            ###########################################################
                            self._writeEnergyToDb(self.influxHdlrLong, sensor_data, '_calcMonthlyHeatQuantitySoFar-1')

                    except Exception as e:
                        self.log.error("_calcMonthlyHeatQuantitySoFar-1: {}".format(e))

                tmpVal = "SELECT (GasForwardMonth_cbm) FROM heizung where instance='PUFFER' and time >= {}".format(MonthTimeStamp)
                GasForwardMonth_cbm = self._getVal(self.influxHdlrLong, tmpVal, Waerme.RegEx, 'GasForwardMonth_cbm', '_calcMonthlyHeatQuantitySoFar')
                tmpVal = "SELECT (GasForwardDay_cbm) FROM heizung where instance='PUFFER' and time >= {}".format(DayTimeStamp)
                GasForwardDay_cbm = self._getVal2(self.influxHdlrLong, tmpVal, Waerme.RegEx, DayTimeStamp, 'last', 'GasForwardDaySoFar_cbm','_calcMonthlyHeatQuantitySoFar')

                GasForwardMonthSoFar_cbm = GasForwardMonth_cbm + GasForwardDay_cbm
                sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["GasForwardMonthSoFar_cbm",], [GasForwardMonthSoFar_cbm,], MonthSoFarTimeStamp))

                tmpVal = "SELECT (GasForwardMonth_kWh) FROM heizung where instance='PUFFER' and time >= {}".format(MonthTimeStamp)
                GasForwardMonth_kWh = self._getVal(self.influxHdlrLong, tmpVal, Waerme.RegEx, 'GasForwardMonth_kWh', '_calcMonthlyHeatQuantitySoFar')
                tmpVal = "SELECT (GasForwardDay_kWh) FROM heizung where instance='PUFFER' and time >= {}".format(DayTimeStamp)
                GasForwardDay_kWh = self._getVal2(self.influxHdlrLong, tmpVal, Waerme.RegEx, DayTimeStamp, 'last', 'GasForwardDay_kWh','_calcMonthlyHeatQuantitySoFar')

                GasForwardMonthSoFar_kWh = GasForwardMonth_kWh + GasForwardDay_kWh
                sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["GasForwardMonthSoFar_cbm",], [GasForwardMonthSoFar_kWh,], MonthSoFarTimeStamp))
                ###########################################################
                #self.log.info("GasForwardMonth : {}".format(GasForwardMonth))
                #self.log.info("self.WaermeMenge['40670'] : {}".format(self.WaermeMenge['40670']))
                #self.log.info("GasForwardMonthSoFar : {}".format(GasForwardMonthSoFar))
                ###########################################################
                datStream = (f'TimeStamp: {lt_tag:02d}.{lt_monat:02d}.{lt_jahr:4d} {lt_h:02d}:{lt_m:02d}:{lt_s:02d} Verbrauch: {GasForwardMonthSoFar_cbm:9.2f} cbm; {GasForwardMonthSoFar_kWh:9.2f} kWh\n')
                if (self.Last_GasForwardMonthSoFar_cbm < GasForwardMonthSoFar_cbm):
                    Utils._write_File(fileGas, datStream, "a")
                self.Last_GasForwardMonthSoFar_cbm = GasForwardMonthSoFar_cbm

                tmpVal = "SELECT (WasserForwardMonth_Lit) FROM heizung where instance='PUFFER' and time >= {}".format(MonthTimeStamp)
                WasserForwardMonth_Lit = self._getVal(self.influxHdlrLong, tmpVal, Waerme.RegEx, 'WasserForwardMonth_Lit', '_calcMonthlyHeatQuantitySoFar')
                tmpVal = "SELECT (WasserForwardDay_Lit) FROM heizung where instance='PUFFER' and time >= {}".format(DayTimeStamp)
                WasserForwardDay_Lit = self._getVal2(self.influxHdlrLong, tmpVal, Waerme.RegEx, DayTimeStamp, 'last', 'WasserForwardDay_Lit','_calcMonthlyHeatQuantitySoFar')

                WasserForwardMonthSoFar_Lit = WasserForwardMonth_Lit + WasserForwardDay_Lit
                sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["WasserForwardMonthSoFar_Lit",], [WasserForwardMonthSoFar_Lit,], MonthSoFarTimeStamp))

                tmpVal = "SELECT (WasserForwardMonth_cbm) FROM heizung where instance='PUFFER' and time >= {}".format(MonthTimeStamp)
                WasserForwardMonth_cbm = self._getVal(self.influxHdlrLong, tmpVal, Waerme.RegEx, 'WasserForwardMonth_cbm', '_calcMonthlyHeatQuantitySoFar')
                tmpVal = "SELECT (WasserForwardDay_Lit) FROM heizung where instance='PUFFER' and time >= {}".format(DayTimeStamp)
                WasserForwardDay_cbm = self._getVal2(self.influxHdlrLong, tmpVal, Waerme.RegEx, DayTimeStamp, 'last', 'WasserForwardDay_cbm','_calcMonthlyHeatQuantitySoFar')

                WasserForwardMonthSoFar_cbm = WasserForwardMonth_cbm + WasserForwardDay_cbm
                sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["WasserForwardMonthSoFar_cbm",], [WasserForwardMonthSoFar_cbm,], MonthSoFarTimeStamp))
                ###########################################################
                #self.log.info("WasserForwardMonth : {}".format(WasserForwardMonth))
                #self.log.info("self.WaermeMenge['30535'] : {}".format(self.WaermeMenge['30535']))
                #self.log.info("WasserForwardMonthSoFar : {}".format(WasserForwardMonthSoFar))
                ###########################################################
                datStream = (f'TimeStamp: {lt_tag:02d}.{lt_monat:02d}.{lt_jahr:4d} {lt_h:02d}:{lt_m:02d}:{lt_s:02d} Verbrauch: {WasserForwardMonthSoFar_Lit:9.0f} l; {WasserForwardMonthSoFar_cbm:9.2f} cbm\n')
                if (self.Last_WasserForwardMonthSoFar_Lit < WasserForwardMonthSoFar_Lit):
                    Utils._write_File(fileWasser, datStream, "a")
                self.Last_WasserForwardMonthSoFar_Lit = WasserForwardMonthSoFar_Lit

                ###########################################################
                #self.log.info("_calcMonthlyHeatQuantitySoFar-2: {}".format(sensor_data))
                ###########################################################
                self._writeEnergyToDb(self.influxHdlrLong, sensor_data, '_calcMonthlyHeatQuantitySoFar-2')

            except Exception as e:
                self.log.error("_calcMonthlyHeatQuantitySoFar-2: {}".format(e))

            except:
                self.log.error("_calcMonthlyHeatQuantitySoFar-3: {}".format(errLog))
                for info in sys.exc_info():
                    self.log.error("{}".format(info))

    # # Ende Funktion: ' _calcMonthlyHeatQuantitySoFar ' #####################################################

    # #################################################################################################
    # #  Funktion: '_calcYearlyHeatQuantitySoFar '
    ## 	\details  am 1. des Monats mit 0 beginnen abspeichern in der AcEnergyForwardMonth, den täglichen zuwachs in der AcEnergyForwardMonthSoFar.
    ## Um Mitternacht, bzw. wenn die Wechselrichter aus sind umspeichern dieses Wertes.
    #   \param[in]	-
    #   \return     -
    # #################################################################################################
        def _calcYearlyHeatQuantitySoFar(self):

            try:
                sensor_data = []
                if (datetime.day == 1) and (datetime.month == 1) and (self.IsInitWritten3 == False):
                    self.IsNewYear = True
                    ###########################################################
                    self.log.info("_calcYearlyHeatQuantitySoFar First Day of YEAR")
                    ###########################################################

                if (datetime.day == 2) and (datetime.month == 1):
                    self.IsInitWritten3 = False
                    ###########################################################
                    self.log.info("_calcYearlyHeatQuantitySoFar Second Day of YEAR")
                    ###########################################################

                bIsNight = False

                AMh, AMm, UMh, UMm, lt_tag, lt_monat, lt_jahr, lt_h, lt_m, lt_s = SunRiseSet.get_Info([])
                sunRise = AMh  * 60 + AMm
                sunSet  = UMh  * 60 + UMm
                localNow  = lt_h * 60 + lt_m

                strFolder = "{}{}".format(_conf.EXPORT_FILEPATH, lt_jahr)
                fileGas = "{}/GasJahresVerbrauch.txt".format(strFolder)
                fileWasser = "{}/WasserJahresVerbrauch.txt".format(strFolder)

                DayTimeStamp = _conf.DAYTIMESTAMP.format(lt_jahr, lt_monat, lt_tag)
                YearTimeStamp = _conf.YEARTIMESTAMP.format(lt_jahr)
                YearSoFarTimeStamp = _conf.YEARSOFARTIMESTAMP.format(lt_jahr)

                if (localNow > sunSet):     #Zeit <= Mitternacht
                    self.IsNewDay3 = True
                    bIsNight = True

                if (localNow < sunRise) and (bIsNight == False):    # Zeit < Sonnenaufgang und Zeit > Mitternacht -> Unmittelbar nach Mitternacht
                    try:
                        if (self.IsNewYear == True):
                            self.IsNewYear = False
                            self.IsInitWritten3 = True

                            ###########################################################
                            ## Werte vom letzten Jahr abspeichern
                            _YesterDay = datetime.utcnow()
                            if (int(lt_tag) == 1) and (int(lt_monat) == 1):
                                _Now = datetime.utcnow()
                                _YesterDay = _Now - datetime.timedelta(days=1)

                            LastYearTimeStamp = _conf.YEARTIMESTAMP.format(_YesterDay.year)

                            ## Die GetWasserTotal.log ins neue Jahr kopieren
                            strFolder = "{}{}".format(_conf.EXPORT_FILEPATH, _YesterDay.year)
                            LastYearIniFile = "{}/GasWasserTotal.log".format(strFolder)
                            strFolder = "{}{}".format(_conf.EXPORT_FILEPATH, lt_jahr)
                            GasWasserIniFile = "{}/GasWasserTotal.log".format(strFolder)
                            shutil.copyfile(LastYearIniFile, GasWasserIniFile)

                            tmpVal = "SELECT (GasForwardYear_cbm) FROM heizung where instance='PUFFER' and time >= {}".format(LastYearTimeStamp)
                            GasForwardYear_cbm = self._getVal2(self.influxHdlrLong, tmpVal, Waerme.RegEx, YesterDayTimeStamp, 'last', 'GasForwardYear_cbm','_calcMonthlyHeatQuantitySoFar')
                            tmpVal = "SELECT (GasForwardYear_kWh) FROM heizung where instance='PUFFER' and time >= {}".format(LastYearTimeStamp)
                            GasForwardYear_kWh = self._getVal2(self.influxHdlrLong, tmpVal, Waerme.RegEx, DayTimeStamp, 'last', 'GasForwardYear_kWh','_calcMonthlyHeatQuantitySoFar')
                            datStream = (f'{_YesterDay.year:02d}.{_YesterDay.month:02d}.{_YesterDay.year:4d}; {GasForwardYear_cbm:9.2f} cbm; {GasForwardYear_kWh:9.2f} kWh\n')
                            Utils._write_File(fileGas, datStream, "a")

                            tmpVal = "SELECT (WasserForwardYear_Lit) FROM heizung where instance='PUFFER' and time >= {}".format(LastYearTimeStamp)
                            WasserForwardYear_Lit = self._getVal2(self.influxHdlrLong, tmpVal, Waerme.RegEx, YesterDayTimeStamp, 'last', 'WasserForwardYear_Lit','_calcMonthlyHeatQuantitySoFar')
                            tmpVal = "SELECT (WasserForwardYear_cbm) FROM heizung where instance='PUFFER' and time >= {}".format(LastYearTimeStamp)
                            WasserForwardYear_cbm = self._getVal2(self.influxHdlrLong, tmpVal, Waerme.RegEx, DayTimeStamp, 'last', 'WasserForwardYear_cbm','_calcMonthlyHeatQuantitySoFar')
                            datStream = (f'{_YesterDay.year:02d}.{_YesterDay.month:02d}.{_YesterDay.year:4d}; {WasserForwardYear_Lit:9.0f} l; {WasserForwardYear_cbm:9.2f} cbm\n')
                            Utils._write_File(fileWasser, datStream, "a")
                            ###########################################################

                            sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["GasForwardYear_cbm",], [int(0),], YearTimeStamp))
                            sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["GasForwardYear_kWh",], [int(0),], YearTimeStamp))
                            sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["GasForwardYearSoFar_cbm",], [int(0),], YearTimeStamp))
                            sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["GasForwardYearSoFar_kWh",], [int(0),], YearTimeStamp))
                            sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["WasserForwardYear_Lit",], [int(0),], YearTimeStamp))
                            sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["WasserForwardYear_cbm",], [int(0),], YearTimeStamp))
                            sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["WasserForwardYearSoFar_Lit",], [int(0),], YearTimeStamp))
                            sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["WasserForwardYearSoFar_cbm",], [int(0),], YearTimeStamp))
                            ###########################################################
                            self.log.info("_calcYearlyHeatQuantitySoFar-1 NEW YEAR: {}".format(sensor_data))
                            ###########################################################
                            self._writeEnergyToDb(self.influxHdlrLong, sensor_data, '_calcYearlyHeatQuantitySoFar-1')

                        if (self.IsNewDay3 == True) and (self.IsNewYear == False):
                            self.IsNewDay3 = False

                            GAS = "SELECT (GasForwardYearSoFar_cbm) FROM heizung where instance='PUFFER' and time >= {}".format(YearSoFarTimeStamp)
                            sensor_data.append(self._prepareData(self.influxHdlrLong, GAS, Waerme.RegEx, Waerme.Label1, 'GasForwardYearSoFar_cbm', 'GasForwardYear_cbm', YearTimeStamp, '_calcYearlyHeatQuantitySoFar'))
                            GAS = "SELECT (GasForwardYearSoFar_kWh) FROM heizung where instance='PUFFER' and time >= {}".format(YearSoFarTimeStamp)
                            sensor_data.append(self._prepareData(self.influxHdlrLong, GAS, Waerme.RegEx, Waerme.Label1, 'GasForwardYearSoFar_kWh', 'GasForwardYear_kWh', YearTimeStamp, '_calcYearlyHeatQuantitySoFar'))

                            WASSER = "SELECT (WasserForwardYearSoFar_Lit) FROM heizung where instance='PUFFER' and time >= {}".format(YearSoFarTimeStamp)
                            sensor_data.append(self._prepareData(self.influxHdlrLong, WASSER, Waerme.RegEx, Waerme.Label1, 'WasserForwardYearSoFar_Lit', 'WasserForwardYear_Lit', YearTimeStamp, '_calcYearlyHeatQuantitySoFar'))
                            WASSER = "SELECT (WasserForwardYearSoFar_cbm) FROM heizung where instance='PUFFER' and time >= {}".format(YearSoFarTimeStamp)
                            sensor_data.append(self._prepareData(self.influxHdlrLong, WASSER, Waerme.RegEx, Waerme.Label1, 'WasserForwardYearSoFar_cbm', 'WasserForwardYear_cbm', YearTimeStamp, '_calcYearlyHeatQuantitySoFar'))
                            ###########################################################
                            self.log.info("_calcYearlyHeatQuantitySoFar-1 NEW DAY: {}".format(sensor_data))
                            ###########################################################
                            self._writeEnergyToDb(self.influxHdlrLong, sensor_data, '_calcYearlyHeatQuantitySoFar-1')

                    except Exception as e:
                        self.log.error("_calcYearlyHeatQuantitySoFar-1: {}".format(e))

                tmpVal = "SELECT (GasForwardYear_cbm) FROM heizung where instance='PUFFER' and time >= {}".format(YearTimeStamp)
                GasForwardYear_cbm = self._getVal(self.influxHdlrLong, tmpVal, Waerme.RegEx, 'GasForwardYear_cbm', '_calcYearlyHeatQuantitySoFar')
                tmpVal = "SELECT (GasForwardDay_cbm) FROM heizung where instance='PUFFER' and time >= {}".format(DayTimeStamp)
                GasForwardDay_cbm = self._getVal2(self.influxHdlrLong, tmpVal, Waerme.RegEx, DayTimeStamp, 'last', 'GasForwardDaySoFar_cbm','_calcYearlyHeatQuantitySoFar')

                GasForwardYearSoFar_cbm = GasForwardYear_cbm + GasForwardDay_cbm
                sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["GasForwardYearSoFar_cbm",], [GasForwardYearSoFar_cbm,], YearSoFarTimeStamp))

                tmpVal = "SELECT (GasForwardYear_kWh) FROM heizung where instance='PUFFER' and time >= {}".format(YearTimeStamp)
                GasForwardYear_kWh = self._getVal(self.influxHdlrLong, tmpVal, Waerme.RegEx, 'GasForwardYear_kWh', '_calcYearlyHeatQuantitySoFar')
                tmpVal = "SELECT (GasForwardDay_kWh) FROM heizung where instance='PUFFER' and time >= {}".format(DayTimeStamp)
                GasForwardDay_kWh = self._getVal2(self.influxHdlrLong, tmpVal, Waerme.RegEx, DayTimeStamp, 'last', 'GasForwardDay_kWh','_calcYearlyHeatQuantitySoFar')

                GasForwardYearSoFar_kWh = GasForwardYear_kWh + GasForwardDay_kWh
                sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["GasForwardYearSoFar_cbm",], [GasForwardYearSoFar_kWh,], YearSoFarTimeStamp))
                ###########################################################
                #self.log.info("GasForwardYear : {}".format(GasForwardYear))
                #self.log.info("self.WaermeMenge['40670'] : {}".format(self.WaermeMenge['40670']))
                #self.log.info("GasForwardYearSoFar : {}".format(GasForwardYearSoFar))
                ###########################################################
                datStream = (f'TimeStamp: {lt_tag:02d}.{lt_monat:02d}.{lt_jahr:4d} {lt_h:02d}:{lt_m:02d}:{lt_s:02d} Verbrauch: {GasForwardYearSoFar_cbm:9.2f} cbm; {GasForwardYearSoFar_kWh:9.2f} kWh\n')
                if (self.Last_GasForwardYearSoFar_cbm < GasForwardYearSoFar_cbm):
                    Utils._write_File(fileGas, datStream, "a")
                self.Last_GasForwardYearSoFar_cbm = GasForwardYearSoFar_cbm

                tmpVal = "SELECT (WasserForwardYear_Lit) FROM heizung where instance='PUFFER' and time >= {}".format(YearTimeStamp)
                WasserForwardYear_Lit = self._getVal(self.influxHdlrLong, tmpVal, Waerme.RegEx, 'WasserForwardYear_Lit', '_calcYearlyHeatQuantitySoFar')
                tmpVal = "SELECT (WasserForwardDay_Lit) FROM heizung where instance='PUFFER' and time >= {}".format(DayTimeStamp)
                WasserForwardDay_Lit = self._getVal2(self.influxHdlrLong, tmpVal, Waerme.RegEx, DayTimeStamp, 'last', 'WasserForwardDay_Lit','_calcYearlyHeatQuantitySoFar')

                WasserForwardYearSoFar_Lit = WasserForwardYear_Lit + WasserForwardDay_Lit
                sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["WasserForwardYearSoFar_Lit",], [WasserForwardYearSoFar_Lit,], YearSoFarTimeStamp))

                tmpVal = "SELECT (WasserForwardYear_cbm) FROM heizung where instance='PUFFER' and time >= {}".format(YearTimeStamp)
                WasserForwardYear_cbm = self._getVal(self.influxHdlrLong, tmpVal, Waerme.RegEx, 'WasserForwardYear_cbm', '_calcYearlyHeatQuantitySoFar')
                tmpVal = "SELECT (WasserForwardDay_cbm) FROM heizung where instance='PUFFER' and time >= {}".format(DayTimeStamp)
                WasserForwardDay_cbm = self._getVal2(self.influxHdlrLong, tmpVal, Waerme.RegEx, DayTimeStamp, 'last', 'WasserForwardDay_cbm','_calcYearlyHeatQuantitySoFar')

                WasserForwardYearSoFar_cbm = WasserForwardYear_cbm + WasserForwardDay_cbm
                sensor_data.append(SensorData(Waerme.RegEx, Waerme.Label1, ["WasserForwardYearSoFar_cbm",], [WasserForwardYearSoFar_cbm,], YearSoFarTimeStamp))
                ###########################################################
                #self.log.info("WasserForwardYear : {}".format(WasserForwardYear))
                #self.log.info("self.WaermeMenge['30535'] : {}".format(self.WaermeMenge['30535']))
                #self.log.info("WasserForwardYearSoFar : {}".format(WasserForwardYearSoFar))
                ###########################################################
                datStream = (f'TimeStamp: {lt_tag:02d}.{lt_monat:02d}.{lt_jahr:4d} {lt_h:02d}:{lt_m:02d}:{lt_s:02d} Verbrauch: {WasserForwardYearSoFar_Lit:9.0f} l; {WasserForwardYearSoFar_cbm:9.2f} cbm\n')
                if (self.Last_WasserForwardYearSoFar_Lit < WasserForwardYearSoFar_Lit):
                    Utils._write_File(fileWasser, datStream, "a")
                self.Last_WasserForwardYearSoFar_Lit = WasserForwardYearSoFar_Lit

                ###########################################################
                #self.log.info("_calcYearlyHeatQuantitySoFar-2: {}".format(sensor_data))
                ###########################################################
                self._writeEnergyToDb(self.influxHdlrLong, sensor_data, '_calcYearlyHeatQuantitySoFar-2')

            except Exception as e:
                self.log.error("_calcYearlyHeatQuantitySoFar-2: {}".format(e))

            except:
                self.log.error("_calcYearlyHeatQuantitySoFar-3: {}".format(errLog))
                for info in sys.exc_info():
                    self.log.error("{}".format(info))

    # # Ende Funktion: ' _calcYearlyHeatQuantitySoFar ' #####################################################

##### Fehlerbehandlung #####################################################
    except IOError as e:
        print('Eine der Bibliotheken konnte nicht geladen werden!\n{}!\n'.format(e))

    except:
        for info in sys.exc_info():
            print ("Fehler: {}".format(info))

# # Ende Klasse: ' CalcPer_CallBack ' ####################################################################


# #################################################################################################
# #  Funktion: ' _main '
## \details         Die Einsprungsfunktion, ruft alle Funktionen und Klassen auf.
#   \param[in]    argv
#   \return            -
# #################################################################################################
def _main(argv):

    CalcWaermeMenge(60, logging)
    while(True):
        time.sleep(10000)

# #################################################################################################
# #  Funktion: 'Einsprung beim Aufruf  '
# #################################################################################################
if __name__ == '__main__':

    _main(sys.argv)

# # DateiEnde #####################################################################################

# # DateiEnde #####################################################################################
