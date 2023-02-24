/*<  > ********************************************************************************/
/*!
*	\brief      Die Headerdatei zu oneWireFunction.cpp
*	\details    -
*
*	\file       oneWireFunction.h
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
* oneWireFunction.h
*/

#ifndef _ONEWIREFUNCTION_H_
#define _ONEWIREFUNCTION_H_

/**************************************************************************************************
* Includes
**************************************************************************************************/
#include <OneWire.h>
#include <DallasTemperature.h>

/**************************************************************************************************
* Defines
**************************************************************************************************/
// Alle Eingänge LOW AKTIV
// Eingänge
// OneWire PIN 32


// Extern mit Langem Kabel  Ds Adr: 0x28:0x34:0xa2:0x97:0x94:0x00:0x03:0xac Temp: 31.25
// Intern verbaut           Ds Adr: 0x28:0x06:0xba:0x96:0x06:0x00:0x00:0x67 Temp: 21.88

/**************************************************************************************************
* Variablen
**************************************************************************************************/

//*************************************************************************************************
// Funktionen: -
/// \details    -
//*************************************************************************************************
void OneWireInit(DeviceAddress* SensorAddress, DallasTemperature* sensors, uint8_t* addr, uint8_t* SensorError, int resolution);
void OneWireAddresses(DeviceAddress* SensorAddress);
int GetTemperature(DeviceAddress* SensorAddress, DallasTemperature* sensors, uint8_t actualSensor, uint8_t* SensorError, float* Temperature);

/************************ Ende Funktionen *************************************************/
#endif /* _ONEWIREFUNCTION_H_ */
/************************ Ende oneWireFunction.h ******************************************************/

