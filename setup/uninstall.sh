#!/bin/bash
# Linux service setup for multi-launcher
# Emanuele Paiano nixw0rm@gmail.com

source env.sh
. env.sh
  

((echo "Removing $MULTI_LAUNCHER_PATH..." && sudo rm -Rf $MULTI_LAUNCHER_PATH || (echo "$MULTI_LAUNCHER_PATH not found. Aborting." && exit 1)) && 

(echo "Disabling multilauncher.service..." && sudo systemctl disable multilauncher || (echo "Error while disabling multilauncher.service. Aborting." && exit 1)) && 

(echo "Removing multilauncher.service..." && sudo rm -f $SYSTEMD_DIR/multilauncher.service || (echo "Error while removing multilauncher.service. Aborting." && exit 1)) && 

echo "Uninstall complete.") || 
echo "Uninstall failed!"
