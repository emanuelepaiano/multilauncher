#!/bin/bash
# Linux service setup for multi-launcher
# Emanuele Paiano nixw0rm@gmail.com

source env.sh
. env.sh
  

((echo "Removing $VENV_NAME..." && sudo rm -Rf $VENV_NAME || (echo "$VENV_NAME not found. Aborting." && exit 1)) && 
echo "Clean complete.") || 
echo "Clean failed!"
