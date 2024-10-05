#!/bin/bash
# Linux service setup for multi-launcher
# Emanuele Paiano nixw0rm@gmail.com

source env.sh
. env.sh
  
CURRENT_PATH=$(dirname "$0")


(which systemctl && echo "Systemctl found!" || (echo "Systemctl not found. Aborting." && exit 1)) && 

(sudo cat<<__EOF__  >$SYSTEMD_DIR/multilauncher.service || (echo "cannot write to $SYSTEMD_DIR/multi-launcher.service (do you have write permission?). Aborting." && exit 1)) &&

[Unit]
Description = Multi launcher for starting service from remote
After = network.target
 
[Service]
Type = simple
ExecStart = $MULTI_LAUNCHER_PATH/multilauncher
User = $USER 
Group = $GROUP
Restart = on-failure
SyslogIdentifier = multilauncher
RestartSec = 5
TimeoutStartSec = infinity
 
[Install]
WantedBy = multi-user.target

__EOF__

(sudo chmod +x $SYSTEMD_DIR/multilauncher.service || exit 1) &&

(sudo mkdir $MULTI_LAUNCHER_PATH || (echo "cannot create folder $MULTI_LAUNCHER_PATH. Aborting." && exit 1)) &&

(sudo cp -R $CURRENT_PATH/../* $MULTI_LAUNCHER_PATH/ || (echo "cannot copy files to $MULTI_LAUNCHER_PATH/. Aborting." && exit 1)) &&

(sudo systemctl enable multilauncher &&

sudo systemctl daemon-reload &&

sudo systemctl start multilauncher &&

echo "Installation complete.") || 
echo "Installation failed!"
