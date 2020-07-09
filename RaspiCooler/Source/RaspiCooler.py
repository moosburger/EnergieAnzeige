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
import RPi.GPIO as GPIO
import time
import os

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

IMPULS_PIN		= 23	#Pin, der zum Transistor fuehrt
SLEEP_TIME		= 30	#Alle wie viel Sekunden die Temperatur ueberprueft wird
MAX_CPU_TEMP	= 40	#Ab welcher CPU Temperatur der Luefter sich drehen soll
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
		tempfile = open("/sys/bus/w1/devices/"+SENSOR_ID+"/w1_slave")
		text = tempfile.read()
		tempfile.close()
		temperature_data = text.split()[-1]
		temperature = float(temperature_data[2:])
		temperature = temperature / 1000
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
def main():

	#Init
	self.log.info("Starte RaspiCooler mit Intervall {} sek.".format(SLEEP_TIME))
	GPIO.setup(IMPULS_PIN, GPIO.OUT)
	GPIO.output(IMPULS_PIN, False)

	while True:
		cpu_temp = get_cpu_temperature()
		sensor_temp = get_sensor_temperature()
		if cpu_temp >= MAX_CPU_TEMP or sensor_temp >= MAX_SENSOR_TEMP :
			GPIO.output(IMPULS_PIN, True)
		else:
			GPIO.output(IMPULS_PIN, False)

		log.info("gemessene CPU Temperatur:" + str(cpu_temp))
		log.info("gemessene Sensor Temperatur:" + str(sensor_temp))

		time.sleep(SLEEP_TIME)

# # Ende Funktion: ' main ' #######################################################################

# #################################################################################################
# #  Funktion: 'Einsprung beim Aufruf  '
# #################################################################################################
if __name__ == '__main__':

    _main(sys.argv)

# # DateiEnde #####################################################################################

