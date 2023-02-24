#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# #################################################################################################
## \brief   Piko Inverter communication software
#  \details Auslesen und steuern der SmartHome Geräte der Fritzbox
#  \file    FritzBox.py
#
#  \date    Erstellt am: 09.10.2021
#
# <History\> ######################################################################################
# Version   Datum         Ticket# Beschreibung
# 1.0       09.10.2021    -       Ersterstellung
#
# #################################################################################################

# #################################################################################################
# # Debug Einstellungen
# #################################################################################################
bDebug = False
bDebugOnLinux = False

# Damit kann aus einem andern Pfad importiert werden. Diejenigen die lokal verwendet werden, vor der Pfaderweiterung importieren
if(bDebug == False):
    importPath = '/mnt/dietpi_userdata/Common'

elif(bDebugOnLinux == True):
    importPath = '/home/users/Grafana/Common'

else:
    importPath = 'D:\\Users\\Download\\PvAnlage\\Common'

# #################################################################################################
# # Python Imports (Standard Library)
# #################################################################################################
try:
    PublicImport = True
    import sys
    from logging.config import fileConfig
    #from importlib import reload
    import os
    import logging
    from datetime import datetime
    import time

except ImportError as e:
    PublicImport = False
    ErrorMsg = e

# #################################################################################################
# # private Imports
# #################################################################################################
try:
    PrivateImport = True
    from fritzhome import FritzBox

    sys.path.insert(0, importPath)
    import SunRiseSet
    import Error
    import Utils

except ImportError as e:
    PrivateImport = False
    ErrorMsg = e

# #################################################################################################
# # UmgebungsVariablen / Globals
# #################################################################################################

# #################################################################################################
# # Logging
# #################################################################################################
fileConfig('/mnt/dietpi_userdata/FritzBoxHome/logging_config.ini')
log = logging.getLogger('FritzHome')

# #################################################################################################
# # Funktionen
# # Prototypen
# # if __name__ == '__main__':
# #################################################################################################

# #################################################################################################
# #  Funktion: '_Read_File '
## 	\details
#   \param[in] 	strFile
#   \return     min max
# #################################################################################################
def _Read_File(strFile):

    txtStream = ''
    with open(strFile, 'r') as f:
        txtStream = f.read()

    f.close()

    tmp = txtStream.split('\n')
    exitCond = False
    iCnt = 1
    while (exitCond == False):
        txtStream = tmp[len(tmp)-iCnt]
        if len(txtStream) == 0:
            iCnt += 1
        else:
            exitCond = True

    max = 0
    min = 0
    strPattern = 'max Power: (.*) W      min Power:  (.*) W'
    match = Utils.RegEx(strPattern, txtStream, Utils.fndFrst, Utils.Srch, '')
    if match:
        max = float(match.group(1))
        min = float(match.group(2))

    return max, min

# # Ende Funktion: ' _Read_File ' ################################################################

# #################################################################################################
# #  Funktion:      ' getEnergy '
## 	\details
#   \param[in]	-
#   \return     -
# #################################################################################################
def getEnergy(context, features):

    try:
        actualPower = -1.0

        """Display energy stats of all actors"""
        fritz = context
        fritz.login()

        for actor in fritz.get_actors():
            actualPower = (actor.get_power() or 0.0) / 1000

    except Exception as e:
        log.error("{}".format(e))

    except:
        for info in sys.exc_info():
            log.error("Fehler: {}".format(info))
            #print ("Fehler: {}".format(info))

    return actualPower

        #logging.warning("{:>8}-TOTAL:     {:10.3f}        {}".format(instance, myVal, date_time_str))

    #~ for actor in fritz.get_actors():
        #~ if actor.temperature is not None:
            #~ click.echo("{} ({}): {:.2f} Watt current, {:.3f} wH total, {:.2f} °C".format(
                #~ actor.name.encode('utf-8'),
                #~ actor.actor_id,
                #~ (actor.get_power() or 0.0) / 1000,
                #~ (actor.get_energy() or 0.0) / 100,
                #~ actor.temperature
            #~ ))
        #~ else:
            #~ click.echo("{} ({}): {:.2f} Watt current, {:.3f} wH total, offline".format(
                #~ actor.name.encode('utf-8'),
                #~ actor.actor_id,
                #~ (actor.get_power() or 0.0) / 1000,
                #~ (actor.get_energy() or 0.0) / 100
            #~ ))
        #~ if features:
            #~ click.echo("  Features: PowerMeter: {}, Temperatur: {}, Switch: {}".format(
                #~ actor.has_powermeter, actor.has_temperature, actor.has_switch
            #~ ))

# # Ende Funktion: ' getEnergy ' ########################################################

# #################################################################################################
# #  Funktion:      ' main '
## 	\details
#   \param[in]	-
#   \return     -
# #################################################################################################
def _main(argv):

    runLogFile = '/home/gerhard/Grafana/FritzBoxHome/LogDataAllowed.txt'
    maxPower = 0
    minPower = 9999
    firstRun = True
    log.info("Starte FritzBoxHome")

    bRunLogging = os.path.exists(runLogFile)
    if (bRunLogging == False):
        log.info("Beende FritzBoxHome")
        sys.exit()

    try:
        ## Import fehlgeschlagen
        if (PrivateImport == False) or (PublicImport == False):
            raise ImportError

        context = FritzBox('192.168.2.68', 'smartHome', '7zgvVFR$')

        if (firstRun):
            strFile = "/mnt/dietpi_userdata/FritzBoxHome/HzgMaxMinPower.log"
            maxPower, minPower = _Read_File(strFile)
            firstRun = False

        while True:
            AMh, AMm, UMh, UMm, lt_tag, lt_monat, lt_jahr, lt_h, lt_m, lt_s = SunRiseSet.get_Info([])
            actualPower = getEnergy(context, False)

            if (maxPower < actualPower) and (actualPower > 0.0):
                maxPower = actualPower
                datStream = ("\tTimeStamp {0:02d}.{1:02d}.{2:4d} {3:02d}:{4:02d}:{5:02d}    max Power: {6:6.2f} W".format(lt_tag, lt_monat, lt_jahr, lt_h, lt_m, lt_s, maxPower))
                strFile = "/mnt/dietpi_userdata/FritzBoxHome/HzgMaxMinPower.log"
                Utils._write_File(strFile, datStream + '\n', "a")

            if (minPower > actualPower) and (actualPower > 0.0):
                minPower = actualPower
                datStream = ("\tTimeStamp {0:02d}.{1:02d}.{2:4d} {3:02d}:{4:02d}:{5:02d}                             min Power: {6:6.2f} W".format(lt_tag, lt_monat, lt_jahr, lt_h, lt_m, lt_s, minPower))
                strFile = "/mnt/dietpi_userdata/FritzBoxHome/HzgMaxMinPower.log"
                Utils._write_File(strFile, datStream + '\n', "a")

            datStream = ("\tTimeStamp {0:02d}.{1:02d}.{2:4d} {3:02d}:{4:02d}:{5:02d}    actual Power: {6:6.2f} W    max Power: {7:6.2f} W    min Power: {8:6.2f} W".format(lt_tag, lt_monat, lt_jahr, lt_h, lt_m, lt_s, actualPower, maxPower, minPower))
            #print(datStream)
            strFile = "/mnt/dietpi_userdata/FritzBoxHome/{0:02d}-{1:4d}".format( lt_monat, lt_jahr)
            if not os.path.exists(strFile):
                os.mkdir(strFile)

            strFile = "{0}/HzgPower_{1:02d}.{2:02d}.{3:4d}.log".format(strFile, lt_tag, lt_monat, lt_jahr)
            Utils._write_File(strFile, datStream + '\n', "a")

            time.sleep(120)


    ##### Fehlerbehandlung #####################################################
    except ImportError as e:
        log.error('Eine der Bibliotheken konnte nicht geladen werden!\n{}\n'.format(ErrorMsg))
        #print('Eine der Bibliotheken konnte nicht geladen werden!\n{}\n'.format(ErrorMsg))

    except IOError as e:
        log.error("IOError: {}".format(e))
        #print("IOError: {}".format(e))

    except Error.OpenFile as e:
        log.error(e.openfileInfo %{'msg': e.msg})
        #print(e.openfileInfo %{'msg': e.msg})

    except Error.Dateiname as e:
        log.error(e.dateinameInfo %{'msg': e.msg})
        #print(e.dateinameInfo %{'msg': e.msg})

    except:
        for info in sys.exc_info():
            log.error("Fehler: {}".format(info))
            #print ("Fehler: {}".format(info))

# # Ende Funktion: ' main ' #######################################################################

# #################################################################################################
# #  Funktion: 'Einsprung beim Aufruf  '
# #################################################################################################
if __name__ == '__main__':

    _main(sys.argv)

# # DateiEnde #####################################################################################

