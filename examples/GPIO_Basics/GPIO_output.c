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
#define GPIO_MODE_IN    0
#define GPIO_MODE_OUT   1
#define GPIO_FSEL_BITS  3

#define GPIO_PIN 4  // pin to be used as output
//#define DEBUG  // print debug information

uint32_t  gpio_phys_addr;
int       file_descriptor;
uint32_t *gpio_virt_addr;
uint32_t *gpfsel0;
uint32_t *gpset0;
uint32_t *gpclr0;

int main()
{
    // calculate the physical address from the bus address
    gpio_phys_addr = GPIO_BASE - BUS_REG_BASE + PHYS_REG_BASE;

    // get a handle to the physical memory space
    if ((file_descriptor = open("/dev/mem", O_RDWR|O_SYNC|O_CLOEXEC)) < 0)
    {
        printf("Error: can't open /dev/mem, run using sudo\n");
        exit(1);
    }

    // allocate virtual memory and map the physical address to it
    gpio_virt_addr = mmap(0, 0x1000, PROT_WRITE|PROT_READ, MAP_SHARED, file_descriptor, gpio_phys_addr);
    close(file_descriptor);

    // check the results
    if (gpio_virt_addr == MAP_FAILED)
    {
        printf("Error: can't map memory\n");
        exit(1);
    }
    #ifdef DEBUG 
      printf("Success: Map %p -> %p\n", (void *)gpio_phys_addr, gpio_virt_addr);
    #endif

    // define variables to access the specific registers
    gpfsel0 = (uint32_t*)((void *)gpio_virt_addr + GPIO_FSEL0);
    gpset0  = (uint32_t*)((void *)gpio_virt_addr + GPIO_SET0);
    gpclr0  = (uint32_t*)((void *)gpio_virt_addr + GPIO_CLR0);

    #ifdef DEBUG
      // print virtual addresses and register content
      printf("GPFSEL0 (%p): 0x%08x \n", (void *)gpfsel0, *gpfsel0);
      printf("GPSET0 (%p): 0x%08x \n", (void *)gpset0, *gpset0);
      printf("GPCLR0 (%p): 0x%08x \n", (void *)gpclr0, *gpclr0);
    #endif

    // configure GPIO as an output
    *gpfsel0 = GPIO_MODE_OUT << (GPIO_FSEL_BITS * GPIO_PIN);
 
     // toggle the output
    *gpset0 = 1 << GPIO_PIN; 
    usleep(1);
    *gpclr0 = 1 << GPIO_PIN; 
    usleep(1);
 
    // configure GPIO as an input (default)
    *gpfsel0 &= GPIO_MODE_IN << (GPIO_FSEL_BITS * GPIO_PIN);

    return(0);
}