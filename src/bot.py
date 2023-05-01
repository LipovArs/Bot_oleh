import discord
from discord.ext import commands
from discord.utils import get
from discord import Game
import os
import bot_func
import datetime
import youtube_dl

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

    elif message.content.startswith('.gauss'):
        await message.channel.send(bot_func.gaussian_method(message.content))

    elif message.content.startswith('.stats'):
        await message.channel.send(bot_func.stat_msg(message))

    elif message.content.startswith('.inf'):
        await bot_func.user_info(message)

    if message.content.startswith('.play'):
        if message.author.voice:
            channel = message.author.voice.channel
            await channel.connect()
        else:
            await message.channel.send("Kakish")
    
    elif message.content.startswith('.role'):
        roles = message.author.roles
        await message.channel.send(roles)

    elif message.content.startswith('.'):
        await message.channel.send("Unknown command.")

    # roles_list = [role.name for role in message.author.roles]
    # message_test = bot_func.message_view(message.content.lower(), roles_list)
    # if not message_test:
    #     pass
    # elif message_test == 'Jid_detected':
    #     await message.delete()
    #     await message.channel.send(f"{message.author.mention} ти не маєш ліцензії на слово ЖИД")
    # else:
    #     await message.delete()
    #     await message.channel.send(f"{message.author.mention}, {message_test}")


bot.run(os.environ['BOT_DS_TOKEN'])
