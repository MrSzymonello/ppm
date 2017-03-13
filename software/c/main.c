#include "LPC17xx.h"
#include "uart.h"
#include "stdlib.h"
#include "base64.h"

#define SAMPLESNO 20000
#define SAMPLESSIZE 30000
#define ADC_VALUE_MAX 0xFFF

volatile uint8_t StartPPM =  0;
volatile uint16_t ADC1 = 0;
volatile uint16_t ADC2 = 0;
volatile uint8_t ADCTab[SAMPLESSIZE];
volatile uint32_t ADCTabCounter = 0;
volatile uint32_t SamplesCounter = 0;
volatile uint32_t msTicks; //counts 1 msec SysTicks

void config_GPIO(void);
void config_Timer0(void);
void config_ADC(void);

void SysTick_Handler(void)
{
 	msTicks++; //increment counter necessary in Delay function
}

//delays number of SysTicks (happens every 1 ms)
__INLINE static void Delay (uint32_t delayTicks)
{
 	uint32_t curTicks;
 	curTicks = msTicks;
 	while ((msTicks - curTicks) < delayTicks);
}

__INLINE static void RELAY_On (void)
{
	LPC_GPIO2->FIOSET |= 1 << 11; //set voltage on pin 2.11
}

__INLINE static void RELAY_Off (void)
{
	LPC_GPIO2->FIOCLR |= 1 << 11; //set 0V on pin 2.11
}

__INLINE static void POLARIZE_On (void)
{
	LPC_GPIO1->FIOSET |= 1 << 0; //set voltage on pin 1.0
}

__INLINE static void POLARIZE_Off (void)
{
	LPC_GPIO1->FIOCLR |= 1 << 0; //set 0V on pin 1.0
}

int main (void)
{
	//delay times
	uint32_t t1 = 20;
	uint32_t t2 = 200;
	uint32_t t3 = 6000;
	uint32_t t4 = 20;
	uint32_t t5 = 10;

	unsigned char UARTinputBuffer[15];
	uint8_t UARTcounter = 0;	
	unsigned char UARTbyte = 0;
	int i = 0;
	char out[4];
	char in[3];			

	//setup SysTick Timer for 1 msec interrupts
	SysTick_Config(SystemCoreClock / 1000);		
	SystemInit();
	config_GPIO();
	UART2_Init();		
	config_Timer0();
	config_ADC();
	
	LPC_TIM0->TCR = 0x2; //timer0 in reset mode
	LPC_TIM0->TCR = 0; //timer0 disabled

	while(1)
	{
		if(StartPPM == 1)
		{
			Delay(t1);
			RELAY_On();
			Delay(t2);
			POLARIZE_On();
			Delay(t3); //now current flows through the coil
			POLARIZE_Off();
			Delay(t4);
			RELAY_Off();
			Delay(t5);
			
			//start ADC sampling at 5 kHz			
			LPC_TIM0->TCR = 0x2; //timer0 in reset mode			
			LPC_TIM0->TCR = 1; //timer0 enabled
			while(SamplesCounter < SAMPLESNO);			
			LPC_TIM0->TCR = 0x2; //timer0 in reset mode			
			LPC_TIM0->TCR = 0; //timer0 disabled

			//encode results to base64 and send them via UART								   
			for(i=0; i < SAMPLESSIZE; i+=3)
			{
				in[0] = ADCTab[i];
				in[1] = ADCTab[i+1];
				in[2] = ADCTab[i+2];																

				base64_encode(in, out);
				UART2_SendString(out);
			}					  

			//reset counters and flags
			ADCTabCounter=0;
			SamplesCounter=0;
			StartPPM = 0;
		}

		//look for incoming data via UART
		if(LPC_UART2->LSR & 0x01)
		{
			do
			{
				UARTbyte = LPC_UART2->RBR;				
				if(UARTcounter < 15) UARTinputBuffer[UARTcounter++] = UARTbyte;				
			}
			while(LPC_UART2->LSR & 0x01);
			   
			if(UARTinputBuffer[0] == 'S') StartPPM = 1;
			for(i=0; i< UARTcounter; i++)
				UARTinputBuffer[i] = 0;
			UARTcounter = 0;
		}						 
	}
}

//configure pins for RELAY and POLARIZE commands
void config_GPIO(void)
{
	LPC_GPIO1->FIODIR = 1 << 0; //pin 1.0 works as output
	LPC_GPIO2->FIODIR = 1 << 11; //pin 2.11 works as output
}

void config_Timer0(void)
{
	LPC_SC->PCONP |= (1 << 1); //power on Timer0
	LPC_SC->PCLKSEL0 |= (1 << 2); //Timer Clock = SystemCoreClock (100MHz)
	
	//Timer0 configured to generate a square wave on MAT0.1 at a rate of 5 kHz
	LPC_TIM0->TCR = 0x2; //Timer0 in reset mode
	LPC_TIM0->TCR = 0; //timer mode
	LPC_TIM0->PR = 200-1; //prescaler	
	LPC_TIM0->MCR = (1 << 4); //reset on MR1	
	LPC_TIM0->MR1 = 25-1; //match register	
	LPC_TIM0->EMR = (1 << 1) | (0x3 << 6); //toggle EM1 on match
}

void config_ADC(void)
{
	LPC_SC->PCONP |= (1 << 12); //power on ADC
	LPC_SC->PCLKSEL0 |= (3 << 24); //ADC Clock = SystemCoreClock/8 (12.5 MHz)	  	
  	LPC_PINCON->PINSEL3 |= (3 << 30); //P1.31 as AD0.5

	//this register controls pull-up/pull-down resistor configuration for Port 1 pins 16 to 31.
	//00 - pin has a pull-up resistor enabled.
	//01 - pin has repeater mode enabled.
	//10 - pin has neither pull-up nor pull-down.
	//11 - has a pull-down resistor enabled.
	LPC_PINCON->PINMODE3 |= (3 << 30); //P1.31 has a pull-down resistor enabled

	//configure AD Control Register	
	LPC_ADC->ADCR = 0; //reset AD control register
	//AD5+AD0+Power-up AD converter+Start conversion triggered by MAT signal (on rising edge)
	LPC_ADC->ADCR = (1 << 5) | (1 << 0) | (1 << 21) | (0 << 27);
	LPC_ADC->ADCR |= (4 << 24); // Start conversion when the edge selected by bit 27 occurs on MAT0.1

	//configure interrupts
	LPC_ADC->ADINTEN |= (1 << 5); //enable AD05 interrupt
	LPC_ADC->ADINTEN &= ~(1 << 8); //only the individual ADC channels enabled by ADINTEN7:0 will generate interrupts
	NVIC_EnableIRQ(ADC_IRQn);		
		
	LPC_PINCON->PINSEL3 |= (3 << 26); //selects MAT0.1 function on GPIO Port 1.29
}

//take voltage samples here
void ADC_IRQHandler(void)
{
	if(LPC_ADC->ADDR5 & (1 << 31))
	{	    
		if(SamplesCounter%2 == 0)
		{
			ADC1 = (LPC_ADC->ADGDR >> 4) & ADC_VALUE_MAX;
		}
		else
		{
			ADC2 = (LPC_ADC->ADGDR >> 4) & ADC_VALUE_MAX;
			
			//ADC1 and ADC2 are saved as 3 bytes			
			ADCTab[ADCTabCounter] = ADC1 >> 4;
			ADCTab[ADCTabCounter+1] = ((ADC1 & 0xF) << 4) | ((ADC2 >> 8) & 0xF);
			ADCTab[ADCTabCounter+2] = ADC2 & 0xFF;
			ADCTabCounter+=3;
		}	  	
		SamplesCounter++;
	}
}
