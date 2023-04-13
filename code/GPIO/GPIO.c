#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/mman.h>

#define BUS_REG_BASE    0x7E000000
#define PHYS_REG_BASE   0xFE000000 // RPi 4 
#define GPIO_BASE       0x7E200000
#define GPIO_FSEL0      0x00  // mode selsction GPIO 0-9
#define GPIO_FSEL1      0x04  // mode selsction GPIO 10-19
#define GPIO_FSEL2      0x08  // mode selsction GPIO 20-29
#define GPIO_SET0       0x1C  // set outputs to '1' GPIO 0-31
#define GPIO_CLR0       0x28  // set outputs to '0' GPIO 0-31
#define GPIO_LEV0       0x34  // get input states GPIO 0-31
#define GPIO_MODE_IN    0x000
#define GPIO_MODE_OUT   0x001
#define GPIO_MODE_ALT0  0x100
#define GPIO_MODE_ALT1  0x101  
#define GPIO_MODE_ALT2  0x110
#define GPIO_MODE_ALT3  0x111
#define GPIO_MODE_ALT4  0x011
#define GPIO_MODE_ALT5  0x010

#define GPIO_FSEL_BITS  3

#define GPIO_PIN 5  // pin to be used as output
//#define DEBUG  // print debug information

uint32_t *gpio_virt_addr_ptr;  // pointer to virtual address
uint32_t *gpfsel0;
uint32_t *gpfsel1;
uint32_t *gpfsel2;
uint32_t *gpset0;
uint32_t *gpclr0;
uint32_t *gplev0;

int setup_gpio_regs()
{
  uint32_t  gpio_phys_addr;  // GPIO register CPU bus address 
  int file_descriptor;  // handle for memory mapping

  // calculate the physical address from the bus address
  gpio_phys_addr = GPIO_BASE - BUS_REG_BASE + PHYS_REG_BASE;

  // get a handle to the physical memory space
  if ((file_descriptor = open("/dev/mem", O_RDWR|O_SYNC|O_CLOEXEC)) < 0)
  {
      printf("Error: can't open /dev/mem, run using sudo\n");
      return(1);
  }

  // allocate virtual memory and map the physical address to it
  gpio_virt_addr_ptr = mmap(0, 0x1000, PROT_WRITE|PROT_READ, MAP_SHARED, file_descriptor, gpio_phys_addr);
  close(file_descriptor);

  // check the results
  if (gpio_virt_addr_ptr == MAP_FAILED)
  {
      printf("Error: can't map memory\n");
      return(1);
  }
  #ifdef DEBUG 
    printf("Success: Map %p -> %p\n", (void *)gpio_phys_addr, gpio_virt_addr_ptr);
  #endif

  // define variables to access the specific registers
  gpfsel0 = (uint32_t*)((void *)gpio_virt_addr_ptr + GPIO_FSEL0);
  gpfsel1 = (uint32_t*)((void *)gpio_virt_addr_ptr + GPIO_FSEL1);
  gpfsel2 = (uint32_t*)((void *)gpio_virt_addr_ptr + GPIO_FSEL2);
  gpset0  = (uint32_t*)((void *)gpio_virt_addr_ptr + GPIO_SET0);
  gpclr0  = (uint32_t*)((void *)gpio_virt_addr_ptr + GPIO_CLR0);
  gplev0  = (uint32_t*)((void *)gpio_virt_addr_ptr + GPIO_LEV0);

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

void cleanup_gpio()
{
  // set default mode (input)
  *gpfsel0 = 0;
  *gpfsel1 = 0;
  *gpfsel2 = 0;
  // free allocated memory
  munmap(gpio_virt_addr_ptr, 0x1000);
}

void set_gpio_mode(int pin, int mode)
{
  // configure GPIO mode
  if (pin < 10)
   *gpfsel0 = mode << (GPIO_FSEL_BITS * pin);
  else if (pin < 20)
   *gpfsel1 = mode << (GPIO_FSEL_BITS * (pin - 10));
  else if (pin < 30)
   *gpfsel2 = mode << (GPIO_FSEL_BITS * (pin - 20));
}

void set_gpio_out(int pin, int level)
{
  if (level)
    *gpset0 = 1 << pin; 
  else
    *gpclr0 = 1 << pin;
}

int main()
{
  int GPIOpin = 27;
  setup_gpio_regs();
  set_gpio_mode(GPIOpin, GPIO_MODE_OUT);
  set_gpio_out(GPIOpin, 1); 
  set_gpio_out(GPIOpin, 0);
  cleanup_gpio();
  return(0);
}