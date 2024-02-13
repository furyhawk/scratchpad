// === === === CONNECTION === === ===
// WIFI_AP settings.
const char* AP_SSID = "Pan-Tilt_Camera";
const char* AP_PWD  = "12345678";

// WIFI_STA settings.
const char* STA_SSID = "JSBZY-2.4G";
const char* STA_PWD  = "waveshare0755";

// set the baud of uart.
// #define UART_BAUD 1000000
// #define UART_BAUD 921600
// #define UART_BAUD 460800
#define UART_BAUD 115200

#define HEART_BEAT 3000
long lastCmdTime;

// the MAC address of the device you want to ctrl.
uint8_t broadcastAddress[] = {0x08, 0x3A, 0xF2, 0x93, 0x5F, 0xA8};

// ESP-NOW message struct.
typedef struct struct_message {
  int messageType;
  int messageA;
  int messageB;
  int messageC;
  int messageD;
  int messageE;
} struct_message;

// Create a struct_message called myData
struct_message myData;

// set the default wifi mode here.
// wifiMode:
// 1 as [AP] mode, it will not connect other wifi.
// 2 as [STA] mode(connecting), it will connect to know wifi.
// 3 as [STA] mode(connected)
// 4 as [STA] in the first 20s, if there is none, setting up [AP] mode.
#define DEFAULT_WIFI_MODE 1

String MAC_ADDRESS;
IPAddress IP_ADDRESS;
byte   WIFI_MODE;
int    WIFI_RSSI;

// true: robot won't react to web heartbeat.
bool jsonCtrlMode = true;
String jsonFeedbackWeb;

// === === === INFO === === ===
// MAX_SPEED = 1.32 -> 1.2
// A:left, B:right


// === === === GIMBAL CTRL === === ===
float gimbalGoalX = 0;
float gimbalGoalY = 0;


// === === === COMMAND DEFINITION === === ===
#define EMERGENCY_STOP 0

#define GIMBAL_CTRL    1
#define BASE_GIMBAL_CTRL  2
#define OLED_SET       3
#define OLED_DEFAULT  -3

#define LIGHT_PWM_CTRL 41

#define BUS_SERVO_CTRL   50
#define BUS_SERVO_SYNC   51
#define BUS_SERVO_MID   -5
#define BUS_SERVO_SCAN   52
#define BUS_SERVO_INFO   53
#define BUS_SERVO_ID_SET 54
#define BUS_SERVO_TORQUE_LOCK  55
#define BUS_SERVO_TORQUE_LIMIT 56
#define BUS_SERVO_MODE         57
#define BUS_SERVO_MID_SET      58
#define BUS_SERVO_STOP         59

#define WIFI_SCAN        60
#define WIFI_TRY_STA     61
#define WIFI_AP_DEFAULT  62
#define WIFI_INFO        65
#define WIFI_OFF         66

#define INA219_INFO    70
#define IMU_INFO       71
#define DEVICE_INFO    74


// bool emergencyStopFlag = 0;


// === === === DEBUG MODE SET === === ===
bool debugOutput = true;


// === === === MOTOR PIN DEFINITION === === ===
const uint16_t PWMA = 25;         // Motor A PWM control  Orange
const uint16_t AIN2 = 17;         // Motor A input 2      Brown
const uint16_t AIN1 = 21;         // Motor A input 1      Green
const uint16_t BIN1 = 22;         // Motor B input 1       Yellow
const uint16_t BIN2 = 23;         // Motor B input 2       Purple
const uint16_t PWMB = 26;         // Motor B PWM control   White

const uint16_t AENCA = 35;        // Encoder A input      Yellow
const uint16_t AENCB = 34;

const uint16_t BENCB = 16;        // Encoder B input      Green
const uint16_t BENCA = 27;

int freq = 100000;
int channel_A = 5;
int channel_B = 6;


// === === === ROBOT IIC INTERFACE === === ===
#define S_SCL   33
#define S_SDA   32

float INA219_DATA_V = -1;
int   IMU_Roll = 100;
int   IMU_Pitch = 100;
int   IMU_Yaw = 100;

int   IMU_Temp = 100;

IMU_ST_ANGLES_DATA stAngles;
IMU_ST_SENSOR_DATA stGyroRawData;
IMU_ST_SENSOR_DATA stAccelRawData;
IMU_ST_SENSOR_DATA stMagnRawData;
IMU_Q_DATA qRawData;


// <<<<<<<<<<=========9DOF-IMU===========>>>>>>>>>>
void getIMU(){
  imuDataGet( &stAngles, &stGyroRawData, &stAccelRawData, &stMagnRawData, &qRawData);
  IMU_Temp = QMI8658_readTemp();
  IMU_Roll  = stAngles.fRoll;
  IMU_Pitch = stAngles.fPitch;
  IMU_Yaw   = stAngles.fYaw;
}