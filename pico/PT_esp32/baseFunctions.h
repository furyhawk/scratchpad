// <<<<<<<<<<=========WIFI Placeholder===========>>>>>>>>>>
void wifiScan();


void wifiConnectSTA(char* ssidInput, char* pwdInput);


void wifiAPStart(char* apName, char* pwdInput);


void wifiInfoGet();


void wifiOff();


void setAP();


void setTrySTA(int timeOutSecs);


void baseGimbalCtrl(float inputX, float inputY, float inputSpd);


// <<<<<<<<<<=========Info Feedback===========>>>>>>>>>>
void ina219Info(){
  jsonInfoSend.clear();
  jsonFeedbackWeb = "";
  jsonInfoSend["shunt_mV"] = shuntVoltage_mV;
  jsonInfoSend["load_V"] = loadVoltage_V;
  jsonInfoSend["bus_V"] = busVoltage_V;
  jsonInfoSend["current_mA"] = current_mA;
  jsonInfoSend["power_mW"] = power_mW;
  serializeJson(jsonInfoSend, Serial);
  serializeJson(jsonInfoSend, jsonFeedbackWeb);
  jsonInfoSend.clear();
}


void imuInfo(){
  jsonInfoSend.clear();
  jsonFeedbackWeb = "";
  imuDataGet( &stAngles, &stGyroRawData, &stAccelRawData, &stMagnRawData, &qRawData);

  jsonInfoSend["temp"] = QMI8658_readTemp();

  jsonInfoSend["roll"] = stAngles.fRoll;
  jsonInfoSend["pitch"] = stAngles.fPitch;
  jsonInfoSend["yaw"] = stAngles.fYaw;

  jsonInfoSend["acce_X"] = stAccelRawData.s16X;
  jsonInfoSend["acce_Y"] = stAccelRawData.s16Y;
  jsonInfoSend["acce_Z"] = stAccelRawData.s16Z;

  jsonInfoSend["gyro_X"] = stGyroRawData.s16X;
  jsonInfoSend["gyro_Y"] = stGyroRawData.s16Y;
  jsonInfoSend["gyro_Z"] = stGyroRawData.s16Z;

  jsonInfoSend["magn_X"] = stMagnRawData.s16X;
  jsonInfoSend["magn_Y"] = stMagnRawData.s16Y;
  jsonInfoSend["magn_Z"] = stMagnRawData.s16Z;

  jsonInfoSend["millis"] = millis();

  serializeJson(jsonInfoSend, Serial);
  serializeJson(jsonInfoSend, jsonFeedbackWeb);
  jsonInfoSend.clear();
}


void jsonInfoSerialFB(){
  jsonInfoSend.clear();

  jsonInfoSend["roll"]  = stAngles.fRoll;
  jsonInfoSend["pitch"] = stAngles.fPitch;
  jsonInfoSend["yaw"]   = stAngles.fYaw;

  jsonInfoSend["acce_X"] = stAccelRawData.s16X;
  jsonInfoSend["acce_Y"] = stAccelRawData.s16Y;
  jsonInfoSend["acce_Z"] = stAccelRawData.s16Z;

  jsonInfoSend["gyro_X"] = stGyroRawData.s16X;
  jsonInfoSend["gyro_Y"] = stGyroRawData.s16Y;
  jsonInfoSend["gyro_Z"] = stGyroRawData.s16Z;

  jsonInfoSend["magn_X"] = stMagnRawData.s16X;
  jsonInfoSend["magn_Y"] = stMagnRawData.s16Y;
  jsonInfoSend["magn_Z"] = stMagnRawData.s16Z;

  jsonInfoSend["q0"] = qRawData.a;
  jsonInfoSend["q1"] = qRawData.b;
  jsonInfoSend["q2"] = qRawData.c;
  jsonInfoSend["q3"] = qRawData.d;

  serializeJson(jsonInfoSend, Serial);
  jsonInfoSend.clear();
}


void deviceInfo(){
  jsonInfoSend.clear();
  jsonFeedbackWeb = "";
  jsonInfoSend["MAC"] = MAC_ADDRESS;
  serializeJson(jsonInfoSend, Serial);
  serializeJson(jsonInfoSend, jsonFeedbackWeb);
  jsonInfoSend.clear();
}


void setJsonOLED(int lineNumInput, String textInput){
  switch(lineNumInput){
    case 0: screenLine_0 = textInput;break;
    case 1: screenLine_1 = textInput;break;
    case 2: screenLine_2 = textInput;break;
    case 3: screenLine_3 = textInput;break;
  }
  screenDefaultMode = false;
}


void cmdHandler(){
  jsonCtrlMode = true;
  int cmdType = jsonCmdReceive["T"].as<int>();
  switch(cmdType){
    case               -1: emergencyStop();break;
    case   EMERGENCY_STOP: emergencyStop();break;

    case      GIMBAL_CTRL: gimbalGoalX = jsonCmdReceive["X"];
                           gimbalGoalY = jsonCmdReceive["Y"];
                           gimbalCtrl(gimbalGoalX,
                                      gimbalGoalY,
                                      jsonCmdReceive["SPD"],
                                      jsonCmdReceive["ACC"]);break;
    case BASE_GIMBAL_CTRL: baseGimbalCtrl(jsonCmdReceive["X"],
                                          jsonCmdReceive["Y"],
                                          jsonCmdReceive["SPD"]);break;

    case   LIGHT_PWM_CTRL: pwmInput();break;

    case         OLED_SET: setJsonOLED(jsonCmdReceive["lineNum"].as<int>(), jsonCmdReceive["Text"]);break;
    case     OLED_DEFAULT: screenDefaultMode = true;break;

    case         BUS_SERVO_CTRL: busServoCtrl(jsonCmdReceive["id"],
                                              jsonCmdReceive["pos"],
                                              jsonCmdReceive["spd"],
                                              jsonCmdReceive["acc"]);break;
    case          BUS_SERVO_MID: busServoMid(jsonCmdReceive["id"]);break;
    case         BUS_SERVO_SCAN: busServoScan(jsonCmdReceive["num"]);break;
    case         BUS_SERVO_INFO: busServoInfo(jsonCmdReceive["id"]);break;
    case       BUS_SERVO_ID_SET: busServoIDSet(jsonCmdReceive["old"], 
                                               jsonCmdReceive["new"]);break;
    case  BUS_SERVO_TORQUE_LOCK: busServoTorqueLock(jsonCmdReceive["id"], 
                                                    jsonCmdReceive["status"]);break;
    case BUS_SERVO_TORQUE_LIMIT: busServoTorqueLimit(jsonCmdReceive["id"], 
                                                     jsonCmdReceive["limit"]);break;
    case         BUS_SERVO_MODE: busServoMode(jsonCmdReceive["id"],
                                              jsonCmdReceive["mode"]);break;
    case      BUS_SERVO_MID_SET: st.CalibrationOfs(jsonCmdReceive["id"].as<int>());break;
    case         BUS_SERVO_STOP: busServoStop(jsonCmdReceive["id"].as<int>());break;

    case              WIFI_INFO: wifiInfoGet();break;

    case            INA219_INFO: ina219Info();break;
    case               IMU_INFO: imuInfo();break;
    case            DEVICE_INFO: deviceInfo();break;
  }
}


// void serialCtrl(){
//   if (Serial.available()){
//     DeserializationError err = deserializeJson(jsonCmdReceive, Serial);
//     if (err == DeserializationError::Ok){
//       cmdHandler();
//       lastCmdTime = millis();
//     }
//     else{
//       while (Serial.available() > 0){
//         Serial.read();
//       }
//     }
//   }
// }


void serialCtrl() {
  static String receivedData;

  while (Serial.available() > 0) {
    char receivedChar = Serial.read();
    receivedData += receivedChar;

    // Detect the end of the JSON string based on a specific termination character
    if (receivedChar == '}') {
      // Now we have received the complete JSON string
      DeserializationError err = deserializeJson(jsonCmdReceive, receivedData);
      if (err == DeserializationError::Ok) {
        cmdHandler();
        lastCmdTime = millis();
      } else {
        // Handle JSON parsing error here
      }
      
      // Reset the receivedData for the next JSON string
      receivedData = "";
    }
  }
}


void commandThreading(void *pvParameter){
  while(1){
    serialCtrl();
    server.handleClient();
    delay(15);
  }
}