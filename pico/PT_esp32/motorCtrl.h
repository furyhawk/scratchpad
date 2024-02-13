void pinInit(){
  // Set the mode of the motorCtrl pin
  pinMode(AIN1, OUTPUT);
  pinMode(AIN2, OUTPUT);
  pinMode(PWMA, OUTPUT);
  pinMode(BIN1, OUTPUT);
  pinMode(BIN2, OUTPUT);
  pinMode(PWMB, OUTPUT);

  ledcSetup(channel_A, freq, 8);
  ledcAttachPin(PWMA, channel_A);

  ledcSetup(channel_B, freq, 8);
  ledcAttachPin(PWMB, channel_B);

  digitalWrite(AIN1, LOW);
  digitalWrite(AIN2, LOW);
  digitalWrite(BIN1, LOW);
  digitalWrite(BIN2, LOW);
}





void switchCtrlA(float pwmInputA){
  int pwmIntA = round(pwmInputA);
  if(pwmIntA > 0){
    digitalWrite(AIN1, HIGH);
    digitalWrite(AIN2, LOW);
    ledcWrite(channel_A, pwmIntA);
  }
  else{
    digitalWrite(AIN1, LOW);
    digitalWrite(AIN2, HIGH);
    ledcWrite(channel_A,-pwmIntA);
  }
}


void switchCtrlB(float pwmInputB){
  int pwmIntB = round(pwmInputB);
  if(pwmIntB > 0){
    digitalWrite(BIN1, HIGH);
    digitalWrite(BIN2, LOW);
    ledcWrite(channel_B, pwmIntB);
  }
  else{
    digitalWrite(BIN1, LOW);
    digitalWrite(BIN2, HIGH);
    ledcWrite(channel_B,-pwmIntB);
  }
}


void pwmInput(){
  switchCtrlA(constrain(jsonCmdReceive["SA"].as<double>(), -255, 255));
  switchCtrlB(constrain(jsonCmdReceive["SB"].as<double>(), -255, 255));
}