#include "input_event_buffer.h"

static InputEventBuffer g_tInputBuffer;

int PutInputEvent(PInputEvent ptInputEvent)
{
    unsigned int i = (g_tInputBuffer.pW + 1) % BUFFER_SIZE;

	if (!ptInputEvent)
		return -1;
	
    if(i != g_tInputBuffer.pR)    // The ring buffer is not full
    {
        g_tInputBuffer.buffer[g_tInputBuffer.pW] = *ptInputEvent;
        g_tInputBuffer.pW = i;
		return 0;
    }
	return -1;
}


int GetInputEvent(PInputEvent ptInputEvent)
{

	if (!ptInputEvent)
		return -1;

	
    if(g_tInputBuffer.pR == g_tInputBuffer.pW)
    {
        return -1;
    }
    else
    {
        *ptInputEvent = g_tInputBuffer.buffer[g_tInputBuffer.pR];
        g_tInputBuffer.pR = (g_tInputBuffer.pR + 1) % BUFFER_SIZE;
        return 0;
    }
}