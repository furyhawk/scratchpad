set(st_sources
    ./s_task/src/s_task.c
    ./s_task/src/s_mutex.c
    ./s_task/src/s_event.c
    ./s_task/src/s_event_embed.c
    ./s_task/src/s_chan.c
    ./s_task/src/s_chan_embed.c
    ./s_task/src/s_timer_fast.c
    ./s_task/src/s_timer_small.c
    ./s_task/src/s_list.c
    ./s_task/src/s_rbtree.c)

add_executable(Pico-RGB-Matrix-P3-64x32-Demo
			./input/input_event_buffer.cpp
            ./input/input_system.cpp
            ./input/reg_gpio_key.cpp
			./Hal/hal_gpio_key.cpp
            ./Hal/hal_RGBMatrix_device.cpp
			./ModuleDrivers/driver_key.cpp
            ./ModuleDrivers/driver_buzzer.cpp
            ./ModuleDrivers/driver_ds3231.cpp
            ./ModuleDrivers/driver_adc.cpp
            ./ModuleDrivers/driver_RGBMatrix.cpp
            ./device/RGBMatrix_device.cpp
            ./display/display_subsystem.cpp
            ./font/font.cpp
            ./src/main.cpp
            ${st_sources})


target_link_libraries(Pico-RGB-Matrix-P3-64x32-Demo pico_stdlib hardware_i2c hardware_adc)

target_include_directories(Pico-RGB-Matrix-P3-64x32-Demo PRIVATE 
                        ./s_task/include 
                        ./Hal
                        ./ModuleDrivers
                        ./input
                        ./device
                        ./config
                        ./font
                        ./display)

# enable usb output, disable uart output
pico_enable_stdio_usb(Pico-RGB-Matrix-P3-64x32-Demo 1)
pico_enable_stdio_uart(Pico-RGB-Matrix-P3-64x32-Demo 1)

# create map/bin/hex file etc.
pico_add_extra_outputs(Pico-RGB-Matrix-P3-64x32-Demo)

# add url via pico_set_program_url
example_auto_set_url(Pico-RGB-Matrix-P3-64x32-Demo)

