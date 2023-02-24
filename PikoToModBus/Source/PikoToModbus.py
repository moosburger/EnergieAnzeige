#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# #################################################################################################
## \brief     Piko Inverter communication software
#  \details
#  \file      PikoToModBus.py
#
#  \date      Erstellt am: 13.03.2020
#  \author    moosburger
#
# <History\> ######################################################################################
# Version     Datum       Ticket#     Beschreibung
# 1.0         13:03.2020
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
    importPath = '/home/users/Grafana/PikoToModbus'

else:
    importPath = 'D:\\Users\\Download\\PvAnlage\\Common'

# #################################################################################################
# # Python Imports (Standard Library)
# #################################################################################################
import sys
import ctypes
import time
import asyncio
import logging
from logging.config import fileConfig

# --------------------------------------------------------------------------- #
# import the modbus libraries we need
# --------------------------------------------------------------------------- #
from pymodbus.server import StartAsyncTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
from pymodbus.version import version

# --------------------------------------------------------------------------- #
# import the twisted libraries we need
# --------------------------------------------------------------------------- #
#from twisted.internet.task import LoopingCall
# --------------------------------------------------------------------------- #

# #################################################################################################
# # private Imports
# #################################################################################################
try:
    PrivateImport = True
    import locConfiguration as _conf
    from PikoCom import PikoWebRead
    from PreparePikoData import PrepareData
    from GetSmaTotal import TotalSmaEnergy

    # Damit kann aus einem andern Pfad importiert werden. Diejenigen die lokal verwendet werden, vor der Pfaderweiterung importieren
    sys.path.insert(0, importPath)
    import SunRiseSet
except:
    PrivateImport = False

# #################################################################################################
# # UmgebungsVariablen / Globals
# #################################################################################################

# #################################################################################################
# # Logging
# #################################################################################################
fileConfig('/mnt/dietpi_userdata/PikoToModbus/logging_config.ini')
log = logging.getLogger('PikoToModbus')

# #################################################################################################
# # Funktionen
# # Prototypen
# #################################################################################################
_FirstRun = True
_FirstDayRun = True
_LastUpdateForDay = True

# #################################################################################################
# #  Funktion: ' _Fetch_Piko_Data '
## 	\details
#   \param[in]	-
#   \return     -
# #################################################################################################
async def _Fetch_Piko_Data(a):
    """ A worker process that runs every so often and
    updates live values of the context which resides in an SQLite3 database.
    It should be noted that there is a race condition for the update.
    :param arguments: The input arguments to the call    """

    try:
        context  = a[0]
        Sma = a[1]
        Piko = a[2]
        Data = a[3]
        global _FirstRun
        global _FirstDayRun
        global _LastUpdateForDay

        while(True):
            await asyncio.sleep(_conf.SCHED_INTERVAL)

            # Tagsueber oder nachts
            AMh, AMm, UMh, UMm, lt_tag, lt_monat, lt_jahr, lt_h, lt_m, lt_s = SunRiseSet.get_Info([])
            log.debug("\tTimeStamp {0:02d}.{1:02d}.{2:4d} {3:02d}:{4:02d}:{5:02d}".format(lt_tag, lt_monat, lt_jahr, lt_h, lt_m, lt_s))

            # Die Zeiten in Minuten; 00:00 Uhr = 0;  23:59 Uhr = 1439
            sunRise = AMh  * 60 + AMm
            sunSet  = UMh  * 60 + UMm
            locNow  = lt_h * 60 + lt_m
            log.debug(f'sunRise: {sunRise}; locNow: {locNow}; sunSet: {sunSet}')

            # Die letzten Werte des SMA holen, da dieser die Werte um Mitternacht löscht
            if ((locNow > sunSet) and (_LastUpdateForDay == True) and (_FirstRun == False)):
                Sma.FetchSmaTotal(False)
                log.debug('_LastUpdateForDay = False')
                _LastUpdateForDay = False

            # Trigger damit die Werte fürs tägliche Log geschrieben werden
            if ((locNow < sunRise) or (locNow > sunSet)) and (_FirstRun == False):
                _FirstDayRun = True
                log.debug('_FirstDayRun = True')
                continue

            # Daten vom Piko holen und aufbereiten
            retStat = Piko.FetchData(Timers=True, Portal=True, Header=True, Data=True)
            if ((retStat == -1) and (_conf.DEBUG == False)):
                log.debug(f'retStat: {retStat} => Fehler')
                continue

            # Die aufbereiteten Daten holen
            pikoData = Piko.GetFetchedData(_FirstDayRun)

            # Sma Werte fürs tägliche Log
            if(_FirstDayRun == True):
                Sma.FetchSmaTotal(_FirstDayRun)

            log.debug("\tUpdating the database context")
            #readfunction = 0x03 # read holding registers
            writefunction = 0x10
            slave_id = 126 # slave address

            sunSpec = Data.Prepare(Piko, pikoData, _FirstRun)
            for dataSet in sunSpec:
                des = dataSet[0].strip()
                vAdr = dataSet[1] - 1
                leng = dataSet[2]
                val = dataSet[3]
                skr = dataSet[4] - 1
                vSkr = dataSet[5]
                context[slave_id].setValues(writefunction, vAdr, val)

                if (skr > 0):
                    context[slave_id].setValues(writefunction, skr, vSkr)

            _FirstRun = False
            _FirstDayRun = False
            _LastUpdateForDay = True
    except:
        for info in sys.exc_info():
            log.error("Fehler _Fetch_Piko_Data: {}".format(info))

# #################################################################################################
# #  Funktion: ' setup_server '
## 	\details
#   \param[in]	-
#   \return     -
# #################################################################################################
def setup_server():
    # ----------------------------------------------------------------------- #
    # initialize your data store
    # ----------------------------------------------------------------------- #
    log.debug("\tInit Values")
    #block = ModbusSequentialDataBlock(0, [1] * 100)
    #store = SqlSlaveContext(block)
    #context = ModbusServerContext(slaves={1: store}, single=False)

    store = ModbusSlaveContext(
      di=ModbusSequentialDataBlock(40000, [0xFFFF]*40700),  #40440
      co=ModbusSequentialDataBlock(40000, [0xFFFF]*40700),
      hr=ModbusSequentialDataBlock(40000, [0xFFFF]*40700),
      ir=ModbusSequentialDataBlock(40000, [0xFFFF]*40700))

    context = ModbusServerContext(slaves=store, single=True)

    # ----------------------------------------------------------------------- #
    # initialize the server information
    # ----------------------------------------------------------------------- #
    # If you don't set this or any fields, they are defaulted to empty strings.
    # ----------------------------------------------------------------------- #
    identity = ModbusDeviceIdentification(
        info_name={
            "VendorName": "Pymodbus",
            "ProductCode": "PM",
            "VendorUrl": "https://github.com/pymodbus-dev/pymodbus/",
            "ProductName": "Pymodbus Server",
            "ModelName": "Pymodbus Server",
            "MajorMinorRevision": version.short(),
        }
    )
    return identity, context

# #################################################################################################
# #  Funktion: ' run_async_server '
## 	\details
#   \param[in]	-
#   \return     -
# #################################################################################################
async def run_async_server(context, identity, address):

    server = await StartAsyncTcpServer(
        context=context,  # Data storage
        identity=identity,  # server identify
        #~ # TBD host=
        #~ # TBD port=
        address=address,  # listen address
        #custom_functions=[_Fetch_Piko_Data(a=(context,Sma,Piko,Data))],  # allow custom handling
        framer=None,  # The framer strategy to use
        handler=None,  # handler for each session
        allow_reuse_address=True,  # allow the reuse of an address
        # ignore_missing_slaves=True,  # ignore request to a missing slave
        # broadcast_enable=False,  # treat unit_id 0 as broadcast address,
        #timeout=_conf.SCHED_INTERVAL,  # waiting time for request to complete
        # TBD strict=True,  # use strict timing, t1.5 for Modbus RTU
        # defer_start=False,  # Only define server do not activate
    )
    #await server.serve_forever()
    return server

# #################################################################################################
# #  Funktion: ' run_updating_server '
## 	\details
#   \param[in]	-
#   \return     -
# #################################################################################################
async def run_updating_server(context, identity, args):

    """Start updater task and async server."""
    asyncio.create_task(_Fetch_Piko_Data(args))
    await run_async_server(context=context, identity=identity, address=(_conf.INVERTER_IP, _conf.MODBUS_PORT))

# #################################################################################################
# #  Funktion: ' _main '
## 	\details 	Die Einsprungsfunktion, ruft alle Funktionen und Klassen auf.
#   \param[in]  argv
#   \return     -
# #################################################################################################
def _main(argv):

    _FirstRun = True
    _FirstDayRun = True
    _LastUpdateForDay = True

    try:
        log.info("gestartet mit Intervall {} sek.".format(_conf.SCHED_INTERVAL))

        # # Mit dem Piko instanzieren ####################################
        _Piko = PikoWebRead(_conf.PIKO_IP, _conf.PIKO_PASSWORD, logging)
        _data = PrepareData(logging)
        _Sma = TotalSmaEnergy(logging)

        #~ # Daten vom Piko holen
        #~ retStat = _Piko.FetchData(Timers=True, Portal=True, Header=True, Data=True)
        #~ pikoData = _Piko.GetFetchedData(False)
        #~ _data.Dbg_Print(_Piko, pikoData)
        #~ sunSpec = _data.Prepare(_Piko, pikoData, _FirstRun)
        #~ for dataSet in sunSpec:
            #~ des = dataSet[0]
            #~ vAdr = dataSet[1] - 1
            #~ leng = dataSet[2]
            #~ val = dataSet[3]
            #~ skr = dataSet[4] - 1
            #~ vSkr = dataSet[5]

            #~ print ("\n%s" % (des.strip()))
            #~ print ("Wert - Adr: %d, Wert: %s" % (vAdr, str(val)))

            #~ if (skr > 0):
                #~ print ("Dkal - Adr: %d, Skal: %s" % (skr, str(vSkr)))

        # Daten vom SMA holen
        #_Sma.FetchSmaTotal(False)

        identity, context = setup_server()
        asyncio.run(run_updating_server(context, identity, args=(context,_Sma,_Piko,_data)), debug=True)

    except IOError as e:
        log.error("IOError: {}".format(e.msg))
        print('IOError')

    except:
        for info in sys.exc_info():
            log.error("Fehler _main: {}".format(info))
            print("Fehler _main: {}".format(info))

# # Ende Funktion: ' _main' #######################################################################

# #################################################################################################
# #  Funktion: 'Einsprung beim Aufruf  '
# #################################################################################################
if __name__ == '__main__':

    _main(sys.argv)

# # DateiEnde #####################################################################################
