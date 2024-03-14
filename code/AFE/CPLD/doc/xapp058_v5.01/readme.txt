*******************************************************************************
** ©1998—2004 Xilinx, Inc. All Rights Reserved.
** Confidential and proprietary information of Xilinx, Inc. 
*******************************************************************************
**   ____  ____ 
**  /   /\/   / 
** /___/  \  /   Vendor:                Xilinx, Inc. 
** \   \   \/    Version:               v5.01 (code version)
**  \   \        Filename:              readme.txt (from xapp058.zip)
**  /   /        Date Last Modified:    02/01/2009
** /___/   /\    Date Created:          circa 1998
** \   \  /  \ 
**  \___\/\___\ 
** 
**  Device:  Xilinx CPLDs:  XC9500/XC9500XL/XC9500XV/CoolRunner/CoolRunner-II
**           Xilinx PROMs:  XC18V00/XCF00S/XCF00P
**           Xilinx FPGAs:  Virtex Families, Spartan Families, and
**                          JTAG-configurable XC4000 Families
**  Purpose:  XAPP058 describes a C code reference design for a processor
**            that can program or configure a Xilinx device via the device's 
**            JTAG port.
**  Reference:  XAPP058
** NEWS:
** 02/01/2008:
**     - No significant code changes from original v5.01 code release.
**     - Ports.C comments updated to clarify waitTime function requirements.
**     - Example Win32 .exe and project added to show how xapp058 code
**       interprets the XSVF.  THIS EXAMPLE DOES NOT INTERACT WITH XILINX CABLES.
**       USE IMPACT IF YOU WANT TO EXECUTE XSVF THROUGH A XILINX CABLE.
**     - Minor additions to Ports.C to support printing in example exe for Win32.
**     - Added Ports.C waitTime function calibration files.
**     - Stand-alone SVF-to-XSVF (SVF2XSVF) translators archived to the old
**       directory.  
**       iMPACT 8.2 or later supports direct XSVF generation. Recommend using
**       the latest ISE iMPACT version.
**     - Stand-alone players archived into zip files in the old directory.
**       Stand-alone players obsoleted due to cable and driver transitions.
**       In place of the stand-alone players, ISE iMPACT 8.2 or later contains 
**       native support for execution of XSVF to a Xilinx cable for testing XSVF.
**       Recommend using the latest ISE iMPACT version.
**     - The advanced, dynamic-targeting player code is archived to a zip file 
**       in the old directory.  This standard player code is highly recommended.
**       The dynamic player should be reserved for very special cases where the
**       user has an excellent understanding of IEEE Standard 1149.1 and where
**       the standard player code absolutely cannot meet the requirements.
**  Revision History:
**  v5.01:
**      Added setPort( TCK, 0 ); to waitTime() function in PORTS.C to ensure
**      that TCK is returned to 0 (at least once) at the beginning of
**      a Run-Test/Idle wait period for the XC18V00/XCF00S.  This addition
**      is required for implementations that do NOT toggle TCK during the
**      wait period.
**      The SVF2XSVF 5.02 translator made backward-compatible with
**      v4.xx XSVF player for the XC18V00/XCF00S devices.
**      (See readme_xc18v00_xcf00s.txt for more XC18V00/XCF00S information!!!)
**  
**  v5.00:
**      Improved SVF STATE command support.
**      Added XWAIT command for on-demand wait instead of pre-specified XRUNTEST.
**      XWAIT also required for CoolRunner/II.
**      The "extensions", that were previously only enabled via the
**      XSVF_SUPPORT_EXTENSIONS macro, is made a standard part of the XSVF player.
**  
**  v4.14:
**      Support XCOMMENT XSVF command for storing SVF comments and/or line
**      numbers in the XSVF.
**  
**  v4.11:
**      SVF2XSVF translator update only--no changes to XSVF player C code.
**      Add -multiple_runtest option for iMPACT CoolRunner SVF.
**  
**  v4.10:
**      Add new XSIR2 command that supports IR shift lengths > 255 bits.
**  
**  v4.07:
**      [Add Notes] Add notes and code examples for the waitTime function
**      in the ports.c file that satisfy the TCK pulse requirements for the
**      Virtex-II.
**  
**  v4.06:
**      [Bug Fix] Fixed xsvfGotoTapState for problem with retry transition.
**  
**  v4.05:
**      [Bug Fix] Fixed backward compatibility problem of previous "alpha"
**          and "beta" versions which did not work with some older XC9500 devices.
**          Fix required XSVF player C source code and svf2xsvf translator
**          modifications.
**      [Enhancement] Added XENDIR and XENDDR commands to support XPLA devices.
**      [Enhancement] Re-wrote micro.c (and lenval.c) due to new TAP transition
**          strategy and to cleanup old code.  (Ports.c remained the same.)
**      [Enhancement] svf2xsvf -v2 option provides excellent backward compatibility
**          for running new XSVF on old v2.00 XSVF player. Works for XC9500/XL
**          devices.  For newer devices (XC18V00 and XPLA3), assumes XSDRTDO bug
**          when XSDRSIZE==0 was fixed in old player.
**  
**  v4.00 - v4.04 "beta":
**      [New Device] Support XC18V00 and XPLA SVF without SirRunTest preprocessor.
**      [New Device] Added XSTATE command to support CoolRunner devices.
**      [Bug Fix] svf2xsvf translator fixed bug in which FPGA bitstream could
**          be corrupted (by previous translators).
**      [Enhancement] svf2xsvf translator re-written.  The single
**          svf2xsvf translator performed function of previous svf2xsvf
**          and xsvf2ascii.  That is, svf2xsvf output both the XSVF file
**          as well as the ASCII text version.
**      [Enhancement] svf2xsvf translator freed from shared library dependencies.
**      [Enhancement] svf2xsvf translator improves translation speed for large
**          FPGA SVF files by greater than 10x.
**      [Change] svf2xsvf translator no longer supported XC9500's XSVF compression
**          technique.  Use svf2xsvf v2.00 to compress XC9500 SVF files.
**  
**  eisp_1800a ("alpha"):
**      [New Device] Modified v2.00 solution to support XC18V00 and
**          CoolRunner devices.  Used existing v2.00 svf2xsvf translator
**          and supplemented with the SirRunTest preprocessor to prepare
**          XC18V00/XPLA SVF files for the XSVF format.
**      [New Device] XSIR command in XSVF player C source code modified to
**          wait for pre-specified RUNTEST time after shifting if RUNTEST time was
**          non-zero.  If RUNTEST time was zero, XSIR ended in Update-IR
**          state so that next command would skip Run-Test/Idle on way to
**          next shift state.  The wait was required for XC18V00 and XPLA
**          devices.  The skip of Run-Test/Idle was required for the XPLA
**          devices.
**      [Bug Fix] Fixed bug in XSVF player C code so that an XSDR or XSDRTDO
**          executed with a pre-specified XSDRSIZE value of zero skipped
**          any kind of TAP transition and only waited for the pre-specified
**          RUNTEST time in the Run-Test/Idle state.  The v2.00 translator
**          performed this sequence when an arbitrary wait was required.
**          But, the v2.00 XSVF player C source code errantly shifted one bit
**          even though zero bits were specified.
**      [Bug Fix] Fixed bug in which XSDRTDOC and XSDRTDOE called the function that
**          performed the XSDRTDOB operation.
**  
**  v2.00:
**      [New Device] svf2xsvf, xsvf2ascii, and XSVF player C code updated to
**          support FPGA bitstreams (i.e. chunking of long SDRs) in SVF.
**  
**  pre-v2.00:
**      [Feature] svf2xsvf translator converted SVF to binary XSVF format.
**      [Feature] xsvf2ascii debugging translator converted binary XSVF format
**          to human-readable ASCII text format.
**      [Feature] XSVF player C code supported XC9500 and XC9500XL CPLDs.
**   
*******************************************************************************
**
**  Disclaimer: 
**
**		Xilinx licenses this Design to you “AS-IS” with no warranty of any kind.  
**		Xilinx does not warrant that the functions contained in the Design will 
**		meet your requirements,that the Design will operate uninterrupted or be 
**		error-free, or that errors or bugs in the Design will be corrected.  
**		Xilinx makes no warranties or representations in regard to the results 
**		obtained from your use of the Design with respect to accuracy, reliability, 
**		or otherwise.  
**
**		XILINX MAKES NO REPRESENTATIONS OR WARRANTIES, WHETHER EXPRESS OR IMPLIED, 
**		STATUTORY OR OTHERWISE, INCLUDING, WITHOUT LIMITATION, IMPLIED WARRANTIES 
**		OF MERCHANTABILITY, NONINFRINGEMENT, OR FITNESS FOR A PARTICULAR PURPOSE. 
**		IN NO EVENT WILL XILINX BE LIABLE FOR ANY LOSS OF DATA, LOST PROFITS, OR FOR 
**		ANY SPECIAL, INCIDENTAL, CONSEQUENTIAL, OR INDIRECT DAMAGES ARISING FROM 
**		YOUR USE OF THIS DESIGN. 
*******************************************************************************

This readme describes how to use the files that come with XAPP058.

                    ------------------------------
                    XAPP058 Reference C Code v5.01
                    ------------------------------

OVERVIEW:
This zip file contains the XSVF player reference C code corresponding
to XAPP058 which you must port to your embedded processor platform.
The iMPACT software can generate XSVF that contains instructions
for programming the design data via JTAG into the selected Xilinx device.
The XSVF player executes the instructions from the XSVF file on your
embedded processor to program the target device in-system.


NOTES: 
- See readme_xc18v00_xcf00s.txt for important information about 
  implementations for XC18V00 or XCFxxS PROM programming.


SUPPORT:
Find technical support answers or contact information at:
http://www.support.xilinx.com


Files/Directories:

  README FILES:
  readme.txt - This readme.txt file.
  readme_ports_c_waittime_calibration.txt - Readme.txt for the directory of
                                            files that help you calibrate
                                            the PORTS.C waitTime function
                                            timing and implementation.
  readme_xc18v00_xcf00s.txt - Readme for special instructions for 
                              implementations supporting XC18V00 or XCFxxS
                              PROM programming.

  REFERENCE SOURCE CODE:
  src/       - This directory contains the reference C code that executes the
               XSVF file format.  See "XSVF C Code Instructions" (below)
               on how to port this code to your platform.
               This code is provided as is and without restriction.

  EXAMPLE .EXE OF XAPP058 REFERENCE SOURCE CODE:
  xapp058_example_for_win32_visualc2008/
            - This directory contains a copy of the files from the src
              directory.  A sample xapp058_example.exe is provided
              along with Visual C++ 2008 solution/project files for 
              compiling the xapp058 reference source code. 
              An example.xsvf is provided to demonstrate how the 
              xapp058 reference source code interprets the XSVF file.
              See the readme.txt within the directory for details
              regarding the xapp058_example.exe and example.xsvf.

  PORTS.C WAITTIME FUNCTION CALIBRATION FILES:
  ports_c_waittime_calibration/
            - This directory contains XSVF files that can help you
              calibrate the timing of your implementation of the 
              waitTime function in the PORTS.C file.
              Calibration XSVF files are provided along with example
              scope-shots of the expected results.
              See the readme_ports_c_waittime_calibration.txt for details.

  ARCHIVES OF OLDER/OBSOLETE FILES:
  old/       - This directory contains previous versions of the XAPP058
               source code.  This is provided so that you can diff the
               old version against the latest version to find the differences.
               This directory also contains obsolete utilities and code.
               A few of the available archives are noted below.

  old/xapp058_v5_01_svf2xsvf.zip - The old stand-alone SVF-to-XSVF translator
                                   utilities. Recommend using iMPACT directly
                                   generate XSVF instead of these translators.

  old/old_v2.00.zip - Old v2.00 svf2xsvf translator provided in case you
                      want to use the XSVF compression mechanism for XC9500
                      or XC9500XL SVF files.  (The v5.xx translator does not
                      implement this compression technique.  However, the
                      v5.xx XSVF player does support this compression
                      mechanism.)


Create XSVF Files to Program Your Device:

  XC9500/XC9500XL/XC9500XV/CoolRunner/CoolRunner-II/XC18V00/XCF00S/XCF00P/FPGA:
    - Use iMPACT 8.2.03i or later (available from the WebPACK at
      http://www.xilinx.com/ise/logic_design_prod/webpack.htm)
      Recommend using the latest software version.
    - See iMPACT Help.
    - Create the JTAG chain in the iMPACT boundary-scan window.
    - Set the iMPACT output to an XSVF file. 
    - Select one target device and invoke the Operation->Program menu item
      with appropriate options to have iMPACT generate the XSVF file content.
        - Operations for XC9500/XL, CoolRunner/II, XC18V00, XCF00S, XCF00P, 
          Spartan-3AN:
            Erase, Program, Verify
                (Operation->Program + check Erase before programming & Verify)
        - Operations for FPGA:
            Program
                (Operation->Program [no other options required])


XAPP058 XSVF Player C Code Implementation Instructions:

  Implement the functions in PORTS.C for your system:
    setPort()    - Set the JTAG signal value.
    readTDOBit() - Get the JTAG TDO signal value.
    waitTime()   - Tune to wait and apply TCK clock pulses.
                   See comments in PORTS.C near the waitTime function
                   for detailed requirements and recommended implementation.
                   (Warning:  Some compilers eliminate empty loops
                    in optimized/release mode.)
    readByte()   - Get the next byte from the XSVF source location.

  Compile all .c code and call xsvfExecute() (defined in micro.h) to
  start the execution of the XSVF.


  Optimizations:
    lenval.h:  #define MAX_LEN 7000
      This #define defines the maximum length (in bytes) of predefined
      buffers in which the XSVF player stores the current shift data.
      This length must be greater than the longest shift length (in bytes)
      in the XSVF files that will be processed.  7000 is a very conservative
      number.  The buffers are stored on the stack and if you have limited
      stack space, you may decrease the MAX_LEN value.

      RECOMMENDATION:  When you have room, leave the MAX_LEN with the
      default value. Or, when you must reduce the MAX_LEN value, do not use
      the minimum value--Use the larest value that your system allows.
      A larger value helps to accommodate support for new devices or
      for changes in the XSVF across different software versions.


      When you must reduce the MAX_LEN value, how do you find the 
      longest (maximum) "shift length" in bytes?
      See table below.
      To verify, use iMPACT to generate an SVF file (instead of XSVF file) that 
      targets your device.  SVF is a text file (versus binary XSVF).
      Search for the "SDR" commands.  The SDR command name is followed 
      by a number of bits to shift. Find the SDR with the most number of
      bits to shift.  That is your maximum "shift length" in bits.
      Convert the maximum shift length from a number of bits to bytes
      for the MAX_LEN value (because MAX_LEN is defined in bytes).

      minimum MAX_LEN = ceil( max( SDR bits to shift ) / 8 );

      NOTE: SVF for direct FPGA configuration can contain SDR statements
      with a maximum shift length equal to the bitstream size which is
      on the order of millions of bits.  When SVF is translated to XSVF,
      the long SVF shifts are optimized by cutting the long shifts into 
      short, partial shifts.  Thus, the maximum XSVF shift length can be 
      less than the maximum SVF SDR shift length.  See table below for
      XSVF maximum shift lengths.

      The following MAX_LEN values have been tested and provide relatively
      good margin for the corresponding devices:

      NOTE:  This table of values is provided as a guideline.  The maximum
      values are not guaranteed for XSVF from different software versions.  
      The XSVF is subject to change as new devices or enhancements are made 
      to the XSVF.

        DEVICE       MAX_LEN   Max Shift Length
        Type         (bytes)   (bits)
        ---------    -------   ----------------------------------------
        XC9500/XL/XV 32        256

        CoolRunner/II 256      2048   - actual max 1 device = 1035 bits

        Spartan-3AN and indirect flash programming:
                     1250      10000  - actual max 1 device = ~8600 bits

        FPGA         128       1024   - svf2xsvf -rlen 1024

        XC18V00/XCF00S
                     1100      8800   - no blank check performed (default)
                                      - actual max 1 device = 8192 bits verify
                                      - max 1 device = 4096 bits program-only

        XC18V00/XCF00S when using the optional Blank Check operation
                     2500      20000  - required for blank check
                                      - blank check max 1 device = 16384 bits

        XCF00P
                     1100      8800   - actual max 1 device = 8192 bits verify
                                      - max 1 device = 256 bits program-only

    micro.c:  #define XSVF_SUPPORT_COMPRESSION
      This #define includes support for an XSVF compression mechanism
      that was used by the previous v2.00 SVF2XSVF translator.  If you
      intend to execute older v2.00 XSVF with compress, then make sure this
      is defined.  Otherwise, the current v5.xx translator does not
      support this compression mode.  You may omit this definition
      the code size and runtime memory requirements are reduced.


Trouble-shooting:

    For XC18V00 or XCF00S failures, see readme_xc18v00_xcf00s.txt.

    The XSVF fails in the embedded implementation.
    - Use the Xilinx iMPACT software to see if it can program
      the devices on your board through a Xilinx cable.
    - Use the Xilinx iMPACT software with a Xilinx cable
      to check if iMPACT can program the devices on your board with your
      XSVF file.
    - Create an XSVF file that performs only an IDCODE check
      ("Operation->Get Device ID").  This will verify the TAP functionality
      and communication.
    - Create separate XSVF files for erase-only, blank-check-only,
      program-only, and verify-only to narrow the error region.

    Check Xilinx Solution Records at http://support.xilinx.com.


