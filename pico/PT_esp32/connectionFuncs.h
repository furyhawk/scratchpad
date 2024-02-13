void getMAC(){
  WiFi.mode(WIFI_AP_STA);
  MAC_ADDRESS = WiFi.macAddress();
  Serial.print("MAC:");
  Serial.println(WiFi.macAddress());
}


void getIP(){
  IP_ADDRESS = WiFi.localIP();
}


void setAP(){
  WiFi.disconnect();
  delay(100);

  WiFi.softAP(AP_SSID, AP_PWD);
  IPAddress myIP = WiFi.softAPIP();
  IP_ADDRESS = myIP;
  Serial.print("AP IP address: ");
  Serial.println(myIP);
  WIFI_MODE = 1;
}


void setSTA(){
  WiFi.disconnect();
  delay(100);

  WiFi.mode(WIFI_STA);
  WiFi.begin(STA_SSID, STA_PWD);
  Serial.print("Connecting to WiFi ..");
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print('.');
    delay(1000);
  }
  WIFI_MODE = 3;
  IP_ADDRESS = WiFi.localIP();
  Serial.print("STA IP address: ");
  Serial.println(IP_ADDRESS);
}


void setTrySTA(int timeOutSecs){
  WiFi.mode(WIFI_STA);
  WiFi.begin(STA_SSID, STA_PWD);

  Serial.print("Connecting to SSID:");
  Serial.println(STA_SSID);
  Serial.println("Setting up AP in");

  for(int i = 0;i < timeOutSecs;i++){
    display.clearDisplay();
    display.setTextSize(1);
    display.setTextColor(SSD1306_WHITE);
    display.setCursor(0,0);

    display.println(F("Connecting to SSID:"));
    display.println(STA_SSID);
    display.println(F("If not available"));
    display.print(F("Set up [AP] in "));
    display.print(timeOutSecs - i);
    display.print(F(" sec."));

    display.display();

    Serial.print(timeOutSecs-i);Serial.println("seconds");

    if(WiFi.status() == WL_CONNECTED){
      WIFI_MODE = 3;
      IP_ADDRESS = WiFi.localIP();
      Serial.print("STA IP address: ");
      Serial.println(IP_ADDRESS);
      break;
    }
    else{
      WIFI_MODE = 1;
    }

    delay(1000);
  }

  if(WIFI_MODE == 1){setAP();}
}


void wifiInit(){
  getMAC();
  WIFI_MODE = DEFAULT_WIFI_MODE;
  if(WIFI_MODE == 1){setAP();}
  else if(WIFI_MODE == 2){setSTA();}
  else if(WIFI_MODE == 4){setTrySTA(setTimeOutSecs);}
}


void getWifiStatus(){
  if(WiFi.status() == WL_CONNECTED && WIFI_MODE == 3){
    getIP();
    WIFI_RSSI = WiFi.RSSI();
  }
  else if(WiFi.status() == WL_CONNECTION_LOST && DEFAULT_WIFI_MODE == 3){
    WiFi.disconnect();
    wifiInit();
  }
}


void wifiScan(){
  Serial.println("Scanning...");
  WiFi.disconnect();
  WiFi.mode(WIFI_STA);
  WiFi.disconnect();
  delay(100);

  int n = WiFi.scanNetworks();
  Serial.println("scan done");
  if (n == 0) {
      Serial.println("no networks found");
  } else {
    Serial.print(n);
    Serial.println(" networks found");
    for (int i = 0; i < n; ++i) {
      // Print SSID and RSSI for each network found
      Serial.print(i + 1);
      Serial.print(": ");
      Serial.print(WiFi.SSID(i));
      Serial.print(" (");
      Serial.print(WiFi.RSSI(i));
      Serial.print(")");
      Serial.println((WiFi.encryptionType(i) == WIFI_AUTH_OPEN)?" ":"*");
      delay(10);
    }
  }
  Serial.println("");
}


void wifiConnectSTA(const char* ssidInput, const char* pwdInput){
  WiFi.disconnect();
  delay(100);
  
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssidInput, pwdInput);

  Serial.print("Connecting to SSID:");
  Serial.println(ssidInput);
  Serial.println("Setting up AP in");

  for(int i = 0;i < 20;i++){
    display.clearDisplay();
    display.setTextSize(1);
    display.setTextColor(SSD1306_WHITE);
    display.setCursor(0,0);
    display.println(F("Connecting to SSID:"));
    display.println(ssidInput);
    display.println(F("If not available"));
    display.print(F("Set up [AP] in "));
    display.print(20 - i);
    display.print(F(" sec."));
    display.display();
    Serial.print(20-i);Serial.println("seconds");
    if(WiFi.status() == WL_CONNECTED){
      WIFI_MODE = 3;
      IP_ADDRESS = WiFi.localIP();
      Serial.print("STA IP address: ");
      Serial.println(IP_ADDRESS);
      break;
    }
    else{
      WIFI_MODE = 1;
    }
    delay(1000);
  }
  if(WIFI_MODE == 1){setAP();}
}


void wifiAPStart(char* apName, char* pwdInput){
  WiFi.disconnect();
  delay(100);
  
  WiFi.softAP(apName, pwdInput);
  IPAddress myIP = WiFi.softAPIP();
  IP_ADDRESS = myIP;
  Serial.print("AP IP address: ");
  Serial.println(myIP);
  AP_SSID = apName;
  AP_PWD = pwdInput;
  WIFI_MODE = 1;
}


void wifiInfoGet(){
  jsonInfoSend.clear();
  jsonFeedbackWeb = "";
  jsonInfoSend["IP"] = IP_ADDRESS;
  jsonInfoSend["RSSI"] = WIFI_RSSI;
  jsonInfoSend["MODE"] = WIFI_MODE;
  jsonInfoSend["AP_NAME"] = AP_SSID;
  jsonInfoSend["AP_PWD"] = AP_PWD;
  jsonInfoSend["STA_SSID"] = STA_SSID;
  jsonInfoSend["STA_PWD"] = STA_PWD;
  serializeJson(jsonInfoSend, Serial);
  serializeJson(jsonInfoSend, jsonFeedbackWeb);
  jsonInfoSend.clear();
}


void wifiOff(){
  WiFi.disconnect();
  WIFI_MODE = -1;
}


void handleRoot(){
  server.send(200, "text/html", index_html); //Send web page
  Serial.println("connecting...");
}


void handleDeviceInfo(){
  char responseJsonWeb[256];

  jsonInfoSend.clear();
  jsonInfoSend["V"] = round(INA219_DATA_V*100)/100;

  jsonInfoSend["r"] = round(stAngles.fRoll*100)/100;
  jsonInfoSend["p"] = round(stAngles.fPitch*100)/100;
  jsonInfoSend["y"] = round(stAngles.fYaw*100)/100;

  jsonInfoSend["mX"] = stMagnRawData.s16X;
  jsonInfoSend["mY"] = stMagnRawData.s16Y;
  jsonInfoSend["mZ"] = stMagnRawData.s16Z;

  jsonInfoSend["IP"] = IP_ADDRESS;
  jsonInfoSend["MAC"] = MAC_ADDRESS;
  jsonInfoSend["RSSI"] = WIFI_RSSI;

  serializeJson(jsonInfoSend, responseJsonWeb);
  server.send(200, "text/plane", responseJsonWeb);
}


void baseGimbalCtrl(float inputX, float inputY, float inputSpd){
  static float goalX = 0;
  static float goalY = 0;

  if(inputX == -1 && inputY == 1){
    goalX = -180;
    goalY = 90;
  }
  else if(inputX == 0 && inputY == 1){
    goalY = 90;
  }
  else if(inputX == 1 && inputY == 1){
    goalX = 180;
    goalY = 90;
  }
  else if(inputX == -1 && inputY == 0){
    goalX = -180;
  }
  else if(inputX == 1 && inputY == 0){
    goalX = 180;
  }
  else if(inputX == -1 && inputY == -1){
    goalX = -180;
    goalY = -45;
  }
  else if(inputX == 0 && inputY == -1){
    goalY = -45;
  }
  else if(inputX == 1 && inputY == -1){
    goalX = 180;
    goalY = -45;
  }

  if(inputX == 2 && inputY == 2){
    gimbalCtrl(0, 0, 0, 50);
  }
  else{
    gimbalCtrl(goalX, goalY, inputSpd, 0);
    if(inputX == 0){
      busServoStop(2);
      // goalX = getAxisAngle(2);
      goalX = panAngle;
    }
    if(inputY == 0){
      busServoStop(1);
      // goalY = getAxisAngle(1);
      goalY = tiltAngle;
    }
  }
}


void funcBtns(int inputB, int inputC){
  static bool busServoTorqueLock = true;
  if(inputB == 0 && inputC == 0){
    if(busServoTorqueLock){
      st.EnableTorque(1, 0);
      st.EnableTorque(2, 0);
      busServoTorqueLock = false;
    }
    else{
      st.EnableTorque(1, 1);
      st.EnableTorque(2, 1);
      busServoTorqueLock = true;
    }
  }
  else if(inputB == 1){
    if(inputC == 2){
      st.CalibrationOfs(2);
    }
    else if(inputC == 1){
      st.CalibrationOfs(1);
    }
  }
}


void lightsCtrl(int inputB, int inputC){
  if(inputB == 0){
    switchCtrlA(0);
    switchCtrlB(0);
  }
  else if(inputB == 1){
    switchCtrlA(64);
    switchCtrlB(64);
  }
  else if(inputB == 2){
    switchCtrlA(255);
    switchCtrlB(255);
  }
}


void handleJsonFb(){
    server.send(200, "text/plane", jsonFeedbackWeb);
    jsonFeedbackWeb = "";
    jsonInfoSend.clear();
}


void webCtrlServer(){
  server.on("/",       handleRoot);
  server.on("/deviceInfo", handleDeviceInfo);
  server.on("/jsfb", handleJsonFb);

  server.on("/cmd", [](){
    int cmdA = server.arg(0).toInt();
    float cmdB = server.arg(1).toFloat();
    float cmdC = server.arg(2).toFloat();
    switch(cmdA){
      case 1: baseGimbalCtrl(cmdB, cmdC, 25);break;
      case 2: funcBtns(cmdB, cmdC);break;
      case 3: lightsCtrl(cmdB, cmdC);break;
    }
    server.send(200, "text/plane", "");
  });

  server.on("/js", [](){
    lastCmdTime = millis();
    String jsonCmdWeb = server.arg(0);
    Serial.println(jsonCmdWeb);
    deserializeJson(jsonCmdReceive, jsonCmdWeb);
    cmdHandler();
    jsonCmdReceive.clear();
  });

  // Start server
  server.begin();
  Serial.println("Server Starts.");
}


void webServerSetup(){
  webCtrlServer();
}