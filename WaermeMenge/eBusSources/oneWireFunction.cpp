/*<  > ********************************************************************************/
/*!
*	\brief      -
*	\details    -
*
*	\file		oneWireFunction.cpp
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
* oneWireFunction.cpp
*/

/**************************************************************************************************
* Includes
**************************************************************************************************/
//#include "main.h"
#include "common.h"
#include "oneWireFunction.h"
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
// FunktionsName:   OneWireInit
/// \details
/// \param[in]      DeviceAddress*
/// \param[in]      DallasTemperature*
/// \param[in]      byte*
/// \param[in]      byte*
/// \param[in]      int
/// \return         -
//*************************************************************************************************
void OneWireInit(DeviceAddress* SensorAddress, DallasTemperature* sensors, uint8_t* addr, uint8_t* SensorError, int resolution)
{
    sensors->begin();

    // The DallasTemperature library can do all this work for you!
    int iMaxCount = sensors->getDS18Count();
    if (iMaxCount > MAXSENSORS)
        iMaxCount = MAXSENSORS;
    for (int i=0; i<iMaxCount; i++)
    {
        sensors->getAddress(addr, i);
        for (int k = 0; k < 9; k++)
            SensorAddress[i][k] = addr[k];

        SensorError[i] = 2;
        sensors->setResolution(SensorAddress[i], resolution);
    }
    sensors->setWaitForConversion(false);
}
/************************ Ende OneWireInit **********************************************************/

//*************************************************************************************************
// FunktionsName:   OneWireAddresses
/// \details
/// \param[in]      DeviceAddress*
/// \return         -
//*************************************************************************************************
void OneWireAddresses(DeviceAddress* SensorAddress)
{
    // Im Array address enthaltene Daten kompakt sedezimal ausgeben
    byte i;

    for (int j=0; j<MAXSENSORS; j++)
    {
        if (OneWire::crc8(SensorAddress[j], 7) != SensorAddress[j][7])
        {
            mDebug_OneWire ? Serialprint("hat keinen gueltigen CRC!\n") : 0;
        }
        else
        {
            //alles ist ok, anzeigen
            for (i = 0; i < 8; i++)
            {
                if (SensorAddress[j][i] <= 0xF)
                {
                    mDebug_OneWire ? Serialprint("Adresse ist 0") : 0;
                }
                mDebug_OneWire ? Serialprint("SensorAdresse %u", (uint8_t)SensorAddress[j][i],HEX) : 0;
            }
            mDebug_OneWire ? Serialprint("\n") : 0;
        }
    }
}
/************************ Ende OneWireAddresses **********************************************************/

//*************************************************************************************************
// FunktionsName:   GetTemperature
/// \details
/// \param[in]      DeviceAddress*
/// \param[in]      DallasTemperature*
/// \param[in]      byte
/// \param[in]      byte*
/// \param[in]      float*
/// \return         int
//*************************************************************************************************
int GetTemperature(DeviceAddress* SensorAddress, DallasTemperature* sensors, uint8_t actualSensor, uint8_t* SensorError, float* Temperature)
{
    Temperature[actualSensor] = sensors->getTempC(SensorAddress[actualSensor]);
    if (Temperature[actualSensor] == -127.0)
    {
      if (SensorError[actualSensor] == 0)
        SensorError[actualSensor] = 2;
    }
    else
      if (SensorError[actualSensor] == 2)
          SensorError[actualSensor] = 0;

    actualSensor++;
    if (actualSensor >= MAXSENSORS)
    {
      actualSensor = 0;
    }
    sensors->requestTemperaturesByAddress(SensorAddress[actualSensor]);
    return actualSensor;
}
/************************ Ende GetTemperature **********************************************************/

/************************ Ende oneWireFunktionen.cpp **********************************************************/

