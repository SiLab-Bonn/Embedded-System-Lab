.. include:: replacements.rst
==============================================================
Experiment: Analog Signal Processing for Semiconductor Sensors
==============================================================

.. figure:: images/afe.png
    :width: 600
    :align: center

    Analog Front-end Module

The goal of this lab is to understand typical analog signal processing steps used for read-out of semiconductor detector charge signals, plus the associated basic data acquisition and analysis methods. In this module, a single-channel analog front-end (AFE) chain made of discrete hardware components will be used to analyze the functionality of each circuit block. In particular the characterization of the noise performance and its dependence on circuit parameters will be discussed. The electrical connections to the AFE hardware allow injection of calibration charge signals, programming of circuit parameters, and the detection of hits. On the software side, scan routines will be developed to set the circuit parameters of interest and read the AFE digital output response. Basic analysis methods will be introduced to extract performance parameters such as equivalent noise charge (ENC), charge transfer gain, linearity etc. Additionally, the fast ADC can be used to record analog waveforms for further analysis.

Signal Processing Overview
==========================
A typical analog read-out chain - also called analog front-end - for a semiconductor detector consists of a charge sensitive amplifier (CSA), a pulse shaping amplifier (SHA) and digitization circuit, which simplest implementation is a comparator (COMP), as shown in the picture below. The CSA converts the charge signal of a detector diode (or an injection circuit) to a voltage step according to the feedback capacitance :math:`C_f` . The shaping amplifier (SHA) acts on the CSA output as a signal filter with a band-pass transfer function. By adjusting its band-pass center frequency the signal-to-noise ratio of the signal processing chain can be optimized. The comparator compares the output of the shaped signal with a programmable threshold. When the input signal is above the threshold, the comparator output goes high and flags a signal hit to the digital read-out logic.

.. figure:: images/AFE_signal_flow.png
    :width: 600
    :align: center

    Generic read-out chain for a semiconductor detector: charge sensitive amplifier (CSA), pulse shaping amplifier (SHA), and comparator (COMP). Shown are typical signal waveforms between the blocks and the parameters that can be controlled for each block.

Circuit Implementation
======================
The simplified schematic in the figure below shows the implementation of the signal processing chain. The CSA is build around a low noise op-amp that is feed-back with a small capacitance :math:`C_f` and a large resistance :math:`R_f`. The feedback capacitance :math:`C_f` defines the charge transfer gain and the resistance :math:`R_f` allows for a slow discharge of :math:`C_f` and setting of the dc operation point of the op-amp. The output voltage of the charge sensitive amplifier in response to an input charge *Q* is a step function with an amplitude given by the expression:

.. math::

  V_{CSA} = \frac{Q}{C_f}.

For calibration and characterization measurements an injection circuit is used to generate programmable charge signals. On the rising edge of the digital **INJ** signal a negative charge of the size :math:`C_{INJ}` times the programmable voltage step amplitude **VINJ** is injected to the CSA input.


.. figure:: images/AFE_simple_schematic.png
    :width: 600
    :align: center

    Simplified schematic of the analog front-end. **INJ** and **HIT** control the charge injection and digital hit readout, respectively. The **SPI** bus is used to program the DAC voltages **VTHR** and **VINJ** and select the shaping amplifier time constant. The full AFE schematic is found here: :download:`AFE_1.1.pdf <documents/AFE_1.1.pdf>`

The shaping amplifier consists of a first-order high pass filter (HPF) and a first-order low pass filter (LPF). Therefore such a filter is also called CR-RC shaper. The high- and low-pass filter are isolated by a voltage amplifier that adds additional signal gain to the circuit. A total gain of :math:`g = 1000` is achieved by using three gain stages with :math:`g' = 10` each. They are located at the CSA output, between the high-pass filter and the low-pass filter (signal **HPF**) and at the output of the shaper (**SHA**), respectively. The time constants of the high- and low-pass filter are controlled by selecting the resistor values for :math:`R_{HP}` and :math:`R_{LP}`. The control circuit sets the values such :math:`\tau_{SHA} = \tau_{HP} = \tau_{LP}`, i.e. the time constants for low pass filter and high pass filter are equal (:math:`C_{HP} = C_{LP} = const.`). It can be shown that in this case the pulse shape in response to an input step function with the amplitude :math:`V_{CSA}` is (for :math:`t \geq 0`) 

.. math::

  V_{SHA}(t) = V_{CSA} \cdot g \cdot \frac{t}{\tau_{SHA}} \cdot e^{\frac{-t}{\tau_{SHA}}},

with the peak amplitude:

.. math::

  V_{SHA}^{peak} = V_{SHA}(t=\tau_{SHA}) = V_{CSA} \cdot g \cdot e^{-1} = \frac{Q}{C_{f}}\cdot g \cdot e^{-1},

where :math:`V_{CSA} = \frac{Q}{C_f}`. The charge sensitivity of the whole signal chain can be expressed as

.. math::

  g_{q} = \frac{V_{SHA}^{peak}}{Q} = \frac{1}{C_{f}} \cdot g \cdot e^{-1},

and is typically given in units of :math:`[mV/fC]` or :math:`[mV/electrons]`.


The final circuit block is the comparator (also called discriminator), which compares the output signal of the shaping amplifier **SHA_OUT** with a programmable threshold voltage **VTHR**. WWhen the input signal arriving from the shaper is above the voltage threshold, the comparator will produce a 'logic high' output. Assuming a constant threshold, the width of the comparator output signal is a function of the signal amplitude. Some systems detect this pulse width (aka **TOT**, time over threshold) to get a measure of the incident charge. On our AFE board, the subsequent digital signal processing for processing the comparator output is implemented in a CPLD (Complex Programmable Logic Device). For the measurement of the time-over-threshold (TOT), this logic IC can be extended as depicted in the schematic diagram below.

.. figure:: images/AFE_digital.png
    :width: 500
    :align: center

    Digital logic implemented in the CPLD. The SR flip-flop is set by the comparator output going high while the 8-bit counter measures the comparator pulse width (time-over-threshold), which value can be read out the SPI interface. A low state of the **INJ** resets HIT signal and TOT counter.



In our particular implementation of the digital signal processing, there first is a set-reset (SR) flip-flop which is asynchronously set by the rising edge of the comparator output signal **COMP**. The flip-flop output signal **HIT** stays high until it is reset by the **INJ** line going low. Parallel to the flip-flop, the **COMP** signal enables an 8-bit counter that has its output incremented (every 25 ns) by a 40 MHz clock signal **CLK**, thereby effectively measuring the comparator output pulse width (time-over-threshold). This **TOT** value can subsequently be read out via a SPI interface implemented in the CPLD logic (**CS_B**, **SCLK** and **MISO**). Finally, a high to low transition from **INJ** resets the TOT counter.

The electrical interface to control the AFE consists of 

* An **SPI** interface controlling

  * the shaping amplifiers time constants by selecting filter resistor values via a multiplexer
  * a digital to analog converter (DAC) which sets the injection step voltage **VINJ** and the comparator threshold **VTHR**
  * the read-out of the TOT counter value via the CPLD SPI interface (if implemented)

* And two **GPIO** signals

  * **INJ** output signal (**GPIO4**, from Rpi to AFE module) that triggers the injection signal and resets the comparator latch
  * **HIT** input signal (**GPIO5**, from AFE module to Rpi) for reading the digital hit output
  
A typical charge injection and digital read-out cycle would look like this:

1. Set **INJ** to '0' to reset the **HIT** output of the digital logic (and TOT counter, if implemented).
2. Set threshold, injection level (and shaping constant) as required.
3. Set **INJ** to '1' to trigger the injection of a negative charge signal. Add a small delay (~100 us) to allow the signal to propagate through the circuit.
4. Check the state of the **HIT** signal. If a high level of the **HIT** is detected store the information. If the (optional) TOT signal is to be acquired, wait approx. another 100 µs (the maximum detectable pulse width) to allow the counter to stop before being read-out.
5. Set **INJ** back to low to reset the **HIT** signal and the TOT counter.
6. Since the CSA also responds to positive charge injection (**INJ** going low), wait for ~ 200 µs to allow the circuit to settle before triggering the next injection. 


Data Acquisition and Analysis Methods
=====================================

An important performance metric of a signal processing circuit is its signal-to-noise ratio (SNR), which is directly related to the efficiency and accuracy of the detection process. A noiseless system would generate a comparator hit signal with 100 % probability if the signal is above threshold and always detect no hit if the signal is below threshold. In the presence of noise, however, the step-like response function of the comparator hit probability as a function of the difference between signal and threshold is smeared out. The following figure shows the comparator response probability of a real system and an ideal system. When the injected charge is equal to the comparator threshold :math:`Q_{INJ} = Q_{THR}`, the hit probability is 50% in both cases. In a noiseless system the hit probability immediately goes to 0 % (100 %) for lower (higher) charge. The noise smooths out this transition region. Actually the knowledge of the slope at the 50 % probability mark allows the calculation of the noise. Mathematically, the response curve is given by a Gaussian error-function (aka s-curve). It is the convolution of a step-function (the ideal comparator response) with a Gaussian probability distribution (representing the noise).


.. figure:: images/AFE_scurve.png
    :width: 400
    :align: center

    Response probability of the comparator as a function of the signal charge. The ideal system (noiseless, blue curve) exhibits a step function, while noise (red curve) will smear-out the transition. That results in a Gaussian error-function, which fitted parameters define the threshold (50 % transition point) and the noise (slope of the curve) of the system.

The measurement of an s-curve is based on a nested loop of injection/read-out cycles. The following steps need to be implemented in a scan routine (also called **threshold scan**):

1. Set threshold and shaping time constant to the desired values.
2. Outer loop: Define a range of injection voltage values (i.e. injection DAC values) to scan. The injection range must cover the chosen threshold, i.e. the transition from zero hits to 100 % hits must occur within the scan range.
3. Inner loop: For each charge value repeat the injection and read-out cycle (see above) a number of times (typical 100) and count the number of detected comparator signals in relation to the total number of injections.
4. Finally plot the hit probability data as a function of the injection voltage.
          
The dataset for the injection voltage scan will represent an s-curve that allows the extraction of the threshold and the noise. For a quantitative evaluation of the s-curve the injection voltage (i.e. DAC setting) has to be converted to the equivalent injection charge :math:`Q_{INJ}`. 

.. math::
  
  Q_{INJ}= k \cdot  V_{INJ} \cdot C_{INJ}

with :math:`k = 0.1` for the attenuation of the resistive divider in front of the injection switch and :math:`C_{INJ} = 0.1 pF` for the injection capacitance which converts the voltage step into a charge.

.. math::
  
  Q_{INJ}[fC]= 0.01 [pF] \cdot V_{INJ}[mV] 
    
or 

.. math::

  Q_{INJ}[e] = 0.01 [pF] \cdot V_{INJ}[mV] \cdot 10^{-15} \cdot q^{-1} 

with the elementary charge :math:`q = 1.602 \cdot 10^{-19} C`.

The threshold voltage of the comparator corresponds to the peak amplitude of the shaper for 50 % hit probability. Therefore, the threshold can be expressed in units of input charge dividing the threshold voltage by the charge sensitivity of the system :math:`g_{q}` as calculated above. 

.. math::
  
  V_{THR}[e] = \frac{V_{THR}[mV]}{g_{q}}


Both voltages **VTHR** and **VINJ** are generated by a 12-bit digital to analog converter (DAC). The maximum output voltage of the DAC is 2048 mV. This corresponds to a LSB step size of 0.5 mV for **VTHR** and 0.05 mV for **VINJ**, respectively, taking into account the attenuation of an additional resistive divider in front of the injection capacitor. With this information the threshold and the injected charge can be converted from DAC register units to charge units (electrons). With this ideal equations and ideal gain constants, the shift along the x-axis for s-curves measured at different threshold settings would be equal to the difference of the injected charge, i.e. if the threshold would be changed by a certain amount of charge (threshold voltage DAC change) the 50 % point of the s-curve would shift by the same amount of injected charge (i.e injection voltage DAC value). However, as the later experiments will show, the gain constants are not ideal and the conversion of the x-axis of the s-curve to charge units has to be calibrated by measurement. The dominant error contributions come from the fact that the sensitive components (i.e. the injection and the feed back capacitance) are very small and therefore the effective capacitance is affected by the parasitic capacitance of the PCB. What can be measured with the injection circuit is the ration of the injection gain and the charge sensitivity of the system. An absolute calibration can only be achieved with a detector diode exposed to a monochromatic X-ray source (radioactive isotope), which would generate a known amount of charge in the sensor, avoiding the uncertainties in the size of the injection capacitance :math:`C_{INJ}`.


Exercises
=========

The exercises are grouped into three parts. In the first part the basic functionality of the analog front-end is tested. This is accomplished by implementing a script to enable the charge injection and to observe waveforms of the charge sensitive amplifier, shaper, and comparator with an external oscilloscope and/or the fast ADC on the Raspberry Pi base board. In the second part methods to extract analog performance parameters from the digital hit information will be developed. Finally, the full analog signal processing chain will be characterized as a function of shaping time and detector capacitance. 

The exercise 0 contains preparatory questions that should be answered before coming to the lab.

.. admonition:: Exercise 0. Preparatory questions

  #. The injection circuit generates a charge signal of the size :math:`C_{inj} \cdot V_{inj}`. What is the charge in femto Coulomb generated by a voltage step of 100 mV with :math:`C_{inj} = 0.1 pF`? What is the charge step size for :math:`V_{inj} = 0.05 mV`, which corresponds to the effective LSB size of the injection voltage DAC? Also calculate these numbers in units of the elementary charge (electrons).
  #. An ideal charge sensitive amplifier generates a step-like output waveform in response to an instantaneous charge signal at the input. What is the **CSA** output step amplitude for an input charge of 1 fC given the feedback capacitance of 1 pF? How is the charge transfer gain defined and what is the unit of the charge transfer gain?
  #. A shaping amplifier responds with a characteristic output pulse to a step-like input waveform. What is the peak pulse amplitude for an input step with a unit amplitude (i.e. 1 V)? Assume a CR-RC (high-pass + low-pass filter) with equal time constants.
  #. What is the ideal charge sensitivity of the experiments analog front-end chain (CSA + SHA) i.e., peak amplitude in mV at the shaper output per fC (or electron) charge at the CSA input? 
  #. The threshold voltage to detect a signal with the comparator is set by a DAC with an LSB size of 0.5 mV. What is the equivalent LSB size in fC or electrons ? (Use the total charge sensitivity as calculated above.)
  #. An amplitude histogram of an ideal noise-free system would consist of delta-like peaks for the baseline and the shaped signal produced by a constant input charge. In a real system, however, noise is overlaying the ideal signals, leading to fluctuations of the analog amplitudes. Modify the amplitude histogram to reflect these fluctuations (assume a Gaussian distribution of the noise).
  #. The threshold of the comparator should be set in a way, that the noise is suppressed and only the signals are detected. Draw an optimum threshold in your amplitude histogram. What would happen if the threshold was too low, what would happen if it was too high? How are purity and efficiency of the detection process defined in this context? What happens if baseline and signal fluctuations are getting too close to each other?
  #. The term 'equivalent-noise-charge' (ENC) represents the number of electrons at the input of an ideal (noise-free) charge sensitive signal chain that would produce the same  amplitude at the output as the noise alone would in a real system. What is the ENC value for a noise amplitude of 10 mV given the charge sensitivity calculated above?
  #. How are the Gaussian distribution and the error-function related? How can one extract the width (sigma) and the mean (lambda) of the underlying Gaussian distribution from a measured error function?
  #. Calculate and plot the time-over-threshold as a function of the ratio of CR-RC shaper peak amplitude and threshold voltage.


.. admonition:: Exercise 1. Waveform measurements

  This exercise is intended to familiarize yout with the analog front-end hardware and the control software. The goal is to observe the different signals of the analog front-end chain (CSA, SHA, COMP) and to understand the effect of the different circuit parameters on the signal shape. To monitor the signal waveform, connect an oscilloscope to the LEMO socket **OUTPUT**. Use the jumper bank in front of the LEMO socket to select the signal to be monitored manually (**CSA, HPF, SHA, COMP**) or use the setting **MUX** to select the signal to be monitored via your program code with the **SPI** interface. Note: As mentioned in the circuit description above, the shaper circuit adds a total gain of 1000 to the CSA output signal. This gain is split in three gain stages with G=10 that are distributed along the signal chain in front of the **CSA**, the **HPF**, and the **SHA** output, respectively. The **CSA** output is amplified by 10, the **HPF** accumulated amplification is 100 and the shaper output **SHA** finally accumulates the total gain of 1000. 

  Once you are familiar with the signal generation and monitoring switch from the external oscilloscope to the fast ADC on the Raspberry Pi base board to record and save the waveform data for further analysis. Connect the monitor signal to the **ADC** input on the base board and set the gain jumper to **1**. The trigger for the waveform acquisition should be derived from the charge injection signal. To select this trigger source set the **TRG** jumper to **GPIO4**. The fast ADC is controlled by a Python script ``osc.py`` which can be found in the folder ``FAST_ADC``. The script needs root privileges to access the interface to the fast ADC and thus has to be started by calling ``sudo -E python osc.py``. A simple command line interface of the ``osc.py`` tool will allow you to set the horizontal resolution and the saving of acquired waveform data to file (csv) or to save a waveform image (png).


  #. Implement a script to continuously inject charge pulses into the CSA. To change configuration parameters (injection amplitude, time constants, output channel of the signal monitor multiplexer) while injecting, use threading to run the injection loop in parallel to the configuration loop (see ``threads.py`` as an example for using threads in Python). 
  #. A negative charge is injected with the rising edge of the **INJ** signal, which will generate a positive amplitude at the **CSA**, **HPF**, and **SHA** outputs. What happens at the falling edge of the **INJ** signal? What happens if the time delay between the rising and the falling injection signal is too short? What time constants do you have to take into account to estimate the maximum injection frequency?
  #. Run your injection script and observe the different signals (**CSA**, high-pass filter **HPF**, shaper **SHA**, and comparator **COMP**) while varying the injected charge amplitude, shaper time constants, and comparator threshold. Hint: To get a reasonable comparator response, the threshold needs to be set in a range between the baseline of the signal and the pulse peak amplitude (remember the LSB step size of the threshold DAC is 0.5 mV).
  #. Select an injection amplitude that is well within the dynamic range of the system (i.e. no amplitude clipping but also well above the noise floor). Sample the **SHA** output with the fast ADC and save the waveforms to file for each time constant setting of the shaper. Write a script that can read and plot the saved waveform data (CSV format). Add a fitting function to the pulse shape (assume an ideal CR-RC pulse shape with equivalent time constants for low and high pass filter) and extract the peaking time and peak amplitude for each shaper setting. Does the peak amplitude change with the peaking time? Give possible explanations. Optional: Implement a fitting function for the shaper pulse with independent time constants for high and low pass filter.


.. admonition:: Exercise 2. Characterization with the digital read-out

  #. Now select the comparator output with the monitor multiplexer. Set a threshold at half of the shaper peak amplitude (the **Vthr** DAC gain is 0.5 mV/DAC step). Observe the pulse width of the comparator output (time-over-threshold, TOT) for different injection amplitudes. What relation between TOT and injected charge would you expect? An automated TOT measurement can be implemented by using the hit signal to start and stop a timer. This will be implemented later with the FPGA lab module.
  #. Implement a scan routine to measure the s-curve of the system. The s-curve is obtained by measuring the hit probability as a function of the injected charge. The charge is varied by changing the injection voltage. The hit probability is calculated by counting the number of hits (using the comparator output pulse) for a given charge step in relation to the total number of injections. Convert the x-axis of the s-curve from DAC units to charge units using the calibration factor of the injection circuit calculated above (in electrons) **Note:** The effective value of the feedback capacitance is :math:`C_{f}^{eff} = 1.39 pF` due to the parasitic capacitance of the PCB traces and the feedback resistor which add to the nominal value :math:`C_{f} = 1.0 pF`
  #. Use the measured s-curve to extract the threshold (50 % value) and the noise (slope at the 50 % point). Repeat for different threshold settings. Does the change of the measured threshold (in injection charge units) correspond to the change of the threshold DAC setting in threshold charge units (both in electrons) as you have calculated above? How large is the deviation?

 
.. admonition:: Exercise 3. Noise performance measurements 

  #. Acquire s-curves for different shaping time constants. What is the effect of the shaping time on the noise? Do not yet connect a sensor diode to the CSA.
  #. Now connect a sensor diode to the CSA and apply 20 V bias voltage. Repeat the s-curves measurements. What happens if you lower the bias voltage? What is the effect of the detector capacitance on the noise performance?
  #. Connect various test capacitors instead of the sensor diode and plot the noise vs. input capacitance. Repeat the measurements for different shaping time constants.

 
