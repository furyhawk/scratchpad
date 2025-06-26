#ifndef __INPUT_EVENT_BUFFER_H
#define __INPUT_EVENT_BUFFER_H

#include "input_system.h"

#define BUFFER_SIZE 10

typedef struct InputEventBuffer{
	InputEvent buffer[BUFFER_SIZE];
	volatile unsigned int pW;
	volatile unsigned int pR;
}InputEventBuffer;

int GetInputEvent(PInputEvent ptInputEvent);

int PutInputEvent(PInputEvent ptInputEvent);

#endif
