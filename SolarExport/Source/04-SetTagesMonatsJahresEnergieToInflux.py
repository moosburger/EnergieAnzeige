#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# #################################################################################################
## \brief     Liest die *.txt Dateien ein und schreibt die DAten nin die Datenbank
#  \details
#  \file      SetTagesMonatsJahresEnergieToInflux.py
#
#  \date      Erstellt am: 26.05.2020
#  \author    moosburger
#
# <History\> ######################################################################################
# Version     Datum      Ticket#     Beschreibung
# 1.0         26.05.2020
#
# #################################################################################################
##
##Aufruf im Raspi
## cd /mnt/dietpi_userdata/SolarExport
##python3 "/mnt/dietpi_userdata/SolarExport/04-SetTagesMonatsJahresEnergieToInflux.py"
##
# #################################################################################################
# # Debug Einstellungen
# #################################################################################################
bDebug = False
bDebugOnLinux = False
bWriteToInflux = True
bPrintIt = False

# #################################################################################################
# # Python Imports (Standard Library)
# #################################################################################################
import sys
import os
import re
import calendar
from collections import namedtuple as NamedTuple, OrderedDict

if (bWriteToInflux):
    from locInfluxHandler import influxIO, _SensorData as SensorData

# Damit kann aus einem andern Pfad importiert werden. Diejenigen die lokal verwendet werden, vor der Pfaderweiterung importieren
if (bDebug == False):
    importPath = '/mnt/dietpi_userdata/Common'

elif(bDebugOnLinux == True):
    importPath = '/home/users/Grafana/Common'

else:
    importPath = 'D:\\Users\\Download\\PvAnlage\\Common'

sys.path.insert(0, importPath)

import Utils
from configuration import Global as _conf, PvInverter as PvInv, Grid, Battery, VeBus, System

# #################################################################################################
# # UmgebungsVariablen / Globals
# #################################################################################################

# #################################################################################################
##
# #################################################################################################
if (not bWriteToInflux):
    SensorData = NamedTuple('SensorData', 'device instance type value timestamp')

# #################################################################################################
# # Funktionen
# # Prototypen
# #################################################################################################

# #################################################################################################
# #  Funktion: '_EnergyPerDay '
## 	\details    Abhaengig von den Parametern die Summe des letzten monats oder des letzten Jahres
#   \param[in] 	sensor_data_day_list
#   \return 	-
# #################################################################################################
def _WriteEnergyToDb(influxHdlr, sensor_data_day_list):

    retVal = True

    try:
        errLog = ''
        for sensor_data in sensor_data_day_list:
            errLog = sensor_data
            retVal = influxHdlr._send_sensor_data_to_influxdb(sensor_data)
            if (retVal == False):
                print("Fehler beim schreiben von {}".format(sensor_data))

    except:
        print("{}".format(errLog))
        for info in sys.exc_info():
            print("{}".format(info))

# # Ende Funktion: '_EnergyPerDay ' ###############################################################

# #################################################################################################
# #  Funktion: 'calc_GatewayMonatJahrEnergy '
## \details
#   \param[in]     -
#   \return          -
# #################################################################################################
def calc_GatewayEnergy(influxHdlr, sma_sensor_data, piko_sensor_data):

    sensor_data = []
    prntLabel = 'MON_'
    for piko_data in piko_sensor_data:
        strVar = "PvInverters{}".format(piko_data[2][0])
        total = (float(piko_data[3][0]))

        if (not sma_sensor_data is None):
            for sma_data in sma_sensor_data:
                if (piko_data[4] == sma_data[4]) and  (piko_data[2][0] == sma_data[2][0]):
                    total = total + float(sma_data[3][0])
                    #print("{:6.5} = {:6.5} + {:6.5} ".format(total, piko_data[3][0], sma_data[3][0]))

        if ('Year' in piko_data[2][0]):
            prntLabel = 'YEAR'

        data = SensorData(System.RegEx, System.Label1, [strVar,], [round(total,3),], piko_data[4])
        total = 0
        sensor_data.append(data)

        if (not bWriteToInflux) and (bPrintIt):
            print('{}_SensorData\t(device: {:>10})\t(instance:{:>10})\t(type:{:>40})\t(value: {:09.3f})\t(timestamp: {})'.format(prntLabel, data[0], data[1], data[2][0], data[3][0], data[4].replace("'","").replace(":",".").replace("T", ";T")))

    if(bWriteToInflux):
        _WriteEnergyToDb(influxHdlr, sensor_data)

# # Ende Funktion: ' calc_GatewayMonatJahrEnergy ' ###########################################################

# #################################################################################################
# #  Funktion: calc_GatewayTagesEnergy
## \details
#   \param[in]     -
#   \return          -
# #################################################################################################
def calc_GatewayTagesEnergy(influxHdlr, sma_sensor_data, piko_sensor_data):

    sensor_data = []
    for piko_data in piko_sensor_data:
        strVar = "PvInverters{}".format(piko_data[2][0])
        total = (float(piko_data[3][0]))

        if (not sma_sensor_data is None):
            for sma_data in sma_sensor_data:
                if (piko_data[4] == sma_data[4]):
                    total = total + float(sma_data[3][0])
                    #print('{:6.5} = {:6.5} + {:6.5}'.format(total, float(piko_data[3][0]), float(sma_data[3][0])))

        data = SensorData(System.RegEx, System.Label1, [strVar,], [round(total,3),], piko_data[4])
        total = 0
        sensor_data.append(data)

        if (not bWriteToInflux) and (bPrintIt):
            print('DAY__SensorData\t(device: {:>10})\t(instance:{:>10})\t(type:{:>40})\t(value: {:09.3f})\t(timestamp: {})'.format(data[0], data[1], data[2][0], data[3][0], data[4].replace("'","").replace(":",".").replace("T", ";T")))

    if(bWriteToInflux):
        _WriteEnergyToDb(influxHdlr, sensor_data)

# # Ende Funktion: calc_GatewayTagesEnergy ###########################################################

# #################################################################################################
# #  Funktion: getEnergy
## \details
#   \param[in]     -
#   \return          -
# #################################################################################################
def getEnergy(datei):

    dataRead = ''
    retVal = []
    with open(datei, "r") as f:
        dataRead =(f.readlines())
    f.close()

    for line in dataRead:
        retVal.append(line)

    return retVal

# # Ende Funktion: getEnergy #################################################################################

# #################################################################################################
# #  Funktion: 'get_InverterLeistung '
## \details
#   \param[in]     -
#   \return          -
# #################################################################################################
def get_InverterTagesLeistung(windowsPath, Jahr, influxHdlr, strFile, Instance, Unit, Variable):

    sensor_data = []
    if(Unit == 'SMA'):
        modUnit = 'Sma'
    elif(Unit == 'PIKO'):
        modUnit = 'Piko'

    datei = '{}/{}/{}{}'.format(windowsPath, Jahr, modUnit, strFile)
    #print(datei)

    if (bDebug == True) and (bDebugOnLinux == False):
        datei = datei.replace('/','\\')

    if not (os.path.exists(datei)):
        return

    Energy = getEnergy(datei)
    if(len(Energy) == 0):
        return

    for line in Energy:
        line = line.strip()
        if not line:
            continue

        smaRegEx = "(TimeStamp:) (\d{2})\.(\d{2})\.(\d{4}) (\d{2})\:(\d{2}) (\d{2})(\s*)(.* Energy:)( *)(\d*)( Wh)"
        match = Utils.RegEx(smaRegEx, line, Utils.fndFrst, Utils.Srch, '')
        if match:
            #print(match.groups())
            _day = int(match.group(2))
            _mon = int(match.group(3))
            _year = int(match.group(4))
            _h = int(match.group(5))
            _m = int(match.group(6))
            _Wh = int(match.group(11))

            timestamp = _conf.DAYSOFARTIMESTAMP.format(_year, _mon, _day)
            tagesEnergie = round((_Wh / 1000), 3)
            sensor_data.append(SensorData(Instance, Unit, [Variable,], [tagesEnergie,], timestamp))

    if (not bWriteToInflux) and (bPrintIt):
        for data in sensor_data:
            print('DAY__SensorData\t(device: {:>10})\t(instance:{:>10})\t(type:{:>40})\t(value: {:09.3f})\t(timestamp: {})'.format(data[0], data[1], data[2][0], data[3][0], data[4].replace("'","").replace(":",".").replace("T", ";T")))

    if(bWriteToInflux):
        _WriteEnergyToDb(influxHdlr, sensor_data)

    return sensor_data

# # Ende Funktion: 'get_InverterLeistung ' ######################################################################

# #################################################################################################
# #  Funktion: 'get_InverterMonatsLeistung '
## \details
#   \param[in]     -
#   \return          -
# #################################################################################################
def get_InverterLeistung(windowsPath, Jahr, influxHdlr, strFile, Instance, Unit, Variable):

    sensor_data = []
    if(Unit == 'SMA'):
        modUnit = 'Sma'
    elif(Unit == 'PIKO'):
        modUnit = 'Piko'

    if(Jahr is None):
        datei = '{}/{}{}'.format(windowsPath, modUnit, strFile)
    else:
        datei = '{}/{}/{}{}'.format(windowsPath, Jahr, modUnit, strFile)
    #print(datei)

    if (bDebug == True) and (bDebugOnLinux == False):
        datei = datei.replace('/','\\')

    if not (os.path.exists(datei)):
        return

    Energy = getEnergy(datei)
    if(len(Energy) == 0):
        return

    prntLabel = 'MON_'
    for line in Energy:
        line = line.strip()
        if not line:
            continue

        smaRegEx = "(\d{2})\.(\d{2})\.(\d{4});(.*)"
        match = Utils.RegEx(smaRegEx, line, Utils.fndFrst, Utils.Srch, '')
        if match:
            #print(match.groups())
            _day = int(match.group(1))
            _mon = int(match.group(2))
            _year = int(match.group(3))
            _Wh = float(match.group(4))

            MonthTimeStamp = _conf.MONTHTIMESTAMP.format(_year, _mon)
            YearTimeStamp = _conf.YEARTIMESTAMP.format(_year)
            if ('SoFar' in Variable):
                MonthTimeStamp = _conf.MONTHSOFARTIMESTAMP.format(_year, _mon)
                YearTimeStamp = _conf.YEARSOFARTIMESTAMP.format(_year)

            tagesEnergie = round((_Wh / 1000), 3)
            if ('Year' in Variable):
                prntLabel = 'YEAR'
                sensor_data.append(SensorData(Instance, Unit, [Variable,], [tagesEnergie,], YearTimeStamp))
            else:
                sensor_data.append(SensorData(Instance, Unit, [Variable,], [tagesEnergie,], MonthTimeStamp))

    if (not bWriteToInflux) and (bPrintIt):
        for data in sensor_data:
            print('{}_SensorData\t(device: {:>10})\t(instance:{:>10})\t(type:{:>40})\t(value: {:09.3f})\t(timestamp: {})'.format(prntLabel, data[0], data[1], data[2][0], data[3][0], data[4].replace("'","").replace(":",".").replace("T", ";T")))

    if(bWriteToInflux):
        _WriteEnergyToDb(influxHdlr, sensor_data)

    return(sensor_data)

# # Ende Funktion: 'get_InverterMonatsLeistung ' ######################################################################


# #################################################################################################
# #  Funktion: ' _main '
## \details         Die Einsprungsfunktion, ruft alle Funktionen und Klassen auf.
#   \param[in]    argv
#   \return            -
# #################################################################################################
def _main(argv):

    influxHdlrDaily = None
    influxHdlrLong = None
    #windowsPath = 'F:\\PvAnlage\\SolarExport\\'

    #rangeYear = [2014,2015,2016,2017,2018,2019,2020,2021,2022]
    rangeYear = [2022,2023]

    if (bDebug == False):
        windowsPath = '/mnt/dietpi_userdata/SolarExport'
        if (bWriteToInflux):
            influxHdlrLong = influxIO(_host = _conf.INFLUXDB_ADDRESS, _port = _conf.INFLUXDB_PORT, _username = _conf.INFLUXDB_USER, _password = _conf.INFLUXDB_PASSWORD, _database = None, _gzip = _conf.INFLUXDB_ZIPPED, logger = None)
            #influxHdlrDaily = influxIO(_host = _conf.INFLUXDB_ADDRESS, _port = _conf.INFLUXDB_PORT, _username = _conf.INFLUXDB_USER, _password = _conf.INFLUXDB_PASSWORD, _database = None, _gzip = _conf.INFLUXDB_ZIPPED, logger = None)
            ver = influxHdlrLong._init_influxdb_database(_conf.INFLUXDB_DATABASE_LONG, 'SetMonatsEnergie')
            #ver = influxHdlrDaily._init_influxdb_database(_conf.INFLUXDB_DATABASE, 'SetTagesEnergieVonLog')

    elif(bDebugOnLinux == True):
        windowsPath = '/home/gerhard/Grafana/SolarExport'

    else:
        windowsPath = 'D:\\Users\\Download\\PvAnlage\\SolarExport'

    strFileDay = "TagesEnergy.txt"
    strFileMonat = "EnergieMonat.txt"
    strFileYear = "EnergieJahr.txt"

    for aktJahr in rangeYear:
        print(aktJahr)
        #print(windowsPath)

        ## TagesLeistung
        sma__sensor_data = get_InverterTagesLeistung(windowsPath, aktJahr, influxHdlrLong, strFileDay, PvInv.RegEx, PvInv.Label1, 'AcEnergyForwardDaySoFar')
        piko_sensor_data = get_InverterTagesLeistung(windowsPath, aktJahr, influxHdlrLong, strFileDay, PvInv.RegEx, PvInv.Label2, 'AcEnergyForwardDaySoFar')
        calc_GatewayTagesEnergy(influxHdlrLong, sma__sensor_data, piko_sensor_data)

        ## Monat
        sma__sensor_data = get_InverterLeistung(windowsPath, aktJahr, influxHdlrLong, strFileMonat, PvInv.RegEx, PvInv.Label1, 'AcEnergyForwardMonth')
        piko_sensor_data = get_InverterLeistung(windowsPath, aktJahr, influxHdlrLong, strFileMonat, PvInv.RegEx, PvInv.Label2, 'AcEnergyForwardMonth')
        calc_GatewayEnergy(influxHdlrLong, sma__sensor_data, piko_sensor_data)

        sma__sensor_data = get_InverterLeistung(windowsPath, aktJahr, influxHdlrLong, strFileMonat, PvInv.RegEx, PvInv.Label1, 'AcEnergyForwardMonthSoFar')
        piko_sensor_data = get_InverterLeistung(windowsPath, aktJahr, influxHdlrLong, strFileMonat, PvInv.RegEx, PvInv.Label2, 'AcEnergyForwardMonthSoFar')
        calc_GatewayEnergy(influxHdlrLong, sma__sensor_data, piko_sensor_data)

    ## Jahr
    sma__sensor_data = get_InverterLeistung(windowsPath, None, influxHdlrLong, strFileYear, PvInv.RegEx, PvInv.Label1, 'AcEnergyForwardYear')
    piko_sensor_data = get_InverterLeistung(windowsPath, None, influxHdlrLong, strFileYear, PvInv.RegEx, PvInv.Label2, 'AcEnergyForwardYear')
    calc_GatewayEnergy(influxHdlrLong, sma__sensor_data, piko_sensor_data)

    sma__sensor_data = get_InverterLeistung(windowsPath, None, influxHdlrLong, strFileYear, PvInv.RegEx, PvInv.Label1, 'AcEnergyForwardYearSoFar')
    piko_sensor_data = get_InverterLeistung(windowsPath, None, influxHdlrLong, strFileYear, PvInv.RegEx, PvInv.Label2, 'AcEnergyForwardYearSoFar')
    calc_GatewayEnergy(influxHdlrLong, sma__sensor_data, piko_sensor_data)

# #################################################################################################
# #  Funktion: 'Einsprung beim Aufruf  '
# #################################################################################################
if __name__ == '__main__':

    _main(sys.argv)

# # DateiEnde #####################################################################################
