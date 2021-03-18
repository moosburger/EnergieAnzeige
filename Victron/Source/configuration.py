#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# #################################################################################################
## \brief     Konfigurationsdatei für VrmGetData
#  \details   DBUS topics -> https://github.com/victronenergy/venus/wiki/dbus
#  \file      configuration.py
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
import logging

# #################################################################################################
# # UmgebungsVariablen
# #################################################################################################
class Global():
    PORTAL_ID = 'PortalID'
    CCGX = '192.168.100.100'
    CLIENT_ID = 'ForGrafana'
    TSL_CERTIFICATION = '/venus-ca.crt'
    USE_TSL = False

    MQTT_USERNAME = 'Victron Username'
    MQTT_PASSWORD = 'Victron Password'
    MQTT_PORT = 1883
    MQTT_TSL_PORT = 8883

    SCHED_INTERVAL = 30          #  seconds delay

    OPENWEATHERMAP_API_KEY = 'Vour Api Key'
    LAT = 45.4567
    LON = 15.9533
    CITY_CODE = '123456'
    CITY_NAME = 'Stadt'

    PERCENTAGE_INTERVAL = 60
    EXPORT_INTERVAL = 120
    EXPORT_FILEPATH = '/mnt/dietpi_userdata/SolarExport/'

    HOST_INTERVAL = 240
    HOST_LABEL = 'Host'
    HOST_INSTANCE ='Raspi'

    INFLUXDB_ADDRESS = '192.168.100.102'
    INFLUXDB_PORT = 8086
    INFLUXDB_USER = None
    INFLUXDB_PASSWORD = None
    INFLUXDB_ZIPPED = False
    INFLUXDB_DATABASE = 'EnergieAnzeige'
    INFLUXDB_DATABASE_LONG = 'MonatsAnzeige'

    MODBUS_PORT = 502
    MODBUS_PIKO_IP = "192.168.100.142"
    MODBUS_SMA_IP = "192.168.100.143"

# #################################################################################################
# # Query auf Influx für zsätzliche Infos aus Berechnungen
# #################################################################################################
    #PIKO = "SELECT last(AcPower) FROM pvinverter where instance='PIKO'"
    #PIKO_VL1 = "SELECT last(AcL1Voltage) FROM pvinverter where instance='PIKO'"
    #PIKO_VL2 = "SELECT last(AcL2Voltage) FROM pvinverter where instance='PIKO'"
    #PIKO_VL3 = "SELECT last(AcL3Voltage) FROM pvinverter where instance='PIKO'"
    #PIKO_IL1 = "SELECT last(AcL1Current) FROM pvinverter where instance='PIKO'"
    #PIKO_IL2 = "SELECT last(AcL2Current) FROM pvinverter where instance='PIKO'"
    #PIKO_IL3 = "SELECT last(AcL3Current) FROM pvinverter where instance='PIKO'"
    PIKO_ENERGY1 = "SELECT last(AcL1EnergyForward) FROM pvinverter where instance='PIKO'"
    PIKO_ENERGY2 = "SELECT last(AcL2EnergyForward) FROM pvinverter where instance='PIKO'"
    PIKO_ENERGY3 = "SELECT last(AcL3EnergyForward) FROM pvinverter where instance='PIKO'"
    #PIKO_ENERGY_TOTAL = "SELECT last(AcEnergyForwardTotal) FROM pvinverter where instance='PIKO'"
    #PIKO_ENERGY_LASTDAY = "SELECT last(AcEnergyForwardDay) FROM pvinverter where instance='PIKO' and time > now() - 26h"

    #SMA = "SELECT last(AcPower) FROM pvinverter where instance='SMA'"
    #SMA_VL1 = "SELECT last(AcL1Voltage) FROM pvinverter where instance='SMA'"
    #SMA_VL2 = "SELECT last(AcL2Voltage) FROM pvinverter where instance='SMA'"
    #SMA_VL3 = "SELECT last(AcL3Voltage) FROM pvinverter where instance='SMA'"
    #SMA_IL1 = "SELECT last(AcL1Current) FROM pvinverter where instance='SMA'"
    #SMA_IL2 = "SELECT last(AcL2Current) FROM pvinverter where instance='SMA'"
    #SMA_IL3 = "SELECT last(AcL3Current) FROM pvinverter where instance='SMA'"
    SMA_ENERGY1 = "SELECT last(AcL1EnergyForward) FROM pvinverter where instance='SMA'"
    SMA_ENERGY2 = "SELECT last(AcL2EnergyForward) FROM pvinverter where instance='SMA'"
    SMA_ENERGY3 = "SELECT last(AcL3EnergyForward) FROM pvinverter where instance='SMA'"
    #SMA_ENERGY_TOTAL = "SELECT last(AcEnergyForwardTotal) FROM pvinverter where instance='SMA'"
    #SMA_ENERGY_LASTDAY = "SELECT last(AcEnergyForwardDay) FROM pvinverter where instance='SMA' and time > now() - 26h"

    #PvOnGridL1 = "SELECT last(AcPvOnGridL1Power) FROM system where instance='Gateway'"
    #PvOnGridL2 = "SELECT last(AcPvOnGridL2Power) FROM system where instance='Gateway'"
    #PvOnGridL3 = "SELECT last(AcPvOnGridL3Power) FROM system where instance='Gateway'"

    #L1Power = "SELECT last(AcL1Power) FROM grid where instance='Meter'"
    #L2Power = "SELECT last(AcL2Power) FROM grid where instance='Meter'"
    #L3Power = "SELECT last(AcL3Power) FROM grid where instance='Meter'"
    AllPower= "SELECT last(AcPower) FROM grid where instance='Meter'"

    #DcBattPower = "SELECT last(DcBatteryPower) FROM system where instance='Gateway'"
    #Dc0Power = "SELECT last(Dc0Power) FROM vebus where instance='MultiPlus-II'"
    AcBattPower = "SELECT last(AcActiveInL1P) FROM vebus where instance='MultiPlus-II'"

    LastL1 = "SELECT last(AcConsumptionOnInputL1Power) FROM system where instance='Gateway'"
    LastL2 = "SELECT last(AcConsumptionOnInputL2Power) FROM system where instance='Gateway'"
    LastL3 = "SELECT last(AcConsumptionOnInputL3Power) FROM system where instance='Gateway'"

# #################################################################################################
# # Topics für die Pv Inverter
# #################################################################################################
class PvInverter():
    """
        Ac/Energy/Forward-          {"value": 18024.213}
        Ac/L1/Current-              {"value": 0.0}
        Ac/L1/Energy/Forward-	    {"value": 6008.0265710869517}
        Ac/L1/Power-	            {"value": 0.0}
        Ac/L1/Voltage-	            {"value": 230.800003439188}
        Ac/L2/Current-	            {"value": 0.0}
        Ac/L2/Energy/Forward-	    {"value": 6008.4146137872212}
        Ac/L2/Power-	            {"value": 0.0}
        Ac/L2/Voltage-	            {"value": 230.30000343173742}
        Ac/L3/Current-	            {"value": 0.5000000074505806}
        Ac/L3/Energy/Forward-	    {"value": 6007.7718151258268}
        Ac/L3/Power-	            {"value": 9.0}
        Ac/L3/Voltage-	            {"value": 230.60000343620777}
        Ac/MaxPower	                {"value": 3000.0}
        Ac/Power-	                {"value": 9.0}

        AcEnergyForwardTotal
        AcEnergyForwardDay
        AcEnergyForwardMonth
        AcEnergyForwardYear
        AcEnergyForwardDaySoFar
        AcEnergyForwardMonthSoFar
        AcEnergyForwardYearSoFar

        Connected	                {"value": 1}
        CustomName	                {"value": ""}
        DeviceInstance	            {"value": 24}
        FirmwareVersion	            {"value": "0200 04.03 04.12"}
        Mgmt/Connection	            {"value": "192.168.2.50 - 126 (sunspec)"}
        Mgmt/ProcessName	        {"value": "/opt/victronenergy/dbus-fronius/dbus-fronius"}
        Mgmt/ProcessVersion	        {"value": "1.3.2"}
        Position	                {"value": 0}
        ProductId	                {"value": 41284}
        ProductName	                {"value": "PIKO Solar Inverter"}
        Serial	                    {"value": "90505MES0000"}
        StatusCode-	                {"value": 11}
                        0=Startup 0; 1=Startup 1; 2=Startup 2; 3=Startup
                        3; 4=Startup 4; 5=Startup 5; 6=Startup 6; 7=Running;
                        8=Standby; 9=Boot loading; 10=Error
    """

    Inst1 = '20'
    Label1 = 'SMA'
    Inst2 = '24'
    Label2 = 'PIKO'
    RegEx = 'pvinverter'
    Topics = ['Ac/L1/Current', 'Ac/L1/Energy/Forward', 'Ac/L1/Power', 'Ac/L1/Voltage',
                'Ac/L2/Current', 'Ac/L2/Energy/Forward', 'Ac/L2/Power', 'Ac/L2/Voltage',
                'Ac/L3/Current', 'Ac/L3/Energy/Forward', 'Ac/L3/Power', 'Ac/L3/Voltage',
                'Ac/Power' ,'StatusCode' ]

# #################################################################################################
# # Topics für das Grid
# #################################################################################################
class Grid():
    """ grid/30/Ac/Current-	            {"value": 0.629}
        grid/30/Ac/Energy/Forward-	    {"value": 1084.8}
        grid/30/Ac/Energy/Reverse-	    {"value": 782.5}
        grid/30/Ac/L1/Current-	        {"value": -1.258}
        grid/30/Ac/L1/Energy/Forward-	{"value": 55.600000000000001}   <- kWh  - bought
        grid/30/Ac/L1/Energy/Reverse-	{"value": 497.90000000000003}   <- kWh  - sold
        grid/30/Ac/L1/Power-	        {"value": -264.5}
        grid/30/Ac/L1/Voltage-	        {"value": 231.30000000000001}
        grid/30/Ac/L2/Current-	        {"value": 0.86099999999999999}
        grid/30/Ac/L2/Energy/Forward-	{"value": 73.100000000000009}
        grid/30/Ac/L2/Energy/Reverse-	{"value": 153.80000000000001}
        grid/30/Ac/L2/Power-	        {"value": 120.7}
        grid/30/Ac/L2/Voltage-	        {"value": 229.80000000000001}
        grid/30/Ac/L3/Current-	        {"value": 1.026}
        grid/30/Ac/L3/Energy/Forward	{"value": 132.0}
        grid/30/Ac/L3/Energy/Reverse-	{"value": 130.5}
        grid/30/Ac/L3/Power-	        {"value": 151.90000000000001}
        grid/30/Ac/L3/Voltage-	        {"value": 230.80000000000001}
        grid/30/Ac/Power-	            {"value": 8.0999999999999996}
        grid/30/Ac/Voltage-	            {"value": 230.60000000000002}
        grid/30/Connected	            {"value": 1}
        grid/30/CustomName	            {"value": ""}
        grid/30/DeviceInstance	        {"value": 30}
        grid/30/DeviceType	            {"value": 345}
        grid/30/ErrorCode	            {"value": 0}
        grid/30/FirmwareVersion	        {"value": 6}
        grid/30/Mgmt/Connection	        {"value": "/dev/ttyUSB0"}
        grid/30/Mgmt/ProcessName	    {"value": "/opt/victronenergy/dbus-cgwacs/dbus-cgwacs"}
        grid/30/Mgmt/ProcessVersion	    {"value": "1.9.0"}
        grid/30/ProductId	            {"value": 45069}
        grid/30/ProductName	            {"value": "Grid meter"}
        grid/30/Serial	                {"value": "308053T"}
    """

    Inst1 = '30'
    Label1 = 'Meter'
    RegEx = 'grid'
    Topics = [ 'Ac/Current', 'Ac/Energy/Forward', 'Ac/Energy/Reverse', 'Ac/Power', 'Ac/Voltage',
                'Ac/L1/Current', 'Ac/L1/Energy/Forward', 'Ac/L1/Energy/Reverse', 'Ac/L1/Power', 'Ac/L1/Voltage',
                'Ac/L2/Current', 'Ac/L2/Energy/Forward', 'Ac/L2/Energy/Reverse', 'Ac/L2/Power', 'Ac/L2/Voltage',
                'Ac/L3/Current', 'Ac/L3/Energy/Forward', 'Ac/L3/Energy/Reverse', 'Ac/L3/Power', 'Ac/L3/Voltage' ]

# #################################################################################################
# # Topics für das BMV-700
# #################################################################################################
class Battery():
    """ battery/258/Alarms/HighStarterVoltage-	        {"value": 0}
        battery/258/Alarms/HighTemperature-	            {"value": 0}
        battery/258/Alarms/HighVoltage-	                {"value": 0}
        battery/258/Alarms/LowSoc-	                    {"value": 0}
        battery/258/Alarms/LowStarterVoltage-	        {"value": 0}
        battery/258/Alarms/LowTemperature-	            {"value": 0}
        battery/258/Alarms/LowVoltage-	                {"value": 0}
        battery/258/Alarms/MidVoltage-	                {"value": 0}
        battery/258/Connected	                        {"value": 1}
        battery/258/ConsumedAmphours-	                {"value": -13.600000381469727}
        battery/258/CustomName	                        {"value": ""}
        battery/258/Dc/0/Current-	                    {"value": -8.1999998092651367}
        battery/258/Dc/0/Power-	                        {"value": -415.27999877929688}
        battery/258/Dc/0/Voltage-	                    {"value": 51.909999847412109}
        battery/258/DeviceInstance	                    {"value": 258}
        battery/258/Devices/0/CustomName	            {"value": ""}
        battery/258/Devices/0/DeviceInstance	        {"value": 258}
        battery/258/Devices/0/FirmwareVersion	        {"value": 776}
        battery/258/Devices/0/ProductId	                {"value": 515}
        battery/258/Devices/0/ProductName	            {"value": "BMV-700"}
        battery/258/Devices/0/ServiceName	            {"value": "com.victronenergy.battery.ttyO2"}
        battery/258/FirmwareVersion	                    {"value": 776}
        battery/258/History/AutomaticSyncs-	            {"value": 4}
        battery/258/History/AverageDischarge-	        {"value": -236.19999694824219}
        battery/258/History/ChargeCycles-	            {"value": 1}
        battery/258/History/ChargedEnergy-	            {"value": 97.330001831054688}
        battery/258/History/DeepestDischarge	        {"value": -236.19999694824219}
        battery/258/History/DischargedEnergy-           {"value": 82.870002746582031}
        battery/258/History/DischargedEnergy-	        {"value": 82.879997253417969}
        battery/258/History/FullDischarges-	            {"value": 0}
        battery/258/History/HighVoltageAlarms	        {"value": 0}
        battery/258/History/LastDischarge-	            {"value": -187.60000610351562}
        battery/258/History/LowVoltageAlarms-	        {"value": 0}
        battery/258/History/MaximumVoltage-	            {"value": 63.090000152587891}
        battery/258/History/MinimumVoltage-	            {"value": 47.209999084472656}
        battery/258/History/TimeSinceLastFullCharge-    {"value": 348467}
        battery/258/History/TotalAhDrawn-	            {"value": -1639.5}
        battery/258/Mgmt/Connection	                    {"value": "VE.Direct"}
        battery/258/Mgmt/ProcessName	                {"value": "vedirect-dbus"}
        battery/258/Mgmt/ProcessVersion	                {"value": "3.45"}
        battery/258/ProductId	                        {"value": 515}
        battery/258/ProductName	                        {"value": "BMV-700"}
        battery/258/Relay/0/State-	                    {"value": 0}
        battery/258/Serial	                            {"value": "HQ184666JII"}
        battery/258/Settings/HasMidVoltage	            {"value": 0}
        battery/258/Settings/HasStarterVoltage	        {"value": 0}
        battery/258/Settings/HasTemperature	            {"value": 0}
        battery/258/Soc-	                            {"value": 98.0}
        battery/258/TimeToGo-	                        {"value": 136440.0}
    """

    Inst1 = '258'
    Label1 = 'BMV-700'
    RegEx = 'battery'
    Topics = ['Alarms/HighStarterVoltage', 'Alarms/HighTemperature', 'Alarms/HighVoltage', 'Alarms/LowSoc', 'Alarms/LowStarterVoltage', 'Alarms/LowTemperature', 'Alarms/LowVoltage', 'Alarms/MidVoltage',
                        'ConsumedAmphours', 'Dc/0/Current', 'Dc/0/Power', 'Dc/0/Voltage',
                        'History/AutomaticSyncs', 'History/AverageDischarge', 'History/ChargeCycles', 'History/ChargedEnergy', 'History/DeepestDischarge', 'History/DischargedEnergy', 'History/DischargedEnergy', 'History/FullDischarges',
                        'History/HighVoltageAlarms', 'History/LastDischarge', 'History/LowVoltageAlarms', 'History/MaximumVoltage', 'History/MinimumVoltage', 'History/TimeSinceLastFullCharge', 'History/TotalAhDrawn',
                        'Relay/0/State', 'Soc', 'TimeToGo' ]

# #################################################################################################
# # Topics für das System
# #################################################################################################
class System():
    """ system/0/Ac/ActiveIn/Source	                    {"value": 1}
        system/0/Ac/Consumption/L1/Power	            {"value": 161.39999999999998}
        system/0/Ac/Consumption/L2/Power	            {"value": 118.40000000000001}
        system/0/Ac/Consumption/L3/Power	            {"value": 158.70000000000002}
        system/0/Ac/Consumption/NumberOfPhases	        {"value": 3}
        system/0/Ac/ConsumptionOnInput/L1/Power-	    {"value": 161.39999999999998}
        system/0/Ac/ConsumptionOnInput/L2/Power-	    {"value": 118.40000000000001}
        system/0/Ac/ConsumptionOnInput/L3/Power-	    {"value": 158.70000000000002}
        AcConsumptionOnInputPower
        system/0/Ac/ConsumptionOnInput/NumberOfPhases	{"value": 3}
        system/0/Ac/Grid/DeviceType	                    {"value": 345}
        system/0/Ac/Grid/L1/Power-	                    {"value": -260.60000000000002}
        system/0/Ac/Grid/L2/Power-	                    {"value": 118.40000000000001}
        system/0/Ac/Grid/L3/Power-	                    {"value": 150.70000000000002}
        AcPvOnGridPower
        system/0/Ac/Grid/NumberOfPhases	                {"value": 3}
        system/0/Ac/Grid/ProductId	                    {"value": 45069}
        system/0/Ac/PvOnGrid/L1/Power-	                {"value": 20.0}
        system/0/Ac/PvOnGrid/L2/Power-	                {"value": 0.0}
        system/0/Ac/PvOnGrid/L3/Power-	                {"value": 9.0}
        system/0/Ac/PvOnGrid/NumberOfPhases	            {"value": 3}
        system/0/Ac/PvOnOutput/L1/Power-	            {"value": 20.0}
        system/0/Ac/PvOnOutput/L2/Power-	            {"value": 0.0}
        system/0/Ac/PvOnOutput/L3/Power-	            {"value": 9.0}
        system/0/Ac/PvOnOutput/NumberOfPhases	        {"value": 3}
        system/0/ActiveBatteryService	                {"value": "com.victronenergy.vebus/261"}
        system/0/AutoSelectedBatteryMeasurement	        {"value": "com_victronenergy_battery_258/Dc/0"}
        system/0/AutoSelectedTemperatureService	        {"value": "MultiPlus-II 48/5000/70-50 on VE.Bus"}
        system/0/AvailableBatteries	                    {"value": "{\"com.victronenergy.battery/258\": {\"type\": \"battery\", \"name\": \"BMV-700\", \"channel\": null}}"}
        system/0/AvailableBatteryMeasurements	        {"value": {"default": "Automatic", "com_victronenergy_vebus_261/Dc/0": "MultiPlus-II 48/5000/70-50 on VE.Bus", "nobattery": "No battery monitor", "com_victronenergy_battery_258/Dc/0": "BMV-700 on VE.Direct"}}
        system/0/AvailableBatteryServices	            {"value": "{\"default\": \"Automatic\", \"com.victronenergy.vebus/261\": \"MultiPlus-II 48/5000/70-50 on VE.Bus\", \"nobattery\": \"No battery monitor\", \"com.victronenergy.battery/258\": \"BMV-700 on VE.Direct\"}"}
        system/0/AvailableTemperatureServices	        {"value": {"default": "Automatic", "nosensor": "No sensor", "com.victronenergy.vebus/261/Dc/0/Temperature": "MultiPlus-II 48/5000/70-50 on VE.Bus"}}
        system/0/Batteries	 {"value": [{"soc": 97.5, "active_battery_service": true, "temperature": 16.0, "power": -385, "current": -8.3000001907348633, "instance": 261, "state": 2, "voltage": 52.009998321533203, "id": "com.victronenergy.vebus.ttyO5", "name": "MultiPlus-II 48/5000/70-50"}]}
        system/0/Buzzer/State	                        {"value": 0}
        system/0/Connected	                            {"value": 1}
        system/0/Control/BatteryCurrentSense	        {"value": 0}
        system/0/Control/BatteryVoltageSense	        {"value": 0}
        system/0/Control/BmsParameters	                {"value": 0}
        system/0/Control/Dvcc	                        {"value": 0}
        system/0/Control/ExtraBatteryCurrent	        {"value": 1}
        system/0/Control/MaxChargeCurrent	            {"value": 0}
        system/0/Control/ScheduledCharge	            {"value": 0}
        system/0/Control/SolarChargeCurrent	            {"value": 0}
        system/0/Control/SolarChargerTemperatureSense	{"value": 0}
        system/0/Control/SolarChargerVoltageSense	    {"value": 1}
        system/0/Control/SolarChargeVoltage	            {"value": 0}
        system/0/Control/VebusSoc	                    {"value": 0}
        system/0/Dc/Battery/ConsumedAmphours
        system/0/Dc/Battery/Current-	                {"value": -8.0}
        system/0/Dc/Battery/Power-	                    {"value": -416.07998657226562}
        system/0/Dc/Battery/Soc-	                    {"value": 97.5}
        system/0/Dc/Battery/State-	                    {"value": 2}
        system/0/Dc/Battery/TimeToGo
        system/0/Dc/Battery/Temperature-	            {"value": 16.0}
        system/0/Dc/Battery/TemperatureService	        {"value": "com.victronenergy.vebus.ttyO5"}
        system/0/Dc/Battery/Voltage-	                {"value": 52.009998321533203}
        system/0/Dc/Battery/VoltageService	            {"value": "com.victronenergy.vebus.ttyO5"}
        system/0/Dc/Vebus/Current 	                    {"value": -8.0}
        system/0/Dc/Vebus/Power 	                    {"value": -382}
        system/0/Debug/BatteryOperationalLimits/CurrentOffset	     {"value": 0}
        system/0/Debug/BatteryOperationalLimits/SolarVoltageOffset	 {"value": 0}
        system/0/Debug/BatteryOperationalLimits/VebusVoltageOffset	 {"value": 0}
        system/0/DeviceInstance	                        {"value": 0}
        system/0/Dvcc/Alarms/FirmwareInsufficient	    {"value": 0}
        system/0/Dvcc/Alarms/MultipleBatteries	        {"value": 0}
        system/0/Hub	                                {"value": 4}
        system/0/Mgmt/Connection	                    {"value": "data from other dbus processes"}
        system/0/Mgmt/ProcessName	                    {"value": "/opt/victronenergy/dbus-systemcalc-py/dbus_systemcalc.py"}
        system/0/Mgmt/ProcessVersion	                {"value": "2.28"}
        system/0/PvInvertersProductIds	                {"value": [41283, 41284]}
        PvInvertersAcEnergyForwardTotal
        PvInvertersAcEnergyForwardDay
        PvInvertersAcEnergyForwardMonth                 war mal PvInvertersAcEnergyForwardPerMonth
        PvInvertersAcEnergyForwardYear                  war mal PvInvertersAcEnergyForwardPerYear
        PvInvertersAcEnergyForwardDaySoFar              war mal PvInvertersAcEnergyForwardPerDay
        PvInvertersAcEnergyForwardMonthSoFar
        PvInvertersAcEnergyForwardYearSoFar
        system/0/Relay/0/State	                        {"value": 0}
        system/0/Relay/1/State	                        {"value": 0}
        system/0/Serial	                                {"value": "0479b7f1e15c"}
        system/0/ServiceMapping/com_victronenergy_battery_258	{"value": "com.victronenergy.battery.ttyO2"}
        system/0/ServiceMapping/com_victronenergy_grid_30	    {"value": "com.victronenergy.grid.cgwacs_ttyUSB0_di30_mb1"}
        system/0/ServiceMapping/com_victronenergy_hub4_0	    {"value": "com.victronenergy.hub4"}
        system/0/ServiceMapping/com_victronenergy_pvinverter_20	{"value": "com.victronenergy.pvinverter.pv_1992054488"}
        system/0/ServiceMapping/com_victronenergy_pvinverter_24	{"value": "com.victronenergy.pvinverter.pv_90505MES0000"}
        system/0/ServiceMapping/com_victronenergy_settings_0	{"value": "com.victronenergy.settings"}
        system/0/ServiceMapping/com_victronenergy_vebus_261	    {"value": "com.victronenergy.vebus.ttyO5"}
        system/0/ServiceMapping/com_victronenergy_vecan_0	    {"value": "com.victronenergy.vecan.can1"}
        system/0/SystemState/State ->   0: Off
                                   ->   1: Low power
                                   ->   2: VE.Bus Fault condition
                                   ->   3: Bulk charging
                                   ->   4: Absorption charging
                                   ->   5: Float charging
                                   ->   6: Storage mode
                                   ->   7: Equalisation charging
                                   ->   8: Passthru
                                   ->   9: Inverting
                                   ->  10: Assisting
                                   -> 256: Discharging
                                   -> 257: Sustain
        system/0/SystemState/BatteryLife	            {"value": 0}
        system/0/SystemState/ChargeDisabled	            {"value": 0}
        system/0/SystemState/DischargeDisabled	        {"value": 0}
        system/0/SystemState/LowSoc	                    {"value": 0}
        system/0/SystemState/SlowCharge	                {"value": 0}
        system/0/SystemState/State	                    {"value": 256}
        system/0/SystemState/UserChargeLimited	        {"value": 0}
        system/0/SystemState/UserDischargeLimited	    {"value": 0}
        system/0/SystemType	                            {"value": "ESS"}
        system/0/Timers/TimeOff	                        {"value": 24}
        system/0/Timers/TimeOnGenerator	                {"value": 0}
        system/0/Timers/TimeOnGrid	                    {"value": 278578}
        system/0/Timers/TimeOnInverter	                {"value": 0}
        system/0/VebusService	                        {"value": "com.victronenergy.vebus.ttyO5"}
    """
    Inst1 = '0'

    Label1 = 'Gateway'
    RegEx = 'system'
    Topics = ['Ac/ConsumptionOnInput/L1/Power', 'Ac/ConsumptionOnInput/L2/Power', 'Ac/ConsumptionOnInput/L3/Power',
                'Ac/Grid/L1/Power', 'Ac/Grid/L2/Power', 'Ac/Grid/L3/Power', 'Ac/PvOnGrid/L1/Power',
                'Ac/PvOnGrid/L2/Power', 'Ac/PvOnGrid/L3/Power', 'Dc/Battery/Current',
                'Dc/Battery/Power', 'Dc/Battery/Soc', 'Dc/Battery/State', 'Dc/Battery/Temperature', 'Dc/Battery/Voltage' ]

# #################################################################################################
# # Topics für den VeBus
# #################################################################################################
class VeBus():
    """ vebus/261/Ac/ActiveIn/ActiveInput	            {"value": 0}
        vebus/261/Ac/ActiveIn/Connected	                {"value": 1}
        vebus/261/Ac/ActiveIn/CurrentLimit-	            {"value": 22.0}
        vebus/261/Ac/ActiveIn/CurrentLimitIsAdjustable	{"value": 1}
        vebus/261/Ac/ActiveIn/L1/F	                    {"value": 50.102565765380859}
        vebus/261/Ac/ActiveIn/L1/I-	                    {"value": -1.8700000047683716}
        vebus/261/Ac/ActiveIn/L1/P-	                    {"value": -402}
        vebus/261/Ac/ActiveIn/L1/S-	                    {"value": 174}
        vebus/261/Ac/ActiveIn/L1/V-	                    {"value": 230.88999938964844}
        vebus/261/Ac/ActiveIn/P	                        {"value": -402}
        vebus/261/Ac/ActiveIn/S	                        {"value": 174}      GesamtEnergy
        vebus/261/Ac/In/1/CurrentLimit	                {"value": 22.0}
        vebus/261/Ac/In/1/CurrentLimitIsAdjustable	    {"value": 1}
        vebus/261/Ac/NumberOfAcInputs	                {"value": 1}
        vebus/261/Ac/NumberOfPhases	                    {"value": 1}
        vebus/261/Ac/Out/L1/F	                        {"value": 49.948848724365234}
        vebus/261/Ac/Out/L1/I	                        {"value": -0.18999999761581421}
        vebus/261/Ac/Out/L1/P	                        {"value": -24}
        vebus/261/Ac/Out/L1/S	                        {"value": 109}
        vebus/261/Ac/Out/L1/V	                        {"value": 230.88999938964844}
        vebus/261/Ac/Out/P	                            {"value": -24}
        vebus/261/Ac/Out/S	                            {"value": 109}
        vebus/261/Ac/PowerMeasurementType	            {"value": 4}
        For all alarms: 0=OK; 1=Warning; 2=Alarm
        vebus/261/Alarms/HighTemperature-	            {"value": 0}
        vebus/261/Alarms/L1/HighTemperature	            {"value": 0}
        vebus/261/Alarms/L1/LowBattery	                {"value": 0}
        vebus/261/Alarms/L1/Overload	                {"value": 0}
        vebus/261/Alarms/L1/Ripple	                    {"value": 0}
        vebus/261/Alarms/L2/HighTemperature	            {"value": 0}
        vebus/261/Alarms/L2/LowBattery	                {"value": 0}
        vebus/261/Alarms/L2/Overload	                {"value": 0}
        vebus/261/Alarms/L2/Ripple	                    {"value": 0}
        vebus/261/Alarms/L3/HighTemperature	            {"value": 0}
        vebus/261/Alarms/L3/LowBattery	                {"value": 0}
        vebus/261/Alarms/L3/Overload	                {"value": 0}
        vebus/261/Alarms/L3/Ripple	                    {"value": 0}
        vebus/261/Alarms/LowBattery-	                {"value": 0}
        vebus/261/Alarms/Overload-	                    {"value": 0}
        vebus/261/Alarms/PhaseRotation-	                {"value": 0}
        vebus/261/Alarms/Ripple-	                    {"value": 0}
        vebus/261/Alarms/TemperatureSensor-	            {"value": 0}
        vebus/261/Alarms/VoltageSensor-	                {"value": 0}
        vebus/261/Bms/AllowToCharge	                    {"value": 1}
        vebus/261/Bms/AllowToChargeRate	                {"value": 0}
        vebus/261/Bms/AllowToDischarge	                {"value": 1}
        vebus/261/Bms/BmsExpected	                    {"value": 0}
        vebus/261/Bms/BmsType	                        {"value": 0}
        vebus/261/Bms/Error	                            {"value": 0}
        vebus/261/Connected	                            {"value": 1}
        vebus/261/Dc/0/Current-	                        {"value": -8.3000001907348633}
        vebus/261/Dc/0/MaxChargeCurrent-	            {"value": 70.0}
        vebus/261/Dc/0/Power-	                        {"value": -381}
        vebus/261/Dc/0/Temperature-	                    {"value": 16.0}
        vebus/261/Dc/0/Voltage-	                        {"value": 52.009998321533203}
        vebus/261/DeviceInstance	                    {"value": 261}
        vebus/261/Devices/0/Assistants	                {"value": [119, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}
        vebus/261/Devices/0/ExtendStatus/GridRelayReport/Reset	{"value": 0}
        vebus/261/Devices/0/ExtendStatus/MainsPllLocked	        {"value": 1}
        vebus/261/Devices/0/ExtendStatus/SocTooLowToInvert	    {"value": 0}
        vebus/261/Devices/0/ExtendStatus/SustainMode	        {"value": 0}
        vebus/261/Devices/0/ExtendStatus/SwitchoverInfo/Connecting	{"value": 0}
        vebus/261/Devices/0/ExtendStatus/SwitchoverInfo/Delay	    {"value": 0}
        vebus/261/Devices/0/ExtendStatus/SwitchoverInfo/ErrorFlags	{"value": 0}
        vebus/261/Devices/0/ExtendStatus/TemperatureHighForceBypass	{"value": 0}
        vebus/261/Devices/0/ExtendStatus/VeBusNetworkQualityCounter	{"value": 0}
        vebus/261/Devices/0/ExtendStatus/WaitingForRelayTest	    {"value": 0}
        vebus/261/Devices/0/Version	                        {"value": 2623473}
        vebus/261/Devices/NumberOfMultis	                {"value": 1}
        vebus/261/Energy/AcIn1ToAcOut	                    {"value": 0.74638217687606812}
        vebus/261/Energy/AcIn1ToInverter-	                {"value": 21.645084381103516}
        vebus/261/Energy/AcIn2ToAcOut	                    {"value": 0.0}
        vebus/261/Energy/AcIn2ToInverter	                {"value": 0.0}
        vebus/261/Energy/AcOutToAcIn1	                    {"value": 0.4733155369758606}
        vebus/261/Energy/AcOutToAcIn2	                    {"value": 0.0}
        vebus/261/Energy/InverterToAcIn1-	                {"value": 15.073280334472656}
        vebus/261/Energy/InverterToAcIn2	                {"value": 0.0}
        vebus/261/Energy/InverterToAcOut	                {"value": 0.14563556015491486}
        vebus/261/Energy/OutToInverter	                    {"value": 0.036408890038728714}
        vebus/261/ExtraBatteryCurrent	                    {"value": 0.0}
        vebus/261/FirmwareFeatures/BolFrame	                {"value": 1}
        vebus/261/FirmwareFeatures/BolUBatAndTBatSense	    {"value": 1}
        vebus/261/FirmwareFeatures/CommandWriteViaId	    {"value": 1}
        vebus/261/FirmwareFeatures/IBatSOCBroadcast	        {"value": 1}
        vebus/261/FirmwareFeatures/NewPanelFrame	        {"value": 1}
        vebus/261/FirmwareFeatures/SetChargeState	        {"value": 1}
        vebus/261/FirmwareSubVersion	                    {"value": 0}
        vebus/261/FirmwareVersion	                        {"value": 1139}
        vebus/261/Hub/ChargeVoltage-                        {"value": 54.819999694824219}
        vebus/261/Hub4/AssistantId	                        {"value": 5}
        vebus/261/Hub4/DisableCharge	                    {"value": 0}
        vebus/261/Hub4/DisableFeedIn	                    {"value": 0}
        vebus/261/Hub4/DoNotFeedInOvervoltage	            {"value": 1}
        vebus/261/Hub4/FixSolarOffsetTo100mV	            {"value": 0}
        vebus/261/Hub4/L1/AcPowerSetpoint	                {"value": -406}
        vebus/261/Hub4/L1/CurrentLimitedDueToHighTemp	    {"value": 0}
        vebus/261/Hub4/L1/OffsetAddedToVoltageSetpoint	    {"value": 0}
        vebus/261/Hub4/Sustain	                            {"value": 0}
        vebus/261/Hub4/TargetPowerIsMaxFeedIn	            {"value": 0}
        vebus/261/Interfaces/Mk2/ProductId	                {"value": 4464}
        vebus/261/Interfaces/Mk2/ProductName	            {"value": "MK3"}
        vebus/261/Interfaces/Mk2/Status/BusFreeMode	        {"value": 1}
        vebus/261/Interfaces/Mk2/Version	                {"value": 1170207}
        LEDs: 0 = Off, 1 = On, 2 = Blinking, 3 = Blinking inverted
        vebus/261/Leds/Absorption-	                        {"value": 0}
        vebus/261/Leds/Bulk-	                            {"value": 0}
        vebus/261/Leds/Float-	                            {"value": 1}
        vebus/261/Leds/Inverter-	                        {"value": 1}
        vebus/261/Leds/LowBattery-	                        {"value": 0}
        vebus/261/Leds/Mains-	                            {"value": 2}
        vebus/261/Leds/Overload-	                        {"value": 0}
        vebus/261/Leds/Temperature-	                        {"value": 0}
        vebus/261/Mgmt/Connection	                        {"value": "VE.Bus"}
        vebus/261/Mgmt/ProcessName	                        {"value": "mk2-dbus"}
        vebus/261/Mgmt/ProcessVersion	                    {"value": "2.99"}
        vebus/261/Mode	                                    {"value": 3}
        vebus/261/ModeIsAdjustable	                        {"value": 1}
        vebus/261/ProductId	                                {"value": 9763}
        vebus/261/ProductName	                            {"value": "MultiPlus-II 48/5000/70-50"}
        vebus/261/PvInverter/Disable	                    {"value": 0}
        vebus/261/Quirks	                                {"value": 0}
        vebus/261/RedetectSystem	                        {"value": 0}
        vebus/261/ShortIds	                                {"value": 1}
        vebus/261/Soc-	                                    {"value": 97.5}
        vebus/261/State	                                    {"value": 5}
        vebus/261/VebusChargeState	                        {"value": 3}
        vebus/261/VebusError	                            {"value": 0}
        vebus/261/VebusMainState	                        {"value": 9}
        vebus/261/VebusSetChargeState	                    {"value": 0}
    """

    Inst1 = '261'
    Label1 = 'MultiPlus-II'
    RegEx = 'vebus'
    Topics = ['Ac/ActiveIn/CurrentLimit', 'Ac/ActiveIn/L1/I', 'Ac/ActiveIn/L1/P', 'Ac/ActiveIn/L1/S', 'Ac/ActiveIn/L1/V',
                    'Alarms/HighTemperature', 'Alarms/LowBattery', 'Alarms/Overload', 'Alarms/PhaseRotation', 'Alarms/Ripple', 'Alarms/TemperatureSensor', 'Alarms/VoltageSensor',
                    'Dc/0/Current', 'Dc/0/MaxChargeCurrent', 'Dc/0/Power', 'Dc/0/Temperature', 'Dc/0/Voltage', 'Energy/AcIn1ToInverter', 'Energy/InverterToAcIn1',
                    'Leds/Absorption', 'Leds/Bulk', 'Leds/Float', 'Leds/Inverter', 'Leds/LowBattery', 'Leds/Mains', 'Leds/Overload', 'Leds/Temperature' ,'Soc']

# #################################################################################################
# # Topics für alles andere
# #################################################################################################
#class Additional():
    ##fronius/0/AutoDetect
    ##fronius/0/ScanProgress
    ##logger/0/Buffer/Count
    ##logger/0/Buffer/ErrorState
    ##logger/0/Buffer/FreeDiskSpace
    ##logger/0/Buffer/Location
    ##logger/0/Storage/MountState
    ##logger/0/Vrm/ConnectionError
    ##logger/0/Vrm/TimeLastContact
    ##vecan/0/Alarms/SameUniqueNameUsed
    ##vecan/0/Link/VoltageSense

# #################################################################################################
# # Topics für die Settings
# #################################################################################################
#class Settings():
    ##settings/0/Settings/Alarm/Audible
    ##settings/0/Settings/Alarm/System/GridLost
    ##settings/0/Settings/Alarm/Vebus/HighDcRipple
    ##settings/0/Settings/Alarm/Vebus/HighTemperature
    ##settings/0/Settings/Alarm/Vebus/InverterOverload
    ##settings/0/Settings/Alarm/Vebus/LowBattery
    ##settings/0/Settings/Alarm/Vebus/TemperatureSenseError
    ##settings/0/Settings/Alarm/Vebus/VeBusError
    ##settings/0/Settings/Alarm/Vebus/VoltageSenseError
    ##settings/0/Settings/AnalogInput/Resistive/1/Function
    ##settings/0/Settings/AnalogInput/Resistive/2/Function
    ##settings/0/Settings/AnalogInput/Resistive/3/Function
    ##settings/0/Settings/AnalogInput/Temperature/1/Function
    ##settings/0/Settings/AnalogInput/Temperature/2/Function
    ##settings/0/Settings/Canbus/can0/Profile
    ##settings/0/Settings/Canbus/can1/Profile
    ##settings/0/Settings/CGwacs/AcPowerSetPoint
    ##settings/0/Settings/CGwacs/BatteryLife/DischargedTime
    ##settings/0/Settings/CGwacs/BatteryLife/Flags
    ##settings/0/Settings/CGwacs/BatteryLife/MinimumSocLimit
    ##settings/0/Settings/CGwacs/BatteryLife/Schedule/Charge/0/Day
    ##settings/0/Settings/CGwacs/BatteryLife/Schedule/Charge/0/Duration
    ##settings/0/Settings/CGwacs/BatteryLife/Schedule/Charge/0/Soc
    ##settings/0/Settings/CGwacs/BatteryLife/Schedule/Charge/0/Start
    ##settings/0/Settings/CGwacs/BatteryLife/Schedule/Charge/1/Day
    ##settings/0/Settings/CGwacs/BatteryLife/Schedule/Charge/1/Duration
    ##settings/0/Settings/CGwacs/BatteryLife/Schedule/Charge/1/Soc
    ##settings/0/Settings/CGwacs/BatteryLife/Schedule/Charge/1/Start
    ##settings/0/Settings/CGwacs/BatteryLife/Schedule/Charge/2/Day
    ##settings/0/Settings/CGwacs/BatteryLife/Schedule/Charge/2/Duration
    ##settings/0/Settings/CGwacs/BatteryLife/Schedule/Charge/2/Soc
    ##settings/0/Settings/CGwacs/BatteryLife/Schedule/Charge/2/Start
    ##settings/0/Settings/CGwacs/BatteryLife/Schedule/Charge/3/Day
    ##settings/0/Settings/CGwacs/BatteryLife/Schedule/Charge/3/Duration
    ##settings/0/Settings/CGwacs/BatteryLife/Schedule/Charge/3/Soc
    ##settings/0/Settings/CGwacs/BatteryLife/Schedule/Charge/3/Start
    ##settings/0/Settings/CGwacs/BatteryLife/Schedule/Charge/4/Day
    ##settings/0/Settings/CGwacs/BatteryLife/Schedule/Charge/4/Duration
    ##settings/0/Settings/CGwacs/BatteryLife/Schedule/Charge/4/Soc
    ##settings/0/Settings/CGwacs/BatteryLife/Schedule/Charge/4/Start
    ##settings/0/Settings/CGwacs/BatteryLife/SocLimit
    ##settings/0/Settings/CGwacs/BatteryLife/State
    ##settings/0/Settings/CGwacs/DeviceIds
    ##settings/0/Settings/CGwacs/Devices/D308053T/CustomName
    ##settings/0/Settings/CGwacs/Devices/D308053T/DeviceInstance
    ##settings/0/Settings/CGwacs/Devices/D308053T/DeviceType
    ##settings/0/Settings/CGwacs/Devices/D308053T/IsMultiPhase
    ##settings/0/Settings/CGwacs/Devices/D308053T/L1ReverseEnergy
    ##settings/0/Settings/CGwacs/Devices/D308053T/L2/CustomName
    ##settings/0/Settings/CGwacs/Devices/D308053T/L2/DeviceInstance
    ##settings/0/Settings/CGwacs/Devices/D308053T/L2/Position
    ##settings/0/Settings/CGwacs/Devices/D308053T/L2/ServiceType
    ##settings/0/Settings/CGwacs/Devices/D308053T/L2ReverseEnergy
    ##settings/0/Settings/CGwacs/Devices/D308053T/L3ReverseEnergy
    ##settings/0/Settings/CGwacs/Devices/D308053T/Position
    ##settings/0/Settings/CGwacs/Devices/D308053T/ServiceType
    ##settings/0/Settings/CGwacs/Hub4Mode
    ##settings/0/Settings/CGwacs/MaxChargePercentage
    ##settings/0/Settings/CGwacs/MaxChargePower
    ##settings/0/Settings/CGwacs/MaxDischargePercentage
    ##settings/0/Settings/CGwacs/MaxDischargePower
    ##settings/0/Settings/CGwacs/OvervoltageFeedIn
    ##settings/0/Settings/CGwacs/PreventFeedback
    ##settings/0/Settings/CGwacs/RunWithoutGridMeter
    ##settings/0/Settings/DigitalInput/1/AlarmSetting
    ##settings/0/Settings/DigitalInput/1/Count
    ##settings/0/Settings/DigitalInput/1/CustomName
    ##settings/0/Settings/DigitalInput/1/InvertAlarm
    ##settings/0/Settings/DigitalInput/1/InvertTranslation
    ##settings/0/Settings/DigitalInput/1/Multiplier
    ##settings/0/Settings/DigitalInput/1/Type
    ##settings/0/Settings/DigitalInput/2/AlarmSetting
    ##settings/0/Settings/DigitalInput/2/Count
    ##settings/0/Settings/DigitalInput/2/CustomName
    ##settings/0/Settings/DigitalInput/2/InvertAlarm
    ##settings/0/Settings/DigitalInput/2/InvertTranslation
    ##settings/0/Settings/DigitalInput/2/Multiplier
    ##settings/0/Settings/DigitalInput/2/Type
    ##settings/0/Settings/DigitalInput/3/AlarmSetting
    ##settings/0/Settings/DigitalInput/3/Count
    ##settings/0/Settings/DigitalInput/3/CustomName
    ##settings/0/Settings/DigitalInput/3/InvertAlarm
    ##settings/0/Settings/DigitalInput/3/InvertTranslation
    ##settings/0/Settings/DigitalInput/3/Multiplier
    ##settings/0/Settings/DigitalInput/3/Type
    ##settings/0/Settings/DigitalInput/4/AlarmSetting
    ##settings/0/Settings/DigitalInput/4/Count
    ##settings/0/Settings/DigitalInput/4/CustomName
    ##settings/0/Settings/DigitalInput/4/InvertAlarm
    ##settings/0/Settings/DigitalInput/4/InvertTranslation
    ##settings/0/Settings/DigitalInput/4/Multiplier
    ##settings/0/Settings/DigitalInput/4/Type
    ##settings/0/Settings/DigitalInput/5/AlarmSetting
    ##settings/0/Settings/DigitalInput/5/Count
    ##settings/0/Settings/DigitalInput/5/CustomName
    ##settings/0/Settings/DigitalInput/5/InvertAlarm
    ##settings/0/Settings/DigitalInput/5/InvertTranslation
    ##settings/0/Settings/DigitalInput/5/Multiplier
    ##settings/0/Settings/DigitalInput/5/Type
    ##settings/0/Settings/Fronius/AutoScan
    ##settings/0/Settings/Fronius/InverterIds
    ##settings/0/Settings/Fronius/Inverters/I1992054488/CustomName
    ##settings/0/Settings/Fronius/Inverters/I1992054488/IsActive
    ##settings/0/Settings/Fronius/Inverters/I1992054488/L1Energy
    ##settings/0/Settings/Fronius/Inverters/I1992054488/L2Energy
    ##settings/0/Settings/Fronius/Inverters/I1992054488/L3Energy
    ##settings/0/Settings/Fronius/Inverters/I1992054488/Phase
    ##settings/0/Settings/Fronius/Inverters/I1992054488/PhaseCount
    ##settings/0/Settings/Fronius/Inverters/I1992054488/Position
    ##settings/0/Settings/Fronius/Inverters/I90505MES0000/CustomName
    ##settings/0/Settings/Fronius/Inverters/I90505MES0000/IsActive
    ##settings/0/Settings/Fronius/Inverters/I90505MES0000/L1Energy
    ##settings/0/Settings/Fronius/Inverters/I90505MES0000/L2Energy
    ##settings/0/Settings/Fronius/Inverters/I90505MES0000/L3Energy
    ##settings/0/Settings/Fronius/Inverters/I90505MES0000/Phase
    ##settings/0/Settings/Fronius/Inverters/I90505MES0000/PhaseCount
    ##settings/0/Settings/Fronius/Inverters/I90505MES0000/Position
    ##settings/0/Settings/Fronius/IPAddresses
    ##settings/0/Settings/Fronius/KnownIPAddresses
    ##settings/0/Settings/Fronius/PortNumber
    ##settings/0/Settings/Gps/Format
    ##settings/0/Settings/Gps/SpeedUnit
    ##settings/0/Settings/Gui/AutoBrightness
    ##settings/0/Settings/Gui/Brightness
    ##settings/0/Settings/Gui/DefaultOverview
    ##settings/0/Settings/Gui/DemoMode
    ##settings/0/Settings/Gui/DisplayOff
    ##settings/0/Settings/Gui/Language
    ##settings/0/Settings/Gui/MobileOverview
    ##settings/0/Settings/Gui/StartWithMenuView
    ##settings/0/Settings/Relay/0/InitialState
    ##settings/0/Settings/Relay/1/InitialState
    ##settings/0/Settings/Relay/Function
    ##settings/0/Settings/Relay/Polarity
    ##settings/0/Settings/Sensors/OnPosition/ACIn1_L1
    ##settings/0/Settings/Sensors/OnPosition/ACIn1_L2
    ##settings/0/Settings/Sensors/OnPosition/ACIn1_L3
    ##settings/0/Settings/Sensors/OnPosition/ACIn2_L1
    ##settings/0/Settings/Sensors/OnPosition/ACIn2_L2
    ##settings/0/Settings/Sensors/OnPosition/ACIn2_L3
    ##settings/0/Settings/Sensors/OnPosition/ACOut_L1
    ##settings/0/Settings/Sensors/OnPosition/ACOut_L2
    ##settings/0/Settings/Sensors/OnPosition/ACOut_L3
    ##settings/0/Settings/Services/AccessPoint
    ##settings/0/Settings/Services/Bluetooth
    ##settings/0/Settings/Services/Bol
    ##settings/0/Settings/Services/Console
    ##settings/0/Settings/Services/FischerPandaAutoStartStop
    ##settings/0/Settings/Services/Modbus
    ##settings/0/Settings/Services/MqttLocal
    ##settings/0/Settings/Services/MqttLocalInsecure
    ##settings/0/Settings/Services/MqttN2k
    ##settings/0/Settings/Services/MqttVrm
    ##settings/0/Settings/Services/Socketcand
    ##settings/0/Settings/System/AccessLevel
    ##settings/0/Settings/System/ActiveNetworkConnection
    ##settings/0/Settings/System/AutoUpdate
    ##settings/0/Settings/System/LogLevel
    ##settings/0/Settings/System/ReleaseType
    ##settings/0/Settings/System/RemoteSupport
    ##settings/0/Settings/System/RemoteSupportPort
    ##settings/0/Settings/System/RemoteVncPort
    ##settings/0/Settings/System/SSHLocal
    ##settings/0/Settings/System/TimeZone
    ##settings/0/Settings/System/VncInternet
    ##settings/0/Settings/System/VncLocal
    ##settings/0/Settings/System/VolumeUnit
    ##settings/0/Settings/SystemSetup/AcInput1
    ##settings/0/Settings/SystemSetup/AcInput2
    ##settings/0/Settings/SystemSetup/Batteries/Configuration/com_victronenergy_battery/258/1/Enabled
    ##settings/0/Settings/SystemSetup/Batteries/Configuration/com_victronenergy_battery/258/1/Name
    ##settings/0/Settings/SystemSetup/Batteries/Configuration/com_victronenergy_battery/258/1/Service
    ##settings/0/Settings/SystemSetup/Batteries/Configuration/com_victronenergy_battery/258/Enabled
    ##settings/0/Settings/SystemSetup/Batteries/Configuration/com_victronenergy_battery/258/Name
    ##settings/0/Settings/SystemSetup/Batteries/Configuration/com_victronenergy_battery/258/Service
    ##settings/0/Settings/SystemSetup/Batteries/Configuration/com_victronenergy_vebus/261/Enabled
    ##settings/0/Settings/SystemSetup/Batteries/Configuration/com_victronenergy_vebus/261/Name
    ##settings/0/Settings/SystemSetup/Batteries/Configuration/com_victronenergy_vebus/261/Service
    ##settings/0/Settings/SystemSetup/BatteryCurrentSense
    ##settings/0/Settings/SystemSetup/BatteryService
    ##settings/0/Settings/SystemSetup/HasAcOutSystem
    ##settings/0/Settings/SystemSetup/HasDcSystem
    ##settings/0/Settings/SystemSetup/MaxChargeCurrent
    ##settings/0/Settings/SystemSetup/SharedTemperatureSense
    ##settings/0/Settings/SystemSetup/SharedVoltageSense
    ##settings/0/Settings/SystemSetup/SystemName
    ##settings/0/Settings/SystemSetup/TemperatureService
    ##settings/0/Settings/Tank/1/Capacity
    ##settings/0/Settings/Tank/1/FluidType
    ##settings/0/Settings/Tank/1/Standard
    ##settings/0/Settings/Tank/2/Capacity
    ##settings/0/Settings/Tank/2/FluidType
    ##settings/0/Settings/Tank/2/Standard
    ##settings/0/Settings/Tank/3/Capacity
    ##settings/0/Settings/Tank/3/FluidType
    ##settings/0/Settings/Tank/3/Standard
    ##settings/0/Settings/Temperature/1/Offset
    ##settings/0/Settings/Temperature/1/Scale
    ##settings/0/Settings/Temperature/1/TemperatureType
    ##settings/0/Settings/Temperature/2/Offset
    ##settings/0/Settings/Temperature/2/Scale
    ##settings/0/Settings/Temperature/2/TemperatureType
    ##settings/0/Settings/Vecan/can1/FreeIdentityNumber
    ##settings/0/Settings/Vecan/can1/MainInterface/IdentityNumber
    ##settings/0/Settings/Vecan/can1/MainInterface/Instance
    ##settings/0/Settings/Vecan/can1/MainInterface/Nad
    ##settings/0/Settings/Vecan/can1/MainInterface/SystemInstance
    ##settings/0/Settings/Vecan/can1/N2kGatewayEnabled
    ##settings/0/Settings/Vecan/can1/VenusUniqueId
    ##settings/0/Settings/Victron/Products/HQ184666JII/CustomName
    ##settings/0/Settings/Vrmlogger/ExternalStorageDir
    ##settings/0/Settings/Vrmlogger/Http/Proxy
    ##settings/0/Settings/Vrmlogger/Http/ProxyPort
    ##settings/0/Settings/Vrmlogger/HttpsEnabled
    ##settings/0/Settings/Vrmlogger/LogInterval
    ##settings/0/Settings/Vrmlogger/Logmode
    ##settings/0/Settings/Vrmlogger/RamDiskMode
    ##settings/0/Settings/Vrmlogger/Url
    ##settings/0/Settings/Watchdog/VrmTimeout

    #Topics = []

# # DateiEnde #####################################################################################