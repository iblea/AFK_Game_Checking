#!/bin/bash


BOT_PATH=/path/to/start.sh

proc=$(ps -aef | grep "bot.py" | grep -v "grep")
if [ "$proc" = "" ]; then
    nohup $BOT_PATH &
fi
