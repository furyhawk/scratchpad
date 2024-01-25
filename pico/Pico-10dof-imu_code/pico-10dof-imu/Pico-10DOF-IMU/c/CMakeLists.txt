cmake_minimum_required(VERSION 3.12)
include(pico_sdk_import.cmake)
project(pico-10dof-imu_project)
pico_sdk_init()
add_subdirectory(icm20948)
add_subdirectory(lps22hb)
include_directories(./icm20948)
include_directories(./lps22hb)

add_executable(imu
main.c
)
pico_enable_stdio_usb(imu 1)
pico_enable_stdio_uart(imu 1)

pico_add_extra_outputs(imu)

# Pull in our pico_stdlib which pulls in commonly used features
target_link_libraries(imu pico_stdlib icm20948 lps22hb hardware_i2c)
