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
import sys
import os
import datetime
import logging
import requests
import json
from subprocess import check_output
#from dotenv import load_dotenv
from configuration import Global as _conf

#reload(sys)
#sys.setdefaultencoding("utf-8")

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
# # Logging
# #################################################################################################
log = logging.getLogger('OpenWeatherMap')
log.setLevel(_conf.LOG_LEVEL)
#~ fh = logging.FileHandler(_conf.LOG_FILEPATH)
#~ fh.setLevel(logging.DEBUG)
#~ log.addHandler(fh)
#~ formatter = logging.Formatter(_conf.LOG_FORMAT)
#~ fh.setFormatter(formatter)

current_dir = os.path.dirname(os.path.abspath(__file__))
#load_dotenv(dotenv_path="{}/.env".format(current_dir))

openweathermap_api_key = '19752eafbc22eeb16e376c53fe811fa1'#os.getenv("OPENWEATHERMAP_API_KEY")
lat = 48.4667
lon = 11.9333
city_name = '2869449'
reader = '{}/reader.js'.format(current_dir)

# #################################################################################################
# # Funktion: ' Destructor '
# #################################################################################################
def get_rain_level_from_weather(weather):
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

# #################################################################################################
# # Funktion: ' Destructor '
# #################################################################################################
def get_weather_conditions(weather):
    #~ "weather":[{"id":803,"main":"Clouds","description":"broken clouds","icon":"04d"}]
    condition = ''

    #print weather
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
                condition = 'klarer Himmel'

            elif w['main'] == 'Clouds':
                if w['id'] == '801':
                    condition = 'heiter'
                elif w['id'] == '802':
                    condition = 'wolkig'
                elif w['id'] == '803':
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


# #################################################################################################
# # Funktion: ' Destructor '
# #################################################################################################
def openweathermap():
    data = {}
    r = requests.get(
        "http://api.openweathermap.org/data/2.5/weather?id={}&appid={}&units=metric".format(city_name, openweathermap_api_key))

    if r.status_code == 200:
        current_data = r.json()
        data['weather'] = current_data['main']
        rain, rain_level = get_rain_level_from_weather(current_data['weather'])
        data['weather']['rain'] = rain
        data['weather']['rain_level'] = rain_level

        print get_weather_conditions(current_data['weather'])

    #print ("http://api.openweathermap.org/data/2.5/forecast?id={}&appid={}&units=metric".format(city_name,openweathermap_api_key))
    r2 = requests.get(
        "http://api.openweathermap.org/data/2.5/uvi?lat={}&lon={}&appid={}".format(lat, lon, openweathermap_api_key))
    if r2.status_code == 200:
        data['uvi'] = r2.json()

    r3 = requests.get(
        "http://api.openweathermap.org/data/2.5/forecast?id={}&appid={}&units=metric".format(city_name,openweathermap_api_key))

    if r3.status_code == 200:
        forecast = r3.json()['list']
        data['forecast'] = []
        for f in forecast:
            rain, rain_level = get_rain_level_from_weather(f['weather'])
            print f
            print get_weather_conditions(f['weather'])
            print

            data['forecast'].append({
                "dt": f['dt'],
                "fields": {
                    "temp": float(f['main']['temp']),
                    "humidity": float(f['main']['humidity']),
                    "rain": rain,
                    "rain_level": int(rain_level),
                    "pressure": float(float(f['main']['pressure']))
                }
            })

        return data

# #################################################################################################
# # Funktion: ' Destructor '
# #################################################################################################
def persists(measurement, fields, location, time):
    #logging.info("{} {} [{}] {}".format(time, measurement, location, fields))

    #print("{} {} [{}] {}".format(time, measurement, location, fields))
    pass
    #~ influx_client.write_points([{
        #~ "measurement": measurement,
        #~ "tags": {"location": location},
        #~ "time": time,
        #~ "fields": fields
    #~ }])

# #################################################################################################
# # Funktion: ' Destructor '
# #################################################################################################
def out_sensors():
    try:
        out_info = openweathermap()
        current_time = datetime.datetime.utcnow()

        persists(measurement='home_pressure',
                 fields={"value": float(out_info['weather']['pressure'])},
                 location="out",
                 time=current_time)
        persists(measurement='home_humidity',
                 fields={"value": float(out_info['weather']['humidity'])},
                 location="out",
                 time=current_time)
        persists(measurement='home_temperature',
                 fields={"value": float(out_info['weather']['temp'])},
                 location="out",
                 time=current_time)
        persists(measurement='home_rain',
                 fields={"value": out_info['weather']['rain'], "level": out_info['weather']['rain_level']},
                 location="out",
                 time=current_time)
        persists(measurement='home_uvi',
                 fields={"value": float(out_info['uvi']['value'])},
                 location="out",
                 time=current_time)
        for f in out_info['forecast']:
            persists(measurement='home_weather_forecast',
                     fields=f['fields'],
                     location="out",
                     time=datetime.datetime.utcfromtimestamp(f['dt']).isoformat())

    except Exception as err:
        logging.error(err)


# #################################################################################################
# # Funktion: ' Destructor '
# #################################################################################################

out_sensors()

# # Ende Klasse: ' KeepAlive ' ####################################################################

# # DateiEnde #####################################################################################

