#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/mman.h>

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
#define GPIO_FSEL_BITS  3

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
    *gpfsel0 = gpfsel0_prev;
    *gpfsel1 = gpfsel1_prev;
    *gpfsel2 = gpfsel2_prev;
  }

  // free allocated memory
  munmap(gpio_virt_addr_ptr, 0x1000);
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


int main()
{
// example using direct register access  
  uint32_t register_value;
  uint32_t gpio_phys_addr;   // GPIO register CPU bus address 
  int      file_descriptor;  // handle for memory mapping

  // calculate the physical address from the bus address
  gpio_phys_addr = GPIO_BASE - BUS_REG_BASE + PHYS_REG_BASE;

  // get a handle to the physical memory space
  file_descriptor = open("/dev/mem", O_RDWR|O_SYNC|O_CLOEXEC);  // requires root permissions ("sudo ...")

  // allocate virtual memory and map the physical address to it
  gpio_virt_addr_ptr = mmap(0, 0x1000, PROT_WRITE|PROT_READ, MAP_SHARED, file_descriptor, gpio_phys_addr);
  close(file_descriptor);

  // define variables to access the specific registers
  gpfsel0 = (uint32_t*)((void *)gpio_virt_addr_ptr + GPIO_FSEL0);
  gpfsel1 = (uint32_t*)((void *)gpio_virt_addr_ptr + GPIO_FSEL1);
  gpfsel2 = (uint32_t*)((void *)gpio_virt_addr_ptr + GPIO_FSEL2);
  gpset0  = (uint32_t*)((void *)gpio_virt_addr_ptr + GPIO_SET0);
  gpclr0  = (uint32_t*)((void *)gpio_virt_addr_ptr + GPIO_CLR0);
  gplev0  = (uint32_t*)((void *)gpio_virt_addr_ptr + GPIO_LEV0);

  register_value  =  *gpfsel2;   // read the current GPIFSEL2 register setting 
  //printf("GPFSEL2: 0x%08x\n", register_value);
  register_value &= ~(0x7 << (7*3)); // clear the GPIO27 mode bits
  register_value |=  (0x1 << (7*3)); // set the GPIO27 mode bits to mode 1 (output)
  *gpfsel2 = register_value;     // set the new GPIFSEL2 register setting
  //printf("GPFSEL2: 0x%08x\n", *gpfsel2);

  *gpset0 = 1 << 27;  // set output to '1'
  sleep(1);
  *gpclr0 = 1 << 27;  // set output to '0'

  register_value &= ~(0x7 << (7*3)); // clear the GPIO27 mode bits -> mode 0 (input)
 *gpfsel2 = register_value;     // set the new GPIFSEL2 register setting

  munmap(gpio_virt_addr_ptr, 0x1000); // free allocated memory

// example using function calls
  // setup_gpio_regs();

  // set_gpio_mode(27, 1); // set GPIO 17 to output
  // set_gpio_out(27, 1);  // set GPIO 17 to high
  // sleep(1);
  // set_gpio_out(27, 0);  // set GPIO 17 to high

  // cleanup(0);
  return(0);
}