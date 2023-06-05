/*<  > ********************************************************************************/
/*!
*   \brief      Die Headerdatei zu eBusFunction.cpp
*   \details    -
*
*   \file       eBusFunction.h
*
*   \copyright  (C) 2016 Gerhard Prexl, All rights reserved.
*   \author     Gerhard Prexl
*/
/*< History > *************************************************************************************
*   Version     Datum       Kuerzel      Ticket#     Beschreibung
*   0.9.0.1     04.02.2023  GP           -------     Ersterstellung
* </ History ></  > ******************************************************************/

/**
* \addtogroup Main
* eBusFunction.h
*/

#ifndef _EBUSFUNCTION_H_
#define _EBUSFUNCTION_H_

/**************************************************************************************************
* Includes
**************************************************************************************************/
#include <stdint.h>
#include <WString.h>

#include "common.h"

/**************************************************************************************************
* Defines
**************************************************************************************************/
#define EBUS_SYN                0xAA
#define EBUS_SYN_ESC_A9         0xA9
#define EBUS_SYN_ESC_01         0x01
#define EBUS_SYN_ESC_00         0x00
//
#define EBUS_ACK                0x00
#define EBUS_NAK                0xFF
//
//#define EBUS_QQ

#define MASTER_ADRESSE          0x77
#define SLAVE_ADRESSE           0x7C
#define WRSOL_MASTER            0xF7
#define WRSOL_SLAVE             0xFC
//
//#define EBUS_GET_RETRY          3
//#define EBUS_GET_RETRY_MAX      10
//#define EBUS_SKIP_ACK           1
//#define EBUS_MAX_WAIT           4000
//#define EBUS_SEND_RETRY         2
//#define EBUS_SEND_RETRY_MAX     10
//#define EBUS_PRINT_SIZE         30
//
//#define EBUS_MSG_BROADCAST      1
//#define EBUS_MSG_MASTER_MASTER  2
//#define EBUS_MSG_MASTER_SLAVE   3
//
#define cSERIAL_BAUDRATE        2400
#define cSERIAL_BUFSIZE         25
//
//#define CMD_DATA_SIZE           50 /* 5+16+3+16+2 = 42 || 256 */

#define cIDENT_STRING           0
#define cIDENTIFIKATION         1
#define cIDENT_REQUEST          2
#define cSLAVE_IDENT_REQUEST    3
#define cSEND_ACK               0
#define cSEND_NAK               1

#define cWRSOL_DATA_LINES       15
#define cWRSOL_DATA_START       4
#define cWRSOL_DATA_END         9

#define eBus0                   Serial6
#define eBus1                   Serial7

#define _Init                   -1
#define _NoData                 0
#define _BeginData              1
#define _FinishedData           2
#define _Sync                   4
#define _RequestetIdent         5
#define _CrcFailed              6
#define _NotValid               7
#define _Valid                  8
#define _SlaveMaster            9
#define _WaitAck                10
#define _WaitNak                11

#define _SelfIdent              0
#define _SelfIdentResponse      1
#define _SlaveIdent             2
#define _SlaveIdentResponse     3
#define _DataCycle              4
#define _DataCycleResponse      5
#define _DataCycleDelayed       6

#define  cDATA_DELAY            60000 // Muss Größer sein als das STUCK_DELAY!
#define cSTUCK_DELAY            10000
/**************************************************************************************************
* Variablen
**************************************************************************************************/
const uint8_t mWRSOL_TABLE[cWRSOL_DATA_LINES][15] = {
/*00*/{SLAVE_ADRESSE,0x07,0x04,0x01,0x00},                                                    // Identanfrage von einem Master                cIDENT_STRING
/*01*/{MASTER_ADRESSE,0xFE,0x07,0x04,0x0A,0xC5,0x53,0x6F,0x6C,0x41,0x6E,0x10,0x10,0x10,0x10}, // Sendet am Start die eigene Identnummer       cIDENTIFIKATION
/*02*/{0x00,0x0A,0xC5,0x53,0x6F,0x6C,0x41,0x6E,0x10,0x10,0x10,0x10},  //  Sendet auf Anforderung die eigene Identnummer                       cIDENT_REQUEST
/*03*/{MASTER_ADRESSE,WRSOL_SLAVE,0x07,0x04,0x01,0x00},               // Fordert die WRSOL auf sich zu Identifizieren                         cWRSOL_IDENT_REQUEST
/*04*/{MASTER_ADRESSE,WRSOL_SLAVE,0x09,0x00,0x03,0x00,0xFC,0x02},     // Fordert die WRSOL auf ihre Zeit zu senden
/*05*/{MASTER_ADRESSE,WRSOL_SLAVE,0x09,0x00,0x03,0x1C,0xF5,0x02},     // TKO Kollektor
/*06*/{MASTER_ADRESSE,WRSOL_SLAVE,0x09,0x00,0x03,0xCA,0xF4,0x02},     // TFK Feststoffkessel
/*07*/{MASTER_ADRESSE,WRSOL_SLAVE,0x09,0x00,0x03,0x84,0xF4,0x02},     // TSO Speicher oben
/*08*/{MASTER_ADRESSE,WRSOL_SLAVE,0x09,0x00,0x03,0x88,0xF4,0x02},     // TSU Speicher unten
/*09*/{MASTER_ADRESSE,WRSOL_SLAVE,0x09,0x00,0x03,0xF4,0xF4,0x02},     // TPU Puffer unten
/*10*/{MASTER_ADRESSE,WRSOL_SLAVE,0x09,0x00,0x03,0x8A,0xF5,0x02},     // TKO Max
/*11*/{MASTER_ADRESSE,WRSOL_SLAVE,0x09,0x00,0x03,0x30,0xF5,0x02},     // PS PumpeSolar
/*12*/{MASTER_ADRESSE,WRSOL_SLAVE,0x09,0x00,0x03,0x58,0xF5,0x02},     // PFK Pumpe Feststoffkessel
/*13*/{MASTER_ADRESSE,WRSOL_SLAVE,0x09,0x00,0x03,0xF2,0xF4,0x02},     // TPO Puffer oben
/*14*/{MASTER_ADRESSE,WRSOL_SLAVE,0x09,0x00,0x03,0xB4,0xF5,0x02},     // Wärmeerzeuger Sperre
};

const uint8_t mEBUS_TABLE[2][2] = {
/*00*/{EBUS_ACK,EBUS_SYN},
/*01*/{EBUS_NAK,EBUS_SYN},
};
const String mEBUS_PARAM[2][2] = {
/*00*/{"Ack"},
/*01*/{"Nok"},
};

/*
 * Master sendet:
 * MASTER_ADRESSE, WRSOL_SLAVE, RAM-Daten-Lesen(2Bytes), Datenlänge, LSB, MSB, Anzahl zu lesender DatenBytes, CRC
 * MASTER_ADRESSE, WRSOL_SLAVE,       0x09,0x00        , 0x03      ,0x88,0xF4, 0x02, CRC
 *
 * Slave antwortet
 * ACK, Anzahl Bytes, LSB, MSB, CRC
 * 0x00,     0x02   ,    ,    , CRC
 *
 * Master antwortet
 * ACK, SYN
 * 0x00, 0xAA
 *
 * oder wenn Fehler
 * 0xFF, 0xAA
 */

const String mWRSOL_PARAM[cWRSOL_DATA_LINES] = {
/*00*/{"Id1"},
/*01*/{"Id2"},
/*02*/{"Id3"},
/*03*/{"Id4"},
/*04*/{"Tim"},
/*05*/{"TKO"},
/*06*/{"TFK"},
/*07*/{"TSO"},
/*08*/{"TSU"},
/*09*/{"TPU"},
/*10*/{"TKM"},
/*11*/{"PS "},
/*12*/{"PFK"},
/*13*/{"TPO"},
/*14*/{"WES"},
};

extern volatile uint8_t     eBus0State;
extern elapsedMillis        mRun_eBus0;
extern elapsedMillis        mDataRequestDelay_eBus0;
#ifdef EBUS2
    extern volatile uint8_t eBus1State;
    extern elapsedMillis    mDataRequestDelay_eBus1;
#endif
struct eBusData
{
    uint16_t        modBusAddr;
    uint8_t         modBusOfs;
    uint8_t         eBus_buffer[cSERIAL_BUFSIZE];    /* buffer for the received message */
    uint8_t         eBus_pos;
    boolean         eBus_out;
    uint8_t         eBus_Byte;

    uint8_t         mRequestDataPos;
    uint8_t         mLastCmd;
    uint8_t         mLastDataSize;
    uint8_t         mFailureCnt;
    bool            mDebug;
};

//*************************************************************************************************
// Funktionen: -
//*************************************************************************************************
void eBus0Init(uint16_t iAddr, boolean bReInit);
int eBus0Task(boolean debug, eBusValues_st* eBusValues);
void sendDataBus0(uint8_t DATA, uint8_t DATA_SIZE);

#ifdef EBUS2
    void eBus1Init(uint16_t iAddr, boolean bReInit);
    int eBus1Task(boolean debug);
    void sendDataBus1(uint8_t DATA, uint8_t DATA_SIZE);
#endif

void sendAck(uint8_t BusNumber);
void sendNak(uint8_t BusNumber);
uint8_t readData();
uint8_t wrsolIdent(uint8_t DATA, uint8_t DATA_SIZE);
uint8_t analyzeData(uint8_t retData, uint8_t eBusState, uint8_t BusNumber);
uint8_t analyzeCmd(uint8_t eBusState, uint8_t BusNumber);
uint8_t eBusTimedOut(uint8_t BusNumber, uint8_t recoverState, uint8_t actState);

/**
BCD*    char                  0 bis 99
data1b  signed char        -127 bis + 127
data1c  char                  0 bis 100
data2b  signed integer  -127,99 bis + 127,99
data2c  signed integer  -2047,9 bis 2047,9
 */
int eb_htoi(const char *buf);
void eb_esc(unsigned char *buf, int *buflen);
void eb_unesc(unsigned char *buf, int *buflen);
int eb_day_to_str(unsigned char day, String *tgt);
void wrSOL_HexToTime(uint16_t timeStamp, uint8_t* DayOfWeek, uint8_t* Hour, uint8_t* Min);
int eb_dat_to_str(unsigned char dd, unsigned char mm, unsigned char yy, char *tgt);
int eb_str_to_dat(int dd, int mm, int yy, unsigned char *tgt);
int eb_tim_to_str(unsigned char hh, unsigned char mm, unsigned char ss, char *tgt);
int eb_str_to_tim(int hh, int mm, int ss, unsigned char *tgt);
int eb_bcd_to_int(unsigned char src, int *tgt);
int eb_int_to_bcd(int src, unsigned char *tgt);
int eb_d1b_to_int(unsigned char src, int *tgt);
int eb_int_to_d1b(int src, unsigned char *tgt);
int eb_d1c_to_float(unsigned char src, float *tgt);
int eb_float_to_d1c(float src, unsigned char *tgt);
int eb_d2b_to_float(unsigned char src_lsb, unsigned char src_msb, float *tgt);
int eb_float_to_d2b(float src, unsigned char *tgt_lsb, unsigned char *tgt_msb);
int eb_d2c_to_float(unsigned char src_lsb, unsigned char src_msb, float *tgt);
int eb_float_to_d2c(float src, unsigned char *tgt_lsb, unsigned char *tgt_msb);
unsigned char eb_calc_crc_byte(unsigned char byte, unsigned char init_crc);
unsigned char eb_calc_crc(const unsigned char *bytes, int size);

/************************ Ende Funktionen *************************************************/
#endif /* _EBUSFUNCTION_H_ */
/************************ Ende eBusFunction.h ******************************************************/

