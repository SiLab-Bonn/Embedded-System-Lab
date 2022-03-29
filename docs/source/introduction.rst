============
Introduction 
============

This modular lab course gives an introduction to selected aspects of analog signal processing and data acquisition techniques. An embedded system running user programs written in Python and/or C is used to directly interact with different signal processing circuits. The embedded system hardware is based on a Raspberry Pi single board computer which is mounted to a custom base board. The base board allows access to various interfaces (UART, I2C, SPI etc.) which are implemented via the general purpose IO ports (GPIO). In addition, the base board features a fast 12-bit ADC, which allows the Raspberry Pi to be used as a simple oscilloscope to sample waveforms for further processing, documentation, and analysis.

.. figure:: images/base_board.png
    :width: 600
    :align: center

    Picture of the Raspberry 4 with the base board attached. 

The individual experiments are featuring dedicated add-on boards (modules) which are controlled from the Raspberry Pi via an SPI bus and other GPIO signals. In addition, the fast on-board ADC is used to record analog waveforms and other lab equipment like power supplies are controlled by the Raspberry Pi as well. In the course of each experiment, the user will:

- Develop the required scripts to control the given module, 
- Acquire various measurement data and
- Document and analyse the measurements.

Each experiment comes with basic code examples which can (but don't have to) be used to get started. The example software is mainly written in Python but C examples are also given in some places. 