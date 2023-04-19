import discord
from discord.ext import commands
from discord.utils import get
import os

intents = discord.Intents.all()
intents.message_content = True

config = {
    'prefix': '.'
}


CONTENT_WORDS = ["жид", "жиди", "жидо-бандерівець", "жидо-бандеравець", "жидобор", "жидо-бандера", "жидобандерівець", "jid", "жидів", "жидами", "жида", "жидах", "жидом", "жиду", "жидам", "жиді", ";bl", ":bl", ";blb", ":blb"]

bot = commands.Bot(command_prefix=config['prefix'], intents=intents)


@bot.event
async def on_ready():
    print(f"Bot {bot.user} is ready")


@bot.event
async def on_message(message):

    if get(message.guild.roles, name="Жидобор") not in message.author.roles:
        print(message.content)
        for content in message.content.lower().split():
            for course_word in CONTENT_WORDS:
                if content == course_word:
                    await message.delete()
                    await message.channel.send(f"{message.author.mention} ти не маєш ліцензії на слово ЖИД")

bot.run(os.environment('BOT_DS_TOKEN'))