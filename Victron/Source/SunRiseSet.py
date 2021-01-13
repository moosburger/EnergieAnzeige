#!/usr/bin/env python
# -*- coding: utf-8 -*-

# #################################################################################################
## \brief	  Sonnenauf_untergang
#  \details
#  \file      SunRiseSet.py
#
#  \date
#  \author    moosburger
#  \Contrib
#
# <History\> ######################################################################################
# Version     Datum       Ticket#     Beschreibung
# 1.0         26.05.2020
#
# #################################################################################################

# #################################################################################################
# # Python Imports (Standard Library)
# #################################################################################################
try:
    import math
    import time

except:
    raise

# #################################################################################################
# # UmgebungsVariablen
# #################################################################################################
pi2 = 2*math.pi
pi = math.pi

RAD = math.pi/180

JD2000 = 2451545
h = -50.0/60.0*RAD
B = math.radians(48.470167)       # geographische Breite Moosburg a.d. Isar  -> https://www.laengengrad-breitengrad.de/
GeographischeLaenge = 11.935867   # geographische Laenge

# #################################################################################################
# # Funktionen
# # Prototypen
# # if __name__ == '__main__':
# #################################################################################################

# #################################################################################################
# #  Funktion: ' JulianischesDatum '
## \details        -
#   \param[in]     -
#   \param[in]     -
#   \return          -
# #################################################################################################
def JulianischesDatum (Jahr, Monat, Tag, Stunde, Minuten, Sekunden):
    if (Monat <= 2):
        Monat = Monat + 12
        Jahr = Jahr - 1
    Gregor = (Jahr/400) - (Jahr/100) + (Jahr/4)  # Gregorianischer Kalender
    return 2400000.5 + 365 * Jahr - 679004 + Gregor \
           + math.floor(30.6001*(Monat + 1)) + Tag + Stunde/24 \
           + Minuten/1440 + Sekunden/86400

# #################################################################################################
# #  Funktion: ' InPi '
## \details        -
#   \param[in]     -
#   \param[in]     -
#   \return          -
# #################################################################################################
def InPi(x):
    n = int(x/pi2)
    x = x - n*pi2
    if (x < 0):
        x += pi2
    return x

# #################################################################################################
# #  Funktion: ' eps '
## \details       Neigung der Erdachse
#   \param[in]     -
#   \param[in]     -
#   \return          -
# #################################################################################################
def eps(T):
    return RAD*(23.43929111 + (-46.8150*T - 0.00059*T**2 + 0.001813*T**3)/3600)

# #################################################################################################
# #  Funktion: ' BerechneZeitgleichung '
## \details        -
#   \param[in]     -
#   \param[in]     -
#   \return          -
# #################################################################################################
def BerechneZeitgleichung(T):
    RA_Mittel = 18.71506921 + 2400.0513369*T +(2.5862e-5 - 1.72e-9*T)*T**2
    M  = InPi(pi2*(0.993133 + 99.997361*T))
    L  = InPi(pi2*(0.7859453 + M/pi2 \
                   + (6893*math.sin(M) + 72*math.sin(2*M) + 6191.2*T) / 1296e3))
    e = eps(T)
    RA = math.atan(math.tan(L)*math.cos(e))
    if (RA < 0):
        RA += pi
    if (L > pi):
        RA += pi
    RA = 24*RA/pi2
    DK = math.asin(math.sin(e)*math.sin(L))
    #Damit 0 <= RA_Mittel < 24
    RA_Mittel = 24.0*InPi(pi2*RA_Mittel/24.0)/pi2
    dRA = RA_Mittel - RA
    if (dRA < -12.0):
        dRA += 24.0
    if (dRA > 12.0):
        dRA -= 24.0
    dRA = dRA* 1.0027379
    return dRA, DK

# #################################################################################################
# #  Funktion: ' Sonnenauf_untergang '
## \details        -
#   \param[in]     -
#   \param[in]     -
#   \return          -
# #################################################################################################
def Sonnenauf_untergang (JD, Zeitzone):
    # Zeitzone = 0 #Weltzeit
    # Zeitzone = 1 #Winterzeit
    # Zeitzone = 2 #Sommerzeit
    # JD = JulianischesDatum

    T = (JD - JD2000)/36525

    Zeitgleichung, DK = BerechneZeitgleichung(T)

    Minuten = Zeitgleichung*60

    Zeitdifferenz = 12*math.acos((math.sin(h) - math.sin(B)*math.sin(DK)) \
                             / (math.cos(B)*math.cos(DK)))/pi

    AufgangOrtszeit = 12 - Zeitdifferenz - Zeitgleichung
    UntergangOrtszeit = 12 + Zeitdifferenz - Zeitgleichung
    AufgangWeltzeit = AufgangOrtszeit - GeographischeLaenge/15
    UntergangWeltzeit = UntergangOrtszeit - GeographischeLaenge/15

    Aufgang = AufgangWeltzeit + Zeitzone
    if (Aufgang < 0):
        Aufgang += 24
    elif (Aufgang >= 24):
        Aufgang -= 24

    AM = round(Aufgang*60)/60 # minutengenau runden

    Untergang = UntergangWeltzeit + Zeitzone
    if (Untergang < 0):
        Untergang += 24
    elif (Untergang >= 24):
        Untergang -= 24

    UM = round(Untergang*60)/60 # minutengenau runden

    return AM, UM

# #################################################################################################
# #  Funktion: ' _Conf_Two_Register '
## \details        -
#   \param[in]     -
#   \param[in]     -
#   \return          -
# #################################################################################################
def get_Info ():

    lt = time.localtime() # Aktuelle, lokale Zeit als Tupel
    # Entpacken des Tupels
    lt_jahr, lt_monat, lt_tag = lt[0:3]        # Datum
    lt_h, lt_m, lt_s = lt[3:6]
    lt_dst = lt[8]                             # Sommerzeit


    #print("Heute ist der {0:02d}.{1:02d}.{2:4d}".format(lt_tag, lt_monat, lt_jahr))
    #if lt_dst == 1:
    #    print("Sommerzeit")
    #elif lt_dst == 0:
    #    print("Winterzeit")
    #else:
    #    print("Keine Sommerzeitinformation vorhanden")

    AM, UM = Sonnenauf_untergang (JulianischesDatum(lt_jahr, lt_monat, lt_tag, 12, 0, 0), lt_dst + 1)

    AMh = int(math.floor(AM))
    AMm = int((AM - AMh)*60)

    UMh = int(math.floor(UM))
    UMm = int((UM - UMh)*60)

    #print("Sonnenaufgang {0:02d}:{1:02d}\nSonnenuntergang {2:02d}:{3:02d}".format(AMh, AMm, UMh, UMm))

    sunInfo = (
                AMh, AMm, # Sonnenaufgang
                UMh, UMm, # Sonnenuntergang
                lt_tag, lt_monat, lt_jahr, # Heute
                lt_h, lt_m, lt_s # Zeit
               )

    return sunInfo