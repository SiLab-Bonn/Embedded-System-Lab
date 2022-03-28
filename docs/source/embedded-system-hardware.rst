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

There are special control registers which configure the GPIO ports to become an input or output port according to the required functionality. For many control tasks this simple so-called bit-banging IO interface is sufficient. For more complex tasks and data transfers requiring higher bandwidth, standardized protocols are available.
To offload the CPU from implementing these protocols and to allow a precise protocol timing which is not affected by the CPU multi-tasking, special hardware blocks can be selectively connected to the GPIO ports. These blocks are enabled by selecting alternative function modes for a given GPIO pin. Every GPIO pin can carry an alternate function (up to 6) but not every alternate functions is available to a given pin as described in Table 6-31 in :download:`BCM2837-ARM-Peripherals.pdf <documents/BCM2837-ARM-Peripherals.pdf>`. Note that this documents actually describes the predecessor of the BCM2711 the BCM2873, which is used on the Raspberry Pi 3 modules. However, the given description of the GPIO port is still valid for the new chip.
Here is an example of a GPIO function register (see also chapter 6.1 in BCM2837-ARM-Peripherals document):

.. table:: GPIO Function Select Register (GPFSEL0 @ 0x7E200000):
    : widths: auto
    ===== =========== ====================== ==== =======
    Bit   Field Name  Description            Type Default
    ===== =========== ====================== ==== =======
    31-30 ---         Reserved                R     0
    29-27 FSEL9       Function Select GPIO9   R/W   0
    26-14 FSEL8       Function Select GPIO8   R/W   0
    23-21 FSEL7       Function Select GPIO7   R/W   0
    20-18 FSEL6       Function Select GPIO6   R/W   0
    17-15 FSEL5       Function Select GPIO5   R/W   0
    14-14 FSEL4       Function Select GPIO4   R/W   0
     11-9 FSEL3       Function Select GPIO3   R/W   0
      8-6 FSEL2       Function Select GPIO2   R/W   0
      5-3 FSEL1       Function Select GPIO1   R/W   0
      2-0 FSEL0       Function Select GPIO0   R/W   0
    ===== =========== ====================== ==== =======

There are 6 registers of this type (GPFSEL0 - GPFSEL5) to cover all 54 GPIO pins. Each 3-bit word selects one out of eight function modes:

.. table:: Function Modes
    : width: auto
    ===== ===================
    

 


- GPIO Multiplexer

- UART
- I2C
- SPI
- PWM
- SMI

Programming Examples
--------------------
- Python
- C++

