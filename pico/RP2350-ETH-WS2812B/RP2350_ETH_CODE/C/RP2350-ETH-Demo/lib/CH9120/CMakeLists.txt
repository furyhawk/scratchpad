# Search all source files in the current directory
# and save the names to the DIR_CH9120_SRCS variable
aux_source_directory(. DIR_CH9120_SRCS)

# add header file directory
include_directories(../Config)

# Generate link library
add_library(CH9120 ${DIR_CH9120_SRCS})
target_link_libraries( CH9120 PUBLIC pico_stdlib hardware_spi)