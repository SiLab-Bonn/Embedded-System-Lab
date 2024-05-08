#!/bin/bash

# setup XILINX environment
source /tools/xilinx/14.7/ISE_DS/settings64.sh

# Run the TCL script using Xilinx tcl shell 
# complete design implementation 
#  - synthesis
#  - translate
#  - fit (place and route)
#  - programming file generation (.jed file)
xtclsh afe.tcl rebuild_project

# generate the XSFV file from the jed file  
impact -batch gen_xsvf.cmd