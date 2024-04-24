#! /opt/homebrew/bin/python3
#! /usr/bin/python3
import discord
from discord.ext import tasks, commands
import json
from os.path import isfile
from time import sleep

# game_scheduler
# 게임 이름은 영어일 경우 모두 소문자로, 공백 없이 적어주세요
# alert_channel

print("START PROGRAM")

gamename = "growcastle"

# discord
bot = None

# telegram
use_telegram = False
tg_bot = None
tg_chatid = -1
tg_user = {}

# 첫 번째 튕긴 시점 확인을 위한 cnt 체크
# 기기변경을 위해 1분가량 접속이 안될 수 있으므로 첫 알림은 튕긴 시점에서 1분 뒤에 울리도록 한다.

first_alert_dict = {}
first_alert_interval = 10

config:dict = None
config_file:str = "config.json"


def is_use_telegram(config):
    if 'telegram' not in config:
        return False
    if 'bot_token' not in config["telegram"]:
        return False
    if 'chat_id' not in config["telegram"]:
        return False
    if config["telegram"]["bot_token"] == "":
        return False
    if config["telegram"]["chat_id"] == 0:
        return False
    return True


def get_config() -> bool:
    global config
    global config_file
    global use_telegram
    global first_alert_interval
    if isfile(config_file) is False:
        print("config file is not exist")
        return False

    with open(config_file, "r") as f:
        config = json.load(f)

    if 'bot_token' not in config:
        print("bot_token is not exist")
        return False
    if 'bot_channel' not in config:
        print("bot_channel is not exist")
        return False

    if config['bot_token'] == "" or config['bot_token'] is None:
        print("bot_token is empty")
        return False

    if config['bot_channel'] == 0 or config['bot_channel'] is None:
        print("bot_channel is empty")
        return False

    if config["alert_repeat"] < 1:
        print("wrong alert repeat time")
        return False

    if is_use_telegram(config):
        use_telegram = True
    else:
        use_telegram = False

    if config["schedule"] < 1:
        print("wrong schedule time")
        return False

    if config["first_alert_interval"] < 1:
        print("wrong first_alert_interval time")
        return False

    try:
        schedule_int = int(config["schedule"])
        first_alert_interval_int = int(config["first_alert_interval"])
        if first_alert_interval_int % schedule_int == 0:
            first_alert_interval = first_alert_interval_int // schedule_int
        else:
            first_alert_interval = first_alert_interval_int // schedule_int

        if first_alert_interval <= 0:
            print("first alert interval 값이 schedule 보다 작을 수 없습니다.")
            return False
    except Exception:
        return False

    print(first_alert_interval)
    return True


def set_config() -> None:
    global config
    global config_file
    global bot
    try:
        with open(config_file, "w") as f:
            json.dump(config, f, indent=4)
    except:
        print("config file save error")
        return False
    return True


if get_config() is False:
    print("config load error")
    exit(1)


def msg_stat(stat:int, userid:int, username:str="") -> str:
    msg:str = ""
    condition_msg:str = ""
    if stat == -1:
        return "존재하지 않는 사용자 입니다."
    if stat == 1:
        condition_msg = "({})님은 오프라인 입니다. 일어나세요 용사여!".format(username)
        # msg = "<@{}> is offline. Wake up!!!".format(userid)
    elif stat == 2:
        condition_msg ="({})님 팅팅팅팅팅. 돌아오세요 용사여!".format(username)
        # msg = "<@{}> is not playing a game. Come back!!!".format(userid)
    elif stat == 3:
        condition_msg = "({})님 팅팅팅팅팅팅팅팅팅팅. 돌아오세요 용사여!".format(username)
        # msg = "<@{}> is playing a another game. Come back!!!".format(userid)
    else:
        return ""

    if userid != 0:
        msg = "<@{}> ".format(userid)

    msg += condition_msg
    return msg



# bot will not be able to send more than 20 messages per minute to the same group.
# telegram은 분당 20 req 이상의 요청을 보낼 수 없다.
# 또한 초당 두개 이상의 메시지를 보낼 수 없다. (이러한 burst 형식의 메시지를 보낼 시 429 오류 발생)
async def telegram_msg_send(msg_str, cnt = 1):
    global tg_bot
    global tg_chatid
    global use_telegram

    if use_telegram is False:
        return
    if tg_bot is None:
        return
    if tg_chatid < 0:
        return

    if msg_str == "":
        return

    for i in range(cnt):
        await tg_bot.sendMessage(chat_id=tg_chatid, text=msg_str)
        # await asyncio.sleep(0.5)

def telegram_thread():
    global tg_user
    global config
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    while True:
        # WARNING: sleep 1초시 초당 1회 요청이라 429 too many requests 로 차단될 가능성 있음.
        sleep(1)
        if not tg_user:
            continue
        userkeys = list(tg_user.keys())
        msg = ""
        for key in userkeys:
            loop = asyncio.get_event_loop()
            msg += msg_stat(tg_user[key], 0, key)
            msg += "\n"
            del tg_user[key]

        # 초당 2번 이상 메시지를 날리면 오류 난다.
        loop.run_until_complete(telegram_msg_send(msg))

    # 사실상 죽은 코드
    loop.close()

if use_telegram:
    try:
        import telegram
        import asyncio
        import threading
        print("Use Telegram")
        tg_bot = telegram.Bot(token=config["telegram"]["bot_token"])
        tg_chatid = config["telegram"]["chat_id"]
        print("Use Telegram!, Setting Success")

        telegram_thread = threading.Thread(target=telegram_thread)
        telegram_thread.daemon = True
        telegram_thread.start()
    except Exception as e:
        print(e)
        print("Telegram set Error")
        tg_bot = None
        tg_chatid = -1
        use_telegram = False
else:
    print("Telegram not use.")

class NewHelp(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        # for page in self.paginator.pages:
        #     emby = discord.Embed(description=page)
        #     await destination.send(embed=emby)
        if channel_check(self.context.channel.id) == False:
            return
        help_message="""봇 명령어
```
!useradd @mention     (ex - !useradd @Ib)
게임 모니터링을 진행할 사용자를 추가합니다.
멘션 없이 사용시 명령을 입력한 사용자를 추가합니다.
!ua 로 줄여 사용할 수 있습니다.

!userdel @mention     (ex - !userdel @Ib)
게임 모니터링중인 사용자를 삭제합니다.
멘션 없이 사용시 명령을 입력한 사용자를 삭제합니다.
!ud 로 줄여 사용할 수 있습니다.

!userlist             (ex - !userlist)
게임 모니터링중인 사용자의 리스트를 조회합니다.

!gamestat @mention  (ex - !gamestat @Ib)
특정 사용자의 게임 정보를 확인합니다. (디버그용 함수입니다.)

!check_game @mention  (ex - !check_game @Ib)
특정 사용자가 현재 게임중인지 확인합니다.

!check_game_name 사용자명#0000 (ex - !check_game Ib#0000)
특정 사용자가 현재 게임중인지 확인합니다.
사용자명은 서버의 별명이 아닌 실제 사용자의 이름과 태그를 입력합니다.
사용자의 아이디가 존재하는 경우 아이디를 입력하고 태그는 0으로 입력합니다. ( ex - !check_game Ib#0 )

!set_schedule 초      (ex - !set_schedule 60)
모니터링을 진행할 시간을 초 단위로 설정합니다.
해당 설정을 적용하려면 봇을 재부팅해야 합니다.

!set_repeat 횟수      (ex - !set_repeat 3)
게임중이 아닐 시 알림을 반복할 횟수를 설정합니다.

!reboot
봇을 재부팅합니다.
```"""
        # emby = discord.Embed(description=help_message)
        # await destination.send(embed=emby)
        await destination.send(help_message)


class MyBot(commands.Bot):
    # await bot start
    # https://gist.github.com/Rapptz/6706e1c8f23ac27c98cee4dd985c8120
    def __init__(self):
        print("Bot initializating...")
        intents = discord.Intents.all()
        super().__init__(command_prefix='!', intents=intents)
        self.initial_extensions = [
            'cogs.admin',
            'cogs.foo',
            'cogs.bar',
        ]

    async def setup_hook(self):
        print('Bot setup hook...')
        self.loop.create_task(game_scheduler())

    async def close(self):
        print("Bot is closing...")
        game_scheduler.cancel()
        await super().close()

    async def on_ready(self):
        print('========== Bot is Ready! ==========')
        game_scheduler.start()

bot = MyBot()
bot.help_command = NewHelp()

schedule_channel = None

schedule_repeat = config["schedule"]
if schedule_repeat < 1:
    print("wrong schedule time")
    if bot is not None:
        bot.close()
    exit(1)

# n초마다 돌면서 게임중인지 확인
# @tasks.loop(seconds=5.0)
@tasks.loop(seconds=schedule_repeat)
async def game_scheduler():
    global schedule_channel
    global config
    global gamename
    global first_alert_dict

    if schedule_channel is None:
        schedule_channel = bot.get_channel(config["bot_channel"])
        return

    none_users = []
    index = -1
    none_flag = False

    rewrite_flag = False
    for i in range(len(config["users"])):
        user = config["users"][i]

        index += 1
        none_flag = False
        alert_list = []
        debug_msg = ""

        if user["enable"] == 0:
            continue

        key = ""
        for i in range(len(user["id"])):
            key += (str(user["id"][i]) + "|")
        if key not in first_alert_dict:
            first_alert_dict[key] = 0

        for i in range(len(user["id"])):
            member = discord.utils.get(bot.get_all_members(), id=user["id"][i])
            stat:int = chk_game(member, gamename)
            if stat == -1:
                none_users.append(index)
                none_flag = True
                break

            # 리스트 인원 중 한명이라도 해당 게임을 하고 있으면 해당 유저는 게임을 하고 있다고 간주 (부계정)
            if stat == 0:
                # alert 가 0이었으면, 방금 게임을 시작한 것, alert을 1로 자동 조정한다.
                if user["alert"] == 0:
                    config["users"][i]["alert"] = 1
                    rewrite_flag = True
                alert_list = []
                debug_msg = ""
                break

            # 알람
            if user["alert"] == 0:
                # alert 가 0이면, 사용자가 알람을 임시적으로 받지 않는다고 설정한 것. (즉, 튕긴 것을 okay 명령어로 체크한 것)
                alert_list = []
                debug_msg = ""
                break

            alert_list.append([stat, member.id, member.display_name, member.discriminator])
            if config["debug_mode"] == True:
                debug_msg += "stat : {}\n".format(stat)
                debug_msg += print_game_inform(member)
                debug_msg += "\n"

        if none_flag is True:
            continue

        if len(alert_list) == 0:
            first_alert_dict[key] = 0
        else:
            first_alert_dict[key] += 1

        if first_alert_dict[key] >= first_alert_interval:
            first_alert_dict[key] = first_alert_interval
            await alert_channel_list(alert_list)
            if debug_msg != "":
                await schedule_channel.send(debug_msg)

    if len(none_users) > 0:
        del_idx = 0
        for none_idx in none_users:
            config["users"].pop(none_idx - del_idx)
            del_idx += 1

    if rewrite_flag == True:
        if set_config() == False:
            await schedule_channel.send("저장에 실패하였습니다.")
            await bot.close()
            await exit(1)


def channel_check(channel):
    global config

    if channel is None:
        return False
    if channel != config["bot_channel"]:
        return False
    return True

def get_user_inform(member):
    if member is None:
        print("member is None")
        return False

    mem = member._user
    if mem is None:
        print("member._user is None")
        return False

    # member의 실제 이름
    print("member name : {}".format(mem.name))
    # member의 서버 내에서의 별명
    print("member display name : {}".format(member.display_name))
    # member의 태그 (아이디 설정시 태그는 0)
    print("member discriminator : {}".format(mem.discriminator))
    # member의 아이디
    print("member id : {}".format(mem.id))

    if member.raw_status == "offline":
        print("member is offline")
        return False
    print("member is online")

    # member의 게임중
    if member.activity is None:
        print("member activity is None")
        return False

    print("member activity name : {}".format(member.activity.name))
    # m = discord.utils.get(bot.get_all_members(), name=member._user.name, discriminator=member._user.discriminator)
    # m = discord.utils.get(bot.get_all_members(), id=member.id)

def diff_game(obj, game_name) -> int:
    if obj is None:
        return False

    name = str(obj).lower().replace(" ", "")
    if name == game_name:
        return True

    return False


def chk_game(member, game_name) -> int:
    """_summary_
    Returns:
        int:
            -1 : 없는 사용자
            0  : 게임중 (정상)
            1  : 오프라인
            2  : 게임중이 아님
            3  : 다른 게임중
    """
    # game debug
    if member is None:
        # print("member is None")
        return -1

    if member.raw_status == "offline":
        # print("member is offline")
        return 1
    if member.activity is None:
        # print("member activity is None")
        return 2

    for activity in member.activities:
        if isinstance(activity, discord.activity.Game) is True:
            if diff_game(activity.name, game_name):
                return 0

            continue

        # 활동 상태에 따라 검사 방식이 다르다.
        elif isinstance(activity, discord.activity.Activity) is True:
            # print(isinstance(activity, discord.activity.Game))
            if diff_game(activity.name, game_name):
                return 0
            if diff_game(activity.details, game_name):
                return 0
            if diff_game(activity.state, game_name):
                return 0
            if diff_game(activity.large_image_text, game_name):
                return 0
            if diff_game(activity.small_image_text, game_name):
                return 0
            if activity.assets is not None:
                if diff_game(activity.assets.get("large_text"), game_name):
                    return 0
                if diff_game(activity.assets.get("small_text"), game_name):
                    return 0

            continue


    return 3

def chk_game_id(member_id, game_name) -> int:
    """_summary_
    Returns:
        int:
            -1 : 없는 사용자
            0  : 게임중 (정상)
            1  : 오프라인
            2  : 게임중이 아님
            3  : 다른 게임중
    """
    mem = discord.utils.get(bot.get_all_members(), id=member_id)
    return chk_game(mem, game_name)

def getid_with_mention(mention) -> list:
    output = []
    usrlist = mention.split(' ')
    for userstr in usrlist:
        user = userstr[2:-1]
        try:
            output.append(int(user))
        except:
            pass

    return output

def find_user_with_id(userid) -> any:
    global config
    for user in config["users"]:
        if user['id'] == userid:
            return user
    return None

def get_userindex_with_id(userid) -> int:
    global config
    userlen = len(config["users"])
    for i in range(userlen):
        if config["users"][i]['id'] == userid:
            return i
    return -1


def print_user_inform(userdict, alert_msg) -> str:
    msg = """{}
```
""".format(alert_msg)

    realname = "\n실제 이름 : "
    nickname = "\n서버 내 별명 : "
    for i in range(len(userdict["name"])):
        realname += "{}#{}, ".format(userdict["name"][i], userdict["tag"][i])
        nickname += "{}#{}, ".format(userdict['display_name'][i], userdict['tag'][i])
    realname = realname[:-2]
    nickname = nickname[:-2]
    msg += realname
    msg += nickname

    msg += "\n```"
    return msg

def parse_mention(ctx, func_name_index) -> list:
    # id 획득
    userid = []
    if len(ctx.message.content) == func_name_index:
        userid.append(ctx.author.id)
    else:
        commands = ctx.message.content[func_name_index + 1:]
        userid = getid_with_mention(commands)

    return userid

def print_game_inform(member) -> str:
    msg = "게임 상태 정보 출력"

    if member is None:
        msg += "\n해당 유저 정보를 찾을 수 없습니다."
        return msg

    userid = member.id
    if userid is None:
        msg += "\n유저 아이디를 획득할 수 없습니다."
        return msg

    if member.raw_status == "offline":
        # print("member is offline")
        msg += "\n<@{}> 님은 오프라인 입니다.".format(userid)
        return msg

    if member.activity is None:
        # print("member activity is None")
        msg += "\n<@{}> 님은 게임을 하고 있지 않습니다.".format(userid)
        return msg

    msg += "\n<@{}> 님의 게임 상태 정보\n".format(userid)
    msg += "```\n"
    for activity in member.activities:
        if isinstance(activity, discord.activity.Game) is True:
            msg += "Activity type : Game\n"
            msg += "activity.name : {}\n".format(activity.name)
            continue

        elif isinstance(activity, discord.activity.Activity) is True:
            msg += "\n"
            msg += "activity type : Activity\n"
            msg += "activity.name : {}\n".format(activity.name)
            msg += "activity.details : {}\n".format(activity.details)
            msg += "activity.large_image_text : {}\n".format(activity.large_image_text)
            msg += "activity.small_image_text : {}\n".format(activity.small_image_text)
            if activity.assets is None:
                msg += "activity.assets : None\n"
            else:
                msg += "activity.assets['large_text'] : {}\n".format(activity.assets.get("large_text"))
                msg += "activity.assets['small_text'] : {}\n".format(activity.assets.get("small_text"))
            continue

        msg += "not activity status"

    msg += "```"

    return msg

async def add_tguser(username, stat):
    global use_telegram
    global tg_user

    if use_telegram is False:
        return

    if username == "":
        return

    if username not in tg_user:
        tg_user[username] = stat

# alert 할 때에만 telegram에 알람을 날린다.
async def alert_channel(stat, userid, username = "", usertag = "0"):
    global config
    global schedule_channel

    if usertag != "0":
        username += ("#" + usertag)

    msg = msg_stat(stat, userid, username)
    if msg == "":
        return

    repeat:int = config["alert_repeat"]
    await add_tguser(username, stat)
    for i in range(repeat):
        # telegram_msg_send(msg)
        await schedule_channel.send(msg)

async def alert_channel_list(alert_list):
    global config
    global schedule_channel
    if len(alert_list) == 0:
        return
    msg = ""
    for i in range(len(alert_list)):
        stat = alert_list[i][0]
        userid = alert_list[i][1]
        username = alert_list[i][2]
        usertag = alert_list[i][3]
        if usertag != "0":
            username += ("#" + usertag)
        msg += msg_stat(stat, userid, username)
        msg += "\n"
        await add_tguser(username, stat)

    repeat:int = config["alert_repeat"]
    for i in range(repeat):
        # telegram_msg_send(msg)
        await schedule_channel.send(msg)


async def ret_code_with_channel(stat, userid, username = "", usertag = "0"):
    global schedule_channel

    if schedule_channel is None:
        schedule_channel = bot.get_channel(config["bot_channel"])
        return

    if usertag != "0":
        username += ("#" + usertag)

    msg = msg_stat(stat, userid, username)
    if msg != "":
        await add_tguser(username, stat)
        await schedule_channel.send(msg)

async def ret_code_with_msg(ctx, stat, userid, game_name="growcastle", username = "", usertag = "0"):
    msg = ""
    if usertag != "0":
        username += ("#" + usertag)

    if stat == 0:
        msg = "<@{}> ({})님은 {}중 입니다. 아주 좋아요!".format(userid, username, game_name)
    else:
        msg = msg_stat(stat, userid, username)

    await add_tguser(username, stat)
    await ctx.send(msg)


# @bot.command()
# async def 안녕(ctx):
#     await ctx.send("{}이라고 하셨군요, 반갑습니다 {}님!".format(
#         ctx.message.content, ctx.author.name))

# @bot.command()
# async def games(ctx):
#     for member in bot.get_all_members():
#         get_user_inform(member)
#         mem = discord.utils.get(bot.get_all_members(), id=member.id)
#         # mem = discord.utils.get(bot.get_all_members(), name=member._user.name, discriminator=member._user.discriminator)
#         if mem:
#             mention = member._user.mention
#             print("test")
#             await ctx.send("user : {}".format(member._user.name))
#             # await ctx.send(f"Hello {mention}>");
#             # ctx.send(f"The user ID of {username}#{tag} is {member.id}.")
#         else:
#             await ctx.send("User not found.")


@bot.command()
async def gamestat(ctx):
    if channel_check(ctx.channel.id) == False:
        return
    userid = parse_mention(ctx, 9)
    if len(userid) <= 0:
        await ctx.send("잘못된 명령어입니다")
        return

    member = discord.utils.get(bot.get_all_members(), id=userid[0])
    msg = print_game_inform(member)
    await ctx.send(msg)

@bot.command()
async def check_game(ctx):
    global gamename

    if channel_check(ctx.channel.id) == False:
        return
    userid = parse_mention(ctx, 11)
    if len(userid) <= 0:
        await ctx.send("잘못된 명령어입니다")
        return

    stat:int = chk_game_id(int(userid[0]), gamename)
    await ret_code_with_msg(ctx, stat, userid[0])

@bot.command()
async def check_game_name(ctx):
    global gamename

    if channel_check(ctx.channel.id) == False:
        return
    commands = ctx.message.content[17:]
    name, tag = commands.split("#", 1)
    if name is None or tag is None:
        await ctx.send("잘못된 명령어입니다")
        return
    mem = discord.utils.get(bot.get_all_members(), name=name, discriminator=tag)
    if mem is None:
        await ctx.send("존재하지 않는 사용자입니다")
        return

    userid = mem.id
    stat:int = chk_game(mem, gamename)
    # await ret_code_with_msg(ctx, stat, userid)
    await ret_code_with_msg(ctx, stat, mem.id, mem.display_name, mem.discriminator)

async def useradd_function(ctx, func_len):
    global config
    global bot
    if channel_check(ctx.channel.id) == False:
        return
    # print(ctx.message.content)
    userids = parse_mention(ctx, func_len)
    if len(userids) <= 0:
        await ctx.send("잘못된 명령어입니다")
        return
    if len(userids) > 3:
        await ctx.send("최대 3명까지 등록이 가능합니다.")
        return

    # 이미 있는 사용자인지 확인
    user = find_user_with_id(userids)
    if user is not None:
        msg = print_user_inform(user, "이미 모니터링 대상에 포함되어 있는 사용자입니다.")
        await ctx.send(msg)
        return

    # 초기화
    user_inform = {}
    user_inform['enable'] = 1
    user_inform['alert'] = 1
    user_inform['id'] = [ ]
    user_inform['name'] = [ ]
    user_inform["display_name"] = [ ]
    user_inform["tag"] = [ ]

    for userid in userids:
        # 사용자 정보 획득
        mem = discord.utils.get(bot.get_all_members(), id=userid)
        if mem is None:
            await ctx.send("존재하지 않는 사용자입니다")
            return
        if mem._user is None:
            await ctx.send("해당 사용자의 정보를 찾을 수 없습니다")
            return
        user_inform['id'].append(mem.id)
        user_inform['name'].append(mem._user.name)
        user_inform["display_name"].append(mem.display_name)
        user_inform["tag"].append(mem._user.discriminator)

    config["users"].append(user_inform)

    if set_config() == False:
        ctx.send("저장에 실패하였습니다.")
        await bot.close()
        await exit(1)
    msg = print_user_inform(user_inform, "모니터링 대상에 추가되었습니다.")
    await ctx.send(msg)


@bot.command()
async def useradd(ctx):
    await useradd_function(ctx, 8)

@bot.command()
async def ua(ctx):
    await useradd_function(ctx, 3)


async def userdel_function(ctx, func_len):
    global config
    global bot
    global first_alert_dict

    if channel_check(ctx.channel.id) == False:
        return
    userid = parse_mention(ctx, func_len)

    key = ""
    for userid_str in userid:
        key += (str(userid_str) + "|")
    if key in first_alert_dict:
        del first_alert_dict[key]

    if len(userid) <= 0:
        await ctx.send("잘못된 명령어입니다")
        return

    delindex = get_userindex_with_id(userid)
    if delindex < 0:
        await ctx.send("모니터링 대상에 포함되어 있지 않은 사용자입니다.")
        return

    removed_element = None
    try:
        removed_element = config["users"].pop(delindex)
    except:
        await ctx.send(print_user_inform(config["users"][delindex], "모니터링 대상에서 삭제되었습니다."))
        return

    if set_config() == False:
        ctx.send("저장에 실패하였습니다.")
        await bot.close()
        await exit(1)
    await ctx.send(print_user_inform(removed_element, "모니터링 대상에서 삭제되었습니다."))

@bot.command()
async def userdel(ctx):
    await userdel_function(ctx, 8)

@bot.command()
async def ud(ctx):
    await userdel_function(ctx, 3)


@bot.command()
async def userlist(ctx):
    global config
    if channel_check(ctx.channel.id) == False:
        return
    msg = "{} 초 마다 게임을 확인\n".format(config["schedule"])
    msg += "{} 번 반복하여 알림\n".format(config["alert_repeat"])
    msg += "모니터링 대상 사용자 리스트\n```"
    users = config["users"]
    if len(users) == 0:
        msg += "모니터링 대상 사용자가 없습니다."
    else:
        for user in users:
            realname = "\n실제 이름 : "
            nickname = "\n서버 내 별명 : "
            for i in range(len(user["name"])):
                realname += "{}#{}, ".format(user["name"][i], user["tag"][i])
                nickname += "{}#{}, ".format(user['display_name'][i], user['tag'][i])
            realname = realname[:-2]
            nickname = nickname[:-2]
            statstr = "\n현재 상태 : enable - {}, alert - {}".format(user["enable"], user["alert"])
            msg += realname
            msg += nickname
            msg += statstr


    msg += "```"
    await ctx.send(msg)
    return

@bot.command()
async def set_schedule(ctx):
    global config
    global bot
    if channel_check(ctx.channel.id) == False:
        return

    if len(ctx.message.content) <= 13:
        return

    commands = ctx.message.content[13:]
    schedule_time = -1
    try:
        schedule_time = int(commands)
    except:
        await ctx.send("잘못된 명령어입니다")
        return

    config["schedule"] = schedule_time
    if set_config() == False:
        ctx.send("저장에 실패하였습니다.")
        await bot.close()
        await exit(1)

    await ctx.send("스케쥴이 {}초로 변경되었습니다.\n해당 설정을 적용하려면 봇을 재부팅해야 합니다.".format(schedule_time))

@bot.command()
async def set_repeat(ctx):
    global config
    global bot
    if channel_check(ctx.channel.id) == False:
        return

    if len(ctx.message.content) <= 11:
        return

    commands = ctx.message.content[11:]
    repeat_time = -1
    try:
        repeat_time = int(commands)
    except:
        await ctx.send("잘못된 명령어입니다")
        return

    config["alert_repeat"] = repeat_time
    if set_config() == False:
        ctx.send("저장에 실패하였습니다.")
        await bot.close()
        await exit(1)

    await ctx.send("알림 반복 횟수가 {}회로 변경되었습니다.".format(repeat_time))



@bot.command()
async def reboot(ctx):
    global config
    global bot
    if channel_check(ctx.channel.id) == False:
        return
    await ctx.send("봇을 재부팅합니다.")
    if set_config() == False:
        ctx.send("저장에 실패하였습니다.")
        await bot.close()
        await exit(1)

    await bot.close()
    await exit(0)

def main():
    global config
    token = config['bot_token']

    if len(token) == 0:
        print("token is empty")
        exit(1)

    bot.run(token)
    set_config()


async def enable_function(ctx, func_len):
    global config
    global bot
    if channel_check(ctx.channel.id) == False:
        return
    # print(ctx.message.content)
    userids = parse_mention(ctx, func_len)
    if len(userids) <= 0:
        await ctx.send("잘못된 명령어입니다")
        return
    if len(userids) > 1:
        await ctx.send("enable 명령어는 복수 개의 mention과 함께 사용할 수 없습니다.")
        return

    finduser = userids[0]
    count = 0
    for i in range(len(config["users"])):
        users = config["users"][i]
        if finduser in users["id"]:
            config["users"][i]["enable"] = 1
            config["users"][i]["alert"] = 1
            count += 1

    if set_config() == False:
        ctx.send("저장에 실패하였습니다.")
        await bot.close()
        await exit(1)

    if count > 0:
        await ctx.send("enable 성공")
    else:
        await ctx.send("사용자를 찾을 수 없습니다.")
    return

@bot.command()
async def enable(ctx):
    await enable_function(ctx, 7)
    return


async def disable_function(ctx, func_len):
    global config
    global bot
    if channel_check(ctx.channel.id) == False:
        return
    # print(ctx.message.content)
    userids = parse_mention(ctx, func_len)
    if len(userids) <= 0:
        await ctx.send("잘못된 명령어입니다")
        return
    if len(userids) > 1:
        await ctx.send("disable 명령어는 복수 개의 mention과 함께 사용할 수 없습니다.")
        return

    finduser = userids[0]
    count = 0
    for i in range(len(config["users"])):
        users = config["users"][i]
        if finduser in users["id"]:
            config["users"][i]["enable"] = 0
            config["users"][i]["alert"] = 0
            count += 1

    if set_config() == False:
        ctx.send("저장에 실패하였습니다.")
        await bot.close()
        await exit(1)

    if count > 0:
        await ctx.send("disable 성공")
    else:
        await ctx.send("사용자를 찾을 수 없습니다.")
    return

@bot.command()
async def disable(ctx):
    await disable_function(ctx, 8)
    return


async def okay_function(ctx, func_len):
    global config
    global bot
    if channel_check(ctx.channel.id) == False:
        return
    # print(ctx.message.content)
    userids = parse_mention(ctx, func_len)
    if len(userids) <= 0:
        await ctx.send("잘못된 명령어입니다")
        return
    if len(userids) > 1:
        await ctx.send("okay 명령어는 복수 개의 mention과 함께 사용할 수 없습니다.")
        return

    finduser = userids[0]
    count = 0
    for i in range(len(config["users"])):
        users = config["users"][i]
        if finduser in users["id"]:
            if users["enable"] == 0:
                continue
            config["users"][i]["alert"] = 0
            count += 1

    if set_config() == False:
        ctx.send("저장에 실패하였습니다.")
        await bot.close()
        await exit(1)

    if count > 0:
        await ctx.send("알람을 일시적으로 비활성화 합니다.")
    else:
        await ctx.send("사용자를 찾을 수 없습니다.")
    return

@bot.command()
async def okay(ctx):
    await okay_function(ctx, 5)


@bot.command()
async def ok(ctx):
    await okay_function(ctx, 3)

@bot.command()
async def userok(ctx):
    await okay_function(ctx, 7)



if __name__ == "__main__":
    main()


