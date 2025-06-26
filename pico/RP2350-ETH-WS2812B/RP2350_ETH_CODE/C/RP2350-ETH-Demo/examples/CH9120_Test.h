/*****************************************************************************
* | File      	:	CH9120_Test.h
* | Author      :   Waveshare team
* | Function    :   RP2350 ETH test Demo
* | Info        :
*----------------
* |	This version:   V1.0
* | Date        :   2024-11-13
* | Info        :   
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
******************************************************************************/
#ifndef _CH9120_TEST_H_
#define _CH9120_TEST_H_

#include "CH9120.h"

extern UCHAR CH9120_LOCAL_IP[4];
extern UCHAR CH9120_GATEWAY[4];
extern UCHAR CH9120_SUBNET_MASK[4];
extern UCHAR CH9120_TARGET_IP[4];
extern UWORD CH9120_PORT1;
extern UWORD CH9120_TARGET_PORT;
extern UDOUBLE CH9120_BAUD_RATE;

int Pico_ETH_CH9120_test(void);

#endif
