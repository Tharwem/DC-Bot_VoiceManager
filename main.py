import datetime
import os

from discord.ext import commands
from discord import Intents
from discord.ext.commands import Context
from colorama import Fore
from utils import info, TOKEN

bot = commands.Bot(command_prefix=".", intents=Intents.all())


@bot.listen("on_ready")
async def is_ready():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')
            info(f'cogs.{filename[:-3]}', 'is loaded.')


@bot.command()
async def test(ctx: Context):
    print(ctx.channel.id)
    await ctx.send("pong")


@bot.command()
@commands.is_owner()
async def load(ctx, extension):
    await bot.load_extension(f'cogs.{extension}')
    await ctx.send(f'{extension} is loaded')


@bot.command()
@commands.is_owner()
async def unload(ctx, extension):
    await bot.unload_extension(f'cogs.{extension}')
    await ctx.send(f'{extension} is unloaded')


@bot.command()
@commands.is_owner()
async def reload(ctx, extension):
    await bot.unload_extension(f'cogs.{extension}')
    await bot.load_extension(f'cogs.{extension}')
    await ctx.send(f'{extension} is reloaded')


@bot.command()
@commands.is_owner()
async def shutdown(ctx):
    await ctx.send(f'Bot wird nun heruntergefahren.')
    await bot.close()


def main():
    token: str = TOKEN
    if token is None or token == '':
        print("Please type/copy your token into the console and hit enter to run the bot.")
        token: str = input()
    bot.run(token)


if __name__ == '__main__':
    main()

