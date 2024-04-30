#!/bin/bash

# Run the TCL script using Xilinx tcl shell 
# complete design implementation 
#  - synthesis
#  - translate
#  - fit (place and route)
#  - programming file generation (.jed file)
xtclsh afe.tcl run_process

# generate the XSFV file from the jed file  
impact -batch gen_xsvf.cmd