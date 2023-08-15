#!/bin/bash


BOT_PATH=/path/to/start.sh
SCRIPT_NAME="bot.py"

botdir=$(dirname $BOT_PATH)
proc=$(ps -aef | grep "$SCRIPT_NAME" | grep -v "grep")
if [ "$proc" = "" ]; then
    if [ -x $BOT_PATH ]; then
        cd "$botdir"
        nohup $BOT_PATH &
    fi
fi
