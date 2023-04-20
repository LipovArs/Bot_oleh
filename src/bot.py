import discord
from discord.ext import commands
from discord.utils import get
import os
import bot_func

intents = discord.Intents.all()
intents.message_content = True

config = {
    'prefix': '.'
}

bot = commands.Bot(command_prefix=config['prefix'], intents=intents)


@bot.event
async def on_ready():
    print(f"Bot {bot.user} is ready")


@bot.event
async def on_message(message):

    if message.content.startswith('.help'):
        await message.channel.send(bot_func.help_fun())

    elif message.content.startswith('.check_all_ban_words'):
        await message.channel.send(bot_func.get_ban_words())

    elif message.content.startswith('.'):
        await message.channel.send("Unknown command.")

    elif get(message.guild.roles, name="Жидобор") not in message.author.roles:
        print(message.content)
        for content in message.content.lower().split():
            for course_word in CONTENT_WORDS:
                if content == course_word:
                    await message.delete()
                    await message.channel.send(f"{message.author.mention} ти не маєш ліцензії на слово ЖИД")


bot.run(os.environment('BOT_DS_TOKEN'))
