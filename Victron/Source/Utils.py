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

# # Ende Funktion: ' GetPythonVersion ' ###########################################################################

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

# # Ende Funktion: ' RegEx ' #################################################################################

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

# # Ende Funktion: ' RegExSplit ' #################################################################################

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

# # Ende Funktion: ' GetEnvironVars ' ############################################################################

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

# # Ende Funktion: ' ErsetzeUmlaute ' ############################################################################

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

# # Ende Funktion: ' ErzeugeUmlaute ' ############################################################################

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

# # Ende Funktion: ' Printable ' ############################################################################

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

# # Ende Funktion: ' monthdelta ' ############################################################################

# # DateiEnde ##########################################################################################