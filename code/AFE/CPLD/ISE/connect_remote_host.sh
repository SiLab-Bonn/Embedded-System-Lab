#!/bin/bash

#set -x

remote_username="pi"

# Extract the local host name and set remote server name
local_hostname=$(hostname)
remote_hostname="asiclab001"

# open ssh connection, create a directory on the remote host if not already present, mount remote folder and keep connection open afterwards
ssh -t $remote_username@$remote_hostname.physik.uni-bonn.de \
"[ ! -d $local_hostname-remote ] && mkdir $local_hostname-remote; " \
"sshfs pi@$local_hostname.physik.uni-bonn.de:/home/pi/work $local_hostname-remote; "\
"cd $local_hostname-remote; "\
"bash -l"

# intercative ssh connection now open



