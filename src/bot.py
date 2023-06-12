import asyncio
import discord
from discord.ext import commands
from discord.utils import get
from discord import Game
import os
import bot_func
import music_func
import vote_func
import datetime
from discord import FFmpegPCMAudio
import youtube_dl
from typing import List

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True


config = {
    'prefix': '.'
}

game_stats = {}


bot = commands.Bot(command_prefix=config['prefix'], intents=intents)
client = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f"Bot {bot.user} is ready")
    await bot.change_presence(activity=Game(".help"))


@bot.event
async def on_message(message):
    if message.content.startswith('.help'):
        await message.channel.send(bot_func.help_fun())

    elif message.content.startswith('.check_all_ban_words'):
        await message.channel.send(bot_func.get_ban_words())

    elif message.content.startswith('.stats'):
        await message.channel.send(bot_func.stat_msg(message))

    elif message.content.startswith('.inf'):
        await bot_func.user_info(message)

    elif message.content.startswith('.play'):
        await music_func.play(message)

    elif message.content.startswith('.skip'):
        await music_func.skip(message)

    elif message.content.startswith('.pause'):
        await music_func.pause(message)

    elif message.content.startswith('.resume'):
        await music_func.resume(message)

    elif message.content.startswith('.queue'):
        await music_func.queue(message)

    elif message.content.startswith('.leave'):
        await music_func.leave(message)

    elif message.content.startswith('.vote'):
        aut_id = message.author.id
        await vote_func.vote(message, bot=bot, author_id=aut_id)

    elif message.content.startswith('.'):
        await message.channel.send("Unknown command.")

    roles_list = [role.name for role in message.author.roles]
    message_test = bot_func.message_view(message.content.lower(), roles_list)
    if not message_test:
        pass
    elif message_test == 'Jid_detected':
        await message.delete()
        await message.channel.send(f"{message.author.mention} ти не маєш ліцензії на слово ЖИД")
    else:
        await message.delete()
        await message.channel.send(f"{message.author.mention}, {message_test}")


bot.run(os.environ['BOT_DS_TOKEN'])
