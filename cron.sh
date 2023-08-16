#!/bin/bash


SH_CONFIG="script_config"
curpath=$(dirname $(realpath $0))

if [ "$curpath" == "" ]; then
    exit 1
fi

if [ ! -f "$curpath/$SH_CONFIG" ]; then
    exit 1
fi

BOT_PATH=$curpath/start.sh
source $curpath/$SH_CONFIG

if [ -z "$SCRIPT_NAME" ]; then
    exit 1
fi

proc=$(ps -aef | grep "$SCRIPT_NAME" | grep -v "grep")
if [ "$proc" = "" ]; then
    if [ -x $BOT_PATH ]; then
        cd "$curpath"
        nohup $BOT_PATH &
    fi
fi
