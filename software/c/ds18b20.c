#include "ds18b20.h"

// code taken and adapted from examples attached to the WB-LPC1768 Beemer development board

// delay using TIM1
// delay time is specified in microseconds
void DS18B20_Delay(uint32_t time)
{
	LPC_TIM1->TCR = 0x02;
	LPC_TIM1->IR = 0x01;
	LPC_TIM1->CTCR = 0x00;
	LPC_TIM1->PR = 0x00;
	LPC_TIM1->TC = 0x00;
	LPC_TIM1->MR0 = time*25;
	LPC_TIM1->MCR = 0x07;
	LPC_TIM1->TCR = 0x01;

	while(!(LPC_TIM1->IR & 0x01));
	LPC_TIM1->IR = 0x01;
}

// reset sequence
// returns 1 when ds18b20 does not respond, 0 - otherwise
uint8_t DS18B20_Reset(void)
{
	uint8_t flag;

	DS18B20_DIR(OUT);
	DS18B20_DQ(HIGH);
	DS18B20_Delay(3);
	DS18B20_DQ(LOW);
	DS18B20_Delay(500);
	DS18B20_DQ(HIGH);

	DS18B20_DIR(IN);
	DS18B20_Delay(30);
	flag = !(!(LPC_GPIO4->FIOPIN & DS18B20_PIN));
	DS18B20_Delay(500);
	return flag;
}

// writes one byte to the scratchpad
// three consecutive calls to this function
// writes into TH byte, TL byte and configuration byte
void DS18B20_WriteData(unsigned char wData)
{
	int i;
	for(i=8; i>0; i--)
	{
		DS18B20_DIR(OUT);
		DS18B20_DQ(HIGH);
		DS18B20_Delay(3);
		DS18B20_DQ(LOW);
		DS18B20_Delay(3);
		DS18B20_DQ(wData&0x01);
		DS18B20_Delay(50);
		DS18B20_DQ(HIGH);
		DS18B20_Delay(3);
		wData >>= 1;
	}
}

// reads one byte from the scratchpad
// consecutive calls to this functions returns bytes from scratchpad
// starting from byte 0 to byte 8
uint8_t DS18B20_ReadData(void)
{
	int i, TmepData = 0;
	for(i=8; i>0; i--)
	{
		TmepData >>= 1;
		DS18B20_DIR(OUT);
		DS18B20_DQ(HIGH);
		DS18B20_Delay(3);
		DS18B20_DQ(LOW);
		DS18B20_Delay(3);
		DS18B20_DQ(HIGH);

		DS18B20_DIR(IN);
		DS18B20_Delay(6);
		if(LPC_GPIO4->FIOPIN & DS18B20_PIN)
		{
			TmepData |= 0x80;
		}
		DS18B20_Delay(50);               
	}
	return TmepData;
}

// initializes ds18b20 sensor by setting TH, TL and configuration byte (resolution)
void DS18B20_Init(void)
{
	DS18B20_Reset();
	DS18B20_WriteData(0xcc);	// skip ROM command
	DS18B20_WriteData(0x4e);	// write scratchpad command
	DS18B20_WriteData(0x20);	// write into TH register
	DS18B20_WriteData(0x00);	// write into TL register
	DS18B20_WriteData(0x7f);	// set 12-bit resolution
	DS18B20_Reset();
}

// returns temperature (multiplied by 16) as 16-bit signed integer
int16_t DS18B20_TemOut(void)
{
	uint16_t t[2];		
	
	DS18B20_Reset();
	DS18B20_WriteData(0xcc);	// skip ROM command
	DS18B20_WriteData(0x44);	// initiate temperature conversion
	DS18B20_Delay(400000);
    
	DS18B20_Reset();
	DS18B20_WriteData(0xcc);	// skip ROM command
	DS18B20_WriteData(0xbe);	// read scratchpad command

	t[0] = DS18B20_ReadData();	// temperature LSB
	t[1] = DS18B20_ReadData();	// temperature MSB

	return t[1] * 0x0100 + t[0];
}
