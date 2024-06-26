#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/mman.h>

#pragma  GCC diagnostic ignored "-Wpointer-arith"
//warning disable

#define BUS_REG_BASE    0x7E000000
#define PHYS_REG_BASE   0xFE000000 // RPi 4 
#define GPIO_BASE       0x7E200000
#define GPIO_FSEL0      0x00  // mode selsction GPIO 0-9
#define GPIO_FSEL1      0x04  // mode selsction GPIO 10-19
#define GPIO_FSEL2      0x08  // mode selsction GPIO 20-29
#define GPIO_SET0       0x1C  // set outputs to '1' GPIO 0-31
#define GPIO_CLR0       0x28  // set outputs to '0' GPIO 0-31
#define GPIO_LEV0       0x34  // get input states GPIO 0-31
#define GPIO_MODE_IN    0 
#define GPIO_MODE_OUT   1 
#define GPIO_MODE_ALT0  4 
#define GPIO_MODE_ALT1  5 
#define GPIO_MODE_ALT2  6 
#define GPIO_MODE_ALT3  7 
#define GPIO_MODE_ALT4  3 
#define GPIO_MODE_ALT5  2 
#define GPIO_FSEL_BITS  3

#define GPCLK_BASE      0x7E101000
#define GPCLK0_CTL      0x70
#define GPCLK0_DIV      0x74
#define GPCLK_PWD       0x5A000000
#define GPCLK_SRC_OFF   0
#define GPCLK_SRC_OSC   1
#define GPCLK_SRC_PLLA  4
#define GPCLK_SRC_PLLC  5
#define GPCLK_SRC_PLLD  6
#define GPCLK_ENABLE    (1 << 4)
#define GPCLK_BUSY      (1 << 7)
#define GPCLK_MASH_1    (1 << 9)

#define GPCLK_OSC_FREQ  54.0  // Rpi 4: 54 Mhz 

// #define DEBUG 

uint32_t *gpio_virt_addr_ptr;  // pointer to virtual address
uint32_t *gpfsel0;
uint32_t *gpfsel1;
uint32_t *gpfsel2;
uint32_t *gpset0;
uint32_t *gpclr0;
uint32_t *gplev0;

uint32_t *gpclk_virt_addr_ptr;  // pointer to virtual address
uint32_t *gpclk0_ctl;
uint32_t *gpclk0_div;

uint32_t gpfsel0_prev;
uint32_t gpfsel1_prev;
uint32_t gpfsel2_prev;
uint32_t gpclk0_ctl_prev;
uint32_t gpclk0_div_prev;

int setup_gpio_regs()
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
      exit(1);
  }

  // allocate virtual memory and map the physical address to it
  gpio_virt_addr_ptr = mmap(0, 0x1000, PROT_WRITE|PROT_READ, MAP_SHARED, file_descriptor, gpio_phys_addr);
//  gpio_virt_addr_ptr = mmap(0, 0x1000, PROT_WRITE|PROT_READ, MAP_SHARED, file_descriptor, 0); // gpiomem automatically points to g'pio_phys_addr'
  close(file_descriptor);

  // check the results
  if (gpio_virt_addr_ptr == MAP_FAILED)
  {
      printf("Error: can't map memory\n");
      exit(1);
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

  // store values for clean-up
  gpfsel0_prev = *gpfsel0;
  gpfsel1_prev = *gpfsel1;
  gpfsel2_prev = *gpfsel2;

  #ifdef DEBUG
    // print virtual addresses and register content
    printf("GPFSEL0 (%p): 0x%08x \n", (void *)gpfsel0, *gpfsel0);
    printf("GPFSEL1 (%p): 0x%08x \n", (void *)gpfsel1, *gpfsel1);
    printf("GPFSEL2 (%p): 0x%08x \n", (void *)gpfsel2, *gpfsel2);
    printf("GPSET0  (%p): 0x%08x \n", (void *)gpset0, *gpset0);
    printf("GPCLR0  (%p): 0x%08x \n", (void *)gpclr0, *gpclr0);
    printf("GPLEV0  (%p): 0x%08x \n", (void *)gplev0, *gplev0);
  #endif  

  return(0);
}

int setup_gpclk_regs()
{
  uint32_t  gpclk_phys_addr;  // GPIO register CPU bus address 
  int file_descriptor;  // handle for memory mapping

  // calculate the physical address from the bus address
  gpclk_phys_addr = GPCLK_BASE - BUS_REG_BASE + PHYS_REG_BASE;

  // get a handle to the physical memory space
  if ((file_descriptor = open("/dev/mem", O_RDWR|O_SYNC|O_CLOEXEC)) < 0)  // requires root permissions ("sudo ...")
 // if ((file_descriptor = open("/dev/gpiomem", O_RDWR|O_SYNC|O_CLOEXEC)) < 0)  // only requires *gpio' group
  {
      printf("Error: can't open /dev/mem, run using sudo\n");
      exit(1);
  }

  // allocate virtual memory and map the physical address to it
  gpclk_virt_addr_ptr = mmap(0, 0x1000, PROT_WRITE|PROT_READ, MAP_SHARED, file_descriptor, gpclk_phys_addr);
//  gpio_virt_addr_ptr = mmap(0, 0x1000, PROT_WRITE|PROT_READ, MAP_SHARED, file_descriptor, 0); // gpiomem automatically points to g'pio_phys_addr'
  close(file_descriptor);

  // check the results
  if (gpclk_virt_addr_ptr == MAP_FAILED)
  {
      printf("Error: can't map memory\n");
      exit(1);
  }
  #ifdef DEBUG 
    printf("Success: Map %p -> %p\n", (void *)gpclk_phys_addr, (void *)gpclk_virt_addr_ptr);
  #endif

  // define variables to access the specific registers
  gpclk0_ctl = (uint32_t*)((void *)gpclk_virt_addr_ptr + GPCLK0_CTL);
  gpclk0_div = (uint32_t*)((void *)gpclk_virt_addr_ptr + GPCLK0_DIV);

  gpclk0_ctl_prev = *gpclk0_ctl;
  gpclk0_div_prev = *gpclk0_div;

  #ifdef DEBUG
    // print virtual addresses and register content
    printf("GPCLK0_CTL (%p): 0x%08x \n", (void *)gpclk0_ctl, *gpclk0_ctl);
    printf("GPCLK0_DIV (%p): 0x%08x \n", (void *)gpclk0_div, *gpclk0_div);

  #endif  
  return(0);
}

void cleanup(int force_default)
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
    *gpfsel0 = gpfsel0_prev; // 0x21200900
    *gpfsel1 = gpfsel1_prev; // 0x00000024
    *gpfsel2 = gpfsel2_prev; // 0x12000000
  }

  // restore previous mode 
  *gpclk0_ctl = gpclk0_ctl_prev | GPCLK_PWD;
  *gpclk0_div = GPCLK_PWD;
  // free allocated memory
  munmap(gpio_virt_addr_ptr, 0x1000);
  munmap(gpclk_virt_addr_ptr, 0x1000);
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

void setup()
{
  setup_gpio_regs();
  setup_gpclk_regs();
}

void set_gpclk_freq(int frequency)
{
  float divider;
  int div_i; 
  int div_f;

  if (frequency == 0)
  {
    *gpclk0_ctl |= GPCLK_PWD | GPCLK_ENABLE; // switch on ???
    *gpclk0_ctl  = GPCLK_PWD | (*gpclk0_ctl & ~GPCLK_ENABLE); // switch off
    while ((*gpclk0_ctl & GPCLK_BUSY) != 0) 
         
    return;
  }

  divider = GPCLK_OSC_FREQ / (frequency/1000.0); // frequency [kHz]


  if (divider > 4095)
  {
    printf("GPCLK frequency too low (f_min > 13 kHz)\n");
    return;
  }

  if (divider < 2) // MASH value + 1
  {
    printf("GPCLK frequency too high (f_max < 25 MHz)\n");
    return;
  }


  div_i = (int)(divider);
  div_f = (int)((divider - div_i) * 1024);

  #ifdef DEBUG 
    printf("divider = %f\n", divider);        
    printf("div_i = %d\n", div_i);    
    printf("div_f = %d\n", div_f);
  #endif

  *gpclk0_ctl |= GPCLK_PWD | GPCLK_ENABLE; // switch on ???
  *gpclk0_ctl  = GPCLK_PWD | (*gpclk0_ctl & ~GPCLK_ENABLE); // switch off
  while ((*gpclk0_ctl & GPCLK_BUSY) != 0) 
    ; // wait for not busy
  *gpclk0_div  = GPCLK_PWD | ((0xfff & div_i) << 12) | (0xfff & div_f);  // set divider
  *gpclk0_ctl |= GPCLK_PWD | GPCLK_MASH_1 | (0xf & GPCLK_SRC_OSC); // enable fractional divide, OSC as source
  *gpclk0_ctl |= GPCLK_PWD | GPCLK_ENABLE; // switch on

  #ifdef DEBUG
      printf("GPCLK0_DIV: 0x%08x \n", *gpclk0_div);
  #endif
}

#define MAX_GPIO_NUM 28

int main()
{
  uint32_t reg;
  int buffer;
  char mode[16];
  setup();

  printf("GPFSEL0 (%p): 0x%08x \n", (void *)gpfsel0, *gpfsel0);
  printf("GPFSEL1 (%p): 0x%08x \n", (void *)gpfsel1, *gpfsel1);
  printf("GPFSEL2 (%p): 0x%08x \n", (void *)gpfsel2, *gpfsel2);
  printf("GPSET0  (%p): 0x%08x \n", (void *)gpset0, *gpset0);
  printf("GPCLR0  (%p): 0x%08x \n", (void *)gpclr0, *gpclr0);
  printf("GPLEV0  (%p): 0x%08x \n", (void *)gplev0, *gplev0);  

  printf("GPIO | mode\n");
  for (int i = 0; i < MAX_GPIO_NUM; i++)
  {
    if (i <= 10)
      reg = *gpfsel0;
    else if (i <= 20)
      reg = *gpfsel1;
    else if (i <= 30)
      reg = *gpfsel2;
    
    buffer = 0x7 & (reg >> ((i%10)*3));
    switch (buffer)
    {
      case 0: sprintf(mode, "input"); break;
      case 1: sprintf(mode, "output"); break;
      case 2: sprintf(mode, "ALT5"); break;
      case 3: sprintf(mode, "ALT4"); break;
      case 4: sprintf(mode, "ALT0"); break;
      case 5: sprintf(mode, "ALT1"); break;
      case 6: sprintf(mode, "ALT2"); break;
      case 7: sprintf(mode, "ALT3"); break;
    }
    printf("  %2d   %s\n", i, mode);

  }

  cleanup(0);
  return(0);
}