#!/bin/bash


BOT_PATH=/path/to/start.sh

botdir=$(dirname $BOT_PATH)
proc=$(ps -aef | grep "bot.py" | grep -v "grep")
if [ "$proc" = "" ]; then
    if [ -f $BOT_PATH ]; then
        cd "$botdir"
        nohup $BOT_PATH &
    fi
fi
