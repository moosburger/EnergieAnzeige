#!/usr/bin/env python
# -*- coding: utf-8 -*-

# #################################################################################################
## \brief     Piko Inverter communication software
#  \details
#  \file      TestPikoToModBus.py
#
#  \date      Erstellt am: 13.03.2020
#  \author    moosburger
#  \Contrib
#
# <History\> ######################################################################################
# Version     Datum       Ticket#     Beschreibung
# 1.0         13:03.2020
#
# #################################################################################################

# #################################################################################################
# # Python Imports (Standard Library)
# #################################################################################################

from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from pymodbus.register_read_message import ReadHoldingRegistersResponse
import ctypes
import sys

# --------------------------------------------------------------------------- #
# configure the client logging
# --------------------------------------------------------------------------- #
import logging
FORMAT = ('%(asctime)-15s %(threadName)-15s '
          '%(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.ERROR)



#'''
# These classes/structures/unions, allow easy conversion between
# modbus 16bit registers and ctypes (a useful format)
#'''

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

# ------------------------------------------------------------------------#
# Define UNIT ID
# ------------------------------------------------------------------------#
UNIT = 126  # default according to the manual, see below

# ------------------------------------------------------------------------#
# Define client
# ------------------------------------------------------------------------#
modbus = ModbusClient('192.168.2.50', port=502)
#client = ModbusClient('localhost', port=502)
modbus.connect()

# ----------------------------------------------------------------------- #
sunSpec = (
            ('   Seriennummer',40053,16,0),
            ('  Softwarepaket',40045, 8,0),
            ('     Geraetetyp',40240, 1,0),
            ('     Geraetetyp',40037, 8,0),
            ('   Gesamtertrag',40303, 4,0),
            ('   Gesamtertrag',40210, 2,40212),
            ('       Leistung',40200, 1,40201),
            ('   Ac1 Spannung',40196, 1,40199),
            ('   Ac2 Spannung',40197, 1,40199),
            ('   Ac3 Spannung',40198, 1,40199),
            ('      Ac1 Strom',40189, 1,40192),
            ('      Ac2 Strom',40190, 1,40192),
            ('      Ac3 Strom',40191, 1,40192),
            ('Innentemperatur',40219, 1,0),
            ('   Dc1 Spannung',40642, 1,40625),
            ('   Dc2 Spannung',40662, 1,40625),
            ('      Dc1 Strom',40641, 1,40624),
            ('      Dc2 Strom',40661, 1,40624),
            ('   Dc1 Leistung',40643, 1,40626),
            ('   Dc2 Leistung',40663, 1,40626)
        )

for dataSet in sunSpec:
    des = dataSet[0]
    adr = dataSet[1] - 1
    leng = dataSet[2]
    skr = dataSet[3] - 1

    Translate = 0
    TranslateScale = 0

    raw = 0
    sk = 0
    val = ''
    if (skr > 0):
        sk = modbus.read_holding_registers(skr, 1, unit=UNIT)

    raw = modbus.read_holding_registers(adr, leng, unit=UNIT)
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

        print  '{} ({}): {}'.format (des, adr + 1, str(val))

    else:
        print 'Adresse:[{}] nicht vorhanden'.format(adr)
# ----------------------------------------------------------------------- #
# close the client
# ----------------------------------------------------------------------- #
modbus.close()
