============================
Software Environment
============================

The Raspberry Pi module runs a Debian-based operating system (32-bit Raspberry Pi OS) with a graphical user interface. For the experiments mainly these programs will be used:

- "Terminal" command line interface
- "Visual Code" integrated development environment for C and Python
- "Chromium" web browser to browse this documentation and other information

There are other editors / development environments available in the Raspberry Pi OS distribution which could also be used instead of "Visual Code" (for example "Geany", "Thonny" etc.).

Folder Structure
================

The code examples and additional documentation is maintained on  `GitHub <https://github.com/silab-bonn/Embedded-System-Lab>`_. The project structure on the Raspberry Pi file system is organized like this::

 |__home
 |  |__ Embedded-System-Lab (GitHub root directory)
 |  |  |__ code (code examples in sub-folders for each experiment)
 |  |  |__ docs (sources for this documentation)
 |  |  |__ hardware (documentation: schematics, datasheets)
 |  |__ work (user working directory, not synchronized to GitHub)

 
.. note:: 
 User programs and measurement data should be saved in the ``work`` folder. The code examples found in the ``Embedded-System-Lab/code`` folder should not be modified but rather copied to the ``work`` folder and modified there, as needed. In case the content of the ``code`` or any other git folder were accidentally changed, the files can be restored by calling ``git checkout --force origin/master`` from the command line within the respective folder.
 
 It is recommended that the user has some basic knowledge of Python (and a bit of C) language since this script does not provide an introduction to the programming languages. Online training with interactive tutorials can be found for example here:

 - Python: https://www.w3schools.com/python/default.asp
 - C: https://www.w3schools.com/c/index.php


Using Visual Code
=================
Start Visual Code and open the folder ``Embedded-System-Lab/code`` via the menu ``File->Open Folder``. In the explorer view one can find sub-folders for each experiment and additional helper functions. Most examples are written in Python while a few examples and low level functions (DMA access for fast ADC operation) are implemented in C. The Visual Code editor will allow comfortable code editing and integrates tool chains to run Python and C code. When you switch between Python and C sources you have to **select the appropriate start and debug configuration** for the given language: Click on the bottom status bar and select

 - "C (Linux): Current file" for compiling and running C code
 - "Python: Current File" for running Python scripts

Here are simple code examples to test the installation and explain the basic methods of the Visual Code IDE.

Python Example
--------------
Open the VisualCode Explorer panel and browse the ``code`` sub folder. Select the file Python script ``hello_world.py`` and copy it to your ``work`` folder and open it in the editor window. To run the script, click the menu ``Run->Run without Debugging`` or press ``Ctrl+F5``. This will invoke the Python interpreter and run the script. The output will be displayed in the Terminal panel at the bottom of the window. If the Terminal panel is not visible, open it via the menu ``View->Terminal``.

C Example
---------
Similar to the previous example, now select the C-file ``hello_world.c`` from the ``code`` folder, copy it to your ``work`` folder and open it in the editor window. To compile and run the code click the menu ``Run->Run without Debugging`` or press ``Ctrl+F5``. This will invoke the C compiler which will build the code and start the executable. The output will be displayed in the Terminal panel at the bottom of the window. You can also just build the binary file without running it by pressing ``Ctrl+Shift+b`` and start the executable from a command line in a terminal.

A powerful tool to test your code and to solve issues is a debugger. By running your code in debug mode (pressing ``F5`` instead of ``Ctrl+F5``) you can define breakpoints by clicking on the column on the left-hand side of the line numbers. A red dot will appear which will halt the code execution at this point to allow the inspection of variables. From a breakpoint you can resume the code execution with ``F5`` or execute step-wise by pressing ``F10`` (or ``F11`` which will step further down into the definition of called functions). See Visual Code documentation on the web for more details.

.. note::

  A few examples like the C-example for low-level GPIO access (see :ref:`gpio-tutorial`) and the library for the fast ADC need access to protected physical memory or I/O resources from within the user space. This access requires privileged permissions (i.e. ``root`` access) to execute the code. To run these programs one has to call ``sudo -E ./<program name>`` from a command line because starting from within the Visual Code IDE would not provides root access. Other examples which use higher level functions by including dedicated libraries, implement this access via kernel mode drivers which can be used from user space without special privileges. 
