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
#Piko
#~ modbus = ModbusClient('192.168.2.42' , port=_conf.MODBUS_PORT)
#~ sunSpec = (
            #~ ('   Seriennummer',40053,16,0, SunSpecUnit),
            #~ ('  Softwarepaket',40045, 8,0, SunSpecUnit),
            #~ ('    Geraetetyp1',40240, 1,0, SunSpecUnit),
            #~ ('    Geraetetyp2',40037, 8,0, SunSpecUnit),
            #~ ('  Gesamtertrag1',40303, 4,0, SunSpecUnit),
            #~ ('  Gesamtertrag2',40210, 2,40212, SunSpecUnit),
            #~ ('       Leistung',40200, 1,40201, SunSpecUnit),
            #~ ('    Tagesertrag',40670, 2,40212, SunSpecUnit),
            #~ ('   Ac1 Spannung',40196, 1,40199, SunSpecUnit),
            #~ ('   Ac2 Spannung',40197, 1,40199, SunSpecUnit),
            #~ ('   Ac3 Spannung',40198, 1,40199, SunSpecUnit),
            #~ ('      Ac1 Strom',40189, 1,40192, SunSpecUnit),
            #~ ('      Ac2 Strom',40190, 1,40192, SunSpecUnit),
            #~ ('      Ac3 Strom',40191, 1,40192, SunSpecUnit),
            #~ ('Innentemperatur',40219, 1,0, SunSpecUnit),
            #~ (' And. Innentemp',40222, 1,0, SunSpecUnit),
            #~ ('   Dc1 Spannung',40642, 1,40625, SunSpecUnit),
            #~ ('   Dc2 Spannung',40662, 1,40625, SunSpecUnit),
            #~ ('      Dc1 Strom',40641, 1,40624, SunSpecUnit),
            #~ ('      Dc2 Strom',40661, 1,40624, SunSpecUnit),
            #~ ('   Dc1 Leistung',40643, 1,40626, SunSpecUnit),
            #~ ('   Dc2 Leistung',40663, 1,40626, SunSpecUnit),
            #~ (' Betriebsstatus',40224, 1,0, SunSpecUnit),
            #~ (' Ereignisnummer',40226, 2,0, SunSpecUnit),
            #~ ('    MAC-Adresse',40076, 4,0, SunSpecUnit),
            #~ ('     IP-Adresse',40097, 8,0, SunSpecUnit)
        #~ )

#SMA
#~ modbus = ModbusClient('192.168.2.43' , port=_conf.MODBUS_PORT)
#~ sunSpec = (
                                #~ ('    Tagesertrag',30535, 2,0, SmaUnit),
                                #~ ('       Leistung',30775, 2,0, SmaUnit),
                                #~ ('   Gesamtertrag',30529, 2,0, SmaUnit),
                                #~ ('Innentemperatur',40219, 1,0, SunSpecUnit),
                                #~ ('   Dc1 Spannung',40642, 1,40625, SunSpecUnit),
                                #~ ('   Dc2 Spannung',40662, 1,40625, SunSpecUnit),
                                #~ ('      Dc1 Strom',40641, 1,40624, SunSpecUnit),
                                #~ ('      Dc2 Strom',40661, 1,40624, SunSpecUnit),
                                #~ ('   Dc1 Leistung',40643, 1,40626, SunSpecUnit),
                                #~ ('   Dc2 Leistung',40663, 1,40626, SunSpecUnit)
        #~ )

# Teensy
Weekday = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
Vers_Addr   =   1000
SoBus1_Addr =   1100
SoBus2_Addr =   1110
OW_Addr     =   2000
eBus1_Addr  =   3000
eBus2_Addr  =   3500
DsInternal  =   '40:6:186:150:6:0:0:103'    #[40, 6, 186, 150, 6, 0, 0, 103]
DsTPO       =   '40:141:48:52:12:0:0:199'   #[40, 141, 48, 52, 12, 0, 0, 199]
DsH2O       =   '40:241:68:200:6:0:0:89'    #[40, 241, 68, 200, 6, 0, 0, 89]

modbus = ModbusClient('192.168.2.39', port=502)
DefaultUnit = 3
sunSpec = (
                    ('   Version',Vers_Addr, 8, 0, 's', DefaultUnit),
                    ('     Gas',SoBus1_Addr, 2, 0, 'u', DefaultUnit),
                    ('  Wasser',SoBus2_Addr, 2, 0, 'u', DefaultUnit),
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
                    #~ (' Ow-Val30',OW_Addr + 30, 2, 0, 'f', DefaultUnit),
                    #~ (' Ow-Adr31',OW_Addr + 32, 1, 0, 's', DefaultUnit),
                    #~ (' Ow-Adr32',OW_Addr + 33, 1, 0, 's', DefaultUnit),
                    #~ (' Ow-Adr33',OW_Addr + 34, 1, 0, 's', DefaultUnit),
                    #~ (' Ow-Adr34',OW_Addr + 35, 1, 0, 's', DefaultUnit),
                    #~ (' Ow-Adr35',OW_Addr + 36, 1, 0, 's', DefaultUnit),
                    #~ (' Ow-Adr36',OW_Addr + 37, 1, 0, 's', DefaultUnit),
                    #~ (' Ow-Adr37',OW_Addr + 38, 1, 0, 's', DefaultUnit),
                    #~ (' Ow-Adr38',OW_Addr + 39, 1, 0, 's', DefaultUnit),
                    (' timeStamp',eBus1_Addr +  0, 2, 0, 'u', DefaultUnit),
                    ('       TKO',eBus1_Addr +  2, 2, 0, 'f', DefaultUnit),
                    ('       TFK',eBus1_Addr +  4, 2, 0, 'f', DefaultUnit),
                    ('       TSO',eBus1_Addr +  6, 2, 0, 'f', DefaultUnit),
                    ('       TSU',eBus1_Addr +  8, 2, 0, 'f', DefaultUnit),
                    ('       TPU',eBus1_Addr + 10, 2, 0, 'f', DefaultUnit),
        )

#log.info("Total energy    : %d Wh" % Data['TotalWh'])
#~ #log.info("Today energy    : %d Wh" % Data['TodayWh'])

for i in range(15000):
    print (f'\nLauf : {i}')
    # ----------------------------------------------------------------------- #
    modbus.connect()

    sunSpecData = {}
    OneWire = []
    DsIntCnt = 0
    DsTPOCnt = 0
    DsH2OCnt = 0

    for dataSet in sunSpec:
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
                    sunSpecData[str(adr + adrOfs)] = valF
                else:
                    sunSpecData[str(adr + adrOfs)] = val

            elif (Einheit == 'f'):
                sunSpecData[DictKey] = valF
            #    print(f'{des} ({adr}) {val} {valF:0.2f}')
            else:
                sunSpecData[DictKey] = val
            #    print(f'{des} ({adr}) {val} {val}')

        else:
            print('\nAdresse:[{}] nicht vorhanden'.format(adr))


    # ----------------------------------------------------------------------- #
    # close the client
    # ----------------------------------------------------------------------- #
    modbus.close()

    DsAdr = []
    DsVal = []
    OW = f"{(sunSpecData[str(OW_Addr + 2)])}:{(sunSpecData[str(OW_Addr + 3)])}:{(sunSpecData[str(OW_Addr + 4)])}:{(sunSpecData[str(OW_Addr + 5)])}:{(sunSpecData[str(OW_Addr + 6)])}:{(sunSpecData[str(OW_Addr + 7)])}:{(sunSpecData[str(OW_Addr + 8)])}:{(sunSpecData[str(OW_Addr + 9)])}"
    DsVal.append(sunSpecData[str(OW_Addr + 0)])
    DsAdr.append(OW)

    OW = f"{(sunSpecData[str(OW_Addr + 12)])}:{(sunSpecData[str(OW_Addr + 13)])}:{(sunSpecData[str(OW_Addr + 14)])}:{(sunSpecData[str(OW_Addr + 15)])}:{(sunSpecData[str(OW_Addr + 16)])}:{(sunSpecData[str(OW_Addr + 17)])}:{(sunSpecData[str(OW_Addr + 18)])}:{(sunSpecData[str(OW_Addr + 19)])}"
    DsVal.append(sunSpecData[str(OW_Addr + 10)])
    DsAdr.append(OW)

    OW = f"{(sunSpecData[str(OW_Addr + 22)])}:{(sunSpecData[str(OW_Addr + 23)])}:{(sunSpecData[str(OW_Addr + 24)])}:{(sunSpecData[str(OW_Addr + 25)])}:{(sunSpecData[str(OW_Addr + 26)])}:{(sunSpecData[str(OW_Addr + 27)])}:{(sunSpecData[str(OW_Addr + 28)])}:{(sunSpecData[str(OW_Addr + 29)])}"
    DsVal.append(sunSpecData[str(OW_Addr + 20)])
    DsAdr.append(OW)

    for k in range(len(DsAdr)):
        if(DsInternal == DsAdr[k]):
            sunSpecData['TInternal'] = DsVal[k]
        if(DsTPO == DsAdr[k]):
            sunSpecData['TPO'] = DsVal[k]
        if(DsH2O == DsAdr[k]):
            sunSpecData['TWasser'] = DsVal[k]


    print (f"Ds Adr: {(sunSpecData[str(OW_Addr + 2)]): 4}:{(sunSpecData[str(OW_Addr + 3)]): 4}:{(sunSpecData[str(OW_Addr + 4)]): 4}:{(sunSpecData[str(OW_Addr + 5)]): 4}:{(sunSpecData[str(OW_Addr + 6)]): 4}:{(sunSpecData[str(OW_Addr + 7)]): 4}:{(sunSpecData[str(OW_Addr + 8)]): 4}:{(sunSpecData[str(OW_Addr + 9)]): 4} Temp: {sunSpecData[str(OW_Addr + 0)]:0.2f}")

    print (f"Ds Adr: {(sunSpecData[str(OW_Addr +12)]): 4}:{(sunSpecData[str(OW_Addr +13)]): 4}:{(sunSpecData[str(OW_Addr +14)]): 4}:{(sunSpecData[str(OW_Addr +15)]): 4}:{(sunSpecData[str(OW_Addr +16)]): 4}:{(sunSpecData[str(OW_Addr +17)]): 4}:{(sunSpecData[str(OW_Addr +18)]): 4}:{(sunSpecData[str(OW_Addr +19)]): 4} Temp: {sunSpecData[str(OW_Addr +10)]:0.2f}")

    print (f"Ds Adr: {(sunSpecData[str(OW_Addr + 22)]): 4}:{(sunSpecData[str(OW_Addr + 23)]): 4}:{(sunSpecData[str(OW_Addr + 24)]): 4}:{(sunSpecData[str(OW_Addr + 25)]): 4}:{(sunSpecData[str(OW_Addr + 26)]): 4}:{(sunSpecData[str(OW_Addr + 27)]): 4}:{(sunSpecData[str(OW_Addr + 28)]): 4}:{(sunSpecData[str(OW_Addr + 29)]): 4} Temp: {sunSpecData[str(OW_Addr + 20)]:0.2f}")

    #print (f"Ds Adr: {(sunSpecData[str(OW_Addr + 32)]):}:{(sunSpecData[str(OW_Addr + 33)])}:{(sunSpecData[str(OW_Addr + 34)])}:{(sunSpecData[str(OW_Addr + 35)])}:{(sunSpecData[str(OW_Addr + 36)])}:{(sunSpecData[str(OW_Addr + 37)])}:{(sunSpecData[str(OW_Addr + 38)])}:{(sunSpecData[str(OW_Addr + 39)])} Temp: {sunSpecData[str(OW_Addr + 30)]:0.2f}")

    timeStamp = sunSpecData['timeStamp']
    #print(f'-{timeStamp}-')
    #print(f"-{sunSpecData['timeStamp']}-")

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

    print(f"     Time: {Weekday[DayOfWeek]}; {Hour:02}:{Min:02}\t{timeStamp}")
    print(f"  Version: {sunSpecData['Version']}")
    print(f"  Gas Imp: {sunSpecData['Gas']}")
    print(f"   Wasser: {sunSpecData['Wasser']}")
    print(f"TInternal: {sunSpecData['TInternal']:0.2f}")
    print(f"      TPO: {sunSpecData['TPO']:0.2f}")
    print(f"  TWasser: {sunSpecData['TWasser']:0.2f}")
    print(f"      TKO: {sunSpecData['TKO']:0.2f}")
    print(f"      TFK: {sunSpecData['TFK']:0.2f}")
    print(f"      TSO: {sunSpecData['TSO']:0.2f}")
    print(f"      TSU: {sunSpecData['TSU']:0.2f}")
    print(f"      TPU: {sunSpecData['TPU']:0.2f}")

    time.sleep(60)

#~ Data = {}
#~ Data['Now'] = datetime.now()
#~ Data['RelVer'] =    sunSpecData['40045']
#~ Data['host'] =      sunSpecData['40097']
#~ Data['Status'] =    sunSpecData['40224']
#~ #Data['StatusTxt'] = sunSpecData['aaa']
#~ Data['InvName'] =   'PowerDorf'
#~ Data['InvSN'] =     sunSpecData['40053']
#~ Data['InvModel'] =  'Sunnboy 3.0'
#~ Data['InvString'] = '2'
#~ Data['InvPhase'] =  '1'
#~ Data['TotalWh1SP'] =   sunSpecData['40303']
#~ Data['TotalWh2SP'] =   sunSpecData['40210']

#~ Data['DayWh'] =   sunSpecData['30537']
#~ Data['TotalWh'] =   sunSpecData['30531']

#~ Data['CC_P'] =      sunSpecData['40643'] + sunSpecData['40663']
#~ Data['CA_P'] =      sunSpecData['40200']

#~ Data['CC1_U'] =   sunSpecData['40642']
#~ Data['CC1_I'] =   sunSpecData['40641']
#~ Data['CC1_P'] =   sunSpecData['40643']
#~ Data['CC1_T'] =   sunSpecData['40219']

#~ Data['CC2_U'] =   sunSpecData['40662']
#~ Data['CC2_I'] =   sunSpecData['40661']
#~ Data['CC2_P'] =   sunSpecData['40663']
#~ Data['CC2_T'] =   sunSpecData['40219']

#~ Data['CA1_U'] =   sunSpecData['40196']
#~ Data['CA1_I'] =   sunSpecData['40189']
#~ Data['CA1_P'] =   sunSpecData['40200']
#~ Data['CA1_T'] =   sunSpecData['40219']



#~ print("")
#~ print("TimeStamp       : {:%m/%d/%y %H:%M %S}".format(Data['Now']))
#~ print("Comm software   : SMA v%s - %s",(Data['RelVer']))
#~ print("Comm host       : %s",Data['host'])
#~ print("Inverter Status : %d",Data['Status'])
#~ print("Inverter Name   : %s",Data['InvName'])
#~ print("Inverter SN     : %s",Data['InvSN'])
#~ print("Inverter Model  : %s",Data['InvModel'])
#~ print("Inverter String : %d",Data['InvString'])
#~ print("Inverter Phase  : %d",Data['InvPhase'])
#~ print("Total energy SS1: %d Wh",Data['TotalWh1SP'])
#~ print("Total energy SS2: %d Wh",Data['TotalWh2SP'])
#~ print("Daily energy    : %d Wh",Data['DayWh'])
#~ print("Total energy    : %d Wh",Data['TotalWh'])
#~ print("DC Power        : %5d W\tAC Power        : %5d W",(Data['CC_P'], Data['CA_P']))
#~ print('DC String 1     : %5.1f V   %4.2f A   %4d W   T= %5.2f C',(Data['CC1_U'], Data['CC1_I'], Data['CC1_P'], Data['CC1_T']))
#~ print('DC String 2     : %5.1f V   %4.2f A   %4d W   T= %5.2f C',(Data['CC2_U'], Data['CC2_I'], Data['CC2_P'], Data['CC2_T']))
#~ print('AC Phase 1      : %5.1f V   %4.2f A   %4d W   T= %5.2f C',(Data['CA1_U'], Data['CA1_I'], Data['CA1_P'], Data['CA1_T']))

#~ log.info("")
#~ log.info("TimeStamp       : {:%m/%d/%y %H:%M %S}".format(Data['Now']))
#~ log.info("Comm software   : SMA v%s - %s" % (Data['RelVer']))
#~ log.info("Comm host       : %s" % Data['host'])
#~ log.info("Inverter Status : %d (%s)" % (Data['Status'], Data['StatusTxt'])
#~ log.info("Inverter Name   : %s" % Data['InvName'])
#~ log.info("Inverter SN     : %s" % Data['InvSN'])
#~ log.info("Inverter Model  : %s" % Data['InvModel'])
#~ log.info("Inverter String : %d" % Data['InvString'])
#~ log.info("Inverter Phase  : %d" % Data['InvPhase'])
#~ log.info("Total energy    : %d Wh" % Data['TotalWh'])
#~ log.info("DC Power        : %5d W\tAC Power        : %5d W" % (Data['CC_P'], Data['CA_P']))
#~ log.info('DC String 1     : %5.1f V   %4.2f A   %4d W   T= %5.2f C' % (Data['CC1_U'], Data['CC1_I'], Data['CC1_P'], Data['CC1_T']))
#~ log.info('DC String 2     : %5.1f V   %4.2f A   %4d W   T= %5.2f C' % (Data['CC2_U'], Data['CC2_I'], Data['CC2_P'], Data['CC2_T']))
#~ log.info('AC Phase 1      : %5.1f V   %4.2f A   %4d W   T= %5.2f C' % (Data['CA1_U'], Data['CA1_I'], Data['CA1_P'], Data['CA1_T'])))





















