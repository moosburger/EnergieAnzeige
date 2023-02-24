/*<  > ********************************************************************************/
/*!
*	\brief      -
*	\details    -
*
*	\file       eBus.cpp
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
* main.cpp
*/
/**************************************************************************************************
* Includes
**************************************************************************************************/
#include <Arduino.h>
#include <avr/io.h>
//#include <avr/wdt.h>
#include <core_pins.h>
#include <usb_serial.h>
#include <TeensyThreads.h>

#include "main.h"
#include "eBusFunction.h"
#include "oneWireFunction.h"
#include "modBusFunction.h"
#include "SerialPrint.h"

/**************************************************************************************************
* Defines
**************************************************************************************************/
    // Eingänge
    // OneWire PIN 32
    // S0 Bus 1 PIN 30
    // S0 Bus 2 PIN 31
    // eBus 1 Rx/Tx Serial6
    // eBus 2 Rx/Tx Serial7

/**************************************************************************************************
* Variablen
**************************************************************************************************/
bool                            mDebugOn;           /*<! */
bool                            mDebug_Ethernet;    /*<! */
bool                            mDebug_OneWire;     /*<! */
bool                            mDebug_SoBus;       /*<! */
bool                            mDebug_eBus0;       /*<! */
bool                            mDebug_eBus1;       /*<! */
bool                            mSerialAvail;       /*<! */
elapsedMillis                   mLebensZeichen;     /*<! */
elapsedMillis                   mLaufZeit;
unsigned long                   mBlinkZeit;
bool                            mBlink;             /*<! */
/*
 * WatchDog in der wdt.h
    wdt_reset()
    wdt_enable(timeout)
    wdt_disable()
 */

//OneWire
OneWire  ds(ONEWIRE_PIN); //pin für DS18B20
DallasTemperature mSensors(&ds);

DeviceAddress mSensorAddress[MAXSENSORS] = {
        { 0x28, 0x3D, 0xB6, 0x3, 0x5, 0x0, 0x0, 0xD7 }
};
uint8_t                         mSensorError[MAXSENSORS] = {0};
uint8_t                         mActualSensor;
float                           mTemperature[MAXSENSORS] = {0};
uint8_t                         mAddr[8];

// So0 Bus
unsigned int                    mS0_Counter1;       /*<! */
unsigned int                    mS0_Counter2;       /*<! */
bool                            mS0_Bus1_DelayOn;
bool                            mS0_Bus2_DelayOn;
unsigned int                    mS0Back1;
unsigned int                    mS0Back2;
elapsedMillis                   mS0_Bus1_ms;        /*<! */
elapsedMillis                   mS0_Bus2_ms;        /*<! */

// Ethernet
boolean                         mbHasIp;
ModbusEthernet*                 mb;
EthernetServer*                 ethServer;

// Set the static IP to something other than INADDR_NONE (zero)
// to not use DHCP. The values here are just examples.
IPAddress staticIP{0, 0, 0, 0};//{192, 168, 2, 39};
IPAddress subnetMask{255, 255, 255, 0};
IPAddress gateway{192, 168, 2, 40};

// Keeps track of what and where belong to whom.
std::vector<ClientState> clients;
/**************************************************************************************************
* Funktionen
**************************************************************************************************/

//*************************************************************************************************
// FunktionsName:   initVar
/// \details        Initialisiert die globalen Vars
/// \param[in]      -
/// \return         -
//*************************************************************************************************
void initVar()
{
    mDebugOn         = false;
    mDebug_Ethernet  = false;
    mDebug_OneWire   = false;
    mDebug_SoBus     = false;
    mDebug_eBus0     = true;
    mDebug_eBus1     = false;

    mSerialAvail     = false;
    mLebensZeichen   = 0;
    mLaufZeit        = 0;
    mBlink           = HIGH;
    mBlinkZeit       = 1000;

    mS0_Counter1     = 0;
    mS0_Counter2     = 0;
    mS0_Bus1_DelayOn = false;
    mS0_Bus2_DelayOn = false;
    mS0_Bus1_ms      = 0;
    mS0_Bus2_ms      = 0;
    mS0Back1         = 0;
    mS0Back2         = 0;

    mActualSensor    = 0;
    mbHasIp          = false;
}
/************************ Ende initVar ************************************************************/

//*************************************************************************************************
// FunktionsName:   setup
/// \details        Wird beim Startup des Prozessors einmal durchlaufen
///                 INPUT, INPUT_PULLUP; OUTPUT
/// \param[in]      -
/// \return         -
//*************************************************************************************************
void setup()
{
    initVar();

    /*  in einer Schleife alle Pins zunächst auf INPUT */
    for (int i = 0; i < MAX_IO; i++)
        pinMode(i, INPUT);

    /* Digitale Ausgänge */
    pinMode(LED_BUILTIN, OUTPUT);

    /* Interrupt Zuordnungen */
    attachInterrupt(digitalPinToInterrupt(S0BUS1_PIN), IRQ_S0_Bus_1, FALLING);
    attachInterrupt(digitalPinToInterrupt(S0BUS2_PIN), IRQ_S0_Bus_2, FALLING);

    /*Serielle Schnittstelle über USB */
    Serial.begin(9600);
    /* Den Com15 im Serial Monitor löschen, Teensy starten, dann wieder hinzufügen */

    /* Trigger Wd Timer */
    //wdt_enable(WDTO_8S)

    /* One Wire initialisieren */
    OneWireInit(mSensorAddress, &mSensors, mAddr, mSensorError, mResolution);
    /* Interne Temperatur holen */
    mSensors.requestTemperatures();

    /* Interrupts freigeben */
    interrupts();

    // Beim debuggen hier warten bis die Serielle Verbindung aufgebaut wurde
    if (mDebug_Ethernet || mDebug_eBus0)
        do  {   delay(500); }   while (!Serial.dtr());

    // Ethernet initialisiern und IP per DHCP holen
    ethServer = new EthernetServer(MODBUS_PORT); // @suppress("Abstract class cannot be instantiated")
    do
    {
        mbHasIp = !((uint32_t) Ethernet.localIP() == 0);
        if(mbHasIp == true)
            break;

        digitalWrite(LED_BUILTIN, HIGH);
        if (InitEthernet() == false)
        {   // Timeout konfigurierbar, default 60s auf 10s gesetzt
            digitalWrite(LED_BUILTIN, LOW);
            delay(mBlinkZeit);
        }

    } while(mbHasIp == false);

    /* ModBus Server initialisieren */
    mb = new ModbusEthernet();
    mb->server(MODBUS_PORT);                    // Act as Modbus TCP server
    //mb->begin();

    // Hier die benötigten Register anlegen
    mb->addReg(HREG(Vers_Addr), (uint16_t)0, 8);   // SerienNummer
    mb->addReg(HREG(SoBus1_Addr), (uint16_t)0, 2);   // S0_Bus_1
    mb->addReg(HREG(SoBus2_Addr), (uint16_t)0, 2);   // S0_Bus_2
    for (int u = 0; u < MAXSENSORS; u++)
    {
        uint16_t iAddr = OW_Addr + u * 10;
        mb->addReg(HREG(iAddr), (uint16_t)0, 10); // OneWire Float
    }
    // eBus Werte Array - 4 Idents, plus 1 als LIVE COUNT
    for (int u = 0; u < cWRSOL_DATA_LINES - 3; u++)
    {
        uint16_t iAddr = eBus0_Addr + u * 2;
        mb->addReg(HREG(iAddr), (uint16_t)0, 2); // eBus Float
    }
    // Serielle HardwareSchnittstellen für eBus initialisieren
    eBus0Init(eBus0_Addr, false);
    threads.addThread(eBus0Handler);

#ifdef EBUS2
    // eBus Werte Array - 4 Idents, plus 1 als LIVE COUNT
    for (int u = 0; u < cWRSOL_DATA_LINES - 3; u++)
    {
        uint16_t iAddr = eBus1_Addr + u * 2;
        mb->addReg(HREG(iAddr), (uint16_t)0, 2); // eBus Float
    }
    eBus1Init(eBus1_Addr, false);
    // Serielle HardwareSchnittstellen für eBus initialisieren
    threads.addThread(eBus1Handler);
#endif

    // Statische werte hier beschreiben, wie Version usw.
    String data = VERSION;//"AbCdEfGhIjKlMnO";
    _ConfCharToInt(1000, data);

    /* Threads */
    threads.addThread(modBusServer);
    threads.addThread(oneWireHandler);
}
/************************ Ende setup *************************************************************/

//*************************************************************************************************
// FunktionsName:   Irq Funktion
/// \details        S0 Bus 1 und 2 auswerten
//*************************************************************************************************
void IRQ_S0_Bus_1()
{
    if(!mS0_Bus1_DelayOn)
    {
        noInterrupts();
        mS0_Bus1_DelayOn = true;
        mS0_Bus1_ms = 0;
        mS0_Counter1++;
        interrupts();
    }
}

void IRQ_S0_Bus_2()
{
    if(!mS0_Bus2_DelayOn)
    {
        noInterrupts();
        mS0_Bus2_DelayOn = true;
        mS0_Bus2_ms = 0;
        mS0_Counter2++;
        interrupts();
    }
}
/************************ Ende Irq Funktionen ****************************************************/

//*************************************************************************************************
// FunktionsName:   modBusServer
/// \details        Thread für den ModBus
/// \param[in]      -
/// \return         -
//*************************************************************************************************
void modBusServer()
{
    while (1)
    {
        mb->task();
        
        threads.delay(modBusDelay_ms);
        threads.yield();
    }
}
/************************ Ende modBusServer Thread ************************************************/

//*************************************************************************************************
// FunktionsName:   eBus0Handler
/// \details        Thread für den eBus
/// \param[in]      -
/// \return         -
//*************************************************************************************************
void eBus0Handler()
{
    while (1)
    {
        if (!eBus0Task(mDebug_eBus0))
        {
            eBus0Init(eBus0_Addr, true);
            threads.delay(eBusDelay_ms);
            threads.yield();
            eBus0Init(eBus0_Addr, false);
        }
        threads.delay(eBusDelay_ms);
        threads.yield();
    }
}
/************************ Ende eBus0Handler Thread ************************************************/

//*************************************************************************************************
// FunktionsName:   eBus1Handler
/// \details        Thread für den eBus
/// \param[in]      -
/// \return         -
//*************************************************************************************************
#ifdef EBUS2
    void eBus1Handler()
    {
        while (1)
        {
            if (!eBus1Task(mDebug_eBus1))
            {
                eBus1Init(eBus1_Addr, true);
                threads.delay(eBusDelay_ms);
                threads.yield();
                eBus1Init(eBus1_Addr, false);
            }
            threads.delay(eBusDelay_ms);
            threads.yield();
        }
    }
#endif
/************************ Ende eBus1Handler Thread ************************************************/

//*************************************************************************************************
// FunktionsName:   oneWireHandler
/// \details        Thread für den OneWire
/// \param[in]      -
/// \return         -
//*************************************************************************************************
void oneWireHandler()
{
    while (1)
    {
        uint8_t actualSensor = GetTemperature(mSensorAddress, &mSensors, mActualSensor, mSensorError, mTemperature);
        mDebug_OneWire ? Serial.print("Temp :") : 0;
        mDebug_OneWire ? Serial.println(mTemperature[mActualSensor]) : 0;
        mDebug_OneWire ? Serialprint("Address: %u:%u:%u:%u:%u:%u:%u:%u\n", mSensorAddress[mActualSensor][0],mSensorAddress[mActualSensor][1],
                     mSensorAddress[mActualSensor][2],mSensorAddress[mActualSensor][3],mSensorAddress[mActualSensor][4],
                     mSensorAddress[mActualSensor][5],mSensorAddress[mActualSensor][6],mSensorAddress[mActualSensor][7]) : 0;

        _Conf_Two_Register(2000 + (mActualSensor) * 10, (float)mTemperature[mActualSensor]);
        for (int i = 0; i < 8; i++)
        {
            String strData(mSensorAddress[mActualSensor][i]);
            int iCnt = strData.length();
            _Conf_One_Register(2000 + (mActualSensor) * 10 + 2 + i, (uint16_t) mSensorAddress[mActualSensor][i], iCnt);
        }
        mActualSensor = actualSensor;
        threads.delay(oneWireDelay_ms);
        threads.yield();
    }
}
/************************ Ende oneWireHandler Thread **********************************************/

//*************************************************************************************************
// FunktionsName:   loop
/// \details        Die Hauptschleife, wird endlos durchlaufen
/// \param[in]      -
/// \return         -
//*************************************************************************************************
void loop()
{
    if (Serial.dtr())
        mSerialAvail = true;
    else
        mSerialAvail = false;

    // WatchDog
    //wdt_reset()

    /* Usb Kommunikation */
    if (mSerialAvail)
        UsbCom();
    /* Debug Ausgaben wenn freigegeben */
    if (mDebugOn)
        UsbDebugCom();

    /* Lebenszeichen */
    if ((mbHasIp) && (mLebensZeichen > mBlinkZeit))
    {
        digitalWrite(LED_BUILTIN, mBlink);
        mLebensZeichen = 0;
        mBlink = !mBlink;
    }

    /* S0 Bus 1.
     * Am Gaszähler ist auch auf dem 0,001 Kubikmeter Gas auf der Zahl 6 eine Reflektion aufgebracht die ausgewertet werden könnte
     * Gaszähler Actaris G4 RF1. 1 Impuls = 0,1 Kubikmeter Gas */
    if(mS0_Counter1 != mS0Back1)
    {
        _Conf_Two_Register(1100, (uint32_t)mS0_Counter1);

        mDebug_SoBus ? Serialprint("So0-1: %u\n", mS0_Counter1) : 0;
        mS0Back1 = mS0_Counter1;
    }
    /* S0 Bus 2.
     * WasserUhr? */
    if(mS0_Counter2 != mS0Back2)
    {
        _Conf_Two_Register(1110, (uint32_t)mS0_Counter2);

        mDebug_SoBus ? Serialprint("So0-2: %u\n", mS0_Counter2) : 0;
        mS0Back2 = mS0_Counter2;
    }

    /* Interrupt wieder nutzen */
    if ((mS0_Bus1_DelayOn) && (mS0_Bus1_ms >= IRQ_DELAY))
    {
        mS0_Bus1_DelayOn = false;
    }
    if ((mS0_Bus2_DelayOn) && (mS0_Bus2_ms >= IRQ_DELAY))
    {
        mS0_Bus2_DelayOn = false;
    }

    threads.delay(mainDelay_ms);
    threads.yield();
}
/************************ Ende loop **************************************************************/

/************************ Ende eBus.cpp **********************************************************/

