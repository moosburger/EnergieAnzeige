/*<  > ********************************************************************************/
/*!
*	\brief      -
*	\details    -
*
*	\file		mainFunction.cpp
*
*	\copyright  (C) 2016 Gerhard Prexl, All rights reserved.
*	\author     Gerhard Prexl
*/
/*< History > *************************************************************************************
*	Version     Datum       Kuerzel      Ticket#     Beschreibung
*   0.9.0.1     04.02.2023  GP           -------     Ersterstellung
* </ History ></  > ******************************************************************/

/**
* \addtogroup Main
* mainFunction.cpp
*/

/**************************************************************************************************
* Includes
**************************************************************************************************/
#include "main.h"
#include "SerialPrint.h"

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
// FunktionsName:   BrennerSperre
/// \details        Abhängig von den Temperaturen wird die BrennerSperre aktiviert
/// \return         -
//*************************************************************************************************
void BrennerSperre(eBusValues_st* eBusValues, PinFuerSperre_st* PinFuerSperre)
{
    /*Serial.print("Tsu: ");
    Serial.println(eBusValues->Tsu);
    Serial.print("Tfk: ");
    Serial.println(eBusValues->Tfk);
    Serial.print("Tso: ");
    Serial.println(eBusValues->Tso);
    Serial.print("Tko: ");
    Serial.println(eBusValues->Tko);
    Serial.print("Tpu: ");
    Serial.println(eBusValues->Tpu);
    Serialprint("PumpeSo: %u, PumpeFK: %u, bSperre: %u\n", PinFuerSperre->PumpeSo, PinFuerSperre->PumpeFK, PinFuerSperre->bSperre);*/
    //BrennerSperre, Ein wenn TSU > 41 und Pumpe läuft (Low Pegel am Eingang)
    if (((eBusValues->Tsu > SPEICHER_TEMP_MIN) and (PinFuerSperre->PumpeSo = true)) or ((eBusValues->Tfk > SPEICHER_TEMP_MIN) and (PinFuerSperre->PumpeFK = true)))
    {
        //Ein
        PinFuerSperre->bSperre = true;
        return;
    }
    if ((eBusValues->Tso < WARMWASSER_TEMP - 3) and ((PinFuerSperre->PumpeSo = true) or (PinFuerSperre->PumpeFK = true)))
    {
        //Nur Aus, wenn unter 51° und Pumpe nicht läuft (High Pegel am Eingang)
        PinFuerSperre->bSperre = false;
        return;
    }
    if (eBusValues->Tso < WARMWASSER_TEMP - 5)
    {
        //Immer aus wenn unter 49°
        PinFuerSperre->bSperre = false;
        return;
    }
}
/************************ Ende RisingEdge **********************************************************/

//*************************************************************************************************
// FunktionsName:   RisingEdge
/// \details        Erkennt steigende Flanke
/// \param[in]      * TstrBck
/// \param[in]      * Tstr
/// \return         retVal
//*************************************************************************************************
bool RisingEdge(bool* Tstr, bool* TstrBck)
{
    bool retval = false;

    if ((*Tstr == true) && (*TstrBck == false))
        retval = true;

    *TstrBck = *Tstr;
    return retval;
}
/************************ Ende RisingEdge **********************************************************/

//*************************************************************************************************
// FunktionsName:   InitEthernet
/// \details        Per DHCP die Ip holen, oder die Fehler rückmelden
/// \param[in]      * macAddr
/// \param[in]      * retStr
/// \return         retVal
//*************************************************************************************************
bool InitEthernet()
{
    // Unlike the Arduino API (which you can still use), QNEthernet uses
    // the Teensy's internal MAC address by default, so we can retrieve
    // it here
    uint8_t mac[6];
    Ethernet.macAddress(mac);  // This is informative; it retrieves, not sets
    mDebug_Ethernet ? Serialprint("MAC = %02x:%02x:%02x:%02x:%02x:%02x\n", mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]) : 0;

    // Add listeners
    // It's important to add these before doing anything with Ethernet
    // so no events are missed.

    // Listen for link changes
    Ethernet.onLinkState([](bool state) {
        mDebug_Ethernet ? Serialprint("[Ethernet] Link %s\n", state ? "ON" : "OFF") : 0;
    });

    // Listen for address changes
    Ethernet.onAddressChanged([]()
    {
        IPAddress ip = Ethernet.localIP();
        bool hasIP = (ip != INADDR_NONE);
        if (hasIP)
        {
            mDebug_Ethernet ? Serialprint("[Ethernet] Address changed:\n") : 0;

            mDebug_Ethernet ? Serialprint("    Local IP = %u.%u.%u.%u\n", ip[0], ip[1], ip[2], ip[3]) : 0;
            ip = Ethernet.subnetMask();
            mDebug_Ethernet ? Serialprint("    Subnet   = %u.%u.%u.%u\n", ip[0], ip[1], ip[2], ip[3]) : 0;
            ip = Ethernet.gatewayIP();
            mDebug_Ethernet ? Serialprint("    Gateway  = %u.%u.%u.%u\n", ip[0], ip[1], ip[2], ip[3]) : 0;
            ip = Ethernet.dnsServerIP();
            if (ip != INADDR_NONE)
            {  // May happen with static IP
                mDebug_Ethernet ? Serialprint("    DNS      = %u.%u.%u.%u\n", ip[0], ip[1], ip[2], ip[3]) : 0;
            }
        }
        else
        {
            mDebug_Ethernet ? Serialprint("[Ethernet] Address changed: No IP address\n") : 0;
        }

        // Tell interested parties the state of the IP address, for
        // example, servers, SNTP clients, and other sub-programs that
        // need to know whether to stop/start/restart/etc
        // Note: When setting a static IP, the address will be set but a
        //       link might not yet exist
        informServer(hasIP);
    });

    if (staticIP == INADDR_NONE)
    {
        mDebug_Ethernet ? Serialprint("Starting Ethernet with DHCP...\n") : 0;
        if (!Ethernet.begin())
        {
            mDebug_Ethernet ? Serialprint("Failed to start Ethernet\n") : 0;
            return false;
        }

      // We can choose not to wait and rely on the listener to tell us
      // when an address has been assigned
      if (kDHCPTimeout > 0)
      {
          if (!Ethernet.waitForLocalIP(kDHCPTimeout))
          {
              mDebug_Ethernet ? Serialprint("Failed to get IP address from DHCP\n") : 0;
              // We may still get an address later, after the timeout,
              // so continue instead of returning
          }
      }
    }
    else
    {
        mDebug_Ethernet ? Serialprint("Starting Ethernet with static IP...\n") : 0;
        Ethernet.begin(staticIP, subnetMask, gateway);

        // When setting a static IP, the address is changed immediately,
        // but the link may not be up; optionally wait for the link here
        if (kLinkTimeout > 0)
        {
            if (!Ethernet.waitForLink(kLinkTimeout))
            {
                mDebug_Ethernet ? Serialprint("Failed to get link\n") : 0;
                // We may still see a link later, after the timeout, so
                // continue instead of returning
            }
        }
    }
    return true;
}
/************************ Ende InitEthernet **********************************************************/

//*************************************************************************************************
// FunktionsName:   informServer
/// \details
/// \param[in]      hasIP
/// \return         retVal
//*************************************************************************************************
// Tell the server there's been an IP address change.
void informServer(bool hasIP)
{
    // If there's no IP address, could optionally stop the server,
    // depending on your needs
    if (hasIP)
    {
        if (*ethServer)
        {
            // Optional
            mDebug_Ethernet ? Serialprint("Address changed: Server already started\n") : 0;
        }
        else
        {
            mDebug_Ethernet ? Serialprint("Starting server on port %u...", MODBUS_PORT) : 0;
            //fflush(stdout);  // Print what we have so far if line buffered
            ethServer->begin();
            mDebug_Ethernet ? Serialprint("%s\n", *ethServer ? "done." : "FAILED!") : 0;
        }
    }
    else
    {
        // Stop the server if there's no IP address
        if (!*ethServer)
        {
            // Optional
            mDebug_Ethernet ? Serialprint("Address changed: Server already stopped\n") : 0;
        }
        else
        {
            mDebug_Ethernet ? Serialprint("Stopping server...") : 0;
            mDebug_Ethernet ? Serialprint("%s\n", ethServer->end() ? "done." : "FAILED!") : 0;
        }
    }
}
/************************ Ende informServer **********************************************************/

/************************ Ende mainFunktionen.cpp **********************************************************/

