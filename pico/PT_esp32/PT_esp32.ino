#include <Preferences.h>
#include <nvs_flash.h>
Preferences preferences;

#include "math.h"
#include <WiFi.h>
#include <WebServer.h>
#include <Wire.h>
#include "WebPage.h"
WebServer server(80);

#include "ArduinoJson.h"
StaticJsonDocument<256> jsonCmdReceive;
StaticJsonDocument<256> jsonInfoSend;
// TaskHandle_t serialCtrlHandle;
// TaskHandle_t feedBackHandle;

#include "IMU.h"
#include "config.h"

#include "motorCtrl.h"
#include "screenCtrl.h"
#include "powerInfo.h"
#include "busServoCtrl.h"

#include "baseFunctions.h"
#include "connectionFuncs.h"


// EMERGENCY_STOP  : {"T":0}

// GIMBAL_CTRL     : {"T":1,"X":45,"Y":45,"SPD":0,"ACC":0}

// BASE_GIMBAL_CTRL： {"T":2,"X":-1,"Y":1,"SPD":25}

// OLED_SET        : {"T":3,"lineNum":0,"Text":"putYourTextHere"}
// OLED_DEFAULT    : {"T":-3}

// ALL_LIGHT_OFF     : {"T":41, "SA":0, "SB":0}
// LIGHT_PWM_CTRL    : {"T":41, "SA":255, "SB":255}

// BUS_SERVO_CTRL    : {"T":50,"id":1,"pos":2047,"spd":500,"acc":30}
// BUS_SERVO_MID     : {"T":-5,"id":1}
// BUS_SERVO_SCAN    : {"T":52,"num":20}
// BUS_SERVO_INFO    : {"T":53,"id":1}
// BUS_SERVO_ID_SET  : {"T":54,"old":1,"new":2}
// BUS_SERVO_TORQUE_LOCK  : {"T":55,"id":1,"status":1}
// BUS_SERVO_TORQUE_LIMIT : {"T":56,"id":1,"limit":500}
// BUS_SERVO_MODE    : {"T":57,"id":1,"mode":0}
// BUS_SERVO_MID_SET : {"T":58,"id":1}
// BUS_SERVO_STOP    : {"T":59,"id":1}

// WIFI_SCAN       : {"T":60}
// WIFI_TRY_STA    : {"T":61}
// WIFI_AP_DEFAULT : {"T":62}
// WIFI_INFO       : {"T":65}
// WIFI_OFF        : {"T":66}

// INA219_INFO     : {"T":70}
// IMU_INFO        : {"T":71}
// DEVICE_INFO     : {"T":74}


void jsonInfoSerialFeedBack(){
  jsonInfoSend.clear();

  // jsonInfoSend["r"] = stAngles.fRoll;
  // jsonInfoSend["p"] = stAngles.fPitch;

  jsonInfoSend["pa"] = panAngle;
  jsonInfoSend["ta"] = tiltAngle;

  jsonInfoSend["pl"] = panLoadRead;
  jsonInfoSend["tl"] = tiltLoadRead;

  // jsonInfoSend["t"] = IMU_Temp;
  jsonInfoSend["v"] = INA219_DATA_V;

  serializeJson(jsonInfoSend, Serial);
  Serial.println();
  jsonInfoSend.clear();
}


void feedBackThreading(void *pvParameter){
  while(1){
    // getIMU();
    getGimbalAngle();
    jsonInfoSerialFeedBack();
    delay(200);
  }
}


void setup() {
  Wire.begin(S_SDA, S_SCL);
  Serial.begin(UART_BAUD);

  while(!Serial){}
  pinInit();

  busServoInit();

  InitScreen();
  allDataUpdate();

  imuInit();
  // xTaskCreatePinnedToCore(&commandThreading, "serialCtrl", 8000, NULL, 5, &serialCtrlHandle, 0);
  // xTaskCreatePinnedToCore(&feedBackThreading, "feedBack", 8000, NULL, 5, &feedBackHandle, 0);
  
  gimbalCtrl(0, 0, 600, 50);

  wifiInit();
  webServerSetup();
}


void loop() {
  static long lastScreenUpdateMillis;
  static long lastSerialSend;
  long currentMillis = millis();

  if(currentMillis - lastScreenUpdateMillis > 500){
    lastScreenUpdateMillis = currentMillis;
    InaDataUpdate();
    getWifiStatus();
    allDataUpdate();
  }

  serialCtrl();
  server.handleClient();

  getGimbalAngle();
  if(currentMillis - lastSerialSend >= 200){
    jsonInfoSerialFeedBack();
    lastSerialSend = currentMillis;
  }
}