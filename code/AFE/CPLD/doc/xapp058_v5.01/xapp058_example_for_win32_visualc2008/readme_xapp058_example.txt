README XAPP058 EXAMPLE FOR WIN32 Visual C++ 2008 Express
--------------------------------------------------------

EXAMPLE EXECUTABLE SIMPLY SHOWS HOW THE XAPP058 CODE INTERPRETS THE XSVF.
EXAMPLE EXECUTABLE DOES NOT INTERACT WITH XILINX CABLES.
USE XILINX ISE IMPACT SOFTWARE IF YOU WANT TO EXECUTE XSVF THROUGH
A XILINX CABLE.


This The xapp058_example_for_win32_visualc2008 directory contains 
a Visual C++ 2008 project file for compiling the xapp058 source
code into an xapp058_example.exe.  The xapp058_example.exe 
can be executed as follows:

    xapp058_example.exe -v 4 example.xsvf

The xapp058_example.exe with the -v 4 (verbose level 4) option
prints the output JTAG signal activity as the xapp058 code 
interprets the given XSVF file.  The xapp058_example.exe prints
individual JTAG output signal values (TCK, TMS, TDI) to the screen
(that would normally be driven to the actual JTAG signals in hardware).
The xapp058_example.exe also prints JTAG TAP state information
and wait timing information.

The xapp058_example.exe can interpret any XSVF file but is shown above
with the given example.xsvf.

NOTE:  The example.xsvf actually fails at a point where the XSVF 
expects a return value from the JTAG TDO signal because there is no
real JTAG TDO signal that returns the expected value. See the example.svf
comments for the example.xsvf activity. 

The xapp058_example_for_win32_visualc2008 directory contains:
  xapp058_example.exe   = Prebuilt example .exe for Win32 platforms.
  xapp058_example.sln   = Open this solution file in Visual C++ 2008 Express
                          to compile the example code.
  xapp058_example.vcproj= Visual C++ 2008 project file for the solution.
  *.c/*.h               = Same xapp058 source code as in the main src directory.

  example.xsvf          = Example XSVF file to run with the xapp058_example.exe
  example.svf           = SVF source of the binary example.xsvf
  example.txt           = ASCII version of the binary example.xsvf



