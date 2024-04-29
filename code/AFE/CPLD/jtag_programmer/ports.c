/*******************************************************/
/* file: ports.c                                       */
/* abstract:  This file contains the routines to       */
/*            output values on the JTAG ports, to read */
/*            the TDO bit, and to read a byte of data  */
/*            from the prom                            */
/* Revisions:                                          */
/* 12/01/2008:  Same code as before (original v5.01).  */
/*              Updated comments to clarify instructions.*/
/*              Add print in setPort for xapp058_example.exe.*/
/*******************************************************/
#include "ports.h"
/*#include "prgispx.h"*/



#pragma  GCC diagnostic ignored "-Wpointer-arith"
//warning disable

// start address of the I/O peripheral register space on the VideoCore bus
#define BUS_REG_BASE    0x7E000000
// start address of the I/O peripheral register space seen from the CPU bus
#define PHYS_REG_BASE   0xFE000000 // RPi 4
// start address of the GPIO register space on the VideoCore bus
#define GPIO_BASE       0x7E200000
// address offsets for the individual registers
#define GPIO_FSEL0      0x00  // mode selsction GPIO 0-9
#define GPIO_FSEL1      0x04  // mode selsction GPIO 10-19
#define GPIO_FSEL2      0x08  // mode selsction GPIO 20-29
#define GPIO_SET0       0x1C  // set outputs to '1' GPIO 0-31
#define GPIO_CLR0       0x28  // set outputs to '0' GPIO 0-31
#define GPIO_LEV0       0x34  // get input states GPIO 0-31
#define GPIO_PUD0       0xE4  // pull-up/down enable
#define GPIO_PUD1       0xE8  // pull-up/down enable
#define GPIO_FSEL_BITS  3
#define GPIO_PUD_BITS   2
#define GPIO_PU_OFF     0x0
#define GPIO_PU_DOWN    0x2
#define GPIO_PU_UP      0x1   

// #define DEBUG 

uint32_t *gpio_virt_addr_ptr;  // pointer to virtual address
uint32_t *gpfsel0;
uint32_t *gpfsel1;
uint32_t *gpfsel2;
uint32_t gpfsel0_prev;
uint32_t gpfsel1_prev;
uint32_t gpfsel2_prev;
uint32_t *gpset0;
uint32_t *gpclr0;
uint32_t *gplev0;
uint32_t *gppud0;
uint32_t *gppud1;
uint32_t gppud0_prev;
uint32_t gppud1_prev;


/* GPIO numbers for each signal. Negative values are invalid */
extern int tms_gpio;
extern int tck_gpio;
extern int tdo_gpio;
extern int tdi_gpio;


bool setup_gpio_regs()
{
  uint32_t  gpio_phys_addr;  // GPIO register CPU bus address 

  int file_descriptor;  // handle for memory mapping

  // calculate the physical address from the bus address
  gpio_phys_addr = GPIO_BASE - BUS_REG_BASE + PHYS_REG_BASE;

  // get a handle to the physical memory space
  if ((file_descriptor = open("/dev/mem", O_RDWR|O_SYNC|O_CLOEXEC)) < 0)  // requires root permissions ("sudo ...")
 // if ((file_descriptor = open("/dev/gpiomem", O_RDWR|O_SYNC|O_CLOEXEC)) < 0)  // only requires *gpio' group
  {
      printf("Error: can't open /dev/mem, run using sudo\n");
      return false;
  }

  // allocate virtual memory and map the physical address to it
  gpio_virt_addr_ptr = mmap(0, 0x1000, PROT_WRITE|PROT_READ, MAP_SHARED, file_descriptor, gpio_phys_addr);
//  gpio_virt_addr_ptr = mmap(0, 0x1000, PROT_WRITE|PROT_READ, MAP_SHARED, file_descriptor, 0); // gpiomem automatically points to g'pio_phys_addr'
  close(file_descriptor);

  // check the results
  if (gpio_virt_addr_ptr == MAP_FAILED)
  {
      printf("Error: can't map memory\n");
      return false;
  }
  #ifdef DEBUG 
    printf("Success: Map %p -> %p\n", (void *)gpio_phys_addr, (void *)gpio_virt_addr_ptr);
  #endif

  // define variables to access the specific registers
  gpfsel0 = (uint32_t*)((void *)gpio_virt_addr_ptr + GPIO_FSEL0);
  gpfsel1 = (uint32_t*)((void *)gpio_virt_addr_ptr + GPIO_FSEL1);
  gpfsel2 = (uint32_t*)((void *)gpio_virt_addr_ptr + GPIO_FSEL2);
  gpset0  = (uint32_t*)((void *)gpio_virt_addr_ptr + GPIO_SET0);
  gpclr0  = (uint32_t*)((void *)gpio_virt_addr_ptr + GPIO_CLR0);
  gplev0  = (uint32_t*)((void *)gpio_virt_addr_ptr + GPIO_LEV0);
  gppud0  = (uint32_t*)((void *)gpio_virt_addr_ptr + GPIO_PUD0);
  gppud1  = (uint32_t*)((void *)gpio_virt_addr_ptr + GPIO_PUD1);

  // store values for clean-up
  gpfsel0_prev = *gpfsel0;
  gpfsel1_prev = *gpfsel1;
  gpfsel2_prev = *gpfsel2;
  gppud0_prev = *gppud0;
  gppud1_prev = *gppud1;

  #ifdef DEBUG
    // print virtual addresses and register content
    printf("GPFSEL0 (%p): 0x%08x \n", (void *)gpfsel0, *gpfsel0);
    printf("GPFSEL1 (%p): 0x%08x \n", (void *)gpfsel1, *gpfsel1);
    printf("GPFSEL2 (%p): 0x%08x \n", (void *)gpfsel2, *gpfsel2);
    printf("GPSET0  (%p): 0x%08x \n", (void *)gpset0, *gpset0);
    printf("GPCLR0  (%p): 0x%08x \n", (void *)gpclr0, *gpclr0);
    printf("GPLEV0  (%p): 0x%08x \n", (void *)gplev0, *gplev0);
  #endif  

   set_gpio_mode(tdo_gpio, 0);  // TDO input
   set_gpio_pull(tdo_gpio, GPIO_PU_UP);  // ???

   set_gpio_out(tck_gpio, 1);  // was 0
   set_gpio_out(tms_gpio, 1);
   set_gpio_out(tdi_gpio, 1);  // was 0

   set_gpio_mode(tck_gpio, 1); // TCK output 
   set_gpio_mode(tms_gpio, 1); // TMS output 
   set_gpio_mode(tdi_gpio, 1); // TDI output
   set_gpio_pull(tck_gpio, GPIO_PU_UP);  // 
   set_gpio_pull(tms_gpio, GPIO_PU_UP);  // 
   set_gpio_pull(tdi_gpio, GPIO_PU_UP);  // 

  return true;
}

void cleanup_gpio_regs(int force_default)
{
  if (force_default == 1)
  {
    // restore default mode 
    *gpfsel0 = 0x21200900;
    *gpfsel1 = 0x00000024;
    *gpfsel2 = 0x12000000;
  }
  else
  {
    // restore previous mode
    *gpfsel0 = gpfsel0_prev;
    *gpfsel1 = gpfsel1_prev;
    *gpfsel2 = gpfsel2_prev;
  }


  set_gpio_mode(tdo_gpio, 0);  
  set_gpio_mode(tck_gpio, 0);  
  set_gpio_mode(tdi_gpio, 0);
  set_gpio_mode(tms_gpio, 0);

  // free allocated memory
  munmap(gpio_virt_addr_ptr, 0x1000);
}

void set_gpio_pull(int pin, int mode)
{
  int offset;
  int mask = 0x3;
  // configure GPIO pull mode
  if (pin < 16)
  {
     offset = GPIO_PUD_BITS * pin;
    *gppud0 &= ~(mask << offset);
    *gppud0 |= mode << offset;
  }
  else if (pin < 32)
  {   
    offset = GPIO_PUD_BITS * (pin - 16);
    *gppud1 &= ~(mask << offset);
    *gppud1 |= mode << offset;
  }
}

void set_gpio_mode(int pin, int mode)
{
  int offset;
  int mask = 0x7;
  // configure GPIO mode
  if (pin < 10)
  {
     offset = GPIO_FSEL_BITS * pin;
    *gpfsel0 &= ~(mask << offset);
    *gpfsel0 |= mode << offset;
  }
  else if (pin < 20)
  {   
    offset = GPIO_FSEL_BITS * (pin - 10);
    *gpfsel1 &= ~(mask << offset);
    *gpfsel1 |= mode << offset;
  }
  else if (pin < 30)
  {
    offset = GPIO_FSEL_BITS * (pin - 20);
    *gpfsel2 &= ~(mask << offset);
    *gpfsel2 |= mode << offset;
  }
}

void set_gpio_out(int pin, int level)
{
  if (level)
    *gpset0 = 1 << pin; 
  else
    *gpclr0 = 1 << pin;
}

bool get_gpio_in(int pin)
{
  return (*gplev0 & (1 << pin)) ? 1 : 0;
}

extern FILE *in;

/*BYTE *xsvf_data=0;*/


/* setPort:  Implement to set the named JTAG signal (p) to the new value (v).*/
/* if in debugging mode, then just set the variables */
void setPort(short p,short val)
{
	struct timespec ts, dummy;

    set_gpio_out(p, val);
    ts.tv_sec = 0;
    ts.tv_nsec = 250L;
    nanosleep(&ts, &dummy);
}


/* toggle tck LH.  No need to modify this code.  It is output via setPort. */
void pulseClock()
{
    setPort(tck_gpio,0);  /* set the TCK port to low  */
    setPort(tck_gpio,1);  /* set the TCK port to high */
}


/* readByte:  Implement to source the next byte from your XSVF file location */
/* read in a byte of data from the prom */
void readByte(unsigned char *data)
{
    /* pretend reading using a file */
    *data   = (unsigned char)fgetc( in );
    /**data=*xsvf_data++;*/
}

/* readTDOBit:  Implement to return the current value of the JTAG TDO signal.*/
/* read the TDO bit from port */
unsigned char readTDOBit()
{
    /* You must return the current value of the JTAG TDO signal. */
    return( (unsigned char) get_gpio_in(tdo_gpio) );
}

/* waitTime:  Implement as follows: */
/* REQUIRED:  This function must consume/wait at least the specified number  */
/*            of microsec, interpreting microsec as a number of microseconds.*/
/* REQUIRED FOR SPARTAN/VIRTEX FPGAs and indirect flash programming:         */
/*            This function must pulse TCK for at least microsec times,      */
/*            interpreting microsec as an integer value.                     */
/* RECOMMENDED IMPLEMENTATION:  Pulse TCK at least microsec times AND        */
/*                              continue pulsing TCK until the microsec wait */
/*                              requirement is also satisfied.               */
void waitTime(long microsec)
{
    
	struct timespec ts, dummy;
	
	//clock_gettime(CLOCK_REALTIME, &ts);
	//long n_time = (ts.tv_sec * 1000000000) + ts.tv_nsec;
	
   //static long tckCyclesPerMicrosec  = 1; /* must be at least 1 */
   //long        tckCycles   = microsec * tckCyclesPerMicrosec;
   //long        i;
    
    /* This implementation is highly recommended!!! */
    /* This implementation requires you to tune the tckCyclesPerMicrosec 
       variable (above) to match the performance of your embedded system
       in order to satisfy the microsec wait time requirement. */
    //for ( i = 0; i < tckCycles; ++i )
    //{
    //    pulseClock();
    //}
	//clock_gettime(CLOCK_REALTIME, &ts);
	//long n_now = (ts.tv_sec * 1000000000) + ts.tv_nsec;
    //while (n_now - n_time < microsec * 1000) {
	//	pulseClock();
	//    clock_gettime(CLOCK_REALTIME, &ts);
	//    n_now = (ts.tv_sec * 1000000000) + ts.tv_nsec;
	//}
    set_gpio_out(tck_gpio, 0);
    ts.tv_sec = 0;
    ts.tv_nsec = microsec * 1000L;
    nanosleep(&ts, &dummy);


    // static long tckCyclesPerMicrosec    = 20; /* must be at least 1 */
    // long        tckCycles   = microsec * tckCyclesPerMicrosec;
    // long        i;

    // /* This implementation is highly recommended!!! */
    // /* This implementation requires you to tune the tckCyclesPerMicrosec 
    //    variable (above) to match the performance of your embedded system
    //    in order to satisfy the microsec wait time requirement. */
    // for ( i = 0; i < tckCycles; ++i )
    // {
    //     pulseClock();
    // }

#if 0
    /* Alternate implementation */
    /* For systems with TCK rates << 1 MHz;  Consider this implementation. */
    /* This implementation does not work with Spartan-3AN or indirect flash
       programming. */
    if ( microsec >= 50L )
    {
        /* Make sure TCK is low during wait for XC18V00/XCFxxS */
        /* Or, a running TCK implementation as shown above is an OK alternate */
        setPort( TCK, 0 );

        /* Use Windows Sleep().  Round up to the nearest millisec */
        _sleep( ( microsec + 999L ) / 1000L );
    }
    else    /* Satisfy FPGA JTAG configuration, startup TCK cycles */
    {
        for ( i = 0; i < microsec;  ++i )
        {
            pulseClock();
        }
    }
#endif

#if 0
    /* Alternate implementation */
    /* This implementation is valid for only XC9500/XL/XV, CoolRunner/II CPLDs, 
       XC18V00 PROMs, or Platform Flash XCFxxS/XCFxxP PROMs.  
       This implementation does not work with FPGAs JTAG configuration. */
    /* Make sure TCK is low during wait for XC18V00/XCFxxS PROMs */
    /* Or, a running TCK implementation as shown above is an OK alternate */
    setPort( TCK, 0 );
    /* Use Windows Sleep().  Round up to the nearest millisec */
    _sleep( ( microsec + 999L ) / 1000L );
#endif
}
