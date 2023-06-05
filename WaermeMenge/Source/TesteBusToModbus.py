#!/usr/bin/env python
# -*- coding: utf-8 -*-

# #################################################################################################
## \brief     Piko Inverter communication software
#  \details
#  \file      TestPikoToModBus.py
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
bDebug = True
bDebugOnLinux = True

# Damit kann aus einem andern Pfad importiert werden. Diejenigen die lokal verwendet werden, vor der Pfaderweiterung importieren
if(bDebug == False):
    importPath = '/mnt/dietpi_userdata/Common'

elif(bDebugOnLinux == True):
    #importPath = 'home/gerhard/Grafana/Common'
    importPath = '/home/gerhard/Grafana/PikoToModbus'

else:
    importPath = 'D:\\Users\\Download\\PvAnlage\\Common'

# #################################################################################################
# # Python Imports (Standard Library)
# #################################################################################################

from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from pymodbus.register_read_message import ReadHoldingRegistersResponse
import ctypes
import sys
from datetime import datetime
import time

sys.path.insert(0, importPath)
import locConfiguration as _conf

# --------------------------------------------------------------------------- #
# configure the client logging
# --------------------------------------------------------------------------- #
import logging
FORMAT = ('%(asctime)-15s %(threadName)-15s '
          '%(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.ERROR)

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

SunSpecUnit = 126
SmaUnit = 3

# ------------------------------------------------------------------------#
# Define client
# ------------------------------------------------------------------------#
# Teensy
Weekday = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
Vers_Addr   =   1000
SoBus1_Addr =   1100
SoBus2_Addr =   1110
PumpeSo_Addr    = 1200
PumpeFK_Addr    = 1202
BrennSperr_Addr = 1204
OW_Addr     =   2000
eBus1_Addr  =   3000
eBus2_Addr  =   3500
DsInternal  =   '40:6:186:150:6:0:0:103'    #[40, 6, 186, 150, 6, 0, 0, 103]
DsTPO       =   '40:141:48:52:12:0:0:199'   #[40, 141, 48, 52, 12, 0, 0, 199]
DsH2O       =   '40:241:68:200:6:0:0:89'    #[40, 241, 68, 200, 6, 0, 0, 89]
DsH2OWarm   =   '40:93:138:200:6:0:0:248'
Heizung   =     '40:46:105:200:6:0:0:173'

modbus = ModbusClient('192.168.2.39', port=502)
DefaultUnit = 3
WaermeEnergieProfil = (
                    ('   Version',Vers_Addr, 8, 0, 's', DefaultUnit),
                    ('     Gas',SoBus1_Addr, 2, 0, 'u', DefaultUnit),
                    ('  Wasser',SoBus2_Addr, 2, 0, 'u', DefaultUnit),
                    ('      PSO',PumpeSo_Addr, 2, 0, 'u', DefaultUnit),
                    ('      PFK',PumpeFK_Addr, 2, 0, 'u', DefaultUnit),
                    ('     BRSP',BrennSperr_Addr, 2, 0, 'u', DefaultUnit),
                    (' Ow-Val00',OW_Addr +  0, 2, 0, 'f', DefaultUnit),
                    (' Ow-Adr01',OW_Addr +  2, 1, 0, 's', DefaultUnit),
                    (' Ow-Adr02',OW_Addr +  3, 1, 0, 's', DefaultUnit),
                    (' Ow-Adr03',OW_Addr +  4, 1, 0, 's', DefaultUnit),
                    (' Ow-Adr04',OW_Addr +  5, 1, 0, 's', DefaultUnit),
                    (' Ow-Adr05',OW_Addr +  6, 1, 0, 's', DefaultUnit),
                    (' Ow-Adr06',OW_Addr +  7, 1, 0, 's', DefaultUnit),
                    (' Ow-Adr07',OW_Addr +  8, 1, 0, 's', DefaultUnit),
                    (' Ow-Adr08',OW_Addr +  9, 1, 0, 's', DefaultUnit),
                    (' Ow-Val10',OW_Addr + 10, 2, 0, 'f', DefaultUnit),
                    (' Ow-Adr11',OW_Addr + 12, 1, 0, 's', DefaultUnit),
                    (' Ow-Adr12',OW_Addr + 13, 1, 0, 's', DefaultUnit),
                    (' Ow-Adr13',OW_Addr + 14, 1, 0, 's', DefaultUnit),
                    (' Ow-Adr14',OW_Addr + 15, 1, 0, 's', DefaultUnit),
                    (' Ow-Adr15',OW_Addr + 16, 1, 0, 's', DefaultUnit),
                    (' Ow-Adr16',OW_Addr + 17, 1, 0, 's', DefaultUnit),
                    (' Ow-Adr17',OW_Addr + 18, 1, 0, 's', DefaultUnit),
                    (' Ow-Adr18',OW_Addr + 19, 1, 0, 's', DefaultUnit),
                    (' Ow-Val20',OW_Addr + 20, 2, 0, 'f', DefaultUnit),
                    (' Ow-Adr21',OW_Addr + 22, 1, 0, 's', DefaultUnit),
                    (' Ow-Adr22',OW_Addr + 23, 1, 0, 's', DefaultUnit),
                    (' Ow-Adr23',OW_Addr + 24, 1, 0, 's', DefaultUnit),
                    (' Ow-Adr24',OW_Addr + 25, 1, 0, 's', DefaultUnit),
                    (' Ow-Adr25',OW_Addr + 26, 1, 0, 's', DefaultUnit),
                    (' Ow-Adr26',OW_Addr + 27, 1, 0, 's', DefaultUnit),
                    (' Ow-Adr27',OW_Addr + 28, 1, 0, 's', DefaultUnit),
                    (' Ow-Adr28',OW_Addr + 29, 1, 0, 's', DefaultUnit),
                    (' Ow-Val30',OW_Addr + 30, 2, 0, 'f', DefaultUnit),
                    (' Ow-Adr31',OW_Addr + 32, 1, 0, 's', DefaultUnit),
                    (' Ow-Adr32',OW_Addr + 33, 1, 0, 's', DefaultUnit),
                    (' Ow-Adr33',OW_Addr + 34, 1, 0, 's', DefaultUnit),
                    (' Ow-Adr34',OW_Addr + 35, 1, 0, 's', DefaultUnit),
                    (' Ow-Adr35',OW_Addr + 36, 1, 0, 's', DefaultUnit),
                    (' Ow-Adr36',OW_Addr + 37, 1, 0, 's', DefaultUnit),
                    (' Ow-Adr37',OW_Addr + 38, 1, 0, 's', DefaultUnit),
                    (' Ow-Adr38',OW_Addr + 39, 1, 0, 's', DefaultUnit),
                    (' Ow-Val40',OW_Addr + 40, 2, 0, 'f', DefaultUnit),
                    (' Ow-Adr41',OW_Addr + 42, 1, 0, 's', DefaultUnit),
                    (' Ow-Adr42',OW_Addr + 43, 1, 0, 's', DefaultUnit),
                    (' Ow-Adr43',OW_Addr + 44, 1, 0, 's', DefaultUnit),
                    (' Ow-Adr44',OW_Addr + 45, 1, 0, 's', DefaultUnit),
                    (' Ow-Adr45',OW_Addr + 46, 1, 0, 's', DefaultUnit),
                    (' Ow-Adr46',OW_Addr + 47, 1, 0, 's', DefaultUnit),
                    (' Ow-Adr47',OW_Addr + 48, 1, 0, 's', DefaultUnit),
                    (' Ow-Adr48',OW_Addr + 49, 1, 0, 's', DefaultUnit),
                    ('timeStamp',eBus1_Addr +  0, 2, 0, 'u', DefaultUnit),
                    ('      TKO',eBus1_Addr +  2, 2, 0, 'f', DefaultUnit),
                    ('      TFK',eBus1_Addr +  4, 2, 0, 'f', DefaultUnit),
                    ('      TSO',eBus1_Addr +  6, 2, 0, 'f', DefaultUnit),
                    ('      TSU',eBus1_Addr +  8, 2, 0, 'f', DefaultUnit),
                    ('      TPU',eBus1_Addr + 10, 2, 0, 'f', DefaultUnit),
        )

for i in range(1):
    print (f'\nLauf : {i}')
# ----------------------------------------------------------------------- #
    modbus.connect()
    WaermeEnergieProfilData = {}
    WaermeEnergieProfilData['TInternal'] = float(-127.0)
    WaermeEnergieProfilData['TPO'] = float(-127.0)
    WaermeEnergieProfilData['TWasser'] = float(-127.0)
    WaermeEnergieProfilData['TWarmWasser'] = float(-127.0)
    WaermeEnergieProfilData['THeizung'] = float(-127.0)
    WaermeEnergieProfilData['PSO'] = int(-1)
    WaermeEnergieProfilData['PFK'] = int(-1)
    WaermeEnergieProfilData['BRSP'] = int(-1)
    OneWire = []

    for dataSet in WaermeEnergieProfil:
        UNIT = dataSet[5]

        adrOfs = 0
        if (SunSpecUnit == UNIT):
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
            sk = modbus.read_holding_registers(skr, 1, unit=UNIT)

        raw = modbus.read_holding_registers(adr, leng, unit=UNIT)
        #print(raw)
        if isinstance(raw, ReadHoldingRegistersResponse):
            #print (f'leng {leng}')
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
                #print(raw.registers[0])
                TranslateScale=convert1()
                TranslateScale.u16 = 0

                if (skr > 0):
                    TranslateScale.u16 = sk.registers[0]
                    #print(sk.registers[0])

                val = Translate.s16*(10**(TranslateScale.s16))
                #print(Translate.s16)
                #print(Translate.u16)

                if (Translate.u16 == 0xFFFF) or (Translate.u16 == 0x8000):
                    val = 0

            # OneWire Sensoren zusammenbauen
            # Ds Adresse ['0x28','0x6','0xba','0x96','0x6','0x0','0x0','0x67] interner Sensor
            if ('Ow-' in DictKey):
                if (Einheit == 'f'):
                    WaermeEnergieProfilData[str(adr + adrOfs)] = valF
                else:
                    WaermeEnergieProfilData[str(adr + adrOfs)] = val

            elif (Einheit == 'f'):
                WaermeEnergieProfilData[DictKey] = valF
            #    print(f'{des} ({adr}) {val} {valF:0.2f}')
            else:
                WaermeEnergieProfilData[DictKey] = val
            #    print(f'{des} ({adr}) {val} {val}')

        #else:
        #    print('\nAdresse:[{}] nicht vorhanden'.format(adr))


    # ----------------------------------------------------------------------- #
    # close the client
    # ----------------------------------------------------------------------- #
    modbus.close()

    DsAdr = []
    DsVal = []
    OW = f"{(WaermeEnergieProfilData[str(OW_Addr + 2)])}:{(WaermeEnergieProfilData[str(OW_Addr + 3)])}:{(WaermeEnergieProfilData[str(OW_Addr + 4)])}:{(WaermeEnergieProfilData[str(OW_Addr + 5)])}:{(WaermeEnergieProfilData[str(OW_Addr + 6)])}:{(WaermeEnergieProfilData[str(OW_Addr + 7)])}:{(WaermeEnergieProfilData[str(OW_Addr + 8)])}:{(WaermeEnergieProfilData[str(OW_Addr + 9)])}"
    DsVal.append(WaermeEnergieProfilData[str(OW_Addr + 0)])
    DsAdr.append(OW)

    OW = f"{(WaermeEnergieProfilData[str(OW_Addr + 12)])}:{(WaermeEnergieProfilData[str(OW_Addr + 13)])}:{(WaermeEnergieProfilData[str(OW_Addr + 14)])}:{(WaermeEnergieProfilData[str(OW_Addr + 15)])}:{(WaermeEnergieProfilData[str(OW_Addr + 16)])}:{(WaermeEnergieProfilData[str(OW_Addr + 17)])}:{(WaermeEnergieProfilData[str(OW_Addr + 18)])}:{(WaermeEnergieProfilData[str(OW_Addr + 19)])}"
    DsVal.append(WaermeEnergieProfilData[str(OW_Addr + 10)])
    DsAdr.append(OW)

    OW = f"{(WaermeEnergieProfilData[str(OW_Addr + 22)])}:{(WaermeEnergieProfilData[str(OW_Addr + 23)])}:{(WaermeEnergieProfilData[str(OW_Addr + 24)])}:{(WaermeEnergieProfilData[str(OW_Addr + 25)])}:{(WaermeEnergieProfilData[str(OW_Addr + 26)])}:{(WaermeEnergieProfilData[str(OW_Addr + 27)])}:{(WaermeEnergieProfilData[str(OW_Addr + 28)])}:{(WaermeEnergieProfilData[str(OW_Addr + 29)])}"
    DsVal.append(WaermeEnergieProfilData[str(OW_Addr + 20)])
    DsAdr.append(OW)

    OW = f"{(WaermeEnergieProfilData[str(OW_Addr + 32)])}:{(WaermeEnergieProfilData[str(OW_Addr + 33)])}:{(WaermeEnergieProfilData[str(OW_Addr + 34)])}:{(WaermeEnergieProfilData[str(OW_Addr + 35)])}:{(WaermeEnergieProfilData[str(OW_Addr + 36)])}:{(WaermeEnergieProfilData[str(OW_Addr + 37)])}:{(WaermeEnergieProfilData[str(OW_Addr + 38)])}:{(WaermeEnergieProfilData[str(OW_Addr + 39)])}"
    DsVal.append(WaermeEnergieProfilData[str(OW_Addr + 30)])
    DsAdr.append(OW)

    OW = f"{(WaermeEnergieProfilData[str(OW_Addr + 42)])}:{(WaermeEnergieProfilData[str(OW_Addr + 43)])}:{(WaermeEnergieProfilData[str(OW_Addr + 44)])}:{(WaermeEnergieProfilData[str(OW_Addr + 45)])}:{(WaermeEnergieProfilData[str(OW_Addr + 46)])}:{(WaermeEnergieProfilData[str(OW_Addr + 47)])}:{(WaermeEnergieProfilData[str(OW_Addr + 48)])}:{(WaermeEnergieProfilData[str(OW_Addr + 49)])}"
    DsVal.append(WaermeEnergieProfilData[str(OW_Addr + 40)])
    DsAdr.append(OW)

    for k in range(len(DsAdr)):
        if(DsInternal == DsAdr[k]):
            WaermeEnergieProfilData['TInternal'] = DsVal[k]
        if(DsTPO == DsAdr[k]):
            WaermeEnergieProfilData['TPO'] = DsVal[k]
        if(DsH2O == DsAdr[k]):
            WaermeEnergieProfilData['TWasser'] = DsVal[k]
        if(DsH2OWarm == DsAdr[k]):
            WaermeEnergieProfilData['TWarmWasser'] = DsVal[k]
        if(Heizung == DsAdr[k]):
            WaermeEnergieProfilData['THeizung'] = DsVal[k]


    print (f"Ds Adr: {(WaermeEnergieProfilData[str(OW_Addr + 2)]): 4}:{(WaermeEnergieProfilData[str(OW_Addr + 3)]): 4}:{(WaermeEnergieProfilData[str(OW_Addr + 4)]): 4}:{(WaermeEnergieProfilData[str(OW_Addr + 5)]): 4}:{(WaermeEnergieProfilData[str(OW_Addr + 6)]): 4}:{(WaermeEnergieProfilData[str(OW_Addr + 7)]): 4}:{(WaermeEnergieProfilData[str(OW_Addr + 8)]): 4}:{(WaermeEnergieProfilData[str(OW_Addr + 9)]): 4} Temp: {WaermeEnergieProfilData[str(OW_Addr + 0)]:0.2f}")

    print (f"Ds Adr: {(WaermeEnergieProfilData[str(OW_Addr + 12)]): 4}:{(WaermeEnergieProfilData[str(OW_Addr + 13)]): 4}:{(WaermeEnergieProfilData[str(OW_Addr + 14)]): 4}:{(WaermeEnergieProfilData[str(OW_Addr + 15)]): 4}:{(WaermeEnergieProfilData[str(OW_Addr + 16)]): 4}:{(WaermeEnergieProfilData[str(OW_Addr + 17)]): 4}:{(WaermeEnergieProfilData[str(OW_Addr + 18)]): 4}:{(WaermeEnergieProfilData[str(OW_Addr + 19)]): 4} Temp: {WaermeEnergieProfilData[str(OW_Addr + 10)]:0.2f}")

    print (f"Ds Adr: {(WaermeEnergieProfilData[str(OW_Addr + 22)]): 4}:{(WaermeEnergieProfilData[str(OW_Addr + 23)]): 4}:{(WaermeEnergieProfilData[str(OW_Addr + 24)]): 4}:{(WaermeEnergieProfilData[str(OW_Addr + 25)]): 4}:{(WaermeEnergieProfilData[str(OW_Addr + 26)]): 4}:{(WaermeEnergieProfilData[str(OW_Addr + 27)]): 4}:{(WaermeEnergieProfilData[str(OW_Addr + 28)]): 4}:{(WaermeEnergieProfilData[str(OW_Addr + 29)]): 4} Temp: {WaermeEnergieProfilData[str(OW_Addr + 20)]:0.2f}")

    print (f"Ds Adr: {(WaermeEnergieProfilData[str(OW_Addr + 32)]): 4}:{(WaermeEnergieProfilData[str(OW_Addr + 33)]): 4}:{(WaermeEnergieProfilData[str(OW_Addr + 34)]): 4}:{(WaermeEnergieProfilData[str(OW_Addr + 35)]): 4}:{(WaermeEnergieProfilData[str(OW_Addr + 36)]): 4}:{(WaermeEnergieProfilData[str(OW_Addr + 37)]): 4}:{(WaermeEnergieProfilData[str(OW_Addr + 38)]): 4}:{(WaermeEnergieProfilData[str(OW_Addr + 39)]): 4} Temp: {WaermeEnergieProfilData[str(OW_Addr + 30)]:0.2f}")

    print (f"Ds Adr: {(WaermeEnergieProfilData[str(OW_Addr + 42)]): 4}:{(WaermeEnergieProfilData[str(OW_Addr + 43)]): 4}:{(WaermeEnergieProfilData[str(OW_Addr + 44)]): 4}:{(WaermeEnergieProfilData[str(OW_Addr + 45)]): 4}:{(WaermeEnergieProfilData[str(OW_Addr + 36)]): 4}:{(WaermeEnergieProfilData[str(OW_Addr + 47)]): 4}:{(WaermeEnergieProfilData[str(OW_Addr + 48)]): 4}:{(WaermeEnergieProfilData[str(OW_Addr + 49)]): 4} Temp: {WaermeEnergieProfilData[str(OW_Addr + 40)]:0.2f}")



    lt = time.localtime() # Aktuelle, lokale Zeit als Tupel
    # Entpacken des Tupels
    lt_jahr, lt_monat, lt_tag = lt[0:3]        # Datum
    lt_h, lt_m, lt_s = lt[3:6]
    lt_dst = lt[8]                             # Sommerzeit


    timeStamp = WaermeEnergieProfilData['timeStamp']
    print(f'-{timeStamp}-')
    #print(f"-{WaermeEnergieProfilData['timeStamp']}-")

    if (lt_dst == 1):
        timeStamp = timeStamp + 60

    weekH = int(timeStamp) / 60
    #print(f'\nweekH: {weekH}')
    DayOfWeek = int(weekH / 24)
    #print(f'Day: {DayOfWeek}')

    #print(DayOfWeek * 24)
    rTime = (weekH - (DayOfWeek * 24))
    #print(f'rTime: {rTime}')
    Hour = int(rTime)
    #print(f'Hour: {Hour}')

    fMin = (rTime - Hour) * 60;
    #print(f'MinF: {fMin}')
    Min = int(fMin)
    #print(f'Min: {Min}')

    fSek = (fMin - Min) * 60;
    #print(f'fSek: {fSek}')
    Sec = int(fSek)
    #print(f'Sek: {Sec}')
    if(Sec >= 30):
        Sec = 0
        Min += 1
    if(Min >= 60):
        Min = Min - 60
        Hour += 1

    print(f"       Time: {Weekday[DayOfWeek]}; {Hour:02}:{Min:02}\t{timeStamp}")
    print(f"    Version: {WaermeEnergieProfilData['Version']}")
    print(f"    Gas Imp: {WaermeEnergieProfilData['Gas']}")
    print(f"     Wasser: {WaermeEnergieProfilData['Wasser']}")
    print(f"  TInternal: {WaermeEnergieProfilData['TInternal']:0.2f}")
    print(f"        TPO: {WaermeEnergieProfilData['TPO']:0.2f}")
    print(f"    TWasser: {WaermeEnergieProfilData['TWasser']:0.2f}")
    print(f"TWarmWasser: {WaermeEnergieProfilData['TWarmWasser']:0.2f}")
    print(f"   THeizung: {WaermeEnergieProfilData['THeizung']:0.2f}")
    print(f"        TKO: {WaermeEnergieProfilData['TKO']:0.2f}")
    print(f"        TFK: {WaermeEnergieProfilData['TFK']:0.2f}")
    print(f"        TSO: {WaermeEnergieProfilData['TSO']:0.2f}")
    print(f"        TSU: {WaermeEnergieProfilData['TSU']:0.2f}")
    print(f"        TPU: {WaermeEnergieProfilData['TPU']:0.2f}")
    print(f"        PSO: {WaermeEnergieProfilData['PSO']:0.2f}")
    print(f"        PFK: {WaermeEnergieProfilData['PFK']:0.2f}")
    print(f"       BRSP: {WaermeEnergieProfilData['BRSP']:0.2f}")

#    time.sleep(60)
