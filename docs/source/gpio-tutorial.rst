=========================
GPIO Programming Tutorial
=========================

This part gives a practical introduction to basic GPIO port programming. It starts with an example for a low-level access to the GPIO registers which are described in section :ref:`gpio-interface`. Then, the use of Python libraries for GPIO handling will be explained and compared to the C-code based low-level access.

.. _gpio-programming-examples:

Basic GPIO Example
========================
This programming example describes the basic access to the GPIO registers. This register handling is made on "low level" (i.e. not using higher-level library functions calls) using **C code**. Here are samples from the ``GPIO.c`` file from ``code/GPIO_Basics`` folder. This first code block takes care of the mapping the user accessible virtual memory to the physical memory of the register.

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
  // set output to '0'
  *gpclr0 = 4;
  // set output to '1'
  *gpset0 = 4;
  // set output to '0'
  *gpclr0 = 4;
  ...
  // cleanup: set default mode (all input) and free allocated memory
  *gpfsel0 = 0;
  munmap(gpio_virt_addr_ptr, 0x1000);

.. note::
  The function ``mmap("dev/mem/"...)`` returns a handle which allows unrestricted access to system wide memory and I/O resources. Since this is a security sensitive access, it can only be executed with elevated access rights. Therefore, programs using that kind of functions have to be called as super user ``sudo ./<program_name>``.

.. admonition:: Exercise 1

  Copy the file :file:`GPIO.c` from the :file:`code/GPIO_Basics` folder to your :file:`work` folder.  Compile ( ``CTRL`` + ``F7``) and run the program by typing :file:`sudo ./GPIO` from the terminal. Connect an oscilloscope probe to the GPIO4 pin on the base board and explain the trace that you see when you run the GPIO program. Make sure you select an appropriate horizontal resolution because the pulse will be very narrow (~ 30ns). 

    - Measure the output minimum pulse width. 
    - Modify the code to extend the pulse width by inserting additional function calls (``sleep(), usleep(), asm("nop")``) between the writes to GPSET and GPCLR registers. Measure the pulse width again. Explain what you see.

The **Python** example uses the `Rpi.GPIO library<https://sourceforge.net/p/raspberry-gpio-python/wiki/Home/>`_ library. Setting up the access to the GPIO registers is done in a similar way as in the C-code example. However, the detailed implementation is hidden in the library. 

.. code-block:: python
  
  # import the library and define the prefix for using its members
  import RPi.GPIO as GPIO

  # tell the library to use pin numbers according to the GPIO naming
  GPIO.setmode(GPIO.BCM) 

  # define GPIO4 as an output
  GPIO.setup(4, GPIO.OUT)
  
  # toggle th output state
  GPIO.output(4, GPIO.LOW)
  GPIO.output(4, GPIO.HIGH)
  GPIO.output(4, GPIO.LOW)
  
  # set GPIO configuration back to default
  GPIO.cleanup()

.. admonition:: Exercise 2

  Copy the file :file:`GPIO.py` from the :file:`code/GPIO_Basics` folder to your :file:`work` folder.  Run the script by pressing ``F5``. Connect an oscilloscope probe to the GPIO4 pin on the base board and explain the trace that you see when you run the GPIO program. What is the minimum pulse width now? Increase the pulse width by inserting calls to ``sleep()`` (add ``import time`` at the top of your script). 

    - Compare the minimum pulse width as generated by the C-code and the Python implementations. 
    - Change  both codes to generate a ~100 us pulse and repeatedly run the code. How stable is the pulse width? Is there a difference between the C-code and Python implementation? 