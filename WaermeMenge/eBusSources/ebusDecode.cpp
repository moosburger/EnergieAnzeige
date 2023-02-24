/*<  > ********************************************************************************/
/*!
*   \brief      -
*   \details    -
* Copyright (C) Roland Jax 2012-2013 <roland.jax@liwest.at>
* crc calculations from http://www.mikrocontroller.net/topic/75698
*
* This file is part of ebusd.
*
* ebusd is free software: you can redistribute it and/or modify
* it under the terms of the GNU General Public License as published by
* the Free Software Foundation, either version 3 of the License, or
* (at your option) any later version.
*
* ebusd is distributed in the hope that it will be useful,
* but WITHOUT ANY WARRANTY; without even the implied warranty of
* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
* GNU General Public License for more details.
*
* You should have received a copy of the GNU General Public License
* along with ebusd. If not, see http://www.gnu.org/licenses/.
*
*   \file       eBusDecode.cpp
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
* eBusDecode.cpp
*/
/**************************************************************************************************
* Includes
**************************************************************************************************/
#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include <math.h>
#include <Arduino.h>

#include "eBusFunction.h"

/**************************************************************************************************
* Defines
**************************************************************************************************/

/**************************************************************************************************
* Variablen
**************************************************************************************************/
const String days[] = {"Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"};

/**************************************************************************************************
* Funktionen
**************************************************************************************************/

//*************************************************************************************************
// FunktionsName:   wrSOL_HexToTime
/// \details        Der Zeitstempel wird vom Wochenbeginn aus berechnet. Montag(0) Wochenbeginn,
///                 Sonntag(6) Ende
/// \param[in]      timeStamp
/// \param[in]      *Zeit
/// \return         retVal
//*************************************************************************************************
void wrSOL_HexToTime(uint16_t timeStamp, uint8_t* DayOfWeek, uint8_t* Hour, uint8_t* Min)
{
    float weekH = (float)timeStamp / 60;
    *DayOfWeek = (uint8_t)(weekH / 24);

    float rTime = (float)(weekH - (*DayOfWeek * 24));
    *Hour = (uint8_t) rTime;

    float fMin = (rTime - *Hour) * 60;
    *Min = (uint8_t)fMin;

    float fSec = (fMin - *Min) * 60;
    uint8_t Sec = (uint8_t)fSec;

    if(Sec >= 30)
    {
        Sec = 0;
        *Min += 1;
    }
    if(*Min >= 60)
    {
        *Min = *Min - 60;
        *Hour += 1;
    }
}
/************************ Ende wrSOL_HexToTime ***************************************************/

//*************************************************************************************************
    /**
     * @brief calculate integer value of given hex byte
     * @param [in] *buf hex byte
     * @return integer value | -1 if given byte is no hex value
     */
//*************************************************************************************************
int eb_htoi(const char *buf)
{
    int ret;
    ret = -1;
    
    if (isxdigit(*buf)) {
        if (isalpha(*buf))
            ret = 55;
        else
            ret = 48;
            
        ret = toupper(*buf) - ret;
    }

    return ret;
}
/************************ Ende eb_htoi **********************************************************/

//*************************************************************************************************
    /**
     * @brief print received results in a specific format
     * @param [out] *buf pointer to a byte array
     * @param [out] *buflen length of byte array
     * @return none
     */
//*************************************************************************************************
/*void eb_esc(unsigned char *buf, int *buflen)
{
    unsigned char tmp[SERIAL_BUFSIZE];
    int tmplen, i;

    memset(tmp, '\0', sizeof(tmp));
    i = 0;
    tmplen = 0;
    
    while (i < *buflen) {
        
        if (buf[i] == EBUS_SYN) {
            tmp[tmplen] = EBUS_SYN_ESC_A9;
            tmplen++;
            tmp[tmplen] = EBUS_SYN_ESC_01;
            tmplen++;
        } else if (buf[i] == EBUS_SYN_ESC_A9) {
            tmp[tmplen] = EBUS_SYN_ESC_A9;
            tmplen++;
            tmp[tmplen] = EBUS_SYN_ESC_00;
            tmplen++;
        } else {
            tmp[tmplen] = buf[i];
            tmplen++;
        }
        
        i++;
    }

    memset(buf, '\0', sizeof(*buf));
    for (i = 0; i < tmplen; i++)
        buf[i] = tmp[i];

    *buflen = tmplen;
}*/
/************************ Ende eb_esc **********************************************************/

//*************************************************************************************************
    /**
     * @brief print received results in a specific format
     * @param [out] *buf pointer to a byte array
     * @param [out] *buflen length of byte array
     * @return none
     */
//*************************************************************************************************
/*void eb_unesc(unsigned char *buf, int *buflen)
{
    unsigned char tmp[SERIAL_BUFSIZE];
    int tmplen, i, found;

    memset(tmp, '\0', sizeof(tmp));
    i = 0;
    tmplen = 0;
    found = 0;
    
    while (i < *buflen) {
        
        if (buf[i] == EBUS_SYN_ESC_A9) {
            found = 1;
        } else if (found == 1) {
            if (buf[i] == EBUS_SYN_ESC_01) {
                tmp[tmplen] = EBUS_SYN;
                tmplen++;
            } else {
                tmp[tmplen] = EBUS_SYN_ESC_A9;
                tmplen++;
            }
            
            found = 0;
        } else {
            tmp[tmplen] = buf[i];
            tmplen++;
        }
        
        i++;
    }

    memset(buf, '\0', sizeof(*buf));
    for (i = 0; i < tmplen; i++)
        buf[i] = tmp[i];

    *buflen = tmplen;
}*/
/************************ Ende eb_unesc **********************************************************/

//*************************************************************************************************
    /**
     * @brief convert hex bytes to day
     * @param [in] day hex byte
     * @param [out] *tgt pointer to day string xxx
     * @return 0 OK | -1 values out of range
     */
//*************************************************************************************************
int eb_day_to_str(unsigned char day, String *tgt)
{
    int dd = (int)day;
    
    if (day >= 0x00 && day <= 0x06)
    {
        eb_bcd_to_int(day, &dd);
        *tgt = days[day];
    } else {
        return -1;
    }
    
    return 0;
}
/************************ Ende eb_day_to_str **********************************************************/

//*************************************************************************************************
    /**
     * @brief convert hex bytes to date
     * @param [in] dd day hex byte
     * @param [in] mm month hex byte
     * @param [in] yy year hex byte
     * @param [out] *tgt pointer to date string dd.mm.yyyy
     * @return 0 OK | -1 values out of range
     */
//*************************************************************************************************
int eb_dat_to_str(unsigned char dd, unsigned char mm, unsigned char yy, char *tgt)
{
    if (dd >= 0x00 && dd <= 0x1F &&
        mm >= 0x00 && mm <= 0x0C &&
        yy >= 0x00 && yy <= 0x63 )
        sprintf(tgt, "%02d.%02d.%04d", dd, mm, yy + 2000);
    else
        return -1;

    return 0;
}
/************************ Ende eb_dat_to_str **********************************************************/

//*************************************************************************************************
    /**
     * @brief convert char date string to hex
     * @param [in] dd day int value
     * @param [in] mm month int value
     * @param [in] yy year int value
     * @param [out] *tgt pointer to hex
     * @return 0 OK | -1 values out of range
     */
//*************************************************************************************************
int eb_str_to_dat(int dd, int mm, int yy, unsigned char *tgt)
{
    if (yy > 2000)
        yy -= 2000;

    if (dd >= 0 && dd <= 31 &&
        mm >= 0 && mm <= 12 &&
        yy >= 0 && yy <= 99 )
        sprintf((char *) tgt, "%02x%02x%02x", dd, mm, yy);

    else
        return -1;

    return 0;
}
/************************ Ende eb_str_to_dat **********************************************************/

//*************************************************************************************************
    /**
     * @brief convert hex bytes to date
     * @param [in] hh hour hex byte
     * @param [in] mm minute hex byte
     * @param [in] ss second hex byte
     * @param [out] *tgt pointer to date string hh:mm:ss
     * @return 0 OK | -1 values out of range
     */
//*************************************************************************************************
int eb_tim_to_str(unsigned char hh, unsigned char mm, unsigned char ss, char *tgt)
{
    if (hh >= 0x00 && hh <= 0x17 &&
        mm >= 0x00 && mm <= 0x3B &&
        ss >= 0x00 && ss <= 0x3B )
        sprintf(tgt, "%02d:%02d:%02d", hh, mm, ss);
    else
        return -1;

    return 0;
}
/************************ Ende eb_tim_to_str **********************************************************/

//*************************************************************************************************
    /**
     * @brief convert char time string to hex
     * @param [in] hh hour int value
     * @param [in] mm minute int value
     * @param [in] ss second int value
     * @param [out] *tgt pointer to hex
     * @return 0 OK | -1 values out of range
     */
//*************************************************************************************************
int eb_str_to_tim(int hh, int mm, int ss, unsigned char *tgt)
{

    if (hh >= 0 && hh <= 23 &&
        mm >= 0 && mm <= 59 &&
        ss >= 0 && ss <= 59 )
        sprintf((char *) tgt, "%02x%02x%02x", hh, mm, ss);

    else
        return -1;

    return 0;
}
/************************ Ende eb_str_to_tim **********************************************************/

//*************************************************************************************************
    /**
     * @brief convert bcd hex byte to int
     * @param [in] src bcd hex byte
     * @param [out] *tgt pointer to int value
     * @return 0 substitute value | 1 positive value
     */
//*************************************************************************************************
int eb_bcd_to_int(unsigned char src, int *tgt)
{
    if ((src & 0x0F) > 0x09 || ((src >> 4) & 0x0F) > 0x09) {
        *tgt = (int) (0xFF);
        return 0;
    } else {
        *tgt = (int) ( ( ((src & 0xF0) >> 4) * 10) + (src & 0x0F) );
        return 1;
    }
}
/************************ Ende eb_bcd_to_int **********************************************************/

//*************************************************************************************************
    /**
     * @brief convert int to bcd hex byte
     * @param [in] src int value
     * @param [out] *tgt pointer to hex byte
     * @return 0 substitute value | 1 positive value
     */
//*************************************************************************************************
int eb_int_to_bcd(int src, unsigned char *tgt)
{
    if (src > 99) {
        *tgt = (unsigned char) (0xFF);
        return 0;
    } else {
        *tgt = (unsigned char) ( ((src / 10) << 4) | (src % 10) );
        return 1;
    }
}
/************************ Ende eb_int_to_bcd **********************************************************/

//*************************************************************************************************
    /**
     * @brief convert data1b hex byte to int
     * @param [in] src data1b hex byte
     * @param [out] *tgt pointer to int value
     * @return 0 substitute value | 1 positive value | -1 negative value
     */
//*************************************************************************************************
int eb_d1b_to_int(unsigned char src, int *tgt)
{
    if ((src & 0x80) == 0x80) {
        *tgt = (int) (- ( ((unsigned char) (~ src)) + 1) );

        if (*tgt  == -0x80)
            return 0;
        else
            return -1;

    } else {
        *tgt = (int) (src);
        return 1;
    }
}
/************************ Ende eb_d1b_to_int **********************************************************/

//*************************************************************************************************
    /**
     * @brief convert int to data1b hex byte
     * @param [in] src int value
     * @param [out] *tgt pointer to data1b hex byte
     * @return 0 substitute value | 1 positive value | -1 negative value
     */
//*************************************************************************************************
int eb_int_to_d1b(int src, unsigned char *tgt)
{
    if (src < -127 || src > 127) {
        *tgt = (unsigned char) (0x80);
        return 0;
    } else {
        if (src >= 0) {
            *tgt = (unsigned char) (src);
            return 1;
        } else {
            *tgt = (unsigned char) (- (~ (src - 1) ) );
            return -1;
        }
    }
}
/************************ Ende eb_int_to_d1b **********************************************************/

//*************************************************************************************************
    /**
     * @brief convert data1c hex byte to float
     * @param [in] src data1c hex byte
     * @param [out] *tgt pointer to float value
     * @return 0 substitute value | 1 positive value | -1 negative value
     */
//*************************************************************************************************
int eb_d1c_to_float(unsigned char src, float *tgt)
{
    if (src > 0xC8) {
        *tgt = (float) (0xFF);
        return 0;
    } else {
        *tgt = (float) (src / 2.0);
        return 1;
    }
}
/************************ Ende eb_d1c_to_float **********************************************************/

//*************************************************************************************************
    /**
     * @brief convert float to data1c hex byte
     * @param [in] src float value
     * @param [out] *tgt pointer to data1c hex byte
     * @return 0 substitute value | 1 positive value | -1 negative value
     */
//*************************************************************************************************
int eb_float_to_d1c(float src, unsigned char *tgt)
{
    if (src < 0.0 || src > 100.0) {
        *tgt = (unsigned char) (0xFF);
        return 0;
    } else {
        *tgt = (unsigned char) (src * 2.0);
        return 1;
    }
}
/************************ Ende eb_float_to_d1c **********************************************************/

//*************************************************************************************************
    /**
     * @brief convert data2b hex bytes to float
     * @param [in] src_lsb least significant data2b hex byte
     * @param [in] src_msb most significant data2b hex byte
     * @param [out] *tgt pointer to float value
     * @return 0 substitute value | 1 positive value | -1 negative value
     */
//*************************************************************************************************
int eb_d2b_to_float(unsigned char src_lsb, unsigned char src_msb, float *tgt)
{
    if ((src_msb & 0x80) == 0x80) {
        *tgt = (float)
            (- ( ((unsigned char) (~ src_msb)) +
            (  ( ((unsigned char) (~ src_lsb)) + 1) / 256.0) ) );

        if (src_msb  == 0x80 && src_lsb == 0x00)
            return 0;
        else
            return -1;

    } else {
        *tgt = (float) (src_msb + (src_lsb / 256.0));
        return 1;
    }
}
/************************ Ende eb_d2b_to_float **********************************************************/

//*************************************************************************************************
    /**
     * @brief convert float to data2b hex bytes
     * @param [in] src float value
     * @param [out] *tgt_lsb pointer to least significant data2b hex byte
     * @param [out] *tgt_msb pointer to most significant data2b hex byte
     * @return 0 substitute value | 1 positive value | -1 negative value
     */
//*************************************************************************************************
int eb_float_to_d2b(float src, unsigned char *tgt_lsb, unsigned char *tgt_msb)
{
    if (src < -127.999 || src > 127.999) {
        *tgt_msb = (unsigned char) (0x80);
        *tgt_lsb = (unsigned char) (0x00);
        return 0;
    } else {
        *tgt_lsb = (unsigned char) ((src - ((unsigned char) src)) * 256.0);

        if (src < 0.0 && *tgt_lsb != 0x00)
            *tgt_msb = (unsigned char) (src - 1);
        else
            *tgt_msb = (unsigned char) (src);

        if (src >= 0.0)
            return 1;
        else
            return -1;

    }
}
/************************ Ende eb_float_to_d2b **********************************************************/

//*************************************************************************************************
    /**
     * @brief convert data2c hex bytes to float
     * @param [in] src_lsb least significant data2c hex byte
     * @param [in] src_msb most significant data2c hex byte
     * @param [out] *tgt pointer to float value
     * @return 0 substitute value | 1 positive value | -1 negative value
     */
//*************************************************************************************************
int eb_d2c_to_float(unsigned char src_lsb, unsigned char src_msb, float *tgt)
{
    if ((src_msb & 0x80) == 0x80) {
        *tgt = (float)
        (- ( ( ( ((unsigned char) (~ src_msb)) * 16.0) ) +
             ( ( ((unsigned char) (~ src_lsb)) & 0xF0) >> 4) +
           ( ( ( ((unsigned char) (~ src_lsb)) & 0x0F) +1 ) / 16.0) ) );

        if (src_msb  == 0x80 && src_lsb == 0x00)
            return 0;
        else
            return -1;

    } else {
        *tgt = (float) ( (src_msb * 16.0) + ((src_lsb & 0xF0) >> 4) +
                        ((src_lsb & 0x0F) / 16.0) );
        return 1;
    }
}
/************************ Ende eb_d2c_to_float **********************************************************/

//*************************************************************************************************
    /**
     * @brief convert float to data2c hex bytes
     * @param [in] src float value
     * @param [out] *tgt_lsb pointer to least significant data2c hex byte
     * @param [out] *tgt_msb pointer to most significant data2c hex byte
     * @return 0 substitute value | 1 positive value | -1 negative value
     */
//*************************************************************************************************
int eb_float_to_d2c(float src, unsigned char *tgt_lsb, unsigned char *tgt_msb)
{
    if (src < -2047.999 || src > 2047.999) {
        *tgt_msb = (unsigned char) (0x80);
        *tgt_lsb = (unsigned char) (0x00);
        return 0;
    } else {
        *tgt_lsb =
          ( ((unsigned char) ( ((unsigned char) src) % 16) << 4) +
            ((unsigned char) ( (src - ((unsigned char) src)) * 16.0)) );

        if (src < 0.0 && *tgt_lsb != 0x00)
            *tgt_msb = (unsigned char) ((src / 16.0) - 1);
        else
            *tgt_msb = (unsigned char) (src / 16.0);

        if (src >= 0.0)
            return 1;
        else
            return -1;
    }
}
/************************ Ende eb_float_to_d2c **********************************************************/

//*************************************************************************************************
    /**
     * @brief calculate crc of hex byte
     * @param [in] byte byte to calculate
     * @param [in] init_crc start value for calculation
     * @return new calculated crc byte from byte and init crc byte
     */
//*************************************************************************************************
unsigned char eb_calc_crc_byte(unsigned char byte, unsigned char init_crc)
{
    unsigned char crc, polynom;
    int i;

    crc = init_crc;

    for (i = 0; i < 8; i++) {

        if (crc & 0x80)
            polynom = (unsigned char) 0x9B;
        else
            polynom = (unsigned char) 0;

        crc = (unsigned char) ((crc & ~0x80) << 1);

        if (byte & 0x80)
            crc = (unsigned char) (crc | 1);

        crc = (unsigned char) (crc ^ polynom);
        byte = (unsigned char) (byte << 1);
    }
    
    return crc;
}
/************************ Ende eb_calc_crc_byte **********************************************************/

//*************************************************************************************************
    /**
     * @brief calculate crc of given hex array
     *
     * \li crc calculation "CRC-8-WCDMA" with Polynom "x^8+x^7+x^4+x^3+x+1"
     * \li crc calculations by http://www.mikrocontroller.net/topic/75698
     *
     * @param [in] *bytes pointer to a byte array
     * @param [in] size length of given bytes
     * @return calculated crc byte
     */
//*************************************************************************************************
unsigned char eb_calc_crc(const unsigned char *buf, int buflen)
{
    int i;
    unsigned char crc = 0;

    for (i = 0 ; i < buflen ; i++, buf++)
        crc = eb_calc_crc_byte(*buf, crc);

    return crc;
}
/************************ Ende eb_calc_crc **********************************************************/

/************************ Ende eBus-decode.cpp **********************************************************/

