cmake_minimum_required(VERSION 3.12)

# Pull in SDK (must be before project)
include(pico_sdk_import.cmake)

project(Pico_UPS_project)

# Initialize the SDK
pico_sdk_init()

add_executable(Pico_UPS
		Pico_UPS.cpp
		)

# Pull in our pico_stdlib which aggregates commonly used features
target_link_libraries(Pico_UPS hardware_i2c pico_stdlib)

# enable usb output, disable uart output
pico_enable_stdio_usb(Pico_UPS 1)
pico_enable_stdio_uart(Pico_UPS 0)

# create map/bin/hex/uf2 file etc.
pico_add_extra_outputs(Pico_UPS)
