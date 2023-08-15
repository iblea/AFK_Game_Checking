#!/bin/bash

venv_name=discordbot
main_script=bot.py

# install
# python3 -m venv $venv_name
# if not create 'activate' file
# python3 -m venv --without-pip $venv_name

source $venv_name/bin/activate

# echo "pip list"
# pip freeze
# pip install -r pip_freeze.txt
# $venv_name/bin/pip3 install discord

echo "venv activate"
$venv_name/bin/python $main_script

deactivate
echo "venv deactivate"
