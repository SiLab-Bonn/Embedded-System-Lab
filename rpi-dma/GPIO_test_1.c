#include  <sys/mman.h>

#define BUS_REG_BASE    0x7E000000  
#define PHYS_REG_BASE   0xFE000000  // RPi 4
#define GPIO_BASE       0x7E200000
#define GPIO_MODE0      0x00
#define GPIO_SET0       0x1C
#define GPIO_CLR0       0x28

uint32_t gpio_phys_addr = GPIO_BASE - BUS_REG_BASE + PHYS_REG_BASE;
int      file_descriptor;
void    *gpio_virt_addr;
void    *gpmode0;
void    *gpset0;
void    *gpclr0;

// get a handle to the physical memory space
if ((file_descriptor = open ("/dev/mem", O_RDWR|O_SYNC|O_CLOEXEC)) < 0)
{
    printf("Error: can't open /dev/mem, run using sudo\n");
    exit();
}

// map the physical address to 
gpio_virt_addr = mmap(0, 0x1000, PROT_WRITE|PROT_READ, MAP_SHARED, file_descriptor, gpio_phys_addr);
close(file_descriptor);
if (mem == MAP_FAILED)
{
    print("Error: can't map memory\n");
    exit();
}
printf("Success: Map %p -> %p\n", (void *)gpio_phys_addr, gpio_virt_addr);

gpmode0 = gpio_virt_addr + GPIO_MODE0;
gpset0  = gpio_virt_addr + GPIO_SET0;
gpclr0  = gpio_virt_addr + GPIO_CLR0;