#!/usr/bin/env python3
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
if (bDebug == False):
    importPath = '/mnt/dietpi_userdata/Common'

elif(bDebugOnLinux == True):
    importPath = '/home/users/Grafana/Common'

else:
    importPath = 'D:\\Users\\Download\\PvAnlage\\Common'

# #################################################################################################
# # Python Imports (Standard Library)
# #################################################################################################
try:
    ImportError = None
    import sys
    import ctypes
    import os
    from datetime import datetime
    from pymodbus.client.sync import ModbusTcpClient as ModbusClient
    from pymodbus.register_read_message import ReadHoldingRegistersResponse

except Exception as e:
    ImportError = e

# #################################################################################################
# # private Imports
# #################################################################################################
try:
    PrivateImportError = None

    sys.path.insert(0, importPath)
    from configuration import Global as _conf

except Exception as e:
    PrivateImportError = e

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
class ModBusHandler():

    try:
        ## Import fehlgeschlagen
        if (PrivateImportError):
            raise IOError(PrivateImportError)

        if (ImportError):
            raise IOError(ImportError)
# #################################################################################################
# # Funktion: ' Constructor '
## \details Die Initialisierung der Klasse KeepAlive
#   \param[in]  self der Objectpointer
#   \param[in]  interval
#   \param[in] CallBack
#   \return -
# #################################################################################################
        def __init__(self, logger):

            try:
                self.log = logger.getLogger('ModBus')
                self.log.info("gestartet")

                # ------------------------------------------------------------------------#
                # Define UNIT ID
                #
                self.SunSpecUnit = 126  # PikoProfil
                self.SmaUnit = 3  # SMA

                # ------------------------------------------------------------------------#
                # Define client
                # ------------------------------------------------------------------------#
                #Piko
                self.modbusPiko = ModbusClient(_conf.MODBUS_PIKO_IP, port=_conf.MODBUS_PORT)
                #SMA
                self.modbusSma = ModbusClient(_conf.MODBUS_SMA_IP, port=_conf.MODBUS_PORT)

            except Exception as e:
                self.log.error("ModBusHandler __init__: {}".format(e))

# # Ende Funktion: ' Constructor ' ################################################################

# #################################################################################################
# # Funktion: ' Destructor '
# #################################################################################################
    #def __del__(self):

# # Ende Funktion: ' Destructor ' #################################################################

# #################################################################################################
# #  Funktion: 'FetchSmaData '
## 	\details
#   \param[in]
#   \return     -
# #################################################################################################
        def FetchSmaData(self, Unit):

            try:
                self.modbusSma.connect()

                adrOfs = 0
                if (self.SunSpecUnit == Unit):
                    adrOfs = 1

                SmaProfil = (
                                ('    Tagesertrag',30535, 2,0),
                                ('   Gesamtertrag',30529, 2,0)
                            )

                SmaProfilData = {}

                for dataSet in SmaProfil:
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
                        sk = self.modbusSma.read_holding_registers(skr, 1, unit=Unit)

                    raw = self.modbusSma.read_holding_registers(adr, leng, unit=Unit)
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

                        SmaProfilData[str(adr + adrOfs)] = val

                self.modbusSma.close()

            except Exception as e:
                self.log.error("FetchSmaData: {}".format(e))

            except:
                self.log.error("FetchSmaData: {}".format(errLog))
                for info in sys.exc_info():
                    self.log.error("{}".format(info))

            return SmaProfilData

    # # Ende Funktion: ' FetchSmaData(' ###################################################################

# #################################################################################################
# #  Funktion: 'FetchPikoData '
## 	\details
#   \param[in]
#   \return     -
# #################################################################################################
        def FetchPikoData(self, Unit):

            try:
                self.modbusPiko.connect()

                adrOfs = 0
                if (self.SunSpecUnit == Unit):
                    adrOfs = 1

                PikoProfil = (
                                ('    Tagesertrag',40670, 2,40212),
                                ('  Gesamtertrag2',40210, 2,40212),
                            )

                PikoProfilData = {}

                for dataSet in PikoProfil:
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
                        sk = self.modbusPiko.read_holding_registers(skr, 1, unit=Unit)

                    raw = self.modbusPiko.read_holding_registers(adr, leng, unit=Unit)
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

                        PikoProfilData[str(adr + adrOfs)] = val

                self.modbusPiko.close()

            except Exception as e:
                self.log.error("FetchPikoData: {}".format(e))

            except:
                self.log.error("FetchPikoData: {}".format(errLog))
                for info in sys.exc_info():
                    self.log.error("{}".format(info))

            return PikoProfilData

    # # Ende Funktion: ' FetchPikoData' ###################################################################

##### Fehlerbehandlung #####################################################
    except IOError as e:
        print('Eine der Bibliotheken konnte nicht geladen werden!\n{}!\n'.format(e))

    except:
        for info in sys.exc_info():
            print ("Fehler: {}".format(info))

# # Ende Klasse: ' ModBusHandler ' ##################################################################

# # DateiEnde #####################################################################################
