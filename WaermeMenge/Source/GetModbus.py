#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# #################################################################################################
## \brief
#  \details
#  \file      GetModbus.py
#
#  \date      Erstellt am: 07.02.2023
#  \author    moosburger
#
# <History\> ######################################################################################
# Version     Datum       Ticket#     Beschreibung
# 1.0         07.02.2023
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
    importPath = '/home/gerhard/Grafana/Common'

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
    from pymodbus.client import ModbusTcpClient as ModbusClient
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
                self.SunSpecUnit = 126 # PikoProfil
                self.DefaultUnit = 3   # Default

                self.Vers_Addr   =   1000
                self.SoBus1_Addr =   1100
                self.SoBus2_Addr =   1110
                self.OW_Addr     =   2000
                self.eBus1_Addr  =   3000
                self.eBus2_Addr  =   3500

                self.DsInternal  =   '40:6:186:150:6:0:0:103'
                self.DsTPO       =   '40:141:48:52:12:0:0:199'
                self.DsH2O       =   '40:241:68:200:6:0:0:89'

                # ------------------------------------------------------------------------#
                # Define client
                # ------------------------------------------------------------------------#
                #Teensy
                self.modbusWaermeEnergie = ModbusClient(_conf.MODBUS_WAERMEENERGIE_IP, port=_conf.MODBUS_PORT)

            except Exception as e:
                self.log.error("ModBusHandler __init__: {}".format(e))

# # Ende Funktion: ' Constructor ' ################################################################

# #################################################################################################
# # Funktion: ' Destructor '
# #################################################################################################
    #def __del__(self):

# # Ende Funktion: ' Destructor ' #################################################################

# #################################################################################################
# #  Funktion: 'FetchWaermeEnergieData '
## 	\details
#   \param[in]
#   \return     -
# #################################################################################################
        def FetchWaermeEnergieData(self):

            try:
                WaermeEnergieProfil = (
                    ('  Version',self.Vers_Addr, 8, 0, 's', self.DefaultUnit),
                    ('      Gas',self.SoBus1_Addr, 2, 0, 'u', self.DefaultUnit),
                    ('   Wasser',self.SoBus2_Addr, 2, 0, 'u', self.DefaultUnit),
                    (' Ow-Val00',self.OW_Addr +  0, 2, 0, 'f', self.DefaultUnit),
                    (' Ow-Adr01',self.OW_Addr +  2, 1, 0, 's', self.DefaultUnit),
                    (' Ow-Adr02',self.OW_Addr +  3, 1, 0, 's', self.DefaultUnit),
                    (' Ow-Adr03',self.OW_Addr +  4, 1, 0, 's', self.DefaultUnit),
                    (' Ow-Adr04',self.OW_Addr +  5, 1, 0, 's', self.DefaultUnit),
                    (' Ow-Adr05',self.OW_Addr +  6, 1, 0, 's', self.DefaultUnit),
                    (' Ow-Adr06',self.OW_Addr +  7, 1, 0, 's', self.DefaultUnit),
                    (' Ow-Adr07',self.OW_Addr +  8, 1, 0, 's', self.DefaultUnit),
                    (' Ow-Adr08',self.OW_Addr +  9, 1, 0, 's', self.DefaultUnit),
                    (' Ow-Val10',self.OW_Addr + 10, 2, 0, 'f', self.DefaultUnit),
                    (' Ow-Adr11',self.OW_Addr + 12, 1, 0, 's', self.DefaultUnit),
                    (' Ow-Adr12',self.OW_Addr + 13, 1, 0, 's', self.DefaultUnit),
                    (' Ow-Adr13',self.OW_Addr + 14, 1, 0, 's', self.DefaultUnit),
                    (' Ow-Adr14',self.OW_Addr + 15, 1, 0, 's', self.DefaultUnit),
                    (' Ow-Adr15',self.OW_Addr + 16, 1, 0, 's', self.DefaultUnit),
                    (' Ow-Adr16',self.OW_Addr + 17, 1, 0, 's', self.DefaultUnit),
                    (' Ow-Adr17',self.OW_Addr + 18, 1, 0, 's', self.DefaultUnit),
                    (' Ow-Adr18',self.OW_Addr + 19, 1, 0, 's', self.DefaultUnit),
                    (' Ow-Val20',self.OW_Addr + 20, 2, 0, 'f', self.DefaultUnit),
                    (' Ow-Adr21',self.OW_Addr + 22, 1, 0, 's', self.DefaultUnit),
                    (' Ow-Adr22',self.OW_Addr + 23, 1, 0, 's', self.DefaultUnit),
                    (' Ow-Adr23',self.OW_Addr + 24, 1, 0, 's', self.DefaultUnit),
                    (' Ow-Adr24',self.OW_Addr + 25, 1, 0, 's', self.DefaultUnit),
                    (' Ow-Adr25',self.OW_Addr + 26, 1, 0, 's', self.DefaultUnit),
                    (' Ow-Adr26',self.OW_Addr + 27, 1, 0, 's', self.DefaultUnit),
                    (' Ow-Adr27',self.OW_Addr + 28, 1, 0, 's', self.DefaultUnit),
                    (' Ow-Adr28',self.OW_Addr + 29, 1, 0, 's', self.DefaultUnit),
                    #~ (' Ow-Val30',self.OW_Addr + 30, 2, 0, 'f', self.DefaultUnit),
                    #~ (' Ow-Adr31',self.OW_Addr + 32, 1, 0, 's', self.DefaultUnit),
                    #~ (' Ow-Adr32',self.OW_Addr + 33, 1, 0, 's', self.DefaultUnit),
                    #~ (' Ow-Adr33',self.OW_Addr + 34, 1, 0, 's', self.DefaultUnit),
                    #~ (' Ow-Adr34',self.OW_Addr + 35, 1, 0, 's', self.DefaultUnit),
                    #~ (' Ow-Adr35',self.OW_Addr + 36, 1, 0, 's', self.DefaultUnit),
                    #~ (' Ow-Adr36',self.OW_Addr + 37, 1, 0, 's', self.DefaultUnit),
                    #~ (' Ow-Adr37',self.OW_Addr + 38, 1, 0, 's', self.DefaultUnit),
                    #~ (' Ow-Adr38',self.OW_Addr + 39, 1, 0, 's', self.DefaultUnit),
                    (' timeStamp',self.eBus1_Addr +  0, 2, 0, 'u', self.DefaultUnit),
                    ('       TKO',self.eBus1_Addr +  2, 2, 0, 'f', self.DefaultUnit),
                    ('       TFK',self.eBus1_Addr +  4, 2, 0, 'f', self.DefaultUnit),
                    ('       TSO',self.eBus1_Addr +  6, 2, 0, 'f', self.DefaultUnit),
                    ('       TSU',self.eBus1_Addr +  8, 2, 0, 'f', self.DefaultUnit),
                    ('       TPU',self.eBus1_Addr + 10, 2, 0, 'f', self.DefaultUnit),
                )

                self.modbusWaermeEnergie.connect()
                WaermeEnergieProfilData = {}
                WaermeEnergieProfilData['TInternal'] = float(-127.0)
                WaermeEnergieProfilData['TPO'] = float(-127.0)
                WaermeEnergieProfilData['TWasser'] = float(-127.0)
                OneWire = []

                for dataSet in WaermeEnergieProfil:
                    UNIT = dataSet[5]

                    adrOfs = 0
                    if (self.SunSpecUnit == UNIT):
                        adrOfs = 1

                    DictKey = dataSet[0].strip()
                    adr = dataSet[1] - adrOfs
                    leng = dataSet[2]
                    skr = dataSet[3] - adrOfs
                    Einheit = dataSet[4]
                    Translate = 0
                    TranslateScale = 0

                    raw = 0
                    sk = 0
                    valF = ''
                    val = ''
                    if (skr > 0):
                        sk = self.modbusWaermeEnergie.read_holding_registers(skr, 1, slave=UNIT)

                    raw = self.modbusWaermeEnergie.read_holding_registers(adr, leng, slave=UNIT)
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
                            valF = float(Translate.float)
                            val = Translate.uint64

                        elif (leng == 2):
                            Translate=convert2()
                            Translate.u16.h = raw.registers[1]
                            Translate.u16.l = raw.registers[0]
                            valF = float(Translate.float)
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

                        # OneWire Sensoren zusammenbauen
                        if ('Ow-' in DictKey):
                            if (Einheit == 'f'):
                                WaermeEnergieProfilData[str(adr + adrOfs)] = valF
                            else:
                                WaermeEnergieProfilData[str(adr + adrOfs)] = val

                        elif (Einheit == 'f'):
                            WaermeEnergieProfilData[DictKey] = valF
                        else:
                            WaermeEnergieProfilData[DictKey] = val

                self.modbusWaermeEnergie.close()

                DsAdr = []
                DsVal = []
                OW = f"{(WaermeEnergieProfilData[str(self.OW_Addr + 2)])}:{(WaermeEnergieProfilData[str(self.OW_Addr + 3)])}:{(WaermeEnergieProfilData[str(self.OW_Addr + 4)])}:{(WaermeEnergieProfilData[str(self.OW_Addr + 5)])}:{(WaermeEnergieProfilData[str(self.OW_Addr + 6)])}:{(WaermeEnergieProfilData[str(self.OW_Addr + 7)])}:{(WaermeEnergieProfilData[str(self.OW_Addr + 8)])}:{(WaermeEnergieProfilData[str(self.OW_Addr + 9)])}"
                DsVal.append(WaermeEnergieProfilData[str(self.OW_Addr + 0)])
                DsAdr.append(OW)

                OW = f"{(WaermeEnergieProfilData[str(self.OW_Addr + 12)])}:{(WaermeEnergieProfilData[str(self.OW_Addr + 13)])}:{(WaermeEnergieProfilData[str(self.OW_Addr + 14)])}:{(WaermeEnergieProfilData[str(self.OW_Addr + 15)])}:{(WaermeEnergieProfilData[str(self.OW_Addr + 16)])}:{(WaermeEnergieProfilData[str(self.OW_Addr + 17)])}:{(WaermeEnergieProfilData[str(self.OW_Addr + 18)])}:{(WaermeEnergieProfilData[str(self.OW_Addr + 19)])}"
                DsVal.append(WaermeEnergieProfilData[str(self.OW_Addr + 10)])
                DsAdr.append(OW)

                OW = f"{(WaermeEnergieProfilData[str(self.OW_Addr + 22)])}:{(WaermeEnergieProfilData[str(self.OW_Addr + 23)])}:{(WaermeEnergieProfilData[str(self.OW_Addr + 24)])}:{(WaermeEnergieProfilData[str(self.OW_Addr + 25)])}:{(WaermeEnergieProfilData[str(self.OW_Addr + 26)])}:{(WaermeEnergieProfilData[str(self.OW_Addr + 27)])}:{(WaermeEnergieProfilData[str(self.OW_Addr + 28)])}:{(WaermeEnergieProfilData[str(self.OW_Addr + 29)])}"
                DsVal.append(WaermeEnergieProfilData[str(self.OW_Addr + 20)])
                DsAdr.append(OW)

                for k in range(len(DsAdr)):
                    if(self.DsInternal == DsAdr[k]):
                        WaermeEnergieProfilData['TInternal'] = DsVal[k]
                    if(self.DsTPO == DsAdr[k]):
                        WaermeEnergieProfilData['TPO'] = DsVal[k]
                    if(self.DsH2O == DsAdr[k]):
                        WaermeEnergieProfilData['TWasser'] = DsVal[k]

            except Exception as e:
                self.log.error("FetchWaermeEnergieData: {}".format(e))

            except:
                self.log.error("FetchWaermeEnergieData: {}".format(errLog))
                for info in sys.exc_info():
                    self.log.error("{}".format(info))

            return WaermeEnergieProfilData

    # # Ende Funktion: ' FetchWaermeEnergieData(' ###################################################################

##### Fehlerbehandlung #####################################################
    except IOError as e:
        print('Eine der Bibliotheken konnte nicht geladen werden!\n{}!\n'.format(e))

    except:
        for info in sys.exc_info():
            print ("Fehler: {}".format(info))

# # Ende Klasse: ' ModBusHandler ' ##################################################################

# # DateiEnde #####################################################################################
