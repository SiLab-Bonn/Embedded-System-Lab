#!/bin/bash

remote_username="krueger"

# Extract the local host name
local_hostname=$(hostname)
remote_hostname="asiclab001"

# open ssh connection and create a directory on the remote host if not already present, mount remote folder and keep connection open afterwards
ssh -t $remote_username@$remote_hostname.physik.uni-bonn.de \
"[ ! -d $local_hostname-remote ] && mkdir  $local_hostname-remote " \
"sshfs pi@$local_hostname.physik.uni-bonn.de:/home/pi/work $local_hostname-remote; bash -l"

# intercative ssh connection 

# clean up sshfs mount
fusermount -u $local_hostname-remote
rmdir $local_hostname-remote

