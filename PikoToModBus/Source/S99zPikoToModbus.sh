#!/bin/sh

###########################################################
# Beschreibungen
# Eigene Scripte sollten in /usr/local/etc/rc.d liegen. Da überleben sie auch ein update
# Datei mit chmod 755 sichtbar machen
# 
# /etc/rc0.d - rc6.d sind nur Links auf das Script in /etc/init.d RunLevel Einträge beim boot, dsm scheint da nur eines zu kennen
#
# Das zu startende Script (PikoToModBus.sh) liegt /etc/init.d
#
###########################################################
#
###########################################################
# einlesen des profile-files, damit globale Umgebungsvariablen funktionieren
# einlesen von rc.status, damit status des dienstes mit abgefragt werden kann
. /etc/profile
#. /etc/rc.status

###########################################################
# der rcstatus sollte vor der benutzung noch einmal gelöscht werden
#rc_reset

###########################################################
### BEGIN INIT INFO
# Provides: VrmGetData
# Required-Start:
# Required-Stop:
# Default-Start: 3 5
# Default-Stop:
# Description: Starts VrmGetData.py zum sammeln der VictronDaten
### END INIT INFO
###########################################################
# benötigte variablen können auch, wie hier, von hand gesetzt werden
PATH=$PATH:/mnt/dietpi_userdata/PikoToModBus:/etc/init.d:
HOME=/root

# Configured Variables:
PYTHON_EXEC="python"
SCRIPT_EXEC="/mnt/dietpi_userdata/PikoToModBus/PikoToModbus.py" 

###########################################################
# $1 beinhaltet den mit übergebenen Wert und anschliessende ausführung

case "$1" in
  start)
    echo "Starting $0" 
    ${PYTHON_EXEC} ${SCRIPT_EXEC} &
    ;;
  stop)
  echo "Stopping $0"
#    kill $(ps aux | grep “python ${SCRIPT_EXEC}” | awk ‘{print $2}’)
    ;;
  *)
    echo "Usage: $0 {start|stop}"
    exit 1
    ;;
esac

exit 0