// Access to parallel ADC using Raspberry Pi SMI (Secondary Memory Interface)
// 
// based on the original sources from Jeremy P Bentham
// For detailed description, see https://iosoft.blog
//
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//
// V0.1 HK 29.11.21 - modified for triggered ADC read-out
// v0.2 HK 03.11.22 - more clean-up, added selectable sample rate

#include <stdio.h>
#include <signal.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include "rpi_dma_utils.h"
#include "rpi_smi_defs.h"

// SMI cycle timings
#define SMI_NUM_BITS    SMI_16_BITS
#define SMI_TIMING      SMI_TIMING_5M

// SMI transfer timing: unit [ns], setup, strobe, hold
#if PHYS_REG_BASE == PI_4_REG_BASE        // Timings for RPi v4 (1.5 GHz): divider, setup, strobe, hold
#define SMI_TIMING_200k 30, 62, 126, 62 // 200 kS/s   (div = 30, 250 cycles)
#define SMI_TIMING_500k 20, 38, 74, 38  // 500 kS/s   (div = 20, 150 cycles)
#define SMI_TIMING_1M   10, 38, 74, 38  // 1 MS/s     (div = 10, 150 cycles)
#define SMI_TIMING_2M   10, 19, 37, 19  // 2 MS/s     (div = 10, 75 cycles)
#define SMI_TIMING_5M    6, 12, 26, 12  // 5 MS/s     (div = 6, 50 cycles)
#define SMI_TIMING_10M   6,  6, 13,  6  // 10 MS/s    (div = 6, 25 cycles)
#define SMI_TIMING_19M   4,  5,  9,  5  // 19.74 MS/s (div = 4, 19 cycles)
#define SMI_TIMING_25M   4,  3,  8,  4  // 25 MS/s    (div = 4, 15 cycles)
#define SMI_TIMING_31M   4,  3,  6,  3  // 31.25 MS/s (div = 4, 12 cycles)
#else                                   // Timings for RPi v0-3 (1 GHz)
#define SMI_TIMING_200k 20, 62, 126, 62 // 200 kS/s
#define SMI_TIMING_500k 20, 25, 50, 25  // 500 kS/s
#define SMI_TIMING_1M   10, 25, 50, 25  // 1 MS/s
#define SMI_TIMING_2M   10, 12, 25, 13  // 2 MS/s
#define SMI_TIMING_5M    8,  6, 13,  6  // 5 MS/s
#define SMI_TIMING_10M   4,  6, 13,  6  // 10 MS/s
#define SMI_TIMING_20M   2,  6, 13,  6  // 20 MS/s
#define SMI_TIMING_25M   2,  5, 10,  5  // 25 MS/s
#define SMI_TIMING_31M   2,  4,  6,  4  // 31.25 MS/s
#define SMI_TIMING_42M   2,  3,  6,  3  // 41.66 MS/s
#define SMI_TIMING_50M   2,  3,  5,  2  // 50 MS/s
#endif

// Number of samples to be discarded to compensate ADC latency
#define PRE_SAMP        7																										
// Number of raw bytes per ADC sample
#define SAMPLE_SIZE     2

// GPIO pin numbers
#define ADC_D0_PIN      12  // data bus @GPIO[23:12]
#define ADC_NPINS       13  // 12 data bits + GPIO24 (DREQ for triggered DMA access)
#define SMI_SOE_PIN     6
#define SMI_SWE_PIN     7
#define SMI_DREQ_PIN    24
#define ADC_ENABLE      25
#define ADC_DISABLE_HBYTE  26 // control of ADC bits [11:4], disable for LSA mode

// DMA request threshold
#define REQUEST_THRESH  4

// SMI register names for diagnostic print
char *smi_regstrs[] = {
    "CS","LEN","A","D","DSR0","DSW0","DSR1","DSW1",
    "DSR2","DSW2","DSR3","DSW3","DMC","DCS","DCA","DCD",""
};

// SMI CS register field names for diagnostic print
#define STRS(x)     STRS_(x) ","
#define STRS_(...)  #__VA_ARGS__
char *smi_cs_regstrs = STRS(SMI_CS_FIELDS);

// Structures for mapped I/O devices, and non-volatile memory
extern MEM_MAP gpio_regs, clk_regs, dma_regs;
MEM_MAP vc_mem,  smi_regs;

// Pointers to SMI registers
volatile SMI_CS_REG  *smi_cs;
volatile SMI_L_REG   *smi_l;
volatile SMI_A_REG   *smi_a;
volatile SMI_D_REG   *smi_d;
volatile SMI_DMC_REG *smi_dmc;
volatile SMI_DSR_REG *smi_dsr;
volatile SMI_DSW_REG *smi_dsw;
volatile SMI_DCS_REG *smi_dcs;
volatile SMI_DCA_REG *smi_dca;
volatile SMI_DCD_REG *smi_dcd;

// Buffer for captured data and mapped adc values
void     *rx_buffer_ptr;
uint16_t *adc_data_ptr;


// register to store controll block 0 address
uint32_t cb0_addr;
uint32_t cb1_addr;

// number of samples
int num_samples;
float time_base;

// trigger modes
bool trigger_mode_single = false;

// data bus width and offsst for ADC and digital signal analyzer
int adc_lsb_pin = ADC_D0_PIN;  // defaults to GPIO 12
int adc_npins  = ADC_NPINS;    // defaults to 13 = 12 bit data + DREQ
int pin_modes_to_restore[28];

// Non-volatile memory size
#define VC_MEM_SIZE(nsamp) (PAGE_SIZE + ((nsamp)+4)*SAMPLE_SIZE)

void map_devices(void);
void smi_start(int nsamples, int packed);
void set_time_base(int time_base_index);
void set_tigger_mode(int mode);
uint32_t *adc_dma_start(MEM_MAP *mp, int nsamp);
int  map_adc_data(void *buff, uint16_t *data, int nsamp);
void smi_init(int width, int ns, int setup, int hold, int strobe);
void disp_smi(void);
void mode_word(uint32_t *wp, int n, uint32_t mode);
void disp_reg_fields(char *regstrs, char *name, uint32_t val);

float get_time_base(void)
{
  return time_base;
}

char* Hello(void)
{
  //system("grep -o BCM2711 /proc/cpuinfo"); 
  system("cat /proc/cpuinfo | grep 'Hardware' | awk '{print $3}'> NULL"); 
  return("Hello World!");
}

void set_resolution(int num_bits)
{
  if (num_bits > 12)
  {
    printf("Max. resolution limited to 12 bit.\n");
    num_bits = 12;
  }
  if (num_bits < 4)
  {
    printf("Min. resolution limited to 4 bit.\n");
    num_bits = 4;
  }

  adc_npins   = num_bits + 1;  // ADC bus width + DREQ bit
  adc_lsb_pin = ADC_NPINS - adc_npins + ADC_D0_PIN;
  // printf("adc_npins: %d\n", adc_npins);
  // printf("adc_lsb_pin: %d\n", adc_lsb_pin);
}

void set_trigger_mode(int mode)
{
  if (mode == 0)
    trigger_mode_single = false;
  else
    trigger_mode_single = true;
}

// Map GPIO, DMA and SMI registers into virtual mem (user space)
// If any of these fail, program will be terminated
void map_devices(void)
{
    map_periph(&gpio_regs, (void *)GPIO_BASE, PAGE_SIZE);
    map_periph(&dma_regs, (void *)DMA_BASE, PAGE_SIZE);
    map_periph(&clk_regs, (void *)CLK_BASE, PAGE_SIZE);
    map_periph(&smi_regs, (void *)SMI_BASE, PAGE_SIZE);
}

void init_device(uint16_t *adc_data, int samples, int time_base_index, int mode)
{
  num_samples = samples;
  adc_data_ptr = adc_data;

  map_devices();
  
  // backup pin modes and setup GPIO pins for SMI
 // for (int i=adc_lsb_pin; i<adc_lsb_pin+adc_npins; i++)
  for (int i=ADC_D0_PIN; i<ADC_D0_PIN+ADC_NPINS; i++)
  {
    pin_modes_to_restore[i] = get_gpio_mode(i);
    gpio_mode(i, GPIO_ALT1);
  }
 
  gpio_mode(SMI_SOE_PIN, GPIO_ALT1);
  gpio_mode(ADC_ENABLE, GPIO_OUT);
  gpio_mode(ADC_DISABLE_HBYTE, GPIO_OUT);

  if (mode == 0)
    gpio_out(ADC_DISABLE_HBYTE, 0);  // oscilloscope mode, ADC bits [11:4] are enabled
  else
    gpio_out(ADC_DISABLE_HBYTE, 1);  // logic signal analyzer mode, ADC bits [11:4] are disabled
  
  set_time_base(time_base_index);

  map_uncached_mem(&vc_mem, VC_MEM_SIZE(num_samples+PRE_SAMP)); 
}

void set_time_base(int time_base_index)
{
  switch (time_base_index)
  {
      case 1: smi_init(SMI_NUM_BITS, SMI_TIMING_200k); time_base = 5.0; break;
      case 2: smi_init(SMI_NUM_BITS, SMI_TIMING_500k); time_base = 2.0; break;
      case 3: smi_init(SMI_NUM_BITS, SMI_TIMING_1M);   time_base = 1.0; break;
      case 4: smi_init(SMI_NUM_BITS, SMI_TIMING_2M);   time_base = 0.5; break;
      case 5: smi_init(SMI_NUM_BITS, SMI_TIMING_5M);   time_base = 0.2; break;
      case 6: smi_init(SMI_NUM_BITS, SMI_TIMING_10M);  time_base = 0.1; break;
      case 7: smi_init(SMI_NUM_BITS, SMI_TIMING_25M);  time_base = 0.04; break;
      default: smi_init(SMI_NUM_BITS, SMI_TIMING_1M);  time_base = 1.0; break;
  }    
}

// Initialise SMI, given data width, time step, and setup/hold/strobe counts
// Step value is in nanoseconds: even numbers, 2 to 30
void smi_init(int width, int ns, int setup, int strobe, int hold)
{
    int divi = ns / 2;

    smi_cs  = (SMI_CS_REG *) REG32(smi_regs, SMI_CS);
    smi_l   = (SMI_L_REG *)  REG32(smi_regs, SMI_L);
    smi_a   = (SMI_A_REG *)  REG32(smi_regs, SMI_A);
    smi_d   = (SMI_D_REG *)  REG32(smi_regs, SMI_D);
    smi_dmc = (SMI_DMC_REG *)REG32(smi_regs, SMI_DMC);
    smi_dsr = (SMI_DSR_REG *)REG32(smi_regs, SMI_DSR0);
    smi_dsw = (SMI_DSW_REG *)REG32(smi_regs, SMI_DSW0);
    smi_dcs = (SMI_DCS_REG *)REG32(smi_regs, SMI_DCS);
    smi_dca = (SMI_DCA_REG *)REG32(smi_regs, SMI_DCA);
    smi_dcd = (SMI_DCD_REG *)REG32(smi_regs, SMI_DCD);
    //smi_cs->value = smi_l->value = smi_a->value = 0;
    //smi_dsr->value = smi_dsw->value = smi_dcs->value = smi_dca->value = 0;
    // clock magic ....
    if (*REG32(clk_regs, CLK_SMI_DIV) != divi << 12)
    {
        *REG32(clk_regs, CLK_SMI_CTL) = CLK_PASSWD | (1 << 5);
        usleep(10);
        while (*REG32(clk_regs, CLK_SMI_CTL) & (1 << 7)) ;
        usleep(10);
        *REG32(clk_regs, CLK_SMI_DIV) = CLK_PASSWD | (divi << 12);
        usleep(10);
        *REG32(clk_regs, CLK_SMI_CTL) = CLK_PASSWD | 6 | (1 << 4);
        usleep(10);
        while ((*REG32(clk_regs, CLK_SMI_CTL) & (1 << 7)) == 0) ;
        usleep(100);
    }
    if (smi_cs->seterr) // clear error flag
        smi_cs->seterr = 1;
 
    smi_dsr->rwidth  = smi_dsw->wwidth  = width;   
    smi_dsr->rsetup  = smi_dsw->wsetup  = setup;
    smi_dsr->rstrobe = smi_dsw->wstrobe = strobe;
    smi_dsr->rhold   = smi_dsw->whold   = hold;
    smi_dmc->panicr  = smi_dmc->panicw  = 8;
    smi_dmc->reqr    = smi_dmc->reqw    = REQUEST_THRESH;

    // external DREQ setup
    smi_dsr->rdreq = 1;
    smi_dmc->dmap = 1;

}

int take_data()
{
  uint16_t timeout_counter = 0;
  uint16_t timeout = time_base * (num_samples+PRE_SAMP) + 5; // timeout in us
  int return_value = 0;
  
  gpio_out(ADC_ENABLE, 1);

  // start SMI
  smi_dmc->dmaen = 1;
  smi_l->len = num_samples + PRE_SAMP;
  smi_cs->pxldat = 1;  // pack bytes to words
  smi_cs->enable = 1;
  smi_cs->clear  = 1;
  smi_cs->start  = 1;  
  
  // start DMA
  rx_buffer_ptr = adc_dma_start(&vc_mem, num_samples);

  while (dma_active(DMA_CHAN_A)) 
  {
    usleep(1);

    if (*REG32(dma_regs, DMA_REG(DMA_CHAN_A, DMA_CONBLK_AD)) == cb0_addr) // still first controll block active
    {
      timeout_counter ++;
    }
 
    if (timeout_counter > timeout) 
    {
      //printf("Timeout: DMA transfer not finished after %d us.\n", timeout);
      stop_dma(DMA_CHAN_A);
      return_value = -1;
      break;
    }
  }

  map_adc_data(rx_buffer_ptr, adc_data_ptr, num_samples);
  //disp_reg_fields(smi_cs_regstrs, "CS", *REG32(smi_regs, SMI_CS));
  
 smi_dmc->dmaen = 0;
 smi_cs->enable = 0;
 smi_dcs->enable = 0;	

  gpio_out(ADC_ENABLE, 0);
  
  return return_value;
}

void close_device(void)
{
  int i;

  if (gpio_regs.virt)
  {
    for (i=ADC_D0_PIN; i<ADC_D0_PIN+ADC_NPINS; i++)
//    for (i=adc_lsb_pin; i<adc_lsb_pin+adc_npins; i++)
      gpio_mode(i, pin_modes_to_restore[i]);
  }
  if (smi_regs.virt)
      *REG32(smi_regs, SMI_CS) = 0;
  stop_dma(DMA_CHAN_A);
  unmap_periph_mem(&vc_mem);
  unmap_periph_mem(&smi_regs);
  unmap_periph_mem(&dma_regs);
  unmap_periph_mem(&gpio_regs);

  //gpio_mode(ADC_ENABLE, GPIO_IN);
}

// Start SMI, given number of samples, optionally pack bytes into words
void smi_start(int nsamples, int packed)
{
    smi_l->len = nsamples + PRE_SAMP;
    smi_cs->pxldat = (packed != 0);
    smi_cs->enable = 1;
    smi_cs->clear = 1;
    smi_cs->start = 1;
}

// Start DMA for SMI ADC, return Rx data buffer
uint32_t *adc_dma_start(MEM_MAP *mp, int nsamp)
{
    DMA_CB   *cbs     = mp->virt;  // DMA control block mapped to virtual memory
    uint32_t *data    = (uint32_t *)(cbs + 4);
  //  uint32_t *pindata = data + 8;
  //  uint32_t *modes   = data + 16;
    uint32_t *rxdata  = data + 32;

    cb0_addr = MEM_BUS_ADDR(mp, &cbs[0]);    
   
    enable_dma(DMA_CHAN_A);
  
// Control block 0: read data pre-sample data
    cbs[0].ti = DMA_SRCE_DREQ | (DMA_SMI_DREQ << 16) | DMA_CB_DEST_INC;
    cbs[0].tfr_len = PRE_SAMP * SAMPLE_SIZE;
    cbs[0].srce_ad = REG_BUS_ADDR(smi_regs, SMI_D);
    cbs[0].dest_ad = MEM_BUS_ADDR(mp, rxdata);
    cbs[0].next_cb = MEM_BUS_ADDR(mp, &cbs[1]); 

// Control block 1: read data
    cbs[1].ti = DMA_SRCE_DREQ | (DMA_SMI_DREQ << 16) | DMA_CB_DEST_INC;
    cbs[1].tfr_len = (nsamp) * SAMPLE_SIZE;
    cbs[1].srce_ad = REG_BUS_ADDR(smi_regs, SMI_D);
    cbs[1].dest_ad = MEM_BUS_ADDR(mp, rxdata);
 
    start_dma(mp, DMA_CHAN_A, &cbs[0], 0);
    return(rxdata);
}


// Start DMA for SMI ADC, return Rx data buffer
uint32_t *adc_dma_start_org(MEM_MAP *mp, int nsamp)
{
    DMA_CB   *cbs     = mp->virt;  // DMA control block mapped to virtual memory
    uint32_t *data    = (uint32_t *)(cbs + 4);
    uint32_t *pindata = data + 8;
    uint32_t *modes   = data + 16;
    uint32_t *rxdata  = data + 32;
    uint32_t i;

    // Get current mode register values, keep one value and change the other one
    modes[0] = modes[3] = *REG32(gpio_regs, GPIO_MODE0);  
    modes[1] = modes[4] = *REG32(gpio_regs, GPIO_MODE1);  
    modes[2] = modes[5] = *REG32(gpio_regs, GPIO_MODE2);  
                                                                      
    // Get mode values with ADC pins set to SMI
    for (i=adc_lsb_pin; i<adc_lsb_pin+adc_npins; i++)  // loop thru GPIO pin numbers connected to ADC
        mode_word(&modes[i/10], i%10, GPIO_ALT1);    // set bits accordingly 

 //   *pindata = 1 << TEST_PIN;

    enable_dma(DMA_CHAN_A);
  
// control block 0: set SMI mode for selected pins in GPIO[29:20]
    cbs[0].ti = DMA_CB_SRCE_INC | DMA_CB_DEST_INC  | DMA_WAIT_RESP;
    cbs[0].tfr_len = 3 * 4;
    cbs[0].srce_ad = MEM_BUS_ADDR(mp, &modes[0]);
    cbs[0].dest_ad = REG_BUS_ADDR(gpio_regs, GPIO_MODE0);
    cbs[0].next_cb = MEM_BUS_ADDR(mp, &cbs[1]);

// Control blocks 1: set test pin
    cbs[1].ti = DMA_WAIT_RESP;
    cbs[1].tfr_len = 4;
    cbs[1].srce_ad = MEM_BUS_ADDR(mp, pindata);  // index of TEST_PIN
    cbs[1].dest_ad = REG_BUS_ADDR(gpio_regs, GPIO_SET0);  // GPIO[31:0] output register
    cbs[1].next_cb = MEM_BUS_ADDR(mp, &cbs[2]); 

// Control block 2: read data
    cbs[2].ti = DMA_SRCE_DREQ | (DMA_SMI_DREQ << 16) | DMA_CB_DEST_INC;
    //cbs[2].ti = DMA_SRCE_DREQ | DMA_CB_DEST_INC  ;
    cbs[2].tfr_len = (nsamp + PRE_SAMP) * SAMPLE_SIZE;
    cbs[2].srce_ad = REG_BUS_ADDR(smi_regs, SMI_D);
    cbs[2].dest_ad = MEM_BUS_ADDR(mp, rxdata);
    cbs[2].next_cb = MEM_BUS_ADDR(mp, &cbs[3]);
 
 // Control block 3: clear test pin
    cbs[3].ti = DMA_CB_SRCE_INC | DMA_CB_DEST_INC;
    cbs[3].tfr_len = 4;
    cbs[3].srce_ad = MEM_BUS_ADDR(mp, pindata);
    cbs[3].dest_ad = REG_BUS_ADDR(gpio_regs, GPIO_CLR0);
    cbs[3].next_cb = MEM_BUS_ADDR(mp, &cbs[4]);

 // Control block 4: disable SMI I/O pins
    cbs[4].ti = DMA_CB_SRCE_INC | DMA_CB_DEST_INC | DMA_WAIT_RESP;
    cbs[4].tfr_len = 3 * 4;
    cbs[4].srce_ad = MEM_BUS_ADDR(mp, &modes[3]);
    cbs[4].dest_ad = REG_BUS_ADDR(gpio_regs, GPIO_MODE0);

    start_dma(mp, DMA_CHAN_A, &cbs[0], 0);
    return(rxdata);
}

// ADC DMA is complete, get data
int map_adc_data(void *rxbuff, uint16_t *adc_data, int nsamp)
{
    uint16_t *bp = (uint16_t *)rxbuff;
    int i;

    for (i=0; i<nsamp+PRE_SAMP; i++)
    {
        if (i >= PRE_SAMP)
            *adc_data++ = (bp[i] >> 4) & 0xfff;
    }
    return(nsamp);
}

// Get GPIO mode value into 32-bit word
void mode_word(uint32_t *wp, int n, uint32_t mode)
{
    uint32_t mask = 7 << (n * 3);

    *wp = (*wp & ~mask) | (mode << (n * 3));
}

// Return ADC value, using GPIO inputs
int adc_gpio_val(void)
{
    int v = *REG32(gpio_regs, GPIO_LEV0);

    return((v>>adc_lsb_pin) & ((1 << adc_npins)-1));
}

// Display bit values in register
void disp_reg_fields(char *regstrs, char *name, uint32_t val)
{
    char *p=regstrs, *q, *r=regstrs;
    uint32_t nbits, v;

    printf("%s %08X", name, val);
    while ((q = strchr(p, ':')) != 0)
    {
        p = q + 1;
        nbits = 0;
        while (*p>='0' && *p<='9')
            nbits = nbits * 10 + *p++ - '0';
        v = val & ((1 << nbits) - 1);
        val >>= nbits;
        if (v && *r!='_')
            printf(" %.*s=%X", q-r, r, v);
        while (*p==',' || *p==' ')
            p = r = p + 1;
    }
    printf("\n");
}
