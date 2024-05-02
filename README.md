## Embedded System Lab

See https://embedded-system-lab.readthedocs.io/en/latest/ for latest documentation.

RPi useful hints:
 - disable hardware acceleration for Chromium (Settings->Advanced->System) and Visual Code (ctrl+shift+p ">runtime")
 - sudo with current environment: sudo -E
 - install python module with current environment: python -m pip install ...
 - refresh git repository: git checkout --force origin/master
 - ssh key based authorization

    On Local server

        ssh-keygen -t rsa
    
    On remote Server

        ssh user@remote_servers_ip "mkdir -p .ssh"
    
    Uploading Generated Public Keys to the Remote Server

        cat ~/.ssh/id_rsa.pub | ssh user@remote_servers_ip "cat >> ~/.ssh/authorized_keys"
    
    Set Permissions on Remote server

        ssh user@remote_servers_ip "chmod 700 ~/.ssh; chmod 640 ~/.ssh/authorized_keys"
    
    Login

        ssh user@remote_servers_ip
    
    Enabling SSH Protocol v2

        uncomment "Protocol 2" in /etc/ssh/sshd_config

    Enabling public key authorization in sshd

        uncomment "PubkeyAuthentication yes" in /etc/ssh/sshd_config

    If StrictModes is set to yes in /etc/ssh/sshd_config then

        restorecon -Rv ~/.ssh
