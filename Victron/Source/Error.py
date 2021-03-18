#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# #################################################################################################
## \brief     Die Fehlerklassen
#  \details   Alle selbstdefinierten Fehler sind hier als Klassen hinterlegt.
#  \file      Error.py
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

# #################################################################################################
# # Python Imports (site-packages)
# #################################################################################################

# #################################################################################################
# # private Imports
# #################################################################################################

# #################################################################################################
# # UmgebungsVariablen
# #################################################################################################

# #################################################################################################
# # FehlerKlassen
# #################################################################################################

## \brief Wird aufgerufen wenn eine Variable nicht in den Umgebungsvariablen definiert ist
class EnvironVars(Exception):
    def __init__(self, z):
        self.msg = z
        self.environvarsInfo = "\nError: '%(msg)s' ist nicht in den Umgebungsvariablen definiert'."

## \brief Wird aufgerufen wenn ein allgemeiner Fehler auftritt
class AllgBuild(Exception):
    def __init__(self, z):
        self.msg = z
        self.AllgBuildInfo = "\n%(msg)s"

## \brief Wird aufgerufen wenn eine Datei nicht erstellt werden kann
class Dateiname(Exception):
    def __init__(self, z):
        self.msg = z
        self.dateinameInfo = "\nError: '%(msg)s' konnte nicht erstellt werden'."

## \brief Wird aufgerufen wenn eine Datei nicht geoeffnet werden konnte
class OpenFile(Exception):
    def __init__(self, z):
        self.msg = z
        self.openfileInfo = "\nError: '%(msg)s' konnte nicht geoeffnet werden'."

## \brief Wird aufgerufen wenn die Version von Python nicht passt
class PytVerErr(Exception):
    def __init__(self, z):
        self.msg = z
        self.PytVerErrInfo = "\nError: Die installierte Version von Python '%(msg)s' wird nicht untestützt\nBitte installiere Version 2.7.x"

# # DateiEnde #########################################################################################