#! /opt/homebrew/bin/python3
#! /usr/bin/python3
import discord
from discord.ext import tasks, commands


print("START PROGRAM")

@tasks.loop(seconds=5.0)
async def game_scheduler():
    print("Game Scheduler")




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

def main():
    token = ""

    with open("token.txt", "r") as f:
        token = f.readline()
        token = token.replace("\r", "")
        token = token.replace("\n", "")

    if len(token) == 0:
        print("token is empty")
        exit(1)

    bot.run(token)

if __name__ == "__main__":
    main()



@bot.command()
async def 안녕(ctx):
    await ctx.send("{}이라고 하셨군요, 반갑습니다 {}님!".format(
        ctx.message.content, ctx.author.name))
