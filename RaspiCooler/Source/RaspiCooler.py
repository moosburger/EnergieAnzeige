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
# siehe https://de.pinout.xyz/pinout/pin13_gpio27 fur das Pinout
# https://tutorials-raspberrypi.de/lueftersteuerung/
# https://www.kompf.de/weather/pionewiremini.html

IMPULS_PIN		= 17	#Pin 11 an Steckerleiste, der zum Transistor fuehrt
SLEEP_TIME		= 60	#Alle wie viel Sekunden die Temperatur ueberprueft wird
MAX_CPU_TEMP	= 45	#Ab welcher CPU Temperatur der Luefter sich drehen soll
MAX_SENSOR_TEMP	= 30	#Ab welcher Temperatur im Gehaeuse der Luefter sich drehen soll
SENSOR_ID 		= ''	#ID des Sensors, BITTE ANPASSEN, falls kein Sensor vorhanden leer lassen

GRIDLOST_PIN	= 22	#Pin 15 an Steckerleiste, der zum Transistor fuehrt
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
#		tempfile = open("/sys/bus/w1/devices/"+SENSOR_ID+"/w1_slave")
#		text = tempfile.read()
#		tempfile.close()
#		temperature_data = text.split()[-1]
#		temperature = float(temperature_data[2:])

		cputemp = psutil.sensors_temperatures()
		temperature = cputemp['w1_slave_temp'][0].current

		return float(temperature)
	except:
		return -1

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

	#Init
	bFirstRun = True
	bLastGridLost = True

	log.info("Starte RaspiCooler mit Intervall {} sek.".format(SLEEP_TIME))
	GPIO.setup(IMPULS_PIN, GPIO.OUT)
	GPIO.output(IMPULS_PIN, False)
	GPIO.setup(GRIDLOST_PIN, GPIO.OUT)
	GPIO.output(GRIDLOST_PIN, False)

	dbgFile = '/mnt/dietpi_userdata/RaspiCooler/DebugIsTrue.txt'
	gridLostFile = '/mnt/dietpi_userdata/RaspiCooler/GridLost.log'

	while True:
		bDebug = os.path.exists(dbgFile)
		cpu_temp = get_cpu_temperature()
		sensor_temp = get_sensor_temperature()

		if (bDebug):
			log.info("   CPU Temperatur: {}".format(cpu_temp))
			log.info("Sensor Temperatur: {}".format(sensor_temp))

		if cpu_temp > MAX_CPU_TEMP + 2.5:
			GPIO.output(IMPULS_PIN, True)
			if (bDebug):
				log.info("Luefter: Ein")
				log.info("   CPU Temperatur: {}".format(cpu_temp))
				log.info("Sensor Temperatur: {}".format(sensor_temp))

		elif cpu_temp < MAX_CPU_TEMP - 2.5:
			GPIO.output(IMPULS_PIN, False)
			if (bDebug):
				log.info("Luefter: Aus")
				log.info("   CPU Temperatur: {}".format(cpu_temp))
				log.info("Sensor Temperatur: {}".format(sensor_temp))

		bGridLost = os.path.exists(gridLostFile)
		if (not bLastGridLost == bGridLost) or (bFirstRun == True):
			log.info(f"Netz verloren: {bGridLost}")
			bLastGridLost = bGridLost

		if (bGridLost):
			GPIO.output(GRIDLOST_PIN, True)
		else:
			GPIO.output(GRIDLOST_PIN, False)

		bFirstRun = False
		time.sleep(SLEEP_TIME)

# # Ende Funktion: ' main ' #######################################################################

# #################################################################################################
# #  Funktion: 'Einsprung beim Aufruf  '
# #################################################################################################
if __name__ == '__main__':

    _main(sys.argv)

# # DateiEnde #####################################################################################

