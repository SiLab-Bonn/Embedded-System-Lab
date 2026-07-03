#!/bin/bash

ssh_list=( pi@pilab01.physik.uni-bonn.de \
           pi@pilab02.physik.uni-bonn.de \
           pi@pilab03.physik.uni-bonn.de \
           pi@pilab04.physik.uni-bonn.de \
           pi@pilab05.physik.uni-bonn.de \
           pi@pilab06.physik.uni-bonn.de \
           pi@pilab08.physik.uni-bonn.de \
)

split_list=()
for ssh_entry in "${ssh_list[@]:1}"; do
    split_list+=( split-pane -h ssh "$ssh_entry" ';' select-layout tiled ';' )
done

tmux new-session -s pilab ssh "${ssh_list[0]}" ';' \
    "${split_list[@]}" \
    set-option -w synchronize-panes on
