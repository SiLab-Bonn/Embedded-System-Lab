#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/mman.h>

#define BUS_REG_BASE    0x7E000000
#define PHYS_REG_BASE   0xFE000000 // RPi 4 
#define GPIO_BASE       0x7E200000
#define GPIO_FSEL0      0x00
#define GPIO_SET0       0x1C
#define GPIO_CLR0       0x28
#define GPIO_LEV0       0x34
#define GPIO_MODE_IN    0x000
#define GPIO_MODE_OUT   0x001
#define GPIO_MODE_ALT0  0x100
#define GPIO_MODE_ALT1  0x101  
#define GPIO_MODE_ALT2  0x110
#define GPIO_MODE_ALT3  0x111
#define GPIO_MODE_ALT4  0x011
#define GPIO_MODE_ALT5  0x010

#define GPIO_FSEL_BITS  3

#define GPIO_PIN 4  // pin to be used as output
//#define DEBUG  // print debug information

uint32_t *gpio_virt_addr_ptr;  // pointer to virtual address
uint32_t *gpfsel0;
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
  gpset0  = (uint32_t*)((void *)gpio_virt_addr_ptr + GPIO_SET0);
  gpclr0  = (uint32_t*)((void *)gpio_virt_addr_ptr + GPIO_CLR0);
  gplev0  = (uint32_t*)((void *)gpio_virt_addr_ptr + GPIO_LEV0);

  #ifdef DEBUG
    // print virtual addresses and register content
    printf("GPFSEL0 (%p): 0x%08x \n", (void *)gpfsel0, *gpfsel0);
    printf("GPSET0 (%p): 0x%08x \n", (void *)gpset0, *gpset0);
    printf("GPCLR0 (%p): 0x%08x \n", (void *)gpclr0, *gpclr0);
    printf("GPLEV0 (%p): 0x%08x \n", (void *)gplev0, *gplev0);
  #endif  
  return(0);
}

void cleanup_gpio()
{
  // set default mode (input)
  *gpfsel0 = 0;
  // free allocated memory
  munmap(gpio_virt_addr_ptr, 0x1000);
}

void set_gpio_mode(int pin, int mode)
{
  // configure GPIO mode
  *gpfsel0 = mode << (GPIO_FSEL_BITS * pin);
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
  setup_gpio_regs();
  set_gpio_mode(4, GPIO_MODE_OUT);
  
  set_gpio_out(4, 0);
  usleep(100);
  set_gpio_out(4, 1); 
  usleep(100);
  set_gpio_out(4, 0);
  usleep(100);
 
  cleanup_gpio();
  return(0);
}