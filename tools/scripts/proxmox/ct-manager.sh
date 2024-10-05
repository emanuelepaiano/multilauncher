#!/bin/bash
# This script permits to start, stop, shutdown and reset virtual machine on Proxmox node
# (C) 2024 - Emanuele Paiano - https://github.com/emanuelepaiano

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

. $SCRIPT_DIR/config

startVm() {
  url=${START_CT_API/VMID/$VMID}
  url=${url/NODE/$NODE}
  COMMAND="$COMMAND $url"
  (echo -n "Starting CT $VMID on node $NODE.." &&
  echo "" &&
  eval "$COMMAND" &&
  echo ""
  echo "DONE") || (echo "ERROR" && exit 1)
}

stopVm() {
  url=${STOP_CT_API/VMID/$VMID}
  url=${url/NODE/$NODE}
  COMMAND="$COMMAND $url"
  (echo -n "Stopping CT $VMID on node $NODE.." &&
  echo "" &&
  eval "$COMMAND" &&
  echo ""
  echo "DONE") || (echo "ERROR" && exit 1)
}

shutdownVm() {
  url=${SHUTDOWN_CT_API/VMID/$VMID}
  url=${url/NODE/$NODE}
  COMMAND="$COMMAND $url"
  (echo -n "Shutdown CT $VMID on node $NODE.." &&
  echo "" &&
  eval "$COMMAND" &&
  echo ""
  echo "DONE") || (echo "ERROR" && exit 1)
}

resetVm() {
  url=${REBOOT_CT_API/VMID/$VMID}
  url=${url/NODE/$NODE}
  COMMAND="$COMMAND $url"
  (echo -n "Forcing reboot CT $VMID on NODE $NODE.." &&
  echo "" &&
  eval "$COMMAND" &&
  echo ""
  echo "DONE") || (echo "ERROR" && exit 1)
}

use() {
  echo "Use $0 <NODE> <VM_ID> <START|STOP|SHUTDOWN|RESET>"
}


# starting script.

# checking parameters number
if [ $# -ne 3 ]; then
  use
  exit 1
fi

COMMAND="$CURL_PATH -X POST -s "

if [ "$VERIFY_SSL" == false ]
then
    COMMAND="$COMMAND -k "
fi

COMMAND="$COMMAND -H 'Authorization: PVEAPIToken=USER!TOKEN_ID=TOKEN_SECRET'"

COMMAND=${COMMAND/USER/$USER}
COMMAND=${COMMAND/TOKEN_ID/$TOKEN_ID}
COMMAND=${COMMAND/TOKEN_SECRET/$TOKEN_SECRET}

NODE=$1
VMID=-1


if [ -n "$2" ] && [[ "$2" =~ ^-?[0-9]+$ ]]; then
  VMID=$2
else
  echo "ERROR: $2 is not valid as VM ID. I expect an integer value."
  echo ""
  use
  exit 1
fi

action=$(echo "$3" | tr '[:upper:]' '[:lower:]')
case $action in
  "start")
    startVm
    ;;
  "stop")
    stopVm
    ;;
  "reset")
    resetVm
    ;;
  "shutdown")
    shutdownVm
    ;;
  *)
  echo "Invalid action $action"
  use
  exit 1
  ;;
esac

exit 0
