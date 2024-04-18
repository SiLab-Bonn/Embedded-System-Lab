.. _gpio-tutorial:

=========================
GPIO Programming Tutorial
=========================

This tutorial provides an introduction to basic GPIO (general purpose input/output) programming. It starts with an example for a low-level access to the GPIO registers which are described in section :ref:`gpio-interface`. Then, the use of Python libraries for GPIO handling will be explained and compared to the C-code based low-level access.

.. _gpio-programming-examples:

Basic GPIO Example (C code)
---------------------------
This programming example describes how to directly access the registers which control the GPIO pins. The register handling is made on "low level" (i.e. not using higher-level library functions calls) using **C code** only. Actually, high-level libraries like the Python Rpi.GPIO library which you will be using later and kernel drivers are often written in C code to allow fast and efficient hardware access. Here are simplified samples from the ``gpio.c`` file from the ``code/GPIO`` folder which you will be using in the first experiment. This first code block takes care of the mapping the user accessible virtual memory to the physical memory of the register.

.. code-block:: c

  // start address of the I/O peripheral register space on the VideoCore bus
  #define BUS_REG_BASE    0x7E000000
  // start address of the I/O peripheral register space seen from the CPU bus
  #define PHYS_REG_BASE   0xFE000000 // RPi 4 
  // start address of the GPIO register space on the VideoCore bus
  #define GPIO_BASE       0x7E200000
  // address offsets for the individual registers
  #define GPIO_FSEL0      0x00  // mode selection GPIO 0-9
  #define GPIO_FSEL1      0x04  // mode selection GPIO 10-19
  #define GPIO_FSEL2      0x08  // mode selection GPIO 20-29
  #define GPIO_SET0       0x1C  // set outputs to '1' GPIO 0-31
  #define GPIO_CLR0       0x28  // set outputs to '0' GPIO 0-31
  #define GPIO_LEV0       0x34  // get input states GPIO 0-31
  
  // calculate the GPIO register physical address from the bus address
  uint32_t gpio_phys_addr = GPIO_BASE - BUS_REG_BASE + PHYS_REG_BASE;

  // get a handle to the physical memory space
  if ((int file_descriptor = open("/dev/mem", O_RDWR|O_SYNC|O_CLOEXEC)) < 0)

  // allocate virtual memory (one page size) and map the physical address to a pointer
  void *gpio_virt_addr_ptr = mmap(0, 0x1000, PROT_WRITE|PROT_READ, MAP_SHARED, file_descriptor, gpio_phys_addr);


Now ``gpio_virt_addr_ptr`` points to the start address of the GPIO register space. For access to the individual registers their specific address offsets are added:

.. code-block:: c

  // define memory pointer to access the specific registers
  gpfsel0 = (uint32_t*)((void *)gpio_virt_addr_ptr + GPIO_FSEL0);
  gpfsel1 = (uint32_t*)((void *)gpio_virt_addr_ptr + GPIO_FSEL1);
  gpfsel2 = (uint32_t*)((void *)gpio_virt_addr_ptr + GPIO_FSEL2);
  gpset0  = (uint32_t*)((void *)gpio_virt_addr_ptr + GPIO_SET0);
  gpclr0  = (uint32_t*)((void *)gpio_virt_addr_ptr + GPIO_CLR0);
  gplev0  = (uint32_t*)((void *)gpio_virt_addr_ptr + GPIO_LEV0);

Finally, the GPIO mode is set for a given pin which then can be used for output (or input) operations. The register configuration is shown explicitly here while the main loop in `gpio.c`` uses function calls:

.. code-block:: c

  // main() block: define GPIO27 as output and toggling it once and cleanup
  *gpfsel2 = 0b001 << (7*3); // output mode: FSEL[3:0] = 0b001, GPIO27 FSEL field starts at bit (7*3) = 21
  *gpclr0  = 1 << 27;  // set output to '0'
  *gpset0  = 1 << 27;  // set output to '1'
  *gpclr0  = 1 << 27;  // set output to '0'
  *gpfsel2 = 0;       // set default mode (all GPIO become inputs) 
  munmap(gpio_virt_addr_ptr, 0x1000); // free allocated memory

.. warning::
  The function ``mmap("dev/mem/"...)`` returns a handle which allows unrestricted access to system wide memory and I/O resources. Since this is a security sensitive access, it can only be executed with elevated access rights. Therefore, programs using that kind of functions have to be called as super user ``sudo -E ./<program_name>``.
  
Python GPIO Example
--------------------
The **Python** example uses the `Rpi.GPIO library <https://sourceforge.net/p/raspberry-gpio-python/wiki/Home/>`_ library. Setting up the access to the GPIO registers is done in a similar way as in the C-code example. However, the detailed implementation is hidden in the library. 

.. code-block:: python
  
  # import the library and define the prefix for using its members
  import RPi.GPIO as GPIO

  # tell the library to use pin numbers according to the GPIO naming
  GPIO.setmode(GPIO.BCM)

  # define GPIO27 as an output
  GPIO.setup(27, GPIO.OUT)

  # set the output to high
  GPIO.output(27, GPIO.HIGH)

  # wait for user input
  input()

  # set the output to low
  GPIO.output(27, GPIO.LOW)

  # wait for user input
  input()

  # set GPIO configuration back to default
  GPIO.cleanup()
  
Exercises 
---------  

.. admonition:: Exercise 1. GPIO programming with C-code

  Copy the file :file:`gpio.c` from the :file:`code/GPIO` folder to your :file:`work` folder. Compile (``CTRL+Shift+b`` or ``Terminal->Run build Task``) and run the program by typing :file:`sudo -E ./gpio` into a terminal from within your :file:`work` folder.
  
  If you receive an error about 'gpio' not found, double check that you've compiled the source code into a binary with the correct file name.

  1. Connect an oscilloscope probe to the GPIO27 pin (red LED of the RGB LED) on the base board and adjust the oscilloscope setting such that it triggers on the output pulse when the GPIO program runs. Make sure you select an appropriate horizontal resolution because the pulse will be very narrow (~ 30ns).
  2. Add a loop statement around the code which toggles the GPIO output state to produce a stream of output pulses. 
  3. Measure the output average pulse width and its peak-to-peak jitter (i.e. the minimum and maximum width). 
  4. Modify the code to extend the pulse width by inserting additional function calls between the writes to GPSET and GPCLR registers:
    
     * ``asm("nop")``, adds the smallest possible delay by inserting a ``NOP`` command (no operation) into the loop
     * ``usleep(<some number>)``, adds delay in microseconds units
     * ``sleep(<some number>)``, adds delay in second units (for visible blinking LED, for example)
    
  Measure the pulse width again for the different pulse width modifications. What happens when the CPU runs other tasks while the output is toggling (start another application or just move a window with the mouse). Explain what you see.

.. admonition:: Exercise 2.  GPIO programming with Python 

  Copy the file :file:`gpio.py` from the :file:`code/GPIO` folder to your :file:`work` folder. Proceed similar to the tasks in the C-code exercises.

  1. If not yet done, connect an oscilloscope probe to the GPIO27 pin (red LED of the RGB LED) on the base board and adjust the oscilloscope setting such that it  triggers on the output pulse when the GPIO scripts runs. What is the pulse width now?
  2. Add a loop statement around the code which toggles the GPIO output state to produce a stream of output pulses. 
  3. Measure the output average pulse width and its peak-to-peak jitter (i.e. the minimum and maximum width). 
  4. Compare the minimum pulse width as generated by the C-code and the Python implementations. 
  5. Increase the pulse width by inserting calls to ``sleep()`` (add ``import time`` at the top of your script). 
  6. Adjust both C- and Python codes to generate a ~100 us pulse. How stable is the pulse width? Is there a difference between the C-code and Python implementation? 
  
.. admonition:: Exercise 3.  Serial UART communication with Python
  
  The goal of this exercise is to implement a simple terminal program running on two Raspberry Pi boards (or a board with itself, in loopback) and to establish a serial link using the UART interface on GPIO pins 14 (TX) and 15 (RX).

  Prerequisites:
    - In Raspberry Pi Configuration GUI ensure 'Serial port' is enabled, and 'Serial Console' is disabled. If a change was necessary, you must reboot for it to take effect.
    - A Python library that instantiates a serial port object (for example PySerial) and allows sending and receiving data.
    - A direct connection between RX and TX pins (loop-back) on a single board for testing the script. 
    - A cross-over connection for making the RX-TX / TX-RX connection between two boards.
  
  Tasks:
    - Write a script, using the `PySerial library<https://pyserial.readthedocs.io/en/latest/shortintro.html>`, to transmit user input strings across the serial interface. Make sure you properly convert strings to a binary format. (Hint: `str.encode()<https://docs.python.org/3/library/stdtypes.html#str.encode>` )
    - Connect an oscilloscope to RX (TX) pins and examine the waveform. Set various serial port configuration parameters (baud rate, number of stop bits, parity) and explain their effect.
    - Connect the serial link between two boards connecting TX of one board to RX of the other board and vice versa.
    - Make sure the serial configuration is the same on both boards and send and receive data.
    - What happens if the settings are not the same on both boards?
    - Extend your script to send and receive binary files.
