NOTE:  See the readme.txt file for an overview of the XAPP058 reference code.

---------------------------------------------------
XAPP058 PORTS.C FILE, WAITTIME FUNCTION CALIBRATION
---------------------------------------------------

This readme_ports_c_waittime_calibration.txt provides instructions for 
calibrating the implementation of PORTS.C waitTime function from the 
XAPP058 code in your embedded system.

An implementation of the PORTS.C waitTime function is critical 
to successful operation of the XSVF player.  The waitTime function is
called for critical timing events during device programming.  The waitTime
function is passed a "microsec" parameter and the requirements of the
waitTime function include the following:

Always required:
    - Must consume (wait) for at least "microsec" microseconds.
      (Waiting for longer then "microsec" microseconds is okay.)

Additional requirement for XC18V00 or XCFxxS PROM programming:
    - At the beginning of the wait period, must do one of the following:
        - Drive TCK Low.
        - Apply one or more TCK pulses.

Additional requirement for FPGA configuration or indirect flash programming:
    - Must apply at least "microsec" (interpreting "microsec" as an integer
      number) TCK pulses.
      (Applying more than "microsec" TCK pulses is okay.)

RECOMMEND:  Meet all of the above requirements in your implementation for
maximum device compatibility.

The waittime_calibration directory contains timing calibration routines for
the waitTime function in the PORTS.C file of the XAPP058 XSVF player src code.
Use these timer calibration routines to calibrate the timer in
your system implementation of the XAPP058 XSVF player.
Calibration routines are provided for various wait times.  A few calibration
routines represent important wait times for PROM programming. 

RECOMMEND: 
- Run a few of the wait time calibration routines to ensure good
  calibration for a variety of different wait times.
- Run the longest wait time calibration routine to check for overflow
  of the variables used in the implementation.  For example, make sure
  the 140 second wait time does not cause a computation overflow that
  results in an actual 10 second wait time.


THE FILES IN THE WAITTIME_CALIBRATION DIRECTORY:
    timer_test_1ms.xsvf     = XSVF for 1 millisecond timer test
    timer_test_10ms.xsvf    = XSVF for 10 millisecond timer test
    timer_test_100ms.xsvf   = XSVF for 100 millisecond timer test
    timer_test_1s.xsvf      = XSVF for 1 second timer test
    timer_test_10s.xsvf     = XSVF for 10 second timer test
    timer_test_100s.xsvf    = XSVF for 100 second timer test

    timer_test_14ms.xsvf    = 14 ms is a XC18V00/XCFxxS program time
    timer_test_15s.xsvf     = 15 s is the XC18V00/XCFxxS erase time
    timer_test_140s.xsvf    = 140 s is the XCFxxP erase time
                              Also, the max wait time for any device
                              as of 11/26/2008.

    In addition, the following file types are provided in association with
    the above XSVF file calibration routines:
    timer_test_<time>.png   = Sample scope capture for timer test
    timer_test_<time>.svf   = SVF reference. Source for XSVF.
    timer_test_<time>.txt   = Text version of XSVF.


CALIBRATION TEST SETUP:
- Prepare your embedded system to execute one of the included 
  timer_test_*.xsvf files.
- Attach a scope probe to the JTAG TMS signal in the target JTAG chain.
- [Optional] Attach a scopr probe to the JTAG TCK signal.
- Set the scope to trigger on the falling edge of TMS.
- Set the scope to capture a time span that can accommodate the timer test time.
  For example, the scope should capture ~20 seconds of time when running the
  15 second test, or the scope should capture ~20 milliseconds of time when
  running the 14 millisecond test.
- Execute the timer_test_*.xsvf file in your system and capture the results
  on the scope.
- From the scope capture, verify that your embedded system waits for at least
  the specified wait time defined by the timer_test_*.xsvf file.

NOTE:
- Execution through a debugger can slow the processor execution.  Be sure that
  the execution of the timer test is performed at the real system speed in
  order to capture accurate timing information.


WHAT DOES THE TIMER TEST DO?
    The timer test does four things:
    1.  Apply a JTAG reset sequence:  TMS==1 for at least 5 TCK cycles.
        Result = TMS is High.
    2.  Transition the JTAG chain to Shift-Data mode and Shift 1 bit.
        Result = TMS quickly toggles a few times.
    3.  Return to the JTAG Run-Test/Idle mode and wait for a specified time.
        Result = TMS stays Low for the specified time.
    4.  Apply a JTAG reset sequence:  TMS==1 for at least 5 TCK cycles.
        Result = TMS returns High.


HOW TO ANALYZE THE SCOPESHOT OF TMS?
    The timer test described above results in a scopeshot that should have
    the following waveform that corresponds to the sequence described above:
    1.  TMS starts High.
    2.  TMS transitions to a Low.  (Quick toggling of TMS actually occurs
        but is probably not viewable at the time scale of the scope for
        test. To the viewer, the scope shows probably what looks like
        only a High-to-Low transition.)
    3.  TMS stays Low for a specified time.
    4.  TMS returns High.
    Step 3 of the sequence is the most important.  The TMS Low time in
    step 3 corresponds to the actual wait time performed by XSVF player's
    waitTime implementation.
    See the timer_test_*.png files for sample scopeshots of expected waveforms.


CALIBRATING THE WAITTIME TIMER:
    Based on the scope-shot results, the following adjustment for your
    implementation of the waitTime function in the PORTS.C file can be:

    1.  If the scopeshot of TMS shows a TMS Low time that is less than
        the specified time in the timer_test_*.xsvf file, then you must
        change the waitTime function implementation to increase the time
        that it waits.  For the typical implementation of the waitTime
        function that pulses TCK, increase the multiplier in the function
        implementation to increase the number of TCK pulses applied in order
        to increase the time consumed by the waitTime function.
        Why?  Waiting for less than specified time can result in incomplete
        internal device operations during XSVF execution.

    2.  If the scopeshot of TMS shows a TMS Low time that is greater than
        the specified time in the timer_test_*.xsvf file, then NO change
        is required.  However, you can change the waitTime implementation
        to wait for less time in order to improve overall performance.
        Why?  The specified time is a minimum time to wait.  Waiting for
        longer than specified does not harm the device.  Waiting for longer
        than specified only makes the overall XSVF operation take longer
        than required.


ADDITIONAL CHECKS:
    - TCK must either be Low during the TMS wait period or TCK must toggle
      at least one time at the beginning of the TMS wait period.  TCK can
      continuously toggle during the TMS wait period.
      See the comments near the waitTime function in the PORTS.C file
      for detailed requirements of the waitTime implementation.  Make
      sure the requirements are met.
      The readme_xc18v00_xcf00s.txt file provides additional details
      specific to the XC18V00 or XCFxxS PROM requirements.



