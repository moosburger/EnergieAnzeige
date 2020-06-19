#!/usr/bin/env python
# -*- coding: utf-8 -*-

# #################################################################################################
## \brief
#  \details
#  \file      PreparePikoData.py
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
import math
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
except:
    PrivateImport = False

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
class PrepareData:

    # #################################################################################################
    # #  Funktion: ' _ConfCharToInt '
    ## \details        -
    #   \param[in]     -
    #   \param[in]     -
    #   \return          -
    # #################################################################################################
    def _ConfCharToInt(self, data, charLen):

        Translate = convertChar()
        SnNmr = []
        second = False
        lsSn = list(data)
        #if (len(lsSn) % 2 != 0):
#            lsSn.append(0)

        for single in lsSn:
            if (second == False):
                Translate.u8.l = ord(single)
                second = True
            else:
                if (isinstance(single, basestring)):
                    Translate.u8.h = ord(single)
                else:
                    Translate.u8.h = single

                SnNmr.append(Translate.u16)
                second = False

        for k in range(len(SnNmr), charLen):
            SnNmr.append(0)

        return SnNmr

    # #################################################################################################
    # #  Funktion: ' _Conf_Two_Register '
    ## \details        -
    #   \param[in]     -
    #   \param[in]     -
    #   \return          -
    # #################################################################################################
    def _Conf_Two_Register(self, data):

        Translate=convert2()
        Translate.uint32 = data

        list = []
        list.append(Translate.u16.l)
        list.append(Translate.u16.h)

        return list

    # #################################################################################################
    # #  Funktion: ' _Conf_Four_Register '
    ## \details        -
    #   \param[in]     -
    #   \param[in]     -
    #   \return          -
    # #################################################################################################
    def _Conf_Four_Register(self, data):

        Translate=convert4()
        Translate.uint64 = data
        list = []
        list.append(Translate.u16.ll)
        list.append(Translate.u16.lh)
        list.append(Translate.u16.hl)
        list.append(Translate.u16.hh)

        return list

    # #################################################################################################
    # #  Funktion: ' _ConfInt32ToInt16 '
    ## \details        -
    #   \param[in]     -
    #   \param[in]     -
    #   \return          -
    # #################################################################################################
    def _Conf_Single_Register(self, data):

        Translate=convert1()
        TranslateScale=convert1()

        # Skaling auf Anzahl der Stellen und max Wert 655535
        # auf eine Stelle hinterm Komma begrenzen
        if isinstance(data, float):
            digits = len(str(data)) - 1 #Dezimalpunkt kann weg
        else:
            digits = len(str(data))

        iCnt = len(str(int(data)))
        if (digits > 5):
            digits = 5

        if (data >= 65000):
            digits = digits - 1

        TranslateScale.s16 = digits - iCnt
        data = round(data, TranslateScale.s16)
        Translate.s16 = int(data*(10**(TranslateScale.s16)))
        # Für die Skalierung und Rückrechnung auf Client Seite nun *-1
        TranslateScale.s16 = -TranslateScale.s16

        list = []
        list.append([Translate.u16,])
        list.append([TranslateScale.u16,])

        return list

      # #################################################################################################
      # #  Funktion: ' _CnvStatusTxt '
      ## \details        -
      #   \param[in]     -
      #   \param[in]     -
      #   \return          -
      # #################################################################################################
    def _CnvStatusTxt(self, Val):

        Txt = "Communication error"
        if Val == 1: Txt = "Aus"            # SMA 1 = Aus
        if Val == 2: Txt = "Idle"           # SMA 2 = Idle
        if Val == 3: Txt = "Starte"         # SMA 3 = Starte
        if Val == 4: Txt = "MPP"            # SMA 4 = MPP
        if Val == 5: Txt = "Abgeregelt"     # SMA 5 = Abgeregelt
                                            # SMA 6 = Fahre herunter
                                            # SMA 7 = Fehler
                                            # SMA 8 = Warte auf EVU
        return Txt

      # #################################################################################################
      # #  Funktion: ' _CnvStatus '
      ## \details        -
      #   \param[in]     -
      #   \param[in]     -
      #   \return          -
      # #################################################################################################
    def _CnvStatus(self, Val):

        if Val == 0: Val = 1    # SMA 1 = Aus
        elif Val == 1: Val = 2    # SMA 2 = Idle
        elif Val == 2: Val = 3    # SMA 3 = Starte
        elif Val == 3: Val = 4    # SMA 4 = MPP
        elif Val == 4: Val = 5    # SMA 5 = Abgeregelt
        elif Val == 5: Val = 4

        return Val

    # #################################################################################################
    # #  Funktion: ' _Prepare_Data '
    ## \details        -
    #   \param[in]     -
    #   \param[in]     -
    #   \return          -
    # #################################################################################################
    def Prepare(self, Piko, Data, FirstRun):

        TotalWh2 = self._Conf_Two_Register(Data['TotalWh'])
        TotalWh4 = self._Conf_Four_Register(Data['TotalWh'])

        CA_P  = self._Conf_Single_Register(Data['CA_P'])
        CA1_U = self._Conf_Single_Register(Data['CA1_U'])
        CA2_U = self._Conf_Single_Register(Data['CA2_U'])
        CA3_U = self._Conf_Single_Register(Data['CA3_U'])

        CA12_U = math.sqrt(3) * Data['CA1_U']
        CA23_U = math.sqrt(3) * Data['CA2_U']
        CA31_U = math.sqrt(3) * Data['CA3_U']
        CA12_U = round(CA12_U , 1)
        CA23_U = round(CA23_U , 1)
        CA31_U = round(CA31_U , 1)
        CA12_U = self._Conf_Single_Register(CA12_U)
        CA23_U = self._Conf_Single_Register(CA23_U)
        CA31_U = self._Conf_Single_Register(CA31_U)

        CA_I = Data['CA1_I'] + Data['CA2_I'] +Data['CA3_I']
        CA_I = self._Conf_Single_Register(round(CA_I, 1))
        CA1_I = self._Conf_Single_Register(round(Data['CA1_I'], 1))
        CA2_I = self._Conf_Single_Register(round(Data['CA2_I'], 1))
        CA3_I = self._Conf_Single_Register(round(Data['CA3_I'], 1))
        CC_T  = [int(((Piko._CnvTemp(Data['CC1_T']) + Piko._CnvTemp(Data['CC2_T'])) / 2)),]
        CC1_U = self._Conf_Single_Register(Data['CC1_U'])
        CC2_U = self._Conf_Single_Register(Data['CC2_U'])
        CC1_I = self._Conf_Single_Register(Data['CC1_I'])
        CC2_I = self._Conf_Single_Register(Data['CC2_I'])
        CC1_P = self._Conf_Single_Register(Data['CC1_P'])
        CC2_P = self._Conf_Single_Register(Data['CC2_P'])
        CC_P = self._Conf_Single_Register(Data['CC_P'])

        Data['Status'] = self._CnvStatus(Data['Status'])
        Status = self._Conf_Single_Register(Data['Status'])

        sunSpec = (
                    ('Ac Strom',40188,1,CA_I[0],40192,CA_I[1]),
                    ('Ac1 Strom',40189, 1,CA1_I[0],40192,CA_I[1]),     #Data['CA1_I']   #~ AC Phase 1      : 3.09 A
                    ('Ac2 Strom',40190, 1,CA2_I[0],40192,CA_I[1]),     #Data['CA2_I']   #~ AC Phase 2      : 3.09 A
                    ('Ac3 Strom',40191, 1,CA3_I[0],40192,CA_I[1]),     #Data['CA3_I']   #~ AC Phase 3       : 3.09 A
                    ('Spannung L1 L2',40193,1,CA12_U[0],40199,CA1_U[1]),
                    ('Spannung L2 L3',40194,1,CA12_U[0],40199,CA1_U[1]),
                    ('Spannung L3 L1',40195,1,CA12_U[0],40199,CA1_U[1]),
                    ('Ac1 Spannung',40196, 1,CA1_U[0],40199,CA1_U[1]),  #Data['CA1_U']   #~ AC Phase 1      : 231.7 V
                    ('Ac2 Spannung',40197, 1,CA2_U[0],40199,CA1_U[1]),  #Data['CA2_U']   #~ AC Phase 2      : 232.4 V
                    ('Ac3 Spannung',40198, 1,CA3_U[0],40199,CA1_U[1]),  #Data['CA3_U']   #~ AC Phase 3      : 232.4 V
                    ('Leistung',40200, 1,CA_P[0],40201,CA_P[1]),        #Data['CA_P']    #~ AC Power        :  2087 W
                    ('Frequenz',40202,1,[49.96,],40203,[0,]),
                    ('Scheinleistung',40204,1,[240,],40205,[0,]),
                    ('Blindleistung',40206,1,[0,],40207,[0,]),
                    ('cos phi',40208,1,[0,],40209,[0,]),
                    ('Gesamtertrag',40210, 2,TotalWh2,40212,[0,]),      #Data['TotalWh'] #~ Total energy    : 17634922 Wh
                    ('DC Leistung',40217,1,CC_P[0],40218,CC_P[1]),
                    ('Innentemperatur',40219, 1,CC_T,0,[0,]),           #(Piko._CnvTemp(Data['CC1_T']) + Piko._CnvTemp(Data['CC2_T'])) / 2 #~ Mittelwertaller Temp  der Dc Werte   #~ DC String 1     :  (94.79 C)  + #~ DC String 2     :  (78.50 C) / 2
                    ('And. Innentemp',40222,1,[0,],40223,[0,]),
                    ('Betriebsstatus',40224,1,Status[0],0,Status[1]),
                    ('Ereignisnummer',40226,2,[0,],0,[0,]),
                    ('Gesamtertrag',40303, 4,TotalWh4,0,[0,]),          #Data['TotalWh'] #~ Total energy    : 17634922 Wh
                    ('Dc1 Spannung',40642, 1,CC1_U[0],40625,CC1_U[1]),  #Data['CC1_U']   #~ DC String 1     : 364.7 V
                    ('Dc2 Spannung',40662, 1,CC2_U[0],40625,CC1_U[1]),  #Data['CC2_U']   #~ DC String 2     :   0.0 V
                    ('Dc1 Strom',40641, 1,CC1_I[0],40624,CC1_I[1]),     #Data['CC1_I']   #~ DC String 1     :  6.04 A
                    ('Dc2 Strom',40661, 1,CC2_I[0],40624,CC1_I[1]),     #Data['CC2_I']   #~ DC String 2     : 0.00 A
                    ('Dc1 Leistung',40643, 1,CC1_P[0],40626,CC1_P[1]),  #Data['CC1_P']   #~ DC String 1     : 2203 W
                    ('Dc2 Leistung',40663, 1,CC2_P[0],40626,CC1_P[1])   #Data['CC2_P']   #~ DC String 2     :  0 W
                )

        if (FirstRun == True):
            InvSN =  self._ConfCharToInt(Data['InvSN'], 16)
            #InvSN =  self._ConfCharToInt('1992054489', 16)
            InvVer = self._ConfCharToInt(Data['InvVer'], 8)
            #InvVer = self._ConfCharToInt('1.03.04.R', 8)
            #InvRef = self._ConfCharToInt(str(Data['InvRef'], 8))
            InvRef = self._ConfCharToInt('9336', 8)
            InvHer = self._ConfCharToInt('PIKO ', 16)
            InvMod = self._ConfCharToInt('Solar Inverter', 16)
            SID = self._Conf_Two_Register(1400204883)
            ISO = self._Conf_Four_Register(3000000)
            MAC = self._Conf_Four_Register(277790954258)
            IP = self._ConfCharToInt(_conf.INVERTER_IP, 8)
            MASK = self._ConfCharToInt('255.255.255.0', 8)
            GATE = self._ConfCharToInt('192.168.2.68', 8)
            DNS = self._ConfCharToInt(_conf.INVERTER_IP, 8)

            pikoHeader = (
                        # Tabelle C001 (Common Model)
                            ('SunSpec ID (SID)',40001,2,SID,0,[0,]),
                            ('Model ID',40003,1,[1,],0,[0,]),
                            ('Register Count',40004,1,[66,],0,[0,]),    # 66    66
                            ('Hersteller',40005,16,InvHer,0,[0,]),
                            ('Modell',40021,16,InvMod,0,[0,]),
                            ('Geraetetyp',40037, 8,InvRef,0,[0,]),      #Data['InvRef']  #~ Inverter Ref    : 269505669
                            ('Softwarepaket',40045, 8,InvVer,0,[0,]),   #Data['InvVer']  #~ Inverter Version: 0200 04.03 04.12
                            ('Seriennummer',40053,16,InvSN,0,[0,]),     #Data['InvSN']  #~ Inverter SN     : 90505MES00003
                        # Tabelle NC 011 (Ethernet Link Layer Model)
                            ('Model ID',40071,1,[11,],0,[0,]),          # 11 = SunSpec Ethernet Link Layer Mode
                            ('Register Count',40072,1,[13,],0,[0,]),    # 13    13
                            ('Datenuebertragungsrate',40073,1,[100,],0,[0,]),
                            ('Schnittstellen-Status',40074,1,[3,],0,[0,]),
                            ('Verbindungs-Status',40075,1,[1,],0,[0,]),
                            ('MAC-Adresse',40076,4,MAC,0,[0,]),
                        # Tabelle NC 012 (IPv4 Model)
                            ('Model ID',40086,1,[12,],0,[0,]),          #12
                            ('Register Count',40087,1,[98,],0,[0,]),    #98     98
                            ('Konfigurationsstatus',40092,1,[1,],0,[0,]),
                            ('Aenderungsstatus (ChgSt)',40093,1,[0,],0,[0,]),
                            ('Aenderungsfaehigkeit (Cap)',40094,1,[5,],0,[0,]),
                            ('IPv4 Konfiguration',40095,1,[0,],0,[0,]),
                            ('Konfiguriere Dienst-Verwendung',40096,1,[0,],0,[0,]),
                            ('IP-Adresse',40097,8,IP,0,[0,]),
                            ('Netzmaske',40105,8,MASK,0,[0,]),
                            ('Gateway',40113,8,GATE,0,[0,]),
                            ('DNS 1',40121,8,DNS,0,[0,]),
                        # Taellen I 101, 102, 103 (Inverter Integer Map)
                            ('Model ID',40186,1,[103,],0,[0,]),         #101 = SunSpec Inverter Model (phsA, phsB, phsC)  | 102 = SunSpec Inverter Model (phsAB, phsAC, phsBC)  | 103 = SunSpec Inverter Model (phsABC)
                            ('Register Count',40187,1,[50,],0,[0,]),    # 50    50
                        # Tabelle IC 120 (Inverter Controls Nameplate Ratings)
                            ('Model ID',40238,1,[120,],0,[0,]),         # 120
                            ('Register Count',40239,1,[26,],0,[0,]),   # 26    26
                            ('Geraetetyp',40240, 1,[4,],0,[0,]),
                            ('WRtg',40241,1,[3000,],40242,[0,]),
                            ('VARtg',40243,1,[3000,],40244,[0,]),
                            ('VArRtgQ1',40245,1,[0,],40249,[0,]),
                            ('VArRtgQ2',40246,1,[0,],40249,[0,]),
                            ('VArRtgQ3',40247,1,[0,],40249,[0,]),
                            ('VArRtgQ4',40248,1,[0,],40249,[0,]),
                            ('ARtg',40250,1,[0,],40256,[0,]),
                            ('PFRtgQ1',40252,1,[0,],40256,[0,]),
                            ('PFRtgQ2',40253,1,[0,],40256,[0,]),
                            ('PFRtgQ3',40254,1,[0,],40256,[0,]),
                            ('PFRtgQ4',40255,1,[0,],40256,[0,]),
                            ('WHRtg',40257,1,[0,],40258,[0,]),
                            ('AhrRtg',40259,1,[0,],40260,[0,]),
                            ('MaxChaRte',40261,1,[0,],40262,[0,]),
                            ('MaxChaRte_SF',40263,1,[0,],40264,[0,]),
                        # Tabelle IC 121 (Inverter Controls Basic Settings)
                            ('Model ID',40266,1,[121,],0,[0,]),         # 121
                            ('Register Count',40267,1,[30,],0,[0,]),  # 30    30
                            ('WMax',40268,1,[3000,],40288,[0,]),
                            ('VRef',40269,1,[0,],40289,[0,]),
                            ('VRefOfs',40270,1,[0,],40290,[0,]),
                            ('VAMax',40273,1,[3000,],40292,[0,]),
                            ('VArMaxQ1',40274,1,[0,],40293,[0,]),
                            ('WGra',40278,1,[0,],40294,[0,]),
                            ('VArAct',40283,1,[0,],0,[0,]),
                            ('ECPNomHz',40286,1,[50,],40297,[0,]),
                            ('ConnPh',40287,1,[1,],0,[0,]),
                        # Tabelle IC 122 (Inverter Controls Extended Measurements)
                            ('Model ID',40298,1,[122,],0,[0,]),         # 122
                            ('Register Count',40299,1,[44,],0,[0,]),    # 44    44
                            ('PVConn',40300,1,[5,],0,[0,]),
                            ('StorConn',40301,1,[0,],0,[0,]),
                            ('ECPConn',40302,1,[0,],0,[0,]),
                            ('Isolationswiderstand',40342,1,ISO,40343,[0,]),
                        # Tabelle IC 123 (Immediate Inverter Controls)
                            ('Model ID',40344,1,[123,],0,[0,]),         # 123
                            ('Register Count',40345,1,[24,],0,[0,]),    # 24    24
                            ('Verbindungskontrolle',40348,1,[1,],0,[0,]),
                            ('WMaxLimPct',40349,1,[0,],40367,[0,]),
                            ('WMaxLim_Ena',40353,1,[0,],0,[0,]),
                            ('Out-PFSet',40354,1,[0,],40368,[0,]),
                            ('OutPFSet_Ena',40358,1,[0,],0,[0,]),
                            ('VArWMaxPct',40359,1,[0,],40369,[0,]),
                            ('VArPct_Mod',40365,1,[1,],0,[0,]),
                            ('VArPct_Ena',40366,1,[0,],0,[0,]),
                        # Tabelle IC 124 (Basic Storage Controls)
                            ('Model ID',40370,1,[124,],0,[0,]),         # 124
                            ('Register Count',40371,1,[24,],0,[0,]),    # 24    24
                            ('WChaMax',40372,1,[0,],40388,[0,]),
                            ('StorCtl_Mod',40375,1,[0,],0,[0,]),
                            ('ChaState',40378,1,[0,],40392,[0,]),
                            ('InBatV',40380,1,[0,],40394,[0,]),
                            ('ChaSt',40381,1,[0,],0,[0,]),
                        #  Tabelle IC 126 (Static Volt-VAR Arrays)
                            ('Model ID',40396,1,[126,],0,[0,]),         # 126
                            ('Register Count',40371,1,[64,],0,[0,]),    # 64    24
                            ('',40398,1,[0,],0,[0,]),
                            ('',40399,1,[0,],0,[0,]),
                            ('',40403,1,[1,],0,[0,]),
                            ('',40404,1,[8,],0,[0,]),
                            ('',40408,1,[0,],0,[0,]),
                            ('',40409,1,[0,],0,[0,]),
                            ('',40410,1,[0,],40405,[0,]),
                            ('',40411,1,[0,],40406,[0,]),
                            ('',40412,1,[0,],40405,[0,]),
                            ('',40413,1,[0,],40406,[0,]),
                            ('',40414,1,[0,],40405,[0,]),
                            ('',40415,1,[0,],40406,[0,]),
                            ('',40416,1,[0,],40405,[0,]),
                            ('',40417,1,[0,],40406,[0,]),
                            ('',40418,1,[0,],40405,[0,]),
                            ('',40419,1,[0,],40406,[0,]),
                            ('',40420,1,[0,],40405,[0,]),
                            ('',40421,1,[0,],40406,[0,]),
                            ('',40422,1,[0,],40405,[0,]),
                            ('',40423,1,[0,],40406,[0,]),
                            ('',40424,1,[0,],40405,[0,]),
                            ('',40425,1,[0,],40406,[0,]),
                            ('',40426,1,[0,],40405,[0,]),
                            ('',40427,1,[0,],40406,[0,]),
                            ('',40428,1,[0,],40405,[0,]),
                            ('',40429,1,[0,],40406,[0,]),
                            ('',40430,1,[0,],40405,[0,]),
                            ('',40431,1,[0,],40406,[0,]),
                            ('',40432,1,[0,],40405,[0,]),
                            ('',40433,1,[0,],40406,[0,]),
                            ('',40459,1,[0,],40407,[0,]),
                            ('',40460,1,[0,],40407,[0,]),
                            ('',40461,1,[0,],0,[0,]),
                        # Tabelle IC 127 (Parameterized Frequency-Watt)
                            ('Model ID',40462,1,[127,],0,[0,]),         # 127
                            ('Register Count',40463,1,[64,],0,[0,]),    # 64    10
                            ('',40464,1,[40,],40470,[0,]),
                            ('',40465,1,[50.2,],40471,[0,]),
                            ('',40466,1,[50.18,],40471,[0,]),
                            ('',40467,1,[0,],0,[0,]),
                            ('',40468,1,[1,],0,[0,]),
                            ('',40469,1,[20,],40472,[0,]),
                        #  Tabelle IC 128 (Dynamic Reactive Current)
                            ('Model ID',40474,1,[128,],0,[0,]),         # 128
                            ('Register Count',40475,1,[14,],0,[0,]),    # 14    14
                            ('',40476,1,[0,],0,[0,]),
                            ('',40477,1,[0,],40487,[0,]),
                            ('',40478,1,[0,],40487,[0,]),
                            ('',40479,1,[0,],0,[0,]),
                            ('',40480,1,[60,],0,[0,]),
                            ('',40481,1,[0,],40488,[0,]),
                            ('',40482,1,[0,],40488,[0,]),
                            ('',40483,1,[0,],40488,[0,]),
                            ('',40485,1,[0,],0,[0,]),
                        # Tabelle IC 131 (Watt-Power Factor)
                            ('Model ID',40490,1,[131,],0,[0,]),         # 131
                            ('Register Count',40491,1,[64,],0,[0,]),    # 64    64
                            ('Index der aktiven Kurve (ActCrv)',40492,1,[0,],0,[0,]),
                            ('Watt-PF-Modus aktiv (ModEna)',40493,1,[0,],0,[0,]),
                            ('Anzahl der unterstuetzten Kurvenpunkte (NPt)',40498,1,[8,],0,[0,]),
                            ('Anzahl aktiver Punkte im Array (ActPt)',40502,1,[0,],0,[0,]),
                            ('Punkt 1 Watt',40503,1,[0,],40499,[0,]),
                            ('Punkt 1 PF',40504,1,[0,],40500,[0,]),
                            ('Punkt 2 Watt',40505,1,[0,],40499,[0,]),
                            ('Punkt 2 PF',40506,1,[0,],40500,[0,]),
                            ('Kurvenpunkte aenderbar',40554,1,[0,],0,[0,]),
                        # Tabelle IC 132 (Volt-Watt)
                            ('Model ID',40556,1,[132,],0,[0,]),         # 132
                            ('Register Count',40557,1,[64,],0,[0,]),    # 64    64
                            ('',40558,1,[0,],0,[0,]),
                            ('',40559,1,[0,],0,[0,]),
                            ('',40563,1,[1,],0,[0,]),
                            ('',40564,1,[8,],0,[0,]),
                            ('',40568,1,[0,],0,[0,]),
                            ('',40569,1,[0.0,],40566,[0,]),
                            ('',40570,1,[0,],40565,[0,]),
                            ('',40571,1,[0,],40566,[0,]),
                            ('',40572,1,[0,],40565,[0,]),
                            ('',40573,1,[0,],40566,[0,]),
                            ('',40574,1,[0,],40565,[0,]),
                            ('',40575,1,[0,],40566,[0,]),
                            ('',40576,1,[0,],40565,[0,]),
                            ('',40577,1,[0,],40566,[0,]),
                            ('',40578,1,[0,],40565,[0,]),
                            ('',40579,1,[0,],40566,[0,]),
                            ('',40580,1,[0,],40565,[0,]),
                            ('',40581,1,[0,],40566,[0,]),
                            ('',40582,1,[0,],40565,[0,]),
                            ('',40583,1,[0,],40566,[0,]),
                            ('',40584,1,[0,],40565,[0,]),
                            ('',40585,1,[0,],40566,[0,]),
                            ('',40586,1,[0,],40565,[0,]),
                            ('',40587,1,[0,],40566,[0,]),
                            ('',40588,1,[0,],40565,[0,]),
                            ('',40589,1,[0,],40566,[0,]),
                            ('',40590,1,[0,],40565,[0,]),
                            ('',40591,1,[0,],40566,[0,]),
                            ('',40592,1,[0,],40565,[0,]),
                            ('',40593,1,[0,],40566,[0,]),
                            ('',40619,1,[0,],0,[0,]),
                            ('',40620,1,[0,],0,[0,]),
                            ('',40621,1,[0,],0,[0,]),
                        #  Tabelle I 160 (MPPT Inverter Extension Model)
                            ('Model ID',40622,1,[160,],0,[0,]),         # 160
                            ('Register Count',40623,1,[48,],0,[0,]),    # 48    128
                            ('Anzahl der Module',40630,1,[12,],0,[0,]),
                            ('ID MPPT Tracker 1',40632,1,[1,],0,[0,]),
                            ('ID MPPT Tracker 2',40652,1,[2,],0,[0,]),
                        )
            sunSpec = pikoHeader + sunSpec

        return sunSpec

    # #################################################################################################
    # #  Funktion: ' _Dbg_Print '
    ## \details        -
    #   \param[in]     -
    #   \param[in]     -
    #   \return          -
    # #################################################################################################
    def Dbg_Print(self, Piko, Data):

        print '#################################################################################################'
        print "TimeStamp       : {:%m/%d/%y %H:%M %S}".format(Data['Now'])
        print "Comm software   : Piko v%s - %s" % (Data['RelVer'], Data['RelDate'])
        print "Comm host       : %s" % Data['host']
        print "Comm port       : %d" % Data['port']
        print "Comm status     : %s\n" % Data['NetStatus']
        print "Inverter Status : %d (%s)" % (Data['Status'], Data['StatusTxt'])
        print "Inverter Error  : %s" % Data['ErrorCode']
        print "Inverter Name   : %s" % Data['InvName']
        print "Inverter SN     : %s" % Data['InvSN']
        print "Inverter Ref    : %s" % Data['InvRef']
        print "Inverter Version: %s" % Data['InvVer']
        print "Inverter Model  : %s" % Data['InvModel']
        print "Inverter String : %d" % Data['InvString']
        print "Inverter Phase  : %d\n" % Data['InvPhase']
        print "Total Time      : %s (%d j)" % (Piko._DspTimer("", Data['InvInstTime'], 1), Data['InvInstTime']//86400)
        print "Running Time    : %s" % Piko._DspTimer("", Data['InvRunTime'], 1)
        print "Last Port. upld : %s" % Piko._DspTimer("", Data['InvPortalTime'], 1)
        print "Last Hist. updt : %s" % Piko._DspTimer("", Data['InvHistTime'], 1)
        print "Hist. updt step : %s\n" % Piko._DspTimer("", Data['InvHistStep'], 1)
        print "Total energy    : %d Wh" % Data['TotalWh']
        print "Today energy    : %d Wh" % Data['TodayWh']
        print "DC Power        : %5d W\nAC Power        : %5d W\nEfficiency      : %5.1f %%\n" % (Data['CC_P'], Data['CA_P'], Data['Eff'])

        print 'DC String 1     : %5.1f V   %4.2f A   %4d W   T=%04x (%5.2f C)  S=%04x' % (Data['CC1_U'], Data['CC1_I'], Data['CC1_P'], Data['CC1_T'], Piko._CnvTemp(Data['CC1_T']), Data['CC1_S'])
        print 'DC String 2     : %5.1f V   %4.2f A   %4d W   T=%04x (%5.2f C)  S=%04x' % (Data['CC2_U'], Data['CC2_I'], Data['CC2_P'], Data['CC2_T'], Piko._CnvTemp(Data['CC2_T']), Data['CC2_S'])
        print 'DC String 3     : %5.1f V   %4.2f A   %4d W   T=%04x (%5.2f C)  S=%04x' % (Data['CC3_U'], Data['CC3_I'], Data['CC3_P'], Data['CC3_T'], Piko._CnvTemp(Data['CC3_T']), Data['CC3_S'])
        print 'AC Status       : %d (%04x %s)' % (Data['CA_S'], Data['CA_S'], Piko._CnvCA_S(Data['CA_S']))
        print 'AC Phase 1      : %5.1f V   %4.2f A   %4d W   T=%04x (%5.2f C)' % (Data['CA1_U'], Data['CA1_I'], Data['CA1_P'], Data['CA1_T'], Piko._CnvTemp(Data['CA1_T']))
        print 'AC Phase 2      : %5.1f V   %4.2f A   %4d W   T=%04x (%5.2f C)' % (Data['CA2_U'], Data['CA2_I'], Data['CA2_P'], Data['CA2_T'], Piko._CnvTemp(Data['CA2_T']))
        print 'AC Phase 3      : %5.1f V   %4.2f A   %4d W   T=%04x (%5.2f C)' % (Data['CA3_U'], Data['CA3_I'], Data['CA3_P'], Data['CA3_T'], Piko._CnvTemp(Data['CA3_T']))
        print '#################################################################################################\n'

    # # Ende Funktion: ' _Dbg_Print ' ###################################################################

# # Ende Klasse: ' PikoWebRead ' ##################################################################

# # DateiEnde #####################################################################################

