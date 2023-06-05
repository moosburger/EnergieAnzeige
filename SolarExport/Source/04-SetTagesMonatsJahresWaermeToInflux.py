#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# #################################################################################################
## \brief     Liest die *.txt Dateien ein und schreibt die DAten nin die Datenbank
#  \details
#  \file      04-SetTagesMonatsJahresWaermeToInflux.py
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
## python3 "/mnt/dietpi_userdata/SolarExport/04-SetTagesMonatsJahresWaermeToInflux.py"
##
# #################################################################################################
# # Debug Einstellungen
# #################################################################################################
bDebug = False
bDebugOnLinux = False
bWriteToInflux = True
bPrintIt = True

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
    importPath = '/home/gerhard/Grafana/Common'

else:
    importPath = 'F:\\Eigene Dateien\\Eigene Projekte\\Grafana\\Common'

sys.path.insert(0, importPath)

import Utils
from configuration import Global as _conf, Waerme

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
# #  Funktion: '_WriteEnergyToDb '
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

# # Ende Funktion: '_WriteEnergyToDb ' ###############################################################

# #################################################################################################
# #  Funktion: getData
## \details
#   \param[in]     -
#   \return          -
# #################################################################################################
def getData(datei):

    dataRead = ''
    retVal = []
    with open(datei, "r") as f:
        dataRead =(f.readlines())
    f.close()

    for line in dataRead:
        retVal.append(line)

    return retVal

# # Ende Funktion: getData ########################################################################

# #################################################################################################
# #  Funktion: 'set_TagesGas '
## \details
#   \param[in]     -
#   \return          -
# #################################################################################################
def set_TagesGas(windowsPath, Jahr, influxHdlr, strFile, Instance, Unit, Variable):

    sensor_data = []
    datei = '{}/{}/{}'.format(windowsPath, Jahr, strFile)
    if (bDebug == True) and (bDebugOnLinux == False):
        datei = datei.replace('/','\\')

    if not (os.path.exists(datei)):
        return

    Energy = getData(datei)
    if(len(Energy) == 0):
        return

    #~ prntLabel = 'MON_'
    for line in Energy:
        line = line.strip()
        if not line:
            continue

        regEx = "(\d{2})\.(\d{2})\.(\d{4});(.*);(.*);"
        match = Utils.RegEx(regEx, line, Utils.fndFrst, Utils.Srch, '')
        if match:
            #print(match.groups())
            _day = int(match.group(1))
            _mon = int(match.group(2))
            _year = int(match.group(3))
            _cbm = float(match.group(4))
            _kWh = float(match.group(5))

            timestamp = _conf.DAYSOFARTIMESTAMP.format(_year, _mon, _day)
            Variable_cbm = Variable
            sensor_data.append(SensorData(Instance, Unit, [Variable_cbm,], [_cbm,], timestamp))
            Variable_kWh = Variable.replace('_cbm', '_kWh')
            sensor_data.append(SensorData(Instance, Unit, [Variable_kWh,], [_kWh,], timestamp))

    if (not bWriteToInflux) and (bPrintIt):
        for data in sensor_data:
            print('DAY__SensorData\t(device: {:>10})\t(instance:{:>10})\t(type:{:>30})\t(value: {:09.3f})\t(timestamp: {})'.format(data[0], data[1], data[2][0], data[3][0], data[4].replace("'","").replace(":",".").replace("T", ";T")))

    if(bWriteToInflux):
        _WriteEnergyToDb(influxHdlr, sensor_data)

# # Ende Funktion: set_TagesGas ########################################################################
# # Ende Funktion: getData ########################################################################

# #################################################################################################
# #  Funktion: 'set_TagesWasser '
## \details
#   \param[in]     -
#   \return          -
# #################################################################################################
def set_TagesWasser(windowsPath, Jahr, influxHdlr, strFile, Instance, Unit, Variable):

    sensor_data = []
    datei = '{}/{}/{}'.format(windowsPath, Jahr, strFile)
    if (bDebug == True) and (bDebugOnLinux == False):
        datei = datei.replace('/','\\')

    if not (os.path.exists(datei)):
        return

    Energy = getData(datei)
    if(len(Energy) == 0):
        return

    #~ prntLabel = 'MON_'
    for line in Energy:
        line = line.strip()
        if not line:
            continue

        regEx = "(\d{2})\.(\d{2})\.(\d{4});(.*);(.*);"
        match = Utils.RegEx(regEx, line, Utils.fndFrst, Utils.Srch, '')
        if match:
            #print(match.groups())
            _day = int(match.group(1))
            _mon = int(match.group(2))
            _year = int(match.group(3))
            _lit = float(match.group(4))
            _cbm = float(match.group(5))

            timestamp = _conf.DAYSOFARTIMESTAMP.format(_year, _mon, _day)
            Variable_Lit = Variable
            sensor_data.append(SensorData(Instance, Unit, [Variable_Lit,], [_lit,], timestamp))
            Variable_cbm = Variable.replace('_Lit', '_cbm')
            sensor_data.append(SensorData(Instance, Unit, [Variable_cbm,], [_cbm,], timestamp))

    if (not bWriteToInflux) and (bPrintIt):
        for data in sensor_data:
            print('DAY__SensorData\t(device: {:>10})\t(instance:{:>10})\t(type:{:>30})\t(value: {:09.3f})\t(timestamp: {})'.format(data[0], data[1], data[2][0], data[3][0], data[4].replace("'","").replace(":",".").replace("T", ";T")))

    if(bWriteToInflux):
        _WriteEnergyToDb(influxHdlr, sensor_data)

# # Ende Funktion: set_TagesWasser ########################################################################

# #################################################################################################
# #  Funktion: 'set_Gas '
## \details
#   \param[in]     -
#   \return          -
# #################################################################################################
def set_Gas(windowsPath, Jahr, influxHdlr, strFile, Instance, Unit, Variable):

    sensor_data = []
    datei = '{}/{}/{}'.format(windowsPath, Jahr, strFile)
    if (bDebug == True) and (bDebugOnLinux == False):
        datei = datei.replace('/','\\')

    if not (os.path.exists(datei)):
        return

    Energy = getData(datei)
    if(len(Energy) == 0):
        return

    prntLabel = 'MON_'
    for line in Energy:
        line = line.strip()
        if not line:
            continue

        regEx = "(\d{2})\.(\d{2})\.(\d{4});(.*);(.*);"
        match = Utils.RegEx(regEx, line, Utils.fndFrst, Utils.Srch, '')
        if match:
            #print(match.groups())
            _day = int(match.group(1))
            _mon = int(match.group(2))
            _year = int(match.group(3))
            _cbm = float(match.group(4))
            _kWh = float(match.group(5))

            MonthTimeStamp = _conf.MONTHTIMESTAMP.format(_year, _mon)
            YearTimeStamp = _conf.YEARTIMESTAMP.format(_year)
            if ('SoFar' in Variable):
                MonthTimeStamp = _conf.MONTHSOFARTIMESTAMP.format(_year, _mon)
                YearTimeStamp = _conf.YEARSOFARTIMESTAMP.format(_year)

            Variable_cbm = Variable
            if ('Year' in Variable):
                prntLabel = 'YEAR'
                sensor_data.append(SensorData(Instance, Unit, [Variable_cbm,], [_cbm,], YearTimeStamp))
                Variable_kWh = Variable.replace('_cbm', '_kWh')
                sensor_data.append(SensorData(Instance, Unit, [Variable_kWh,], [_kWh,], YearTimeStamp))
            else:
                sensor_data.append(SensorData(Instance, Unit, [Variable_cbm,], [_cbm,], MonthTimeStamp))
                Variable_kWh = Variable.replace('_cbm', '_kWh')
                sensor_data.append(SensorData(Instance, Unit, [Variable_kWh,], [_kWh,], MonthTimeStamp))

    if (not bWriteToInflux) and (bPrintIt):
        for data in sensor_data:
            print('{}_SensorData\t(device: {:>10})\t(instance:{:>10})\t(type:{:>30})\t(value: {:09.3f})\t(timestamp: {})'.format(prntLabel, data[0], data[1], data[2][0], data[3][0], data[4].replace("'","").replace(":",".").replace("T", ";T")))

    if(bWriteToInflux):
        _WriteEnergyToDb(influxHdlr, sensor_data)

# # Ende Funktion: set_Gas ########################################################################

# #################################################################################################
# #  Funktion: 'set_Wasser '
## \details
#   \param[in]     -
#   \return          -
# #################################################################################################
def set_Wasser(windowsPath, Jahr, influxHdlr, strFile, Instance, Unit, Variable):

    sensor_data = []
    datei = '{}/{}/{}'.format(windowsPath, Jahr, strFile)
    if (bDebug == True) and (bDebugOnLinux == False):
        datei = datei.replace('/','\\')

    if not (os.path.exists(datei)):
        return

    Energy = getData(datei)
    if(len(Energy) == 0):
        return

    prntLabel = 'MON_'
    for line in Energy:
        line = line.strip()
        if not line:
            continue

        regEx = "(\d{2})\.(\d{2})\.(\d{4});(.*);(.*);"
        match = Utils.RegEx(regEx, line, Utils.fndFrst, Utils.Srch, '')
        if match:
            #print(match.groups())
            _day = int(match.group(1))
            _mon = int(match.group(2))
            _year = int(match.group(3))
            _lit = float(match.group(4))
            _cbm = float(match.group(5))

            MonthTimeStamp = _conf.MONTHTIMESTAMP.format(_year, _mon)
            YearTimeStamp = _conf.YEARTIMESTAMP.format(_year)
            if ('SoFar' in Variable):
                MonthTimeStamp = _conf.MONTHSOFARTIMESTAMP.format(_year, _mon)
                YearTimeStamp = _conf.YEARSOFARTIMESTAMP.format(_year)

            Variable_lit = Variable
            if ('Year' in Variable):
                prntLabel = 'YEAR'
                sensor_data.append(SensorData(Instance, Unit, [Variable_lit,], [_lit,], YearTimeStamp))
                Variable_cbm = Variable.replace('_Lit', '_cbm')
                sensor_data.append(SensorData(Instance, Unit, [Variable_cbm,], [_cbm,], YearTimeStamp))
            else:
                sensor_data.append(SensorData(Instance, Unit, [Variable_lit,], [_lit,], MonthTimeStamp))
                Variable_cbm = Variable.replace('_Lit', '_cbm')
                sensor_data.append(SensorData(Instance, Unit, [Variable_cbm,], [_cbm,], MonthTimeStamp))

    if (not bWriteToInflux) and (bPrintIt):
        for data in sensor_data:
            print('{}_SensorData\t(device: {:>10})\t(instance:{:>10})\t(type:{:>30})\t(value: {:09.3f})\t(timestamp: {})'.format(prntLabel, data[0], data[1], data[2][0], data[3][0], data[4].replace("'","").replace(":",".").replace("T", ";T")))

    if(bWriteToInflux):
        _WriteEnergyToDb(influxHdlr, sensor_data)

# # Ende Funktion: set_Wasser ########################################################################

# #################################################################################################
# #  Funktion: ' _main '
## \details         Die Einsprungsfunktion, ruft alle Funktionen und Klassen auf.
#   \param[in]    argv
#   \return            -
# #################################################################################################
def _main(argv):

    influxHdlrDaily = None
    influxHdlrLong = None

    rangeYear = [2014,2015,2016,2017,2018,2019,2020,2021,2022,2023]

    if (bDebug == False):
        windowsPath = '/mnt/dietpi_userdata/SolarExport'
        if (bWriteToInflux):
            influxHdlrLong = influxIO(_host = _conf.INFLUXDB_ADDRESS, _port = _conf.INFLUXDB_PORT, _username = _conf.INFLUXDB_USER, _password = _conf.INFLUXDB_PASSWORD, _database = None, _gzip = _conf.INFLUXDB_ZIPPED, logger = None)
            ver = influxHdlrLong._init_influxdb_database(_conf.INFLUXDB_DATABASE_WAERME_LONG, 'SetMonatsEnergie')
            #influxHdlrDaily = influxIO(_host = _conf.INFLUXDB_ADDRESS, _port = _conf.INFLUXDB_PORT, _username = _conf.INFLUXDB_USER, _password = _conf.INFLUXDB_PASSWORD, _database = None, _gzip = _conf.INFLUXDB_ZIPPED, logger = None)
            #ver = influxHdlrDaily._init_influxdb_database(_conf.INFLUXDB_DATABASE_WAERME, 'SetTagesEnergieVonLog')

    elif(bDebugOnLinux == True):
        windowsPath = '/home/gerhard/Grafana/SolarExport'

    else:
        windowsPath = 'F:\\Eigene Dateien\\Eigene Projekte\\Grafana\\SolarExport'

    strFileDay   = "GasTagesVerbrauch.txt"
    strFileMonat = "GasMonatsVerbrauch.txt"
    strFileYear  = "GasJahresVerbrauch.txt"

    for aktJahr in rangeYear:
        #print(aktJahr)
        #print(windowsPath)

        set_TagesGas(windowsPath, aktJahr, influxHdlrDaily, strFileDay, Waerme.RegEx, Waerme.Label1, 'GasForwardDaySoFar_cbm')
        set_TagesGas(windowsPath, aktJahr, influxHdlrDaily, strFileDay, Waerme.RegEx, Waerme.Label1, 'GasForwardDaySoFar_kWh')

        #set_Gas(windowsPath, aktJahr, influxHdlrLong, strFileMonat, Waerme.RegEx, Waerme.Label1, 'GasForwardMonthSoFar_cbm')
        #set_Gas(windowsPath, aktJahr, influxHdlrLong, strFileMonat, Waerme.RegEx, Waerme.Label1, 'GasForwardMonth_cbm')

        #set_Gas(windowsPath, aktJahr, influxHdlrLong, strFileYear, Waerme.RegEx, Waerme.Label1, 'GasForwardYearSoFar_cbm')
        #set_Gas(windowsPath, aktJahr, influxHdlrLong, strFileYear, Waerme.RegEx, Waerme.Label1, 'GasForwardYear_cbm')


    strFileDay   = "WasserTagesVerbrauch.txt"
    strFileMonat = "WasserMonatsVerbrauch.txt"
    strFileYear  = "WasserJahresVerbrauch.txt"

    for aktJahr in rangeYear:
        #print(aktJahr)
        #print(windowsPath)

        set_TagesWasser(windowsPath, aktJahr, influxHdlrDaily, strFileDay, Waerme.RegEx, Waerme.Label1, 'WasserForwardDaySoFar_Lit')
        set_TagesWasser(windowsPath, aktJahr, influxHdlrDaily, strFileDay, Waerme.RegEx, Waerme.Label1, 'WasserForwardDaySoFar_cbm')

        #set_Wasser(windowsPath, aktJahr, influxHdlrLong, strFileMonat, Waerme.RegEx, Waerme.Label1, 'WasserForwardMonthSoFar_Lit')
        #set_Wasser(windowsPath, aktJahr, influxHdlrLong, strFileMonat, Waerme.RegEx, Waerme.Label1, 'WasserForwardMonth_Lit')

        #set_Wasser(windowsPath, aktJahr, influxHdlrLong, strFileYear, Waerme.RegEx, Waerme.Label1, 'WasserForwardYearSoFar_Lit')
        #set_Wasser(windowsPath, aktJahr, influxHdlrLong, strFileYear, Waerme.RegEx, Waerme.Label1, 'WasserForwardYear_Lit')

# #################################################################################################
# #  Funktion: 'Einsprung beim Aufruf  '
# #################################################################################################
if __name__ == '__main__':

    _main(sys.argv)

# # DateiEnde #####################################################################################