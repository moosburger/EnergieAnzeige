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
# # Python Imports (Standard Library)
# #################################################################################################
try:
    ImportError = None
    import threading
    import time
    import datetime
    import sys

except Exception as e:
    ImportError = e

# #################################################################################################
# # Python Imports (site-packages)
# #################################################################################################

# #################################################################################################
# # private Imports
# #################################################################################################
try:
    PrivateImportError = None
    import Error
    import Utils
    import SunRiseSet

    from GetModbus import ModBusHandler
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

                ## Modbus Initialisieren
                self.mdbHdlr = ModBusHandler(logger = logger)
                self.SmaEn = {}
                self.PikoEn = {}
                self.IsNewDay = False

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

            try:
                self.log.info("Starte Berechnungen mit Intervall {} sek.".format(interval))
                ## Database initialisieren
                for i in range(10):
                    ver = self.influxHdlrDaily._init_influxdb_database(_conf.INFLUXDB_DATABASE, 'Calculations')
                    if (ver != None):
                        self.log.info('influxdb Version: {}'.format(ver))
                        break

                    time.sleep(5)

                for i in range(10):
                    ver = self.influxHdlrLong._init_influxdb_database(_conf.INFLUXDB_DATABASE_LONG, 'CalculationsMonth')
                    if (ver != None):
                        self.log.info('influxdb Version: {}'.format(ver))
                        break

                    time.sleep(5)

                # Beim Init verzögern, da kommen viele Daten vom mqtt Broker
                time.sleep(interval)
                time.sleep(interval)

                while True:
                    time.sleep(interval / 5)
                    self.SmaEn = self.mdbHdlr.FetchSmaData(3)
                    #self.log.info('SmaEn: {}'.format(self.SmaEn ))
                    self.PikoEn = self.mdbHdlr.FetchPikoData(126)
                    #self.log.info('PikoEn: {}'.format(self.PikoEn ))
                    self._calcTotalEnergy()
                    time.sleep(interval / 5)
                    self._calcPercentage()
                    time.sleep(interval / 5)
                    self._calcDailyEnergySoFar()
                    time.sleep(interval / 5)
                    self._calcMonthlyEnergySoFar()
                    time.sleep(interval / 5)
                    self._calcYearlyEnergySoFar()

            except:
                for info in sys.exc_info():
                    self.log.error("Fehler: {}".format(info))
                    print("Fehler: {}".format(info))

    # # Ende Funktion: ' run ' ###############################################################################

    # #################################################################################################
    # #  Funktion: '_check_Data_Type '
    ## 	\details    -
    #   \param[in] 	myVal
    #   \return 	myVal
    # #################################################################################################
        def _check_Data_Type(self, myVal):

            #float, int, str, list, dict, tuple
            if (isinstance(myVal, str)):
                pass
            elif (isinstance(myVal, int)):
                myVal = float(myVal)
            elif (isinstance(myVal, float)):
                myVal = float(myVal)
            else:
                myVal = str(myVal)

            return myVal

    # # Ende Funktion: '_check_Data_Type ' ############################################################

    # #################################################################################################
    # #  Funktion: '_prepareData '
    ## 	\details    -
    #   \param[in] 	myVal
    #   \return 	myVal
    # #################################################################################################
        def _prepareData(self, influxHandler, QUERY, Instance, Unit, where, TargetVar, timestamp):

            resultVar, = influxHandler._Query_influxDb([QUERY,], Instance, where)
            resultVar = self._check_Data_Type(resultVar)

            return(SensorData(Instance, Unit, [TargetVar,], [resultVar,], timestamp))

    # # Ende Funktion: '_check_Data_Type ' ############################################################

    # #################################################################################################
    # #  Funktion: '_getVal '
    ## 	\details    -
    #   \param[in] 	myVal
    #   \return 	myVal
    # #################################################################################################
        def _getVal(self, influxHandler, QUERY, Instance, where):

            resultVar, = influxHandler._Query_influxDb([QUERY,], Instance, where)
            resultVar = self._check_Data_Type(resultVar)

            return resultVar

    # # Ende Funktion: '_getVal ' ############################################################

    # #################################################################################################
    # #  Funktion: '_EnergyPerDay '
    ## 	\details    Abhaengig von den Parametern die Summe des letzten monats oder des letzten Jahres
    #   \param[in] 	sensor_data_day_list
    #   \return 	-
    # #################################################################################################
        def _writeEnergyToDb(self, influxHandler, sensor_data_day_list):

            retVal = False
            errLog = ''
            try:
                for sensor_data in sensor_data_day_list:
                    errLog = sensor_data
                    retVal = influxHandler._send_sensor_data_to_influxdb(sensor_data)

            except Exception as e:
                self.log.error("writeEnergyToDb: {}".format(e))

            except:
                self.log.error("{}".format(errLog))
                for info in sys.exc_info():
                    self.log.error("{}".format(info))
                    #print ("Fehler: {}".format(info))

            if (retVal == False):
                self.log.warning("Fehler beim schreiben von {}".format(sensor_data))
                ## Database initialisieren
                #influxHandler._init_influxdb_database(_conf.INFLUXDB_DATABASE, 'Calculations')

    # # Ende Funktion: '_EnergyPerDay ' ###############################################################

    # #################################################################################################
    # #  Funktion: '_calcDailyEnergySoFar '
    ## 	\details
    #   \param[in]	-
    #   \return     -
    # #################################################################################################
        def _calcDailyEnergySoFar(self):

            try:
                sensor_data = []
                AMh, AMm, UMh, UMm, lt_tag, lt_monat, lt_jahr, lt_h, lt_m, lt_s = SunRiseSet.get_Info()
                sunRise = AMh  * 60 + AMm
                sunSet  = UMh  * 60 + UMm
                localNow  = lt_h * 60 + lt_m

                DaySoFarTimeStamp = _conf.DAYSOFARTIMESTAMP.format(lt_jahr, lt_monat, lt_tag)
                #print(sunRise)
                #print(sunSet)
                #print(localNow)
                if (localNow > sunSet):
                    self.IsNewDay = False
                    #print("Nacht")
                    return

                if (localNow < sunRise):
                    if (self.IsNewDay == False):
                        sensor_data.append(SensorData(PvInv.RegEx, PvInv.Label1, ["AcEnergyForwardDaySoFar",], [0.0,], DaySoFarTimeStamp))
                        sensor_data.append(SensorData(PvInv.RegEx, PvInv.Label2, ["AcEnergyForwardDaySoFar",], [0.0,], DaySoFarTimeStamp))
                        sensor_data.append(SensorData(System.RegEx, System.Label1, ["PvInvertersAcEnergyForwardDaySoFar",], [0.0,], DaySoFarTimeStamp))
                        self.log.info("_calcDailyEnergySoFar NEW DAY: {}".format(sensor_data))
                        self._writeEnergyToDb(self.influxHdlrDaily, sensor_data)
                    self.IsNewDay = True
                    return

                PikoEn = round(self._check_Data_Type(self.PikoEn['40670'] / 1000), 3)
                sensor_data.append(SensorData(PvInv.RegEx, PvInv.Label2, ["AcEnergyForwardDaySoFar",], [PikoEn,], DaySoFarTimeStamp))
                SmaEn = round(self._check_Data_Type(self.SmaEn['30535'] / 1000), 3)
                sensor_data.append(SensorData(PvInv.RegEx, PvInv.Label1, ["AcEnergyForwardDaySoFar",], [SmaEn,], DaySoFarTimeStamp))
                PvInvertersAcEnergyForwardDaySoFar = round(self._check_Data_Type(PikoEn + SmaEn), 3)
                sensor_data.append(SensorData(System.RegEx, System.Label1, ["PvInvertersAcEnergyForwardDaySoFar",], [PvInvertersAcEnergyForwardDaySoFar,], DaySoFarTimeStamp))

                #self.log.info("_calcDailyEnergySoFar: {}".format(sensor_data))
                self._writeEnergyToDb(self.influxHdlrDaily, sensor_data)

            except Exception as e:
                #print('_calcDailyEnergySoFar: {}'.format(e))
                self.log.error("_calcDailyEnergySoFar: {}".format(e))

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
                if (datetime.datetime.day == 1) and (self.IsInitWritten2 == False):
                    self.IsNewMonth = True

                if (datetime.datetime.day == 2):
                    self.IsInitWritten2 = False

                AMh, AMm, UMh, UMm, lt_tag, lt_monat, lt_jahr, lt_h, lt_m, lt_s = SunRiseSet.get_Info()
                sunRise = AMh  * 60 + AMm
                sunSet  = UMh  * 60 + UMm
                localNow  = lt_h * 60 + lt_m

                MonthTimeStamp = _conf.MONTHTIMESTAMP.format(lt_jahr, lt_monat)
                MonthSoFarTimeStamp = _conf.MONTHSOFARTIMESTAMP.format(lt_jahr, lt_monat)
                #print(sunRise)
                #print(sunSet)
                #print(localNow)
                if (localNow > sunSet):
                    self.IsNewDay2 = True
                    #print("Nacht")
                    return

                if (localNow < sunRise):
                    if (self.IsNewMonth == True):
                        sensor_data.append(SensorData(PvInv.RegEx, PvInv.Label2, ["AcEnergyForwardMonth",], [0.0,], MonthTimeStamp))
                        sensor_data.append(SensorData(PvInv.RegEx, PvInv.Label1, ["AcEnergyForwardMonth",], [0.0,], MonthTimeStamp))
                        sensor_data.append(SensorData(System.RegEx, System.Label1, ["PvInvertersAcEnergyForwardMonth",], [0.0,], MonthTimeStamp))
                        sensor_data.append(SensorData(PvInv.RegEx, PvInv.Label2, ["AcEnergyForwardMonthSoFar",], [0.0,], MonthSoFarTimeStamp))
                        sensor_data.append(SensorData(PvInv.RegEx, PvInv.Label1, ["AcEnergyForwardMonthSoFar",], [0.0,], MonthSoFarTimeStamp))
                        sensor_data.append(SensorData(System.RegEx, System.Label1, ["PvInvertersAcEnergyForwardMonthSoFar",], [0.0,], MonthSoFarTimeStamp))

                        self.log.info("_calcMonthlyEnergySoFar NEW MONTH: {}".format(sensor_data))
                        self._writeEnergyToDb(self.influxHdlrLong, sensor_data)
                        self.IsInitWritten2 = True
                    self.IsNewMonth = False

                    if (self.IsNewDay2 == True):
                        PIKO_ENERGY = "SELECT (AcEnergyForwardMonthSoFar) FROM pvinverter where instance='PIKO' and time >= {}".format(MonthSoFarTimeStamp)
                        sensor_data.append(self._prepareData(self.influxHdlrLong, PIKO_ENERGY, PvInv.RegEx, PvInv.Label2, 'AcEnergyForwardMonthSoFar', 'AcEnergyForwardMonth', MonthTimeStamp))

                        SMA_ENERGY = "SELECT (AcEnergyForwardMonthSoFar) FROM pvinverter where instance='SMA' and time >= {}".format(MonthSoFarTimeStamp)
                        sensor_data.append(self._prepareData(self.influxHdlrLong, SMA_ENERGY, PvInv.RegEx, PvInv.Label1, 'AcEnergyForwardMonthSoFar', 'AcEnergyForwardMonth', MonthTimeStamp))

                        SYSTEM_ENERGY = "SELECT (PvInvertersAcEnergyForwardMonthSoFar) FROM system where instance='Gateway' and time >= {}".format(MonthSoFarTimeStamp)
                        sensor_data.append(self._prepareData(self.influxHdlrLong, SYSTEM_ENERGY, System.RegEx, System.Label1, 'PvInvertersAcEnergyForwardMonthSoFar', 'PvInvertersAcEnergyForwardMonth', MonthTimeStamp))

                        self.log.info("_calcMonthlyEnergySoFar NEW DAY: {}".format(sensor_data))
                        self._writeEnergyToDb(self.influxHdlrLong, sensor_data)
                    self.IsNewDay2 = False
                    return

                PIKO_ENERGY = "SELECT (AcEnergyForwardMonth) FROM pvinverter where instance='PIKO' and time >= {}".format(MonthTimeStamp)
                AcEnergyForwardMonth = self._getVal(self.influxHdlrLong, PIKO_ENERGY, PvInv.RegEx, 'AcEnergyForwardMonth')

                PikoEn = round(self._check_Data_Type(self.PikoEn['40670'] / 1000), 3)
                AcEnergyForwardMonthSoFar = round(AcEnergyForwardMonth + PikoEn, 3)
                sensor_data.append(SensorData(PvInv.RegEx, PvInv.Label2, ["AcEnergyForwardMonthSoFar",], [AcEnergyForwardMonthSoFar,], MonthSoFarTimeStamp))

                ###########################################################
                #self.log.info("PIKO AcEnergyForwardMonth : {}".format(AcEnergyForwardMonth))
                #self.log.info("PIKO self.PikoEn['40670'] : {}".format(self.PikoEn['40670']))
                #self.log.info("PIKO PikoEn : {}".format(PikoEn))
                ###########################################################

                SMA_ENERGY = "SELECT (AcEnergyForwardMonth) FROM pvinverter where instance='SMA' and time >= {}".format(MonthTimeStamp)
                AcEnergyForwardMonth = self._getVal(self.influxHdlrLong, SMA_ENERGY, PvInv.RegEx, 'AcEnergyForwardMonth')

                SmaEn = round(self._check_Data_Type(self.SmaEn['30535'] / 1000), 3)
                AcEnergyForwardMonthSoFar = round(AcEnergyForwardMonth + SmaEn, 3)
                sensor_data.append(SensorData(PvInv.RegEx, PvInv.Label1, ["AcEnergyForwardMonthSoFar",], [AcEnergyForwardMonthSoFar,], MonthSoFarTimeStamp))

                ###########################################################
                #self.log.info("SMA AcEnergyForwardMonth : {}".format(AcEnergyForwardMonth))
                #self.log.info("SMA self.SmaEn['30535'] : {}".format(self.SmaEn['30535']))
                #self.log.info("SMA SmaEn : {}".format(SmaEn))
                ###########################################################

                SYSTEM_ENERGY = "SELECT (PvInvertersAcEnergyForwardMonth) FROM system where instance='Gateway' and time >= {}".format(MonthTimeStamp)
                PvInvertersAcEnergyForwardMonth = self._getVal(self.influxHdlrLong, SYSTEM_ENERGY, System.RegEx, 'PvInvertersAcEnergyForwardMonth')

                PvInvertersAcEnergyForwardMonthSoFar = round(PvInvertersAcEnergyForwardMonth + PikoEn + SmaEn, 3)
                sensor_data.append(SensorData(System.RegEx, System.Label1, ["PvInvertersAcEnergyForwardMonthSoFar",], [PvInvertersAcEnergyForwardMonthSoFar,], MonthSoFarTimeStamp))

                ###########################################################
                #self.log.info("_calcMonthlyEnergySoFar: {}".format(sensor_data))
                ###########################################################
                self._writeEnergyToDb(self.influxHdlrLong, sensor_data)

            except Exception as e:
                #print('_calcMonthlyEnergySoFar: {}'.format(e))
                self.log.error("_calcMonthlyEnergySoFar: {}".format(e))

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
                if (datetime.datetime.day == 1) and (datetime.datetime.month == 1) and (self.IsInitWritten3 == False):
                    self.IsNewYear = True

                if (datetime.datetime.day == 2) and (datetime.datetime.month == 1):
                    self.IsInitWritten3 = False

                AMh, AMm, UMh, UMm, lt_tag, lt_monat, lt_jahr, lt_h, lt_m, lt_s = SunRiseSet.get_Info()
                sunRise = AMh  * 60 + AMm
                sunSet  = UMh  * 60 + UMm
                localNow  = lt_h * 60 + lt_m

                YearTimeStamp = _conf.YEARTIMESTAMP.format(lt_jahr)
                YearSoFarTimeStamp = _conf.YEARSOFARTIMESTAMP.format(lt_jahr)
                #print(sunRise)
                #print(sunSet)
                #print(localNow)
                if (localNow > sunSet):
                    self.IsNewDay3 = True
                    #print("Nacht")
                    return

                if (localNow < sunRise):
                    if (self.IsNewYear == True):
                        sensor_data.append(SensorData(PvInv.RegEx, PvInv.Label2, ["AcEnergyForwardYear",], [0.0,], YearTimeStamp))
                        sensor_data.append(SensorData(PvInv.RegEx, PvInv.Label1, ["AcEnergyForwardYear",], [0.0,], YearTimeStamp))
                        sensor_data.append(SensorData(System.RegEx, System.Label1, ["PvInvertersAcEnergyForwardYear",], [0.0,], YearTimeStamp))
                        sensor_data.append(SensorData(PvInv.RegEx, PvInv.Label2, ["AcEnergyForwardYearSoFar",], [0.0,], YearSoFarTimeStamp))
                        sensor_data.append(SensorData(PvInv.RegEx, PvInv.Label1, ["AcEnergyForwardYearSoFar",], [0.0,], YearSoFarTimeStamp))
                        sensor_data.append(SensorData(System.RegEx, System.Label1, ["PvInvertersAcEnergyForwardYearSoFar",], [0.0,], YearSoFarTimeStamp))

                        self.log.info("_calcYearlyEnergySoFar NEW YEAR: {}".format(sensor_data))
                        self._writeEnergyToDb(self.influxHdlrLong, sensor_data)
                        self.IsInitWritten3 = True
                    self.IsNewYear = False

                    if (self.IsNewDay3 == True):
                        PIKO_ENERGY = "SELECT (AcEnergyForwardYearSoFar) FROM pvinverter where instance='PIKO' and time >= {}".format(YearSoFarTimeStamp)
                        sensor_data.append(self._prepareData(self.influxHdlrLong, PIKO_ENERGY, PvInv.RegEx, PvInv.Label2, 'AcEnergyForwardYearSoFar', 'AcEnergyForwardYear', YearTimeStamp))

                        SMA_ENERGY = "SELECT (AcEnergyForwardYearSoFar) FROM pvinverter where instance='SMA' and time >= {}".format(YearSoFarTimeStamp)
                        sensor_data.append(self._prepareData(self.influxHdlrLong, SMA_ENERGY, PvInv.RegEx, PvInv.Label1, 'AcEnergyForwardYearSoFar', 'AcEnergyForwardYear', YearTimeStamp))

                        SYSTEM_ENERGY = "SELECT (PvInvertersAcEnergyForwardYearSoFar) FROM system where instance='Gateway' and time >= {}".format(YearSoFarTimeStamp)
                        sensor_data.append(self._prepareData(self.influxHdlrLong, SYSTEM_ENERGY, System.RegEx, System.Label1, 'PvInvertersAcEnergyForwardYearSoFar', 'PvInvertersAcEnergyForwardYear', YearTimeStamp))

                        self.log.info("_calcYearlyEnergySoFar NEW DAY: {}".format(sensor_data))
                        self._writeEnergyToDb(self.influxHdlrLong, sensor_data)
                    self.IsNewDay3 = False
                    return

                PIKO_ENERGY = "SELECT (AcEnergyForwardYear) FROM pvinverter where instance='PIKO' and time >= {}".format(YearTimeStamp)
                AcEnergyForwardYear = self._getVal(self.influxHdlrLong, PIKO_ENERGY, PvInv.RegEx, 'AcEnergyForwardYear')

                PikoEn = round(self._check_Data_Type(self.PikoEn['40670'] / 1000), 3)
                AcEnergyForwardYearSoFar = round(AcEnergyForwardYear + PikoEn, 3)
                sensor_data.append(SensorData(PvInv.RegEx, PvInv.Label2, ["AcEnergyForwardYearSoFar",], [AcEnergyForwardYearSoFar,], YearSoFarTimeStamp))

                ###########################################################
                #self.log.info("PIKO AcEnergyForwardYear : {}".format(AcEnergyForwardYear))
                #self.log.info("PIKO self.PikoEn['40670'] : {}".format(self.PikoEn['40670']))
                #self.log.info("PIKO PikoEn : {}".format(PikoEn))
                ###########################################################

                SMA_ENERGY = "SELECT (AcEnergyForwardYear) FROM pvinverter where instance='SMA' and time >= {}".format(YearTimeStamp)
                AcEnergyForwardYear = self._getVal(self.influxHdlrLong, SMA_ENERGY, PvInv.RegEx, 'AcEnergyForwardYear')

                SmaEn = round(self._check_Data_Type(self.SmaEn['30535'] / 1000), 3)
                AcEnergyForwardYearSoFar = round(AcEnergyForwardYear + SmaEn, 3)
                sensor_data.append(SensorData(PvInv.RegEx, PvInv.Label1, ["AcEnergyForwardYearSoFar",], [AcEnergyForwardYearSoFar,], YearSoFarTimeStamp))

                ###########################################################
                #self.log.info("SMA AcEnergyForwardYear : {}".format(AcEnergyForwardYear))
                #self.log.info("SMA self.SmaEn['30535'] : {}".format(self.SmaEn['30535']))
                #self.log.info("SMA SmaEn : {}".format(SmaEn))
                ###########################################################

                SYSTEM_ENERGY = "SELECT (PvInvertersAcEnergyForwardYear) FROM system where instance='Gateway' and time >= {}".format(YearTimeStamp)
                PvInvertersAcEnergyForwardYear = self._getVal(self.influxHdlrLong, SYSTEM_ENERGY, System.RegEx, 'PvInvertersAcEnergyForwardYear')

                PvInvertersAcEnergyForwardYearSoFar = round(PvInvertersAcEnergyForwardYear + PikoEn + SmaEn, 3)
                sensor_data.append(SensorData(System.RegEx, System.Label1, ["PvInvertersAcEnergyForwardYearSoFar",], [PvInvertersAcEnergyForwardYearSoFar,], YearSoFarTimeStamp))

                ###########################################################
                #self.log.info("_calcYearlyEnergySoFar: {}".format(sensor_data))
                ###########################################################
                self._writeEnergyToDb(self.influxHdlrLong, sensor_data)

            except Exception as e:
                #print('_calcYearlyEnergySoFar: {}'.format(e))
                self.log.error("_calcYearlyEnergySoFar: {}".format(e))

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
                AMh, AMm, UMh, UMm, lt_tag, lt_monat, lt_jahr, lt_h, lt_m, lt_s = SunRiseSet.get_Info()
                sunRise = AMh  * 60 + AMm
                sunSet  = UMh  * 60 + UMm
                localNow  = lt_h * 60 + lt_m
                DaySoFarTimeStamp = _conf.DAYSOFARTIMESTAMP.format(lt_jahr, lt_monat, lt_tag)
                if ((localNow > sunSet) or (localNow < sunRise)):
                    return

                PikoEn = round(self._check_Data_Type(self.PikoEn['40210'] / 1000), 3)
                sensor_data.append(SensorData(PvInv.RegEx, PvInv.Label2, ["AcEnergyForwardTotal",], [PikoEn,], DaySoFarTimeStamp))

                SmaEn = round(self._check_Data_Type(self.SmaEn['30529'] / 1000), 3)
                sensor_data.append(SensorData(PvInv.RegEx, PvInv.Label1, ["AcEnergyForwardTotal",], [SmaEn,], DaySoFarTimeStamp))

                PvInvertersAcEnergyForwardTotal = round(self._check_Data_Type(PikoEn + SmaEn), 3)
                sensor_data.append(SensorData(System.RegEx, System.Label1, ["PvInvertersAcEnergyForwardTotal",], [PvInvertersAcEnergyForwardTotal,], DaySoFarTimeStamp))

                #self.log.info("_calcTotalEnergy: {}".format(sensor_data))
                self._writeEnergyToDb(self.influxHdlrDaily, sensor_data)

            except Exception as e:
                #print('_calcTotalEnergy: {}'.format(e))
                self.log.error("_calcTotalEnergy: {}".format(e))

    # # Ende Funktion: ' _calcTotalEnergy ' #####################################################

    # #################################################################################################
    # #  Funktion: '_calcPercentagey '
    ## 	\details
    #   \param[in]	-
    #   \return     -
    # #################################################################################################
        def _calcPercentage(self):

            try:
                timestamp = datetime.datetime.utcnow()
                SoFarTimeStamp = _conf.DAYSOFARTIMESTAMP.format(timestamp.year, timestamp.month, timestamp.day)
                AcConsumptionOnInputPower, AcBatt, AcPvOnGridPower, GridAcPower = self._getPowerForPercentage()
                self._calcConsumptionPercentage(AcPvOnGridPower, GridAcPower, AcBatt, SoFarTimeStamp)
                self._calcSolarPercentage(AcConsumptionOnInputPower, AcPvOnGridPower, GridAcPower, AcBatt, SoFarTimeStamp)

            except Exception as e:
                #print('_calcPercentage: {}'.format(e))
                self.log.error("_calcPercentage: {}".format(e))

    # # Ende Funktion: ' _calcPercentagey ' #####################################################

    # #################################################################################################
    # #  Funktion: '_getPowerForPercentage '
    ## 	\details
    #   \param[in]	-
    #   \return     -
    # #################################################################################################
        def _getPowerForPercentage(self):

            AcConsumptionOnInputPower = 0.0
            AcBatt = 0.0
            AcPvOnGridPower = 0.0
            GridAcPower = 0.0
            try:
                ConsPower1, ConsPower2, ConsPower3 = self.influxHdlrDaily._Query_influxDb([_conf.LastL1, _conf.LastL2, _conf.LastL3], System.RegEx, 'last')
                AcConsumptionOnInputPower = self._check_Data_Type(ConsPower1 + ConsPower2 + ConsPower3)
                AcBatt, = self.influxHdlrDaily._Query_influxDb([_conf.AcBattPower,], VeBus.RegEx, 'last')
                AcPvOnGridPower, = self.influxHdlrDaily._Query_influxDb(["SELECT last(AcPvOnGridPower) FROM system where instance='Gateway'",], System.RegEx, 'last')
                GridAcPower, = self.influxHdlrDaily._Query_influxDb([_conf.AllPower,], Grid.RegEx, 'last')

            except Exception as e:
                self.log.error("getPowerForPercentage: {}".format(e))

            except:
                self.log.error("getPowerForPercentage: {}".format(errLog))
                for info in sys.exc_info():
                    self.log.error("{}".format(info))

            return [AcConsumptionOnInputPower, AcBatt, AcPvOnGridPower, GridAcPower]

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
        def _calcConsumptionPercentage(self, AcPvOnGridPower, GridAcPower, AcBatt, timestamp):
            # Wenn Netz negativ wird eingespeist, aus Batterie oder Solar
            # Netz positiv, Strom wird gekauft
            try:
                GesamtPower = AcPvOnGridPower
                if (GridAcPower >= 0):
                    GesamtPower = GesamtPower + GridAcPower

                if (AcBatt < 0):
                    GesamtPower = GesamtPower + abs(AcBatt)

                if (GesamtPower > 0):
                    AcConsumptionFromPv = int(round(AcPvOnGridPower/GesamtPower*100))
                    AcConsumptionFromGrid = 0
                    if (GridAcPower >= 0):
                        AcConsumptionFromGrid = int(round(abs(GridAcPower)/GesamtPower*100))

                    AcConsumptionFromBatt = 0
                    if (AcBatt < 0):    # Damit die prozentuale Aufteilng stimmt, da die BatteriePower immer mit Wirkungsgradverlusten behaftet ist
                        AcConsumptionFromBatt = int(round(abs(AcBatt)/GesamtPower*100))

                else:
                    AcConsumptionFromPv = 0
                    AcConsumptionFromBatt = 0
                    AcConsumptionFromGrid = 0

                #self.log.info ("Gesamt Last Calc: {} (AcBatt:{} + PvGesamt:{} + GridSumme:{})".format(GesamtPower, AcBatt, AcPvOnGridPower, GridAcPower))
                #self.log.info ("Solar: {}%".format(AcConsumptionFromPv))
                #self.log.info ("Batterie:{}%".format(AcConsumptionFromBatt))
                #self.log.info ("Netz: {}%\n".format(AcConsumptionFromGrid))

                sensor_data = []
                sensor_data.append(SensorData(System.RegEx, System.Label1, ['AcConsumptionFromPv',], [AcConsumptionFromPv,], timestamp))
                sensor_data.append(SensorData(System.RegEx, System.Label1, ['AcConsumptionFromBatt',], [AcConsumptionFromBatt,], timestamp))
                sensor_data.append(SensorData(System.RegEx, System.Label1, ['AcConsumptionFromGrid',], [AcConsumptionFromGrid,], timestamp))

                #self.log.info("_calcConsumptionPercentage: {}".format(sensor_data))
                self._writeEnergyToDb(self.influxHdlrDaily, sensor_data)

            except Exception as e:
                #print('_calcConsumptionPercentage: {}'.format(e))
                self.log.error("_calcConsumptionPercentage: {}".format(e))

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
        def _calcSolarPercentage(self, AcConsumptionOnInputPower, AcPvOnGridPower, GridAcPower, AcBatt, timestamp):

            try:
                # Wenn Solarertrag > Gesamtverbrauch, und Batterie lädt, bzw. nicht entladen wird, kann aufgeteilt werden
                PvPowerToLoad = 0
                PvPowerToBattery = 0
                PvPowerToGrid = 0
                if (AcPvOnGridPower > AcConsumptionOnInputPower) and (AcBatt >= 0):
                    PvPowerToLoad = int(round(abs(AcConsumptionOnInputPower/AcPvOnGridPower*100)))
                    PvPowerToBattery = int(round(abs(AcBatt/AcPvOnGridPower*100)))
                    PvPowerToGrid = int(round(abs(GridAcPower/AcPvOnGridPower*100)))

                # Solarertrag < Gesamtverbrauch und Batterie entlädt, 100% Direktverbrauch
                elif (AcPvOnGridPower < AcConsumptionOnInputPower) and (AcPvOnGridPower > 1):
                    PvPowerToLoad = 100

                #self.log.info ("Solarertrag: {}\nAcBatt:{}\nNetzLast:{}\nGridSumme:{}\n\n".format(AcPvOnGridPower, AcBatt, AcConsumptionOnInputPower, GridAcPower))
                #self.log.info ("Direkt: {}%".format(PvPowerToLoad))
                #self.log.info ("Batterie:{}%%".format(PvPowerToBattery))
                #self.log.info ("Netz: {}%\n".format(PvPowerToGrid))

                sensor_data = []
                sensor_data.append(SensorData(System.RegEx, System.Label1, ['PvPowerToLoad',], [round(PvPowerToLoad, 1),], timestamp))
                sensor_data.append(SensorData(System.RegEx, System.Label1, ['PvPowerToBattery',], [round(PvPowerToBattery, 1),], timestamp))
                sensor_data.append(SensorData(System.RegEx, System.Label1, ['PvPowerToGrid',], [round(PvPowerToGrid, 1),], timestamp))

                #self.log.info("_calcSolarPercentage: {}".format(sensor_data))
                self._writeEnergyToDb(self.influxHdlrDaily, sensor_data)

            except Exception as e:
                #print('_calcSolarPercentage: {}'.format(e))
                self.log.error("_calcSolarPercentage: {}".format(e))

    # # Ende Funktion: ' _calcSolarPercentage ' #######################################################

##### Fehlerbehandlung #####################################################
    except IOError as e:
        print('Eine der Bibliotheken konnte nicht geladen werden!\n{}!\n'.format(e))

    except:
        for info in sys.exc_info():
            print ("Fehler: {}".format(info))

# # Ende Klasse: ' CalcPer_CallBack ' ####################################################################

# # DateiEnde #####################################################################################
