#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# #################################################################################################
##  \brief      Liest die Csv aus und schreibt eine Datei mit Tageswerten
#   \details
#   \file        SetTagesEnergie.py
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
bDebug = True
bDebugOnLinux = True

# #################################################################################################
# # Python Imports (Standard Library)
# #################################################################################################
import sys
import os
import time
import datetime
import math
import re
import json
import numbers
from glob import glob

# Damit kann aus einem andern Pfad importiert werden. Diejenigen die lokal verwendet werden, vor der Pfaderweiterung importieren
if (bDebug == False):
    importPath = '/mnt/dietpi_userdata/Common'

elif(bDebugOnLinux == True):
    importPath = '/home/users/Grafana/Common'

else:
    importPath = 'D:\\Users\\Download\\PvAnlage\\Common'

sys.path.insert(0, importPath)

from configuration import Global as _conf, PvInverter as PvInv, Grid, Battery, VeBus, System
import SunRiseSet
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
# #  Funktion: 'Read_Piko_Csv '
## \details
#   \param[in]     -
#   \return          -
# #################################################################################################
def getEnergy(datei):

    #print(datei)
    dataRead = ''
    retVal = []

    if (bDebug == True) and (bDebugOnLinux == False):
        datei = datei.replace('/','\\')

    if not (os.path.exists(datei)):
        return retVal

    with open(datei, "r") as f:
        dataRead =(f.readlines())
    f.close()

    for line in dataRead:
        retVal.append(line)

    return retVal

# # Ende Funktion: ' RegEx ' #################################################################################

# #################################################################################################
# #  Funktion: writetoFile
## \details
#   \param[in]     -
#   \return          -
# #################################################################################################
def writetoFile(windowsPath, _year, Inverter, DateiName, Energie):

    filePath = '{}/{}/{}{}'.format(windowsPath, _year, Inverter, DateiName)
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
# #  Funktion: getPathForGlob
## \details
#   \param[in]     -
#   \return          -
# #################################################################################################
def getPathForGlob(path, Year, Inverter):

    invPath = '{}/{}/{}-*.csv'.format(path, Year, Inverter)

    if (bDebug == True) and (bDebugOnLinux == False):
        invPath = invPath.replace('/','\\')

    #print(invPath)
    importList = sorted(glob(invPath))

    return importList

# # Ende Funktion: getPathForGlob #################################################################################

# #################################################################################################
# #  Funktion: calcTagesEnergieVonLog
## \details
#   \param[in]     -
#   \return          -
# #################################################################################################
def calcTagesEnergieVonLog(path, _year, Inverter):

    #den letzen Tag vom Vorjahr
    #~ logE = getEnergy('{}/{}/{}TotalEnergy.log'.format(path, (_year - 1), Inverter))
    #~ lastDayLine = ''
    #~ for line in logE:
        #~ line = line.strip()
        #~ if not line:
            #~ continue
        #~ lastDayLine = line

    lastDayEnergy = 0
    #~ smaRegEx = "(TimeStamp:) (\d{2})\.(\d{2})\.(\d{4}) (\d{2})\:(\d{2}) (\d{2})(\s*)(Total Energy:)( *)(\d*)( Wh)"
    #~ match = Utils.RegEx(smaRegEx, lastDayLine, Utils.fndFrst, Utils.Srch, '')
    #~ if match:
        #~ print(match.groups())
        #~ lastDayEnergy = int(match.group(11))

    txtDay = []
    logE = getEnergy('{}/{}/{}TotalEnergy.log'.format(path, _year, Inverter))
    for line in logE:
        line = line.strip()
        if not line:
            continue

        #print(line)
        smaRegEx = "(TimeStamp:) (\d{2})\.(\d{2})\.(\d{4}) (\d{2})\:(\d{2}) (\d{2})(\s*)(Total Energy:)( *)(\d*)( Wh)"
        match = Utils.RegEx(smaRegEx, line, Utils.fndFrst, Utils.Srch, '')
        if match:
            #print(match.groups())
            _day = int(match.group(2))
            _mon = int(match.group(3))
            _year = int(match.group(4))
            _h = int(match.group(5))
            _m = int(match.group(6))
            _s = int(match.group(7))
            _Wh = int(match.group(11))

            date = ('{:02}.{:02}.{}'.format(_day, _mon, _year))
            datetimeFormat = '%d.%m.%Y'
            diff = datetime.datetime.strptime(date, datetimeFormat) - datetime.timedelta(days=1)

            ## TagesEnergie
            if (lastDayEnergy == 0):
                lastDayEnergy = _Wh
                continue

            TagesE = _Wh - lastDayEnergy

            ## TagesEnergie
            strLine = 'TimeStamp: {:02}.{:02}.{} {:02}:{:02} {:02}    Tages Energy: {: 6} Wh'.format(diff.day, diff.month, diff.year, _h, _m, _s, TagesE)
            txtDay.append(strLine)
            #print(strLine)

            lastDayEnergy = _Wh

    return txtDay

# # Ende Funktion: calcTagesEnergieVonLog #################################################################################

# #################################################################################################
# #  Funktion: 'Read_Piko_Csv '
## \details
#   \param[in]     -
#   \return          -
# #################################################################################################
def Read_Piko_Csv(path, Year, Inverter):

    importList = getPathForGlob(path, Year, Inverter)
    if (len(importList) == 0):
        importList = getPathForGlob(path, Year, Inverter.upper())

    #print(importList)
    txtDay = []
    txtTot = []
    smaE = []
    smaDict = {}

    for datei in importList:
        dataRead = []
        with open(datei, "r") as f:
            dataRead.append(f.readlines())
        f.close()

        resultList = datei.split('\\')
        Datum = (resultList[len(resultList) - 1])

        Datum = Datum.split('.')[0]
        Datum = Datum.split('-')[1]
        _day = Datum[6:]
        _mon = Datum[4:6]
        _year = Datum[:4]

        # Ab dem Datum wurde Piko und SMA zusammengezält
        if (_year == '2020') and (len(smaE) == 0):
            smaE = getEnergy('{}/{}/SmaTotalEnergy.log'.format(path, _year))

        if (Datum == '20200620'):
            sma_Daily = 0
            yes_wh = 0
            for line in smaE:
                line = line.strip()
                if not line:
                    continue

                smaRegEx = "(TimeStamp:) (\d{2})\.(\d{2})\.(\d{4}) (\d{2})\:(\d{2}) (\d{2})(\s*)(Total Energy:)( *)(\d*)( Wh)"
                match = Utils.RegEx(smaRegEx, line, Utils.fndFrst, Utils.Srch, '')
                if match:
                    #print(match.groups())
                    sma_day = int(match.group(2))
                    sma_mon = int(match.group(3))
                    sma_year = int(match.group(4))
                    #_h = int(match.group(5))
                    #_m = int(match.group(6))
                    sma_Wh = int(match.group(11))

                    datetimeFormat = '%d.%m.%Y'
                    date = '{:02}.{:02}.{}'.format(sma_day, sma_mon, sma_year)
                    _date = datetime.datetime.strptime(date, datetimeFormat)
                    if(_date < datetime.datetime.strptime('19.06.2020', datetimeFormat)):
                        continue

                    if(yes_wh == 0):
                        yes_wh = sma_Wh
                        smaDict[date] = [sma_Wh, sma_Daily]
                        continue

                    diff = datetime.datetime.strptime(date, datetimeFormat) - datetime.timedelta(days=1)
                    date = ('{:02}.{:02}.{}'.format(diff.day, diff.month, diff.year))

                    sma_Daily = sma_Wh - yes_wh #Tagesenergie für einen Tag zuvor, da totalenergie im am Tag in der früh nach Sonnenaufgang ist
                    smaDict[date] = [yes_wh, sma_Daily]
                    yes_wh = sma_Wh

        for dataSet in dataRead:
            bFound = False
            TotalE = 0
            TagesE = 0
            StartE = 0
            EndLineE = 0
            SmaTotalE = 0
            SmaTagesE = 0

            for line in dataSet:
                if (not 'Zeit' in line) and (bFound == False):
                    continue;
                if ('Zeit' in line):
                    bFound = True
                    continue

                # ; als Separator
                resultList = line.split(';')
                # TAB als Separator
                if (len(resultList) == 1):
                    resultList = line.split('\t')

                resultList[0] = resultList[0].replace("'", "")
                Zeit = resultList[0].split(':')
                h = Zeit[0]
                m = Zeit[1]
                s = Zeit[2]

                if(TotalE == 0):
                    StartE = float(resultList[25].replace(',','.'))
                    TotalE = resultList[25]
                    TotalE = TotalE.replace(',', '')
                    TotalE = int(TotalE.replace('.', ''))

                    datetimeFormat = '%d.%m.%Y'
                    pDate = '{:2}.{:2}.{}'.format(_day, _mon, _year)
                    if(len(smaDict) > 0):
                        SmaTmp = smaDict.get(pDate)
                        SmaTotalE = SmaTmp[0]
                        SmaTagesE = SmaTmp[1]
                        if(not SmaTotalE is None):
                            del smaDict[pDate]
                        else:
                            SmaTotalE = 0
                            SmaTagesE = 0

                    #print('SMA {} : {} : {}'.format(pDate, SmaTotalE, SmaTagesE))

                    ## GesamtEnergie heute
                    TotalE = TotalE - SmaTotalE
                    strLine = 'TimeStamp: {:2}.{:2}.{} {:2}:{:2} {:2}    Total Energy: {: 9} Wh'.format(_day, _mon, _year, h, m, s, TotalE)
                    txtTot.append(strLine)

                #TagesEnergie überprüfen und auslesen
                tmpE = resultList[24]
                tmpE = tmpE.replace(',', '')
                tmpE = int(tmpE.replace('.', ''))

                if (TotalE < 15000):    # für die ersten Tage der Anlage, bei der die Gesamtsumme immer mit der Tagesleitung gleich war
                    TagesE = tmpE
                elif(tmpE < TotalE) and (tmpE > 0):
                    TagesE = tmpE
                elif(TagesE == 0):
                    EndLineE = float(resultList[25].replace(',','.'))

            if(TagesE == 0):
                TagesE = (int(EndLineE * 1000) - int(StartE * 1000))

            ## TagesEnergie
            TagesE = TagesE - SmaTagesE
            strLine = 'TimeStamp: {:2}.{:2}.{} {:2}:{:2} {:2}    Tages Energy: {: 6} Wh'.format(_day, _mon, _year, h, m, s, TagesE)
            txtDay.append(strLine)
            #print(strLine)

    # KeineCsv Dateien vorhanden, die TotalEnergy.log auslesen
    if (len(importList) == 0):
        txtDay = calcTagesEnergieVonLog(path, int(Year), Inverter)

    # Was ist noch über)
    #print (smaDict)
    if(int(Year) < 2021):
        writetoFile(path, Year, Inverter, 'TotalEnergy.log', txtTot)

    writetoFile(path, Year, Inverter, 'TagesEnergy.txt', txtDay)

    return

# # Ende Funktion: 'Read_Piko_Csv ' ############################################################################################################################################

# #################################################################################################
# #  Funktion: 'Read_Sma_Csv '
## \details
#   \param[in]     -
#   \return          -
# #################################################################################################
def Read_Sma_Csv(path, Year, Inverter, lastDay):

    importList = getPathForGlob(path, Year, Inverter)
    if (len(importList) == 0):
        importList = getPathForGlob(path, Year, Inverter.upper())

    #print(importList)
    txtTot = []
    txtDay = []
    totLine = ''
    dayLine = ''

    for datei in importList:
        dataRead = []
        with open(datei, "r") as f:
            dataRead.append(f.readlines())
        f.close()
        #print(datei)

        if (bDebug == True) and (bDebugOnLinux == False):
            resultList = datei.split('\\')
        else:
            resultList = datei.split('/')

        lastYear = resultList[len(resultList) -2]

        for dataSet in dataRead:
            bFound = False
            TotalE = 0
            for line in dataSet:
                line = line.replace('\0', '')
                line = line.replace('\n', '')

                if (line == ''):
                    continue
                if (not 'dd.MM.yyyy' in line) and (bFound == False):
                    continue;
                if ('dd.MM.yyyy' in line):
                    bFound = True
                    continue

                # ; als Separator
                resultList = line.split(';')
                # TAB als Separator
                if (len(resultList) == 1):
                    resultList = line.split('\t')

                date = resultList[0].replace("'", "")
                date = date.replace('00:00:00', '')
                Datum = date.split('.')
                # Dann kommen die Tages Csv Dateien
                if(len(Datum[2]) > 4):
                    break

                datetimeFormat = '%d.%m.%Y'
                diff = datetime.datetime.strptime(date, datetimeFormat) + datetime.timedelta(days=1)
                date = ('{:02}.{:02}.{}'.format(diff.day, diff.month, diff.year))
                _day = diff.day
                _mon = diff.month
                _year = diff.year
                Day = int(Datum[0])
                Mon = int(Datum[1])
                Year = int(Datum[2])

                lt = []
                lt.append(_year)
                lt.append(_mon)
                lt.append(_day)
                lt.append(1)
                lt.append(0)
                lt.append(0)
                AMh, AMm, UMh, UMm, lt_tag, lt_monat, lt_jahr, lt_h, lt_m, lt_s = SunRiseSet.get_Info(lt)

                h = AMh
                m = AMm
                s = 0

                TagesE = resultList[2]
                TagesE = TagesE.replace(',', '')
                TagesE = TagesE.replace('.', '')
                try:
                    TagesE = int(TagesE)
                except:
                    TagesE = 0

                dayLine = ('TimeStamp: {:02}.{:02}.{} {:02}:{:02} {:02}    Tages Energy: {: 6} Wh'.format(Day, Mon, Year, h, m, s, TagesE))

                TotalE = resultList[1]
                TotalE = TotalE.replace(',', '')
                TotalE = int(TotalE.replace('.', ''))
                totLine = ('TimeStamp: {:02}.{:02}.{} {:02}:{:02} {:02}    Total Energy: {: 9} Wh'.format(_day, _mon, _year, h, m, s, TotalE))

                if (len(lastDay) > 0):
                    txtTot.append(lastDay)
                    lastDay = ''

                txtDay.append(dayLine)
                if(int(lastYear) == int(_year)):
                    txtTot.append(totLine)

    # KeineCsv Dateien vorhanden, die TotalEnergy.log auslesen
    if (len(importList) == 0):
        txtDay = calcTagesEnergieVonLog(path, int(Year), Inverter)

    if(Year < 2021) and (len(txtTot) > 0):
        writetoFile(path, Year, Inverter, 'TotalEnergy.log', txtTot)

    if (len(txtDay) > 0):
        writetoFile(path, Year, Inverter, 'TagesEnergy.txt', txtDay)

    return totLine

# # Ende Funktion: 'Read_Sma_Csv ' ######################################################################

# #################################################################################################
# #  Funktion: ' _main '
## \details         Die Einsprungsfunktion, ruft alle Funktionen und Klassen auf.
#   \param[in]    argv
#   \return            -
# #################################################################################################
def _main(argv):
    global influxHdlr

    lastDay = ''

    aktJahr = [2014,2015,2016,2017,2018,2019,2020,2021]
    #aktJahr = [2020]

    if (bDebug == False):
        windowsPath = '/mnt/dietpi_userdata/SolarExport'

    elif(bDebugOnLinux == True):
        windowsPath = '/home/gerhard/Grafana/SolarExport'

    else:
        windowsPath = 'D:/Users/Download/PvAnlage/SolarExport'

    try:
        for year in aktJahr:
            print(year)
            lastDay = Read_Sma_Csv(windowsPath, year, 'Sma', lastDay)
            #print(lastDay)
            Read_Piko_Csv(windowsPath, year, 'Piko')

    ##### Fehlerbehandlung #####################################################
    except ImportError as e:
        print('Eine der Bibliotheken konnte nicht geladen werden!\n{}\n'.format(e))

# # Ende Funktion: ' _main' #######################################################################

# #################################################################################################
# #  Funktion: 'Einsprung beim Aufruf  '
# #################################################################################################
if __name__ == '__main__':

    _main(sys.argv)

# # DateiEnde #####################################################################################

