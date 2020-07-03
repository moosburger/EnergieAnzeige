#!/usr/bin/env python
# -*- coding: utf-8 -*-

# #################################################################################################
## \brief     Wetterabfrage an OpenWeather
#  \details
#  \file      OpenWeatherMap.py
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
    import sys
    import os
    import threading
    import datetime
    import time
    import json
    #from influxHandler import influxIO, _SensorData as SensorData
    import requests
    from subprocess import check_output
    from configuration import Global as _conf
    from collections import namedtuple as NamedTuple

except:
    raise

reload(sys)
sys.setdefaultencoding("utf-8")

# #################################################################################################
# # Python Imports (site-packages)
# #################################################################################################

# #################################################################################################
# # private Imports
# #################################################################################################

# #################################################################################################
# # UmgebungsVariablen / Globals
# #################################################################################################

# #################################################################################################
# # Logging geht in dieselbe Datei, trotz verschiedener Prozesse!
# #################################################################################################

SensorData = NamedTuple('SensorData', 'device instance type value timestamp')
# #################################################################################################
# # Funktionen
# # Prototypen
# #################################################################################################

# #################################################################################################
# # Classes: OpenWeatherMap
## \details Pingt in regelmaessigen Abstaenden den Vrm Mqtt Broker an
# https://dev.to/hasansajedi/running-a-method-as-a-background-process-in-python-21li
# #################################################################################################
class OpenWeatherMap(object):

# #################################################################################################
# # Funktion: ' Constructor '
## \details Die Initialisierung der Klasse KeepAlive
#   \param[in]  self der Objectpointer
#   \param[in]  interval
#   \param[in]  mqttClient
#   \param[in] portal_id
#   \return -
# #################################################################################################
    def __init__(self, interval, logger):

        self.log = logger.getLogger('OpenWeatherMap')

        #self.influxHdlr = influxIO(_host = _conf.INFLUXDB_ADDRESS, _port = _conf.INFLUXDB_PORT, _username = _conf.INFLUXDB_USER, _password = _conf.INFLUXDB_PASSWORD, _database = None, _gzip = _conf.INFLUXDB_ZIPPED, logger)
        thread = threading.Thread(target=self.main, args=(interval, ))
        thread.daemon = True
        thread.start()

# # Ende Funktion: ' Constructor ' ################################################################

# #################################################################################################
# # Funktion: ' Destructor '
# #################################################################################################
    #def __del__(self):

# # Ende Funktion: ' Destructor ' #################################################################

# #################################################################################################
# #  Funktion: 'get_rain_level_from_weather '
## \details
#   \param[in] weather
#   \return rain, rain_level
# #################################################################################################
    def get_rain_level_from_weather(self, weather):
        rain = False
        rain_level = 0
        if len(weather) > 0:
            for w in weather:
                if w['icon'] == '09d':
                    rain = True
                    rain_level = 1
                elif w['icon'] == '10d':
                    rain = True
                    rain_level = 2
                elif w['icon'] == '11d':
                    rain = True
                    rain_level = 3
                elif w['icon'] == '13d':
                    rain = True
                    rain_level = 4

        return rain, rain_level

# # Ende Funktion: 'get_rain_level_from_weather ' ######################################################################

# #################################################################################################
# #  Funktion: 'get_weather_conditions '
## \details     https://openweathermap.org/weather-conditions
#   \param[in] weather
#   \return condition
# #################################################################################################
    def get_weather_conditions(self, weather):

        condition = ''
        if len(weather) > 0:
            for w in weather:
                if w['main'] == 'Thunderstorm':
                    condition = 'Gewitter'
                elif w['main'] == 'Drizzle':
                    condition = 'Nieseln'

                elif w['main'] == 'Rain':
                    if ('09' in w['icon']):
                        condition = 'Regenschauer'
                    elif ('10' in w['icon']):
                        condition = 'Regen'
                    elif ('13' in w['icon']):
                        condition = 'gerfierender Regen'

                elif w['main'] == 'Snow':
                    condition = 'Schnee'

                elif w['main'] == 'Atmosphere':
                    condition = 'Nebel'

                elif w['main'] == 'Clear':
                    if ('n' in w['icon']):
                        condition = 'klar'
                    else:
                        condition = 'sonnig'

                elif w['main'] == 'Clouds':
                    if (w['id'] == 801):
                        if ('n' in w['icon']):
                            condition = 'leicht bewoelkt'
                        else:
                            condition = 'heiter'
                    elif w['id'] == 802:
                        condition = 'wolkig'
                    elif w['id'] == 803:
                        condition = 'bewoelkt'
                    else:
                        condition = 'bedeckt'
            #~ 800  01d.png  01n.png  klarer Himmel
            #~ 801  02d.png  02n.png  heiter   1-2 / 8
            #~ 802  03d.png  03n.png  wolkig 3 - 4 /8
            #~ 803  04d.png  04n.png  bewoelkt  5-7 / 8
            #~ 804  04d.png  04n.png  bedeckt  8 / 8

            #~ 3xx  09d.png  09n.png  Nieseln

            #~ 5xx  09d.png  09n.png  Regenschauer
            #~ 5xx  10d.png  10n.png  Regen
            #~ 5xx 13d.png  13n.png  gerfierender Regen

            #~ 6xx  13d.png  13n.png  Schnee

            #~ 7xx  50d.png  50n.png  Nebel
            #~ 2xx  11d.png  11n.png  Gewitter

            #~ Group 2xx: Thunderstorm  Gewitter
            #~ Group 3xx: Drizzle   Niesel
            #~ Group 5xx: Rain  Regen
            #~ Group 6xx: Snow  Schnee
            #~ Group 7xx: Atmosphere    Atmosphaere
            #~ Group 800: Clear Klar
            #~ Group 80x: Clouds    Wolken

        return condition

# # Ende Funktion: 'get_weather_conditions ' ######################################################################

# #################################################################################################
# #  Funktion: 'call_api '
## \details
#   \param[in]     -
#   \return          -
# #################################################################################################
    def call_api(self):

        data = {}
        r = requests.get(
            "http://api.openweathermap.org/data/2.5/weather?id={}&appid={}&units=metric".format(_conf.CITY_CODE, _conf.OPENWEATHERMAP_API_KEY))

        if r.status_code == 200:
            current_data = r.json()
            data['weather'] = current_data['main']
            rain, rain_level = self.get_rain_level_from_weather(current_data['weather'])
            data['weather']['rain'] = rain
            data['weather']['rain_level'] = rain_level
            condition = self.get_weather_conditions(current_data['weather'])
            data['weather']['condition'] = condition
            data['weather']['w_speed'] = current_data['wind']['speed']
            data['weather']['w_deg'] = current_data['wind']['deg']
            data['weather']['dt'] = current_data['dt']
            del data['weather']['temp_max']
            del data['weather']['temp_min']
            del data['weather']['feels_like']

        r2 = requests.get(
            "http://api.openweathermap.org/data/2.5/uvi?lat={}&lon={}&appid={}".format(_conf.LAT, _conf.LON, _conf.OPENWEATHERMAP_API_KEY))
        if r2.status_code == 200:
            data['uvi'] = r2.json()

        r3 = requests.get(
            "http://api.openweathermap.org/data/2.5/forecast?id={}&appid={}&units=metric".format(_conf.CITY_CODE, _conf.OPENWEATHERMAP_API_KEY))

        if r3.status_code == 200:
            forecast = r3.json()['list']
            data['forecast'] = []
            for f in forecast:
                rain, rain_level = self.get_rain_level_from_weather(f['weather'])
                condition = self.get_weather_conditions(f['weather'])

                data['forecast'].append({
                    "dt": f['dt'],
                    "fields": {
                        "condition": condition,
                        "temp": float(f['main']['temp']),
                        "humidity": float(f['main']['humidity']),
                        "rain": rain,
                        "rain_level": int(rain_level),
                        "pressure": float(float(f['main']['pressure']))
                    }
                })

        return data

# # Ende Funktion: ' call_api ' #################################################################

# #################################################################################################
# #  Funktion: 'out_sensors '
## \details
#   \param[in]     -
#   \return          -
# #################################################################################################
    def get_Weather(self):

        try:
            out_info = self.call_api()
            #timestamp = datetime.datetime.utcnow()
            timestamp = datetime.datetime.utcfromtimestamp(out_info['weather']['dt']).isoformat()

            sensor_data = SensorData('WEATHER', 'Current', ['Condition', 'W_Speed', 'W_Deg', 'Pressure', 'Humidity', 'Temp'], [ out_info['weather']['condition'], out_info['weather']['w_speed'], out_info['weather']['w_deg'], out_info['weather']['pressure'], out_info['weather']['humidity'], out_info['weather']['temp'] ], timestamp)
            self.log.info(sensor_data)

            for f in out_info['forecast']:
                sensor_data = SensorData('WEATHER', 'FORECAST', ['fields', ], [ f['fields'] ], datetime.datetime.utcfromtimestamp(f['dt']).isoformat())
                self.log.info(sensor_data)

        except Exception as err:
            print(err)
            self.log.error(err)

# # Ende Funktion: ' out_sensors ' #################################################################

# #################################################################################################
# #  Funktion: ' _main '
## \details         Die Einsprungsfunktion, ruft alle Funktionen und Klassen auf.
#   \return            -
# #################################################################################################
    def main(self, interval):

        self.log.info("Starte")

        while True:
            self.get_Weather()
            #Updates kommen ca alle 10 min
            time.sleep(interval)

# # Ende Funktion: ' _main' #######################################################################

# #################################################################################################
# #  Funktion: 'Einsprung beim Aufruf  '
# #################################################################################################
    if __name__ == '__init__':

        __init__()

# # DateiEnde #####################################################################################

