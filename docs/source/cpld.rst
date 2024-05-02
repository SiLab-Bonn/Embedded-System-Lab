===========
CPLD/FPGA Programming
===========

Environment setup
=================

The development of FPGA (or CPLD) firmware requires tools (Xilinx ISE) which are not available for a Raspeberry Pi. Therefore, a remote Linux machine will be used to compile the firmware. The ouput of the design implementation will be a binary file that can be loaded into the CPLD using a JTAG interface. Follow these steps to setup the environment:

1. The folder ``/home/pi/Embedded-System-Lab/code/AFE/`` has a subfolder called ISE that contains the required files and scripts for the design implementation. This folder should be copied to your work folder ``/home/pi/work``.

2. Open a terminal and go to ``/home/pi/work/ISE``. There is a script called ``connect_remote_host.sh`` that will connect to the remote Linux machine and mount your local folder ``/home/pi/work/ISE`` there. Run the script by typing:

  .. code-block:: bash

    ./connect_remote_host.sh

  Type ``pwd`` to check if the folder is mounted correctly. The output should be  ``/home/pi/pilab<xy>-remote`` where <xy> is the number of the local Rasperry Pi. The command ``ls`` should list the folder ``ISE``. Keep the terminal session open, you will nee it for the design implementation

The design of the CPLD logic can now be done on the local Raspberry Pi while the design implementation will be executed on the remote machine:

1. Edit the Verilog code ``afe.v`` in your local work folder according to your design ideas. Save the file and call the design implemetation script by typing into the terminal with the ssh connection to the remote machine:
 
  .. code-block::
  
    ./implement_design.sh

  The script will execute a sequence of tasks accoring to the CPLD design flow: 

  * Design synthesis
  * Translation
  * Fitting (place and route)
  * Proramming file generation 

  Examine the output messages. If all tasks are executed without errors, an output file ``afe.xsvf`` will be generated in the folder ``/home/pi/work/ISE``. This file will be used to program the CPLD.

2. Now you can use the JTAG programming tool ``jtag_programmer`` to program the CPLD (you will need a special cable to connect the CPLD's JTAG interface to the GPIO port of the Raspberry Pi). The programming tool is located in the folder ``/home/pi/Embedded-System-Lab/code/AFE/jtag_programmer``. To execute the tool on the local Raspberry Pi, open a new terminal and type:

  .. code-block::
  
    sudo /home/pi/Embedded-System-Lab/code/AFE/CPLD/jtag_programmer/jtag_programmer /home/pi/work/ISE/afe.xsvf

  If you see ``SUCCESS - Completed XSVF execution.`` at the end of the messages the CPLD has been programmed successfully.



