#!/bin/bash
# Linux depenendencies setup for multi-launcher
# Emanuele Paiano nixw0rm@gmail.com

source env.sh
. env.sh

echo "Building custom environment for python applications..." &&

(echo -n "Checking for $PYTHON..." && which $PYTHON || (echo "$PYTHON not found. Aborting." && exit 1)) &&

($PYTHON -m venv $VENV_NAME && echo "Python environment $VENV_NAME created!" || (echo "Error while creating environment $VENV_NAME. Aborting." && exit 1)) &&

(source $VENV_NAME/bin/activate && echo "$VENV_NAME activated!" || (echo "Error while activating environment $VENV_NAME. Aborting." && exit 1)) &&

(echo -n "Checking for $PIP..." && which $PIP || (echo "$PIP not found. Aborting." && exit 1)) &&

($PIP install -r python_requirements.txt || (echo "Error while installing dependencies into environment $VENV_NAME. Aborting." && exit 1)) 

