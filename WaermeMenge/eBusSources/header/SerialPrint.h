/*<  > ********************************************************************************/
/*!
*   \brief      Header zu SerialPrint.c
*   \details    There is no println() version � instead, add \n or \r to your strings: Serialprint("Count %d, Data: %d\n",count,data);
                The Streamprint() is the more flexible option � you can use it for other serial items, of even the NewSoftSerial object. You just pass the Serial object of your choice as the first parameter � for example, here we�ll use Serial, in effect, doing the same as Serialprint();
                Streamprint(Serial,"Count %d, Data: %d\n",count,data);
*
*   \file       SerialPrint.cpp
*
*   \copyright  (C) 2016 Gerhard Prexl, All rights reserved.
*   \date       Erstellt am: 20.03.2016
*   \author     Gerhard Prexl
*
*   \version    1.0  -  20.02.2016
*/
/*< History > *************************************************************************************
*   Version     Datum       Kuerzel      Ticket#     Beschreibung
*   1.0         05.08.2014  GP           -------     Ersterstellung
* </ History ></  > ******************************************************************/

/**
* \addtogroup Main
* SerialPrint.h
*/
#ifndef SERIALPRINT_H
#define SERIALPRINT_H

/**************************************************************************************************
* Includes
**************************************************************************************************/
#include <avr/pgmspace.h>
#include <stdarg.h>
#include <Print.h>

/**************************************************************************************************
* Variablen
**************************************************************************************************/

/**************************************************************************************************
* Funktionen
**************************************************************************************************/
//int freeRam();
int StreamPrint_progmem(Print &out, PGM_P format, ...);

void SerialArrayPrint(const uint8_t* pDATA, uint8_t DATA_SIZE);

/**************************************************************************************************
* Defines
**************************************************************************************************/
#define Serialprint(format, ...) StreamPrint_progmem(Serial,PSTR(format),##__VA_ARGS__)
#define Streamprint(stream,format, ...) StreamPrint_progmem(stream,PSTR(format),##__VA_ARGS__)

/************************ Ende SerialPrint.h **********************************************************/

#endif
