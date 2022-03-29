==============
GPIO Interface
==============
The BCM2711 has 54 general purpose input/output ports of which 28 are available on the Raspberry Pi module (``GPIO[27:0]``). When a GPIO port is used as an output, its  state can be toggled between logic 0 and logic 1 and a high-impedance state (tri-state). Since the GPIO ports are powered from a 3.3 V supply, the voltage levels are 0 V and 3.3 V respectively. When used as an input, the port can read these levels.

.. warning::
    The voltage applied to the GPIO pins **must not exceed 3.3 V**. When connected to circuits with higher output levels, appropriate levels shifters or resistive dividers must be used. 

There are special control registers which configure the GPIO ports to become an input or output port according to the required functionality. For many control tasks this simple so-called bit-banging IO interface is sufficient. For more complex tasks and data transfers requiring higher bandwidth, standardized serial protocols are available. To offload the CPU from implementing these protocols and to allow a precise protocol timing, special hardware blocks can be selected to be used with the GPIO ports. These blocks are enabled by selecting alternative function modes for a given GPIO pin. Every GPIO pin can carry an alternate function (up to 6) but not every alternate functions is available to a given pin as described in Table 6-31 in :download:`BCM2837-ARM-Peripherals.pdf <documents/BCM2837-ARM-Peripherals.pdf>`. Note that this documents actually describes the predecessor of the BCM2711 the BCM2835 (and not even the BCM2837, as the name suggests), which is used on the Raspberry Pi 1 modules. However, the given description of the GPIO port and other peripherals is still valid for the newer chip generations - apart from a few details like bus address offsets (see below).
Here is an example of a **GPIO Function Register** (see also chapter 6.1 in BCM2837-ARM-Peripherals document):


.. table:: **GPIO Function Select Register (GPFSEL0 @ 0x7E200000)**

    =====  ===========  ======================  ====  =======
    Bit    Field Name   Description             Type  Default
    =====  ===========  ======================  ====  =======
    31-30  ---          Reserved                R      0
    29-27  FSEL9        Function Select GPIO9   R/W    0
    26-24  FSEL8        Function Select GPIO8   R/W    0
    23-21  FSEL7        Function Select GPIO7   R/W    0
    20-18  FSEL6        Function Select GPIO6   R/W    0
    17-15  FSEL5        Function Select GPIO5   R/W    0
    14-12  FSEL4        Function Select GPIO4   R/W    0
    11-9   FSEL3        Function Select GPIO3   R/W    0
    8-6    FSEL2        Function Select GPIO2   R/W    0
    5-3    FSEL1        Function Select GPIO1   R/W    0
    2-0    FSEL0        Function Select GPIO0   R/W    0
    =====  ===========  ======================  ====  =======

The address space of the IO peripheral registers starts at 0x7E000000 of the VideoCore bus. There are six 32-bit registers of this type (GPFSEL0 - GPFSEL5) to cover all 54 GPIO pins. Each 3-bit word selects one out of eight function modes for a given GPIO pin:

.. table:: **GPIO Function Modes**

    ===== ===================
    FSELn Function
    ===== ===================
    000   Input
    001   Output
    100   Alternate function 0
    101   Alternate function 1
    110   Alternate function 2
    111   Alternate function 3
    011   Alternate function 4
    010   Alternate function 5
    ===== ===================

To use a GPIO pin as an output, the value 0x001 has to be written to its corresponding GPFSEL register. Here is a pseudo code example enabling GPIO4 as an output:

.. code::
    
    GPFSEL0 |= 0x001 << 12

    # this is the abbreviation for a read-modify-write operation:

    temp    = GPFSEL0;             # read 
    temp    = temp | (0x001 << 12) # modify
    GPFSEL0 = temp                 # write

To set the output state to 1 or 0, the **Pin Output Set/Clear Registers** are used:

.. table:: **GPIO Pin Output Set Registers (GPSET0 @ 0x7E20001C)**

    =====  ===========  ======================  ====  =======
    Bit    Field Name   Description             Type  Default
    =====  ===========  ======================  ====  =======
    31-0   SETn         1 = set pin to logic 1   R/W      0
    =====  ===========  ======================  ====  =======
 
.. table:: **GPIO Pin Output Clear Registers (GPCLR0 @ 0x7E200028)**

    =====  ===========  ======================  ====  =======
    Bit    Field Name   Description             Type  Default
    =====  ===========  ======================  ====  =======
    31-0   CLRn         1 = set pin to logic 0   R/W      0
    =====  ===========  ======================  ====  =======

Writing a 0 to one of the Set/Clear registers has no effect. Having separate functions to set the logic levels to 1 and 0 allows changing the state of a GPIO pin without the need for read-modify-write operations (i.e read the current register value, modify it, write back the new value). This pseudo code will toggle GPIO4 from 0 to 1 and immediately back to 0 (assuming that the GPCLR0 and GPSET0 variables point to memory mapped register addresses as described above):

.. code::

    GPCLR0 = 4
    GPSET0 = 4
    GPCLR0 = 4
 
There are more GPIO configuration registers (documented and undocumented) which control additional features like pull-up/pull-down resistor for inputs, sensitivity for interrupt usage (level- or edge-sensitivity and its polarity), drive strength for outputs and more, which are beyond the scope of exercise. 


Alternate GPIO Functions
========================
The GPIO ports can not only act a simple inputs or outputs but can be used to implement more complex I/O operations. A couple of industrial standard protocols a supported directly be dedicated hardware blocks. These alternate functions are configured and controlled via peripheral registers in a similar way like the basic input/output modes. However, these configurations settings a much more complex and will not be described in detail. Typically, a user will call functions from a library to set-up and use the alternate function modes. Here is a table which shows the available alternate functions which can be selected via the appropriate GPFSEL registers for each GPIO pin. Note that all alternate functions require a number of consecutive pins to be set to the same mode.

.. figure:: images/GPIO_Alt.png
    :width: 600
    :align: center


Next, the properties of a few of those commonly used serial protocols are described.


UART
----
The Universal-Asynchronous-Receiver-Transmitter (UART) protocol is widely used for communication between a pair of hardware components. It is a full-duplex peer-to-peer protocol which uses two separate data lines: one for sending data from host to device and the other for sending data from device to host. Unlike other serial protocols like I2C or SPI (see below) the two communicating devices can send data any time - there are no master or slaves roles. The data transmission is asynchronous because there is no additional clock signal needed to synchronize the transfer. However, to set-up a communication link via an UART bus, host and device have to use the same configuration settings for the data transfer engine:

  - Data rate (also called baud rate): Typically multiples of 9600 up to 115200 
  - Number of data bits: 8 (but also 7 or 9 bits are supported)
  - Number of stop bits: 1, 2 or 1.5
  - Parity: odd, even or none

In addition, other features for making the communication more robust (handshaking, software or hardware based) are sometimes used but will be omitted here. 

Data are being sent always one byte at a time. A data transmission starts by sending a start bit (always 0), then the data bits LSB first, the parity bit (if configured) and finally the stop bit(s) which are always 1. A typical UART configuration is 8 data bits, even parity, one stop bit (8E1) and thus one data byte is transferred using 11 bit-clock cycles. This is a timing diagram of an UART transfer of one byte with a 8E1 setting. The period of one bit cycle is 1/F_baud.

.. figure:: images/UART.png
    :width: 600
    :align: center


The encoding and decoding of the parity bit is done in the UART hardware. If even (odd) parity is selected the transmitter will set the parity to a logic value such the sum off all data bytes including the parity bit is even (odd). The checking of the validity of a received byte is transparent to the user. A mismatch of calculated and received parity will be notified to the user as a receive error.

.. note::
    The signal names RX and TX, which are commonly used for labeling the UART bus, can cause confusion when connecting one device with another. Since a device sends data via its TX port and expects to receive data via its RX port, at some point the TX labeled net from one device needs to be connected to the RX labeled net of the other device and vice versa.




I2C
---

SPI
---

PWM
---

SMI
---


