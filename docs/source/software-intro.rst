============================
Introduction to the Software
============================

The Raspberry Pi module runs a Debian-based operating system (32-bit Raspberry Pi OS) including a graphical user interface, which looks similar to many common desktops. For the experiments, manly these programs will be used:

- Terminal (what the name suggests)
- Chromium, a web browser which you already use, when you read this document on the RPi
- File Manager
- Visual Code, an integrated development environment for C and Python to develop and run the user code

The code examples and additional documentation is maintained on  `GitHub <https://github.com/hansk68/Embedded-System-Lab>`_. The project structure on the Raspberry Pi file system is organized like this::

 |─ home
 |  |─ Embedded-System-Lab (GitHub root directory)
 |  |  |─ docs (sources for this documentation)
 |  |  |─ code (code examples in sub-folders for each experiment)
 |  |  |─ rpi-dma (C code functions for fast ADC readout)
 |  |  |─ hardware (documentation: schematics, datasheets)
 |  |─ work (user working directory, not synchronized to GitHub)

 
.. note:: 
 User programs and measurement data should be saved in the ``work`` folder. The code examples in the ``Embedded-System-Lab/code`` folder should not be modified directly but rather copied to the ``work`` folder and modified there, as needed. In case the content of the ``code`` or any other folder were accidentally changed, the files can be restored by calling ``git checkout *`` from the command line within the respective folder.
 It s highly recommended that the user has some basic knowledge of the Python language since this script does not provide an introduction in general programming concepts.

Running Code Using VisualCode
=============================
Start VisualCode and open the folder ``Embedded-System-Lab/code`` via the menu ``File->Open Folder``. In the explorer view one can find sub-folders for each experiment and additional helper functions. Most examples are written in Python while a few examples and low level functions (DMA access for fast ADC operation) are implemented in C code. The VisualCode editor will allow comfortable code and integrates tool chains to compile, build and run Python a C code.

.. note::

  A few examples access physical memory or I/O resources from within the user space. This access needs privileged access rights to execute the code. These respective programs have to be run by calling ``sudo ./<program name>`` from a command line. Other examples which use higher level functions by including dedicated libraries access these ressources via kernel mode drivers which can be used from user space without special privileges. 



Input / Output
--------------
- Python
- C++


- LED, Button, PWM
- UART (Rpi to Rpi terminal)
