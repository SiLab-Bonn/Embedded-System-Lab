/*******************************************************/
/* file: ports.h                                       */
/* abstract:  This file contains extern declarations   */
/*            for providing stimulus to the JTAG ports.*/
/*******************************************************/

#ifndef ports_dot_h
#define ports_dot_h

#include "stdio.h"
#include <bcm_host.h>
#include <fcntl.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/mman.h>


/* GPIO numbers for each signal. Negative values are invalid */
static int tms_gpio =  1;
static int tck_gpio =  0;
static int tdo_gpio = 27;
static int tdi_gpio = 26;

void set_gpio_mode(int pin, int mode);
void set_gpio_pull(int pin, int mode);
void set_gpio_out(int pin, int level);
bool get_gpio_in(int pin);
bool setup_gpio_regs();
void cleanup_gpio_regs(int def);


/* set the port "p" (TCK, TMS, or TDI) to val (0 or 1) */
extern void setPort(short p, short val);

/* read the TDO bit and store it in val */
extern unsigned char readTDOBit();

/* make clock go down->up->down*/
extern void pulseClock();

/* read the next byte of data from the xsvf file */
extern void readByte(unsigned char *data);

extern void waitTime(long microsec);

#endif
