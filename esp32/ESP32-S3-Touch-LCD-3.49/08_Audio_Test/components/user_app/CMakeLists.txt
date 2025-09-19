idf_component_register(
  SRCS "user_app.cpp"
  PRIV_REQUIRES 
  main 
  lvgl 
  ui_bsp 
  lcd_bl_pwm_bsp
  audio_bsp
  espressif__esp_io_expander_tca9554
  INCLUDE_DIRS "./")
