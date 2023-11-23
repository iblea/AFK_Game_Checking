import json
from os.path import isfile
from sys import exit

config:dict = None
config_file:str = "config.json"

tg_bot = None

def get_config() -> bool:
    global config
    global config_file
    if isfile(config_file) is False:
        print("config file is not exist")
        return False

    with open(config_file, "r") as f:
        config = json.load(f)

    return True

if get_config() is not True:
    print("Config Error")
    exit(1)


import telegram
import asyncio

tg_bot = telegram.Bot(token=config["telegram"]["bot_token"])
if tg_bot is None:
    print("Telegram Bot Error")
    exit(1)

tg_chatid = config["telegram"]["chat_id"]
print("Use Telegram!, Setting Success")


async def telegram_msg_send(msg_str, cnt = 1):
    global tg_bot
    for i in range(cnt):
        await tg_bot.sendMessage(chat_id=tg_chatid, text=msg_str)
        # await asyncio.sleep(0.5)

    print("Message Send Success")

loop = asyncio.new_event_loop()

loop.run_until_complete(telegram_msg_send("message test", 1))
loop.close()