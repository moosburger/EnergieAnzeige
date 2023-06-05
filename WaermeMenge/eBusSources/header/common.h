/*<  > ********************************************************************************/
/*!
*	\brief      Headerdatei die die gemeinsamen Variablen deklariert
*	\details    -
*
*	\file       common.h
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
* common.h
*/

#ifndef _COMMON_H_
#define _COMMON_H_

/**************************************************************************************************
* Includes
**************************************************************************************************/
#include <OneWire.h>
#include <DallasTemperature.h>

#include <ModbusEthernet.h>
/**************************************************************************************************
* Defines
**************************************************************************************************/
#define boolean     bool
#define VERSION     "0.9.1.0\t"

//OneWire
#define MAXSENSORS 5
#define ONEWIRE_PIN 32

// ModBus
#define MODBUS_PORT  502

// Wenn der zweite eBus verwendet werden soll
//#define EBUS

enum eBusStatus
{
    eBus_reInit,
    eBus_Ok,
    eBus_dataReady
};
/**************************************************************************************************
* Variablen
**************************************************************************************************/
//OneWire
extern volatile bool            mDebug_OneWire;
extern OneWire                  ds;
extern DallasTemperature        mSensors;

//ModBus
extern ModbusEthernet*          mb;

//eBus Werte
struct eBusValues_st
{
    float Tko;
    float Tfk;
    float Tso;
    float Tsu;
    float Tpu;
};
/************************ Ende  ******************************************************************/
#endif /* _MAIN_H_ */
/************************ Ende _COMMON_H_.h ******************************************************/

