===========
Experiment: Analog Front-end for silicon sensor read-out
===========
Signal Processing for Semiconductor Detectors
---------------------------------------------
A typical analog read-out chain, also called analog front-end, for a semiconductor detector consists of a charge sensitive amplifier (CSA), a pulse shaping amplifier (SHA) and digitization circuit which simplest implementation is a comparator (COMP), as shown in the picture below. The CSA converts the charge signal of the connected detector diode to a voltage step equal to the ratio of signal charge and feedback capacitance (Qsig/Cf). The shaping amplifier acts on the CSA output as a signal filter with a bandpass transfer function. By adjusting its bandpass center frequency the signal-to-noise ratio of the signal processing chain can be optimized. The comparator compares the output of the shaped signal with a programmable threshold. When the input signal is above the threshold, the comparator output goes high and flags a signal hit to the digital read-out logic.

.. figure:: images/AFE_signal_flow.png
    :width: 600
    :align: center

    Generic read-out chain for a semiconductor detector: charge sensitive amplifier (CSA), pulse shaping amplifier (SHA), and comparator (COMP). Shown are typical signal waveforms between the blocks and the parameters which can be controlled for each block.


The CSA is build around a low noise Opamp which is feed-back with a small capacitance Cf and a large resistance Rf. The feedback capacitance Cf defines the charge transfer gain and the resistance Rf allows for a slow discharge of Cf and setting of the DC operation point of the Opamp. To enable calibration and characterization measurements, an injection circuit is used to generate a programmable CSA input signal. On the rising edge of the digital TRG_INJ signal a negative charge of the size Cinj times the programmable voltage step amplitude Vinj is applied to the CSA input.

.. figure:: images/AFE_simple_schematic.png
    :width: 600
    :align: center

    Simplified schematic of the analog front-end.

Characterization
----------------
 - Charge injection 
 - S-curve measurements
 - Noise vs. SHA_tau / CSA_input load
 - Multi Channel Analyzer
 
