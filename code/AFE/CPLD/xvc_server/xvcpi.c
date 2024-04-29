/*
 * Description :  Xilinx Virtual Cable Server for Raspberry Pi
 *
 * See Licensing information at End of File.
 * 
 *  modified: GPIO functions for Raspberry Pi 4, H.Krüger 2024
 */

#include <bcm_host.h>
#include <fcntl.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <netinet/tcp.h>
#include <netinet/in.h>
#include <sys/mman.h>
#include <sys/socket.h>

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

void set_gpio_mode(int pin, int mode);
void set_gpio_pull(int pin, int mode);
void set_gpio_out(int pin, int level);
bool get_gpio_in(int pin);

static int      JTAG_read(void);
static void     JTAG_write(int tck, int tms, int tdi);
static uint32_t JTAG_xfer(int n, uint32_t tms, uint32_t tdi);

/* GPIO numbers for each signal. Negative values are invalid */
static int tms_gpio = 1;
static int tck_gpio = 0;
static int tdo_gpio = 27;
static int tdi_gpio = 26;

static int verbose = 0;

#define LISTEN_PORT 2542

/* Transition delay coefficients */
#define JTAG_DELAY (10)
static unsigned int jtag_delay = JTAG_DELAY;

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
   set_gpio_pull(tdo_gpio, GPIO_PU_DOWN);  // ???

   set_gpio_out(tck_gpio, 1);  // was 0
   set_gpio_out(tms_gpio, 1);
   set_gpio_out(tdi_gpio, 1);  // was 0

   set_gpio_mode(tck_gpio, 1); // TCK output 
   set_gpio_mode(tms_gpio, 1); // TMS output 
   set_gpio_mode(tdi_gpio, 1); // TDI output
   set_gpio_pull(tck_gpio, GPIO_PU_UP);  // 
   set_gpio_pull(tms_gpio, GPIO_PU_UP);  // 
   set_gpio_pull(tdi_gpio, GPIO_PU_UP);  // 

   JTAG_write(1, 1, 1); // was 0,1,0

  return true;
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

static int JTAG_read(void)
{
   return get_gpio_in(tdo_gpio);
}

static void JTAG_write(int tck, int tms, int tdi)
{
   uint32_t set = tck<<tck_gpio | tms<<tms_gpio | tdi<<tdi_gpio;
   uint32_t clear = !tck<<tck_gpio | !tms<<tms_gpio | !tdi<<tdi_gpio;

   *gpset0 = set;
   *gpclr0 = clear;

   usleep(jtag_delay);

   // for (unsigned int i = 0; i < jtag_delay; i++)
   //    asm volatile ("");
}

static uint32_t JTAG_xfer(int n, uint32_t tms, uint32_t tdi)
{
   uint32_t tdo = 0;

   for (int i = 0; i < n; i++) {
      JTAG_write(0, tms & 1, tdi & 1);
      tdo |= JTAG_read() << i;  // ???
      JTAG_write(1, tms & 1, tdi & 1);
      tms >>= 1;
      tdi >>= 1;
   }
   return tdo;
}

static int sread(int fd, void *target, int len) {
   unsigned char *t = target;
   while (len) {
      int r = read(fd, t, len);
      if (r <= 0)
         return r;
      t += r;
      len -= r;
   }
   return 1;
}

int handle_data(int fd) {
   const char xvcInfo[] = "xvcServer_v1.0:2048\n";

   do {
      char cmd[16];
      unsigned char buffer[2048], result[1024];
       memset(cmd, 0, 16);

      if (sread(fd, cmd, 2) != 1)
         return 1;
      // if(verbose)
      //    printf("%u : Received command (raw): '%s'\n", (int)time(NULL), cmd);

      if (memcmp(cmd, "ge", 2) == 0) {
         if (sread(fd, cmd, 6) != 1)
            return 1;
         memcpy(result, xvcInfo, strlen(xvcInfo));
         if (write(fd, result, strlen(xvcInfo)) != strlen(xvcInfo)) {
            perror("write");
            return 1;
         }
         if (verbose) {
            printf("%u : Received command: 'getinfo'\n", (int)time(NULL));
            printf("\t Replied with %s\n", xvcInfo);
         }
         break;
      } else if (memcmp(cmd, "se", 2) == 0) {
         if (sread(fd, cmd, 9) != 1)
            return 1;
         memcpy(result, cmd + 5, 4);
         if (write(fd, result, 4) != 4) {
            perror("write");
            return 1;
         }
         if (verbose) {
            printf("%u : Received command: 'settck'\n", (int)time(NULL));
            printf("\t Replied with '%.*s'\n\n", 4, cmd + 5);
         }
         break;
      } else if (memcmp(cmd, "sh", 2) == 0) {
         if (sread(fd, cmd, 4) != 1)
            return 1;
         if (verbose) {
            printf("%u : Received command: 'shift'\n", (int)time(NULL));
            //printf("%u : Received data: '0x%x%x%x%x'\n", (int)time(NULL), cmd[0], cmd[1], cmd[2], cmd[3]);
            //printf("%u : Received data: '%s'\n", (int)time(NULL), cmd);
         }
      } else {

         fprintf(stderr, "invalid cmd '%s'\n", cmd);
         return 1;
      }

      int len;
      if (sread(fd, &len, 4) != 1) {
         fprintf(stderr, "reading length failed\n");
         return 1;
      }

      int nr_bytes = (len + 7) / 8;
      if (nr_bytes * 2 > sizeof(buffer)) {
         fprintf(stderr, "buffer size exceeded\n");
         return 1;
      }

      if (sread(fd, buffer, nr_bytes * 2) != 1) {
         fprintf(stderr, "reading data failed\n");
         return 1;
      }
      memset(result, 0, nr_bytes);

      if (verbose) {
         printf("\tNumber of Bits  : %d\n", len);
         printf("\tNumber of Bytes : %d \n", nr_bytes);
         printf("\n");
      }

      JTAG_write(0, 1, 1);

      int bytesLeft = nr_bytes;
      int bitsLeft = len;
      int byteIndex = 0;
      uint32_t tdi, tms, tdo;

      while (bytesLeft > 0) {
         tms = 0;
         tdi = 0;
         tdo = 0;
         if (bytesLeft >= 4) {
            memcpy(&tms, &buffer[byteIndex], 4);
            memcpy(&tdi, &buffer[byteIndex + nr_bytes], 4);

            tdo = JTAG_xfer(32, tms, tdi);
            memcpy(&result[byteIndex], &tdo, 4);

            bytesLeft -= 4;
            bitsLeft -= 32;
            byteIndex += 4;

            if (verbose) {
               printf("LEN : 0x%08x\n", 32);
               printf("TMS : 0x%08x\n", tms);
               printf("TDI : 0x%08x\n", tdi);
               printf("TDO : 0x%08x\n", tdo);
            }

         } else {
            memcpy(&tms, &buffer[byteIndex], bytesLeft);
            memcpy(&tdi, &buffer[byteIndex + nr_bytes], bytesLeft);

            tdo = JTAG_xfer(bitsLeft, tms, tdi);
            memcpy(&result[byteIndex], &tdo, bytesLeft);

            bytesLeft = 0;

            if (verbose) {
               printf("LEN : 0x%08x\n", bitsLeft);
               printf("TMS : 0x%08x\n", tms);
               printf("TDI : 0x%08x\n", tdi);
               printf("TDO : 0x%08x\n", tdo);
            }
            break;
         }
      }

      JTAG_write(1, 1, 1);  // was 0,1,0

      if (write(fd, result, nr_bytes) != nr_bytes) {
         perror("write");
         return 1;
      }

   } while (1);
   /* Note: Need to fix JTAG state updates, until then no exit is allowed */
   return 0;
}

int main(int argc, char **argv) {
   int i;
   int s;
   int c;

   struct sockaddr_in address;

   opterr = 0;

   printf("Xilinx Virtual Cable Server for Raspberry Pi at port %d\n", LISTEN_PORT);
   
   while ((c = getopt(argc, argv, "vd:")) != -1) {
      switch (c) {
      case 'v':
         verbose = 1;
         break;
      case 'd':
         jtag_delay = atoi(optarg);
         if (jtag_delay < 0)
             jtag_delay = JTAG_DELAY;
         break;
      case '?':
         fprintf(stderr, "usage: %s [-v]\n", *argv);
         return 1;
      }
   }
   if (verbose)
      printf("jtag_delay=%d\n", jtag_delay);

   if (!setup_gpio_regs()) {
      fprintf(stderr,"Failed setup_gpio_regs()\n");
      return -1;
   }

   s = socket(AF_INET, SOCK_STREAM, 0);

   if (s < 0) {
      perror("socket");
      return 1;
   }

   i = 1;
   setsockopt(s, SOL_SOCKET, SO_REUSEADDR, &i, sizeof i);

   address.sin_addr.s_addr = INADDR_ANY;
   address.sin_port = htons(LISTEN_PORT);
   address.sin_family = AF_INET;

   if (bind(s, (struct sockaddr*) &address, sizeof(address)) < 0) {
      perror("bind");
      return 1;
   }

   if (listen(s, 0) < 0) {
      perror("listen");
      return 1;
   }

   fd_set conn;
   int maxfd = 0;

   FD_ZERO(&conn);
   FD_SET(s, &conn);

   maxfd = s;

   while (1) {
      fd_set read = conn, except = conn;
      int fd;

      if (select(maxfd + 1, &read, 0, &except, 0) < 0) {
         perror("select");
         break;
      }

      for (fd = 0; fd <= maxfd; ++fd) {
         if (FD_ISSET(fd, &read)) {
            if (fd == s) {
               int newfd;
               socklen_t nsize = sizeof(address);

               newfd = accept(s, (struct sockaddr*) &address, &nsize);

               if (verbose)
                  printf("connection accepted - fd %d\n", newfd);
               if (newfd < 0) {
                  perror("accept");
               } else {
                 int flag = 1;
                 int optResult = setsockopt(newfd,
                                               IPPROTO_TCP,
                                               TCP_NODELAY,
                                               (char *)&flag,
                                               sizeof(int));
                 if (optResult < 0)
                    perror("TCP_NODELAY error");
                  if (newfd > maxfd) {
                     maxfd = newfd;
                  }
                  FD_SET(newfd, &conn);
               }
            }
            else if (handle_data(fd)) {

               if (verbose)
                  printf("connection closed - fd %d\n", fd);
               close(fd);
               FD_CLR(fd, &conn);
            }
         }
         else if (FD_ISSET(fd, &except)) {
            if (verbose)
               printf("connection aborted - fd %d\n", fd);
            close(fd);
            FD_CLR(fd, &conn);
            if (fd == s)
               break;
         }
      }
   }
   return 0;
}

/*
 * This work, "xvcpi.c", is a derivative of "xvcServer.c" (https://github.com/Xilinx/XilinxVirtualCable)
 * by Avnet and is used by Xilinx for XAPP1251.
 *
 * "xvcServer.c" is licensed under CC0 1.0 Universal (http://creativecommons.org/publicdomain/zero/1.0/)
 * by Avnet and is used by Xilinx for XAPP1251.
 *
 * "xvcServer.c", is a derivative of "xvcd.c" (https://github.com/tmbinc/xvcd)
 * by tmbinc, used under CC0 1.0 Universal (http://creativecommons.org/publicdomain/zero/1.0/).
 *
 * Portions of "xvcpi.c" are derived from OpenOCD (http://openocd.org)
 *
 * "xvcpi.c" is licensed under CC0 1.0 Universal (http://creativecommons.org/publicdomain/zero/1.0/)
 * by Derek Mulcahy.*
 */