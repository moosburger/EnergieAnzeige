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

    strStream = "Datum;{} Stand Jahr (kWh)".format(Inverter)
    Energie.insert(0, strStream)
    filePath = '{}/{}{}'.format(windowsPath, Inverter, DateiName)
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
# #  Funktion: get_InverterJahresLeistung
## \details
#   \param[in]     -
#   \return          -
# #################################################################################################
def get_InverterJahresLeistung(windowsPath, Inverter, datMonat, year):

    YearE = 0
    datei = '{}/{}/{}{}'.format(windowsPath, year, Inverter, datMonat)

    if (bDebug == True) and (bDebugOnLinux == False):
        datei = datei.replace('/','\\')

    if not (os.path.exists(datei)):
        return
    #print(datei)

    monE = getEnergy(datei)

    if(len(monE) == 0):
        return

    for line in monE:
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
            _Wh = int(match.group(4))

            YearE += _Wh

    egal, days = monthrange(_year, _mon)
    _Now = datetime.datetime.now()
    if(_Now.year == _year):
        days = _day

    strStream = "{:02}.{:02}.{};{: 9}".format(days, _mon, _year, YearE)
    return (strStream)

# # Ende Funktion: get_InverterMonatsLeistung ######################################################################

# #################################################################################################
# #  Funktion: ' _main '
## \details         Die Einsprungsfunktion, ruft alle Funktionen und Klassen auf.
#   \param[in]    argv
#   \return            -
# #################################################################################################
def _main(argv):

    windowsPath = 'D:/Users/Download/PvAnlage/SolarExport'
    windowsPath = '/home/gerhard/Grafana/SolarExport'
    pikoJahr = []
    smaJahr =[]

    aktJahr = [2014,2015,2016,2017,2018,2019,2020,2021,2022,2023]
    #aktJahr = [2022,2023]

    if (bDebug == False):
        windowsPath = '/mnt/dietpi_userdata/SolarExport'

    elif(bDebugOnLinux == True):
        windowsPath = '/home/gerhard/Grafana/SolarExport'

    else:
        windowsPath = 'D:/Users/Download/PvAnlage/SolarExport'

    for year in aktJahr:
        print(year)
        smaJahr.append(get_InverterJahresLeistung(windowsPath, 'Sma', 'EnergieMonat.txt',  year))
        pikoJahr.append(get_InverterJahresLeistung(windowsPath, 'Piko', 'EnergieMonat.txt', year))

    writetoFile(windowsPath, 'Sma', 'EnergieJahr.txt', smaJahr)
    writetoFile(windowsPath, 'Piko', 'EnergieJahr.txt', pikoJahr)

# #################################################################################################
# #  Funktion: 'Einsprung beim Aufruf  '
# #################################################################################################
if __name__ == '__main__':

    _main(sys.argv)

# # DateiEnde #####################################################################################