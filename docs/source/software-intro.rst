============================
Introduction to the Software
============================

The Raspberry Pi module runs a Debian-based operating system (Raspberry Pi OS) including a graphical user interface, which looks similar to many common desktops. For the experiments, manly these programs will be used:

- Terminal (what the name suggests)
- Chromium, a web browser which you already use, when you read this document on the RPi
- File Manager
- Visual Code, an integrated development environment for C and Python to develop and run the user code

The code examples and additional documentation is maintained on  `GitHub <https://github.com/hansk68/Embedded-System-Lab>`_. The project structure on the Raspberry Pi file system is organized like this::

 | home
 | |─ Embedded-System-Lab (GitHub root directory)
 | |   |─ docs (sources for this documentation)
 | |   |─ examples (code snippets for the experiments)
 | |   |─ rpi-dma (C code functions for fast ADC readout)
 | |   |─ hardware (documentation: schematics, datasheets)
 | |─ work (user working directory, not synchronized to GitHub)

 
.. note:: 
 User programs and measurement data should be saved in the ``work`` folder. The code examples in the ``Embedded-System-Lab/examples`` folder should not be modified directly but rather copied to the ``work`` folder and modified there, as needed. In case the content of the ``examples`` or any other folder were accidentally changed, the files can be restored by calling ``git checkout *`` from the command line within the respective folder.

Basic Programming Examples
==========================

Input / Output
--------------
- Python
- C++


- LED, Button, PWM
- UART (Rpi to Rpi terminal)
