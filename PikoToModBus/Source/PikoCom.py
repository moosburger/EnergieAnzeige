#!/usr/bin/env python
# -*- coding: utf-8 -*-

# #################################################################################################
## \brief     Piko Inverter communication software
#  \details
#  \file      Piko.py
#
#  \date      Erstellt am: 13.03.2020
#  \author    moosburger,  based on the work from
#  \Contrib   Romuald Dufour
#             emoncms export code by Peter Hasse (peter.hasse@fokus.fraunhofer.de)
#  \Licence   GPL v3
#
#  \version   1.4.1  -  3.07.2018
#
# <History\> ######################################################################################
# Version     Datum       Kuerzel      Ticket#     Beschreibung
#           : 1.3.3 - 20140117 - Exception handling on emoncms
#                    20140110 - Added support for emoncms export (http://emoncms.org)
#                               json and requests modules depencies added
#                               ('easy_install requests' maybe needed)
#           : 1.3.2 - 20131115 - Bug fixes for some inverter software
#                               (old release not responding to some request)
#           : 1.3.1 - 20130731 - Bug fixes, temp by model, get FW version
#           : 1.3.0 - 20130730 - Csv export (WebSolarLog, ...), -a self.Option
#                               Get additional data (timers, model, strings, phases, ...)
#           : 1.2.6 - 201303xx - Bug fix in comm error handling
#           : 1.2.5 - 20130227 - Add RS485 bus address parameter (--id=xxx)
#           : 1.2.4 - 20121026 - No change (keep rel nb in sync w. Pyko_db)
#           : 1.2.3 - 20110907 - Correct small bug in history import (F=-.-)
#           : 1.2.1 - 20110825 - Temp Decoding beter accuracy
#           : 1.2.0 - 20110824 - Realtime DB save + Status/Temp Decoding
#           : 1.1.0 - 20110817 - History DB save
#           : 1.0.0 - 20110816 - History data
#           : 0.5.0 - 20110812 - Realtime data
#           : 0.1.0 - 20110810 - Online protocol
#
# #################################################################################################

# #################################################################################################
# # Python Imports (Standard Library)
# #################################################################################################
import sys
import socket
import urllib2
import csv
#import os

from optparse import OptionParser, OptionGroup
from datetime import datetime, timedelta

reload(sys)
sys.setdefaultencoding("utf-8")

# #################################################################################################
# # Python Imports (site-packages)
# #################################################################################################

# #################################################################################################
# # private Imports
# #################################################################################################
#try:
#    PrivateImport = True
#    import Error
#    import Utils
#    from GetTrello import (TrelloCards)
#    from GetMercurial import (HgLogOutput)
#except:
#    PrivateImport = False

# #################################################################################################
# # UmgebungsVariablen
# #################################################################################################
#env =  os.environ

RelVer="1.4.1"
RelDate="20160218"
TRef="c800"
#P="?"

# #################################################################################################
# # Funktionen
# # Prototypen
# # if __name__ == '__main__':
# #################################################################################################

# #################################################################################################
# # Classes: PikoWebRead
## \details#
#
# #################################################################################################
class PikoWebRead:

# #################################################################################################
# # Funktion: ' Constructor '
## \details Die Initialisierung der Klasse TrelloCards
#   \param[in]  self der Objectpointer
#   \param[in]
#   \param[in]
#   \return -
# #################################################################################################
  def __init__(self, bDbg, Inv_Host, InvPwd):

    self.SocketStream = 0

    self.Opt = {}

    #HostGroup.add_option("", "--id", help="RS485 bus address", type=int, dest="Addr", metavar="255", default="255")
    self.Opt['Addr'] = 255
    #HostGroup.add_option("", "--tref", help="Temp reference", dest="TRef", metavar="c800", default="0")
    self.Opt['TRef'] = '0'
    #HostGroup.add_option("", "--debug", help="Show data frames", dest="Dbg", action="store_true", default=False)
    self.Opt['Dbg'] = bDbg

    #HistGroup.add_option("", "--user", help="http username", dest="InvUser", metavar="USERNAME", default="pvserver")
    self.Opt['InvUser'] = 'pvserver',
    #HistGroup.add_option("", "--password", help="http password", dest="InvPassword", metavar="PASSWORD", default="")
    self.Opt['InvPassword'] = InvPwd,

    # Datenstrukur
    self.Data = {}
    self.Data['TechData'] = 0
    self.Data['Now'] = 0
    # Inverter Status
    self.Data['Status'] = 0
    # Inverter Status Text
    self.Data['StatusTxt'] = ''
    # Comm software
    self.Data['RelVer'] = RelVer
    self.Data['RelDate'] = RelDate
    # Comm host
    self.Data['host'] = Inv_Host
    # "Comm port
    self.Data['port'] = 81
    # Comm status
    self.Data['NetStatus'] = 0
    # Inverter Error
    self.Data['ErrorCode'] = 0
    # Total energy
    self.Data['TotalWh'] = 17612176
    # Today energy
    self.Data['TodayWh'] = 11629
    # DC Power
    self.Data['CC_P'] = 660
    # AC Power
    self.Data['CA_P'] = 600
    # nEfficiency
    self.Data['Eff'] = 90.9
    # Inverter Name
    self.Data['InvName'] = 'PowerDorf'
    # Inverter SN
    self.Data['InvSN'] = '90505MES00003'
    # Inverter Ref
    self.Data['InvRef'] = 269505669
    # Inverter Model
    self.Data['InvModel'] = 'PIKO 4.2'
    # Inverter Version
    self.Data['InvVer'] = '0200 04.03 04.12'
    # Inverter String
    self.Data['InvString'] = 2
    # Inverter Phase
    self.Data['InvPhase'] = 3
    # Total Time
    self.Data['InvInstTime'] = 0
    # Running Time
    self.Data['InvRunTime'] = 0
    # Last Port. upld
    self.Data['InvPortalTime'] = 0
    # Last Hist. updt
    self.Data['InvHistTime'] = 0
    # Hist. updt step
    self.Data['InvHistStep'] = 0

    # DC String 1
    # Spannung
    self.Data['CC1_U'] = 432.7
    # Strom
    self.Data['CC1_I'] = 1.52
    # Leistung
    self.Data['CC1_P'] = 660
    # Temperatur
    self.Data['CC1_T'] = 0x5620
    # S?
    self.Data['CC1_S'] = 0x4009
    # DC String 2
    # Spannung
    self.Data['CC2_U'] = 0
    # Strom
    self.Data['CC2_I'] = 0
    # Leistung
    self.Data['CC2_P'] = 0
    # Temperatur
    self.Data['CC2_T'] = 0x5fc0
    # S?
    self.Data['CC2_S'] = 0x9002
    # DC String 3
    # Spannung
    self.Data['CC3_U'] = 0
    # Strom
    self.Data['CC3_I'] = 0
    # Leistung
    self.Data['CC3_P'] = 0
    # Temperatur
    self.Data['CC3_T'] = 0xf6a0
    # S?
    self.Data['CC3_S'] = 0x0003

    # AC Phase 1
    # Spannung
    self.Data['CA1_U'] = 230.9
    # Strom
    self.Data['CA1_I'] = 1.06
    # Leistung
    self.Data['CA1_P'] = 202
    # Temperatur
    self.Data['CA1_T'] = 5520
    # AC Phase 2
    # Spannung
    self.Data['CA2_U'] = 230.7
    # Strom
    self.Data['CA2_I'] = 1.05
    # Leistung
    self.Data['CA2_P'] = 198
    # Temperatur
    self.Data['CA2_T'] = 0x55a0
    # AC Phase 3
    # Spannung
    self.Data['CA3_U'] = 232.1
    # Strom
    self.Data['CA3_I'] = 1.06
    # Leistung
    self.Data['CA3_P'] = 200
    # Temperatur
    self.Data['CA3_T'] = 5700

    # AC Status
    self.Data['CA_S'] = 0x003c

# # Ende Funktion: ' Constructor ' ################################################################

# #################################################################################################
# # Funktion: ' Destructor '
# # \details
#   \param[in]
#   \param[in]
#   \param[in]
#   \return
# #################################################################################################
    #def __del__(self):

# # Ende Funktion: ' Destructor ' #################################################################

# #################################################################################################
# #  Funktion:      ' _PrintHexa '
## \details        -
#   \param[in]     -
#   \param[in]     -
#   \return          -
# #################################################################################################
  def _PrintHexa(self, Txt, St):
    HexSt=''; TxtSt='';
    for i in range(len(St)):
      HexSt += "%02x" % ord(St[i])
      if ((ord(St[i])>=0x20) and (ord(St[i])<0x7f)):
        TxtSt+=St[i];
      else:
        TxtSt+='.';
    #print "%s%s %s" % (Txt, HexSt, TxtSt)
    print "%s%s" % (Txt, HexSt)

  # #################################################################################################
  # #  Funktion: ' _DspTimer '
  ## \details        -
  #   \param[in]     -
  #   \param[in]     -
  #   \return          -
  # #################################################################################################
  def _DspTimer(self, Txt, Timer, fmt):
    St = ""; Space = ""
    if fmt==1: Space=" "
    d = datetime(1,1,1)+timedelta(seconds=Timer)
    if Timer>86400:
      St = "%s%dh%s%02dm%s%02ds" % (Txt, (Timer//86400)*24+d.hour, Space, d.minute, Space, d.second)
    else:
      St = "%s%02dh%s%02dm%s%02ds" % (Txt, d.hour, Space, d.minute, Space, d.second)
    return St

  # #################################################################################################
  # #  Funktion: ' SndRecv '
  ## \details        -
  #   \param[in]     -
  #   \param[in]     -
  #   \return          -
  # #################################################################################################
  def _SndRecv(self, Addr, Snd, Dbg) :
    Snd="\x62"+chr(Addr)+"\x03"+chr(Addr)+Snd
    Snd+=chr(self._CalcChkSum(Snd))+"\x00"
    self.SocketStream.send(Snd)
    i = 0
    Recv = ''
    data = ''
    while (1):
      try :
        data = self.SocketStream.recv(4096)
      except :
        Recv += data
        break
      if (i < 5):
          Recv += data
          data = ''
      if not data:
          break
    if (len(Recv)>0) and (ord(Recv[0])==255):
      Recv=""
    if Dbg and (len(Recv)>0) and (ord(Recv[0])!=255):
      self._PrintHexa("Sent:", Snd)
      self._PrintHexa("Recv:", Recv)
    return Recv

  # #################################################################################################
  # #  Funktion: ' _ChkSum '
  ## \details        -
  #   \param[in]     -
  #   \param[in]     -
  #   \return          -
  # #################################################################################################
  def _ChkSum(self, St):
    Chk = 0
    if len(St) == 0: return 0
    for i in range(len(St)):
      Chk += ord(St[i])
      Chk %= 256
    if Chk == 0:
      return 1
    else:
      return 0

  # #################################################################################################
  # #  Funktion: ' _CalcChkSum '
  ## \details        -
  #   \param[in]     -
  #   \param[in]     -
  #   \return          -
  # #################################################################################################
  def _CalcChkSum(self, St):
    Chk = 0
    if len(St) == 0: return 0
    for i in range(len(St)):
      Chk -= ord(St[i])
      Chk %= 256
    return Chk

  # #################################################################################################
  # #  Funktion: ' _GetWord '
  ## \details        -
  #   \param[in]     -
  #   \param[in]     -
  #   \return          -
  # #################################################################################################
  def _GetWord(self, St, Idx):
    Val = 0
    Val = ord(St[Idx])+256*ord(St[Idx+1])
    return Val

  # #################################################################################################
  # #  Funktion: ' _GetDWord '
  ## \details        -
  #   \param[in]     -
  #   \param[in]     -
  #   \return          -
  # #################################################################################################
  def _GetDWord(self, St, Idx):
    Val = 0
    Val = ord(St[Idx])+256*ord(St[Idx+1])+65536*ord(St[Idx+2])+256*65536*ord(St[Idx+3])
    return Val

  # #################################################################################################
  # #  Funktion: ' _CnvTemp '
  ## \details        -
  #   \param[in]     -
  #   \param[in]     -
  #   \return          -
  # #################################################################################################
  def _CnvTemp(self, Val):
    T=(int("0x"+TRef, 16)-Val)/448.0+22
    if T<0.0: T=0.0
    if T>99.99: T=99.99
    return T

  # #################################################################################################
  # #  Funktion: ' _CnvCA_S '
  ## \details        -
  #   \param[in]     -
  #   \param[in]     -
  #   \return          -
  # #################################################################################################
  def _CnvCA_S(self, Val):
    # Maybe some mising bit value
    L1="1" if Val & 0x04 else "-"
    L2="2" if Val & 0x08 else "-"
    L3="3" if Val & 0x10 else "-"
    L=L1+L2+L3
    L="L"+L if L!="---" else "-"+L
    I="I" if Val & 0x01 else "-"
    C="C" if Val & 0x02 else "-"
    E="E" if Val & 0x100 else "-"
    return E+I+C+L

  # #################################################################################################
  # #  Funktion: ' _CnvStatusTxt '
  ## \details        -
  #   \param[in]     -
  #   \param[in]     -
  #   \return          -
  # #################################################################################################
  def _CnvStatusTxt(self, Val):
    Txt = "Communication error"
    if Val == 0: Txt = "Off"                        # SMA 1 = Aus
    if Val == 1: Txt = "Idle"                       # SMA 2 = Idle
    if Val == 2: Txt = "Starting"                   # SMA 3 = Starte
    if Val == 3: Txt = "Running-MPP"                # SMA 4 = MPP
    if Val == 4: Txt = "Running-Regulated"          # SMA 5 = Abgeregelt
    if Val == 5: Txt = "Running"                    # SMA 6 = Fahre herunter
                                                    # SMA 7 = Fehler
                                                    # SMA 8 = Warte auf EVU
    return Txt

  # #################################################################################################
  # #  Funktion: ' _GetHistInt '
  ## \details        -
  #   \param[in]     -
  #   \param[in]     -
  #   \return          -
  # #################################################################################################
  def _GetHistInt(self, St):
    St = St.strip()
    if len(St) > 0:
      return int(St.replace(".", ""))
    else: return 0;

  # #################################################################################################
  # #  Funktion: ' _GetHistTime '
  ## \details        -
  #   \param[in]     -
  #   \param[in]     -
  #   \return          -
  # #################################################################################################
  def _GetHistTime(self, t, tref, now):
    dt=timedelta(seconds=tref-t)
    ht=now-dt
    ht=ht.replace(microsecond=0)
    return ht.isoformat()

  # #################################################################################################
  # #  Funktion: ' GetFetchedData '
  ## \details        -
  #   \param[in]     -
  #   \param[in]     -
  #   \return          -
  # #################################################################################################
  def GetFetchedData(self):
    return self.Data

  # #################################################################################################
  # #  Funktion: ' DbgPrintOut '
  ## \details        -
  #   \param[in]     -
  #   \param[in]     -
  #   \return          -
  # #################################################################################################
  def DbgPrintOut(self):

    print "TimeStamp       : {:%m/%d/%y %H:%M %S}".format(self.Data['Now'])
    print "Comm software   : Piko v%s - %s" % (self.Data['RelVer'], self.Data['RelDate'])
    print "Comm host       : %s" % self.Data['host']
    print "Comm port       : %d" % self.Data['port']
    print "Comm status     : %s\n" % self.Data['NetStatus']
    print "Inverter Status : %d (%s)" % (self.Data['Status'], self.Data['StatusTxt'])
    print "Inverter Error  : %s" % self.Data['ErrorCode']
    print "Inverter Name   : %s" % self.Data['InvName']
    print "Inverter SN     : %s" % self.Data['InvSN']
    print "Inverter Ref    : %s" % self.Data['InvRef']
    print "Inverter Version: %s" % self.Data['InvVer']
    print "Inverter Model  : %s" % self.Data['InvModel']
    print "Inverter String : %d" % self.Data['InvString']
    print "Inverter Phase  : %d\n" % self.Data['InvPhase']
    print "Total Time      : %s (%d j)" % (self._DspTimer("", self.Data['InvInstTime'], 1), self.Data['InvInstTime']//86400)
    print "Running Time    : %s" % self._DspTimer("", self.Data['InvRunTime'], 1)
    print "Last Port. upld : %s" % self._DspTimer("", self.Data['InvPortalTime'], 1)
    print "Last Hist. updt : %s" % self._DspTimer("", self.Data['InvHistTime'], 1)
    print "Hist. updt step : %s\n" % self._DspTimer("", self.Data['InvHistStep'], 1)
    print "Total energy    : %d Wh" % self.Data['TotalWh']
    print "Today energy    : %d Wh" % self.Data['TodayWh']
    print "DC Power        : %5d W\nAC Power        : %5d W\nEfficiency      : %5.1f %%\n" % (self.Data['CC_P'], self.Data['CA_P'], self.Data['Eff'])

    print 'DC String 1     : %5.1f V   %4.2f A   %4d W   T=%04x (%5.2f C)  S=%04x' % (self.Data['CC1_U'], self.Data['CC1_I'], self.Data['CC1_P'], self.Data['CC1_T'], self._CnvTemp(self.Data['CC1_T']), self.Data['CC1_S'])
    print 'DC String 2     : %5.1f V   %4.2f A   %4d W   T=%04x (%5.2f C)  S=%04x' % (self.Data['CC2_U'], self.Data['CC2_I'], self.Data['CC2_P'], self.Data['CC2_T'], self._CnvTemp(self.Data['CC2_T']), self.Data['CC2_S'])
    print 'DC String 3     : %5.1f V   %4.2f A   %4d W   T=%04x (%5.2f C)  S=%04x' % (self.Data['CC3_U'], self.Data['CC3_I'], self.Data['CC3_P'], self.Data['CC3_T'], self._CnvTemp(self.Data['CC3_T']), self.Data['CC3_S'])
    print 'AC Status       : %d (%04x %s)' % (self.Data['CA_S'], self.Data['CA_S'], self._CnvCA_S(self.Data['CA_S']))
    print 'AC Phase 1      : %5.1f V   %4.2f A   %4d W   T=%04x (%5.2f C)' % (self.Data['CA1_U'], self.Data['CA1_I'], self.Data['CA1_P'], self.Data['CA1_T'], self._CnvTemp(self.Data['CA1_T']))
    print 'AC Phase 2      : %5.1f V   %4.2f A   %4d W   T=%04x (%5.2f C)' % (self.Data['CA2_U'], self.Data['CA2_I'], self.Data['CA2_P'], self.Data['CA2_T'], self._CnvTemp(self.Data['CA2_T']))
    print 'AC Phase 3      : %5.1f V   %4.2f A   %4d W   T=%04x (%5.2f C)' % (self.Data['CA3_U'], self.Data['CA3_I'], self.Data['CA3_P'], self.Data['CA3_T'], self._CnvTemp(self.Data['CA3_T']))

  # #################################################################################################
  # #  Funktion: ' _GetPikoTimes '
  ## \details        -
  #   \param[in]     -
  #   \param[in]     -
  #   \return          -
  # #################################################################################################
  def _GetPikoTimes(self):

    # Total Running time
    self.Data['InvRunTime'] = 0
    Recv=""; Snd="\x00\x46"
    Recv=self._SndRecv(self.Opt['Addr'], Snd, self.Opt['Dbg'])
    if self._ChkSum(Recv) != 0:
      self.Data['InvRunTime']=self._GetDWord(Recv, 5)

    # Total Install time
    self.Data['InvInstTime'] = 0
    Recv=""; Snd="\x00\x5b"
    Recv=self._SndRecv(self.Opt['Addr'], Snd, self.Opt['Dbg'])
    if self._ChkSum(Recv) != 0:
      self.Data['InvInstTime']=self._GetDWord(Recv, 5)

    # Last history update time and interval
    self.Data['InvHistTime'] = 0
    Recv=""; Snd="\x00\x5d"
    Recv=self._SndRecv(self.Opt['Addr'], Snd, self.Opt['Dbg'])
    if self._ChkSum(Recv) != 0:
      self.Data['InvHistTime']=self.Data['InvInstTime'] - self._GetDWord(Recv, 5)
      if self.Data['InvHistTime'] < 0: self.Data['InvHistTime'] = 0
    self.Data['InvHistStep'] = 0
    Recv=""; Snd="\x00\x5e"

    Recv=self._SndRecv(self.Opt['Addr'], Snd, self.Opt['Dbg'])
    if self._ChkSum(Recv) != 0:
      self.Data['InvHistStep']=self._GetDWord(Recv, 5)

  # #################################################################################################
  # #  Funktion: ' _GetPikoPortalData '
  ## \details        -
  #   \param[in]     -
  #   \param[in]     -
  #   \return          -
  # #################################################################################################
  def _GetPikoPortalData(self):

    # Portal Name & Update Timer
    self.Data['InvPortalTime'] = 0
    Recv=""; Snd="\x00\x92"
    Recv=self._SndRecv(self.Opt['Addr'], Snd, self.Opt['Dbg'])
    if self._ChkSum(Recv) != 0:
      self.Data['InvPortalTime']=self._GetDWord(Recv, 5)
      if self.Data['InvPortalTime']==0xffffffff: self.Data['InvPortalTime']=0;
    InvPortalName = ""
    Recv=""; Snd="\x00\xa6"
    Recv=self._SndRecv(self.Opt['Addr'], Snd, self.Opt['Dbg'])
    if self._ChkSum(Recv) != 0:
      for i in range(32):
        if 0x20 <= ord(Recv[5+i]) <= 0x7f: InvPortalName+=Recv[5+i]

  # #################################################################################################
  # #  Funktion: ' _GetPikoHeader '
  ## \details        -
  #   \param[in]     -
  #   \param[in]     -
  #   \return          -
  # #################################################################################################
  def _GetPikoHeader(self):

    # Get Inverter Model
    self.Data['InvModel'] = ""
    self.Data['InvString'] = 1
    self.Data['InvPhase'] = 1
    Snd="\x00\x90"
    Recv=self._SndRecv(self.Opt['Addr'], Snd, self.Opt['Dbg'])
    if self._ChkSum(Recv) != 0 and len(Recv)>=21:
      for i in range(16):
        if 0x20 <= ord(Recv[5+i]) <= 0x7f: self.Data['InvModel']+=Recv[5+i]
      self.Data['InvString'] = ord(Recv[5+16])
      self.Data['InvPhase'] = ord(Recv[5+23])

    # Get Inverter Version
    InvVer1 = InvVer2 = InvVer3 = 0
    self.Data['InvVer'] = ""
    Recv=""; Snd="\x00\x8a"
    Recv=self._SndRecv(self.Opt['Addr'], Snd, self.Opt['Dbg'])
    if self._ChkSum(Recv) != 0 and len(Recv)==13:
      InvVer1 = self._GetWord(Recv, 5)
      InvVer2 = self._GetWord(Recv, 7)
      InvVer3 = self._GetWord(Recv, 9)
      self.Data['InvVer'] = "%04x %02x.%02x %02x.%02x" % (InvVer1, InvVer2//256, InvVer2%256, InvVer3//256, InvVer3%256)

    # Calc TRef (Default 0xc800)
    if self.Data['InvModel'] == "convert 10T":
      TRef="c800"
    if self.Data['InvModel'] == "PIKO 8.3":
      TRef="c800"
    if self.Data['InvModel'] == "PIKO 5.5":
      TRef="8000"
    if self.Opt['TRef'] != "0": TRef = self.Opt['TRef']

    # Get Inverter Name
    self.Data['InvName'] = ""
    Recv=""; Snd="\x00\x44"
    Recv=self._SndRecv(self.Opt['Addr'], Snd, self.Opt['Dbg'])
    if self._ChkSum(Recv) != 0:
      for i in range(15):
        if 0x20 <= ord(Recv[5+i]) <= 0x7f: self.Data['InvName']+=Recv[5+i]

    # Get Inverter SN
    self.Data['InvSN'] = ""; self.Data['InvRef'] = ""
    Recv=""; Snd="\x00\x50"
    Recv=self._SndRecv(self.Opt['Addr'], Snd, self.Opt['Dbg'])
    if self._ChkSum(Recv) != 0:
      if len(Recv) == 20:
        for i in range(13):
          if 0x20 <= ord(Recv[5+i]) <= 0x7f: self.Data['InvSN']+=Recv[5+i]
      if len(Recv) == 12:
        SN1=ord(Recv[5]); SN2=ord(Recv[6]); SN3=ord(Recv[7]); SN4=ord(Recv[8]); SN5=ord(Recv[9])
        self.Data['InvSN']+="%1x%1x%1x%1x%1x%1x%1x%1x%1x" % (SN1//16, SN1%16, SN3%16, SN2//16, SN2%16, SN5//16, SN5%16, SN4//16, SN4%16)

    # Get Inverter Ref
    Recv=""; Snd="\x00\x51"
    Recv=self._SndRecv(self.Opt['Addr'], Snd, self.Opt['Dbg'])
    if self._ChkSum(Recv) != 0:
      self.Data['InvRef']=self._GetDWord(Recv, 5)

  # #################################################################################################
  # #  Funktion: ' _GetPikoData '
  ## \details        -
  #   \param[in]     -
  #   \param[in]     -
  #   \return          -
  # #################################################################################################
  def _GetPikoData(self):

    # Get Total Wh
    self.Data['TotalWh'] = -1
    Recv=""; Snd="\x00\x45"
    Recv=self._SndRecv(self.Opt['Addr'], Snd, self.Opt['Dbg'])
    if self._ChkSum(Recv) != 0:
      self.Data['TotalWh']=self._GetDWord(Recv, 5)

    # Get Today Wh
    self.Data['TodayWh'] = -1
    Recv=""; Snd="\x00\x9d"
    Recv=self._SndRecv(self.Opt['Addr'], Snd, self.Opt['Dbg'])
    if self._ChkSum(Recv) != 0:
      self.Data['TodayWh']=self._GetDWord(Recv, 5)

    # Debug self.Options
    if self.Opt['Dbg'] :
      for i in range(256):
        if (i != 0x50) and (i != 81):
          Recv=""; Snd="\x00"+chr(i)
          Recv=self._SndRecv(self.Opt['Addr'], Snd, self.Opt['Dbg'])

    # Get Technical data
    self.Data['TechData'] = -1
    Recv=""; Snd="\x00\x43"
    Recv=self._SndRecv(self.Opt['Addr'], Snd, self.Opt['Dbg'])
    if self._ChkSum(Recv) != 0 and (len(Recv)>65):
      self.Data['TechData'] = 1
      self.Data['CC1_U']=self._GetWord(Recv, 5)*1.0/10
      self.Data['CC1_I']=self._GetWord(Recv, 7)*1.0/100
      self.Data['CC1_P']=self._GetWord(Recv, 9)
      self.Data['CC1_T']=self._GetWord(Recv, 11)
      self.Data['CC1_S']=self._GetWord(Recv, 13)
      self.Data['CC2_U']=self._GetWord(Recv, 15)*1.0/10
      self.Data['CC2_I']=self._GetWord(Recv, 17)*1.0/100
      self.Data['CC2_P']=self._GetWord(Recv, 19)
      self.Data['CC2_T']=self._GetWord(Recv, 21)
      self.Data['CC2_S']=self._GetWord(Recv, 23)
      self.Data['CC3_U']=self._GetWord(Recv, 25)*1.0/10
      self.Data['CC3_I']=self._GetWord(Recv, 27)*1.0/100
      self.Data['CC3_P']=self._GetWord(Recv, 29)
      self.Data['CC3_T']=self._GetWord(Recv, 31)
      self.Data['CC3_S']=self._GetWord(Recv, 33)
      self.Data['CA1_U']=self._GetWord(Recv, 35)*1.0/10
      self.Data['CA1_I']=self._GetWord(Recv, 37)*1.0/100
      self.Data['CA1_P']=self._GetWord(Recv, 39)
      self.Data['CA1_T']=self._GetWord(Recv, 41)
      self.Data['CA2_U']=self._GetWord(Recv, 43)*1.0/10
      self.Data['CA2_I']=self._GetWord(Recv, 45)*1.0/100
      self.Data['CA2_P']=self._GetWord(Recv, 47)
      self.Data['CA2_T']=self._GetWord(Recv, 49)
      self.Data['CA3_U']=self._GetWord(Recv, 51)*1.0/10
      self.Data['CA3_I']=self._GetWord(Recv, 53)*1.0/100
      self.Data['CA3_P']=self._GetWord(Recv, 55)
      self.Data['CA3_T']=self._GetWord(Recv, 57)
      self.Data['CA_S']=self._GetWord(Recv, 61)
      self.Data['CC_P']=self.Data['CC1_P']+self.Data['CC2_P']+self.Data['CC3_P']
      self.Data['CA_P']=self.Data['CA1_P']+self.Data['CA2_P']+self.Data['CA3_P']
      if self.Data['CC_P']<1: self.Data['Eff']=0
      else : self.Data['Eff']=self.Data['CA_P']*100.0/self.Data['CC_P']

  # #################################################################################################
  # #  Funktion: ' FetchData '
  ## \details         Die Einsprungsfunktion, ruft alle Funktionen und Klassen auf.
  #   \param[in]    argv
  #   \return            -
  # #################################################################################################
  def FetchData(self, Timers, Portal, Header, Data):

    self.SocketStream = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Setup TCP socket
    self.SocketStream.settimeout(5)
    self.Data['NetStatus']=0
    try:
      self.SocketStream.connect((self.Data['host'],  self.Data['port']))
      self.SocketStream.settimeout(1)
    except socket.error, msg:
      self.Data['NetStatus']=msg

    # Get Inverter Status (0=Stop; 1=dry-run; 3..5=running)
    Status = -1; self.Data['ErrorCode'] = 0;
    if self.Data['NetStatus'] == 0:
      if self.Opt['Dbg']: print "- - - - - - - - - -  D A T A   F R A M E S  - - - - - - - - - -"
      Snd="\x00\x57"
      Recv=self._SndRecv(self.Opt['Addr'], Snd, self.Opt['Dbg'])
      if self._ChkSum(Recv) != 0:
        Status = ord(Recv[5]);
        Error = ord(Recv[6]);
        self.Data['ErrorCode'] = self._GetWord(Recv, 7)
      if (Status > 5): Status = -1

    Now = datetime.now()
    self.Data['Now'] = Now
    self.Data['Status'] = Status
    self.Data['StatusTxt'] = self._CnvStatusTxt(Status)

    if Status != -1:
      if Data == True : self._GetPikoData()
      if Timers == True : self._GetPikoTimes()
      if Portal == True : self._GetPikoPortalData()
      if Header == True : self._GetPikoHeader()

    if self.Opt['Dbg']: print "- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -"
    self.SocketStream.close()

    return Status

# # Ende Funktion: ' FetchData ' ###################################################################

# # Ende Klasse: ' PikoWebRead ' ##################################################################

# # DateiEnde #####################################################################################

