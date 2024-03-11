NOTE:  See the readme.txt file for an overview of the XAPP058 reference code.

                -------------------------------------------
                Xilinx XC18V00/XCF00S ISP PROM Requirements
                -------------------------------------------
                                08/06/2003

NEWS:

    SVF2XSVF v5.02 backward-compatible with XSVF player v4.xx or v5.00.
    (See below to determine whether your pre-v5.01 XSVF meets the special
    requirements.)


OVERVIEW:

    In 2003, Xilinx announced a change in the source of the Xilinx ISP PROMs.
    The new source was ST Microelectronics.  (The previous source was UMC.)
    The first two PROMs from ST Microelectronics was an XC18V00-compatible
    PROM and a new Platform Flash PROM (XCF00S).

    The flash technology and JTAG programming logic in these ST Microelectronic
    PROMs introduce new JTAG programming algorithm requirements.  Both PROM
    designs share the same flash technology and same JTAG programming logic
    design.  As a result, both the The STMicro XC18V00 and XCF00S PROMs
    also share the same requirements for JTAG in-system programming (ISP).

    This file provides descriptions of the new JTAG programming algorithm
    requirements and instructions for programming the STMicro PROMs via
    the XAPP058 (XSVF) solution.

    NOTE:   The special JTAG ISP requirement does not apply to the XCF00P
            Platform Flash PROMs that uses a different JTAG programming engine.

References:

    Product Change Notice:
        http://www.xilinx.com/bvdocs/notifications/pcn2003-04.pdf

    XC18V00 Algorithm Change Notice:
        http://www.xilinx.com/bvdocs/notifications/acn2003-01.pdf

    XC18V00 Data Sheet:
        http://www.xilinx.com/bvdocs/publications/ds026.pdf

    Platform Flash PROM (XCF00S) Data Sheet:
        http://www.xilinx.com/bvdocs/publications/ds123.pdf

    Solution Record for XC18V00 Cross-Ship Flow and SVF Update Tips:
        Go to http://support.xilinx.com
        and search the Answer Database for "16741".


Quick Requirements Overview:

    Minimum Version Summary:
    +===============+=========================================================+
    | Tool          | Minimum Version                                         |
    +===============+=========================================================+
    | iMPACT        | 5.2.03i                                                 |
    +---------------+---------------------------------------------------------+
    | SVF2XSVF      | 5.02                                                    |
    +---------------+---------------------------------------------------------+
    | XSVF Player   | 5.01 recommended (but not required).                    |
    |               | See following sections for special requirements.        |
    +---------------+---------------------------------------------------------+


XSVF Solution (Brief):

    - Implement the XSVF player as directed in readme.txt.
        See sections below for special requirements.
    - SVF-XSVF flow:
        1.  Generate SVF using iMPACT 5.2.03i or later
        2.  Translate the SVF to XSVF:
            svf2xsvf502 -r 0 -i myfile.svf -o myfile.xsvf
            where
            -r 0 = Zero retries.  (Retries applicable to only XC9500 series.)
            -i myfile.svf  = input SVF file
            -o myfile.xsvf = output XSVF file
        3.  Execute XSVF using an XSVF player.


Background:  UMC XC18V00 and STMicro XC18V00/XCF00S Erase/Program Operations:

    UMC XC18V00 Sequence:
        1. Go to TAP Shift-IR state and shift-in the erase/program instruction
        2. Go to the TAP Run-Test/Idle state
       *3. Start erase/program operation immediately upon entering the TAP
           Run-Test/Idle state via rising [Low-to-High] transition on TCK.
        4. Wait within TAP Run-Test/Idle for maximum erase/program time
        5. Exit TAP Run-Test/Idle ends the erase/program operation, if not
           already completed

    STMicro XC18V00/XCF00S Sequence:
        1. Go to TAP Shift-IR state and shift-in the erase/program instruction
        2. Go to the TAP Run-Test/Idle state
       *3. Start erase/program operation after falling TCK edge within
           the TAP Run-Test/Idle state, i.e. a falling (High-to-Low) TCK
           transition is required to start the operation after the rising
           (Low-to-High) TCK transition that causes the TAP to enter
           the Run-Test/Idle state.
        4. Wait within TAP Run-Test/Idle for maximum erase/program time
        5. Exit TAP Run-Test/Idle ends the erase/program operation, if not
           already completed

Background:  Difference Between UMC and STMicro XC18V00/XCF00S Sequence:

    Step 3 in the sequence shows a difference between the exact event that
    starts the erase/program operation within the TAP Run-Test/Idle state:
        UMC XC18V00:
            Starts to erase/program immediately upon entering the TAP
            Run-Test/Idle state via rising [Low-to-High] transition on TCK.
        STMicro XC18V00/XCF00S:
            Starts to erase/program only after a falling (High-to-Low)
            TCK transition after the Low-to-High TCK transition that
            causes the TAP to enter the Run-Test/Idle state.


Special ST Micro XC18V00/XCF00S PROM Requirement:

    The difference (shown above) indicates the special requirement for
    the ST Micro XC18V00/XCF00S PROM.  The requirement is that the
    XSVF player must exhibit a High-to-Low transition within the TAP
    Run-Test/Idle state (Step 3) to initiate an erase/program operation.
    The transition must occur prior to the wait period (Step 4) for
    the erase/program operation.


Satisfying the Sequence Requirements for UMC and STMicro XC18V00/XCF00S:

    An implementation of the JTAG sequence that exhibits at least one
    High-to-Low TCK transition within the Run-Test/Idle state before
    Step 4 (wait for the maximum erase/program time) satisfies the
    requirements of both the UMC and STMicro XC18V00/XCF00S devices.

    The TAP enters the Run-Test/Idle on a rising (Low-to-High) TCK edge.
    The TCK must additionally exhibit at least one falling edge immediately
    after entering Run-Test/Idle to start the STMicro erase/program operation.

    See the timing diagrams below for examples of TCK implementations that
    succeed or fail to meet the sequence requirements for the UMC and STMicro
    XC18V00/XCF00S devices.


Figure 1 - Timing Diagrams

                         | Operations executed within Run-Test  |
                         |                                      |
                ________ |______________________________________| ____________
TAP STATE       Update  \/ Run-Test/Idle (Erasing/Programming)  \/ Select-DR
                ________/\______________________________________/\____________
                         |Enter RTI on rising TCK edge          |
                         |                                      |
TCK Type 1:     __       |____         ____           ____      | ____
Continuous        \      /    \       /    \         /    \     |/    \
TCK Pulses         \____/|     \_____/      \__...__/      \____/      \______
====OKAY====             |     ^Start...Erasing/Programming..End^
                         |                                      |
TCK Type 2:              |____                                  | ____
Low-High-Low             /    \ ...wait with static TCK...      |/    \
TCK Pulse       ________/|     \________________________________/      \______
====OKAY====             |     ^Start...Erasing/Programming..End^
                         |                                      |
TCK Type 3:     __       |________________________________      | ____________
High-Low-High     \      /      ...wait with static TCK...\     |/
TCK Pulse          \____/|                                 \____/
==NOT-GOOD==             |Waiting for falling edge to Start^.End^--Too short!!
                         |                                  ^^^^
                         |                                  NOT enough time
                                                            for operation
                                                            to complete.

How To Know Which Type of TCK Implementation You Have?

    Check the TCK activity with a scope...
    or
    Look at the XAPP058 XSVF player C code...

    Step A - Check for TCK Type 1 (Continuous TCK)
        Look at PORTS.C waitTime() function to see if a continuous TCK
        clock is implemented.  (XC18V00/XCF00S erase/program wait times are
        15000000us/14000us.)
        If waitTime() function is implemented as a continuous TCK, then
        the implementation satisfies the UMC and STMicro XC18V00/XCF00S
        requirements.
            Example continuous TCK implementation in PORTS.C, waitTime() function:
                waitTime( time )
                {
                    for ( int i = 0; i < time; i++ )
                    {
                        pulseClock();   // repeatedly pulse TCK
                    }
                }
        If waitTime() function is implemented as a simple wait that does
        nothing, i.e. that holds TCK at a static level, then go to Step B
        to determine the static TCK level and TCK type.
            Example static implementations of waitTime in PORTS.C:
                // Example 1
                waitTime( time )
                {
                    for ( int i = 0; i < time; i++ )
                    {
                        // Empty loop...do nothing while waiting
                    }
                }
                // Example 2
                waitTime( time )
                {
                    sleep( time );  // call simple sleep that does nothing
                }
    Step B - Check How MICRO.C Handles TCK
        Look at the MICRO.C code to see how it handles the TCK.
        See the #define XSVF_VERSION in MICRO.C to determine the version.
        Old versions (prior to 4.x or unspecified version) of MICRO.C
        may call the pulseClock function in the PORTS.C file.  If
        MICRO.C calls pulseClock in PORTS.C, then go to Step C.
        For recent versions (4.x or later) of MICRO.C, look at the
        xsvfTmsTransition function in MICRO.C.  (xsvfTmsTransition is used to
        set the new TMS value for transitioning to a new TAP state such
        as transitioning to the Run-Test/Idle state.)
        If the xsvfTmsTransition function calls pulseClock in PORTS.C,
        then go to Step C.  Example xsvfTmsTransition that calls pulseClock:
            xsvfTmsTransition( newTmsValue )
            {
                setPort( TMS, newTmsValue );
                pulseClock();   // Go to STEP C to determine TCK type
            }
        If the xsvfTmsTransition function implements a TCK Type 3
        (High-Low-High), then there may be a problem.
        Example xsvfTmsTransition function with TCK Type 3 (High-Low-High):
            xsvfTmsTransition( newTmsValue )
            {
                setPort( TMS, newTmsValue );
                // Assumes previous TCK == High
                setPort( TCK, 0 );
                setPort( TCK, 1 );  // Low->High transition changes TAP state
                                    // Last TCK level == High.
                // PROBLEM...May not satisfy STMicro XC18V00/XCF00S sequence
                //           requirement!!!
                //           If PORTS.C waitTime function sets TCK Low,
                //           then the STMicro requirement is satisfied.
                //           If PORTS.C waitTime function does nothing to TCK
                //           then the STMicro requirement is NOT satisfied!!!
            }
    Step C - Check the TCK type in the pulseClock function in the PORTS.C file
        Look at the pulseClock function in PORTS.C.
        TCK Type 2 (Low-High-Low) pulseClock function, example implementation:
            pulseClock()
            {
                // TCK Type 2 - Low-High-Low TCK pulse
                setPort( TCK, 0 );  // Low
                setPort( TCK, 1 );  // High
                setPort( TCK, 0 );  // Low...last TCK transition is High->Low
                // GOOD--Satisfies UMC and STMicro XC18V00/XCF00S
            }
        TCK Type 3 (High-Low-High) pulseClock function, example implementation:
            pulseClock()
            {
                // TCK Type 3 - High-Low-High TCK pulse
                // Assumes previous TCK value was High
                setPort( TCK, 0 );  // Low
                setPort( TCK, 1 );  // High...last TCK transition is Low->High
                // PROBLEM...May not satisfy STMicro XC18V00/XCF00S sequence
                //           requirement!!!
                //           If PORTS.C waitTime function sets TCK Low,
                //           then the STMicro requirement is satisfied.
                //           If PORTS.C waitTime function does nothing to TCK
                //           then the STMicro requirement is NOT satisfied!!!
            }

How To Fix a TCK Type 3 (High-Low-High) Problem:
    XSVF Player Workaround (ONLY for v5.xx XSVF Players):
        For a v5.xx XSVF player implementation that does not meet
        the Special ST Micro XC18V00/XCF00S PROM Requirement:
        Use the -xwait option when translating the iMPACT 5.2.03i SVF
        to XSVF.  For example:
            svf2xsvf502 -r 0 -xwait -i myfile.svf -o myfile.xsvf
            where
            -r 0 = Zero retries.  (Retries applicable to only XC9500 series.)
            -xwait = use the XSVF XWAIT command.
            -i myfile.svf  = input SVF file
            -o myfile.xsvf = output XSVF file

    Generic Fix (All XSVF Player Versions):
        The fix is to set the TCK to a Low value in the PORTS.C waitTime
        function prior to the wait period.  This will ensure the High->Low
        TCK transition requirement of the STMicro XC18V00/XCF00S.
            Example waitTime function fix in PORTS.C:
                waitTime( time )
                {
                    setPort( TCK, 0 );  // ***FIX:  Make sure TCK High->Low
                                        //          transition occurs within
                                        //          TAP Run-Test/Idle prior
                                        //          to the wait period.
                    // Wait for requested period
                    for ( int i = 0; i < time; i++ )
                    {
                        // Empty loop...do nothing while waiting
                    }
                }

    Alternate Generic Fix (All XSVF Player Versions):
        The alternate fix is to pulse the TCK at least once in the PORTS.C
        waitTime function prior to the wait period.  This will ensure the
        High->Low TCK transition requirement of the STMicro XC18V00/XCF00S.
            Example waitTime function alternate fix in PORTS.C:
                waitTime( time )
                {
                    pulseClock();   // ***FIX:  A full TCK clock period
                                    //          ensures a TCK High->Low
                                    //          transition occurs within
                                    //          TAP Run-Test/Idle prior
                                    //          to the wait period.
                    // Wait for requested period
                    for ( int i = 0; i < time; i++ )
                    {
                        // Empty loop...do nothing while waiting
                    }
                }



