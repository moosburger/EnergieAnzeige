/*<  > ********************************************************************************/
/*!
*	\brief      -
*	\details    -
*
*	\file		UsbCom.cpp
*
*	\copyright  (C) 2016 Gerhard Prexl, All rights reserved.
*	\author     Gerhard Prexl
*/
/*< History > *************************************************************************************
*	Version     Datum       Kuerzel      Ticket#     Beschreibung
*   0.1         05.08.2021  GP           -------     Ersterstellung
* </ History ></  > ******************************************************************/

/**
* \addtogroup Main
* UsbCom.cpp
*/
/**************************************************************************************************
* Includes
**************************************************************************************************/
#include "SerialPrint.h"
#include "main.h"
#include "oneWireFunction.h"

/**************************************************************************************************
* Defines
**************************************************************************************************/

/**************************************************************************************************
* Variablen
**************************************************************************************************/

/**************************************************************************************************
* Funktionen
**************************************************************************************************/

//*************************************************************************************************
// FunktionsName:   UsbCom
/// \details        Wenn über USB der Teensy abgefragt wird
/// \param[in]      -
/// \return         -
//*************************************************************************************************
void UsbDebugCom()
{
    if (!mDebugOn)
        return;
}
/************************ Ende UsbDebugCom Funktionen **********************************************************/

//*************************************************************************************************
// FunktionsName:   UsbCom
/// \details        Wenn über USB der Teensy abgefragt wird
/// \param[in]      -
/// \return         -
//*************************************************************************************************
void UsbCom()
{
    bool SerialAvail = Serial.available();
    if(!SerialAvail)
        return;

    IPAddress myLocal = Ethernet.localIP();
    // On a Teensy, large groups of bytes tend to arrive all at once.
    // This bytecount prevents taking too much time processing them.
    unsigned char bytecount = 0;
    int byteArr[MAXBYTE];
    for (int i = 0; i < MAXBYTE; i++)
        byteArr[i] = 0;

    while (Serial.available() && bytecount < MAXBYTE)
    {
        byteArr[bytecount] = Serial.read();
        bytecount++;
    }

    // Versionsabfrage 'V'
    if ((byteArr[0] == 86) && (byteArr[1] == 0) && (byteArr[2] == 0) && (byteArr[3] == 0) && (byteArr[4] == 0) && (byteArr[5] == 0))
        Serialprint("Version: %s\n", VERSION);

    // Ip Adresse 'Ip'
    else if ((byteArr[0] == 73) && (byteArr[1] == 112) && (byteArr[2] == 0) && (byteArr[3] == 0) && (byteArr[4] == 0) && (byteArr[5] == 0))
        Serialprint("MyIp: %d.%d.%d.%d\n", myLocal[0],myLocal[1],myLocal[2],myLocal[3]);

    // OneWire Adressen 'One'
    else if ((byteArr[0] == 79) && (byteArr[1] == 110) && (byteArr[2] == 101) && (byteArr[3] == 0) && (byteArr[4] == 0) && (byteArr[5] == 0))
        OneWireAddresses(mSensorAddress);

    //************************************ DebugAusgabe ein oder aus ****************************
    // Debug Ausgabe ein 'DbgOf'
    else if ((byteArr[0] == 68) && (byteArr[1] == 98) && (byteArr[2] == 103) && (byteArr[3] == 79) && (byteArr[4] == 102) && (byteArr[5] == 0))
    {
        mDebugOn = false;
        mDebug_Ethernet = false;
        mDebug_OneWire = false;
        mDebug_SoBus = false;
        mDebug_eBus0 = false;
        mDebug_eBus1 = false;
    }

    // Debug Ausgabe ein 'DbgOn'
    else if ((byteArr[0] == 68) && (byteArr[1] == 98) && (byteArr[2] == 103) && (byteArr[3] == 79) && (byteArr[4] == 110) && (byteArr[5] == 0))
        mDebugOn = true;

    // Debug Ausgabe ein 'DbgEt'-> Ethernet
    else if ((byteArr[0] == 68) && (byteArr[1] == 98) && (byteArr[2] == 103) && (byteArr[3] == 69) && (byteArr[4] == 116) && (byteArr[5] == 0))
        mDebug_Ethernet = true;

    // Debug Ausgabe ein 'DbgWi'-> OneWire
    else if ((byteArr[0] == 68) && (byteArr[1] == 98) && (byteArr[2] == 103) && (byteArr[3] == 87) && (byteArr[4] == 105) && (byteArr[5] == 0))
        mDebug_OneWire = true;

    // Debug Ausgabe ein 'DbgSo'-> So0 Bus
    else if ((byteArr[0] == 68) && (byteArr[1] == 98) && (byteArr[2] == 103) && (byteArr[3] == 83) && (byteArr[4] == 111) && (byteArr[5] == 0))
        mDebug_SoBus = true;

    // Debug Ausgabe ein 'DbgEB' -> eBus
    else if ((byteArr[0] == 68) && (byteArr[1] == 98) && (byteArr[2] == 103) && (byteArr[3] == 69) && (byteArr[4] == 66) && (byteArr[5] == 0))
        mDebug_eBus0 = true;


    else
        Serialprint("Unbekanntes Kommando %3d %3d %3d %3d %3d %3d\n", byteArr[0], byteArr[1], byteArr[2], byteArr[3], byteArr[4], byteArr[5]);
}
/************************ Ende UsbCom Funktionen **********************************************************/

/************************ Ende main.cpp **********************************************************/

