#ifndef __DS18B20_H__
#define __DS18B20_H__

#include "lpc17xx.h"

#define DS18B20_PIN			0x20000000

#define HIGH			0x01
#define LOW				0x00
#define DS18B20_DQ(x)	((x) ? (LPC_GPIO4->FIOSET = DS18B20_PIN) : \
                               (LPC_GPIO4->FIOCLR = DS18B20_PIN))

#define OUT				0x01
#define IN				0x00
#define DS18B20_DIR(x)	((x) ? (LPC_GPIO4->FIODIR |= DS18B20_PIN) : \
                               (LPC_GPIO4->FIODIR &= (~DS18B20_PIN)))

void DS18B20_Init(void);
int16_t DS18B20_TemOut(void);
void DS18B20_Delay(uint32_t time);
#endif
