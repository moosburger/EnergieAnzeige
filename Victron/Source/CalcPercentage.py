#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# #################################################################################################
## \brief     Berechnet die prozentuale Verteilung
#  \details
#  \file      CalcPercentage.py
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
bDebug = False
bDebugOnLinux = False

# Damit kann aus einem andern Pfad importiert werden. Diejenigen die lokal verwendet werden, vor der Pfaderweiterung importieren
if(bDebug == False):
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
    import os
    import sys
    import threading
    import time
    from datetime import datetime, timedelta

except Exception as e:
    ImportError = e

# #################################################################################################
# # private Imports
# #################################################################################################
try:
    PrivateImportError = None
    from GetModbus import ModBusHandler
    from Host import Raspi_CallBack

    sys.path.insert(0, importPath)
    import Error
    import Utils
    import SunRiseSet
    from configuration import Global as _conf, PvInverter as PvInv, Grid, Battery, VeBus, System
    from influxHandler import influxIO, _SensorData as SensorData

except Exception as e:
    PrivateImportError = e

# #################################################################################################
# # UmgebungsVariablen / Globals
# #################################################################################################

# #################################################################################################
# # Logging geht in dieselbe Datei, trotz verschiedener Prozesse!
# #################################################################################################

# #################################################################################################
# # Funktionen
# # Prototypen
# #################################################################################################

# #################################################################################################
# # Classes: CallRaspi
## \details Pingt in regelmaessigen Abstaenden den Vrm Mqtt Broker an
# https://dev.to/hasansajedi/running-a-method-as-a-background-process-in-python-21li
# #################################################################################################
class CalcPercentageBreakdown():  #object

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
                self.log = logger.getLogger('Calculations')
                self.influxHdlrDaily = influxIO(_host = _conf.INFLUXDB_ADDRESS, _port = _conf.INFLUXDB_PORT, _username = _conf.INFLUXDB_USER, _password = _conf.INFLUXDB_PASSWORD, _database = None, _gzip = _conf.INFLUXDB_ZIPPED, logger = logger)
                self.influxHdlrLong = influxIO(_host = _conf.INFLUXDB_ADDRESS, _port = _conf.INFLUXDB_PORT, _username = _conf.INFLUXDB_USER, _password = _conf.INFLUXDB_PASSWORD, _database = None, _gzip = _conf.INFLUXDB_ZIPPED, logger = logger)

                self.bufferList = []
                self.WriteEnergyToDbDelay = 0

                ## Modbus Initialisieren
                self.mdbHdlr = ModBusHandler(logger = logger)
                self.SmaEn = {}
                self.PikoEn = {}
                self.IsNewDay = True

                self.UBatMax = float(0.0)
                self.IBatCharge = float(0.0)
                self.PBatCharge = float(0.0)
                self.UBatMin = float(100.0)
                self.IBatDis = float(0.0)
                self.PBatDis = float(0.0)
                self.AmpHourMax = float(0.0)
                self.WattHourMax = float(0.0)
                self.SmaP = 0
                self.PikoP = 0

                self.IsNewDay2 = False
                self.IsNewMonth = False
                self.IsInitWritten2 = False

                self.IsNewDay3 = False
                self.IsNewYear = False
                self.IsInitWritten3 = False

                ## auslesen der Raspi Temperatur
                Raspi_CallBack(_conf.HOST_INTERVAL, self.on_Raspi, logger)

                thread = threading.Thread(target=self.run, args=(interval, ))
                thread.daemon = True
                thread.start()

            except Exception as e:
                self.log.error("CalcPercentageBreakdown __init__: {}".format(e))

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

            divide = 8

            try:
                self.log.info("Starte Berechnungen mit Intervall {} sek.".format(interval))
                ## Database initialisieren
                for i in range(10):
                    ver = self.influxHdlrDaily._init_influxdb_database(_conf.INFLUXDB_DATABASE, 'Calculations')
                    if (ver != None):
                        self.log.info('Daily influxdb Version: {}'.format(ver))
                        break

                    self.influxHdlrDaily._close_connection(_conf.INFLUXDB_DATABASE, 'Calculations')
                    time.sleep(_conf.INLFUXDB_DELAY)

                for i in range(10):
                    ver = self.influxHdlrLong._init_influxdb_database(_conf.INFLUXDB_DATABASE_LONG, 'CalculationsMonth')
                    if (ver != None):
                        self.log.info('Monthly influxdb Version: {}'.format(ver))
                        break

                    self.influxHdlrLong._close_connection(_conf.INFLUXDB_DATABASE_LONG, 'CalculationsMonth')
                    time.sleep(_conf.INLFUXDB_DELAY)

                # Beim Init verzögern, da kommen viele Daten vom mqtt Broker
                time.sleep(interval)
                self.log.info('waiting')
                time.sleep(interval)
                self.log.info('running')

                while True:
                    time.sleep(interval / divide)
                    self.SmaEn = self.mdbHdlr.FetchSmaData()
                    #self.log.info('SmaEn: {}'.format(self.SmaEn))
                    self.PikoEn = self.mdbHdlr.FetchPikoData(126)
                    #self.log.info('PikoEn: {}'.format(self.PikoEn))
                    self._calcPercentage()

                    time.sleep(interval / divide)
                    self._calcTotalEnergy()

                    time.sleep(interval / divide)
                    self._calcPercentage()

                    time.sleep(interval / divide)
                    self._calcDailyEnergySoFar()

                    time.sleep(interval / divide)
                    self._calcPercentage()

                    time.sleep(interval / divide)
                    self._calcMonthlyEnergySoFar()

                    time.sleep(interval / divide)
                    self._calcPercentage()

                    time.sleep(interval / divide)
                    self._calcYearlyEnergySoFar()

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
                influxHandler._close_connection(influxHandler.database, 'Calculations')
                time.sleep(_conf.INLFUXDB_SHORT_DELAY)
                influxHandler._init_influxdb_database(influxHandler.database, 'Calculations')
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
                influxHandler._close_connection(influxHandler.database, 'Calculations')
                time.sleep(_conf.INLFUXDB_SHORT_DELAY)
                influxHandler._init_influxdb_database(influxHandler.database, 'Calculations')
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
                    self.log.warning("_getVal: Fehler beim lesen von {}".format(QUERY))
                    ## Database initialisieren
                    influxHandler._close_connection(influxHandler.database, 'Calculations')
                    time.sleep(_conf.INLFUXDB_SHORT_DELAY)
                    influxHandler._init_influxdb_database(influxHandler.database, 'Calculations')
                    tmp[0] = 0.0
                    #break
                break

            resultVar, typ, length = Utils._check_Data_Type(tmp[0], Utils.toFloat)
            return resultVar

    # # Ende Funktion: '_getVal ' ############################################################

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
                        retVal = influxHandler._send_sensor_data_to_influxdb(sensor_data, 'Calculations')

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
                influxHandler._close_connection(influxHandler.database, 'Calculations')
                time.sleep(_conf.INLFUXDB_SHORT_DELAY)
                influxHandler._init_influxdb_database(influxHandler.database, 'Calculations')

    # # Ende Funktion: '_writeEnergyToDb ' ###############################################################

    # #################################################################################################
    # #  Funktion: '_calcDailyEnergySoFar '
    ## 	\details
    #   \param[in]	-
    #   \return     -
    # #################################################################################################
        def _calcDailyEnergySoFar(self):

            try:
                sensor_data = []
                sensor_dataShort = []
                bIsNight = False
                datStream = []

                AMh, AMm, UMh, UMm, lt_tag, lt_monat, lt_jahr, lt_h, lt_m, lt_s = SunRiseSet.get_Info([])
                sunRise = AMh  * 60 + AMm
                sunSet  = UMh  * 60 + UMm
                localNow  = lt_h * 60 + lt_m

                strFolder = "{}{}".format(_conf.EXPORT_FILEPATH, lt_jahr)
                fileName = "{}/MaxMinVal.log".format(strFolder)
                AhWhLog = "{}/AhWh.log".format(strFolder)
                if (not os.path.exists(strFolder)):
                    os.mkdir(strFolder)
                    os.chmod(strFolder, 0o777)

                DayTimeStamp = _conf.DAYTIMESTAMP.format(lt_jahr, lt_monat, lt_tag)
                DaySoFarTimeStamp = _conf.DAYSOFARTIMESTAMP.format(lt_jahr, lt_monat, lt_tag)
                timestamp = datetime.utcnow()
                timestamp = ("'{0}-{1:02}-{2:02}T{3:02}:{4:02}:{5:02}.{6}Z'").format(timestamp.year, timestamp.month, timestamp.day, timestamp.hour, timestamp.minute, timestamp.second, timestamp.microsecond)

                #self.log.info(f'sunRise: {sunRise}; localNow: {localNow}; sunSet: {sunSet}')
                if (localNow > sunSet):     #Zeit <= Mitternacht
                    self.IsNewDay = False
                    bIsNight = True

                if (localNow < sunRise) and (bIsNight == False):    # Zeit < Sonnenaufgang und Zeit > Mitternacht -> Unmittelbar nach Mitternacht
                    if (self.IsNewDay == False):
                        self.IsNewDay = True

                        sensor_data.append(SensorData(PvInv.RegEx, PvInv.Label1, ["AcEnergyForwardDaySoFar",], [float(0.0),], DaySoFarTimeStamp))
                        sensor_data.append(SensorData(PvInv.RegEx, PvInv.Label2, ["AcEnergyForwardDaySoFar",], [float(0.0),], DaySoFarTimeStamp))
                        sensor_data.append(SensorData(System.RegEx, System.Label1, ["PvInvertersAcEnergyForwardDaySoFar",], [float(0.0),], DaySoFarTimeStamp))

                        self.UBatMax = 0.0
                        sensor_data.append(SensorData(VeBus.RegEx, VeBus.Label1, ["UBatMax",], [self.UBatMax,], DaySoFarTimeStamp))
                        self.IBatCharge = 0.0
                        sensor_data.append(SensorData(VeBus.RegEx, VeBus.Label1, ["IBatCharge",], [self.IBatCharge,], DaySoFarTimeStamp))
                        self.PBatCharge = 0.0
                        sensor_data.append(SensorData(VeBus.RegEx, VeBus.Label1, ["PBatCharge",], [self.PBatCharge,], DaySoFarTimeStamp))
                        self.UBatMin = 100.0
                        sensor_data.append(SensorData(VeBus.RegEx, VeBus.Label1, ["UBatMin",], [self.UBatMin,], DaySoFarTimeStamp))
                        self.IBatDis = 0.0
                        sensor_data.append(SensorData(VeBus.RegEx, VeBus.Label1, ["IBatDis",], [self.IBatDis,], DaySoFarTimeStamp))
                        self.PBatDis = 0.0
                        sensor_data.append(SensorData(VeBus.RegEx, VeBus.Label1, ["PBatDis",], [self.PBatDis,], DaySoFarTimeStamp))
                        self.AmpHourMax = 0.0
                        sensor_data.append(SensorData(VeBus.RegEx, VeBus.Label1, ["AmpHourMax",], [self.AmpHourMax ,], DaySoFarTimeStamp))
                        self.WattHourMax = 0.0
                        sensor_data.append(SensorData(VeBus.RegEx, VeBus.Label1, ["WattHourMax",], [self.WattHourMax,], DaySoFarTimeStamp))
                        self.SmaP = 0
                        sensor_data.append(SensorData(PvInv.RegEx, PvInv.Label1, ["PeakSmaPower",], [self.SmaP,], DaySoFarTimeStamp))
                        self.PikoP = 0
                        sensor_data.append(SensorData(PvInv.RegEx, PvInv.Label2, ["PeakPikoPower",], [self.PikoP,], DaySoFarTimeStamp))
                        ###########################################################
                        self.log.info("_calcDailyEnergySoFar NEW DAY: {}".format(sensor_data))
                        ###########################################################

                        self._writeEnergyToDb(self.influxHdlrLong, sensor_data, '_calcDailyEnergySoFar-1')

                if (bIsNight == False) and (self.IsNewDay == True):
                    #resultVar = Utils._check_Data_TypeOld(self.PikoEn['40670'])
                    resultVar, typ, length = Utils._check_Data_Type(self.PikoEn['40670'], Utils.toFloat)
                    PikoEn = round(resultVar / 1000, 3)
                    sensor_data.append(SensorData(PvInv.RegEx, PvInv.Label2, ["AcEnergyForwardDaySoFar",], [PikoEn,], DaySoFarTimeStamp))

                    #resultVar = Utils._check_Data_TypeOld(self.SmaEn['30535'])
                    resultVar, typ, length = Utils._check_Data_Type(self.SmaEn['30535'], Utils.toFloat)
                    SmaEn = round(resultVar / 1000, 3)
                    sensor_data.append(SensorData(PvInv.RegEx, PvInv.Label1, ["AcEnergyForwardDaySoFar",], [SmaEn,], DaySoFarTimeStamp))

                    #resultVar = Utils._check_Data_TypeOld(PikoEn + SmaEn)
                    resultVar, typ, length = Utils._check_Data_Type(PikoEn + SmaEn, Utils.toFloat)
                    PvInvertersAcEnergyForwardDaySoFar = round(resultVar, 3)
                    sensor_data.append(SensorData(System.RegEx, System.Label1, ["PvInvertersAcEnergyForwardDaySoFar",], [PvInvertersAcEnergyForwardDaySoFar,], DaySoFarTimeStamp))
                    ###########################################################
                    #self.log.info("_calcDailyEnergySoFar: {}".format(sensor_data))
                    ###########################################################

                    ## PeakLeistung SMA und PIKO
                    #resultVar = Utils._check_Data_TypeOld(self.PikoEn['40200'])
                    resultVar, typ, length = Utils._check_Data_Type(self.PikoEn['40200'], Utils.toInt)
                    PikoPower = round(resultVar, 3)
                    if (self.PikoP < PikoPower) and (PikoPower < 4000):
                        self.PikoP = PikoPower
                        sensor_data.append(SensorData(PvInv.RegEx, PvInv.Label2, ["PeakPikoPower",], [PikoPower,], DaySoFarTimeStamp))
                        ###########################################################
                        #self.log.info(f'   PeakPikoPower: {PikoPower:9.2f}W')
                        ###########################################################

                    #resultVar = Utils._check_Data_TypeOld(self.SmaEn['30775'])
                    resultVar, typ, length = Utils._check_Data_Type(self.SmaEn['30775'], Utils.toInt)
                    SmaPower = round(resultVar, 3)
                    if (self.SmaP < SmaPower) and (SmaPower < 4000):
                        self.SmaP = SmaPower
                        sensor_data.append(SensorData(PvInv.RegEx, PvInv.Label1, ["PeakSmaPower",], [SmaPower,], DaySoFarTimeStamp))
                        ###########################################################
                        #self.log.info(f'    PeakSmaPower: {SmaPower:9.2f}W')
                        ###########################################################

                    ## Strings GleichSpannung, ~Strom, ~Leistung, Temperatur
                    ## SMA
                    #SmaDc1U = Utils._check_Data_TypeOld(self.SmaEn['40642'])
                    SmaDc1U, typ, length = Utils._check_Data_Type(self.SmaEn['40642'], Utils.toFloat)
                    sensor_dataShort.append(SensorData(PvInv.RegEx, PvInv.Label1, ["Dc1U",], [SmaDc1U,], timestamp))
                    #SmaDc1I = Utils._check_Data_TypeOld(self.SmaEn['40641'])
                    SmaDc1I, typ, length = Utils._check_Data_Type(self.SmaEn['40641'], Utils.toFloat)
                    sensor_dataShort.append(SensorData(PvInv.RegEx, PvInv.Label1, ["Dc1I",], [SmaDc1I,], timestamp))
                    #SmaDc1P = Utils._check_Data_TypeOld(self.SmaEn['40643'])
                    SmaDc1P, typ, length = Utils._check_Data_Type(self.SmaEn['40643'], Utils.toFloat)
                    sensor_dataShort.append(SensorData(PvInv.RegEx, PvInv.Label1, ["Dc1P",], [SmaDc1P,], timestamp))
                    #SmaDc2U = Utils._check_Data_TypeOld(self.SmaEn['40662'])
                    SmaDc2U, typ, length = Utils._check_Data_Type(self.SmaEn['40662'], Utils.toFloat)
                    sensor_dataShort.append(SensorData(PvInv.RegEx, PvInv.Label1, ["Dc2U",], [SmaDc2U,], timestamp))
                    #SmaDc2I = Utils._check_Data_TypeOld(self.SmaEn['40661'])
                    SmaDc2I, typ, length = Utils._check_Data_Type(self.SmaEn['40661'], Utils.toFloat)
                    sensor_dataShort.append(SensorData(PvInv.RegEx, PvInv.Label1, ["Dc2I",], [SmaDc2I,], timestamp))
                    #SmaDc2P = Utils._check_Data_TypeOld(self.SmaEn['40663'])
                    SmaDc2P, typ, length = Utils._check_Data_Type(self.SmaEn['40663'], Utils.toFloat)
                    sensor_dataShort.append(SensorData(PvInv.RegEx, PvInv.Label1, ["Dc2P",], [SmaDc2P,], timestamp))
                    #SmaTemp = int(Utils._check_Data_TypeOld(self.SmaEn['40219']))
                    #SmaTemp, typ, length = Utils._check_Data_Type(self.SmaEn['40219'], Utils.toInt)
                    #sensor_dataShort.append(SensorData(PvInv.RegEx, PvInv.Label1, ["DcTemp",], [SmaTemp,], timestamp))
                    ###########################################################
                    #self.log.info(f'SMA: Dc1U: {SmaDc1U:9.2f}V;  Dc1I: {SmaDc1I:9.2f}A Dc1P: {SmaDc1P:9.2f}W Dc2U: {SmaDc2U:9.2f}V Dc2I: {SmaDc2I:9.2f}A Dc2P: {SmaDc2P:9.2f}W Temp: {SmaTemp:9.2f}C')
                    ###########################################################

                    ##Piko
                    #PikoDc1U = Utils._check_Data_TypeOld(self.PikoEn['40642'])
                    PikoDc1U, typ, length = Utils._check_Data_Type(self.PikoEn['40642'], Utils.toFloat)
                    sensor_dataShort.append(SensorData(PvInv.RegEx, PvInv.Label2, ["Dc1U",], [PikoDc1U,], timestamp))
                    #PikoDc1I = Utils._check_Data_TypeOld(self.PikoEn['40641'])
                    PikoDc1I, typ, length = Utils._check_Data_Type(self.PikoEn['40641'], Utils.toFloat)
                    sensor_dataShort.append(SensorData(PvInv.RegEx, PvInv.Label2, ["Dc1I",], [PikoDc1I,], timestamp))
                    #PikoDc1P = Utils._check_Data_TypeOld(self.PikoEn['40643'])
                    PikoDc1P, typ, length = Utils._check_Data_Type(self.PikoEn['40643'], Utils.toFloat)
                    sensor_dataShort.append(SensorData(PvInv.RegEx, PvInv.Label2, ["Dc1P",], [PikoDc1P,], timestamp))
                    #PikoTemp = int(Utils._check_Data_TypeOld(self.PikoEn['40219']))
                    #PikoTemp, typ, length = Utils._check_Data_Type(self.PikoEn['40219'], Utils.toInt)
                    #sensor_dataShort.append(SensorData(PvInv.RegEx, PvInv.Label2, ["Dc1Temp",], [PikoTemp,], timestamp))
                    ###########################################################
                    #self.log.info(f'Piko: Dc1U: {PikoDc1U:9.2f}V;  Dc1I: {PikoDc1I:9.2f}A Dc1P: {PikoDc1P:9.2f}W Temp: {PikoTemp:9.2f}C')
                    ###########################################################
                    #self._writeEnergyToDb(self.influxHdlrDaily, sensor_dataShort, '_calcDailyEnergySoFar-2')

                #SmaTemp = int(Utils._check_Data_TypeOld(self.SmaEn['40219']))
                SmaTemp, typ, length = Utils._check_Data_Type(self.SmaEn['40219'], Utils.toInt)
                sensor_dataShort.append(SensorData(PvInv.RegEx, PvInv.Label1, ["DcTemp",], [SmaTemp,], timestamp))

                #PikoTemp = int(Utils._check_Data_TypeOld(self.PikoEn['40219']))
                PikoTemp, typ, length = Utils._check_Data_Type(self.PikoEn['40219'], Utils.toInt)
                sensor_dataShort.append(SensorData(PvInv.RegEx, PvInv.Label2, ["Dc1Temp",], [PikoTemp,], timestamp))
                ###########################################################
                self._writeEnergyToDb(self.influxHdlrDaily, sensor_dataShort, '_calcDailyEnergySoFar-2')

                ## max und min, Batterie Spannung, Strom, Lade und Entladeleistung, max Amphours und WattHours
                #sensor_data = []
                tmpVal = "SELECT max(Dc0Voltage) FROM vebus where instance='MultiPlus-II' and time >= {}".format(DayTimeStamp)
                UBatMax = self._getVal(self.influxHdlrDaily, tmpVal, VeBus.RegEx, 'max', '_calcDailyEnergySoFar')
                if (self.UBatMax < UBatMax):
                    self.UBatMax = UBatMax
                    datStream.append(f'{lt_tag:02d}.{lt_monat:02d}.{lt_jahr:4d} {lt_h:02d}:{lt_m:02d}:{lt_s:02d}    UBatMax:{UBatMax:9.2f}')
                    sensor_data.append(SensorData(VeBus.RegEx, VeBus.Label1, ["UBatMax",], [UBatMax,], DaySoFarTimeStamp))
                    ###########################################################
                    #self.log.info(f'    Bat UBatMax : {UBatMax:9.2f}V')
                    ###########################################################
                tmpVal = "SELECT max(Dc0Current) FROM vebus where instance='MultiPlus-II' and time >= {}".format(DayTimeStamp)
                IBatCharge = self._getVal(self.influxHdlrDaily, tmpVal, VeBus.RegEx, 'max', '_calcDailyEnergySoFar')
                if (self.IBatCharge < IBatCharge):
                    self.IBatCharge = IBatCharge
                    datStream.append(f'{lt_tag:02d}.{lt_monat:02d}.{lt_jahr:4d} {lt_h:02d}:{lt_m:02d}:{lt_s:02d} IBatCharge:{IBatCharge:9.2f}')
                    sensor_data.append(SensorData(VeBus.RegEx, VeBus.Label1, ["IBatCharge",], [IBatCharge,], DaySoFarTimeStamp))
                    ###########################################################
                    #self.log.info(f' Bat IBatCharge : {IBatCharge:9.2f}A')
                    ###########################################################
                tmpVal = "SELECT max(DcBatteryPower) FROM system where instance='Gateway' and time >= {}".format(DayTimeStamp)
                PBatCharge = self._getVal(self.influxHdlrDaily, tmpVal, System.RegEx, 'max', '_calcDailyEnergySoFar')
                if (self.PBatCharge < PBatCharge):
                    self.PBatCharge = PBatCharge
                    datStream.append(f'{lt_tag:02d}.{lt_monat:02d}.{lt_jahr:4d} {lt_h:02d}:{lt_m:02d}:{lt_s:02d} PBatCharge:{PBatCharge:9.2f}')
                    sensor_data.append(SensorData(VeBus.RegEx, VeBus.Label1, ["PBatCharge",], [PBatCharge,], DaySoFarTimeStamp))
                    ###########################################################
                    #self.log.info(f' Bat PBatCharge : {PBatCharge:9.2f}W')
                    ###########################################################
                tmpVal = "SELECT min(Dc0Voltage) FROM vebus where instance='MultiPlus-II' and time >= {}".format(DayTimeStamp)    # = max. negative Entladung
                UBatMin = self._getVal(self.influxHdlrDaily, tmpVal, VeBus.RegEx, 'min', '_calcDailyEnergySoFar')
                if (self.UBatMin > UBatMin):
                    self.UBatMin = UBatMin
                    datStream.append(f'{lt_tag:02d}.{lt_monat:02d}.{lt_jahr:4d} {lt_h:02d}:{lt_m:02d}:{lt_s:02d}    UBatMin:{UBatMin:9.2f}')
                    sensor_data.append(SensorData(VeBus.RegEx, VeBus.Label1, ["UBatMin",], [UBatMin,], DaySoFarTimeStamp))
                    ###########################################################
                    #self.log.info(f'    Bat UBatMin : {UBatMin:9.2f}V')
                    ###########################################################
                tmpVal = "SELECT min(Dc0Current) FROM vebus where instance='MultiPlus-II' and time >= {}".format(DayTimeStamp)    # = max. negative Entladung
                IBatDis = self._getVal(self.influxHdlrDaily, tmpVal, VeBus.RegEx, 'min', '_calcDailyEnergySoFar')
                if (self.IBatDis > IBatDis):
                    self.IBatDis = IBatDis
                    datStream.append(f'{lt_tag:02d}.{lt_monat:02d}.{lt_jahr:4d} {lt_h:02d}:{lt_m:02d}:{lt_s:02d}    IBatDis:{IBatDis:9.2f}')
                    sensor_data.append(SensorData(VeBus.RegEx, VeBus.Label1, ["IBatDis",], [IBatDis,], DaySoFarTimeStamp))
                    ###########################################################
                    #self.log.info(f'    Bat IBatDis : {IBatDis:9.2f}A')
                    ###########################################################
                tmpVal = "SELECT min(DcBatteryPower) FROM system where instance='Gateway' and time >= {}".format(DayTimeStamp)    # = max. negative Entladung
                PBatDis = self._getVal(self.influxHdlrDaily, tmpVal, System.RegEx, 'min', '_calcDailyEnergySoFar')
                if (self.PBatDis > PBatDis):
                    self.PBatDis = PBatDis
                    datStream.append(f'{lt_tag:02d}.{lt_monat:02d}.{lt_jahr:4d} {lt_h:02d}:{lt_m:02d}:{lt_s:02d}    PBatDis:{PBatDis:9.2f}')
                    sensor_data.append(SensorData(VeBus.RegEx, VeBus.Label1, ["PBatDis",], [PBatDis,], DaySoFarTimeStamp))
                    ###########################################################
                    #self.log.info(f'    Bat PBatDis : {PBatDis:9.2f}W')
                    ###########################################################

                ### Bei diesen werten in der Vergangenheit zurückgehen bis gültiger Wert kommt, bzw. den letzten gültigen separat abspeichern
                tmpVal = "SELECT min(ConsumedAmphours) FROM vebus where instance='MultiPlus-II' and time >= {}"   # = max. negative Entladung
                AmpHourMax = self._getVal2(self.influxHdlrDaily, tmpVal, VeBus.RegEx, DayTimeStamp, 'min', 'ConsumedAmphours', '_calcDailyEnergySoFar')
                if (self.AmpHourMax > AmpHourMax):
                    self.AmpHourMax = AmpHourMax
                    datStream.append(f'{lt_tag:02d}.{lt_monat:02d}.{lt_jahr:4d} {lt_h:02d}:{lt_m:02d}:{lt_s:02d} AmpHourMax:{AmpHourMax:9.2f}')
                    sensor_data.append(SensorData(VeBus.RegEx, VeBus.Label1, ["AmpHourMax",], [AmpHourMax,], DaySoFarTimeStamp))
                    ###########################################################
                    #self.log.info(f' Bat AmpHourMax : {AmpHourMax:9.2f}Ah')
                    ###########################################################

                tmpVal = "SELECT last(ConsumedAmphours) FROM vebus where instance='MultiPlus-II' and time >= {}"
                AktAmpHour = self._getVal2(self.influxHdlrDaily, tmpVal, VeBus.RegEx, DayTimeStamp, 'last', 'ConsumedAmphours','_calcDailyEnergySoFar')
                Utils._write_File(AhWhLog, f'{AktAmpHour:9.2f}\n', "w")
                ### Ende Vergangenheit suchen

                for dat in datStream:
                    Utils._write_File(fileName, f'{dat}\n', "a")

                self._writeEnergyToDb(self.influxHdlrLong, sensor_data, '_calcDailyEnergySoFar-3')

            except Exception as e:
                #print('_calcDailyEnergySoFar: {}'.format(e))
                self.log.error("_calcDailyEnergySoFar-4: {}".format(e))

    # # Ende Funktion: ' _calcDailyEnergySoFar ' #####################################################

    # #################################################################################################
    # #  Funktion: '_calcMonthlyEnergySoFar '
    ## 	\details  am 1. des Monats mit 0 beginnen abspeichern in der AcEnergyForwardMonth, den täglichen zuwachs in der AcEnergyForwardMonthSoFar.
    ## Um Mitternacht, bzw. wenn die Wechselrichter aus sind umspeichern dieses Wertes.
    #   \param[in]	-
    #   \return     -
    # #################################################################################################
        def _calcMonthlyEnergySoFar(self):

            try:
                sensor_data = []
                if (datetime.day == 1) and (self.IsInitWritten2 == False):
                    self.IsNewMonth = True
                    ###########################################################
                    self.log.info("_calcMonthlyEnergySoFar First Day of MONTH")
                    ###########################################################

                if (datetime.day == 2):
                    self.IsInitWritten2 = False
                    ###########################################################
                    self.log.info("_calcMonthlyEnergySoFar Second Day of MONTH")
                    ###########################################################

                AMh, AMm, UMh, UMm, lt_tag, lt_monat, lt_jahr, lt_h, lt_m, lt_s = SunRiseSet.get_Info([])
                sunRise = AMh  * 60 + AMm
                sunSet  = UMh  * 60 + UMm
                localNow  = lt_h * 60 + lt_m

                MonthTimeStamp = _conf.MONTHTIMESTAMP.format(lt_jahr, lt_monat)
                MonthSoFarTimeStamp = _conf.MONTHSOFARTIMESTAMP.format(lt_jahr, lt_monat)

                if (localNow > sunSet):
                    self.IsNewDay2 = True
                    return

                if (localNow < sunRise):
                    if (self.IsNewMonth == True):
                        self.IsNewMonth = False
                        self.IsInitWritten2 = True

                        sensor_data.append(SensorData(PvInv.RegEx, PvInv.Label2, ["AcEnergyForwardMonth",], [float(0.0),], MonthTimeStamp))
                        sensor_data.append(SensorData(PvInv.RegEx, PvInv.Label1, ["AcEnergyForwardMonth",], [float(0.0),], MonthTimeStamp))
                        sensor_data.append(SensorData(System.RegEx, System.Label1, ["PvInvertersAcEnergyForwardMonth",], [float(0.0),], MonthTimeStamp))
                        sensor_data.append(SensorData(PvInv.RegEx, PvInv.Label2, ["AcEnergyForwardMonthSoFar",], [float(0.0),], MonthSoFarTimeStamp))
                        sensor_data.append(SensorData(PvInv.RegEx, PvInv.Label1, ["AcEnergyForwardMonthSoFar",], [float(0.0),], MonthSoFarTimeStamp))
                        sensor_data.append(SensorData(System.RegEx, System.Label1, ["PvInvertersAcEnergyForwardMonthSoFar",], [float(0.0),], MonthSoFarTimeStamp))

                        self.log.info("_calcMonthlyEnergySoFar NEW MONTH: {}".format(sensor_data))
                        self._writeEnergyToDb(self.influxHdlrLong, sensor_data, '_calcMonthlyEnergySoFar-1')

                    if (self.IsNewDay2 == True) and (self.IsNewMonth == False):
                        self.IsNewDay2 = False

                        PIKO_ENERGY = "SELECT (AcEnergyForwardMonthSoFar) FROM pvinverter where instance='PIKO' and time >= {}".format(MonthSoFarTimeStamp)
                        sensor_data.append(self._prepareData(self.influxHdlrLong, PIKO_ENERGY, PvInv.RegEx, PvInv.Label2, 'AcEnergyForwardMonthSoFar', 'AcEnergyForwardMonth', MonthTimeStamp, '_calcMonthlyEnergySoFar'))

                        SMA_ENERGY = "SELECT (AcEnergyForwardMonthSoFar) FROM pvinverter where instance='SMA' and time >= {}".format(MonthSoFarTimeStamp)
                        sensor_data.append(self._prepareData(self.influxHdlrLong, SMA_ENERGY, PvInv.RegEx, PvInv.Label1, 'AcEnergyForwardMonthSoFar', 'AcEnergyForwardMonth', MonthTimeStamp, '_calcMonthlyEnergySoFar'))

                        SYSTEM_ENERGY = "SELECT (PvInvertersAcEnergyForwardMonthSoFar) FROM system where instance='Gateway' and time >= {}".format(MonthSoFarTimeStamp)
                        sensor_data.append(self._prepareData(self.influxHdlrLong, SYSTEM_ENERGY, System.RegEx, System.Label1, 'PvInvertersAcEnergyForwardMonthSoFar', 'PvInvertersAcEnergyForwardMonth', MonthTimeStamp, '_calcMonthlyEnergySoFar'))
                        ###########################################################
                        self.log.info("_calcMonthlyEnergySoFar NEW DAY: {}".format(sensor_data))
                        ###########################################################

                        self._writeEnergyToDb(self.influxHdlrLong, sensor_data, '_calcMonthlyEnergySoFar-2')

                PIKO_ENERGY = "SELECT (AcEnergyForwardMonth) FROM pvinverter where instance='PIKO' and time >= {}".format(MonthTimeStamp)
                AcEnergyForwardMonth = self._getVal(self.influxHdlrLong, PIKO_ENERGY, PvInv.RegEx, 'AcEnergyForwardMonth', '_calcMonthlyEnergySoFar')

                resultVar = Utils._check_Data_TypeOld(self.PikoEn['40670'])
                #resultVar, typ, length = Utils._check_Data_Type(self.PikoEn['40670'], Utils.toFloat)
                PikoEn = round(resultVar / 1000, 3)
                AcEnergyForwardMonthSoFar = round(AcEnergyForwardMonth + PikoEn, 3)
                sensor_data.append(SensorData(PvInv.RegEx, PvInv.Label2, ["AcEnergyForwardMonthSoFar",], [AcEnergyForwardMonthSoFar,], MonthSoFarTimeStamp))
                ###########################################################
                #self.log.info("PIKO AcEnergyForwardMonth : {}".format(AcEnergyForwardMonth))
                #self.log.info("PIKO self.PikoEn['40670'] : {}".format(self.PikoEn['40670']))
                #self.log.info("PIKO PikoEn : {}".format(PikoEn))
                ###########################################################

                SMA_ENERGY = "SELECT (AcEnergyForwardMonth) FROM pvinverter where instance='SMA' and time >= {}".format(MonthTimeStamp)
                AcEnergyForwardMonth = self._getVal(self.influxHdlrLong, SMA_ENERGY, PvInv.RegEx, 'AcEnergyForwardMonth', '_calcMonthlyEnergySoFar')

                resultVar = Utils._check_Data_TypeOld(self.SmaEn['30535'])
                #resultVar, typ, length = Utils._check_Data_Type(self.SmaEn['30535'], Utils.toFloat)
                SmaEn = round(resultVar / 1000, 3)
                AcEnergyForwardMonthSoFar = round(AcEnergyForwardMonth + SmaEn, 3)
                sensor_data.append(SensorData(PvInv.RegEx, PvInv.Label1, ["AcEnergyForwardMonthSoFar",], [AcEnergyForwardMonthSoFar,], MonthSoFarTimeStamp))
                ###########################################################
                #self.log.info("SMA AcEnergyForwardMonth : {}".format(AcEnergyForwardMonth))
                #self.log.info("SMA self.SmaEn['30535'] : {}".format(self.SmaEn['30535']))
                #self.log.info("SMA SmaEn : {}".format(SmaEn))
                ###########################################################

                SYSTEM_ENERGY = "SELECT (PvInvertersAcEnergyForwardMonth) FROM system where instance='Gateway' and time >= {}".format(MonthTimeStamp)
                PvInvertersAcEnergyForwardMonth = self._getVal(self.influxHdlrLong, SYSTEM_ENERGY, System.RegEx, 'PvInvertersAcEnergyForwardMonth', '_calcMonthlyEnergySoFar')

                PvInvertersAcEnergyForwardMonthSoFar = round(PvInvertersAcEnergyForwardMonth + PikoEn + SmaEn, 3)
                sensor_data.append(SensorData(System.RegEx, System.Label1, ["PvInvertersAcEnergyForwardMonthSoFar",], [PvInvertersAcEnergyForwardMonthSoFar,], MonthSoFarTimeStamp))

                ###########################################################
                #self.log.info("_calcMonthlyEnergySoFar: {}".format(sensor_data))
                ###########################################################

                self._writeEnergyToDb(self.influxHdlrLong, sensor_data, '_calcMonthlyEnergySoFar-3')

            except Exception as e:
                self.log.error("_calcMonthlyEnergySoFar-4: {}".format(e))

    # # Ende Funktion: ' _calcMonthlyEnergySoFar ' #####################################################

    # #################################################################################################
    # #  Funktion: '_calcYearlyEnergySoFar '
    ## 	\details  am 1. des Monats mit 0 beginnen abspeichern in der AcEnergyForwardMonth, den täglichen zuwachs in der AcEnergyForwardMonthSoFar.
    ## Um Mitternacht, bzw. wenn die Wechselrichter aus sind umspeichern dieses Wertes.
    #   \param[in]	-
    #   \return     -
    # #################################################################################################
        def _calcYearlyEnergySoFar(self):

            try:
                sensor_data = []
                if (datetime.day == 1) and (datetime.month == 1) and (self.IsInitWritten3 == False):
                    self.IsNewYear = True

                if (datetime.day == 2) and (datetime.month == 1):
                    self.IsInitWritten3 = False

                AMh, AMm, UMh, UMm, lt_tag, lt_monat, lt_jahr, lt_h, lt_m, lt_s = SunRiseSet.get_Info([])
                sunRise = AMh  * 60 + AMm
                sunSet  = UMh  * 60 + UMm
                localNow  = lt_h * 60 + lt_m

                YearTimeStamp = _conf.YEARTIMESTAMP.format(lt_jahr)
                YearSoFarTimeStamp = _conf.YEARSOFARTIMESTAMP.format(lt_jahr)
                if (localNow > sunSet):
                    self.IsNewDay3 = True
                    return

                if (localNow < sunRise):
                    if (self.IsNewYear == True):
                        self.IsNewYear = False
                        self.IsInitWritten3 = True

                        sensor_data.append(SensorData(PvInv.RegEx, PvInv.Label2, ["AcEnergyForwardYear",], [float(0.0),], YearTimeStamp))
                        sensor_data.append(SensorData(PvInv.RegEx, PvInv.Label1, ["AcEnergyForwardYear",], [float(0.0),], YearTimeStamp))
                        sensor_data.append(SensorData(System.RegEx, System.Label1, ["PvInvertersAcEnergyForwardYear",], [float(0.0),], YearTimeStamp))
                        sensor_data.append(SensorData(PvInv.RegEx, PvInv.Label2, ["AcEnergyForwardYearSoFar",], [float(0.0),], YearSoFarTimeStamp))
                        sensor_data.append(SensorData(PvInv.RegEx, PvInv.Label1, ["AcEnergyForwardYearSoFar",], [float(0.0),], YearSoFarTimeStamp))
                        sensor_data.append(SensorData(System.RegEx, System.Label1, ["PvInvertersAcEnergyForwardYearSoFar",], [float(0.0),], YearSoFarTimeStamp))

                        ###########################################################
                        self.log.info("_calcYearlyEnergySoFar NEW YEAR: {}".format(sensor_data))
                        ###########################################################
                        self._writeEnergyToDb(self.influxHdlrLong, sensor_data, '_calcYearlyEnergySoFar-1')

                    if (self.IsNewDay3 == True) and (self.IsNewYear == False):
                        self.IsNewDay3 = False

                        PIKO_ENERGY = "SELECT (AcEnergyForwardYearSoFar) FROM pvinverter where instance='PIKO' and time >= {}".format(YearSoFarTimeStamp)
                        sensor_data.append(self._prepareData(self.influxHdlrLong, PIKO_ENERGY, PvInv.RegEx, PvInv.Label2, 'AcEnergyForwardYearSoFar', 'AcEnergyForwardYear', YearTimeStamp, '_calcYearlyEnergySoFar'))
                        SMA_ENERGY = "SELECT (AcEnergyForwardYearSoFar) FROM pvinverter where instance='SMA' and time >= {}".format(YearSoFarTimeStamp)
                        sensor_data.append(self._prepareData(self.influxHdlrLong, SMA_ENERGY, PvInv.RegEx, PvInv.Label1, 'AcEnergyForwardYearSoFar', 'AcEnergyForwardYear', YearTimeStamp, '_calcYearlyEnergySoFar'))
                        SYSTEM_ENERGY = "SELECT (PvInvertersAcEnergyForwardYearSoFar) FROM system where instance='Gateway' and time >= {}".format(YearSoFarTimeStamp)
                        sensor_data.append(self._prepareData(self.influxHdlrLong, SYSTEM_ENERGY, System.RegEx, System.Label1, 'PvInvertersAcEnergyForwardYearSoFar', 'PvInvertersAcEnergyForwardYear', YearTimeStamp, '_calcYearlyEnergySoFar'))

                        ###########################################################
                        #self.log.info("_calcYearlyEnergySoFar NEW DAY: {}".format(sensor_data))
                        ###########################################################
                        self._writeEnergyToDb(self.influxHdlrLong, sensor_data, '_calcYearlyEnergySoFar-2')

                PIKO_ENERGY = "SELECT (AcEnergyForwardYear) FROM pvinverter where instance='PIKO' and time >= {}".format(YearTimeStamp)
                AcEnergyForwardYear = self._getVal(self.influxHdlrLong, PIKO_ENERGY, PvInv.RegEx, 'AcEnergyForwardYear', '_calcYearlyEnergySoFar')

                resultVar = Utils._check_Data_TypeOld(self.PikoEn['40670'])
                #resultVar, typ, length = Utils._check_Data_Type(self.PikoEn['40670'], Utils.toFloat)
                PikoEn = round(resultVar / 1000, 3)
                AcEnergyForwardYearSoFar = round(AcEnergyForwardYear + PikoEn, 3)
                sensor_data.append(SensorData(PvInv.RegEx, PvInv.Label2, ["AcEnergyForwardYearSoFar",], [AcEnergyForwardYearSoFar,], YearSoFarTimeStamp))

                ###########################################################
                #self.log.info("PIKO AcEnergyForwardYear : {}".format(AcEnergyForwardYear))
                #self.log.info("PIKO self.PikoEn['40670'] : {}".format(self.PikoEn['40670']))
                #self.log.info("PIKO PikoEn : {}".format(PikoEn))
                ###########################################################

                SMA_ENERGY = "SELECT (AcEnergyForwardYear) FROM pvinverter where instance='SMA' and time >= {}".format(YearTimeStamp)
                AcEnergyForwardYear = self._getVal(self.influxHdlrLong, SMA_ENERGY, PvInv.RegEx, 'AcEnergyForwardYear', '_calcYearlyEnergySoFar')

                resultVar = Utils._check_Data_TypeOld(self.SmaEn['30535'])
                #resultVar, typ, length = Utils._check_Data_Type(self.SmaEn['30535'], Utils.toFloat)
                SmaEn = round(resultVar / 1000, 3)
                AcEnergyForwardYearSoFar = round(AcEnergyForwardYear + SmaEn, 3)
                sensor_data.append(SensorData(PvInv.RegEx, PvInv.Label1, ["AcEnergyForwardYearSoFar",], [AcEnergyForwardYearSoFar,], YearSoFarTimeStamp))

                ###########################################################
                #self.log.info("SMA AcEnergyForwardYear : {}".format(AcEnergyForwardYear))
                #self.log.info("SMA self.SmaEn['30535'] : {}".format(self.SmaEn['30535']))
                #self.log.info("SMA SmaEn : {}".format(SmaEn))
                ###########################################################

                SYSTEM_ENERGY = "SELECT (PvInvertersAcEnergyForwardYear) FROM system where instance='Gateway' and time >= {}".format(YearTimeStamp)
                PvInvertersAcEnergyForwardYear = self._getVal(self.influxHdlrLong, SYSTEM_ENERGY, System.RegEx, 'PvInvertersAcEnergyForwardYear', '_calcYearlyEnergySoFar')

                PvInvertersAcEnergyForwardYearSoFar = round(PvInvertersAcEnergyForwardYear + PikoEn + SmaEn, 3)
                sensor_data.append(SensorData(System.RegEx, System.Label1, ["PvInvertersAcEnergyForwardYearSoFar",], [PvInvertersAcEnergyForwardYearSoFar,], YearSoFarTimeStamp))

                ###########################################################
                #self.log.info("_calcYearlyEnergySoFar: {}".format(sensor_data))
                ###########################################################
                self._writeEnergyToDb(self.influxHdlrLong, sensor_data, '_calcYearlyEnergySoFar-3')

            except Exception as e:
                self.log.error("_calcYearlyEnergySoFar-4: {}".format(e))

    # # Ende Funktion: ' _calcYearlyEnergySoFar ' #####################################################

    # #################################################################################################
    # #  Funktion: '_calcTotalEnergy '
    ## 	\details
    #   \param[in]	-
    #   \return     -
    # #################################################################################################
        def _calcTotalEnergy(self):

            try:
                sensor_data = []
                AMh, AMm, UMh, UMm, lt_tag, lt_monat, lt_jahr, lt_h, lt_m, lt_s = SunRiseSet.get_Info([])
                sunRise = AMh  * 60 + AMm
                sunSet  = UMh  * 60 + UMm
                localNow  = lt_h * 60 + lt_m
                DaySoFarTimeStamp = _conf.DAYSOFARTIMESTAMP.format(lt_jahr, lt_monat, lt_tag)
                if ((localNow > sunSet) or (localNow < sunRise)):
                    return

                resultVar = Utils._check_Data_TypeOld(self.PikoEn['40210'])
                #resultVar, typ, length = Utils._check_Data_Type(self.PikoEn['40210'], Utils.toFloat)
                PikoEn = round(resultVar / 1000, 3)
                sensor_data.append(SensorData(PvInv.RegEx, PvInv.Label2, ["AcEnergyForwardTotal",], [PikoEn,], DaySoFarTimeStamp))

                resultVar = Utils._check_Data_TypeOld(self.SmaEn['30529'])
                #resultVar, typ, length = Utils._check_Data_Type(self.SmaEn['30529'], Utils.toFloat)
                SmaEn = round(resultVar / 1000, 3)
                sensor_data.append(SensorData(PvInv.RegEx, PvInv.Label1, ["AcEnergyForwardTotal",], [SmaEn,], DaySoFarTimeStamp))

                resultVar = Utils._check_Data_TypeOld(PikoEn + SmaEn)
                #resultVar, typ, length = Utils._check_Data_Type(PikoEn + SmaEn, Utils.toFloat)
                PvInvertersAcEnergyForwardTotal = round(resultVar / 1000, 3)
                sensor_data.append(SensorData(System.RegEx, System.Label1, ["PvInvertersAcEnergyForwardTotal",], [PvInvertersAcEnergyForwardTotal,], DaySoFarTimeStamp))

                ###########################################################
                #self.log.info("_calcTotalEnergy: {}".format(sensor_data))
                ###########################################################
                self._writeEnergyToDb(self.influxHdlrDaily, sensor_data, '_calcTotalEnergy')

            except Exception as e:
                #print('_calcTotalEnergy: {}'.format(e))
                self.log.error("_calcTotalEnergy-1: {}".format(e))

    # # Ende Funktion: ' _calcTotalEnergy ' #####################################################

    # #################################################################################################
    # #  Funktion: '_calcPercentagey '
    ## 	\details
    #   \param[in]	-
    #   \return     -
    # #################################################################################################
        def _calcPercentage(self):

            try:
                timestamp = datetime.utcnow()
                SoFarTimeStamp = _conf.DAYSOFARTIMESTAMP.format(timestamp.year, timestamp.month, timestamp.day)
                AcConsumptionOnInputPower, AcBatt, AcPvOnGridPower, GridAcPower = self._getPowerForPercentage()
                self._calcConsumptionPercentage(AcPvOnGridPower, GridAcPower, AcBatt, SoFarTimeStamp)
                self._calcSolarPercentage(AcConsumptionOnInputPower, AcPvOnGridPower, GridAcPower, AcBatt, SoFarTimeStamp)

                # Stromausfall, dann über Raspi und Leuchte anzeigen
                IsConnected = self._getVal(self.influxHdlrDaily, "SELECT last(Connected) FROM grid where instance='Meter'", Grid.RegEx, 'last', '_calcPercentage')
                ###########################################################
                #self.log.info(f"Netz verbunden: {IsConnected}")
                ###########################################################

                fileName = "{}/GridLost.log".format('/mnt/dietpi_userdata/RaspiCooler')
                if (IsConnected > 0):
                    if ( os.path.exists(fileName)):
                        os.remove(fileName)
                else:
                    Utils._write_File(fileName, f'Verbunden: {IsConnected}\n', "w")

            except Exception as e:
                self.log.error("_calcPercentage-1: {}".format(e))

    # # Ende Funktion: ' _calcPercentagey ' #####################################################

    # #################################################################################################
    # #  Funktion: '_getPowerForPercentage '
    ## 	\details
    #   \param[in]	-
    #   \return     -
    # #################################################################################################
        def _getPowerForPercentage(self):

            AcConsumptionOnInputPower = float(0.0)
            Dc0Power = float(0.0)
            AcPvOnGridPower = float(0.0)
            GridAcPower = float(0.0)
            ConsPower1 = float(0.0)
            ConsPower2 = float(0.0)
            ConsPower3 = float(0.0)
            tmp = []
            bLen = False

            try:
                Dc0Power = self._getVal(self.influxHdlrDaily, _conf.Dc0Power, VeBus.RegEx, 'last', '_getPowerForPercentage')
                GridAcPower = self._getVal(self.influxHdlrDaily, _conf.AllPower, Grid.RegEx, 'last', '_getPowerForPercentage')
                AcPvOnGridPower = self._getVal(self.influxHdlrDaily, "SELECT last(AcPvOnGridPower) FROM system where instance='Gateway'", System.RegEx, 'last', '_getPowerForPercentage')

                tmp = self.influxHdlrDaily._Query_influxDb([_conf.LastL1Out, _conf.LastL2Out, _conf.LastL3Out], System.RegEx, 'last', '_getPowerForPercentage')
                if (len(tmp) == 3):
                    ConsPower1 = tmp[0]
                    ConsPower2 = tmp[1]
                    ConsPower3 = tmp[2]
                    bLen = True

                AcConsumptionOnInputPower, typ, length = Utils._check_Data_Type(ConsPower1 + ConsPower2 + ConsPower3, Utils.toFloat)

                #self.log.info(f'Dc0Power: {Dc0Power}; GridAcPower: {GridAcPower}; AcPvOnGridPower: {AcPvOnGridPower}')
                #self.log.info(f'ConsPower1: {ConsPower1}; ConsPower2: {ConsPower2}; ConsPower3: {ConsPower3}; AcConsumptionOnInputPower: {AcConsumptionOnInputPower}')

            except Exception as e:
                self.log.error("getPowerForPercentage-1: {}".format(e))
                self.log.error("tmp {}, Len == {}, Dc0Power {}, AcPvOnGridPower {}, GridAcPower {}".format(tmp, bLen, Dc0Power, AcPvOnGridPower, GridAcPower))

            except:
                self.log.error("getPowerForPercentage-2: {}".format(errLog))
                for info in sys.exc_info():
                    self.log.error("{}".format(info))

            return [AcConsumptionOnInputPower, Dc0Power, AcPvOnGridPower, GridAcPower]

    # # Ende Funktion: ' _getPowerForPercentage ' #####################################################

    # #################################################################################################
    # #  Funktion: '_calcConsumptionPercentage '
    ## 	\details 	Aufteilung Stromverbrauch nach Solar, Batterie, Netz
    #   \param[in]  AcPvOnGridPower
    #   \param[in]  GridAcPower
    #   \param[in]  AcBatt
    #   \param[in]  SoFarTimeStamp
    #   \return     -
    # #################################################################################################
        def _calcConsumptionPercentage(self, AcPvOnGridPower, GridAcPower, Dc0Power, timestamp):
            # Wenn Netz negativ wird eingespeist, aus Batterie oder Solar
            # Netz positiv, Strom wird gekauft
            try:
                GesamtPower = AcPvOnGridPower
                if (GridAcPower >= 0):
                    GesamtPower = GesamtPower + GridAcPower

                if (Dc0Power < 0):
                    GesamtPower = GesamtPower + abs(Dc0Power)

                if (GesamtPower > 0):
                    AcConsumptionFromPv = int(round(AcPvOnGridPower/GesamtPower*100))
                    AcConsumptionFromGrid = 0
                    if (GridAcPower >= 0):
                        AcConsumptionFromGrid = int(round(abs(GridAcPower)/GesamtPower*100))

                    AcConsumptionFromBatt = 0
                    if (Dc0Power < 0):    # Damit die prozentuale Aufteilung stimmt, da die BatteriePower immer mit Wirkungsgradverlusten behaftet ist
                        AcConsumptionFromBatt = int(round(abs(Dc0Power)/GesamtPower*100))

                else:
                    AcConsumptionFromPv = 0
                    AcConsumptionFromBatt = 0
                    AcConsumptionFromGrid = 0

                #self.log.info ("Gesamt Last Calc: {}\nAcBatt:{}\nPvGesamt:{}\nGridSumme:{}\n\n".format(GesamtPower, AcBatt, AcPvOnGridPower, GridAcPower))
                #self.log.info ("Solar: {}%".format(AcConsumptionFromPv))
                #self.log.info ("Batterie:{}%".format(AcConsumptionFromBatt))
                #self.log.info ("Netz: {}%\n".format(AcConsumptionFromGrid))

                sensor_data = []
                sensor_data.append(SensorData(System.RegEx, System.Label1, ['AcConsumptionFromPv',], [AcConsumptionFromPv,], timestamp))
                sensor_data.append(SensorData(System.RegEx, System.Label1, ['AcConsumptionFromBatt',], [AcConsumptionFromBatt,], timestamp))
                sensor_data.append(SensorData(System.RegEx, System.Label1, ['AcConsumptionFromGrid',], [AcConsumptionFromGrid,], timestamp))

                #self.log.info("_calcConsumptionPercentage: {}".format(sensor_data))
                self._writeEnergyToDb(self.influxHdlrDaily, sensor_data, '_calcConsumptionPercentage')

            except Exception as e:
                #print('_calcConsumptionPercentage: {}'.format(e))
                self.log.error("_calcConsumptionPercentage-1: {}".format(e))

    # # Ende Funktion: ' _calcConsumptionPercentage ' #################################################

    # #################################################################################################
    # #  Funktion: '_calcSolarPercentage '
    ## 	\details 	Aufteilung des Solarertrages nach Direktvebrauch, Batterieladen, einspeisen ins Netz
    #   \param[in]  AcConsumptionOnInputPower
    #   \param[in]  AcPvOnGridPower
    #   \param[in]  GridAcPower
    #   \param[in]  AcBatt
    #   \param[in]  SoFarTimeStamp
    #   \return     -
    # #################################################################################################
        def _calcSolarPercentage(self, AcConsumptionOnInputPower, AcPvOnGridPower, GridAcPower, Dc0Power, timestamp):

            try:
                # Wenn Solarertrag > Gesamtverbrauch, und Batterie lädt, bzw. nicht entladen wird, kann aufgeteilt werden
                PvPowerToLoad = 0
                PvPowerToBattery = 0
                PvPowerToGrid = 0
                if (AcPvOnGridPower > AcConsumptionOnInputPower) and (Dc0Power >= 0):
                    PvPowerToLoad = int(round(abs(AcConsumptionOnInputPower/AcPvOnGridPower*100)))
                    PvPowerToBattery = int(round(abs(Dc0Power/AcPvOnGridPower*100)))
                    PvPowerToGrid = int(round(abs(GridAcPower/AcPvOnGridPower*100)))

                # Solarertrag < Gesamtverbrauch und Batterie entlädt, 100% Direktverbrauch
                elif (AcPvOnGridPower < AcConsumptionOnInputPower) and (AcPvOnGridPower > 1):
                    PvPowerToLoad = 100

                #self.log.info (f"\nSolarertrag: {AcPvOnGridPower}\Dc0Power: {Dc0Power}\nNetzLast: {AcConsumptionOnInputPower}\nGridSumme: {GridAcPower}\nDirekt: {PvPowerToLoad}% = {AcConsumptionOnInputPower} / {AcPvOnGridPower} * 100\nBatterie:{PvPowerToBattery}% = {Dc0Power} / {AcPvOnGridPower} * 100\nNetz: {PvPowerToGrid}% = {GridAcPower} / {AcPvOnGridPower} * 100\n")

                if (PvPowerToGrid >= 100) and (PvPowerToLoad < 100):
                    PvPowerToGrid = 100 - PvPowerToBattery - PvPowerToLoad
                    #self.log.info (f"NetzKor: {PvPowerToGrid}% = {GridAcPower} / {AcPvOnGridPower} * 100")
                elif (PvPowerToLoad + PvPowerToBattery + PvPowerToGrid != 100) and (PvPowerToLoad > 0) and (PvPowerToBattery > 0) and (PvPowerToGrid > 0):
                    PvPowerToBattery = 100 - PvPowerToGrid - PvPowerToLoad
                    Dc0Power = AcPvOnGridPower * PvPowerToBattery / 100
                    #self.log.info (f"BatterieKor:{PvPowerToBattery}% = {Dc0Power} / {AcPvOnGridPower} * 100")

                sensor_data = []
                sensor_data.append(SensorData(System.RegEx, System.Label1, ['PvPowerToLoad',], [round(PvPowerToLoad, 1),], timestamp))
                sensor_data.append(SensorData(System.RegEx, System.Label1, ['PvPowerToBattery',], [round(PvPowerToBattery, 1),], timestamp))
                sensor_data.append(SensorData(System.RegEx, System.Label1, ['PvPowerToGrid',], [round(PvPowerToGrid, 1),], timestamp))

                #self.log.info("_calcSolarPercentage: {}".format(sensor_data))
                self._writeEnergyToDb(self.influxHdlrDaily, sensor_data, '_calcSolarPercentage')

            except Exception as e:
                #print('_calcSolarPercentage: {}'.format(e))
                self.log.error("_calcSolarPercentage-1: {}".format(e))

    # # Ende Funktion: ' _calcSolarPercentage ' #######################################################

    # #################################################################################################
    # #  Funktion: 'on_Raspi '
    ## \details     callback der mqtt Klasse zum loggen
    #   \param[in]     client
    #   \param[in]     userdata
    #   \param[in]     level
    #   \param[in]     buf
    #   \return         -
    # #################################################################################################
        def on_Raspi(self, obj, Raspi):

            timestamp = datetime.utcnow()
            timestamp = _conf.RASPITIMESTAMP.format(timestamp.year, timestamp.month)
            retVal = True

            _cpuLabel = 'Cpu'
            if (obj == 'GetBootTimeData'):
                self.log.debug('GetBootTimeData')
                bootTime = Raspi.GetBootTimeData()
                sensor_data = SensorData(_conf.HOST_INSTANCE, 'CpuInfo', ['BootTime',], [bootTime,], timestamp)
                retVal = self.influxHdlrDaily._send_sensor_data_to_influxdb(sensor_data, 'Raspi')

            if (obj == 'GetCpuInfoData'):
                self.log.debug('GetCpuInfoData')
                CpuInfo = Raspi.GetCpuInfoData()
                _typ = []
                _val = []
                for j, core in enumerate(CpuInfo.cores):
                    _typ.append('UsageCore{}'.format(j))
                    _val.append(core)

                _typ.extend(['PhysicalCores', 'TotalCores', 'MaxFreq', 'MinFreq', 'ActFreq', 'Usage', 'Temp', 'CaseTemp'])
                _val.extend([CpuInfo.physical, CpuInfo.total, CpuInfo.max, CpuInfo.min, CpuInfo.current, CpuInfo.usage, CpuInfo.temp, CpuInfo.DStemp])

                sensor_data = SensorData(_conf.HOST_INSTANCE, 'CpuInfo', _typ, _val, timestamp)
                retVal = self.influxHdlrDaily._send_sensor_data_to_influxdb(sensor_data, 'Raspi')

            if (obj == 'GetMemoryInfoData'):
                self.log.debug('GetMemoryInfoData')
                Memorys = Raspi.GetMemoryInfoData() # Werte in KB
                for ram in Memorys:
                    sensor_data = SensorData(_conf.HOST_INSTANCE, ram.device, ['Total', 'Used', 'Available', 'Percentage'], [ram.total, ram.used, ram.free, ram.percentage], timestamp)
                    retVal = self.influxHdlrDaily._send_sensor_data_to_influxdb(sensor_data, 'Raspi')
                    if (retVal != True):
                        break

            if (obj == 'GetDiskUsageData'):
                self.log.debug('GetDiskUsageData')
                Disks = Raspi.GetDiskUsageData() # Werte in KB
                for disk in Disks:
                    sensor_data = SensorData(_conf.HOST_INSTANCE, disk.device, ['Total', 'Used', 'Free', 'Percentage'], [disk.total, disk.used, disk.free, disk.percentage], timestamp)
                    retVal = self.influxHdlrDaily._send_sensor_data_to_influxdb(sensor_data, 'Raspi')
                    if (retVal != True):
                        break

            if (retVal != True):
                if (retVal == False):
                    self.log.warning("Fehler beim schreiben von Raspi: {}".format(sensor_data))

    # # Ende Funktion: 'on_Raspi ' ######################################################################

##### Fehlerbehandlung #####################################################
    except IOError as e:
        print('Eine der Bibliotheken konnte nicht geladen werden!\n{}!\n'.format(e))

    except:
        for info in sys.exc_info():
            print ("Fehler: {}".format(info))

# # Ende Klasse: ' CalcPer_CallBack ' ####################################################################

# # DateiEnde #####################################################################################
