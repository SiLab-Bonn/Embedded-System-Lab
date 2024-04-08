.. include:: replacements.rst
===================================
Experiment: SMU and MOSFET Parameter Extraction
===================================

.. figure:: images/smu.png
    :width: 300
    :align: center

    Source-Meter Module

In this experiment the characteristic I-V curves of (active) electronic devices will be measured and used for the extraction of devices electrical parameters. For example, a MOSFET is typically characterized by it threshold voltage |VTHR|, its transconductance |gm|, which describes its voltage-to-current gain and other parameters, which can be extracted from I-V measurements. The SMU ('source monitoring unit') module used in this experiment provides two programmable voltage sources with a wide range current measurement capability (~mA down to ~nA) spanning over three current measurement ranges. To achieve the best measurement accuracy, the current measurement range needs to be selected according to the expected current values. The Raspberry Pi communicates with the SMU via an I2C bus that writes the data to set the output voltages, sets the current mesuarement eange, and reads back the measured output current. 



Source Monitoring Unit
=====================

The SMU module is a dual channel voltage source that supports single-quadrant measurements. That means it can only generate positive potentials and the measurement polarity is restricted to current flowing out of the module into the device. Four-quadrant SMUs, as typically available with commercial test equipment, can do bipolar current measurement independent of the polarity of the output voltage. Commercial SMUs can also be configured to work as a programmable current source while this module only implements a voltage source mode.

The SMU module has two independent channels which supply a programmable voltage in the range of 0 to ~4 Volts. The voltages are set by a 12-bit DAC which is connected to the I2C interface of the Raspberry Pi. With a reference voltage |VREF| = 4.096 V and 12-bit resolution the DAC LSB corresponds to 1 mV. Thus, the SMU output voltage is 

.. math::
  
  V_{OUT} = DAC_{REG} \cdot \frac{V_{REF}}{4096} =  DAC_{REG} \cdot mV.

The DAC output voltage is buffered by an opamp configured as a unity gain buffer. A sense resistor |RSNS| at the opamp output is used for the current measurement. The voltage drop across |RSNS| is amplified by a difference amplifier with a gain of 10 and digitized by a 12-bit ADC which is also connected to the I2C bus. The figure below shows the simplified circuit diagram of one SMU channel.

 .. figure:: images/SMU_block.png
    :width: 600
    :align: center

    Simplified circuit diagram of a single SMU channel.

To improve the dynamic range of the current measurement, the sense resistor |RSNS| can be selected from three values (8 Ohm, 800 Ohm and 80 kOhm). The selection is controlled via a multiplexer that is also programmed over the I2C bus. The programmable sense resistor enables these current measurement ranges: 


===========  ========  ===========  ==================  ==========
 Range       SEL[1:0]  RSNS [Ohm]   Max. current [A]    ADC resolution [A]  
===========  ========  ===========  ==================  ==========
  Off          b00        ---         Output is off         ---      
  LOW          b01        80 k         5.12 µ             1.25 n      
  MID          b10       800            512 µ               125 n      
  HIGH         b11         8           51.2 m              12.5 µ      
===========  ========  ===========  ==================  ==========

The ADC input voltage |VISNS| as a function of the SMU output current is given by

.. math::
  
  V_{ISNS} = I_{OUT} \cdot R_{SNS} \cdot 10.

The 12-bit ADC converts this voltage according to

.. math::

  ADC_{CODE} = V_{ISNS} \cdot \frac{4096}{V_{REF}} = I_{OUT} \cdot R_{SNS} \cdot 10 \cdot mV^{-1},

and therefore

.. math::

  I_{OUT} = \frac{ADC_{CODE}}{R_{SNS} \cdot 10} \cdot mV.


This formula is the conversion factor (conversion gain) to calculate the output current in mA units from the ADC code. To use the full dynamic current measurement range, the switching between current ranges can be automated by the measurement scripts: During a voltage sweep, the measured current should be compared to threshold values defined by the boundaries between the current measurement ranges (5 µA and 500 µA) and the ranges selected accordingly.

There are a few more circuit details that are found in the full circuit schematic: :download:`SMU_1.1.pdf <documents/SMU_1.1.pdf>`. For example, the module has on-board sockets to connect a transistor to the SMU output channels without using the LEMO connectors. Other circuits elements are used to decrease the output resistance of the multiplexer in the highest current range and to limit the output current to the range maximum.



I-V Curve Measurements
======================

The simplest I-V curves are obtained by a measuring a device with two ports (a resistor or a diode, for example) connected to one of the SMU outputs. The measurement script then sweeps the the output voltage of the used channel in a given range and step size. The smallest voltage step is 1 mV which corresponds to one DAC bit (see DAC output voltage calculation above). For faster voltage sweeps with less points, the voltage step size can be increased. In the scan loop, the output current is measured for each voltage step and both values are stored for later plotting and analysis. 

Devices with more than two ports like transistors typically have more than one voltage applied. For example the input characteristic of a MOSFET (drain current |ID| as a function of the gate voltage |VGS|) requires the drain and the gate potential to be individually controlled (i.e. |VGS| is swept while |VDS| is held constant). For those kind of I-V measurements, both SMU channels will be used simultaneously. 

MOSFET Parameter Extraction
===========================

A MOSFET is characterized with a number of electrical parameters describing its dc- and ac- performance. Many of these parameters are typically found in the devices datasheet and even more parameters are needed for simulation models. Special integrated test equipment dedicated for parameter extraction is typically used for this task. Simple I-V scans, however, can be used to extract some of the basic MOSFET parameters: 

 * Transconductance |gm| 
 * Threshold voltage |VTHR| 
 * Subthreshold slope n
 * Output resistance |go|

The MOSFET input characteristic (|ID| vs |VGS| curve) is used to extract transconductance |gm|, threshold voltage |VTHR| and subthreshold slope, and the output characteristic (|ID| vs |VDS| curve, with |VGS| as a parameter) allows the extraction of the output resistance |go|.

 ....

Exercises 
---------
The exercises are divided into three parts: The first part is about the basic operation of the SMU module and the implementation of a simple I-V scan loop. The second part is about the implementation of an automatic current range selection and the improvement of the measurement precision. The third part is about the measurement of I-V curves of a MOSFET and the extraction of its parameters. 
There is a script ``smu.py`` in the folder ``code\SMU`` that contains the necessary includes and the basic configuration for the I2C interface and the I2C devices (DAC, ADC and |RSNS|-MUX) on the SMU module. Copy it into your ``work`` folder and use it as a template for your scripts. There are also another files called ``smu_class.py``, ``smu_preparation.solution.py``, and ``smu_mosfet_solution.py`` that contains working code for most of the exercises. Note that this should only be used for reference or as a last resort if you got stuck. 


.. admonition:: The following preparatory questions should be answered before coming to lab (SMU related)

  #. What do the terms accuracy, resolution, and precision mean? Where is the difference? 
  #. What is the resolution of an ADC? What is the quantization error? (Extra: Derive the formula for the quantization error.)
  #. The current (or voltage) measurement accuracy of an SMU or multimeter is often given as the error in percent of the full scale. How large is this error for the current mesaurement with the 12 bit ADC, taking into account the quantization error only? Does this error depend on the current range?
  #. The voltage source has a maximum output voltage of 4095 mV and 1 mV resolution (12 bit DAC). What would be the appropriate current range for measuring the I-V curve of a 1 kOhm load resistor? How many I-V measurement points would you get? Which value for the curren sense resistor |RSNS| would you choose? 
  #. How many measurement points would you get for a 5 kOhm or a 200 Ohm load resistor, respectively? Hint: If the resistance is higher than 1 kOhm, the number of independent points is limited by the resolution of the current measurement i.e. the ADC range is not fully utilized. If the resistance is lower, the number of (meaningful) measurement points is defined by the maximum current the ADC can measure that will be reached before the full DAC voltage range is used. The plot below illustrates the situation. Shown are the I-V curves for the three resistors using a fixed current range. The 1 kOhm load resistance yields the maximum measurement points while the 5 kOhm (200 Ohm) load resistors I-V curves are limited by the DAC (ADC), respectively. 
  #. The current mesurement ranges of the SMU have a ratio of 1\:100\:1000 (see table above). What would be appropriate threshold values (in ADC counts) for the current range switching? Note that the auto-ranging functionality requires one thresholds for switching from a lower range to a higher range and another threshold for switching from a higher to a lower range (i.e. one threshold at the lower ADC count range and one at the higher ADC count range). What relation between the two thresholds must be met to not have 'gaps' in the combined current measuremnt range? Note\: Typically ADCs perform best if not operated at the extreme ends of their range (i.e. keep the ADC values at least ~10-20 counts from their limits).

  .. figure:: images/smu_ranges.png
    :width: 600
    :align: center

    I-V curves for three load resistors values using a fixed current range.

.. admonition:: Additional preparatory questions to be answered before coming to lab (MOSFET related)

  #. List and describe the operation regions of a MOSFET. What are the meanings of weak-, moderate- and strong inversion? What is the difference between linear- and saturation region? Plot example I-V curves based on a simple (SPICE level 2 MOSFET model) to explain.
  #. Derive the formula for definition of the transconductance |gm|. 
  #. How would one extract the threshold parameter |VTHR| from Id vs. Ugs curve? Also consider the extraction of the subthreshold slope, the transconductance |gm|, and the output resistance |go| (from the Id vs. Uds curve).


.. admonition:: Exercise 1. I-V scan loop implementation
  
  #. Write a simple script that allows to set the output voltage and read back the current of an SMU channel (you also need to set a current range, otherwise the output will be off). Control the output voltage with a voltmeter and compare the measured voltage with the value you have set in the script. Implement the current range selection and check the LED on the board for the selected range.
  #. Add a loop statement to the script and connect a 1 kOhm resistor to the output. Measure and plot I-V curves for all three current measurement ranges (fixed ranging).
  #. Extract the slope and offset from each of the three I-V curves. How well do the three current ranges match? 
  #. Connect a diode to the SMU and plot the I-V curve for the forward region of the diode. Make the scans for all three current ranges separately and combine the traces in one plot. Remember to set the calibration constant to convert ADC code to current according to the selected current range (see equation above).


.. admonition:: Exercise 2. Automatic current range selection

  #. Implement an "auto-ranging" functionality in the scan loop with the ADC count thresholds you have derived in the preporatory part. Measure the diode I-V curve again and plot linear and log current scales. 
  #. Now consider the precision of the current measurement. Repeat each current measurement 100 times and plot the standard deviation as error bars (choose a large voltage step size to limit the scan time). Compare the error to the theoretical limit given by the quantization error (see Exercise 0). What additional noise sources have to be considered?
  #. Improve the measurement precision by averaging over a number of current readings for each voltage step. Consider to adjust the number of averages according to the measurement range to optimize the scan time.
  #. Redo the diode I-V curve with the optimized scan loop and minimum voltage step size. Examine the curve at the points where the current range changes (also plot the derivative). How good do the |RSNS| resistor values match?



.. admonition:: Exercise 3. MOSFET I-V curves

  For measuring transistor I-V curves and extracting parameters, an N-channel MOSFET (BSP295) plugged into a transistor socket on the SMU module will be used. The gate of the MOSFET is permanently connected to output 1 and the drain is connected via a jumper to output 2. The MOSFET source is connected to ground.
  #. The drain current vs. gate voltage curves are measured by sweeping the gate voltage (output 1) and measuring the drain current (output 2) at a constant drain voltage. Write a scan loop to sweep the gate from 0 to 2000 mV and measures the drain current while keeping the drain voltage constant at 200 mV. Repeat the loop (nested loop) with a range of different drain voltages in the range of 100 to 500 mV.
  #. Now add a measurement for the drain current vs. drain voltage characteristic. Sweep the drain voltage from 0 to 2000 mV and measure the drain current for different constant gate voltages in the range of 800 to 1100 mV. Where does the transition from the linear to the saturation region occur?

.. admonition:: Exercise 4. MOSFET parameter extraction

  For extracting some of the MOSFET parameters, the I-V curves (i.e. scan and plotting routines) from the previous exercise will be used and modified.

  #. Implement the extraction of the threshold parameters |VTHR|. Use the drain current vs. gate voltage data from the previous exercise and modify the plot to show the square root of the drain current vs. gate voltage. With the ideal quadratic Id-Ugs relation the threshold voltage is the gate voltage where the square root of the drain current is zero. Why is this not the case with a real MOSFET transistor? 
  #. Now plot the same drain current vs. gate voltage with a logarithmic scale for the drain current. What happens below the threshold voltage? Can the MOSFET still be used to control current in this region? Extract the subthreshold slope (slope factor) from the linear region of the curve.
  #. Plot the transconductance |gm| as a function of the gate voltage. Also plot |gm|/|ID| and |gm|/sqrt(|ID|). What are these plots showing? What would you expect from a ideal MOSFET model? Take a look at the algebraic presentation of these terms using the simple MOSFET model equation.
  #. Extract the output resistance |go| from the drain current vs. drain voltage curves in the saturation region. Identify the "Early" voltage in the linear extrapolation of the |ID| vs. |VDS| curve. What is the physical meaning of the Early voltage?
  #. (Extra) Use the extracted parameters with the formula of a simple MOSFET model to calculate the drain current for the I-V curves. Compare the calculated values with the measured data.
  #. (Extra) Use the manufacturers SPICE model of the BSS295 MOSFET and simulate I-V curves with 'ltspice'. Compare the simulation with your measurements. 


  .....