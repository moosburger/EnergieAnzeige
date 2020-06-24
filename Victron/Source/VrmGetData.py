#!/usr/bin/env python
# -*- coding: utf-8 -*-

# #################################################################################################
## \brief     Main zur Abfrage des Vrm mqtt Brokers in der CCGX/VenusGX
#  \details   Sortiert die Werte dann in die InfluxDatenbank ein
#             konfiguriert wird das ganze über die configuration.py
#             Der für Victron notwendige KeepAlive wird über die VrmKeepAlive.py gehandelt
#  \file      VrmGetData.py
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
import json
import ssl
import logging
from logging.config import fileConfig
#from logging.handlers import RotatingFileHandler
from datetime import datetime
import paho.mqtt.client as mqtt
from configuration import Global as _conf, PvInverter as PvInv, Grid, Battery, VeBus, System

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
    from VrmKeepAlive import KeepAlive
    import Error
    import Utils
    from Host import Raspi_CallBack
    from influxHandler import influxIO, _SensorData as SensorData
    from dataExport import ExportDataFromInflux
except:
    PrivateImport = False

# #################################################################################################
# # UmgebungsVariablen / Globals
# #################################################################################################

# #################################################################################################
# # Logging
# #################################################################################################
fileConfig('/mnt/dietpi_userdata/EnergieAnzeige/logging_config.ini')
log = logging.getLogger('VrmGetData')
#~ log.setLevel(_conf.LOG_LEVEL)
#~ fh = RotatingFileHandler(_conf.LOG_FILEPATH, maxBytes=_conf.LOG_SIZE, backupCount=_conf.LOG_BACKUP)
#~ fh.setLevel(logging.DEBUG)
#~ log.addHandler(fh)
#~ formatter = logging.Formatter(_conf.LOG_FORMAT)
#~ fh.setFormatter(formatter)
#~ log.addHandler(fh)

#log.debug('Debug-Nachricht')
#log.info('Info-Nachricht')
#log.warning('Warnhinweis')
#log.error('Fehlermeldung')
#log.critical('Schwerer Fehler')

# #################################################################################################
# # Funktionen
# # Prototypen
# # if __name__ == '__main__':
# #################################################################################################

# Um alle Daten in der Influx zu loeschen
#  influx -database 'EnergieAnzeige'
# DROP SERIES FROM /.*/

# #################################################################################################
# #  Funktion: '_get_vrm_broker_url '
## \details
#   \param[in]     vrm_portal_id
#   \return          Broker als String
# #################################################################################################
def _get_vrm_broker_url(vrm_portal_id):
    sum = 0
    for character in vrm_portal_id.lower().strip():
        sum += ord(character)
    broker_index = sum % 128
    return 'mqtt{}.victronenergy.com'.format(broker_index)

# # Ende Funktion: ' _get_vrm_broker_url ' ########################################################

# #################################################################################################
# #  Funktion: 'on_connect '
## \details     callback der beim Connect aufgerufen wird
#   \param[in]     self
#   \param[in]     mosq
#   \param[in]     obj
#   \param[in]     rc
#   \return         -
# #################################################################################################
def on_connect(self, mosq, obj, rc):
    mqtt_errno, mid = self.subscribe('N/%s/#' % _conf.PORTAL_ID, 1)
    log.info(str(mqtt.connack_string(rc)))

# # Ende Funktion: ' ' ############################################################################

# #################################################################################################
# #  Funktion: 'on_disconnect '
## \details     callback der beim DisConnect aufgerufen wird
#   \param[in]     client
#   \param[in]     userdata
#   \param[in]     rc
#   \return         -
# #################################################################################################
def on_disconnect(client, userdata, rc):
    log.info(str(mqtt.connack_string(rc)))

# # Ende Funktion: 'on_disconnect ' ###############################################################

# #################################################################################################
# #  Funktion: ' on_message_fallback'
## \details         This function is called everytime the topic is published to.
#   \param[in]     mosq
#   \param[in]     obj
#   \param[in]     msg
#   \return         -
# #################################################################################################
def on_message_fallback(client, userdata, message):

    log.info ("Msg.Payload: {}\n\t\t\t\t\t\t- Msg.Topic: {}\n\t\t\t\t\t\t- Msg.qos: {}\n\t\t\t\t\t\t- Userdata: {}".format(message.payload, message.topic, message.qos, userdata))

# # Ende Funktion: ' on_message_fallback' ##################################################################

# #################################################################################################
# #  Funktion: ' on_message'
## \details         This function is called everytime the topic is published to.
#   \param[in]     mosq
#   \param[in]     obj
#   \param[in]     msg
#   \return         -
# #################################################################################################
def on_message(client, userdata, message):

    timestamp = datetime.utcnow()
    myVal = _checkPayload(client, userdata, message)
    if (myVal is None):
        return

    _extract_Data(message, myVal, timestamp)

# # Ende Funktion: ' on_message' ##################################################################

# #################################################################################################
# #  Funktion: 'on_publish '
## \details     callback der beim publishen aufgerufen wird
#   \param[in]     client
#   \param[in]     userdata
#   \param[in]     rc
#   \return         -
# #################################################################################################
def on_publish(client, userdata, mid):
    pass

# # Ende Funktion: 'on_publish ' ##################################################################

# #################################################################################################
# #  Funktion: 'on_subscribe '
## \details     callback der beim subscriben aufgerufen wird
#   \param[in]     mosq
#   \param[in]     obj
#   \param[in]     mid
#   \param[in]     granted_qos
#   \return         -
# #################################################################################################
def on_subscribe(mosq, userdata, mid, granted_qos):
    log.info("Subscribed: {} {} {} {}".format(str(mid), str(granted_qos), str(userdata), str(mosq)))

# # Ende Funktion: 'on_subscribe ' ################################################################

# #################################################################################################
# #  Funktion: 'on_unsubscribe '
## \details     callback der beim unsubscribe aufgerufen wird
#   \param[in]     client
#   \param[in]     userdata
#   \param[in]     mid
#   \return         -
# #################################################################################################
def on_unsubscribe(client, userdata, mid):
    pass

# # Ende Funktion: 'on_unsubscribe ' ##############################################################

# #################################################################################################
# #  Funktion: 'on_log '
## \details     callback der mqtt Klasse zum loggen
#   \param[in]     client
#   \param[in]     userdata
#   \param[in]     level
#   \param[in]     buf
#   \return         -
# #################################################################################################
def on_log(client, userdata, level, buf):
    log.debug('Client: {0}\n log: {1}\n Level: {2}\n UserData: {3}'.format(client, buf, level, userdata))

# # Ende Funktion: 'on_log ' ######################################################################

# #################################################################################################
# #  Funktion: 'on_Raspi '
## \details     callback der mqtt Klasse zum loggen
#   \param[in]     client
#   \param[in]     userdata
#   \param[in]     level
#   \param[in]     buf
#   \return         -
# #################################################################################################
def on_Raspi(obj, Raspi):

    timestamp = datetime.utcnow()
## BootTime noch in sep. Datei, zum auslesen und vergleich on Reboot erfolgt, wenn andere Zeit und Datum

    _cpuLabel = 'Cpu'
    if (obj == 'GetBootTimeData'):
        log.debug('GetBootTimeData')
        bootTime = Raspi.GetBootTimeData()
        sensor_data = SensorData(_conf.HOST_INSTANCE, 'CpuInfo', ['BootTime',], [bootTime,], timestamp)
        influxHdlr._send_sensor_data_to_influxdb(sensor_data)

    if (obj == 'GetCpuInfoData'):
        log.debug('GetCpuInfoData')
        CpuInfo = Raspi.GetCpuInfoData()
        _typ = []
        _val = []
        for j, core in enumerate(CpuInfo.cores):
            _typ.append('UsageCore{}'.format(j))
            _val.append(core)

        _typ.extend(['PhysicalCores', 'TotalCores', 'MaxFreq', 'MinFreq', 'ActFreq', 'Usage', 'Temp'])
        _val.extend([CpuInfo.physical, CpuInfo.total, CpuInfo.max, CpuInfo.min, CpuInfo.current, CpuInfo.usage, CpuInfo.temp])

        sensor_data = SensorData(_conf.HOST_INSTANCE, 'CpuInfo', _typ, _val, timestamp)
        influxHdlr._send_sensor_data_to_influxdb(sensor_data)

    if (obj == 'GetMemoryInfoData'):
        log.debug('GetMemoryInfoData')
        Memorys = Raspi.GetMemoryInfoData() # Werte in KB
        for ram in Memorys:
            sensor_data = SensorData(_conf.HOST_INSTANCE, ram.device, ['Total', 'Used', 'Available', 'Percentage'], [ram.total, ram.used, ram.free, ram.percentage], timestamp)
            influxHdlr._send_sensor_data_to_influxdb(sensor_data)

    if (obj == 'GetDiskUsageData'):
        log.debug('GetDiskUsageData')
        Disks = Raspi.GetDiskUsageData() # Werte in KB
        for disk in Disks:
            sensor_data = SensorData(_conf.HOST_INSTANCE, disk.device, ['Total', 'Used', 'Free', 'Percentage'], [disk.total, disk.used, disk.free, disk.percentage], timestamp)
            influxHdlr._send_sensor_data_to_influxdb(sensor_data)

# # Ende Funktion: 'on_Raspi ' ######################################################################

# #################################################################################################
# #  Funktion: '_get_Sma_Current '
## \details     -
#   \param[in]
#   \return
# #################################################################################################
def _get_Sma_Current(device, instance, AcPower, timestamp):

    #Strom
    AcL1Current = 0
    SmaV, = influxHdlr._Query_influxDb([_conf.SMA_VL1,], device, 'last')
    if SmaV > 0:
       AcL1Current = AcPower / SmaV

    AcL1Current = _check_Data_Type(AcL1Current)
    sensor_data = SensorData(device, instance, ["AcL1Current",], [AcL1Current,], timestamp)

    return sensor_data

# # Ende Funktion: '_get_Sma_Current ' ######################################################################

# #################################################################################################
# #  Funktion: '_get_Total_Power '
## \details     -
#   \param[in]
#   \return
# #################################################################################################
def _get_Total_Power(device, query, otherPower, timestamp):

    #Leistung Pv
    AcPvOnGridPower, = influxHdlr._Query_influxDb([query,], device, 'last')
    AcPvOnGridPower = _check_Data_Type(AcPvOnGridPower)
    #Gesamt Piko + akt. Sma
    AcPvOnGridPower = AcPvOnGridPower + otherPower
    sensor_data = SensorData(System.RegEx, System.Label1, ["AcPvOnGridPower",], [AcPvOnGridPower,], timestamp)

    return sensor_data

# # Ende Funktion: '_get_Total_Power ' ######################################################################

# #################################################################################################
# #  Funktion: '_get_Total_Consumption '
## \details     -
#   \param[in]
#   \return
# #################################################################################################
def _get_Total_Consumption(instance, timestamp):

    ConsPower1, ConsPower2, ConsPower3 = influxHdlr._Query_influxDb([_conf.LastL1, _conf.LastL2, _conf.LastL3], System.RegEx, 'last')
    AcConsumptionOnInputPower = _check_Data_Type(ConsPower1 + ConsPower2 + ConsPower3)
    sensor_data = SensorData(System.RegEx, instance, ["AcConsumptionOnInputPower",], [AcConsumptionOnInputPower,], timestamp)

    return sensor_data

# # Ende Funktion: '_get_Total_Consumption ' ######################################################################

# #################################################################################################
# #  Funktion: '_check_Data_Type '
## \details     -
#   \return
# #################################################################################################
def _check_Data_Type(myVal):

    #float, int, str, list, dict, tuple
    if (isinstance(myVal, basestring)):
        pass
    elif (isinstance(myVal, int)):
        myVal = float(myVal)
    elif (isinstance(myVal, long)):
        myVal = float(myVal)
    elif (isinstance(myVal, float)):
        myVal = float(myVal)
    else:
        myVal = str(myVal)

    return myVal

# # Ende Funktion: '_check_Data_Type ' ######################################################################

# #################################################################################################
# #  Funktion: '_checkPayload '
## \details     -
#   \param[in]     msg
#   \return
# #################################################################################################
def _checkPayload(client, userdata, message):

    myDict = []
    retVal = None
    try:
        if not (message.payload):
            log.error ("Msg.Topic: {}".format(message.topic))
            log.error ("Msg.Payload: {}".format(message.payload))
            return retVal

        payload = message.payload.decode('utf-8')
        # ConvertBytearry to dictonary
        myDict=json.loads(payload)
        retVal = myDict['value']

    except ValueError as e:
        log.error("ValueError in '_checkPayload': {}".format(e))
        log.error ("Msg.Payload: {}".format(message.payload))
        log.error ("Msg.Topic: {}".format(message.topic))
        log.error ("Userdata: {}".format(userdata))

    except:
        for info in sys.exc_info():
            log.error("Fehler in '_checkPayload': {}".format(info))
            print ("Fehler in '_checkPayload': {}".format(info))

        print ("Msg: {}".format(message))
        log.error ("Msg: {}".format(message))

    return retVal

# # Ende Funktion: '_checkPayload ' ######################################################################

# #################################################################################################
# #  Funktion: '_extract_Data '
## \details     -
#   \param[in]     msg
#   \return
# #################################################################################################
def _extract_Data(msg, myVal, timestamp):
    global EnergyPerDay

    topic = str(msg.topic).strip()

    smaRegEx = "N/{0}/([^/]+)/([^/]+)/(.*)".format(_conf.PORTAL_ID)
    match = Utils.RegEx(smaRegEx, topic, Utils.fndFrst, Utils.Srch, '')
    if match:
        device = match.group(1)
        #Messwert Typ
        type = match.group(3).replace("/", "")  #Ac/Energy/Forward

        sensor_data_list = []
        if (device == PvInv.RegEx) and (match.group(2) == PvInv.Inst1):
            instance = PvInv.Label1

            # Beim SMA den Strom berechnen, die Gesamtleistung und ~Energie aller PvInverter
            if (type == 'AcPower'):
                #Strom
                sensor_data_list.append(_get_Sma_Current(device, instance, myVal, timestamp))
                #Gesamt Piko + akt. Sma
                sensor_data_list.append(_get_Total_Power(device, _conf.PIKO, myVal, timestamp))

        elif (device == PvInv.RegEx) and (match.group(2) == PvInv.Inst2):
            instance = PvInv.Label2

            # Beim Piko die Gesamtleistung und ~Energie aller PvInverter
            if (type == 'AcPower'):
                #Gesamt Sma + akt. Piko
                sensor_data_list.append(_get_Total_Power(device, _conf.SMA, myVal, timestamp))

        elif (device == Grid.RegEx) and (match.group(2) == Grid.Inst1):
            instance = Grid.Label1
        elif (device == Battery.RegEx) and (match.group(2) == Battery.Inst1):
            instance = Battery.Label1
        elif (device == VeBus.RegEx) and (match.group(2) == VeBus.Inst1):
            instance = VeBus.Label1
        elif (device == System.RegEx):
            instance = System.Label1

            # Der gesamte Verbrauch aller Lasten, für die Prozentuale Aufteilung
            if (type == 'AcConsumptionOnInputL1Power') or (type == 'AcConsumptionOnInputL2Power') or (type == 'AcConsumptionOnInputL3Power'):
               sensor_data_list.append(_get_Total_Consumption(instance, timestamp))

        else:
            instance = str(match.group(2))

        #float, int, str, list, dict, tuple
        myVal = _check_Data_Type(myVal)
        sensor_data_list.insert(0,SensorData(device, instance, [type,], [myVal,], timestamp))

        for sensor_data in sensor_data_list:
            retVal = influxHdlr._send_sensor_data_to_influxdb(sensor_data)
            if (retVal == False):
                log.warning("Fehler beim schreiben von {}".format(sensor_data))

# # Ende Funktion: '_extract_Data ' ######################################################################

# #################################################################################################
# #  Funktion: ' _main '
## \details         Die Einsprungsfunktion, ruft alle Funktionen und Klassen auf.
#   \param[in]    argv
#   \return            -
# #################################################################################################
def _main(argv):
    global EnergyPerDay, influxHdlr

    log.info('VrmGetData started')
    try:
        ## Import fehlgeschlagen
        if (PrivateImport == False):
            raise ImportError

        #raise Error.AllgBuild('Übergebens Argument (Pfad) ist leer!')

        EnergyPerDay = False
        _MqttPort = _conf.MQTT_PORT

        ## Database initialisieren
        influxHdlr = influxIO(_host = _conf.INFLUXDB_ADDRESS, _port = _conf.INFLUXDB_PORT, _username = _conf.INFLUXDB_USER, _password = _conf.INFLUXDB_PASSWORD, _database = None, _gzip = _conf.INFLUXDB_ZIPPED, logger = logging)
        influxHdlr._init_influxdb_database(_conf.INFLUXDB_DATABASE)

        ## Client instanzieren
        mqttClient = mqtt.Client(_conf.CLIENT_ID, protocol=mqtt.MQTTv311)

        ## Background KeepAlive
        KeepAlive(_conf.SCHED_INTERVAL, mqttClient, _conf.PORTAL_ID, logging)

        ## Extended Logging
        #mqttClient.enable_logger(log)

        ## sichere Verbindung
        if (_conf.USE_TSL == True):
            mqttClient.tls_set(_conf.TSL_CERTIFICATION, tls_version=ssl.PROTOCOL_TLSv1_2 )
            mqttClient.username_pw_set(_conf.MQTT_USERNAME, _conf.MQTT_PASSWORD)
            _MqttPort = _conf.MQTT_TSL_PORT
            CCGX = _get_vrm_broker_url(_conf.PORTAL_ID)

        ## Callbacks on connecting, and on receiving a message
        mqttClient.on_connect = on_connect
        #mqttClient.on_message = on_message_fallback

        ## Grid
        for topic in Grid.Topics:
            mqttClient.message_callback_add('N/{0}/{1}/+/{2}'.format( _conf.PORTAL_ID, Grid.RegEx, topic), on_message)

        ## Bmv
        for topic in Battery.Topics:
            mqttClient.message_callback_add('N/{0}/{1}/+/{2}'.format( _conf.PORTAL_ID, Battery.RegEx, topic), on_message)

        ## PvInverter SMA + Piko
        for topic in PvInv.Topics:
            mqttClient.message_callback_add('N/{0}/{1}/+/{2}'.format( _conf.PORTAL_ID, PvInv.RegEx, topic), on_message)

        ## System
        for topic in System.Topics:
            mqttClient.message_callback_add('N/{0}/{1}/+/{2}'.format( _conf.PORTAL_ID, System.RegEx, topic), on_message)

        ## VeBus
        for topic in VeBus.Topics:
            mqttClient.message_callback_add('N/{0}/{1}/+/{2}'.format( _conf.PORTAL_ID, VeBus.RegEx, topic), on_message)

        ## Settings
        ##for topic in Setting.Topics:
        ##    mqttClient.message_callback_add('N/{0}/{1}/+/{2}'.format( _conf.PORTAL_ID, Setting.RegEx, topic), on_message)

        mqttClient.on_subscribe = on_subscribe
        #mqttClient.on_log = on_log
        ##mqttClient.on_unsubscribe = on_unsubscribe
        ##mqttClient.on_publish = on_publish
        mqttClient.on_disconnect = on_disconnect

        ## Once everything has been set up, we can (finally) connect to the broker
        connac = mqttClient.connect(_conf.CCGX, int(_MqttPort), int(_conf.SCHED_INTERVAL))
        log.debug(connac)

        ## auslesen der Raspi Temperatur
        Raspi_CallBack(_conf.HOST_INTERVAL, on_Raspi, logging)

        ## Daten zu csv und SolarLog exportieren
        ExportDataFromInflux(_conf.EXPORT_INTERVAL, logging)

        ## Once we have told the client to connect, let the client object run itself
        mqttClient.loop_forever()
        mqttClient.disconnect()

    ##### Fehlerbehandlung #####################################################
    except ImportError as e:
        log.error('Eine der Bibliotheken konnte nicht geladen werden!\n{}!\n'.format(e))
        print 'Eine der Bibliotheken konnte nicht geladen werden!\n{}!\n'.format(e)

    except IOError as e:
        log.error("IOError: {}".format(e.msg))
        print 'IOError'

    except Error.OpenFile as e:
        print e.openfileInfo %{'msg': e.msg}

    except Error.Dateiname as e:
        print e.dateinameInfo %{'msg': e.msg}

    except:
        for info in sys.exc_info():
            log.error("Fehler: {}".format(info))
            print ("Fehler: {}".format(info))

# # Ende Funktion: ' _main' #######################################################################

# #################################################################################################
# #  Funktion: 'Einsprung beim Aufruf  '
# #################################################################################################
if __name__ == '__main__':

    _main(sys.argv)

# # DateiEnde #####################################################################################

