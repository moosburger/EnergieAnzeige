#!/usr/bin/env python
# -*- coding: utf-8 -*-

# #################################################################################################
## \brief     Running a method as Background process
#  \details   Pingt in regelmässigen Abständen den Vrm Mqtt Broker an
#  \file      VrmKeepAlive.py
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
#import sys
#import os
import time
import threading
import logging
from configuration import Global as _conf

#reload(sys)
#sys.setdefaultencoding("utf-8")

# #################################################################################################
# # Python Imports (site-packages)
# #################################################################################################

# #################################################################################################
# # private Imports
# #################################################################################################

# #################################################################################################
# # UmgebungsVariablen / Globals
# #################################################################################################

# #################################################################################################
# # Logging geht in dieselbe Datei, trotz verschiedener Prozesse!
# #################################################################################################
log = logging.getLogger('VrmKeepAlive')
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
class KeepAlive(object):

# #################################################################################################
# # Funktion: ' Constructor '
## \details Die Initialisierung der Klasse KeepAlive
#   \param[in]  self der Objectpointer
#   \param[in]  interval
#   \param[in]  mqttClient
#   \param[in] portal_id
#   \return -
# #################################################################################################
    def __init__(self, interval, mqttClient, portal_id):
        #self.interval = interval
        #self.mqttClient = mqttClient
        #self.portal_id = portal_id

        thread = threading.Thread(target=self.run, args=(interval, mqttClient, portal_id))
        thread.daemon = True
        thread.start()

    def run(self, interval, mqttClient, portal_id):
        log.info('Starte Alive Ping')
        while True:
            mqttClient.publish("R/%s/system/0/Serial" % portal_id)

            time.sleep(interval)

# # Ende Funktion: ' Constructor ' ################################################################

# #################################################################################################
# # Funktion: ' Destructor '
# #################################################################################################
    #def __del__(self):

# # Ende Funktion: ' Destructor ' #################################################################

# # Ende Klasse: ' KeepAlive ' ####################################################################

# # DateiEnde #####################################################################################