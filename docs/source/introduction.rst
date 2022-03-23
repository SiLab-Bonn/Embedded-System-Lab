============
Introduction 
============

This modular lab course gives an introduction to selected aspects of analog signal processing and data acquisition using an embedded system. The system hardware is based on a Raspberry Pi single board computer which is connected to a custom base board. The base board allows access to various interfaces (UART, I2C, SPI etc.) which are implemented via the general purpose IO ports (GPIO). In addition, the base board features a fast 12-bit ADC, which allows the Raspberry Pi to be used as a simple oscilloscope to sample waveforms for further processing, documentation, and analysis.

The individual experiments are featuring dedicated add-on boards (modules) which are controlled from the Raspberry Pi via an SPI bus and other GPIO signals. In addition, the on-board ADC will be used to record data (for some experiments) and other lab equipment like power supplies will be controlled as well. The goal of each experiment is:

 - Develop the required software to control the given module, 
 - Acquire various measurement data and
 - Document and analyse the measurements.

Every experiment comes with basic code examples which can but don't have to be used to get started. The example software is mainly written in Python but C examples are also given in some places. The code examples and additional documentation is maintained on  `GitHub <https://github.com/hansk68/Embedded-System-Lab>`_.