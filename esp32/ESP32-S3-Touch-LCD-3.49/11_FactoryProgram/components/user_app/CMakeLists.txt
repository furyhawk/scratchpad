idf_component_register(
  SRCS "user_app.cpp"
  PRIV_REQUIRES 
  main 
  ble_scan_bsp 
  esp_wifi_bsp
  sdcard_bsp 
  lvgl 
  ui_bsp 
  button_bsp 
  adc_bsp 
  i2c_equipment 
  lcd_bl_pwm_bsp
  audio_bsp
  espressif__esp_io_expander_tca9554
  INCLUDE_DIRS "./")
