// <<<<<<<<<<=========BUS Servo===========>>>>>>>>>>
#include <SCServo.h>
SMS_STS st;

// the uart used to control servos.
// GPIO 18 - S_RXD, GPIO 19 - S_TXD, as default.
#define S_RXD 18
#define S_TXD 19

u16 panPosRead;
u16 tiltPosRead;

byte ID_List[253];
s16 loadRead;
s16 speedRead;
byte voltageRead;
int currentRead;
s16 posRead;
s16 modeRead;
s16 temperRead;
int MAX_ID;

s16 stMiddlePos = 2047;

float panAngle;
float tiltAngle;

s16 panLoadRead;
s16 tiltLoadRead;


void busServoInit(){
  Serial1.begin(1000000, SERIAL_8N1, S_RXD, S_TXD);
  st.pSerial = &Serial1;
  while(!Serial1) {}
}


void busServoCtrl(u8 idInput, s16 posInput, u16 spdInput, u8 accInput){
  st.WritePosEx(idInput, posInput, spdInput, accInput);
}


void busServoMid(u8 idInput){
  st.WritePosEx(idInput, 2047, 0, 0);
}


void busServoSync(u8 numInput, u8 idInput[], s16 posInput[], u16 spdInput[], u8 accInput[]){
  st.SyncWritePosEx(idInput, numInput, posInput, spdInput, accInput);
}


void busServoScan(u8 maxNumInput){
  int pingStatus;
  int servoNumScan = 0;
  jsonInfoSend.clear();
  jsonFeedbackWeb = "";
  for(int i = 0; i <= maxNumInput; i++){
    pingStatus = st.Ping(i);
    if(pingStatus != -1){
      servoNumScan++;
      Serial.print(i);Serial.print(" ");Serial.println(st.ReadMode(i));
      jsonInfoSend[("servoID_%d_mode:", i)] = st.ReadMode(i);
    }
  }
  jsonInfoSend["ServoNum"] = servoNumScan;
  serializeJson(jsonInfoSend, Serial);
  serializeJson(jsonInfoSend, jsonFeedbackWeb);
}


void busServoInfo(byte idInput){
  if(st.FeedBack(idInput)!=-1){
    jsonInfoSend.clear();
    jsonFeedbackWeb = "";
    jsonInfoSend["pos"]  = st.ReadPos(-1);
    jsonInfoSend["spd"]  = st.ReadSpeed(-1);
    jsonInfoSend["load"] = st.ReadLoad(-1);
    jsonInfoSend["volt"] = st.ReadVoltage(-1);
    jsonInfoSend["curt"] = st.ReadCurrent(-1);
    jsonInfoSend["temp"] = st.ReadTemper(-1);
    jsonInfoSend["mode"] = st.ReadMode(idInput);
    serializeJson(jsonInfoSend, Serial);
    serializeJson(jsonInfoSend, jsonFeedbackWeb);
  }
  else{

  }
}


void busServoIDSet(byte oldInput, byte newInput){
  st.unLockEprom(oldInput);
  st.writeByte(oldInput, SMS_STS_ID, newInput);
  st.LockEprom(newInput);
}


float getAxisAngle(byte InputID){
  int stepRead;
  float angleRead;
  if(st.FeedBack(InputID)!=-1){
    stepRead = st.ReadPos(-1);
    if(InputID == 2){
      angleRead = map((stepRead - 2047), 0, 4095, 0, 360);
    }
    else if(InputID == 1){
      angleRead = map((2047 - stepRead), 0, 4095, 0, 360);
    }
  }
}


void busServoStop(byte InputID){
  st.EnableTorque(InputID, 0);
  delay(5);
  st.EnableTorque(InputID, 1);
}


void emergencyStop(){
  busServoStop(254);
}


void busServoTorqueLock(byte idInput, int statusInput){
  if(statusInput == 1){
    st.EnableTorque(idInput, 1);
  }
  else if(statusInput == 0){
    st.EnableTorque(idInput, 0);
  }
}


void busServoTorqueLimit(byte idInput, int limitInput){
  if(limitInput > 1000 || limitInput < 0){
    return;
  }
  st.unLockEprom(idInput);
  st.writeWord(idInput, 16, limitInput);
  st.writeWord(idInput, 48, limitInput);
  st.LockEprom(idInput);
}


void busServoMode(byte InputID, byte InputMode){
  if(InputMode == 0){
    st.unLockEprom(InputID);
    st.writeWord(InputID, 11, 4095);
    st.writeByte(InputID, SMS_STS_MODE, InputMode);
    st.LockEprom(InputID);
  }
  else if(InputMode == 3){
    st.unLockEprom(InputID);
    st.writeByte(InputID, SMS_STS_MODE, InputMode);
    st.writeWord(InputID, 11, 0);
    st.LockEprom(InputID);
  }
}


//  <2>  
//  ----
//  <1>
void gimbalCtrl(float Xinput, float Yinput, float spdInput, float accInput){
  Xinput = constrain(Xinput, -180, 180);
  Yinput = constrain(Yinput, -45, 90);

  byte gimbalID[2];
  s16  gimbalPos[2];
  u16  gimbalSpd[2];
  u8   gimbalAcc[2];

  gimbalID[0] = 2;
  gimbalID[1] = 1;

  // X.compute
  gimbalPos[0] = 2047 + (int)round(map(Xinput, 0, 360, 0, 4095));
  gimbalPos[1] = 2047 - (int)round(map(Yinput, 0, 360, 0, 4095));

  gimbalSpd[0] = (int)round(map(spdInput, 0, 360, 0, 4095));
  gimbalSpd[1] = (int)round(map(spdInput, 0, 360, 0, 4095));

  gimbalAcc[0] = (int)round(map(accInput, 0, 360, 0, 4095));
  gimbalAcc[1] = (int)round(map(accInput, 0, 360, 0, 4095));

  st.SyncWritePosEx(gimbalID, 2, gimbalPos, gimbalSpd, gimbalAcc);
}


void getGimbalAngle(){
  if(st.FeedBack(2)!=-1){
    panPosRead  = st.ReadPos(-1);
    panLoadRead = st.ReadLoad(-1);
  }

  if(st.FeedBack(1)!=-1){
    tiltPosRead  = st.ReadPos(-1);
    tiltLoadRead = st.ReadLoad(-1);
  }

  panAngle  =  (int)round(map(panPosRead - 2047, 0, 4095, 0, 360));
  tiltAngle =  (int)round(map(2047 - tiltPosRead, 0, 4095, 0, 360));
}