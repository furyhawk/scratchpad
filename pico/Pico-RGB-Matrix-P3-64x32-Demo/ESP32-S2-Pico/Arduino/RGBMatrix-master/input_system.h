#ifndef __INPUT_SYSTEM_H
#define __INPUT_SYSTEM_H

#define INPUT_BUF_LEN 10

#ifndef NULL
#define NULL (void *)0
#endif

typedef enum
{
	INPUT_EVENT_TYPE_KEY,
	INPUT_EVENT_TYPE_IR
}INPUT_EVENT_TYPE;


typedef struct InputEnent{
	INPUT_EVENT_TYPE eType;
	int iKey;
	int iPressure;
	char IR_Value;
	char str[INPUT_BUF_LEN];
}InputEvent,*PInputEvent;


typedef struct InputDevice{
	char *name;
	int (*GetInputEvent)(PInputEvent ptInputEvent);
	int (*DeviceInit)(void);
	struct InputDevice *pNext;
}InputDevice,*PInputDevice;




void InputDeviceRegister(PInputDevice ptInputDevice);
void InitInputDevices(void);

#endif