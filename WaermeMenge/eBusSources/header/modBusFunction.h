/*<  > ********************************************************************************/
/*!
*	\brief      Die Headerdatei zu modBusFunction.cpp
*	\details    -
*
*	\file       modBusFunction.h
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
* modBusFunction.h
*/

#ifndef _MODBUSFUNCTION_H_
#define _MODBUSFUNCTION_H_

/**************************************************************************************************
* Includes
**************************************************************************************************/
//#include "main.h"
#include <ModbusEthernet.h>

/**************************************************************************************************
* Defines
**************************************************************************************************/

/**************************************************************************************************
* Variablen
**************************************************************************************************/

//*************************************************************************************************
// KlassenName: convertChar
/// \details    Two bytes (16 bit) based types
//*************************************************************************************************
class convertChar {
private:
    union {
        struct {
            uint8_t h;
            uint8_t l;
        } _x2u8Struct;
        uint16_t _u16;
        int16_t _s16;
    } _convertChar;
public:
    // Constructors
    convertChar() {
        _convertChar._u16 = 0;
    }
    convertChar(uint16_t val) {
        _convertChar._u16 = val;
    }
    convertChar(int16_t val) {
        _convertChar._s16 = val;
    }
    convertChar(uint8_t val_h, uint8_t val_l) {
        _convertChar._x2u8Struct.h = val_h;
        _convertChar._x2u8Struct.l = val_l;
    }
    virtual ~convertChar(){};

    void l (uint8_t val_l) {
        _convertChar._x2u8Struct.l = val_l;
    }
    void h (uint8_t val_h) {
        _convertChar._x2u8Struct.h = val_h;
    }
    void _u16 (uint16_t val) {
        _convertChar._u16 = val;
    }
    void _s16 (int16_t val) {
        _convertChar._s16 = val;
    }
    uint16_t _u16 () {
        return _convertChar._u16;
    }
    int16_t _s16 () {
        return _convertChar._s16;
    }
    uint8_t l () {
        return _convertChar._x2u8Struct.l;
    }
    uint8_t h () {
        return _convertChar._x2u8Struct.h;
    }
};
/************************ Ende convertChar *************************************************/

//*************************************************************************************************
// KlassenName: convert1
/// \details    Single register (16 bit) based types
//*************************************************************************************************

class convert1 {
private:
    union {
        uint16_t _u16;
        int16_t _s16;
    } _convert1;
public:
    // Constructors
    convert1() {
        _convert1._u16 = 0;
    }
    convert1(uint16_t val) {
        _convert1._u16 = val;
    }
    convert1(int16_t val) {
        _convert1._s16 = val;
    }
    virtual ~convert1(){};

    void _u16 (uint16_t val) {
        _convert1._u16 = val;
    }
    void _s16 (int16_t val) {
        _convert1._s16 = val;
    }
    uint16_t _u16 () {
        return _convert1._u16;
    }
    int16_t _s16 () {
        return _convert1._s16;
    }
};
/************************ Ende convert1 *************************************************/

//*************************************************************************************************
// KlassenName: convert2
/// \details    Two register (32 bit) based types
//*************************************************************************************************
class convert2 {
private:
    union {
        float _float;
        int32_t _sint32;
        uint32_t _uint32;
        struct {
            uint16_t h;
            uint16_t l;
        } _x2u16Struct;
    } _convert2;
public:
    // Constructors
    convert2() {
        _convert2._uint32 = 0;
    }
    convert2(float val) {
        _convert2._float = val;
    }
    convert2(uint32_t val) {
        _convert2._uint32 = val;
    }
    convert2(int32_t val) {
        _convert2._sint32 = val;
    }
    convert2(uint16_t val_h, uint16_t val_l) {
        _convert2._x2u16Struct.h = val_h;
        _convert2._x2u16Struct.l = val_l;
    }
    virtual ~convert2(){};

    void _float (float val) {
        _convert2._float = val;
    }
    void _uint32 (uint32_t val) {
        _convert2._uint32 = val;
    }
    void _sint32 (int32_t val) {
        _convert2._sint32 = val;
    }
    void l (uint16_t val) {
        _convert2._x2u16Struct.l = val;
    }
    void h (uint16_t val) {
        _convert2._x2u16Struct.h = val;
    }

    float _float () {
        return _convert2._float;
    }
    uint32_t _uint32 () {
        return _convert2._uint32;
    }
    int32_t _sint32 () {
        return _convert2._sint32;
    }
    uint16_t l () {
        return _convert2._x2u16Struct.l;
    }
    uint16_t h () {
        return _convert2._x2u16Struct.h;
    }
};
/************************ Ende convert2 *************************************************/

//*************************************************************************************************
// KlassenName: convert4
/// \details    Four register (64 bit) based types
//*************************************************************************************************
class convert4 {
private:
    union {
        struct {
            uint16_t hh;
            uint16_t hl;
            uint16_t lh;
            uint16_t ll;
        } _x4u16Struct;
        int64_t _sint64;
        uint64_t _uint64;
    } _convert4;
public:
    // Constructors
    convert4() {
        _convert4._uint64 = 0;
    }
    convert4(uint64_t val) {
        _convert4._uint64 = val;
    }
    convert4(int64_t val) {
        _convert4._sint64 = val;
    }
    convert4(uint16_t val_hh, uint16_t val_hl, uint16_t val_lh, uint16_t val_ll) {
        _convert4._x4u16Struct.hh = val_hh;
        _convert4._x4u16Struct.hl = val_hl;
        _convert4._x4u16Struct.lh = val_lh;
        _convert4._x4u16Struct.ll = val_ll;
    }
    virtual ~convert4(){};

    void _uint46 (uint64_t val) {
        _convert4._uint64= val;
    }
    void _sint64 (int64_t val) {
        _convert4._sint64= val;
    }
    void hh (uint16_t val) {
        _convert4._x4u16Struct.hh= val;
    }
    void hl (uint16_t val) {
        _convert4._x4u16Struct.hl= val;
    }
    void lh (uint16_t val) {
        _convert4._x4u16Struct.lh= val;
    }
    void ll (uint16_t val) {
        _convert4._x4u16Struct.ll= val;
    }

    uint64_t _uint46 () {
        return _convert4._uint64;
    }
    int64_t _sint64 () {
        return _convert4._sint64;
    }
    uint16_t hh () {
        return _convert4._x4u16Struct.hh;
    }
    uint16_t hl () {
        return _convert4._x4u16Struct.hl;
    }
    uint16_t lh () {
        return _convert4._x4u16Struct.lh;
    }
    uint16_t ll () {
        return _convert4._x4u16Struct.ll;
    }
};
/************************ Ende convert4 *************************************************/

//*************************************************************************************************
// Funktionen: -
/// \details    -
//*************************************************************************************************
void _Conf_One_Register(uint16_t addr, uint16_t data, uint8_t digits, uint16_t scaleAddr = 0);
void _Conf_One_Register(uint16_t addr, uint32_t data, uint8_t digits, uint16_t scaleAddr = 0);
void _Conf_One_Register(uint16_t addr, int32_t data, uint8_t digits, uint16_t scaleAddr = 0);
void _Conf_One_Register(uint16_t addr, float data, uint8_t digits, uint16_t scaleAddr = 0);

void _Conf_Two_Register(uint16_t addr, uint32_t data);
void _Conf_Two_Register(uint16_t addr, int32_t data);
void _Conf_Two_Register(uint16_t addr, float data);

void _Conf_Four_Register(uint16_t addr, uint64_t data);
void _Conf_Four_Register(uint16_t addr, int64_t data);

void _ConfCharToInt(uint16_t addr, String data);

/************************ Ende Funktionen *************************************************/
#endif /* _MODBUSFUNCTION_H_ */
/************************ Ende modBusFunction.h ******************************************************/

