#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# #################################################################################################
## \brief     Hilfsfunktionen
#  \details   Hilfsfunktionen die in den anderen Funktionen gebraucht werden
#  \file      Utils.py
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
    import re
    import datetime
    import calendar

# #################################################################################################
# # Python Imports (site-packages)
# #################################################################################################

# #################################################################################################
# # private Imports
# #################################################################################################
    import Error
except:
    raise

# #################################################################################################
# # UmgebungsVariablen
# #################################################################################################
fndFrst=True
fndAll=False
Rplc=True
Srch=False
toFloat=True
toInt=False

# #################################################################################################
# # Funktionen
# # Prototypen
# # def GetPythonVersion():
# # def __init__(self, Cntdwn):
# # def run(self):
# # def stop(self):
# # def RegEx(pattern, string, findFirst, Replace, repString):
# # def GetEnvironVars(EnvironVar, env):
# # def ErsetzeUmlaute(Stream):
# # def DbgFormatOutput(txtStream):
# # def __init__(self, parent, msgStream, title, InputBox, Button1, Button2='None'):
# # def DelWin (self):
# # def Weiter(self):
# #################################################################################################

# #################################################################################################
# # Anfang Funktion: ' GetPythonVersion '
## \details       Gibt die Version von Python zurück
#   \param[in]  -
#   \return             Versionsnummer als String
# #################################################################################################
def GetPythonVersion():

    PytVer = sys.version_info
    return PytVer

# # Ende Funktion: ' GetPythonVersion ' ###########################################################

# #################################################################################################
# # Anfang Funktion: ' RegEx '
## \details  Regular Expression
#   \param[in]    pattern   das RegEx Muster
#   \param[in]    string    der zu durchsuchende String
#   \param[in]    findFirst nur den ersten oder alle finden
#   \param[in]    Replace   suchen und ersetzen
#   \param[in]    repString der String mit dem der zusuchende ersetzt werden soll
#   \return Wenn Suchen&Ersetzen, dann der ersetzte String, sonst das Objekt
# #################################################################################################
def RegEx(pattern, Stream, findFirst, Replace, repString):

    if Replace :
        str = re.sub(pattern, repString, Stream)#, count=0, flags=0)
        return str
    else:
        p = re.compile(pattern, re.IGNORECASE)
        if findFirst:
            m = p.search(Stream)
        else:
            m = p.findall(Stream)

        return m
    return 0

# # Ende Funktion: ' RegEx ' ######################################################################

# #################################################################################################
# # Anfang Funktion: ' RegExSplit '
## \details  Regular Expression
#   \param[in]    pattern   das RegEx Muster
#   \param[in]    string    der zu durchsuchende String
#   \return         Die SplitList
# #################################################################################################
def RegExSplit(pattern, Stream):

    splitList =  re.split(pattern, Stream)
    return splitList

# # Ende Funktion: ' RegExSplit ' #################################################################

# #################################################################################################
# # Anfang Funktion: ' GetEnvironVars '
## \details Dursucht die env Variable nach der übergebenden Variable, wenn gefunden, wird diese zurückgegeben sont eine Fehlermeldung gezogen
#   \param[in]    EnvironVar
#   \param[in]    env   = 0s.environ
#   \return Die gesuchte Variable
# #################################################################################################
def GetEnvironVars(EnvironVar, env):

    Found = False
    for iter in env:
        if (EnvironVar.lower() == iter.lower()):
            Found = True
            break

    if (Found == False):
        raise Error.EnvironVars(EnvironVar)

    return os.environ[EnvironVar]

# # Ende Funktion: ' GetEnvironVars ' #############################################################

# #################################################################################################
# #  Funktion: '_check_Data_TypeOld '
## 	\details    -
#   \param[in] 	myVal
#   \return 	myVal
# #################################################################################################
def _check_Data_TypeOld(myVal):

    #float, int, str, list, dict, tuple
    if (isinstance(myVal, str)):
        pass
    elif (isinstance(myVal, int)):
        #myVal = float(myVal)
        #myVal = round(myVal, 2)
        pass
    elif (isinstance(myVal, float)):
        myVal = float(myVal)
        myVal = round(myVal, 2)
    else:
        myVal = str(myVal)

    return myVal

# # Ende Funktion: _check_Data_TypeOld ############################################################

# #################################################################################################
# #  Funktion: '_check_Data_Type '
# 	\details    -
#   \param[in] 	myVal
#   \return 	myVal
# #################################################################################################
def _check_Data_Type(myVal, toFloat, digit=2, Format=None):

    type = ''
    length = len(str(myVal))
    #float, int, str, datetime, list, dict, tuple

    if (Format is not None):
        if ('%S' in Format) and ('%m' in Format):
            myVal = datetime.datetime.strptime(myVal, Format)
            type = 'datetime'
        elif ('%S' in Format):
            myVal = datetime.datetime.strptime(myVal, Format).time()
            type = 'time'
        elif ('%m' in Format):
            myVal = datetime.datetime.strptime(myVal, Format).date()
            type = 'date'
    else:
        try:
            #print(f"toFloat: {toFloat}; myVal: {myVal}")
            if not (isinstance(myVal, str)):
                #print ("Is Not AN String")
                if (toFloat == True):
                    myVal = float(myVal)
                else:
                    myVal = int(myVal)

            else:
                if (myVal.isnumeric()):
                    #print ("IsNumeric")
                    if (toFloat == True):
                        myVal = float(myVal)
                    else:
                        myVal = int(myVal)
                elif ('.' in myVal):
                    #print ("HasDot")
                    myVal = float(myVal)
        except:
            #print ("InPass")
            pass

        if (isinstance(myVal, int)):
            type = 'int'
            myVal = int(myVal)
#        elif (isinstance(myVal, long)):
#            type = 'long'
#            myVal = int(myVal)
        elif (isinstance(myVal, float)):
            type = 'float'
            myVal = float(myVal)
            myVal = round(myVal, digit)
        elif (isinstance(myVal, list)):
            type = 'list'
        elif (isinstance(myVal, dict)):
            type = 'dict'
        elif (isinstance(myVal, tuple)):
            type = 'tuple'
        else:
            type = 'string'
            myVal = str(myVal)

    #print(f"type: {type}; myVal: {myVal}")
    return myVal, type, length

# # Ende Funktion: _check_Data_Type ###############################################################

# #################################################################################################
# # Anfang Funktion: ' ErsetzeUmlaute '
## \details Ersetzt  die Umlaute
#   \param[in]  Stream
#   \return Stream
# #################################################################################################
def ErsetzeUmlaute(Stream):

    Stream = Stream.replace('Ä', 'Ae')
    Stream = Stream.replace('Ö', 'Oe')
    Stream = Stream.replace('Ü', 'Ue')
    Stream = Stream.replace('ä', 'TTaeTT')
    Stream = Stream.replace('채', 'TTaeTT')
    Stream = Stream.replace('ö', 'TToeTT')
    Stream = Stream.replace('ü', 'TTueTT')
    Stream = Stream.replace('ß', 'TTssTT')

    return Stream

# # Ende Funktion: ' ErsetzeUmlaute ' #############################################################

# #################################################################################################
# # Anfang Funktion: ' ErzeugeUmlaute '
## \details Ersetzt  die Umlaute
#   \param[in]  Stream
#   \return Stream
# #################################################################################################
def ErzeugeUmlaute(Stream):

    Stream = Stream.replace('Ae', 'Ä')
    Stream = Stream.replace('Oe', 'Ö')
    Stream = Stream.replace('Ue', 'Ü')
    Stream = Stream.replace('TTaeTT', 'ä')
    Stream = Stream.replace('TToeTT', 'ö')
    Stream = Stream.replace('TTueTT', 'ü')
    Stream = Stream.replace('TTssTT', 'ß')

    return Stream

# # Ende Funktion: ' ErzeugeUmlaute ' #############################################################

# #################################################################################################
# # Anfang Funktion: ' Printable '
## \details Ersetzt  die Umlaute
#   \param[in]  Stream
#   \return Stream
# #################################################################################################
def Printable(Stream):

    Stream = ErsetzeUmlaute(Stream)
    Stream = ErsetzeLogIn(Stream)

    pattern = '[ -~,\n]*'
    p = re.compile(pattern, re.DOTALL)
    matches = p.findall(Stream)
    str = ''
    for match in matches:
        if match == '':
            continue

        str = str + match

    return ErzeugeUmlaute(str)

# # Ende Funktion: ' Printable ' ##################################################################

# #################################################################################################
# # Anfang Funktion: ' monthdelta '
## \details Berechnet aus dem Monats Delta den Monat und gibt die Anzahl der Tage dieses Monats zurueck
#   \param[in]  date
#   \param[in]  delta
#   \return Day, Month, Year
# #################################################################################################
def monthdelta(date, delta, asDateObject):

    m, y = (date.month+delta) % 12, date.year + ((date.month)+delta-1) // 12
    if not m: m = 12
    d = min(date.day, calendar.monthrange(y, m)[1])
    d_m = calendar.monthrange(y, m)[1]

    if (asDateObject):
        return date.replace(day=d,month=m, year=y)
    else:
        return [d,m,y,d_m]

# # Ende Funktion: ' monthdelta ' #################################################################

# #################################################################################################
# #  Funktion: '_write_File '
## 	\details
##  "r" - Read - Default value. Opens a file for reading, error if the file does not exist
##  "a" - Append - Opens a file for appending, creates the file if it does not exist
##  "w" - Write - Opens a file for writing, creates the file if it does not exist
##  "x" - Create - Creates the specified file, returns an error if the file exists
#   \param[in] 	strFile
#   \param[in]  txtStream
#   \param[in]  oType
#   \return     -
# #################################################################################################
def _write_File(strFile, txtStream, oType):

    with open(strFile, oType) as f:
      f.write (txtStream)
      f.flush()

    f.close()

    # chmod sendet Oktal Zahlen, Python2 0 davor, python 3 0o
    os.chmod(strFile, 0o777)

# # Ende Funktion: ' _write_File ' ################################################################

# # DateiEnde #####################################################################################