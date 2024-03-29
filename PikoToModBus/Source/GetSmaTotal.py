#!/usr/bin/env python
# -*- coding: utf-8 -*-

# #################################################################################################
## \brief
#  \details
#  \file      GetSmaTotal.py
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
    importPath = '/home/users/Grafana/Common'

else:
    importPath = 'D:\\Users\\Download\\PvAnlage\\Common'

# #################################################################################################
# # Python Imports (Standard Library)
# #################################################################################################

from pymodbus.client import ModbusTcpClient as ModbusClient
from pymodbus.register_read_message import ReadHoldingRegistersResponse
import ctypes
import sys
import os
import locConfiguration as _conf
from datetime import datetime

# #################################################################################################
# # Python Imports (site-packages)
# #################################################################################################
sys.path.insert(0, importPath)
import Utils

# ------------------------------------------------------------------------#
# Define client
# ------------------------------------------------------------------------#
#SMA
modbus = ModbusClient('192.168.2.43' , port=_conf.MODBUS_PORT)
modbus.connect()

# #################################################################################################
# These classes/structures/unions, allow easy conversion between
# modbus 16bit registers and ctypes (a useful format)
# #################################################################################################

# Two bytes (16 bit) based types
class x2u8Struct(ctypes.Structure):
    _fields_ = [("h", ctypes.c_uint8),
                ("l", ctypes.c_uint8)]
class convertChar(ctypes.Union):
    _fields_ = [("u8", x2u8Struct),
                ("u16", ctypes.c_uint16),
                ("s16", ctypes.c_int16)]

# Single register (16 bit) based types
class convert1(ctypes.Union):
    _fields_ = [("u16", ctypes.c_uint16),
                ("s16", ctypes.c_int16)]

# Two register (32 bit) based types
class x2u16Struct(ctypes.Structure):
    _fields_ = [("h", ctypes.c_uint16),
                ("l", ctypes.c_uint16)]
class convert2(ctypes.Union):
    _fields_ = [("float", ctypes.c_float),
                ("u16", x2u16Struct),
                ("sint32", ctypes.c_int32),
                ("uint32", ctypes.c_uint32)]

# Four register (64 bit) based types
class x4u16Struct(ctypes.Structure):
    _fields_ = [("hh", ctypes.c_uint16),
                ("hl", ctypes.c_uint16),
                ("lh", ctypes.c_uint16),
                ("ll", ctypes.c_uint16)]
class convert4(ctypes.Union):
    _fields_ = [("u16", x4u16Struct),
                ("sint64", ctypes.c_int64),
                ("uint64", ctypes.c_uint64)]

# #################################################################################################
# # Funktionen
# # Prototypen
# # if __name__ == '__main__':
# #################################################################################################

# #################################################################################################
# # Classes: PrepareDate
## \details#
#
# #################################################################################################
class TotalSmaEnergy():


# #################################################################################################
# # Funktion: ' Constructor '
## \details Die Initialisierung der Klasse KeepAlive
#   \param[in]  self der Objectpointer
#   \param[in]  interval
#   \param[in] CallBack
#   \return -
# #################################################################################################
    def __init__(self, logger):

        self.log = logger.getLogger('SmaEnergy')
        self.log.info("gestartet")

        self.Data = {}

# # Ende Funktion: ' Constructor ' ################################################################

# #################################################################################################
# # Funktion: ' Destructor '
# #################################################################################################
    #def __del__(self):

# # Ende Funktion: ' Destructor ' #################################################################

# #################################################################################################
# #  Funktion: '_FetchSmaTotal '
## 	\details
#   \param[in]
#   \return     -
# #################################################################################################
    def FetchSmaTotal(self, WriteOut):

        SunSpecUnit = 126
        SmaUnit = 3
        SmaProfil = ()

        try:
            if (WriteOut == False):
                SmaProfil = (('    Tagesertrag',30535, 2,0, SmaUnit),)
            else:
                SmaProfil = (
                            ('   Seriennummer',40053,16,0, SunSpecUnit),
                            ('  Softwarepaket',40045, 8,0, SunSpecUnit),
                            ('    Geraetetyp1',40240, 1,0, SunSpecUnit),
                            ('    Geraetetyp2',40037, 8,0, SunSpecUnit),
                            ('  Gesamtertrag1',40303, 4,0, SunSpecUnit),
                            ('  Gesamtertrag2',40210, 2,40212, SunSpecUnit),
                            ('       Leistung',40200, 1,40201, SunSpecUnit),
                            ('   Ac1 Spannung',40196, 1,40199, SunSpecUnit),
                            ('   Ac2 Spannung',40197, 1,40199, SunSpecUnit),
                            ('   Ac3 Spannung',40198, 1,40199, SunSpecUnit),
                            ('      Ac1 Strom',40189, 1,40192, SunSpecUnit),
                            ('      Ac2 Strom',40190, 1,40192, SunSpecUnit),
                            ('      Ac3 Strom',40191, 1,40192, SunSpecUnit),
                            ('Innentemperatur',40219, 1,0, SunSpecUnit),
                            ('   Dc1 Spannung',40642, 1,40625, SunSpecUnit),
                            ('   Dc2 Spannung',40662, 1,40625, SunSpecUnit),
                            ('      Dc1 Strom',40641, 1,40624, SunSpecUnit),
                            ('      Dc2 Strom',40661, 1,40624, SunSpecUnit),
                            ('   Dc1 Leistung',40643, 1,40626, SunSpecUnit),
                            ('   Dc2 Leistung',40663, 1,40626, SunSpecUnit),
                            (' Betriebsstatus',40224, 1,0, SunSpecUnit),
                            (' Ereignisnummer',40226, 2,0, SunSpecUnit),
                            ('    MAC-Adresse',40076, 4,0, SunSpecUnit),
                            ('     IP-Adresse',40097, 8,0, SunSpecUnit),
                            #('  Gesamtertrag3',30529, 2,0, SmaUnit),
                            ('    Tagesertrag',30535, 2,0, SmaUnit)
                            )

            sunSpecData = {}

            self.Data['Now'] = datetime.now()

            for dataSet in SmaProfil:
                UNIT = dataSet[4]

                adrOfs = 0
                if (SunSpecUnit == UNIT):
                    adrOfs = 1

                des = dataSet[0]
                adr = dataSet[1] - adrOfs
                leng = dataSet[2]
                skr = dataSet[3] - adrOfs
                Translate = 0
                TranslateScale = 0

                raw = 0
                sk = 0
                val = ''
                if (skr > 0):
                    sk = modbus.read_holding_registers(skr, 1, slave=UNIT)

                raw = modbus.read_holding_registers(adr, leng, slave=UNIT)
                if isinstance(raw, ReadHoldingRegistersResponse):
                    if (leng == 16):
                        Translate = convertChar()
                        for chrGrp in raw.registers:
                            if (chrGrp == 0):
                                break
                            Translate.u16 = chrGrp
                            val = val + chr(Translate.u8.l) + chr(Translate.u8.h)

                    elif (leng == 8):
                        Translate = convertChar()
                        for chrGrp in raw.registers:
                            if (chrGrp == 0):
                                break
                            Translate.u16 = chrGrp
                            val = val + chr(Translate.u8.l) + chr(Translate.u8.h)

                    elif (leng == 4):
                        Translate=convert4()
                        Translate.u16.hh = raw.registers[3]
                        Translate.u16.hl = raw.registers[2]
                        Translate.u16.lh = raw.registers[1]
                        Translate.u16.ll = raw.registers[0]
                        val = Translate.uint64

                    elif (leng == 2):
                        Translate=convert2()
                        Translate.u16.h = raw.registers[1]
                        Translate.u16.l = raw.registers[0]
                        val = Translate.uint32

                    else:
                        Translate=convert1()
                        Translate.u16=raw.registers[0]
                        TranslateScale=convert1()
                        TranslateScale.u16 = 0

                        if (skr > 0):
                            TranslateScale.u16 = sk.registers[0]

                        val = Translate.s16*(10**(TranslateScale.s16))

                        if (Translate.u16 == 0xFFFF) or (Translate.u16 == 0x8000):
                            val = 0

                    sunSpecData[str(adr + adrOfs)] = val

                    if ((adr + 1) == 40303): #      Gesamtertrag1
                        timestamp = "{}.{}.{} {}:{} {}".format(self.Data['Now'].strftime("%d"), self.Data['Now'].strftime("%m"), self.Data['Now'].strftime("%Y"), self.Data['Now'].strftime("%H"), self.Data['Now'].strftime("%M"), self.Data['Now'].strftime("%S"))
                        datStream = "TimeStamp: {}    Total energy: {} Wh\n".format(timestamp, val)

                        strFolder = "{}{}".format(_conf.EXPORT_FILEPATH, self.Data['Now'].strftime("%Y"))
                        fileName = "{}/SmaTotalEnergy.log".format(strFolder)

                        if (not os.path.exists(strFolder)):
                            os.mkdir(strFolder)
                            # chmod sendet Oktal Zahlen, Python2 0 davor, python 3 0o
                            os.chmod(strFolder, 0o777)

                        Utils._write_File(fileName , datStream, "a")
            modbus.close()

            # Sma loescht die Tagesleistung um Mitternacht...
            if (sunSpecData['30535'] > 0):
                self.Data['TodayWh'] = sunSpecData['30535']

            if (WriteOut == True):
                self.Data['RelVer'] =    sunSpecData['40045'].replace('\00', '/00')
                self.Data['host'] =      sunSpecData['40097']
                self.Data['Status'] =    sunSpecData['40224']
                #self.Data['StatusTxt'] = sunSpecData['aaa']
                self.Data['InvName'] =   'PowerDorf'
                self.Data['InvSN'] =     sunSpecData['40053']
                self.Data['InvModel'] =  'Sunnboy 3.0'
                self.Data['InvString'] = '2'
                self.Data['InvPhase'] =  '1'
                self.Data['TotalWh'] =   sunSpecData['40303']
                #self.Data['TotalWh2'] =   sunSpecData['30529']

                self.Data['CC_P'] =    sunSpecData['40643'] + sunSpecData['40663']
                self.Data['CA_P'] =    sunSpecData['40200']

                self.Data['CC1_U'] =   sunSpecData['40642']
                self.Data['CC1_I'] =   sunSpecData['40641']
                self.Data['CC1_P'] =   sunSpecData['40643']
                self.Data['CC1_T'] =   sunSpecData['40219']

                self.Data['CC2_U'] =   sunSpecData['40662']
                self.Data['CC2_I'] =   sunSpecData['40661']
                self.Data['CC2_P'] =   sunSpecData['40663']
                self.Data['CC2_T'] =   sunSpecData['40219']

                self.Data['CA1_U'] =   sunSpecData['40196']
                self.Data['CA1_I'] =   sunSpecData['40189']
                self.Data['CA1_P'] =   sunSpecData['40200']
                self.Data['CA1_T'] =   sunSpecData['40219']

                self.log.info("")
                self.log.info("TimeStamp       : {:%m/%d/%y %H:%M %S}".format(self.Data['Now']))
                self.log.info("Comm software   : SMA v%s" % (self.Data['RelVer']))
                self.log.info("Comm host       : %s" % self.Data['host'])
                self.log.info("Inverter Status : %d" % self.Data['Status'])
                self.log.info("Inverter Name   : %s" % self.Data['InvName'])
                self.log.info("Inverter SN     : %s" % self.Data['InvSN'])
                self.log.info("Inverter Model  : %s" % self.Data['InvModel'])
                self.log.info("Inverter String : %s" % self.Data['InvString'])
                self.log.info("Inverter Phase  : %s" % self.Data['InvPhase'])
                self.log.info("Total energy    : %d Wh" % self.Data['TotalWh'])
                #self.log.info("Total energy2   : %d Wh" % self.Data['TotalWh2'])
                self.log.info("Today energy    : %d Wh" % self.Data['TodayWh'])
                self.log.info("DC Power        : %5d W\tAC Power : %5d W" % (self.Data['CC_P'], self.Data['CA_P']))
                self.log.info('DC String 1     : %5.1f V   %4.2f A   %4d W   T= %5.2f C' % (self.Data['CC1_U'], self.Data['CC1_I'], self.Data['CC1_P'], self.Data['CC1_T']))
                self.log.info('DC String 2     : %5.1f V   %4.2f A   %4d W   T= %5.2f C' % (self.Data['CC2_U'], self.Data['CC2_I'], self.Data['CC2_P'], self.Data['CC2_T']))
                self.log.info('AC Phase 1      : %5.1f V   %4.2f A   %4d W   T= %5.2f C' % (self.Data['CA1_U'], self.Data['CA1_I'], self.Data['CA1_P'], self.Data['CA1_T']))

        except:
            for info in sys.exc_info():
                self.log.error("FetchSmaTotal Fehler: {}".format(info))
                print("FetchSmaTotal Fehler: {}".format(info))


    # # Ende Funktion: ' _FetchSmaTotal(' ###################################################################

# # Ende Klasse: ' GetSmaTotal ' ##################################################################

# # DateiEnde #####################################################################################
