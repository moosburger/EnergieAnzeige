#!/usr/bin/env python
# -*- coding: utf-8 -*-

# #################################################################################################
## \brief     Piko Inverter communication software
#  \details	Anschluss eines Kuehlkoerpers und Temperatur Sensor
#  \file      cooler.py
#
#  \date      Erstellt am: 04.04.2014
#  \author    Felix Stern
# Website:      www.tutorials-raspberrypi.de
#
# <History\> ######################################################################################
# Version     Datum       Ticket#     Beschreibung
# 1.0         04.04.2014
#
# #################################################################################################

# #################################################################################################
# # Python Imports (Standard Library)
# #################################################################################################
import sys
import RPi.GPIO as GPIO
import time
import os
import psutil

import logging
from logging.config import fileConfig

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
#except:
#    PrivateImport = False

# #################################################################################################
# # UmgebungsVariablen / Globals
# #################################################################################################

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

IMPULS_PIN		= 17	#Pin, der zum Transistor fuehrt
SLEEP_TIME		= 60	#Alle wie viel Sekunden die Temperatur ueberprueft wird
MAX_CPU_TEMP	= 45	#Ab welcher CPU Temperatur der Luefter sich drehen soll
MAX_SENSOR_TEMP	= 30	#Ab welcher Temperatur im Gehaeuse der Luefter sich drehen soll
SENSOR_ID 		= ''	#ID des Sonsors, BITTE ANPASSEN, falls kein Sensor vorhanden leer lassen

# #################################################################################################
# # Logging
# #################################################################################################
fileConfig('/mnt/dietpi_userdata/RaspiCooler/logging_config.ini')
log = logging.getLogger('RaspiCooler')

# #################################################################################################
# # Funktionen
# # Prototypen
# # if __name__ == '__main__':
# #################################################################################################

# #################################################################################################
# #  Funktion:      ' get_sensor_temperature '
## 	\details
#   \param[in]	-
#   \return     -
# #################################################################################################
def get_sensor_temperature():
	try:
		#tempfile = open("/sys/bus/w1/devices/"+SENSOR_ID+"/w1_slave")
		#text = tempfile.read()
		#tempfile.close()
		#temperature_data = text.split()[-1]
		#temperature = float(temperature_data[2:])
		cputemp = psutil.sensors_temperatures()
		temperature = cputemp['w1_slave_temp'][0].current

		return float(temperature)
	except:
		return 0

# # Ende Funktion: ' get_sensor_temperature ' #####################################################

# #################################################################################################
# #  Funktion:      ' get_cpu_temperature '
## 	\details
#   \param[in]	-
#   \return     -
# #################################################################################################
def get_cpu_temperature():
	temp = os.popen('vcgencmd measure_temp').readline()
	return float(temp.replace("temp=","").replace("'C\n",""))

# # Ende Funktion: ' get_cpu_temperature ' ########################################################

# #################################################################################################
# #  Funktion:      ' main '
## 	\details
#   \param[in]	-
#   \return     -
# #################################################################################################
def _main(argv):

	iLogCount = -1
	#Init
	log.info("Starte RaspiCooler mit Intervall {} sek.".format(SLEEP_TIME))
	GPIO.setup(IMPULS_PIN, GPIO.OUT)
	GPIO.output(IMPULS_PIN, False)

	while True:
		cpu_temp = get_cpu_temperature()
		sensor_temp = get_sensor_temperature()
		#if cpu_temp >= MAX_CPU_TEMP or sensor_temp >= MAX_SENSOR_TEMP :
		if cpu_temp > MAX_CPU_TEMP + 2.5:
			GPIO.output(IMPULS_PIN, True)
		elif cpu_temp < MAX_CPU_TEMP - 2.5:
			GPIO.output(IMPULS_PIN, False)

		#~ if (iLogCount > 10) or (iLogCount == -1):
			#~ log.info("   CPU Temperatur: {}".format(cpu_temp))
			#~ log.info("Sensor Temperatur: {}".format(sensor_temp))
			#~ iLogCount = 0

		time.sleep(SLEEP_TIME)
		iLogCount = iLogCount + 1

# # Ende Funktion: ' main ' #######################################################################

# #################################################################################################
# #  Funktion: 'Einsprung beim Aufruf  '
# #################################################################################################
if __name__ == '__main__':

    _main(sys.argv)

# # DateiEnde #####################################################################################

