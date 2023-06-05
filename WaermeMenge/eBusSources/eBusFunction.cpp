/*<  > ********************************************************************************/
/*!
*   \brief      -
*   \details    -
*
*   \file       eBusFunction.cpp
*
*   \copyright  (C) 20236 Gerhard Prexl, All rights reserved.
*   \author     Gerhard Prexl
*/
/*< History > *************************************************************************************
*   Version     Datum       Kuerzel      Ticket#     Beschreibung
*   0.9.0.1     04.02.2023  GP           -------     Ersterstellung
* </ History ></  > ******************************************************************/

/**
* \addtogroup Main
* eBusFunction.cpp
*/
/**************************************************************************************************
* Includes
**************************************************************************************************/
#include <elapsedMillis.h>

#include "modBusFunction.h"
#include "eBusFunction.h"
#include "SerialPrint.h"

/**************************************************************************************************
* Defines
**************************************************************************************************/

/**************************************************************************************************
* Variablen
**************************************************************************************************/
volatile uint8_t        eBus0State;
elapsedMillis           mRun_eBus0;
elapsedMillis           mDataRequestDelay_eBus0;
#ifdef EBUS2
    volatile uint8_t    eBus1State;
    elapsedMillis       mRun_eBus1;
    elapsedMillis       mDataRequestDelay_eBus1;
#endif

volatile eBusData       eBuses[2];
/***************************************************************************************************
* Funktionen
**************************************************************************************************/

//*************************************************************************************************
// FunktionsName:   eBus0Init
/// \details        Initialisiert eBus 0
/// \param[in]      -
/// \return         -
//*************************************************************************************************
void eBus0Init(uint16_t iAddr, boolean bReInit)
{
    if (bReInit)
    {
        eBuses[0].mDebug ? Serialprint("ReInit eBus 1\n") : 0;
        eBus0.end();
        return;
    }

    mRun_eBus0 = 0;
    mDataRequestDelay_eBus0 = 0;
    eBuses[0].modBusAddr = iAddr;
    eBuses[0].modBusOfs = 0;
    eBuses[0].eBus_out = false;
    eBuses[0].eBus_Byte = 0;

    eBuses[0].eBus_pos = 0;
    eBuses[0].mRequestDataPos = cWRSOL_DATA_START;
    eBuses[0].mLastCmd = 0;
    eBuses[0].mLastDataSize = 0;
    eBuses[0].mFailureCnt = 0;
    eBuses[0].mDebug = false;

    Serialprint("Init eBus 1\n");
    eBus0.begin(cSERIAL_BAUDRATE);
}
/************************ Ende eBus0Init **********************************************************/

//*************************************************************************************************
// FunktionsName:   eBus1Init
/// \details        Initialisiert eBus 1
/// \param[in]      -
/// \return         -
//*************************************************************************************************
#ifdef EBUS2
void eBus1Init(uint16_t iAddr, boolean bReInit)
{
    if (bReInit)
    {
        eBuses[1].mDebug ? Serialprint("Init eBus 2\n") : 0;
        eBus1.end();
        return;
    }

    mRun_eBus1 = 0;
    eBuses[1].modBusAddr = iAddr;
    eBuses[1].modBusOfs = 2;
    eBuses[1].eBus_out = false;
    eBuses[1].eBus_Byte = 0;

    eBuses[1].eBus_pos = 0;
    eBuses[1].mRequestDataPos = cWRSOL_DATA_START;
    eBuses[1].mLastCmd = 0;
    eBuses[1].mLastDataSize = 0;
    eBuses[1].mFailureCnt = 0;
    eBuses[1].mLastTimeStamp = 0;
    eBuses[1].mLastValue = 0;
    eBuses[1].mFirstRun = true;
    eBuses[1].mDebug = false;

    Serialprint("Init eBus 2\n");
    eBus1.begin(cSERIAL_BAUDRATE);
}
#endif
/************************ Ende eBus1Init **********************************************************/

//*************************************************************************************************
// FunktionsName:   wrsolIdent
/// \details        wertet das Telegramm aus und prüft die CRC. Wenn die Identifizierung angefordet werden sollte
/// \param[in]      DATA
/// \param[in]      DATA_SIZE
/// \return         Ident Angefordert
//*************************************************************************************************
uint8_t wrsolIdent(uint8_t DATA, uint8_t DATA_SIZE)
{
    uint8_t l = 0;
    uint8_t crc1 =  eb_calc_crc(mWRSOL_TABLE[DATA], DATA_SIZE);

    unsigned char* test = (unsigned char*)eBuses[0].eBus_buffer;
    uint8_t crc2 =  eb_calc_crc(test, DATA_SIZE);

    if (crc1 == crc2)
        l++;

    for (uint8_t i=1; i < DATA_SIZE; i++)
    {
        if (eBuses[0].eBus_buffer[i] == mWRSOL_TABLE[DATA][i-1])
            l++;
    }

    if (l == DATA_SIZE + 1)
        return 1;
    else
        return 0;
}
/************************ Ende eBusInit **********************************************************/

//*************************************************************************************************
// FunktionsName:   sendData
/// \details        -
/// \param[in]      DATA
/// \param[in]      DATA_SIZE
/// \return         -
//*************************************************************************************************
void sendDataBus0(uint8_t DATA, uint8_t DATA_SIZE)
{
    eBuses[0].mLastCmd = DATA;
    eBuses[0].mLastDataSize = DATA_SIZE;

    /*if (eBuses[0].mDebug == true)
    {
        Serial.print("\nCmd:\t");
        Serial.print(mWRSOL_PARAM[DATA]);
        Serial.print("\t");
        //Serial.print("Crc: ");
        //Serial.println(eb_calc_crc(mWRSOL_TABLE[DATA], DATA_SIZE));
    }*/

    // Daten
    eBus0.write(mWRSOL_TABLE[DATA], DATA_SIZE);
    // Crc
    eBus0.write(eb_calc_crc(mWRSOL_TABLE[DATA], DATA_SIZE));
    eBus0.flush();

    if (DATA == cIDENT_STRING)
    {
        Serial.println("cIDENT_STRING");
        SerialArrayPrint(mWRSOL_TABLE[DATA], DATA_SIZE);
    }
}
/************************ Ende sendData **********************************************************/

//*************************************************************************************************
// FunktionsName:   sendData
/// \details        -
/// \param[in]      DATA
/// \param[in]      DATA_SIZE
/// \return         -
//*************************************************************************************************
#ifdef EBUS2
void sendDataBus1(uint8_t DATA, uint8_t DATA_SIZE)
{
    eBuses[1].mLastCmd = DATA;
    eBuses[1].mLastDataSize = DATA_SIZE;

    if (eBuses[1]].mDebug == true)
    {
        Serial.print("\nCmd:\t");
        Serial.print(mWRSOL_PARAM[DATA]);
        Serial.print("\t");
        //Serial.print("Crc: ");
        //Serial.println(eb_calc_crc(mWRSOL_TABLE[DATA], DATA_SIZE));
    }

    // Daten
    eBus1.write(mWRSOL_TABLE[DATA], DATA_SIZE);
    // Crc
    eBus1.write(eb_calc_crc(mWRSOL_TABLE[DATA], DATA_SIZE));
    eBus1.flush();

    if (DATA == cIDENT_STRING)
    {
        Serial.println("cIDENT_STRING");
        SerialArrayPrint(mWRSOL_TABLE[DATA], DATA_SIZE);
    }
}
#endif
/************************ Ende sendData **********************************************************/

//*************************************************************************************************
// FunktionsName:   sendAck
/// \details        -
/// \param[in]      -
/// \param[in]      -
/// \return         -
//*************************************************************************************************
void sendAck(uint8_t BusNumber)
{
    /*if (eBuses[BusNumber].mDebug == true)
    {
        Serial.print("\nCmd: ");
        Serial.print(mEBUS_PARAM[cSEND_ACK]);
        Serial.print("\t");
        SerialArrayPrint(mEBUS_TABLE[cSEND_ACK], 2);
    }*/
    if (BusNumber == 0)
    {
        eBus0.write(mEBUS_TABLE[cSEND_ACK], 2);
        eBus0.flush();
    }

    if (BusNumber == 1)
    {
        eBus1.write(mEBUS_TABLE[cSEND_ACK], 2);
        eBus1.flush();
    }
}
/************************ Ende sendAck **********************************************************/

//*************************************************************************************************
// FunktionsName:   sendNak
/// \details        -
/// \param[in]      -
/// \param[in]      -
/// \return         -
//*************************************************************************************************
void sendNak(uint8_t BusNumber)
{
    /*if (eBuses[BusNumber].mDebug == true)
    {
        Serial.print("\nCmd: ");
        Serial.print(mEBUS_PARAM[cSEND_ACK]);
        Serial.print("\t");
        SerialArrayPrint(mEBUS_TABLE[cSEND_NAK], 2);
    }*/
    if (BusNumber == 0)
    {
        eBus0.write(mEBUS_TABLE[cSEND_NAK], 2);
        eBus0.flush();
    }

    if (BusNumber == 1)
    {
        eBus1.write(mEBUS_TABLE[cSEND_NAK], 2);
        eBus1.flush();
    }
}
/************************ Ende sendNak **********************************************************/

//*************************************************************************************************
// FunktionsName:   analyzeData
/// \details        -
/// \param[in]      DATA
/// \param[in]      DATA_SIZE
/// \return         retVal
//*************************************************************************************************
uint8_t analyzeData(uint8_t retData, uint8_t eBusState, uint8_t BusNumber)
{
    uint8_t locPos = 0;
    uint8_t valRet = retData;

    do
    {
        // Slave will Identifikation
        if (wrsolIdent(cIDENT_STRING, 5))
        {
            valRet = _RequestetIdent;
            break;
        }

        // Kommando gültig
        uint8_t retStat = analyzeCmd(eBusState, BusNumber);
        if ((retStat == _NotValid) || (retStat == _SlaveMaster) || (retStat ==_WaitAck) || (retStat ==_WaitNak))
        {
            valRet = retStat;
            break;
        }

        if (eBusState == _DataCycleResponse)
        {
            volatile uint8_t buffer[cSERIAL_BUFSIZE];
            memset((void*)buffer, '\0', cSERIAL_BUFSIZE);
            for (uint8_t i = 0; i < cSERIAL_BUFSIZE; i++)
            {
                // Antwort nach vorne, so das das Kommando verschwindet
                buffer[i] = eBuses[BusNumber].eBus_buffer[i + 9];
                if (buffer[i] == EBUS_SYN)
                    break;
            }

            memset((void*)eBuses[BusNumber].eBus_buffer, '\0', sizeof(eBuses[BusNumber].eBus_buffer));
            for (uint8_t i = 0; i < cSERIAL_BUFSIZE; i++)
                eBuses[BusNumber].eBus_buffer[i] = buffer[i];
        }

        for (int k = 0; k < cSERIAL_BUFSIZE; k++)
        {
            //*eBuses[BusNumber].mDebug ? */Serial.print(ebus_buffer[k], HEX);// : 0;
            if (eBuses[BusNumber].eBus_buffer[k] == EBUS_SYN)
            {
                locPos = k -1;
                break;
            }
//            eBuses[BusNumber].mDebug ? Serial.print(" ") : 0;
        }

        // Wenn an der Position ein 0x00 ist, kommt letztlich EBUS_ACK EBUS_SYN
        if(eBuses[BusNumber].eBus_buffer[locPos] == EBUS_ACK)
            locPos--;

        if(locPos >= cSERIAL_BUFSIZE)
            locPos = 0;

        if (eBusState == _SlaveIdentResponse)
            break;

        unsigned char* test = (unsigned char*)eBuses[BusNumber].eBus_buffer;
        uint8_t crc =  eb_calc_crc(test, locPos);
        if ((eBuses[BusNumber].eBus_buffer[locPos] != crc) || (locPos == 0))
        {
          //eBuses[0].mDebug ? Serialprint("\tLength: %u", locPos) : 0;
          //*eBuses[BusNumber].mDebug ? */Serial.print("\t\tCrc Failed:\t");// : 0;
          //*eBuses[BusNumber].mDebug ? */Serial.println(crc, HEX);// : 0;
            valRet = _CrcFailed;
            eBuses[BusNumber].eBus_out = false;
        }
    }
    while(false);

    return valRet;
}
/************************ Ende analyzeData **********************************************************/

//*************************************************************************************************
// FunktionsName:   analyzeData
/// \details        -
/// \param[in]      loc_eBusState
/// \return         retVal
//*************************************************************************************************
uint8_t analyzeCmd(uint8_t eBusState, uint8_t BusNumber)
{
    uint8_t retVal = _Valid;
    do
    {
        /* F7 9A 10 20 1 22 5A AA 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
         * F7 9A 10 20 1 22 5A AA 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
         * F7 9B 10 20 1 22 D5 AA 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
         * F7 9B 10 20 1 22 D5 AA 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
         * F7 9C 10 20 1 22 4E AA 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
         * F7 9C 10 20 1 22 4E AA 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
         * F7 9D 10 20 1 22 C1 AA 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
         * F7 9D 10 20 1 22 C1 AA 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
         */
        if ((eBuses[BusNumber].eBus_buffer[0] == WRSOL_MASTER) &&
                ((eBuses[BusNumber].eBus_buffer[1] == 0x9A) || (eBuses[BusNumber].eBus_buffer[1] == 0x9B) || (eBuses[BusNumber].eBus_buffer[1] == 0x9C) || (eBuses[BusNumber].eBus_buffer[1] == 0x9D)) &&
                (eBuses[BusNumber].eBus_buffer[2] == 0x10) && (eBuses[BusNumber].eBus_buffer[3] == 0x20) && (eBuses[BusNumber].eBus_buffer[4] == 0x1) && (eBuses[BusNumber].eBus_buffer[5] == 0x22)
            )
        {
            retVal = _SlaveMaster;
            break;
        }

        if ((eBuses[BusNumber].eBus_buffer[0] == EBUS_ACK) && (eBuses[BusNumber].eBus_buffer[1] == EBUS_SYN))
        {
            retVal = _WaitAck;
            break;
        }
        if ((eBuses[BusNumber].eBus_buffer[0] == EBUS_NAK) && (eBuses[BusNumber].eBus_buffer[1] == EBUS_SYN))
        {
            retVal = _WaitNak;
            break;
        }

        /* Wenn empfangenes Cmd nicht mit gesendeten übereinstimmt, bzw. Datenlänge zu kurz ist
         * AA AA 53 FC 9 0 3 8A F5 2 CC FF AA AA AA AA
         *       77 FC 9 0 3 8A F5 2 CC 0 2 3D 1 38 AA   End  */
        // Länge
        if (eBusState == _DataCycleResponse)
        {
            if (eBuses[BusNumber].eBus_pos < 14)
            {
                //SerialArrayPrint(DATA_TABLE[lastCmd], lastDataSize);
                //SerialArrayPrint((const uint8_t *)ebus_buffer, lastDataSize);
                retVal = _NotValid;
            }
        }

        // Kommando ist 8 Byte lang, dann kommmen ACK, Anzahl Bytes, LSB, MSB, CRC
        for (int k = 0; k < eBuses[BusNumber].mLastDataSize; k++)
        {
            if (eBuses[BusNumber].eBus_buffer[k] != mWRSOL_TABLE[eBuses[BusNumber].mLastCmd][k])
            {
                retVal = _NotValid;
                break;
            }
        }
    }
    while(false);

    return retVal;
}
/************************ Ende analyzeData **********************************************************/

//*************************************************************************************************
// FunktionsName:   readData
/// \details        -
/// \return         retVal
//*************************************************************************************************
uint8_t readData(uint8_t BusNumber)
{
    //static int syncNewLine = 0;
    uint8_t retVal = _NoData;
    bool bByteAvail = false;

    if (BusNumber == 0)
    {
        if (eBus0.available() > 0)
        {
            eBuses[BusNumber].eBus_Byte = eBus0.read();
            bByteAvail = true;
        }
    }
    else if (BusNumber == 1)
    {
        if (eBus1.available() > 0)
        {
            eBuses[BusNumber].eBus_Byte = eBus1.read();
            bByteAvail = true;
        }
    }
    else
    {
        bByteAvail = false;
    }

    if (bByteAvail)
    {
        if(eBuses[BusNumber].eBus_Byte == EBUS_SYN)
        {
            retVal = _Sync;
            /*syncNewLine++;
            if ((syncNewLine >= 40) && (eBuses[BusNumber].mDebug = true))
            {
                //eBuses[BusNumber].mDebug ? Serial.println("\tNewLine") : 0;
                syncNewLine = 0;
            }*/
            //eBuses[BusNumber].mDebug ? Serial.print("Sync") : 0;
        }

        // Daten
        if ((!eBuses[BusNumber].eBus_out) && (eBuses[BusNumber].eBus_Byte != EBUS_SYN))
        {
            memset((void*)eBuses[BusNumber].eBus_buffer, '\0', cSERIAL_BUFSIZE);
            eBuses[BusNumber].eBus_pos = 0;
            eBuses[BusNumber].eBus_out = true;
        }

        if(eBuses[BusNumber].eBus_out)
        {
            eBuses[BusNumber].eBus_buffer[eBuses[BusNumber].eBus_pos++] = eBuses[BusNumber].eBus_Byte;
            retVal = _BeginData;
//            /*eBuses[BusNumber].mDebug ? */Serial.print(eBus1_Byte, HEX);// : 0;
//            /*eBuses[BusNumber].mDebug ? */Serial.print(" ");// : 0;
        }

        if(eBuses[BusNumber].eBus_out && eBuses[BusNumber].eBus_Byte == EBUS_SYN)
        {
            retVal = _FinishedData;
            eBuses[BusNumber].eBus_out = false;
//            /*eBuses[BusNumber].mDebug ? */Serial.println("\tEnd");// : 0;
        }
    }
    return retVal;
}
/************************ Ende readData **********************************************************/

//*************************************************************************************************
// FunktionsName:   eBusTimedOut
/// \details        -
/// \return         -
//*************************************************************************************************
uint8_t eBusTimedOut(uint8_t BusNumber, uint8_t recoverState, uint8_t actState)
{
    uint8_t eBusState = actState;
    uint32_t dataRequestDelay = mDataRequestDelay_eBus0;

#ifdef EBUS2
    if (BusNumber == 1)
        dataRequestDelay = mDataRequestDelay_eBus1;
#endif
    if ((eBuses[BusNumber].mFailureCnt == 1) && (dataRequestDelay >= cDATA_DELAY))
    {
        eBusState = recoverState;
        eBuses[BusNumber].mFailureCnt = 0;
        eBuses[BusNumber].mDebug ? Serialprint("zurück zu eBusState: %u\n", eBusState) : 0;
    }
    return eBusState;
}
/************************ Ende eBusTimedOut **********************************************************/

//*************************************************************************************************
// FunktionsName:   eBus0Task
/// \details        -
/// \return         -
//*************************************************************************************************
int eBus0Task(boolean debug, eBusValues_st* eBusValues)
{
    eBuses[0].mDebug = debug;
    eBusStatus retStatus = eBus_Ok;

    int8_t retVal = readData(0);
    if (retVal == _FinishedData)
    {
        mRun_eBus0 = 0;

        // Auswerten
        retVal = analyzeData(retVal, eBus0State, 0);
        if (retVal == _RequestetIdent)
        {
            Serial.print("\nSende Ident");
            sendDataBus0(cIDENT_REQUEST, 12);
            return retStatus;
        }
        if (retVal ==_WaitAck)
        {
            //eBuses[0].mDebug ? Serialprint("_WaitAck eBusState: %u\n", eBus0State) : 0;
            return retStatus;
        }
        if (retVal ==_WaitNak)
        {
            //eBuses[0].mDebug ? Serialprint("_WaitNak eBusState: %u\n", eBus0State) : 0;
            return retStatus;
        }
        if (retVal == _SlaveMaster)
        {
            // Zum Recovern in den VerzögerungsState
            eBus0State = _DataCycleDelayed;
            mDataRequestDelay_eBus0 = cDATA_DELAY / 3;
            //Serial.print("\nSlaveMaster Cmd\n");
            //SerialArrayPrint((const uint8_t *)eBuses[0].eBus_buffer, cSERIAL_BUFSIZE);
            //eBuses[0].mDebug ? Serialprint("_SlaveMaster eBusState: %u\n", eBus0State) : 0;
            sendAck(0);
            return retStatus;
        }
        if (retVal == _NotValid)
        {
            //Serial.print(mWRSOL_PARAM[eBuses[0].mRequestDataPos]);
            //Serial.print("\tNot Valid\nSendCmd  ");
            //SerialArrayPrint(mWRSOL_TABLE[eBuses[0].mLastCmd], eBuses[0].mLastDataSize);
            //Serial.print("Received ");
            //SerialArrayPrint((const uint8_t *)eBuses[0].eBus_buffer, cSERIAL_BUFSIZE);
            sendNak(0);
            //Wird danach von Save erneut einmal gesendet, wenn wieder Fehler, dann gilt es als nicht übertragen
            eBuses[0].mFailureCnt++;
            mDataRequestDelay_eBus0 = 0;
        }
        if (retVal == _CrcFailed)
        {
            //Serial.print(mWRSOL_PARAM[eBuses[0].mRequestDataPos]);
            //Serial.print("\tCrc Failed\nSendCmd  ");
            //SerialArrayPrint(mWRSOL_TABLE[eBuses[0].mLastCmd], eBuses[0].mLastDataSize);
            //Serial.print("Received ");
            //SerialArrayPrint((const uint8_t *)eBuses[0].eBus_buffer, cSERIAL_BUFSIZE);
            sendNak(0);
            //Wird danach von Slave erneut einmal gesendet, wenn wieder Fehler, dann gilt es als nicht übertragen
            eBuses[0].mFailureCnt++;
            mDataRequestDelay_eBus0 = 0;
        }
        if (eBuses[0].mFailureCnt >= 2)
        {
            if ((eBus0State == _SelfIdentResponse) || (eBus0State == _SlaveIdentResponse))
                eBus0State--;

            if (eBus0State == _DataCycleResponse)
            {
                // Zum Recovern in den VerzögerungsState
                eBus0State = _DataCycleDelayed;
                mDataRequestDelay_eBus0 = cDATA_DELAY / 3;
            }
            eBuses[0].mFailureCnt = 0;
            //eBuses[0].mDebug ? Serialprint("failureCnt eBusState: %u\n", eBus0State) : 0;
        }
    }

    switch (eBus0State)
    {
        case _SelfIdent:
            if (retVal == _Sync)
            {
                sendDataBus0(cIDENTIFIKATION, 15);
                eBus0State = _SelfIdentResponse;
            }
        break;

        case _SelfIdentResponse:
            // Timeout, wenn der Slave nach dem NAK doch nichts mehr schickt
            eBus0State = eBusTimedOut(0, _SelfIdent, _SelfIdentResponse);
            if (retVal == _FinishedData)
            {
                //eBuses[0].mDebug ? Serial.print("SelfIdent Daten") : 0;
                eBus0State = _SlaveIdent;
            }
        break;

        case _SlaveIdent:
            if (retVal == _Sync)
            {
                sendDataBus0(cSLAVE_IDENT_REQUEST, 6);
                eBus0State = _SlaveIdentResponse;
            }
        break;

        case _SlaveIdentResponse:
            // Timeout, wenn der Slave nach dem NAK doch nichts mehr schickt
            eBus0State = eBusTimedOut(0, _SlaveIdent, _SlaveIdentResponse);
            if (retVal == _FinishedData)
            {
                //eBuses[0].mDebug ? Serial.print("SlaveIdent Daten") : 0;
                eBus0State = _DataCycle;
                sendAck(0);
            }
        break;

        case _DataCycle:
            if (retVal == _Sync)
            {
                //if (eBuses[0].mRequestDataPos == cWRSOL_DATA_START)
                //    Serial.print("\n");

                sendDataBus0(eBuses[0].mRequestDataPos, 8);
                eBus0State = _DataCycleResponse;
            }
        break;

        case _DataCycleResponse:
            // Timeout, wenn der Slave nach dem NAK doch nichts mehr schickt
            eBus0State = eBusTimedOut(0, _DataCycle, _DataCycleResponse);
            if (retVal == _FinishedData)
            {
                sendAck(0);

                // Werte brechnen
                int16_t iVal = (eBuses[0].eBus_buffer[3] << 8) + (eBuses[0].eBus_buffer[2]);
                float fVal = (float)iVal / 10;
                //eBuses[0].mDebug ? Serialprint("   iVal:   %u\n",iVal) :0 ;

                eBus0State = _DataCycle;
                if (eBuses[0].mRequestDataPos == cWRSOL_DATA_START)
                {
                    //SerialArrayPrint((const uint8_t *)ebus_buffer, SERIAL_BUFSIZE);
                    uint8_t DayOfWeek, Hour, Min;
                    wrSOL_HexToTime(iVal, &DayOfWeek, &Hour, &Min);
                    String timeStamp;
                    eb_day_to_str((unsigned char)DayOfWeek, &timeStamp);
                    timeStamp = timeStamp + "," + (String)Hour + ":" + (String)Min;

                    _Conf_Two_Register(eBuses[0].modBusAddr, (uint32_t)iVal);
                    //eBuses[0].mDebug ? Serial.print(timeStamp) : 0;
                    //eBuses[0].mDebug ? Serialprint("   iVal:   %u",iVal) :0 ;
                }
                else if ((eBuses[0].mRequestDataPos > cWRSOL_DATA_START) && (eBuses[0].mRequestDataPos <= cWRSOL_DATA_END))
                {
                    _Conf_Two_Register(eBuses[0].modBusAddr + eBuses[0].modBusOfs + (eBuses[0].mRequestDataPos - cWRSOL_DATA_START) * 2, (float)fVal);
                    switch (eBuses[0].mRequestDataPos)
                    {
                        case 5:
                            eBusValues->Tko = fVal;
                            break;
                        case 6:
                            eBusValues->Tfk = fVal;
                            break;
                        case 7:
                            eBusValues->Tso = fVal;
                            break;
                        case 8:
                            eBusValues->Tsu = fVal;
                            break;
                        case 9:
                            eBusValues->Tpu = fVal;
                            break;
                        default:
                        break;
                    }
                    //Serial.print(mWRSOL_PARAM[eBuses[0].mRequestDataPos]);
                    //Serial.print("\t");
                    //eBuses[0].mDebug ? Serial.println(fVal) : 0;
                    //eBuses[0].mDebug ? Serial.print("\t") : 0;
                    //eBuses[0].mDebug ? Serial.print(eBuses[0].modBusAddr + eBuses[0].modBusOfs + (eBuses[0].mRequestDataPos - cWRSOL_DATA_START) * 2) : 0;
                    //eBuses[0].mDebug ? Serial.println() : 0;
                }
                eBuses[0].mFailureCnt = 0;
                eBuses[0].mRequestDataPos++;

                if  (eBuses[0].mRequestDataPos > cWRSOL_DATA_END)
                {
                    eBus0State = _DataCycleDelayed;
                    mDataRequestDelay_eBus0 = 0;
                    retStatus = eBus_dataReady;
                }
            }
        break;

        case _DataCycleDelayed:
            //if (retVal == _FinishedData)
            //    SerialArrayPrint((const uint8_t *)eBuses[0].eBus_buffer, cSERIAL_BUFSIZE);

            /* Delay ellapsedmillis von 5s dann wieder von vorne */
            if (mDataRequestDelay_eBus0 >= cDATA_DELAY / 2)
            {
                eBuses[0].mRequestDataPos = cWRSOL_DATA_START;
                eBus0State = _DataCycle;
                eBuses[0].mFailureCnt = 0;
            }
        break;

        default:
        break;
    }

    if (mRun_eBus0 > cDATA_DELAY * 5)
    {
        retStatus = eBus_reInit;
    }
    else if (retStatus == eBus_Ok)
    {
        mRun_eBus0 = 0;
    }
    return retStatus;
}
/************************ Ende eBus0Task **********************************************************/

//*************************************************************************************************
// FunktionsName:   eBus1Task
/// \details        -
/// \return         -
//*************************************************************************************************
#ifdef EBUS2
int eBus1Task(boolean debug)
{
    eBusStatus retStatus = eBus_Ok;
    eBuses[1].mDebug = debug;

    int8_t retVal = readData(1);
    if (retVal == _FinishedData)
    {
        mRun_eBus1 = 0;
        SerialArrayPrint((const uint8_t *)eBuses[1].ebus_buffer, SERIAL_BUFSIZE);
    }

    if (mRun_eBus1 > cDATA_DELAY * 5)
    {
        retStatus = eBus_reInit;
    }
    else if (retStatus == eBus_Ok)
    {
        mRun_eBus0 = 0;
    }
    return retStatus;
}
#endif
/************************ Ende eBus1Task **********************************************************/

/************************ Ende eBusFunktionen.cpp **********************************************************/

