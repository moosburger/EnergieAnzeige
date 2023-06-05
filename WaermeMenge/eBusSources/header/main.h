/*<  > ********************************************************************************/
/*!
*	\brief      Die Headerdatei zu main.cpp
*	\details    -
*
*	\file       main.h
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
* main.h
*/

#ifndef _MAIN_H_
#define _MAIN_H_

/**************************************************************************************************
* Includes
**************************************************************************************************/
#include <algorithm>
#include <utility>
#include <cmath>

#include <elapsedMillis.h>
#include <vector>
#include <stdint.h>

#include "common.h"
//#include "oneWireFunction.h"
//#include "modBusFunction.h"
/**************************************************************************************************
* Defines
**************************************************************************************************/
#define AKTIV           LOW
#define PASSIV          HIGH
#define MAXBYTE         6      /*<! Empfangsbyte der USB Verbindung */

#define MAX_IO          33
#define S0BUS1_PIN      30
#define S0BUS2_PIN      31
#define IRQ_DELAY       1000

#define Vers_Addr       1000
#define SoBus1_Addr     1100
#define SoBus2_Addr     1110
#define PumpeSo_Addr    1200
#define PumpeFK_Addr    1202
#define BrennSperr_Addr 1204
#define OW_Addr         2000

#define eBus0_Addr      3000
#ifdef EBUS2
    #define eBus1_Addr  3500
#endif

#define SPEICHER_TEMP_MIN 41
#define WARMWASSER_TEMP   54

#define PSOLAR_PIN       4
#define PFK_PIN          3
#define BSP_PIN          2
// Alle Eingänge LOW AKTIV
// Ausgänge
//LED_BUILTIN                   13      /*<! Eingebaute LED*/ 

// Eingänge
// OneWire  PIN 32
// S0 Bus 1 PIN 30
// S0 Bus 2 PIN 31
// eBus 1 Rx/Tx 6
// eBus 2 Rx/Tx 7

// analoge Eingänge

// Frei und NICHT verbunden
//

// Freie Analog Eingänge
//

/**************************************************************************************************
* Variablen
**************************************************************************************************/
// The DHCP timeout, in milliseconds. Set to zero to not wait and
// instead rely on the listener to inform us of an address assignment.
constexpr uint32_t                      kDHCPTimeout = 10000;  // 10 seconds

// The link timeout, in milliseconds. Set to zero to not wait and
// instead rely on the listener to inform us of a link.
constexpr uint32_t                      kLinkTimeout = 5000;  // 5 seconds
constexpr uint16_t                      kServerPort = 80;
// Timeout for waiting for input from the client.
constexpr uint32_t                      kClientTimeout = 5000;  // 5 seconds
// Timeout for waiting for a close from the client after a
// half close.
constexpr uint32_t                      kShutdownTimeout = 30000;  // 30 seconds

extern volatile bool                    mDebugOn;           /*<! */
extern volatile bool                    mDebug_Ethernet;    /*<! */
extern volatile bool                    mDebug_SoBus;       /*<! */
extern volatile bool                    mDebug_eBus0;       /*<! */
extern volatile bool                    mDebug_eBus1;       /*<! */
extern volatile bool                    mSerialAvail;       /*<! */
extern volatile unsigned long           mBlinkZeit;
extern volatile bool                    mBlink;             /*<! */

constexpr uint32_t                      mainDelay_ms    = 20;
constexpr uint32_t                      oneWireDelay_ms = 1500;
constexpr uint32_t                      modBusDelay_ms  = 250;
constexpr uint32_t                      eBusDelay_ms    = 50;

/*OneWire*/
constexpr int                           mResolution = 12;
extern DeviceAddress                    mSensorAddress[MAXSENSORS];
extern volatile uint8_t                 mSensorError[MAXSENSORS];
extern volatile uint8_t                 mActualSensor;
extern volatile float                   mTemperature[MAXSENSORS];
extern volatile uint8_t                 mAddr[8];

// So Bus
extern volatile unsigned int            mS0_Counter1;       /*<! */
extern volatile unsigned int            mS0_Counter2;       /*<! */
extern volatile bool                    mS0_Bus1_DelayOn;
extern volatile bool                    mS0_Bus2_DelayOn;
extern volatile unsigned int            mS0Back1;
extern volatile unsigned int            mS0Back2;

extern EthernetServer*                  ethServer;
// Set the static IP to something other than INADDR_NONE (zero)
// to not use DHCP. The values here are just examples.
extern IPAddress                        staticIP;
extern IPAddress                        subnetMask;
extern IPAddress                        gateway;
extern volatile boolean                 mbHasIp;

struct ClientState {
                    ClientState(EthernetClient client)
                        : client(std::move(client)) {}

                    EthernetClient client;
                    bool closed = false;

                    // For timeouts.
                    uint32_t lastRead = millis();  // Mark creation time

                    // For half closed connections, after "Connection: close" was sent
                    // and closeOutput() was called
                    uint32_t closedTime = 0;    // When the output was shut down
                    bool outputClosed = false;  // Whether the output was shut down

                    // Parsing state
                    bool emptyLine = false;
};

// Keeps track of what and where belong to whom.
extern std::vector<ClientState> clients;

struct PinFuerSperre_st
{
    uint8_t PumpeSo;
    uint8_t PumpeFK;
    uint8_t bSperre;
};

//*************************************************************************************************
// Funktionen: -
/// \details    -
//*************************************************************************************************
// Irq Funktionen
void IRQ_S0_Bus_1();
void IRQ_S0_Bus_2();
void initVar();

// Threads
void modBusServer();
void oneWireHandler();
void eBus0Handler();
#ifdef EBUS2
    void eBus1Handler();
#endif
void UsbCom();
void UsbDebugCom();

bool RisingEdge(bool*, bool*);

bool InitEthernet();
void informServer(bool hasIP);

void BrennerSperre(eBusValues_st* eBusValues, PinFuerSperre_st* PinFuerSperre);

/************************ Ende Funktionen *************************************************/
#endif /* _MAIN_H_ */
/************************ Ende main.h ******************************************************/

