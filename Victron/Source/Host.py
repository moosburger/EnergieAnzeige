#!/usr/bin/env python
# -*- coding: utf-8 -*-

# #################################################################################################
## \brief     Hilfsfunktionen
#  \details   Hilfsfunktionen die den Rapi (Host für Grafane) auslesen
#  \file      Host.py
#
#  \date      Erstellt am: 26.05.2020
#  \author    moosburger
#
# <History\> ######################################################################################
# Version     Datum      Ticket#     Beschreibung
# 1.0         26.05.2020
#
# #################################################################################################

# #################################################################################################
# # Python Imports (Standard Library)
# #################################################################################################
#import string
import threading
import time
import logging
from datetime import datetime
import psutil
from collections import namedtuple as NamedTuple
from configuration import Global as _conf

# #################################################################################################
# # Python Imports (site-packages)
# #################################################################################################

# #################################################################################################
# # private Imports
# #################################################################################################
import Error

# #################################################################################################
# # UmgebungsVariablen / Globals
# #################################################################################################
DiskInfo = NamedTuple('DiskInfo', 'device total used free percentage')
CpuInfo = NamedTuple('CpuInfo', 'physical total max min current usage temp cores')

# #################################################################################################
# # Logging geht in dieselbe Datei, trotz verschiedener Prozesse!
# #################################################################################################
log = logging.getLogger('Host')
log.setLevel(_conf.LOG_LEVEL)
fh = logging.FileHandler(_conf.LOG_FILEPATH)
fh.setLevel(logging.DEBUG)
log.addHandler(fh)
formatter = logging.Formatter(_conf.LOG_FORMAT)
fh.setFormatter(formatter)
log.addHandler(fh)

#log.debug('Debug-Nachricht')
#log.info('Info-Nachricht')
#log.warning('Warnhinweis')
#log.error('Fehlermeldung')
#log.critical('Schwerer Fehler')

# #################################################################################################
# # Funktionen
# # Prototypen
# #################################################################################################

# #################################################################################################
# # Classes: CallRaspi
## \details Pingt in regelmässigen Abständen den Vrm Mqtt Broker an
# https://dev.to/hasansajedi/running-a-method-as-a-background-process-in-python-21li
# #################################################################################################
class Raspi_CallBack():  #object

# #################################################################################################
# # Funktion: ' Constructor '
## \details Die Initialisierung der Klasse KeepAlive
#   \param[in]  self der Objectpointer
#   \param[in]  interval
#   \param[in] CallBack
#   \return -
# #################################################################################################
    def __init__(self, interval, funcObj):
        #self.interval = interval
        #self.funcObj = funcObj
        self.callFunc = ['GetBootTimeData', 'GetCpuInfoData', 'GetMemoryInfoData', 'GetCpuInfoData', 'GetDiskUsageData']
        self.mBootTime = ""
        self.mDiskUsage = []
        self.mMemoryInfo = []
        self.mCpuInfo = []

        thread = threading.Thread(target=self.run, args=(interval, funcObj))
        thread.daemon = True
        thread.start()

# # Ende Funktion: ' Constructor ' ################################################################

# #################################################################################################
# # Funktion: ' Destructor '
# #################################################################################################
    #def __del__(self):

# # Ende Funktion: ' Destructor ' #################################################################

# #################################################################################################
# # Anfang Funktion: ' run '
## \details Liest die Cpu Temperatur des Raspi aus
#   \param[in]  -
#   \return Temperatur
# #################################################################################################
    def run(self, interval, funcObj):

        log.info("Starte Raspi Callback mit Intervall {} sek.".format(self.interval))

        self.mBootTime = self._GetBootTime()

        fncCnt = 0
        while True:
            log.debug(self.callFunc[fncCnt])

            if (self.callFunc[fncCnt] == 'GetDiskUsageData'):
                self.mDiskUsage = self._GetDiskUsage()
            if (self.callFunc[fncCnt] == 'GetMemoryInfoData'):
                self.mMemoryInfo = self._GetMemoryInfo()
            if (self.callFunc[fncCnt] == 'GetCpuInfoData'):
                self.mCpuInfo = self._GetCpuInfo()

            funcObj(self.callFunc[fncCnt], self)
            fncCnt = fncCnt + 1
            if fncCnt >= len(self.callFunc):
                fncCnt = 1 # BootTime nur einmal

            time.sleep(interval)

# # Ende Funktion: ' run ' ###############################################################################

# #################################################################################################
# # Anfang Funktion: ' _get_size '
## \details Liest die Cpu Temperatur des Raspi aus
#   \param[in]  -
#   \return Temperatur
# #################################################################################################
    def _get_size(self, bytes, suffix="B".format()):
        """
        Scale bytes to its proper format
        e.g:
            1253656 => '1.20MB'
            1253656678 => '1.17GB'
        """
        factor = 1024
        for unit in ["", "K", "M", "G", "T", "P"]:
            if bytes < factor:
                return '{:.2f}{}{}'.format(bytes, unit, suffix)
            bytes /= factor

# # Ende Funktion: ' _get_size ' ############################################################################

# #################################################################################################
# # Anfang Funktion: ' GetBootTime '
## \details Liest die Cpu Temperatur des Raspi aus
#   \param[in]  -
#   \return Temperatur
# #################################################################################################
    def GetBootTimeData(self):

        return self.mBootTime

# # Ende Funktion: ' GetBootTime ' ############################################################################

# #################################################################################################
# # Anfang Funktion: ' GetDiskUsage '
## \details Liest die Cpu Temperatur des Raspi aus
#   \param[in]  -
#   \return Temperatur
# #################################################################################################
    def GetDiskUsageData(self):

        return self.mDiskUsage

# # Ende Funktion: ' GetDiskUsage ' ############################################################################

# #################################################################################################
# # Anfang Funktion: ' GetMemoryInfo '
## \details
#   \param[in]  -
#   \return
# #################################################################################################
    def GetMemoryInfoData(self):

        return self.mMemoryInfo

# # Ende Funktion: ' GetMemoryInfo ' ############################################################################

# #################################################################################################
# # Anfang Funktion: ' GetCpuInfo '
## \details
#   \param[in]  -
#   \return
# #################################################################################################
    def GetCpuInfoData(self):

        return self.mCpuInfo

# # Ende Funktion: ' GetCpuInfo ' ############################################################################

# #################################################################################################
# # Anfang Funktion: ' GetBootTime '
## \details Liest die Cpu Temperatur des Raspi aus
#   \param[in]  -
#   \return Temperatur
# #################################################################################################
    def _GetBootTime(self):

        # Boot Time
        boot_time_timestamp = psutil.boot_time()
        bt = datetime.fromtimestamp(boot_time_timestamp)
        return ("{}/{}/{} {}:{}:{}".format(bt.year, bt.month, bt.day, bt.hour, bt.minute, bt.second))

# # Ende Funktion: ' GetBootTime ' ############################################################################

# #################################################################################################
# # Anfang Funktion: ' GetDiskUsage '
## \details Liest die Cpu Temperatur des Raspi aus
#   \param[in]  -
#   \return Temperatur
# #################################################################################################
    def _GetDiskUsage(self):

        DiskInfoList = []
        partitions = psutil.disk_partitions()
        for partition in partitions:

            device = partition.device
            total = 0
            used = 0
            free = 0
            percentage = 0
            valid = True

            try:
                partition_usage = psutil.disk_usage(partition.mountpoint)

            except PermissionError as e:
                valid = False

            if (valid == True):
                total = partition_usage.total/1024
                used = partition_usage.used/1024
                free = partition_usage.free/1024
                percentage = partition_usage.percent

            DiskInfoList.append(DiskInfo(device, total, used, free, percentage))

        return DiskInfoList

# # Ende Funktion: ' GetDiskUsage ' ############################################################################

# #################################################################################################
# # Anfang Funktion: ' GetMemoryInfo '
## \details
#   \param[in]  -
#   \return
# #################################################################################################
    def _GetMemoryInfo(self):

        MemInfoList = []
        # get the memory details
        svmem = psutil.virtual_memory()
        total = svmem.total/1024
        used = svmem.used/1024
        free = svmem.available/1024
        percentage = svmem.percent
        MemInfoList.append(DiskInfo('Memory', total, used, free, percentage))

        # get the swap memory details (if exists)
        swap = psutil.swap_memory()
        total = swap.total/1024
        used = swap.used/1024
        free = swap.free/1024
        percentage = swap.percent
        MemInfoList.append(DiskInfo('Swap', total, used, free, percentage))

        return MemInfoList

# # Ende Funktion: ' GetMemoryInfo ' ############################################################################

# #################################################################################################
# # Anfang Funktion: ' GetCpuInfo '
## \details
#   \param[in]  -
#   \return
# #################################################################################################
    def _GetCpuInfo(self):

        # number of cores
        physical = psutil.cpu_count(logical=False)
        total = psutil.cpu_count(logical=True)

        # CPU frequencies
        cpufreq = psutil.cpu_freq()
        max = cpufreq.max
        min = cpufreq.min
        current = cpufreq.current

        # CPU usage
        cores = []
        for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
            cores.append(percentage)

        usage = psutil.cpu_percent()

        # CPU temp
        cputemp = psutil.sensors_temperatures()
        temp = cputemp['cpu-thermal'][0].current

        return CpuInfo(physical, total, max, min, current, usage, temp, cores)

# # Ende Funktion: ' GetCpuInfo ' ############################################################################

# # Ende Klasse: ' CallRaspi ' ####################################################################

# # DateiEnde #####################################################################################