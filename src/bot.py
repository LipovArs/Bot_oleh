import discord
from discord.ext import commands
from discord.utils import get
from discord import Game
import os
import bot_func

intents = discord.Intents.all()
intents.message_content = True
intents.members = True
intents.presences = True

config = {
    'prefix': '.'
}

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

    elif message.content.startswith('.g'):
        await message.channel.send(bot_func.gaussian_method(message.content))

    elif message.content.startswith('.'):
        await message.channel.send("Unknown command.")

    elif get(message.guild.roles, name="Жидобор") not in message.author.roles:
        print(message.content)
        for content in message.content.lower().split():
            for course_word in bot_func.get_ban_words():
                if content == course_word:
                    await message.delete()
                    await message.channel.send(f"{message.author.mention} ти не маєш ліцензії на слово ЖИД")


@client.event
async def on_member_update(before, after):
    if before.activities != after.activities:
        if len(after.activities) == 0:
            print(f"{after.name} has stopped playing a game.")
        elif str(after.activities[0].type) == "ActivityType.playing":
            print(f"{after.name} is now playing {after.activities[0].name}.")


bot.run(os.environ['BOT_DS_TOKEN'])