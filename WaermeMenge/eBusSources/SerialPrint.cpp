/*<  > ********************************************************************************/
/*!
*   \brief      -
*   \details    There is no println() version instead, add \n or \r to your strings: Serialprint("Count %d, Data: %d\n",count,data);
*               The Streamprint() is the more flexible option you can use it for other serial items, of even the NewSoftSerial object.
*               You just pass the Serial object of your choice as the first parameter for example, here well use Serial, in effect,
*               doing the same as Serialprint();
*               Streamprint(Serial,"Count %d, Data: %d\n",count,data);
                Untestützt kein %f für float Werte.
*
*   \file       SerialPrint.cpp
*
*   \copyright  (C) 2016 Gerhard Prexl, All rights reserved.
*   \author     Gerhard Prexl
*/
/*< History > *************************************************************************************
*   Version     Datum       Kuerzel      Ticket#     Beschreibung
*   0.1         05.08.2021  GP           -------     Ersterstellung
* </ History ></  > ******************************************************************/

/**
* \addtogroup Main
* SerialPrint.cpp
*/

/**************************************************************************************************
* Includes
**************************************************************************************************/
#include "Arduino.h"
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
// FunktionsName:   StreamPrint_progmem
/// \details        -
/// \param[in]      -
/// \return         -
//*************************************************************************************************
int StreamPrint_progmem(Print &out, PGM_P format, ...)
{
    int retVal;
    // program memory version of printf - copy of format string and result share a buffer
    // so as to avoid too much memory use
    char formatString[128], *ptr;
    strncpy_P( formatString, format, sizeof(formatString) ); // copy in from program mem

    // null terminate - leave last char since we might need it in worst case for result's \0
    formatString[ sizeof(formatString)-2 ]='\0';
    ptr=&formatString[ strlen(formatString)+1 ]; // our result buffer...

    va_list args;
    va_start(args,format);

    vsnprintf(ptr, sizeof(formatString)-1-strlen(formatString), formatString, args );

    va_end (args);
    formatString[ sizeof(formatString)-1 ]='\0';

    retVal = out.print(ptr);
    return retVal;
}
/************************ Ende StreamPrint_progmem **********************************************************/

//*************************************************************************************************
// FunktionsName:   SerialArrayPrint
/// \details        -
/// \param[in]      -
/// \return         -
//*************************************************************************************************
void SerialArrayPrint(const uint8_t* pDATA, uint8_t DATA_SIZE)
{
    for (int i = 0; i < DATA_SIZE; i++)
    {
        Serial.print(pDATA[i], HEX);
        Serial.print(" ");
    }
    Serial.println();
}
/************************ Ende SerialArrayPrint **********************************************************/

/************************ Ende SerialPrint.cpp **********************************************************/

