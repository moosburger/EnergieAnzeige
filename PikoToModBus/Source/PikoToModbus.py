#!/usr/bin/env python
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
# # Python Imports (Standard Library)
# #################################################################################################
import ctypes
import sys
import time

# --------------------------------------------------------------------------- #
# import the modbus libraries we need
# --------------------------------------------------------------------------- #
from pymodbus.server.asynchronous import StartTcpServer
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext

# --------------------------------------------------------------------------- #
# import the twisted libraries we need
# --------------------------------------------------------------------------- #
from twisted.internet.task import LoopingCall
# --------------------------------------------------------------------------- #
# import the logging libraries we need
# --------------------------------------------------------------------------- #
import logging

reload(sys)
sys.setdefaultencoding("utf-8")

# #################################################################################################
# # Python Imports (site-packages)
# #################################################################################################

# #################################################################################################
# # private Imports
# #################################################################################################
try:
    PrivateImport = True
    import configuration as _conf
    from PikoCom import (PikoWebRead)
    from PreparePikoData import (PrepareData)
    import SunRiseSet
except:
    PrivateImport = False

# #################################################################################################
# # UmgebungsVariablen
# #################################################################################################

# --------------------------------------------------------------------------- #
# configure the service logging
# --------------------------------------------------------------------------- #
logging.basicConfig()
log = logging.getLogger()
log.setLevel(_conf.LOG_LEVEL) # Levels: NONE, FATAL, ERROR, NOTICE, DEBUG

# #################################################################################################
# # Funktionen
# # Prototypen
# #################################################################################################
_FirstRun = True

# #################################################################################################
# #  Funktion: ' _Fetch_Piko_Data '
## \details        -
#   \param[in]     -
#   \param[in]     -
#   \return          -
# #################################################################################################
def _Fetch_Piko_Data(a):
    """ A worker process that runs every so often and
    updates live values of the context which resides in an SQLite3 database.
    It should be noted that there is a race condition for the update.
    :param arguments: The input arguments to the call    """

    context  = a[0]
    Piko = a[1]
    Data = a[2]
    global _FirstRun

    # Tagsüber oder nachts
    AMh, AMm, UMh, UMm, lt_tag, lt_monat, lt_jahr, lt_h, lt_m, lt_s = SunRiseSet.get_Info()
    log.debug("\tTimeStamp {0:02d}.{1:02d}.{2:4d} {3:02d}:{4:02d}:{5:02d}".format(lt_tag, lt_monat, lt_jahr, lt_h, lt_m, lt_s))

    sunRise = AMh  * 60 + AMm
    sunSet  = UMh  * 60 + UMm
    locNow  = lt_h * 60 + lt_m
    #print sunRise
    #print locNow
    #print sunSet

    if ((locNow < sunRise) or (locNow > sunSet)) and (_FirstRun == False):
        return

    log.debug("\tUpdating the database context")
    #readfunction = 0x03 # read holding registers
    writefunction = 0x10
    slave_id = 126 # slave address

    #print 'FIRSTRUN 1 %s \n' %(str(_FirstRun))
    # Daten vom Piko holen
    retStat = Piko.FetchData(Timers=True, Portal=True, Header=True, Data=True)
    if ((retStat == -1) and (_conf.DEBUG == False)):
        return

    pikoData = Piko.GetFetchedData()
    #Data.Dbg_Print(Piko, pikoData)

    sunSpec = Data.Prepare(Piko, pikoData, _FirstRun)
    for dataSet in sunSpec:
        #print (dataSet)
        des = dataSet[0]
        vAdr = dataSet[1] - 1
        leng = dataSet[2]
        val = dataSet[3]
        skr = dataSet[4] - 1
        vSkr = dataSet[5]

        #print "\n%s" % (des.strip())
        #print "Wert - Adr: %d, Wert: %s" % (vAdr, str(val))
        context[slave_id].setValues(writefunction, vAdr, val)

        if (skr > 0):
            #print "Dkal - Adr: %d, Skal: %s" % (skr, str(vSkr))
            context[slave_id].setValues(writefunction, skr, vSkr)

    _FirstRun = False
    #print '\n\nFIRSTRUN 2 %s\n\n' %(str(_FirstRun))

# #################################################################################################
# #  Funktion: ' _run_modbus_server '
## \details        -
#   \param[in]     -
#   \param[in]     -
#   \return          -
# #################################################################################################
def _run_modbus_server(Piko, Data):
    global _Loop
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
    identity = ModbusDeviceIdentification()
    identity.VendorName = 'pymodbus'
    identity.ProductCode = 'PM'
    identity.VendorUrl = 'http://github.com/bashwork/pymodbus/'
    identity.ProductName = 'pymodbus Server'
    identity.ModelName = 'pymodbus Server'
    identity.MajorMinorRevision = '2.3.0'

    # ----------------------------------------------------------------------- #
    # run the server you want
    # ----------------------------------------------------------------------- #
    _Loop = LoopingCall(f=_Fetch_Piko_Data, a=(context,Piko,Data))
    _Loop.start(_conf.SCHED_INTERVAL, now=False)  # initially delay by time

    StartTcpServer(context, identity=identity, address=(_conf.INVERTER_IP, _conf.MODBUS_PORT))

# #################################################################################################
# #  Funktion: ' _main '
## \details         Die Einsprungsfunktion, ruft alle Funktionen und Klassen auf.
#   \param[in]    argv
#   \return            -
# #################################################################################################
def _main(argv):

    _FirstRun = True
    try:
        # # Mit dem Piko instanzieren ####################################
        _Piko = PikoWebRead(False, _conf.PIKO_IP, '3edcCFT&')
        _data = PrepareData()

        # Daten vom Piko holen
        #~retStat = _Piko.FetchData(Timers=True, Portal=True, Header=True, Data=True)
        #~pikoData = _Piko.GetFetchedData()
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

        _run_modbus_server(_Piko, _data)

    except:
        for info in sys.exc_info():
            print ("Fehler:", info)

# # Ende Funktion: ' _main' ###########################################################################

# #################################################################################################
# #  Funktion: 'Einsprung beim Aufruf  '
# #################################################################################################
if __name__ == '__main__':

    _main(sys.argv)

# # DateiEnde #####################################################################################
