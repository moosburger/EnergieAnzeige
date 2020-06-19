#!/usr/bin/env python
# -*- coding: utf-8 -*-

# #################################################################################################
## \brief     Piko Inverter communication software
#  \details
#  \file      configuration.py
#
#  \date      Erstellt am: 13.03.2020
#  \author    moosburger
#
# <History\> ######################################################################################
# Version     Datum       Ticket#     Beschreibung
# 1.0         13:03.2020
#
# #################################################################################################

# #################################################################################################
# # Python Imports (Standard Library)
# #################################################################################################
import logging

# #################################################################################################
# # Python Imports (site-packages)
# #################################################################################################

# #################################################################################################
# # private Imports
# #################################################################################################

# #################################################################################################
# # UmgebungsVariablen
# #################################################################################################
# GLOBAL
DEBUG = True

# PIKO DETAILS
PIKO_IP = "192.168.100.100"
PIKO_NAME ="HOSTNAME"

# FAKED PIKO SERVER MODBUS DETAILS
INVERTER_IP = "192.168.100.101"
#INVERTER_IP = "127.0.0.1"
MODBUS_PORT = 502
#MODBUS_TIMEOUT = 30 #seconds to wait before failure

#SCHEDULER
SCHED_INTERVAL = 10          #  seconds delay

# DATA
#EPOCH_INVERTER = False      # False = Use compueter time, True = get time off inverter (scheduler will still use compurter time)
#POW_THERESHOLD = 10         # Watt threshold
LOG_LEVEL = logging.ERROR    # Levels: NONE, FATAL, ERROR, NOTICE, DEBUG


