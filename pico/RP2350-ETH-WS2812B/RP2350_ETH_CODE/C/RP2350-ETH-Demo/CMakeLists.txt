cmake_minimum_required(VERSION 3.12)
include(pico_sdk_import.cmake)
project(Pico_ePaper_Code)
pico_sdk_init()

# add compiled files subdirectory
add_subdirectory(lib/CH9120)
add_subdirectory(examples)

# add header file directory
include_directories(examples)
include_directories(./lib/CH9120)

# generate executable file
add_executable(main 
main.c
)

# enable usb output, disable uart output
pico_enable_stdio_usb(main 1)
pico_enable_stdio_uart(main 1)

# create map/bin/hex/uf2 file etc.
pico_add_extra_outputs(main)

target_link_libraries(main examples CH9120  pico_stdlib hardware_spi)