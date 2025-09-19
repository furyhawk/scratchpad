idf_component_register(
  SRCS "user_app.cpp"
  PRIV_REQUIRES 
  main 
  lvgl 
  ui_bsp 
  button_bsp 
  espressif__esp_io_expander_tca9554
  INCLUDE_DIRS "./")
