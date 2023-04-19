===================================
Experiment: Device Characterization
===================================

.. figure:: images/smu.png
    :width: 300
    :align: center

    Source-Meter Module

In this experiment the characteristic I-V curves of (active) electronic devices will be measured and used for the extraction of devices electrical parameters. For example, a MOSFET is typically characterized by it threshold voltage VTHR, its transconductance (gm, which describes its voltage-to-current gain) and other parameters, which can be extracted from I-V measurements. The SMU ('source monitoring unit') module used in this experiment provides two programmable voltage sources with a wide range current sensing capability (~mA down to ~nA). The Raspberry Pi connects to the SMU via an I2C bus which writes the data to the on-board DAC which sets the output voltages and reads back the measured output current.

Source Monitoring Unit
=====================

The SMU module has two independent channels which supply a programmable voltage in the range of 0 to ~4 Volts. The voltages are set by a 12-bit DAC which is written via an I2C bus from the Raspberry Pi board. With a reference voltage VREF = 4.096 V and 12-bit resolution the DAC LSB corresponds to 1 mV. Thus, the SMU output voltage is 

.. math::
  
  V_{OUT} = DAC_{REG} \cdot \frac{4096 mV}{2^12} =  DAC_{REG} \cdot mV.

The DAC output voltage is buffered by an opamp configured as a unit gain buffer. A sense resistor Rsns at the opamp output is used for the current measurement. The voltage drop across Rsns is amplified by a difference amplifier with a gain of 10 and then digitized by an 12-bit ADC which is also connected to the I2C bus. 

To improve the dynamic range of the current measurement, the sense resistor Rs can be selected from three values (8 Ohm, 800 Ohm and 80 kOhm). The selection is controlled via a multiplexer which is programmed over the I2C bus. The programmable sense resistor enables these current measurement ranges: 

    ========  ===========  ==================  ==========
    SEL[1:0]   Rsns [Ohm]   Max. current [A]    I_LSB [A]  
    ========  ===========  ==================  ==========
      00        ---         Output is off         ---      
      01        80 k          5 µ                1.25 n      
      10       800          500 µ                 125 n      
      11         8           50 m                12.5 µ      
    ========  ===========  ==================  ==========

The ADC input voltage V_ISNS which corresponds to the SMU output current is given by

.. math::
  
  V_{ISNS} = I_{OUT} \cdot R_{SNS} \cdot 10.

The 12-bit ADC converts this voltage according to

.. math::

  ADC_{code} = V_{ISNS} \cdot \frac{2^12}{4096 mV} = I_{OUT} \cdot R_{SNS} \cdot 10 \cdot mV^{-1}.

This formula leads to the conversion factor given in the above table to calculate the output current in Ampere from the ADC code. To use the full dynamic current measurement range, the switching between current ranges can be automated by the measurement scripts. For example during a voltage sweep, the measured current should be compared to threshold values defined by the boundaries between the current measurement ranges (5 µA and 500 µA) and the ranges selected accordingly.

There are a few more circuit details which are found in the full circuit schematic: :download:`SMU_1.1.pdf <documents/SMU_1.1.pdf>`. For example, the module has on-board sockets to connect a transistor to the SMU output channels without using the LEMO connectors. Other circuits elements are used to decrease the output resistance of the multiplexer in the highest current range and to limit the output current to the range maximum.

I-V Curve Measurements
======================

The simplest I-V curve is obtained by a measuring a resistor by connecting the output of a single SMU channel to it. Of course, also other devices with two ports like (i.e. diodes) are connected that way. Devices with more than two ports like transistors typically have more than one voltage applied. For example the input characteristic of a MOSFET (drain current I_D as a function of the gate voltage V_GS) requires the drain and the gate potential to be individually controlled (i.e. V_GS is swept while V_DS is held constant).

MOSFET Parameter Extraction
===========================
