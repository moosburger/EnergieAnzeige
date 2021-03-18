#!/usr/bin/env python3
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
try:
    ImportError = None
    import threading
    import time
    import os
    from datetime import datetime
    from collections import namedtuple as NamedTuple
    import psutil

except Exception as e:
    ImportError = e

# #################################################################################################
# # UmgebungsVariablen / Globals
# #################################################################################################
DiskInfo = NamedTuple('DiskInfo', 'device total used free percentage')
CpuInfo = NamedTuple('CpuInfo', 'physical total max min current usage temp DStemp cores')

# #################################################################################################
# # Python Imports (site-packages)
# #################################################################################################

# #################################################################################################
# # private Imports
# #################################################################################################
try:
    PrivateImportError = None
    import Error
    from configuration import Global as _conf

except Exception as e:
    PrivateImportError = e

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
        def __init__(self, interval, funcObj, logger):

            self.log = logger.getLogger('Host')
            self.callFunc = ['GetBootTimeData', 'GetCpuInfoData', 'GetMemoryInfoData', 'GetCpuInfoData', 'GetDiskUsageData']
            self.mBootTime = ""
            self.mDiskUsage = []
            self.mMemoryInfo = []
            self.mCpuInfo = []
            self.firstRun = True

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

            self.log.info("Starte Raspi Callback mit Intervall {} sek.".format(interval))
            self.mBootTime = self._GetBootTime()

            fncCnt = 0
            while True:
                self.log.debug(self.callFunc[fncCnt])

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
                    self.firstRun = False

                if (self.firstRun == False):
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
                    total = int(partition_usage.total/1024)
                    used = int(partition_usage.used/1024)
                    free = int(partition_usage.free/1024)
                    percentage = float(partition_usage.percent)

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
            total = int(svmem.total/1024)
            used = int(svmem.used/1024)
            free = int(svmem.available/1024)
            percentage = float(svmem.percent)
            MemInfoList.append(DiskInfo('Memory', total, used, free, percentage))

            # get the swap memory details (if exists)
            swap = psutil.swap_memory()
            total = int(swap.total/1024)
            used = int(swap.used/1024)
            free = int(swap.free/1024)
            percentage = float(swap.percent)
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
            physical = int(psutil.cpu_count(logical=False))
            total = int(psutil.cpu_count(logical=True))

            # CPU frequencies
            cpufreq = psutil.cpu_freq()
            max = float(cpufreq.max)
            min = float(cpufreq.min)
            current = float(cpufreq.current)

            # CPU usage
            cores = []
            for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
                cores.append(float(percentage))

            usage = float(psutil.cpu_percent())

            # CPU temp
            ## Wenn ein Dallas DS Sensor angeschlossen ist, liefert psutils den Ds zurück als w1_slave_temp
            ## {'w1_slave_temp': [shwtemp(label='', current=27.187, high=None, critical=None)]}
            ## ohne kommt die Cpu Temp
            ## {'cpu-thermal': [shwtemp(label='', current=51.54, high=None, critical=None)]}
            cputemp = psutil.sensors_temperatures()
            temp = 0
            DStemp = 0
            try:
                temp = cputemp['cpu-thermal'][0].current
            except:
                temp = os.popen('vcgencmd measure_temp').readline()
                temp = float(temp.replace("temp=","").replace("'C\n",""))

            try:
                DStemp = float(cputemp['w1_slave_temp'][0].current)
            except:
                DStemp = float(-1)

            return CpuInfo(physical, total, max, min, current, usage, temp, DStemp, cores)

# # Ende Funktion: ' GetCpuInfo ' ############################################################################

##### Fehlerbehandlung #####################################################
    except IOError as e:
        print('Eine der Bibliotheken konnte nicht geladen werden!\n{}!\n'.format(e))

    except:
        for info in sys.exc_info():
            print ("Fehler: {}".format(info))

# # Ende Klasse: ' CallRaspi ' ####################################################################

# # DateiEnde #####################################################################################