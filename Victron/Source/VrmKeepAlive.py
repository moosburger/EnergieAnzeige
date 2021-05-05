#!/usr/bin/env python3
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
# # Debug Einstellungen
# #################################################################################################
bDebug = False
bDebugOnLinux = False

# #################################################################################################
# # Python Imports (Standard Library)
# #################################################################################################
try:
    import sys
    import time
    import threading

    # Damit kann aus einem andern Pfad importiert werden. Diejenigen die lokal verwendet werden, vor der Pfaderweiterung importieren
    if (bDebug == False):
        importPath = '/mnt/dietpi_userdata/Common'

    elif(bDebugOnLinux == True):
        importPath = '/home/users/Grafana/Common'

    else:
        importPath = 'D:\\Users\\Download\\PvAnlage\\Common'

    sys.path.insert(0, importPath)
    from configuration import Global as _conf

except:
    raise

# #################################################################################################
# # private Imports
# #################################################################################################

# #################################################################################################
# # UmgebungsVariablen / Globals
# #################################################################################################

# #################################################################################################
# # Logging geht in dieselbe Datei, trotz verschiedener Prozesse!
# #################################################################################################

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
    def __init__(self, interval, mqttClient, portal_id, logger):

        self.log = logger.getLogger('VrmKeepAlive')
        thread = threading.Thread(target=self.run, args=(interval, mqttClient, portal_id))
        thread.daemon = True
        thread.start()

    def run(self, interval, mqttClient, portal_id):
        self.log.info('Starte Alive Ping')
        while True:
            mqttClient.publish("R/%s/system/0/Serial" % portal_id)

            time.sleep(interval)
            #self.log.info('Alive Ping')

# # Ende Funktion: ' Constructor ' ################################################################

# #################################################################################################
# # Funktion: ' Destructor '
# #################################################################################################
    #def __del__(self):

# # Ende Funktion: ' Destructor ' #################################################################

# # Ende Klasse: ' KeepAlive ' ####################################################################

# # DateiEnde #####################################################################################