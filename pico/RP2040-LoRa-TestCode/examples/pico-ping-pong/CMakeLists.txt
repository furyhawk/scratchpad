cmake_minimum_required(VERSION 3.12)

#---------------------------------------------------------------------------------------
# Options
#---------------------------------------------------------------------------------------

# Allow selection of region
option(REGION_EU868 "Region EU868" OFF)
option(REGION_US915 "Region US915" OFF)
option(REGION_CN779 "Region CN779" OFF)
option(REGION_EU433 "Region EU433" ON)
option(REGION_AU915 "Region AU915" OFF)
option(REGION_AS923 "Region AS923" OFF)
option(REGION_CN470 "Region CN470" OFF)
option(REGION_KR920 "Region KR920" OFF)
option(REGION_IN865 "Region IN865" OFF)
option(REGION_RU864 "Region RU864" OFF)
set(REGION_LIST REGION_EU868 REGION_US915 REGION_CN779 REGION_EU433 REGION_AU915 REGION_AS923 REGION_CN470 REGION_KR920 REGION_IN865 REGION_RU864)

# Allow switching of modulation
set(MODULATION_LIST LORA FSK)
set(MODULATION LORA CACHE STRING "Default modulation is LoRa")
set_property(CACHE MODULATION PROPERTY STRINGS ${MODEM_LIST})

# Loops through all regions and add compile time definitions for the enabled ones.
foreach( REGION ${REGION_LIST} )
    if(${REGION})
        target_compile_definitions(${PROJECT_NAME} INTERFACE -D"${REGION}")
    endif()
endforeach()

if(MODULATION STREQUAL LORA)
    target_compile_definitions(${PROJECT_NAME} INTERFACE USE_MODEM_LORA)
elseif(MODULATION STREQUAL FSK)
    target_compile_definitions(${PROJECT_NAME} INTERFACE USE_MODEM_FSK)
endif()


# rest of your project
add_executable(pico_ping_pong
    main.c
)

# target_link_libraries(pico_ping_pong INTERFACE pico_lora_sx1262)
target_link_libraries(pico_ping_pong pico_lora_sx1262 hardware_spi pico_stdlib)

# enable usb output, disable uart output
pico_enable_stdio_usb(pico_ping_pong 1)
pico_enable_stdio_uart(pico_ping_pong 0)

# create map/bin/hex/uf2 file in addition to ELF.
pico_add_extra_outputs(pico_ping_pong)
