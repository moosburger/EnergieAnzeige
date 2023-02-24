/*<  > ********************************************************************************/
/*!
*	\brief      -
*	\details    -
*
*	\file		modBusFunction.cpp
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
* modBusFunction.cpp
*/

/**************************************************************************************************
* Includes
**************************************************************************************************/
//#include "main.h"
#include "common.h"
#include "modBusFunction.h"

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
// FunktionsName:   _Conf_One_Register
/// \details        Werte so runden und dann Skalieren, daß sie in einen 16Bit wert passen. Zweites Register hält die Skalierung
/// \param[in]      addr
/// \param[in]      data
/// \param[in]      scaleAddr
/// \return         -
//*************************************************************************************************
void _Conf_One_Register(uint16_t addr, uint16_t data, uint8_t digits, uint16_t scaleAddr)
{
    convert1 toScale;
    convert1 to16;

    String strData(data);
    int iCnt = strData.length();

    toScale._s16(digits - iCnt);
    float factor = pow(10, toScale._s16());
    float tmpF = (data*factor);
    to16._s16((int16_t)(round(tmpF)));
    // Für die Skalierung und Rückrechnung auf Client Seite nun *-1
    toScale._s16(toScale._s16() * -1);

    mb->Reg(HREG(addr), to16._u16());
    if (scaleAddr > 0)
        mb->Reg(HREG(scaleAddr), toScale._u16());
}
void _Conf_One_Register(uint16_t addr, uint32_t data, uint8_t digits, uint16_t scaleAddr)
{
    convert1 toScale;
    convert1 to16;

    String strData(data);
    int iCnt = strData.length();

    toScale._s16(digits - iCnt);
    float factor = pow(10, toScale._s16());
    float tmpF = (data*factor);
    to16._s16((int16_t)(round(tmpF)));
    // Für die Skalierung und Rückrechnung auf Client Seite nun *-1
    toScale._s16(toScale._s16() * -1);

    mb->Reg(HREG(addr), to16._u16());
    if (scaleAddr > 0)
        mb->Reg(HREG(scaleAddr), toScale._u16());
}
void _Conf_One_Register(uint16_t addr, int32_t data, uint8_t digits, uint16_t scaleAddr)
{
    convert1 toScale;
    convert1 to16;

    String strData(data);
    int iCnt = strData.length();
    if(data < 0)
        digits += 1;

    toScale._s16(digits - iCnt);
    float factor = pow(10, toScale._s16());
    float tmpF = (data*factor);
    to16._s16((int16_t)(round(tmpF)));
    // Für die Skalierung und Rückrechnung auf Client Seite nun *-1
    toScale._s16(toScale._s16() * -1);

    mb->Reg(HREG(addr), to16._u16());
    if (scaleAddr > 0)
        mb->Reg(HREG(scaleAddr), toScale._u16());
}
void _Conf_One_Register(uint16_t addr, float data, uint8_t digits, uint16_t scaleAddr)
{
    convert1 toScale;
    convert1 to16;

    int32_t _data = int32_t(round(data));
    String strData(_data);
    int iCnt = strData.length();
    if(data < 0)
        digits += 1;

    toScale._s16(digits - iCnt);
    float factor = pow(10, toScale._s16());
    float tmpF = (_data*factor);
    to16._s16((int16_t)(round(tmpF)));
    // Für die Skalierung und Rückrechnung auf Client Seite nun *-1
    toScale._s16(toScale._s16() * -1);

    mb->Reg(HREG(addr), to16._u16());
    if (scaleAddr > 0)
        mb->Reg(HREG(scaleAddr), toScale._u16());
}
/************************ Ende _Conf_One_Register **********************************************************/

//*************************************************************************************************
// FunktionsName:   _Conf_Two_Register
/// \details        32Bit Wert in 2 16Bit Register schieben
/// \param[in]      addr
/// \param[in]      data
/// \return         -
//*************************************************************************************************
void _Conf_Two_Register(uint16_t addr, uint32_t data)
{
    convert2 to32(data);
    mb->Reg(HREG(addr++), to32.l());
    mb->Reg(HREG(addr), to32.h());
}
void _Conf_Two_Register(uint16_t addr, int32_t data)
{
    convert2 to32(data);
    mb->Reg(HREG(addr++), to32.l());
    mb->Reg(HREG(addr), to32.h());
}
void _Conf_Two_Register(uint16_t addr, float data)
{
    convert2 to32(data);
    mb->Reg(HREG(addr++), to32.l());
    mb->Reg(HREG(addr), to32.h());
}
/************************ Ende _Conf_Two_Register **********************************************************/

//*************************************************************************************************
// FunktionsName:   _Conf_Four_Register
/// \details        64Bit Wert in 4 16Bit Register schieben
/// \param[in]      addr
/// \param[in]      data
/// \return         -
//*************************************************************************************************
void _Conf_Four_Register(uint16_t addr, uint64_t data)
{
    convert4 to64(data);
    mb->Reg(HREG(addr++), to64.ll());
    mb->Reg(HREG(addr++), to64.lh());
    mb->Reg(HREG(addr++), to64.hl());
    mb->Reg(HREG(addr), to64.hh());
}
void _Conf_Four_Register(uint16_t addr, int64_t data)
{
    convert4 to64(data);
    mb->Reg(HREG(addr++), to64.ll());
    mb->Reg(HREG(addr++), to64.lh());
    mb->Reg(HREG(addr++), to64.hl());
    mb->Reg(HREG(addr), to64.hh());
}
/************************ Ende _Conf_One_Register **********************************************************/

//*************************************************************************************************
// FunktionsName:   _ConfCharToInt
/// \details        Chars im Strings in jeweils zweier Gruppen in ein 16Bit Register schreiben
/// \param[in]      addr
/// \param[in]      data
/// \return         -
//*************************************************************************************************
void _ConfCharToInt(uint16_t addr, String data)
{    convertChar toChar;
    bool second = false;
    for (uint8_t n = 0; n < data.length(); n++)
    {
        if (!second)
        {
            toChar.l(data.charAt(n));
            second = true;
        }
        else
        {
            toChar.h(data.charAt(n));
            second = false;
            mb->Reg(HREG(addr++), toChar._u16());
        }
    }
    if (second)
    {
        toChar.h(0);
        second = false;
        mb->Reg(HREG(addr++), toChar._u16());
    }
}

/************************ Ende _ConfCharToInt **********************************************************/

/************************ Ende modBusFunktionen.cpp **********************************************************/

