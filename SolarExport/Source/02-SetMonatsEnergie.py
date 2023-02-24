#!/usr/bin/env python3
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
# # Debug Einstellungen
# #################################################################################################
bDebug = True
bDebugOnLinux = True

# #################################################################################################
# # Python Imports (Standard Library)
# #################################################################################################
import sys
import os
import re
import datetime
from calendar import monthrange

# Damit kann aus einem andern Pfad importiert werden. Diejenigen die lokal verwendet werden, vor der Pfaderweiterung importieren
if (bDebug == False):
    importPath = '/mnt/dietpi_userdata/Common'

elif(bDebugOnLinux == True):
    importPath = '/home/users/Grafana/Common'

else:
    importPath = 'D:\\Users\\Download\\PvAnlage\\Common'

sys.path.insert(0, importPath)

import Utils

# #################################################################################################
# # UmgebungsVariablen
# #################################################################################################

# #################################################################################################
# # Funktionen
# # Prototypen
# # if __name__ == '__main__':
# #################################################################################################

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
# #  Funktion: writetoFile
## \details
#   \param[in]     -
#   \return          -
# #################################################################################################
def writetoFile(windowsPath, Inverter, DateiName, Energie):

    filePath = '{}/{}{}'.format(windowsPath, Inverter, DateiName)
    if (bDebug == True) and (bDebugOnLinux == False):
        filePath = filePath.replace('/','\\')
    #print(filePath)
    #return

    with open(filePath, "w") as f:
        for line in Energie:
            if not line:
                continue
            #print(line)
            f.write("{}\n".format(line))
    f.close()

# # Ende Funktion: writetoFile #################################################################################

# #################################################################################################
# #  Funktion: 'get_DayHistPac '
## \details
#   \param[in]     -
#   \return          -
# #################################################################################################
def get_InverterMonatsLeistung(windowsPath, Inverter, datMonat, datTagLog, year):

    StartE = 0
    MonthE = 0
    lastMonth = 0
    monatsDaten = []
    diff = 0
    lastDate = 0
    datei = '{}/{}/{}{}'.format(windowsPath, year, Inverter, datTagLog)

    if (bDebug == True) and (bDebugOnLinux == False):
        datei = datei.replace('/','\\')

    if not (os.path.exists(datei)):
        return
    #print(datei)

    dayE = getEnergy(datei)

    if(len(dayE) == 0):
        return

    for line in dayE:
        line = line.strip()
        if not line:
            continue

        smaRegEx = "(TimeStamp:) (\d{2})\.(\d{2})\.(\d{4}) (\d{2})\:(\d{2}) (\d{2})(\s*)(Total Energy:)( *)(\d*)( Wh)"
        match = Utils.RegEx(smaRegEx, line, Utils.fndFrst, Utils.Srch, '')
        if match:
            #print(match.groups())
            _day = int(match.group(2))
            _mon = int(match.group(3))
            _year = int(match.group(4))
            _h = int(match.group(5))
            _m = int(match.group(6))
            _Wh = int(match.group(11))

            date = ('{:02}.{:02}.{}'.format(_day, _mon, _year))

            if (lastMonth == 0):
                strStream = "Datum;{} Stand Monat (kWh)".format(Inverter)
                monatsDaten.append(strStream)
                StartE = _Wh
                lastMonth = _mon

            if(lastMonth != _mon):
                MonthE = _Wh - StartE

                datetimeFormat = '%d.%m.%Y'
                diff = datetime.datetime.strptime(lastDate, datetimeFormat)

                strStream = "{:02}.{:02}.{};{: 8}".format(diff.day, diff.month, diff.year, MonthE)
                monatsDaten.append(strStream)
                lastMonth = _mon
                StartE = _Wh
                MonthE = 0

            lastDate = date

    MonthE = _Wh - StartE
    egal, days = monthrange(_year, _mon)
    _Now = datetime.datetime.now()
    if(_Now.year == _year):
        days = _day

    strStream = "{:02}.{:02}.{};{: 8}".format(days, _mon, _year, MonthE)
    monatsDaten.append(strStream)

    #print (monatsDaten)
    windowsPath = '{}/{}'.format(windowsPath, year)
    writetoFile(windowsPath, Inverter, datMonat, monatsDaten)

    return

# # Ende Funktion: 'get_InverterMonatsLeistung ' ######################################################################

# #################################################################################################
# #  Funktion: ' _main '
## \details         Die Einsprungsfunktion, ruft alle Funktionen und Klassen auf.
#   \param[in]    argv
#   \return            -
# #################################################################################################
def _main(argv):

    windowsPath = 'D:/Users/Download/PvAnlage/SolarExport'
    windowsPath = '/home/gerhard/Grafana/SolarExport'

    #aktJahr = [2014,2015,2016,2017,2018,2019,2020,2021,2021]
    aktJahr = [2022,2023]

    if (bDebug == False):
        windowsPath = '/mnt/dietpi_userdata/SolarExport'

    elif(bDebugOnLinux == True):
        windowsPath = '/home/gerhard/Grafana/SolarExport'

    else:
        windowsPath = 'D:/Users/Download/PvAnlage/SolarExport'

    for year in aktJahr:
        print(year)

        get_InverterMonatsLeistung(windowsPath, 'Sma', 'EnergieMonat.txt', 'TotalEnergy.log', year)
        get_InverterMonatsLeistung(windowsPath, 'Piko', 'EnergieMonat.txt', 'TotalEnergy.log', year)

# #################################################################################################
# #  Funktion: 'Einsprung beim Aufruf  '
# #################################################################################################
if __name__ == '__main__':

    _main(sys.argv)

# # DateiEnde #####################################################################################