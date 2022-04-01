=========================
GPIO Programming Tutorial
=========================

This part gives a practical introduction to basic GPIO port programming. It begins with an example for a low-level access to the GPIO registers which are described in section :ref:`GPIO Interface`.

.. _gpio-programming-examples:

GPIO Programming Example
========================
This programming example describes the basic access to the GPIO registers. This register handling is made on "low level" (i.e. not using higher-level library functions calls) using C code. Here are samples from the ``GPIO.c`` file from ``code/GPIO_Basics`` folder. This first code block takes care of the mapping the user accessible virtual memory to the physical memory of the register.

.. code-block:: c

  // start address of the I/O peripheral register space on the VideoCore bus
  #define BUS_REG_BASE    0x7E000000
  // start address of the I/O peripheral register space seen from the CPU bus
  #define PHYS_REG_BASE   0xFE000000 // RPi 4 
  // start address of the GPIO register space on the VideoCore bus
  #define GPIO_BASE       0x7E200000
  // address offsets for the individual registers
  #define GPIO_FSEL0      0x00  // mode selection
  #define GPIO_SET0       0x1C  // set outputs to '1'
  #define GPIO_CLR0       0x28  // set outputs to '0'
  #define GPIO_LEV0       0x34  // get input states
  
  // calculate the GPIO register physical address from the bus address
  uint32_t gpio_phys_addr = GPIO_BASE - BUS_REG_BASE + PHYS_REG_BASE;

  // get a handle to the physical memory space
  if ((int file_descriptor = open("/dev/mem", O_RDWR|O_SYNC|O_CLOEXEC)) < 0)

  // allocate virtual memory (one page size) and map the physical address to a pointer
  void *gpio_virt_addr_ptr = mmap(0, 0x1000, PROT_WRITE|PROT_READ, MAP_SHARED, file_descriptor, gpio_phys_addr);


Now ``gpio_virt_addr_ptr`` points to the start address of the GPIO register space. For access to the individual registers their specific address offsets are added:

.. code-block:: c

  // define memory pointer to access the specific registers
  uint32_t *gpfsel0 = (uint32_t*)((void *)gpio_virt_addr_ptr + GPIO_FSEL0);
  uint32_t *gpset0  = (uint32_t*)((void *)gpio_virt_addr_ptr + GPIO_SET0);
  uint32_t *gpclr0  = (uint32_t*)((void *)gpio_virt_addr_ptr + GPIO_CLR0);
  uint32_t *gplev0  = (uint32_t*)((void *)gpio_virt_addr_ptr + GPIO_LEV0);

Finally, the GPIO mode is set for a given pin which then can be used for output (or input) operations:

.. code-block:: c

  // Example: defining GPIO4 as output
  *gpfsel0 = 0x001 << (12); // output mode: FSEL[3:0] = 0x001, GPIO4 FSEL filed starts a bit 12
  // set output to '1'
  *gpset0 = 4;
  // set output to '0'
  *gpclr0 = 4;
  // read state from GPIO5
  state = 0x01 & (*gplev0 >> 5);

.. note::
  The function ``mmap("dev/mem/"...)`` returns a handle which allows unrestricted access to system wide memory and I/O ressources. Since this is a security sensitve access, it can only be executed with elevated access rights. Therefore, programs using that kind of functions have to be called as super user ``su ./<program_name>``.
