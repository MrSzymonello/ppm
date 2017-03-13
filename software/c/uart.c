#include "lpc17xx.h"
#include "uart.h"

void UART0_Init (void)
{
    LPC_PINCON->PINSEL0 |= (1 << 4); //Pin P0.2 used as TXD0 (UART0)
    LPC_PINCON->PINSEL0 |= (1 << 6); //Pin P0.3 used as RXD0 (UART0)
  
	//speed 115200
  	LPC_UART0->LCR  = 0x83;
	LPC_UART2->DLM  = 0;
    LPC_UART2->DLL  = 27;
    LPC_UART0->LCR  = 0x03;
    LPC_UART0->FCR  = 0x06; 				   
}

int UART0_SendByte (int ucData)
{
	while (!(LPC_UART0->LSR & 0x20));
    return (LPC_UART0->THR = ucData);
}

int UART0_GetChar (void) 
{
  	while (!(LPC_UART0->LSR & 0x01));
  	return (LPC_UART0->RBR);
}

void UART0_SendString (unsigned char *s) 
{
  	while (*s != 0) 
	{
   		UART0_SendByte(*s++);
	}
}

void UART2_Init (void)
{	
	LPC_SC->PCLKSEL1 |= (2 << 16); //UART2 Clock = SystemCoreClock/2 (50 MHz)
	
	LPC_PINCON->PINSEL0 |= (1 << 20); //Pin P0.10 used as TXD2 (UART2)
	LPC_PINCON->PINSEL0 |= (1 << 22); //Pin P0.11 used as RXD2 (UART2)

	LPC_SC->PCONP |= (1 << 24);
	
	//speed 115200
	LPC_UART2->LCR  = 0x83;
	LPC_UART2->DLM  = 0;
	LPC_UART2->DLL  = 27;
	LPC_UART2->LCR  = 0x03;
	LPC_UART2->FCR  = 0x07;
}

int UART2_SendByte (int ucData)
{
	while (!(LPC_UART2->LSR & 0x20));
	return (LPC_UART2->THR = ucData);
}

int UART2_GetChar (void) 
{
	while (!(LPC_UART2->LSR & 0x01));
	return (LPC_UART2->RBR);
}

void UART2_SendString (unsigned char *s) 
{
	while (*s != 0) 
	{
		UART2_SendByte(*s++);
	}
}

void UART3_Init (void)
{
	LPC_PINCON->PINSEL0 |= 2;        //Pin P0.0 used as TXD3 (UART3)
	LPC_PINCON->PINSEL0 |= (2 << 2); //Pin P0.1 used as RXD3 (UART3)

	LPC_SC->PCONP |= (1 << 25);

	//speed 115200
	LPC_UART3->LCR  = 0x83;
	LPC_UART2->DLM  = 0;
	LPC_UART2->DLL  = 27;
	LPC_UART3->LCR  = 0x03;
	LPC_UART3->FCR  = 0x06;
}

int UART3_SendByte (int ucData)
{
	while (!(LPC_UART3->LSR & 0x20));
	return (LPC_UART3->THR = ucData);
}

int UART3_GetChar (void) 
{
	while (!(LPC_UART3->LSR & 0x01));
	return (LPC_UART3->RBR);
}

void UART3_SendString (unsigned char *s) 
{
	while (*s != 0) 
	{
		UART3_SendByte(*s++);
	}
}
