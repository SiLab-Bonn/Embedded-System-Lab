.. include:: replacements.rst
===================================
Experiment: MOSFET Parameter Extraction
===================================

.. figure:: images/smu.png
    :width: 300
    :align: center

    Source-Meter Module

In this experiment the characteristic I-V curves of (active) electronic devices will be measured and used for the extraction of devices electrical parameters. For example, a MOSFET is typically characterized by it threshold voltage |VTHR|, its transconductance |gm|, which describes its voltage-to-current gain and other parameters, which can be extracted from I-V measurements. The SMU ('source monitoring unit') module used in this experiment provides two programmable voltage sources with a wide range current sensing capability (~mA down to ~nA). The Raspberry Pi connects to the SMU via an I2C bus which writes the data to the on-board DAC which sets the output voltages and reads back the measured output current.

Source Monitoring Unit
=====================

The SMU module has two independent channels which supply a programmable voltage in the range of 0 to ~4 Volts. The voltages are set by a 12-bit DAC which is written via an I2C bus from the Raspberry Pi board. With a reference voltage |VREF| = 4.096 V and 12-bit resolution the DAC LSB corresponds to 1 mV. Thus, the SMU output voltage is 

.. math::
  
  V_{OUT} = DAC_{REG} \cdot \frac{V_{REF}}{4096} =  DAC_{REG} [\text{mV}].

The DAC output voltage is buffered by an opamp configured as a unit gain buffer. A sense resistor |RSNS| at the opamp output is used for the current measurement. The voltage drop across |RSNS| is amplified by a difference amplifier with a gain of 10 and then digitized by an 12-bit ADC which is also connected to the I2C bus. The figure below shows the simplified circuit diagram of one SMU channel.

 .. figure:: images/SMU_block.png
    :width: 600
    :align: center

    Simplified circuit diagram

To improve the dynamic range of the current measurement, the sense resistor |RSNS| can be selected from three values (8 Ohm, 800 Ohm and 80 kOhm). The selection is controlled via a multiplexer which is programmed over the I2C bus. The programmable sense resistor enables these current measurement ranges: 


    ========  ===========  ==================  ==========
    SEL[1:0]  |RSNS|[Ohm]   Max. current [A]    I LSB [A]  
    ========  ===========  ==================  ==========
      00        ---         Output is off         ---      
      01        80 k          5 µ                1.25 n      
      10       800          500 µ                 125 n      
      11         8           50 m                12.5 µ      
    ========  ===========  ==================  ==========

The ADC input voltage |VISNS| which corresponds to the SMU output current is given by

.. math::
  
  V_{ISNS} = I_{OUT} \cdot R_{SNS} \cdot 10.

The 12-bit ADC converts this voltage according to

.. math::

  ADC_{CODE} = V_{ISNS} \cdot \frac{4096}{V_{REF}} = I_{OUT} \cdot R_{SNS} \cdot 10 \cdot mV^{-1}.

and therefore

.. math::

  I_{OUT} = \frac{ADC_{CODE}}{R_{SNS} \cdot 10} \cdot mV.


This formula is the conversion factor (conversion gain) to calculate the output current in mA units from the ADC code. To use the full dynamic current measurement range, the switching between current ranges can be automated by the measurement scripts. For example during a voltage sweep, the measured current should be compared to threshold values defined by the boundaries between the current measurement ranges (5 µA and 500 µA) and the ranges selected accordingly.

There are a few more circuit details which are found in the full circuit schematic: :download:`SMU_1.1.pdf <documents/SMU_1.1.pdf>`. For example, the module has on-board sockets to connect a transistor to the SMU output channels without using the LEMO connectors. Other circuits elements are used to decrease the output resistance of the multiplexer in the highest current range and to limit the output current to the range maximum.

I-V Curve Measurements
======================

The simplest I-V curves are obtained by a measuring a device with two ports (a resistor or a diode, for example) which gets connected to one of the SMU outputs. The measurement script then sweeps the the output voltage of the used channel in a given range and step size. The smallest voltage step is 1 mV which corresponds to one DAC bit (see DAC output voltage calculation above). For faster voltage sweeps with less points, the voltage step size can be increased. In the scan loop, the output current is measured for each voltage step and both values are stored for later plotting and analysis. 

Devices with more than two ports like transistors typically have more than one voltage applied. For example the input characteristic of a MOSFET (drain current |ID| as a function of the gate voltage |VGS|) requires the drain and the gate potential to be individually controlled (i.e. |VGS| is swept while |VDS| is held constant). For those kind of I-V measurements, both SMU channels will be used simultaneously. 

MOSFET Parameter Extraction
===========================

A MOSFET is characterized with a number of electrical parameters describing its dc- and ac- performance. Many of these parameters are typically found in the devices datasheet and even more parameters are needed for simulation models. Simple I-V scans, however, can be used to extract the most important MOSFET parameters: 

 * Transconductance |gm| 
 * Threshold voltage |VTHR| 
 * Subthreshold slope
 * Output resistance |go|

 The MOSFET input characteristic (|ID| vs |VGS| curve) will be used to extract transconductance |gm|, threshold voltage |VTHR| and subthreshold slope, and the output characteristic (|ID| vs |VDS| curve, with |VGS| as a parameter) will be used to extract the output resistance |go|.

 ....


.. admonition:: Exercise 0. A bit of theory

  #. Plot the theoretical current measurement error as a function of the current for a fixed current measurement range (no switching of |RSNS|). Assume that the error is only defined by the ADC resolution. Repeat the plot considering automatic switching of the current measurement range. Also use a logarithmic y-scale for the plots.
  #. List and describe the operation regions of a MOSFET. What are the meanings of weak-, moderate- and strong inversion? What is the difference between linear- and saturation region?. Plot example I-V curves to explain.
  #. Derive the formula for definition of the transconductance |gm|. 
  #. What different methods exist to extract |VTHR| from I-V curves?


.. admonition:: Exercise 1. I-V scan loop implementation
  
  #. Write a simple script which allows to set the output voltage and read back the current of an SMU channel (you also need to set a current range, otherwise the output will be off). Control the output voltage with a DVM and compare the measured voltage with the value you have set in the script.
  #. Add a loop statement to the script and connect a 1 kOhm resistor to the output. Measure and plot I-V curves for different resistor values. Discuss the choice of current measurement range (fixed ranging).
  #. Connect a diode to the SMU and plot the I-V curve for the forward region of the diode. Make the scans for all three current ranges separately and combine the traces in one plot. Remember to set the calibration constant to convert ADC code to current according to the selected current range.


.. admonition:: Exercise 2. Automatic current range selection

  #. Implement an "autoranging" functionality in the scan loop. Measure the diode I-V curve again and plot linear and log current scales. 
  #. ....

.. admonition:: Exercise 3. MOSFET Parameter Extraction

  .....