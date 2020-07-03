#!/usr/bin/env python
# -*- coding: utf-8 -*-

# #################################################################################################
## \brief     Exportiert Daten im Csv und SolarLog Format
#  \details
#  \file      dataExport.py
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
    import os
    import threading
    import time
    import datetime
    from configuration import Global as _conf, PvInverter as PvInv, Grid, Battery, VeBus, System
    from influxHandler import influxIO, _SensorData as SensorData

except:
    raise

reload(sys)
sys.setdefaultencoding("utf-8")

# #################################################################################################
# # Python Imports (site-packages)
# #################################################################################################

# #################################################################################################
# # private Imports
# #################################################################################################
try:
    PrivateImport = True
    import Error
    import Utils
    import SunRiseSet

except ImportError as e:
    raise

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
# # Classes: KeepAlive
## \details Pingt in regelmässigen Abständen den Vrm Mqtt Broker an
# https://dev.to/hasansajedi/running-a-method-as-a-background-process-in-python-21li
# #################################################################################################
class ExportDataFromInflux(object):

# #################################################################################################
# # Funktion: ' Constructor '
##  \details 	Die Initialisierung der Klasse KeepAlive
#   \param[in]  self der Objectpointer
#   \param[in]  interval
#   \param[in] 	logger
#   \return -
# #################################################################################################
    def __init__(self, interval, logger):

        self.log = logger.getLogger('ExportData')
        self.influxHdlr = influxIO(_host = _conf.INFLUXDB_ADDRESS, _port = _conf.INFLUXDB_PORT, _username = _conf.INFLUXDB_USER, _password = _conf.INFLUXDB_PASSWORD, _database = None, _gzip = _conf.INFLUXDB_ZIPPED, logger = logger)
        thread = threading.Thread(target=self.main, args=(interval, ))
        thread.daemon = True
        thread.start()

# # Ende Funktion: ' Constructor ' ################################################################

# #################################################################################################
# # Funktion: ' Destructor '
# #################################################################################################
    #def __del__(self):

# # Ende Funktion: ' Destructor ' #################################################################

# #################################################################################################
# #  Funktion: '_Get_Energy_Piko '
## 	\details
#   \param[in]
#   \return 	PikoEn
# #################################################################################################
    def _Get_Energy_Piko(self):

        Piko1, Piko2, Piko3 = self.influxHdlr._Query_influxDb([_conf.PIKO_ENERGY1,_conf.PIKO_ENERGY2,_conf.PIKO_ENERGY3], PvInv.RegEx, 'last')
        PikoEn = self._check_Data_Type(Piko1 + Piko2 + Piko3)

        return PikoEn

# # Ende Funktion: '_Get_Energy_Piko ' ############################################################

# #################################################################################################
# #  Funktion: '_Get_Energy_Sma '
## 	\details
#   \param[in]
#   \return 	SmaEn
# #################################################################################################
    def _Get_Energy_Sma(self):

        Sma1, Sma2, Sma3 = self.influxHdlr._Query_influxDb([_conf.SMA_ENERGY1,_conf.SMA_ENERGY2,_conf.SMA_ENERGY3], PvInv.RegEx, 'last')
        SmaEn = self._check_Data_Type(Sma1 + Sma2 + Sma3)

        return SmaEn

# # Ende Funktion: '_Get_Energy_Sma ' #############################################################

# #################################################################################################
# #  Funktion: '_check_Data_Type '
## 	\details    -
#   \param[in] 	myVal
#   \return 	myVal
# #################################################################################################
    def _check_Data_Type(self, myVal):

        #float, int, str, list, dict, tuple
        if (isinstance(myVal, basestring)):
            pass
        elif (isinstance(myVal, int)):
            myVal = float(myVal)
        elif (isinstance(myVal, long)):
            myVal = float(myVal)
        elif (isinstance(myVal, float)):
            myVal = float(myVal)
        else:
            myVal = str(myVal)

        return myVal

# # Ende Funktion: '_check_Data_Type ' ############################################################

# #################################################################################################
# #  Funktion: '_EnergyPerDay '
## 	\details    Abhaengig von den Parametern die Summe des letzten monats oder des letzten Jahres
#   \param[in] 	sensor_data_day_list
#   \return 	-
# #################################################################################################
    def _WriteEnergyToDb(self, sensor_data_day_list):

        for sensor_data in sensor_data_day_list:
            retVal = self.influxHdlr._send_sensor_data_to_influxdb(sensor_data)
            if (retVal == False):
                self.log.warning("Fehler beim schreiben von {}".format(sensor_data))

# # Ende Funktion: '_EnergyPerDay ' ###############################################################

# #################################################################################################
# #  Funktion: '_EnergyPerMonth '
## 	\details	Abhaengig von den Parametern die Summe des letzten monats oder des letzten Jahres
#   \param[in] 	toDay
#   \param[in] 	sensor_data
#   \return 	sensor_data
# #################################################################################################
    def _EnergyPerMonth(self, toDay, sensor_data):

        sensor_data = []
        Tage, Monat, Jahr, TageMonat = Utils.monthdelta(toDay, -1, False)      # Am 1. Januar ist das Monats Delta 1 um ins alte Jahr zu kommen
        timeRange = "time > '{0}-{1:02d}-01T00:00:00.0Z' and time < '{0}-{1:02d}-{2:02d}T23:59:59.9Z'".format(Jahr, Monat, TageMonat)
        PvQuery = 'AcEnergyForwardPerDay'
        PvTarget = 'AcEnergyForwardPerMonth'
        SystemQuery = 'PvInvertersAcEnergyForwardPerDay'
        SystemTarget = 'PvInvertersAcEnergyForwardPerMonth'

        sensor_data.extend(self._EnergySum(timeRange, PvQuery, PvTarget, SystemQuery, SystemTarget, Jahr, Monat, Monat, TageMonat))
        return sensor_data

# # Ende Funktion: '_EnergyPerMonth ' #############################################################

# #################################################################################################
# #  Funktion: '_EnergyPerYear '
## 	\details    Abhaengig von den Parametern die Summe des letzten monats oder des letzten Jahres
#   \param[in] 	toDay
#   \param[in] 	sensor_data
#   \return 	sensor_data
# #################################################################################################
    def _EnergyPerYear(self, toDay, sensor_data):

        Tage, Monat, Jahr, TageMonat = Utils.monthdelta(toDay, -1, False)      # Am 1. Januar ist das Monats Delta 1 um ins alte Jahr zu kommen
        timeRange = "time > '{0}-01-01T00:00:00.0Z' and time < '{0}-{1:02d}-{2:02d}T23:59:59.9Z'".format(Jahr, Monat, TageMonat)
        PvQuery = 'AcEnergyForwardPerMonth'
        PvTarget = 'AcEnergyForwardPerYear'
        SystemQuery = 'PvInvertersAcEnergyForwardPerMonth'
        SystemTarget = 'PvInvertersAcEnergyForwardPerYear'
        EndMonat = 12
        Monat = 01

        sensor_data.extend(self._EnergySum(timeRange, PvQuery, PvTarget, SystemQuery, SystemTarget, Jahr, Monat, EndMonat, TageMonat))
        return sensor_data

# # Ende Funktion: '_EnergyPerYear ' ##############################################################

# #################################################################################################
# #  Funktion: '_EnergySum '
## 	\details 	Abhaengig von den Parametern die Summe des letzten monats oder des letzten Jahres
#   \param[in] 	toDay
#   \param[in] 	timeRange
#   \param[in] 	PvQuery
#   \param[in] 	PvTarget
#   \param[in] 	SystemQuery
#   \param[in] 	SystemTarget
#   \param[in] 	Jahr
#   \param[in] 	Monat
#   \param[in] 	TageMonat
#   \return 	sensor_data
# #################################################################################################
    def _EnergySum(self, timeRange, PvQuery, PvTarget, SystemQuery, SystemTarget, Jahr, Monat, EndMonat, TageMonat):

        sensor_data = []
        print timeRange
        starttimestamp = "'{0}-{1:02d}-01T01:00:00.0Z'".format(Jahr, Monat)
        endtimestamp = "'{0}-{1:02d}-{2:02d}T21:00:00.0Z'".format(Jahr, Monat, EndMonat, TageMonat)
        SMA_ENERGY = "SELECT ({}) FROM pvinverter where instance='{}' and {}".format(PvQuery, PvInv.Label1, timeRange)
        PIKO_ENERGY = "SELECT ({}) FROM pvinverter where instance='{}' and {}".format(PvQuery, PvInv.Label2, timeRange)

        SmaList  = self.influxHdlr._Query_influxDb([SMA_ENERGY,], PvInv.RegEx, PvQuery)
        PikoList = self.influxHdlr._Query_influxDb([PIKO_ENERGY,], PvInv.RegEx, PvQuery)

        PikoTotal = 0.0
        step = len(PikoList)/12
        if (step < 1):
            step = 1
        for PikoEnergy in PikoList[::step]:
            PikoTotal = PikoTotal + float(PikoEnergy)

        SmaTotal = 0.0
        step = len(SmaList)/12
        if (step < 1):
            step = 1
        for SmaEnergy in SmaList[::step]:
            SmaTotal = SmaTotal + float(SmaEnergy)

        sensor_data.append(SensorData(PvInv.RegEx, PvInv.Label2, [PvTarget,], [round(PikoTotal),], starttimestamp))
        sensor_data.append(SensorData(PvInv.RegEx, PvInv.Label2, [PvTarget,], [round(PikoTotal),], endtimestamp))
        sensor_data.append(SensorData(PvInv.RegEx, PvInv.Label1, [PvTarget,], [round(SmaTotal),], starttimestamp))
        sensor_data.append(SensorData(PvInv.RegEx, PvInv.Label1, [PvTarget,], [round(SmaTotal),], endtimestamp))

        PV_TOTAL_ENERGY = "SELECT ({}) FROM system where instance='{}' and {}".format(SystemQuery, System.Label1, timeRange)
        PvInverterList = self.influxHdlr._Query_influxDb([PV_TOTAL_ENERGY,], System.RegEx, SystemQuery)

        Total = 0.0
        step = len(PvInverterList)/12
        if (step < 1):
            step = 1
        for Energy in PvInverterList[::step]:
            Total = Total + float(Energy)

        sensor_data.append(SensorData(System.RegEx, System.Label1, [SystemTarget,], [round(Total),], starttimestamp))
        sensor_data.append(SensorData(System.RegEx, System.Label1, [SystemTarget,], [round(Total),], endtimestamp))

        return sensor_data

# # Ende Funktion: '_check_Data_Type ' ############################################################

# #################################################################################################
# #  Funktion: '_get_Enery '
## 	\details
#   \param[in] 	timestamp
#   \return          -
# #################################################################################################
    def _get_Enery(self):

        sensor_data = []
        timestamp = datetime.datetime.utcnow()

        # Aktuelle Gesamtenergie Piko
        PikoEn = self._Get_Energy_Piko()
        sensor_data.append(SensorData(PvInv.RegEx, PvInv.Label2, ["AcEnergyForwardTotal",], [PikoEn,], timestamp))

        # Aktuelle Gesamtenergie SMA
        SmaEn = self._Get_Energy_Sma()
        sensor_data.append(SensorData(PvInv.RegEx, PvInv.Label1, ["AcEnergyForwardTotal",], [SmaEn,], timestamp))

        # Gesamtenergie Piko und SMA gestern
        PikoLastDayTotal, SmaLastDayTotal = self.influxHdlr._Query_influxDb([_conf.PIKO_ENERGY_LASTDAY,_conf.SMA_ENERGY_LASTDAY], PvInv.RegEx, 'last')

        PikoAcEnergyForwardPerDay = PikoEn - PikoLastDayTotal  # 18207,76 - 19,751  kWh
        SmaAcEnergyForwardPerDay = SmaEn - SmaLastDayTotal     # 4344,58 - 0
        PvInvertersAcEnergyForwardPerDay = PikoAcEnergyForwardPerDay + SmaAcEnergyForwardPerDay
        PvInvertersAcEnergyForwardTotal = PikoEn + SmaEn
        sensor_data.append(SensorData(System.RegEx, System.Label1, ["PvInvertersAcEnergyForwardTotal",], [PvInvertersAcEnergyForwardTotal,], timestamp))
        # aktuelle Energie bis jetzt
        sensor_data.append(SensorData(System.RegEx, System.Label1, ["PvInvertersAcEnergyForwardDay",], [PvInvertersAcEnergyForwardPerDay,], timestamp))

        sensor_data_day = []
        #GesamtEnergie am heutigen Tag für Sma, Piko
        sensor_data_day.append(SensorData(PvInv.RegEx, PvInv.Label2, ["AcEnergyForwardDay",], [PikoEn,], timestamp))
        sensor_data_day.append(SensorData(PvInv.RegEx, PvInv.Label1, ["AcEnergyForwardDay",], [SmaEn,], timestamp))

        # TagesEnergie für Sma, Piko, Beide gesamt
        sensor_data_day.append(SensorData(PvInv.RegEx, PvInv.Label2, ["AcEnergyForwardPerDay",], [PikoAcEnergyForwardPerDay,], timestamp))
        sensor_data_day.append(SensorData(PvInv.RegEx, PvInv.Label1, ["AcEnergyForwardPerDay",], [SmaAcEnergyForwardPerDay,], timestamp))
        sensor_data_day.append(SensorData(System.RegEx, System.Label1, ["PvInvertersAcEnergyForwardPerDay",], [PvInvertersAcEnergyForwardPerDay,], timestamp))

        toDay = datetime.date.today()
        yesterDay = datetime.date(2020,6,21)
        if (yesterDay == toDay):
            self.log.info("Piko AcEnergyForwardDay: {}".format(PikoEn))
            self.log.info("Sma AcEnergyForwardDay: {}".format(SmaEn))

            self.log.info("Piko AcEnergyForwardPerDay: {}".format(PikoAcEnergyForwardPerDay))
            self.log.info("Sma AcEnergyForwardPerDay: {}".format(SmaAcEnergyForwardPerDay))
            self.log.info("Sma PvInvertersAcEnergyForwardPerDay: {}".format(PvInvertersAcEnergyForwardPerDay))

        return [PvInvertersAcEnergyForwardPerDay, PvInvertersAcEnergyForwardTotal, sensor_data, sensor_data_day]

# # Ende Funktion: ' _get_Enery ' #################################################################

# #################################################################################################
# #  Funktion: '_get_PUI '
## 	\details
#   \param[in]	-
#   \return     -
# #################################################################################################
    def _get_PUI(self):

        # Aktuelle Spannungen und Ströme Piko
        Piko_U1, Piko_U2, Piko_U3, Piko_I1, Piko_I2, Piko_I3 = self.influxHdlr._Query_influxDb([_conf.PIKO_VL1,_conf.PIKO_VL2,_conf.PIKO_VL3, _conf.PIKO_IL1, _conf.PIKO_IL2, _conf.PIKO_IL3], PvInv.RegEx, 'last')

        # Aktuelle Spannungen und Ströme Sma
        Sma_U1, Sma_U2, Sma_U3, Sma_I1, Sma_I2, Sma_I3 = self.influxHdlr._Query_influxDb([_conf.SMA_VL1,_conf.SMA_VL2,_conf.SMA_VL3, _conf.SMA_IL1, _conf.SMA_IL2, _conf.SMA_IL3], PvInv.RegEx, 'last')

        # GesamtStröme je Phase
        Ges_I1 = int((Piko_I1 + Sma_I1) * 1000)
        Ges_I2 = int((Piko_I2 + Sma_I2) * 1000)
        Ges_I3 = int((Piko_I3 + Sma_I3) * 1000)

        U1 = Piko_U1 if Sma_U1 < Piko_U1 else Sma_U1
        U2 = Piko_U2 if Sma_U2 < Piko_U2 else Sma_U2
        U3 = Piko_U3 if Sma_U3 < Piko_U3 else Sma_U3

        # Aktuelle Gesamtleistung je Phase
        Ges_P1, Ges_P2, Ges_P3 = self.influxHdlr._Query_influxDb([_conf.PvOnGridL1,_conf.PvOnGridL2,_conf.PvOnGridL3], System.RegEx, 'last')
        PAC = int(round(Ges_P1 + Ges_P2 + Ges_P3))

        return [int(round(U1)), Ges_I1, int(round(Ges_P1)), int(round(U2)), Ges_I2, int(round(Ges_P2)), int(round(U3)), Ges_I3, int(round(Ges_P3)), PAC]

# # Ende Funktion: ' _get_PUI ' ###################################################################

# #################################################################################################
# #  Funktion: '_calcPercentagey '
## 	\details
#   \param[in]	-
#   \return     -
# #################################################################################################
    def _calcPercentage(self):

        timestamp = datetime.datetime.utcnow()
        AcConsumptionOnInputPower, AcBatt, AcPvOnGridPower, GridAcPower = self._getPowerForPercentage()
        self._calcConsumptionPercentage(AcPvOnGridPower, GridAcPower, AcBatt, timestamp)
        self._calcSolarPercentage(AcConsumptionOnInputPower, AcPvOnGridPower, GridAcPower, AcBatt, timestamp)

# # Ende Funktion: ' _calcPercentagey ' #####################################################

# #################################################################################################
# #  Funktion: '_getPowerForPercentage '
## 	\details
#   \param[in]	-
#   \return     -
# #################################################################################################
    def _getPowerForPercentage(self):

        ConsPower1, ConsPower2, ConsPower3 = self.influxHdlr._Query_influxDb([_conf.LastL1, _conf.LastL2, _conf.LastL3], System.RegEx, 'last')
        AcConsumptionOnInputPower = self._check_Data_Type(ConsPower1 + ConsPower2 + ConsPower3)
        AcBatt, = self.influxHdlr._Query_influxDb([_conf.AcBattPower,], VeBus.RegEx, 'last')
        AcPvOnGridPower, = self.influxHdlr._Query_influxDb(["SELECT last(AcPvOnGridPower) FROM system where instance='Gateway'",], System.RegEx, 'last')
        GridAcPower, = self.influxHdlr._Query_influxDb([_conf.AllPower,], Grid.RegEx, 'last')

        return [AcConsumptionOnInputPower, AcBatt, AcPvOnGridPower, GridAcPower]

# # Ende Funktion: ' _getPowerForPercentage ' #####################################################

# #################################################################################################
# #  Funktion: '_calcConsumptionPercentage '
## 	\details 	Aufteilung Stromverbrauch nach Solar, Batterie, Netz
#   \param[in]  AcPvOnGridPower
#   \param[in]  GridAcPower
#   \param[in]  AcBatt
#   \param[in]  timestamp
#   \return     -
# #################################################################################################
    def _calcConsumptionPercentage(self, AcPvOnGridPower, GridAcPower, AcBatt, timestamp):
        # Wenn Netz negativ wird eingespeist, aus Batterie oder Solar
        # Netz positiv, Strom wird gekauft

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

        self._WriteEnergyToDb(sensor_data)

# # Ende Funktion: ' _calcConsumptionPercentage ' #################################################

# #################################################################################################
# #  Funktion: '_calcSolarPercentage '
## 	\details 	Aufteilung des Solarertrages nach Direktvebrauch, Batterieladen, einspeisen ins Netz
#   \param[in]  AcConsumptionOnInputPower
#   \param[in]  AcPvOnGridPower
#   \param[in]  GridAcPower
#   \param[in]  AcBatt
#   \param[in]  timestamp
#   \return     -
# #################################################################################################
    def _calcSolarPercentage(self, AcConsumptionOnInputPower, AcPvOnGridPower, GridAcPower, AcBatt, timestamp):

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
        sensor_data.append(SensorData(System.RegEx, System.Label1, ['PvPowerToLoad',], [PvPowerToLoad,], timestamp))
        sensor_data.append(SensorData(System.RegEx, System.Label1, ['PvPowerToBattery',], [PvPowerToBattery,], timestamp))
        sensor_data.append(SensorData(System.RegEx, System.Label1, ['PvPowerToGrid',], [PvPowerToGrid,], timestamp))

        self._WriteEnergyToDb(sensor_data)

# # Ende Funktion: ' _calcSolarPercentage ' #######################################################

# #################################################################################################
# #  Funktion: '_prepare_Csv_Header '
## 	\details
#   \param[in]	toDay
#   \return     -
# #################################################################################################
    def _prepare_Csv_Header(self, toDay):

        csvStream = ("Datum: {}\n".format(toDay.strftime('%d.%m.%y'))) \
                    + "WR-Nr;Name;Typ;Serien-Nr;Strings;Leistung;\n" \
                    + "1;{};WR;{};2;{};\n".format('NAME', 'SERIENNUMMER', 'LEISTUNG') \
                    + "Einheiten: U[V], I[mA], P[W], E[kWh], Ain [mV]\n" \
                    + "Zeit;WR-Nr;DC1 U;DC1 I;DC1 P;DC2 U;DC2 I;DC2 P;DC3 U;DC3 I;DC3 P;AC1 U;AC1 I;AC1 P;AC2 U;AC2 I;AC2 P;AC3 U;AC3 I;AC3 P;Ain1;Ain2;Ain3;Ain4;Tages E;Total E;Tages E Out;Total E Out;Tages E In;Total E In;\n"

        return csvStream

# # Ende Funktion: ' _prepare_Csv_Header ' ########################################################

# #################################################################################################
# #  Funktion: '_write_days_hist '
## 	\details
#   \param[in] 	Zeit
#   \param[in]  PvInvertersAcEnergyForwardPerDay
#   \return     -
# #################################################################################################
    def _write_days_hist(self, Zeit, PacMax, PvInvertersAcEnergyForwardPerDay):

        days_hist = ('da[dx++]="{}.{}.{}|{};{}"\r\n'.format(Zeit.strftime("%d"), Zeit.strftime("%m"), Zeit.strftime("%y"), int(round(PvInvertersAcEnergyForwardPerDay*1000)), PacMax))

        dataRead = ''
        with open(_conf.EXPORT_FILEPATH + "days_hist.js", "r") as f:
            dataRead = f.read()

        f.close()

        with open(_conf.EXPORT_FILEPATH + "days_hist.js", "w") as f:
            days_hist = "{}{}".format(days_hist, dataRead)
            f.write (days_hist)
            f.flush()

        f.close()

# # Ende Funktion: ' _write_days_hist ' ###########################################################

# #################################################################################################
# #  Funktion: '_write_File '
## 	\details
#   \param[in] 	strFile
#   \param[in]  txtStream
#   \param[in]  oType
#   \return     -
# #################################################################################################
    def _write_File(self, strFile, txtStream, oType):

        with open(strFile, oType) as f:
            f.write (txtStream)
            f.flush()

        f.close()

# # Ende Funktion: ' _write_File ' ################################################################

# #################################################################################################
# #  Funktion: ' _main '
## 	\details 	Die Einsprungsfunktion, ruft alle Funktionen und Klassen auf.
#   \return     -
# #################################################################################################
    def main(self, interval):

        while True:

            try:
                ## Import fehlgeschlagen
                if (PrivateImport == False):
                    raise ImportError

                self.log.info("ExportPfad: {} Intervall {} sek.".format(_conf.EXPORT_FILEPATH, interval))

            ## Database initialisieren
                self.influxHdlr._init_influxdb_database(_conf.INFLUXDB_DATABASE)

                # Datum initialisieren
                yesterDay = datetime.date(2000,1,2)
                PacMax = 0
                bFirstRun = True
                bDays_hist_written = False
                bOnceMore = True
                bMonat = False
                bYear = False

                # Programm
                while True:
                    toDay = datetime.date.today()

                    FolderYear = toDay.strftime('[%Y]')
                    strFolder = os.path.join(_conf.EXPORT_FILEPATH, FolderYear)
                    csvFile = toDay.strftime('%Y%m%d.csv')
                    strFile = os.path.join(strFolder, csvFile)
                    PacMax = 0

                    # Neues Jahr
                    if (yesterDay.year < toDay.year) and (bFirstRun == True):
                        bYear = True

                    # Neuer Monat
                    if (yesterDay.month < toDay.month) and (bFirstRun == True):
                        bMonat = True

                    # Neuer Tag
                    if (yesterDay < toDay) and (not os.path.exists(strFile)):
                        yesterDay = toDay
                        bDays_hist_written = False
                        bOnceMore = True

                        if (not os.path.exists(strFolder)):
                            os.mkdir(strFolder)

                    ## Csv Stream zusammenbauen
                        csvStream = self._prepare_Csv_Header(toDay)
                        self._write_File(strFile, csvStream, "w")

            ##### Prozentuale Aufteilung des Verbrauches und des Solarertrages #############
                    self._calcPercentage()

            ##### Warten bis die Zeit vergeht ##############################################
                    time.sleep(int(interval/2))    # das Intervall ist 120 sek. die prozentuale aufteilung dann alle 60
            ##### Warten bis die Zeit vergeht ##############################################

            ##### Prozentuale Aufteilung des Verbrauches und des Solarertrages #############
                    self._calcPercentage()

            ##### Tagsueber oder nachts ####################################################
                    AMh, AMm, UMh, UMm, lt_tag, lt_monat, lt_jahr, lt_h, lt_m, lt_s = SunRiseSet.get_Info()
                    sunRise = AMh  * 60 + AMm
                    sunSet  = UMh  * 60 + UMm
                    localNow  = lt_h * 60 + lt_m
                    if ((localNow < sunRise) or (localNow > sunSet)) and (bDays_hist_written == True) and (bOnceMore == False):
                        # Ausrechnen wie lange in den Sleep zu schicken bis morgen SunRise ( da nehmen wir den heutigen Wert zum Rechnen)
                        #  Tag hat 86400 sek.
                        #time.sleep(86400 - localNow * 60 + sunRise * 60)
                        continue
            ################################################################################

                ## Aktuelle Tages und Gesamtenergieen
                    PvInvertersAcEnergyForwardPerDay, PvInvertersAcEnergyForwardTotal, sensor_data_list, sensor_data_day_list = self._get_Enery()
                    self._WriteEnergyToDb(sensor_data_list)

                ## Aktuelle Gesamtleistung je Phase, sowie einzel Spannung und Strom
                    Pv_U1, Ges_I1, Ges_P1, Pv_U2, Ges_I2, Ges_P2, Pv_U3, Ges_I3, Ges_P3, PAC = self._get_PUI()
                    if (PacMax < PAC):
                        PacMax = PAC

                ## Dc Werte müssen evtl gefaket werden, wenn Werte in der Csv nötig sein sollten
                    ##

            ##### Logging der Daten ####################################################
                    Zeit = datetime.datetime.now()
                ## Wenn eine Spannung > 0 ist, die Daten rausloggen
                    if (Pv_U1 > 0) or (Pv_U2 > 0) or (Pv_U3 > 0) or (Ges_P1 > 0) or (Ges_P2 > 0) or (Ges_P3 > 0) or (bOnceMore == True):
                    ## Csv Stream in Datei schreiben
                        datStream = "{:02d}:{:02d}:{:02d};1;0;0;0;0;0;0;0;0;0;{};{};{};{};{};{};{};{};{};0;0;0;0;{:.3f};{:.3f};0.000;0.000;0.000;0.000;\n". \
                                    format(Zeit.hour, Zeit.minute, Zeit.second, Pv_U1, Ges_I1, Ges_P1, Pv_U2, Ges_I2, Ges_P2, Pv_U3, Ges_I3, Ges_P3, PvInvertersAcEnergyForwardPerDay, PvInvertersAcEnergyForwardTotal)
                        self._write_File(strFile, datStream, "a")

                    ## days.js
                        self._write_File(_conf.EXPORT_FILEPATH + "days.js", 'da[dx++]="{}.{}.{}|{};{}"'.format(Zeit.day, Zeit.month, Zeit.year, int(round(PvInvertersAcEnergyForwardPerDay*1000)), PacMax), "wt")

                        if (Pv_U1 == 0) and (Pv_U2 == 0) and (Pv_U3 == 0):
                            bOnceMore = False

                ## days_hist.js
                    ShutDowntime = datetime.time(UMh, UMm - 5, 00)  # 5 min vor Sonnenuntergang
                    actTime = datetime.time(Zeit.hour, Zeit.minute, Zeit.second)
                    ## Die Zeit ist UTC also 21 entspricht 23 MEZ Berlin
                    if ((actTime > ShutDowntime) and (bDays_hist_written == False)):
                    ## Die Tagesenergie aufsummiern zu Monat
                        if (bMonat):
                            bMonat = False
                            self.log.info("Monatswerte")
                            sensor_data_day_list.extend(self._EnergyPerMonth(toDay, sensor_data_day_list))

                    ## Die Monatsenergien zum Jahr
                        if (bYear):
                            bYear = False
                            self.log.info("Jahreswerte")
                            sensor_data_day_list.extend(self._EnergyPerYear(toDay, sensor_data_day_list))

                    ## Die Tagesenergie
                        self._WriteEnergyToDb(sensor_data_day_list)
                        bDays_hist_written = True
                        self._write_days_hist(Zeit, PacMax, PvInvertersAcEnergyForwardPerDay)

                    bFirstRun = False

            ##### Fehlerbehandlung #####################################################
            except NameError as e:
                self.log.error("VariablenFehler: {}".format(e))

            except IOError as e:
                self.log.error("IOError: {}".format(e))
                #print 'IOError'

            except:
                for info in sys.exc_info():
                    self.log.error("Fehler: {}".format(info))
                    #print ("Fehler: {}".format(info))

# # Ende Funktion: ' _main' #######################################################################

# #################################################################################################
# #  Funktion: 'Einsprung beim Aufruf  '
# #################################################################################################
#if __name__ == '__init__':

    #__init__()

# # DateiEnde #####################################################################################

