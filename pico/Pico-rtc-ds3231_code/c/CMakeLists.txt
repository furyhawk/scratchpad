cmake_minimum_required(VERSION 3.12)

include(pico_sdk_import.cmake)

project(pico-rtc-ds3231_project)

pico_sdk_init()

add_subdirectory(ds3231)
include_directories(./ds3231)
add_executable(rtc
        main.c
        )

pico_enable_stdio_usb(rtc 1)
pico_enable_stdio_uart(rtc 1)

pico_add_extra_outputs(rtc)

# Pull in our pico_stdlib which pulls in commonly used features
target_link_libraries(rtc ds3231 hardware_i2c pico_stdlib)
