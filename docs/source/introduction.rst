============
Introduction 
============

This modular lab course gives an introduction to selected aspects of analog signal processing and data acquisition techniques. An embedded system running user programs written in Python and/or C is used to directly interact with different signal processing circuits. The embedded system hardware is based on a Raspberry Pi single board computer which is mounted to a custom base board. The base board allows access to various interfaces (UART, I2C, SPI etc.) which are implemented via the general purpose IO ports (GPIO). In addition, the base board features a fast 12-bit ADC, which allows the Raspberry Pi to be used as a simple oscilloscope to sample waveforms for further processing, documentation, and analysis.

.. image:: images/base_board.png
    :width: 400

The individual experiments are featuring dedicated add-on boards (modules) which are controlled from the Raspberry Pi via an SPI bus and other GPIO signals. In addition, the fast on-board ADC is used to record analog waveforms and other lab equipment like power supplies are controlled by the Raspberry Pi as well. In the course of each experiment, the user will:

- Develop the required scripts to control the given module, 
- Acquire various measurement data and
- Document and analyse the measurements.

Each experiment comes with basic code examples which can (but don't have to) be used to get started. The example software is mainly written in Python but C examples are also given in some places. The code examples and additional documentation is maintained on  `GitHub <https://github.com/hansk68/Embedded-System-Lab>`_. The project structure on the Raspberry Pi file system is organized like this::

 | home
 | |─ Embedded-System-Lab (GitHub root directory)
 | |   |─ docs (sources for this documentation)
 | |   |─ examples (code snippets for the experiments)
 | |   |─ rpi-dma (C code functions for fast ADC readout)
 | |   |─ hardware (documentation: schematics, datasheets)
 | |─ work (user working directory, not synchronized to GitHub)

 
.. note:: 
 User programs and measurement data should be saved in the ``work`` folder. The code examples in the ``Embedded-System-Lab/examples`` folder should not be modified directly but rather copied to the ``work`` folder and modified there, as needed. In case the content of the ``examples`` or any other folder were accidentally changed, the files can be restored by calling ``git checkout *`` from the command line within the respective folder.
