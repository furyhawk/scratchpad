aux_source_directory(. DIR_lps22hb_SRCS)

add_library(lps22hb ${DIR_lps22hb_SRCS})
target_link_libraries(lps22hb PUBLIC hardware_i2c pico_stdlib)
