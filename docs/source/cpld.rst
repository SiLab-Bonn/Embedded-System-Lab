===========
CPLD/FPGA Programming
===========

Environment setup
=================

The development of FPGA (or CPLD) firmware requires software tools (Xilinx ISE, integrated development environment) that are not available for a Raspberry Pi. Therefore, a remote Linux machine will be used to compile the firmware. The output of the design implementation will be a binary file that can be loaded into the CPLD using a JTAG interface. Follow these steps to setup the development environment:

1. The folder ``/home/pi/Embedded-System-Lab/code/AFE/`` has a subfolder called ``ISE`` that contains the required files and scripts for the design implementation. This folder should be copied to your work folder ``/home/pi/work``.

2. Open a terminal and go to ``/home/pi/work/ISE``. There is a script called ``connect_remote_host.sh`` that will connect to a remote Linux machine hosting the Xilinx ISE design environment. The script will also mount your local folder ``/home/pi/work/ISE`` at the Linux host file system. Run the script by typing:

  .. code-block:: bash

    ./connect_remote_host.sh

Type ``pwd`` to check if the folder is mounted correctly. The output should be  ``/home/pi/pilab<xy>-remote`` where <xy> is the number of the local Raspberry Pi. The command ``ls`` should list the folder ``ISE`` and any other content of your local work folder. Keep the terminal session open, you will need it for the design implementation.

Design implementation and CPLD programming
==========================================

The development of the digital logic can now be done on the local Raspberry Pi while the design implementation will be executed with the Xilinx ISE tool chain on the remote machine:

1. Edit the Verilog code in the ``afe.v`` file in your local work folder according to your design ideas. Save the file and call the design implementation script by typing into the terminal (the one with the ssh session to the remote Linux machine):
 
  .. code-block::
  
    ./implement_design.sh

  The script will execute a sequence of tasks following the CPLD design flow: 

  * Design synthesis
  * Translation
  * Fitting (place and route)
  * Programming file generation 

  Examine the output messages. If all tasks are executed without errors, an output file ``afe.xsvf`` will be generated in the folder ``/home/pi/work/ISE``. This file will be used in the next step to program the CPLD.

2. Now you can use the JTAG programming tool ``jtag_programmer`` to program the CPLD (you will need a special cable to connect the CPLD's JTAG interface to the GPIO port of the Raspberry Pi). The programming tool is located in the folder ``/home/pi/Embedded-System-Lab/code/AFE/jtag_programmer``. To execute the tool on the local Raspberry Pi, open a new terminal and type:

  .. code-block::
  
    sudo -E /home/pi/Embedded-System-Lab/code/AFE/CPLD/jtag_programmer/jtag_programmer /home/pi/work/ISE/afe.xsvf

  If you see ``SUCCESS - Completed XSVF execution.`` at the end of the messages the CPLD has been programmed successfully.



