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
import sys
import os
import threading
import time
import logging
import datetime
from configuration import Global as _conf, PvInverter as PvInv, Grid, Battery, VeBus, System
from influxHandler import influxIO, _SensorData as SensorData

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
except:
    PrivateImport = False

# #################################################################################################
# # UmgebungsVariablen / Globals
# #################################################################################################

# #################################################################################################
# # Logging geht in dieselbe Datei, trotz verschiedener Prozesse!
# #################################################################################################
log = logging.getLogger('ExportDataFromInflux')
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
## \details Die Initialisierung der Klasse KeepAlive
#   \param[in]  self der Objectpointer
#   \param[in]  interval
#   \param[in]  mqttClient
#   \param[in] portal_id
#   \return -
# #################################################################################################
    def __init__(self, interval):

        self.influxHdlr = influxIO(_host = _conf.INFLUXDB_ADDRESS, _port = _conf.INFLUXDB_PORT, _username = _conf.INFLUXDB_USER, _password = _conf.INFLUXDB_PASSWORD, _database = None, _gzip = _conf.INFLUXDB_ZIPPED)
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
## \details
#   \param[in]
#   \return
# #################################################################################################
    def _Get_Energy_Piko(self):

        Piko1, Piko2, Piko3 = self.influxHdlr._Query_influxDb([_conf.PIKO_ENERGY1,_conf.PIKO_ENERGY2,_conf.PIKO_ENERGY3], PvInv.RegEx, 'last')
        PikoEn = self._check_Data_Type(Piko1 + Piko2 + Piko3)

        return PikoEn

# # Ende Funktion: '_Get_Energy_Piko ' ######################################################################

# #################################################################################################
# #  Funktion: '_Get_Energy_Sma '
## \details
#   \param[in]
#   \return
# #################################################################################################
    def _Get_Energy_Sma(self):

        Sma1, Sma2, Sma3 = self.influxHdlr._Query_influxDb([_conf.SMA_ENERGY1,_conf.SMA_ENERGY2,_conf.SMA_ENERGY3], PvInv.RegEx, 'last')
        SmaEn = self._check_Data_Type(Sma1 + Sma2 + Sma3)

        return SmaEn

# # Ende Funktion: '_Get_Energy_Sma ' ######################################################################

# #################################################################################################
# #  Funktion: '_check_Data_Type '
## \details     -
#   \return
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

# # Ende Funktion: '_check_Data_Type ' ######################################################################

# #################################################################################################
# #  Funktion: '_get_Enery '
## \details
#   \param[in]     -
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

        sensor_data_day = []
        #GesamtEnergie am heutigen Tag für Sma, Piko
        sensor_data_day.append(SensorData(PvInv.RegEx, PvInv.Label2, ["AcEnergyForwardDay",], [PikoEn,], timestamp))
        sensor_data_day.append(SensorData(PvInv.RegEx, PvInv.Label1, ["AcEnergyForwardDay",], [SmaEn,], timestamp))

        # TagesEnergie für Sma, Piko, Beide gesamt
        sensor_data_day.append(SensorData(PvInv.RegEx, PvInv.Label2, ["AcEnergyForwardPerDay",], [PikoAcEnergyForwardPerDay,], timestamp))
        sensor_data_day.append(SensorData(PvInv.RegEx, PvInv.Label1, ["AcEnergyForwardPerDay",], [SmaAcEnergyForwardPerDay,], timestamp))
        sensor_data_day.append(SensorData(System.RegEx, System.Label1, ["PvInvertersAcEnergyForwardPerDay",], [PvInvertersAcEnergyForwardPerDay,], timestamp))

        return [PvInvertersAcEnergyForwardPerDay, PvInvertersAcEnergyForwardTotal, sensor_data, sensor_data_day]

# # Ende Funktion: ' _get_Enery ' #################################################################

# #################################################################################################
# #  Funktion: '_get_PUI '
## \details
#   \param[in]     -
#   \return          -
# #################################################################################################
    def _get_PUI(self):

        # Aktuelle Spannungen und Ströme Piko
        Piko_U1, Piko_U2, Piko_U3, Piko_I1, Piko_I2, Piko_I3 = self.influxHdlr._Query_influxDb([_conf.PIKO_VL1,_conf.PIKO_VL2,_conf.PIKO_VL3, _conf.PIKO_IL1, _conf.PIKO_IL2, _conf.PIKO_IL3], PvInv.RegEx, 'last')

        # Aktuelle Spannungen und Ströme Sma
        Sma_U1, Sma_U2, Sma_U3, Sma_I1, Sma_I2, Sma_I3 = self.influxHdlr._Query_influxDb([_conf.SMA_VL1,_conf.SMA_VL2,_conf.SMA_VL3, _conf.SMA_IL1, _conf.SMA_IL2, _conf.SMA_IL3], PvInv.RegEx, 'last')

        # GesamtStröme je Phase
        Ges_I1 = round(Piko_I1 + Sma_I1) * 1000
        Ges_I2 = round(Piko_I2 + Sma_I2) * 1000
        Ges_I3 = round(Piko_I3 + Sma_I3) * 1000

        # Aktuelle Gesamtleistung je Phase
        Ges_P1, Ges_P2, Ges_P3 = self.influxHdlr._Query_influxDb([_conf.PvOnGridL1,_conf.PvOnGridL2,_conf.PvOnGridL3], System.RegEx, 'last')
        PAC = round(Ges_P1 + Ges_P2 + Ges_P3)

        return [round(Piko_U1), Ges_I1, round(Ges_P1), round(Piko_U2), Ges_I2, round(Ges_P2), round(Piko_U3), Ges_I3, round(Ges_P3), PAC]

# # Ende Funktion: ' _get_PUI ' #################################################################

# #################################################################################################
# #  Funktion: '_prepare_Csv_Header '
## \details
#   \param[in]     toDay
#   \return          -
# #################################################################################################
    def _prepare_Csv_Header(self, toDay):

        csvStream = ("Datum: {}\n".format(toDay.strftime('%d.%m.%y'))) \
                    + "WR-Nr;Name;Typ;Serien-Nr;Strings;Leistung;\n" \
                    + "1;{};WR;{};2;{};\n".format('NAME', 'SERIENNUMMER', 'LEISTUNG') \
                    + "Einheiten: U[V], I[mA], P[W], E[kWh], Ain [mV]\n" \
                    + "Zeit;WR-Nr;DC1 U;DC1 I;DC1 P;DC2 U;DC2 I;DC2 P;DC3 U;DC3 I;DC3 P;AC1 U;AC1 I;AC1 P;AC2 U;AC2 I;AC2 P;AC3 U;AC3 I;AC3 P;Ain1;Ain2;Ain3;Ain4;Tages E;Total E;Tages E Out;Total E Out;Tages E In;Total E In;\n"

        return csvStream

# # Ende Funktion: ' _prepare_Csv_Header ' #################################################################

# #################################################################################################
# #  Funktion: '_write_File '
## \details
#   \param[in]     -
#   \return          -
# #################################################################################################
    def _write_File(self, strFile, txtStream, oType):

        try:
            with open(strFile, oType) as f:
                f.write (txtStream)
                f.close()

        except IOError as e:
            log.error("IOError: {}".format(e.msg))

# # Ende Funktion: ' _write_File ' #################################################################

# #################################################################################################
# #  Funktion: ' _main '
## \details         Die Einsprungsfunktion, ruft alle Funktionen und Klassen auf.
#   \return            -
# #################################################################################################
    def main(self, interval):

        try:
            log.info("Starte Export mit Intervall {} sek.".format(interval))
            log.info("ExportPfad: {}".format(_conf.EXPORT_FILEPATH))

            ## Import fehlgeschlagen
            if (PrivateImport == False):
                raise ImportError

        ## Database initialisieren
            self.influxHdlr._init_influxdb_database(_conf.INFLUXDB_DATABASE)

            # Datum initialisieren
            yesterDay = datetime.date(2000,1,2)
            PacMax = 0
            days_hist_written = False

            # Programm
            while True:
                Zeit = datetime.datetime.now()
            ## Csv Stream zusammenbauen
                toDay = datetime.date.today()

                FolderYear = toDay.strftime('[%Y]')
                strFolder = os.path.join(_conf.EXPORT_FILEPATH, FolderYear)
                csvFile = toDay.strftime('%Y%m%d.csv')
                strFile = os.path.join(strFolder, csvFile)

                if (yesterDay < toDay):
                    yesterDay = toDay
                    days_hist_written = False

                    if (not os.path.exists(strFolder)):
                        os.mkdir(strFolder)

                    csvStream = self._prepare_Csv_Header(toDay)
                    self._write_File(strFile, csvStream, "wt")

            ## Tagsüber oder nachts
                AMh, AMm, UMh, UMm, lt_tag, lt_monat, lt_jahr, lt_h, lt_m, lt_s = SunRiseSet.get_Info()
                sunRise = AMh  * 60 + AMm
                sunSet  = UMh  * 60 + UMm
                localNow  = lt_h * 60 + lt_m

                if ((localNow < sunRise) or (localNow > sunSet)) and (days_hist_written == True):
                    # Ausrechnen wie lange in den Sleep zu schicken bis morgen SunRise ( da nehmen wir den heutigen Wert zum Rechnen)
                    #  Tag hat 86400 sek.
                    time.sleep(86400 - localNow * 60 + sunRise * 60)
                    continue

            ## Aktuelle Tages und Gesamteenergieen
                PvInvertersAcEnergyForwardPerDay, PvInvertersAcEnergyForwardTotal, sensor_data_list, sensor_data_day_list = self._get_Enery()
                for sensor_data in sensor_data_list:
                    retVal = self.influxHdlr._send_sensor_data_to_influxdb(sensor_data)
                    if (retVal == False):
                        log.warning("Fehler beim schreiben von {}".format(sensor_data))

            ## Aktuelle Gesamtleistung je Phase, sowie einzel Spannung und Strom
                Piko_U1, Ges_I1, Ges_P1, Piko_U2, Ges_I2, Ges_P2, Piko_U3, Ges_I3, Ges_P3, PAC = self._get_PUI()
                if (PacMax < PAC):
                    PacMax = PAC

            ## Dc Werte müssen evtl gefaket werden, wenn Werte in der Csv nötig sein sollten
                #

            ## Csv Stream in Datei schreiben
                datStream = "{:02d}:{:02d}:{:02d};1;0;0;0;0;0;0;0;0;0;{};{};{};{};{};{};{};{};{};0;0;0;0;{};{};0;0;0;0;\n". \
                            format(Zeit.hour, Zeit.minute, Zeit.second, Piko_U1, Ges_I1, Ges_P1, Piko_U2, Ges_I2, Ges_P2, Piko_U3, Ges_I3, Ges_P3, round(PvInvertersAcEnergyForwardPerDay), round(PvInvertersAcEnergyForwardTotal))
                self._write_File(strFile, datStream, "at")

            ## days.js
                self._write_File(_conf.EXPORT_FILEPATH + "days.js", 'da[dx++]="{}.{}.{}|{};{}"'.format(Zeit.day, Zeit.month, Zeit.year, round(PvInvertersAcEnergyForwardPerDay*1000), PacMax), "wt")

            ## days_hist.js
                ShutDowntime = datetime.time(UMh, UMm - 5, 00)  # 5 min vor Sonnenuntergang
                actTime = datetime.time(Zeit.hour, Zeit.minute, Zeit.second)
                ##  /Ac/Energy/Forward täglich um 21h abspeichern, dann differenz zum diesem Wert ist tägliche Energie. um 23h abspeichern, dann Monat (30Tage evtl), dann Jahr
                ## Die Zeit ist UTC also 21 entspricht 23 MEZ Berlin
                if ((actTime > ShutDowntime) and (days_hist_written == False)):
                    for sensor_data in sensor_data_day_list:
                        retVal = self.influxHdlr._send_sensor_data_to_influxdb(sensor_data)
                        if (retVal == False):
                            log.warning("Fehler beim schreiben von {}".format(sensor_data))

                    days_hist_written = True
                    days_hist = ('da[dx++]="{}.{}.{}|{};{}"\n'.format(Zeit.day, Zeit.month, Zeit.year, round(PvInvertersAcEnergyForwardPerDay)*1000, PacMax))

                    with open(_conf.EXPORT_FILEPATH + "days_hist.js", "wt+") as f:
                        days_hist = days_hist + f.read()
                        f.write (days_hist)
                        f.close()

            ## Warten bis die Zeit vergeht
                time.sleep(interval)

        ##### Fehlerbehandlung #####################################################
        except ImportError as e:
            log.error('Eine der Bibliotheken konnte nicht geladen werden!\n{}!\n'.format(e))
            print 'Eine der Bibliotheken konnte nicht geladen werden!\n{}!\n'.format(e)

        except IOError as e:
            log.error("IOError: {}".format(e.msg))
            print 'IOError'

        except:
            for info in sys.exc_info():
                log.error("Fehler: {}".format(info))
                print ("Fehler: {}".format(info))

# # Ende Funktion: ' _main' #######################################################################

# #################################################################################################
# #  Funktion: 'Einsprung beim Aufruf  '
# #################################################################################################
#if __name__ == '__init__':

    #__init__()

# # DateiEnde #####################################################################################

