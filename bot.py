#! /opt/homebrew/bin/python3
#! /usr/bin/python3
import discord
from discord.ext import tasks, commands
import json
from os.path import isfile

# game_scheduler
# 게임 이름은 영어일 경우 모두 소문자로, 공백 없이 적어주세요

print("START PROGRAM")

config:dict = None
config_file:str = "config.json"

def get_config() -> bool:
    global config
    global config_file
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

    return True


def set_config() -> None:
    global config
    global config_file
    try:
        with open(config_file, "w") as f:
            json.dump(config, f, indent=4)
    except:
        print("config file save error")
        exit(1)


if get_config() is False:
    print("config load error")
    exit(1)

repeat = config["repeat"]


class NewHelp(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        # for page in self.paginator.pages:
        #     emby = discord.Embed(description=page)
        #     await destination.send(embed=emby)
        help_message="""봇 명령어
```
!useradd @mention     (ex - !useradd @Ib)
게임 모니터링을 진행할 사용자를 추가합니다.
멘션 없이 사용시 명령을 입력한 사용자를 추가합니다.

!userdel @mention     (ex - !userdel @Ib)
게임 모니터링중인 사용자를 삭제합니다.
멘션 없이 사용시 명령을 입력한 사용자를 삭제합니다.

!userlist             (ex - !userlist)
게임 모니터링중인 사용자의 리스트를 조회합니다.

!check_game @mention  (ex - !check_game @Ib)
특정 사용자가 현재 게임중인지 확인합니다.

!check_game_name 사용자명#0000 (ex - !check_game Ib#0000)
특정 사용자가 현재 게임중인지 확인합니다.
사용자명은 서버의 별명이 아닌 실제 사용자의 이름과 태그를 입력합니다.
사용자의 아이디가 존재하는 경우 아이디를 입력하고 태그는 0으로 입력합니다. ( ex - !check_game Ib#0 )
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

# n초마다 돌면서 게임중인지 확인
@tasks.loop(seconds=5.0)
async def game_scheduler():
    global schedule_channel
    global config

    if schedule_channel is None:
        schedule_channel = bot.get_channel(config["bot_channel"])
        return

    none_users = []
    index = -1
    for user in config["users"]:
        index += 1
        stat = chk_game_id(user["id"], "growcastle")
        if stat == -1:
            none_users.append(index)
            continue
        await alert_channel(stat, user["id"])

    if len(none_users) > 0:
        del_idx = 0
        for none_idx in none_users:
            config["users"].pop(none_idx - del_idx)
            del_idx += 1


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

def getid_with_mention(mention) -> int:
    user = mention[2:-1]
    real_id = -1
    try:
        real_id = int(user)
    except:
        return -1

    return real_id

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
실제 이름 : {}#{}
서버 내 별명 : {}#{}
```""".format(alert_msg, userdict['name'], userdict["tag"]
              ,userdict['display_name'], userdict['tag'])
    return msg

def parse_mention(ctx, func_name_index) -> int:
    # id 획득
    if len(ctx.message.content) == func_name_index:
        userid = ctx.author.id
    else:
        commands = ctx.message.content[func_name_index + 1:]
        userid = getid_with_mention(commands)

    return userid


async def alert_channel(stat, userid):
    global repeat
    global schedule_channel
    # for i in range(repeat):
    msg = ""
    if stat == 1:
        msg = "<@{}> 님은 오프라인 입니다. 일어나세요 용사여!".format(userid)
        # msg = "<@{}> is offline. Wake up!!!".format(userid)
    elif stat == 2:
        msg ="<@{}> 님은 게임을 하고 있지 않습니다. 돌아오세요 용사여!".format(userid)
        # msg = "<@{}> is not playing a game. Come back!!!".format(userid)
    elif stat == 3:
        msg = "<@{}> 님은 다른 게임을 하고 있습니다. 돌아오세요 용사여!".format(userid)
        # msg = "<@{}> is playing a another game. Come back!!!".format(userid)

    if msg == "":
        return

    await schedule_channel.send(msg)


async def ret_code_with_channel(stat, userid):
    global schedule_channel

    if schedule_channel is None:
        schedule_channel = bot.get_channel(config["bot_channel"])
        return

    msg = ""
    if stat == -1:
        msg = "존재하지 않는 사용자입니다"
        # msg = "no user"
    elif stat == 1:
        msg = "<@{}> 님은 오프라인 입니다. 일어나세요 용사여!".format(userid)
        # msg = "<@{}> is offline. Wake up!!!".format(userid)
    elif stat == 2:
        msg = "<@{}> 님은 게임을 하고 있지 않습니다. 돌아오세요 용사여!".format(userid)
        # msg = "<@{}> is not playing a game. Come back!!!".format(userid)
    elif stat == 3:
        msg = "<@{}> 님은 다른 게임을 하고 있습니다. 돌아오세요 용사여!".format(userid)
        # msg = "<@{}> is playing a another game. Come back!!!".format(userid)

    if msg != "":
        await schedule_channel.send(msg)

async def ret_code_with_msg(ctx, stat, userid, game_name="growcastle"):
    msg = ""
    if stat == -1:
        msg = "존재하지 않는 사용자입니다"
        # msg = "no user"
    elif stat == 1:
        msg = "<@{}> 님은 오프라인 입니다. 일어나세요 용사여!".format(userid)
        # msg = "<@{}> is offline. Wake up!!!".format(userid)
    elif stat == 2:
        msg = "<@{}> 님은 게임을 하고 있지 않습니다. 돌아오세요 용사여!".format(userid)
        # msg = "<@{}> is not playing a game. Come back!!!".format(userid)
    elif stat == 3:
        msg = "<@{}> 님은 다른 게임을 하고 있습니다. 돌아오세요 용사여!".format(userid)
        # msg = "<@{}> is playing a another game. Come back!!!".format(userid)
    else:
        msg = "<@{}> 님은 {}중 입니다. 아주 좋아요!".format(userid, game_name)
        # msg = "<@{}> is playing {}. very good!!!".format(userid, game_name)

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
async def check_game(ctx):
    if channel_check(ctx.channel.id) == False:
        return
    userid = parse_mention(ctx, 11)
    if userid < 0:
        await ctx.send("잘못된 명령어입니다")
        return

    game_name = "growcastle"
    stat:int = chk_game_id(int(userid), game_name)
    await ret_code_with_msg(ctx, stat, userid)

@bot.command()
async def check_game_name(ctx):
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
    game_name = "growcastle"
    stat:int = chk_game(mem, game_name)
    await ret_code_with_msg(ctx, stat, userid)


@bot.command()
async def useradd(ctx):
    global config
    if channel_check(ctx.channel.id) == False:
        return
    userid = parse_mention(ctx, 8)
    if userid < 0:
        await ctx.send("잘못된 명령어입니다")
        return

    # 이미 있는 사용자인지 확인
    user = find_user_with_id(userid)
    if user is not None:
        msg = print_user_inform(user, "이미 모니터링 대상에 포함되어 있는 사용자입니다.")
        await ctx.send(msg)
        return

    # 사용자 정보 획득
    mem = discord.utils.get(bot.get_all_members(), id=userid)
    if mem is None:
        await ctx.send("존재하지 않는 사용자입니다")
        return
    if mem._user is None:
        await ctx.send("해당 사용자의 정보를 찾을 수 없습니다")
        return

    # 추가
    user_inform = {}
    user_inform['id'] = mem.id
    user_inform['name'] = mem._user.name
    user_inform["display_name"] = mem.display_name
    user_inform["tag"] = mem._user.discriminator
    config["users"].append(user_inform)
    set_config()
    msg = print_user_inform(user_inform, "모니터링 대상에 추가되었습니다.")
    await ctx.send(msg)


@bot.command()
async def userdel(ctx):
    global config
    if channel_check(ctx.channel.id) == False:
        return
    userid = parse_mention(ctx, 8)
    if userid < 0:
        await ctx.send("잘못된 명령어입니다")
        return

    delindex = get_userindex_with_id(userid)
    if delindex < 0:
        await ctx.send("모니터링 대상에 포함되어 있지 않은 사용자입니다.")
        return

    removed_element = None
    try:
        removed_element = config["users"].pop(delindex)
        set_config()
    except:
        await ctx.send(print_user_inform(config["users"][delindex], "모니터링 대상에서 삭제되었습니다."))
        return

    await ctx.send(print_user_inform(removed_element, "모니터링 대상에서 삭제되었습니다."))

@bot.command()
async def userlist(ctx):
    global config
    if channel_check(ctx.channel.id) == False:
        return
    msg = "모니터링 대상 사용자 리스트\n```"
    users = config["users"]
    if len(users) == 0:
        msg += "모니터링 대상 사용자가 없습니다."
    else:
        for user in users:
            msg += "\n실제 이름 : {}#{}\n".format(user["name"], user["tag"])
            msg += "서버 내 별명 : {}#{}\n".format(user['display_name'], user['tag'])


    msg += "```"
    await ctx.send(msg)
    return


def main():
    global config
    token = config['bot_token']

    if len(token) == 0:
        print("token is empty")
        exit(1)

    bot.run(token)
    set_config()

if __name__ == "__main__":
    main()


