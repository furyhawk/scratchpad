#include "CH9120.h"

UCHAR CH9120_Mode = TCP_CLIENT; //Optional:TCP_SERVER、TCP_CLIENT、UDP_SERVER、UDP_CLIENT
UCHAR CH9120_LOCAL_IP[4] = {192, 168, 1, 200};    // LOCAL IP
UCHAR CH9120_GATEWAY[4] = {192, 168, 1, 1};       // GATEWAY
UCHAR CH9120_SUBNET_MASK[4] = {255, 255, 255, 0}; // SUBNET MASK
UCHAR CH9120_TARGET_IP[4] = {192, 168, 1, 10};    // TARGET_IP
UWORD CH9120_PORT1 = 1000;                        // LOCAL PORT1
UWORD CH9120_TARGET_PORT = 2000;                  // TARGET PORT
UDOUBLE CH9120_BAUD_RATE = 115200;                // BAUD RATE

UCHAR tx[8] = {0x57, 0xAB};

/******************************************************************************
function:	Send four bytes
parameter:
    data: parameter
    command: command code
Info:  Set mode, enable port, clear serial port, switch DHCP, switch port 2
******************************************************************************/
void CH9120_TX_4_bytes(UCHAR data, int command)
{
    for (int i = 2; i < 4; i++)
    {
        if (i == 2)
            tx[i] = command;
        else
            tx[i] = data;
    }
    DEV_Delay_ms(10);
    for (int o = 0; o < 4; o++)
        uart_putc(UART_ID1, tx[o]);
    DEV_Delay_ms(10);
    for (int i = 2; i < 4; i++)
        tx[i] = 0;
}

/******************************************************************************
function:	Send five bytes
parameter:
    data: parameter
    command: command code
Info:  Set the local port and target port
******************************************************************************/
void CH9120_TX_5_bytes(UWORD data, int command)
{
    UCHAR Port[2];
    Port[0] = data & 0xff;
    Port[1] = data >> 8;
    for (int i = 2; i < 5; i++)
    {
        if (i == 2)
            tx[i] = command;
        else
            tx[i] = Port[i - 3];
    }
    DEV_Delay_ms(10);
    for (int o = 0; o < 5; o++)
        uart_putc(UART_ID1, tx[o]);
    DEV_Delay_ms(10);
    for (int i = 2; i < 5; i++)
        tx[i] = 0;
}
/******************************************************************************
function:	Send seven bytes
parameter:
    data: parameter
    command: command code
Info:  Set the IP address, subnet mask, gateway,
******************************************************************************/
void CH9120_TX_7_bytes(UCHAR data[], int command)
{
    for (int i = 2; i < 7; i++)
    {
        if (i == 2)
            tx[i] = command;
        else
            tx[i] = data[i - 3];
    }
    DEV_Delay_ms(10);
    for (int o = 0; o < 7; o++)
        uart_putc(UART_ID1, tx[o]);
    DEV_Delay_ms(10);
    for (int i = 2; i < 7; i++)
        tx[i] = 0;
}

/******************************************************************************
function:	CH9120_TX_BAUD
parameter:
    data: parameter
    command: command code
Info:  Set baud rate
******************************************************************************/
void CH9120_TX_BAUD(UDOUBLE data, int command)
{
    UCHAR Port[4];
    Port[0] = (data & 0xff);
    Port[1] = (data >> 8) & 0xff;
    Port[2] = (data >> 16) & 0xff;
    Port[3] = data >> 24;

    for (int i = 2; i < 7; i++)
    {
        if (i == 2)
            tx[i] = command;
        else
            tx[i] = Port[i - 3];
    }
    DEV_Delay_ms(10);
    for (int o = 0; o < 7; o++)
        uart_putc(UART_ID1, tx[o]);
    DEV_Delay_ms(10);
    for (int i = 2; i < 7; i++)
        tx[i] = 0;
}

/******************************************************************************
function:	CH9120_Start
parameter:
Info:  Start configuration Parameters
******************************************************************************/
void CH9120_Start()
{
    gpio_put(RES_PIN, 1);
    gpio_put(CFG_PIN, 0);
    DEV_Delay_ms(500);
}

/******************************************************************************
function:	CH9120_End
parameter:
Info:  Updating configuration Parameters
******************************************************************************/
void CH9120_End()
{
    tx[2] = 0x0d;
    uart_puts(UART_ID1, tx);
    DEV_Delay_ms(200);
    tx[2] = 0x0e;
    uart_puts(UART_ID1, tx);
    DEV_Delay_ms(200);
    tx[2] = 0x5e;
    uart_puts(UART_ID1, tx);
    DEV_Delay_ms(200);
    gpio_put(CFG_PIN, 1);
}

/******************************************************************************
Function:	CH9120_SetMode
Parameters:
    Mode: Mode parameter
Info:  Configure communication mode
******************************************************************************/
void CH9120_SetMode(UCHAR Mode)
{
    CH9120_TX_4_bytes(Mode, Mode1); //Mode
    DEV_Delay_ms(100);
}

/******************************************************************************
Function:	CH9120_SetLocalIP
Parameters:
    CH9120_LOCAL_IP: Local IP parameter
Info:  Configure local IP
******************************************************************************/
void CH9120_SetLocalIP(UCHAR CH9120_LOCAL_IP[])
{
    CH9120_TX_7_bytes(CH9120_LOCAL_IP, LOCAL_IP); //LOCALIP
    DEV_Delay_ms(100);
}

/******************************************************************************
Function:	CH9120_SetSubnetMask
Parameters:
    CH9120_SUBNET_MASK: SUBNET MASK parameter
Info:  Configure subnet mask
******************************************************************************/
void CH9120_SetSubnetMask(UCHAR CH9120_SUBNET_MASK[])
{
    CH9120_TX_7_bytes(CH9120_SUBNET_MASK, SUBNET_MASK); //SUBNET MASK
    DEV_Delay_ms(100);
}

/******************************************************************************
Function:	CH9120_SetGateway
Parameters:
    CH9120_GATEWAY: Gateway parameter
Info:  Configure gateway
******************************************************************************/
void CH9120_SetGateway(UCHAR CH9120_GATEWAY[])
{
    CH9120_TX_7_bytes(CH9120_GATEWAY, GATEWAY); //GATEWAY
    DEV_Delay_ms(100);
}

/******************************************************************************
Function:	CH9120_SetTargetIP
Parameters:
    CH9120_TARGET_IP: Target IP parameter
Info:  Configure target IP
******************************************************************************/
void CH9120_SetTargetIP(UCHAR CH9120_TARGET_IP[])
{
    CH9120_TX_7_bytes(CH9120_TARGET_IP, TARGET_IP1); //TARGET IP
    DEV_Delay_ms(100);
}

/******************************************************************************
Function:	CH9120_SetLocalPort
Parameters:
    CH9120_PORT: Local Port parameter
Info:  Configure local port number
******************************************************************************/
void CH9120_SetLocalPort(UWORD CH9120_PORT)
{
    CH9120_TX_5_bytes(CH9120_PORT, LOCAL_PORT1); //Local port
    DEV_Delay_ms(100);
}

/******************************************************************************
Function:	CH9120_SetTargetPort
Parameters:
    CH9120_TARGET_PORT: Target Port parameter
Info:  Configure target port number
******************************************************************************/
void CH9120_SetTargetPort(UWORD CH9120_TARGET_PORT)
{
    CH9120_TX_5_bytes(CH9120_TARGET_PORT, TARGET_PORT1); //Target port
    DEV_Delay_ms(100);
}

/******************************************************************************
Function:	CH9120_SetBaudRate
Parameters:
    CH9120_BAUD_RATE: Baud Rate parameter
Info:  Configure communication baud rate
******************************************************************************/
void CH9120_SetBaudRate(UDOUBLE CH9120_BAUD_RATE)
{
    CH9120_TX_BAUD(CH9120_BAUD_RATE, UART1_BAUD1); //Port 1 baud rate
    DEV_Delay_ms(100);
}

/**
 * delay x ms
**/
void DEV_Delay_ms(UDOUBLE xms)
{
    sleep_ms(xms);
}

void DEV_Delay_us(UDOUBLE xus)
{
    sleep_us(xus);
}

/******************************************************************************
function:	CH9120_init
parameter:
Info:  Initialize CH9120
******************************************************************************/
void CH9120_init(void)
{
    stdio_init_all();

    uart_init(UART_ID1, Inti_BAUD_RATE);
    gpio_set_function(UART_TX_PIN1, GPIO_FUNC_UART);
    gpio_set_function(UART_RX_PIN1, GPIO_FUNC_UART);

    gpio_init(CFG_PIN);
    gpio_init(RES_PIN);
    gpio_set_dir(CFG_PIN, GPIO_OUT);
    gpio_set_dir(RES_PIN, GPIO_OUT);

    CH9120_Start();
    CH9120_SetMode(CH9120_Mode);               //Mode
    CH9120_SetLocalIP(CH9120_LOCAL_IP);       //LOCALIP
    CH9120_SetSubnetMask(CH9120_SUBNET_MASK); //SUBNET MASK
    CH9120_SetGateway(CH9120_GATEWAY);        //GATEWAY
    CH9120_SetTargetIP(CH9120_TARGET_IP);     //TARGET IP
    CH9120_SetLocalPort(CH9120_PORT1);        //Local port
    CH9120_SetTargetPort(CH9120_TARGET_PORT); //Target port
    CH9120_SetBaudRate(CH9120_BAUD_RATE);     //Port 1 baud rate
    CH9120_End();

    uart_set_baudrate(UART_ID1, Transport_BAUD_RATE);
    while (uart_is_readable(UART_ID1))
    {
        UBYTE ch1 = uart_getc(UART_ID1);
    }
}


/******************************************************************************
function:	RX_TX
parameter:
Info:  Serial port 1 and serial port 2 receive and dispatch
******************************************************************************/
void RX_TX()
{
    while (1)
    {
        while (uart_is_readable(UART_ID1))
        {
            UBYTE ch1 = uart_getc(UART_ID1);
            if (uart_is_writable(UART_ID1))
            {
                uart_putc(UART_ID1, ch1);
            }
        }
    }
}