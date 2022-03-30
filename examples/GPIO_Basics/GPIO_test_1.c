#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <signal.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/mman.h>

#define BUS_REG_BASE    0x7E000000  
#define PHYS_REG_BASE   0xFE000000  // RPi 4
#define GPIO_BASE       0x7E200000
#define GPIO_FSEL0      0x00
#define GPIO_SET0       0x1C
#define GPIO_CLR0       0x28

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
    printf("Success: Map %p -> %p\n", (void *)gpio_phys_addr, gpio_virt_addr);

    // // define variables to access the specific registers
    // gpfsel0 = gpio_virt_addr + GPIO_FSEL0;
    // gpset0  = gpio_virt_addr + GPIO_SET0;
    // gpclr0  = gpio_virt_addr + GPIO_CLR0;

    // // configure GPIO as an output
    // *gpfsel0 |= 0x001 << 12;

    // // toggle the output
    // *gpset0 = 1 << 4; 
    // *gpclr0 = 1 << 4; 
    // *gpset0 = 1 << 4; 
    // *gpclr0 = 1 << 4; 
    // *gpset0 = 1 << 4; 
    // *gpclr0 = 1 << 4; 

    // // configure GPIO as an input
    // *gpfsel0 &= 0x000 << 12;

    return(0);
}