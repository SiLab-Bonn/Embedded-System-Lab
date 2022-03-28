========================
Embedded System Hardware
========================
This chapter introduces the computing hardware which is used in all experiments. Although the specific details of the following description relate to the Raspberry Pi platform, the fundamental aspects of interaction between software, system hardware and external devices are platform independent. The first section describes the Raspberry Pi hardware with a focus on the access to the GPIO ports. The second section gives an overview of commonly used serial protocols for communication between systems and electronic components. Finally, programming examples are presented and simple tasks which introduce the first experiment (GPIO Programming) are shown.

Computing Platform
---------------
The central part of the Raspberry Pi module is a system-on-chip (SOC). In a system-on-chip, peripheral components like display controller, various communication interfaces (USB, Ethernet, PCIe, etc.), memory controller, power regulators and others are integrated on a single chip together with the CPU. Therefore, only very few external components are needed to build a complete computing system.

The Raspberry Pi SOC is based on a highly integrated, low power video processor (video core) with a multi-core ARM CPU attached to it. The following block diagram of the BCM2711 chip, which is used on the Raspberry Pi 4 modules, shows the SOC main function blocks which communicate and exchange data via an internal system bus (AMBA/AXI bus). The operation system and the user programs run on a quad-core CPU (ARM Cortex A-72) while video data processing is handled by VideoCore GPU. In this SOC, the access to external memory or internal peripheral devices like the GPIO ports is managed by the video core. That means that the physical address of a device on the system bus cannot be directly accessed. It has to be mapped by the GPU memory management unit (MMU) to a virtual address, which the CPU (and thus the user code) can use. This memory mapping will be explained in one of the GPIO programming examples.


GPIO Interface
---------------
The BCM2711 has 54 general purpose input/output ports of which 28 are available on the Raspberry Pi module (``GPIO[27:0]``). When a GPIO port is used as an output, its  state can be toggled between logic 0 and logic 1 and a high-impedance state (tri-state). Since the GPIO ports are powered from a 3.3 V supply, the voltage levels are 0 V and 3.3 V respectively. When used as an input, the port can read these levels.

.. warning::
    Any potential applied to the GPIO pins must not exceed 3.3 V. When connected to circuits with higher output levels, appropriate levels shifters or resistive dividers must be used. 

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

    # which is the abbreviation for a read-modify-write operation:

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

Writing a 0 to one of the Set/Clear registers has no effect. Having separate functions to set the logic levels to 1 and 0 allows changing the state of a GPIO pin without the need for read-modify-write operations (i.e read the current register value, modify it, write back the new value). This code will toggle GPIO4 from 0 to 1 and immediately back to 0:

.. code::

    GPCLR0 = 4
    GPSET0 = 4
    GPCLR0 = 4
 
.. note:: It is not possible to directly access these registers (i.e. reading/writing from/to the specific bus address). A user accessible (virtual) memory space has to be allocated first and than mapped to the register addresses. Since the register addresses used in the BCM2837-ARM-Peripherals document are referring to the VideoCore address space, the corresponding address offsets as seen by the CPU core have to be taken into account. Here is the description and the pseudo code of such mapping:

At first the address at which the CPU core can access the IO periphery register is calculated. This step converts address at which the peripheral register is located on the VideoCore bus to the physical address the CPU core can access:

.. code::

    reg_physical_address = reg_bus_address - BUS_REG_BASE + PHYS_REG_BASE

Than the physical address needs to be mapped to user accessible virtual memory:

.. code::
    
    allocate_mem(reg_phys_address, virt_reg_address, size)


 The ``BUS_REG_BASE`` address offset of the VideoCore bus is ``0x7E000000`` for all models, while the ``PHYS_REG_BASE`` offset depends on the specific chip implementation. This is important for the code portability between different Raspberry Pi platforms.

.. table::
    
    ===========  ==========  ==================
     Model        Chip        PHYS_REG_BASE
    ===========  ==========  ==================
      RPi 1       BCM2835     0x20000000
      RPi 2       BCM2836     0x3F000000
      RPi 3       BCM2837     0x3F000000
      RPi 4       BCM2711     0xFE000000      
    ===========  ==========  ==================

There are more GPIO configuration registers (documented and undocumented) which control additional features like pull-up/pull-down resistor for inputs, sensitivity for interrupt usage (level- or edge-sensitivity and its polarity), drive strength for outputs and more, which are beyond the scope of exercise. 


Alternate GPIO Functions
-------------------------
The alternate functions are configured and controlled via peripheral registers in a similar way like the basic input/output modes. However, these configurations settings a much more complex and will not be described in detail. Typically, a user will call a library function to set-up and use the alternate function modes. Here the properties of the most commonly used function modes for implementing serial protocols are briefly described:

- UART
- I2C
- SPI
- PWM
- SMI

Programming Examples
--------------------
- Python
- C++

