/*
 * Copyright (c) 2021 Arm Limited and Contributors. All rights reserved.
 *
 * SPDX-License-Identifier: BSD-3-Clause
 * 
 */

#include <stdint.h>
#include <string.h>

#include "pico.h"
#include "pico/unique_id.h"
#include "hardware/sync.h"

#include "board.h"
#include "board-config.h"

#include "sx126x-board.h"

#include "hardware/spi.h"
#include "rtc-board.h"

extern SX126x_t SX126x;

void BoardInitMcu( void )
{
    
    RtcInit();

    Gpio_t gpio_busy;
    Gpio_t gpio_dio1;
    Gpio_t gpio_reset;
    Gpio_t gpio_nss;

    Spi_t spi1_t;

    gpio_busy.pin = RADIO_BUSY;
    gpio_dio1.pin = RADIO_DIO_1;
    gpio_reset.pin = RADIO_RESET;
    gpio_nss.pin = RADIO_NSS;
    spi1_t.Nss = gpio_nss;
// raspberry pi pico spi1
    spi1_t.SpiId = SPI_2;

    SX126x.BUSY = gpio_busy;
    SX126x.DIO1 = gpio_dio1;
    SX126x.Reset = gpio_reset;
    SX126x.Spi = spi1_t;
    SpiInit( &SX126x.Spi, SPI_2, RADIO_MOSI, RADIO_MISO, RADIO_SCLK, NC );
    SX126xIoInit();
}

void BoardInitPeriph( void )
{
    
}

void BoardLowPowerHandler( void )
{
    __wfi();
}

uint8_t BoardGetBatteryLevel( void )
{
    return 0;
}

uint32_t BoardGetRandomSeed( void )
{
    uint8_t id[8];

    BoardGetUniqueId(id);

    return (id[3] << 24) | (id[2] << 16) | (id[1] << 1) | id[0];
}

void BoardGetUniqueId( uint8_t *id )
{
    pico_unique_board_id_t board_id;

    pico_get_unique_board_id(&board_id);

    memcpy(id, board_id.id, 8);
}

void BoardCriticalSectionBegin( uint32_t *mask )
{
    *mask = save_and_disable_interrupts();
}

void BoardCriticalSectionEnd( uint32_t *mask )
{
    restore_interrupts(*mask);
}

void BoardResetMcu( void )
{
}
