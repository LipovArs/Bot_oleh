import discord
from discord.ext import commands
from discord import Game
from dotenv import load_dotenv
import os
import bot_func
import vote_func
import db_manage
import music_func
import message_control
import casino_fun
from db_manage import db_connection

load_dotenv()
BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.all()
intents.message_content = True
intents.members = True
intents.presences = True


game_stats = {}


bot = commands.Bot(command_prefix='.', intents=intents)
client = discord.Client(intents=intents)

bot.help_command = bot_func.CustomHelpCommand()


def admin_only_command(func):
    func.admin_only = True
    return commands.has_permissions(administrator=True)(func)


@bot.event
async def on_ready():
    print(f"Bot {bot.user} is ready")
    await bot.change_presence(activity=Game(".help"))


@bot.command(name="help_admin")
@admin_only_command
async def help_admin(ctx):
    await bot_func.help_admin(ctx)

@bot.command(name="check_all_ban_words")
@admin_only_command
async def example(ctx):
    await ctx.channel.send(message_control.get_ban_words())

@bot.command(name="stats")
async def stats(ctx):
    await ctx.channel.send(bot_func.stat_msg(ctx))

@bot.command(name="inf")
@admin_only_command
async def inf(ctx):
    await bot_func.user_info(ctx)

@bot.command(name="play")
async def play_command(ctx, *, url: str):
    await music_func.play(ctx, url=url)

@bot.command(name="pause")
async def pause_command(ctx):
    await music_func.pause(ctx)

@bot.command(name="resume")
async def resume_command(ctx):
    await music_func.resume(ctx)

@bot.command(name="skip")
async def skip_command(ctx):
    await music_func.skip(ctx)

@bot.command(name="queue")
async def queue_command(ctx):
    await music_func.queued(ctx)

@bot.command(name="leave")
async def leave_command(ctx):
    await music_func.leave(ctx)

@bot.command(name="stop")
async def stop_command(ctx):
    await music_func.stop(ctx)

@bot.command(name="vote")
async def vote(ctx):
    aut_id = ctx.author.id
    await vote_func.vote(ctx, bot=bot, author_id=aut_id)

@bot.command(name="top_voice_users")
async def top_voice_users(ctx):
    await db_manage.top_voice_users(ctx)

@bot.command(name="get_message_log")
@admin_only_command
async def get_message_log(ctx, user: str = "all", *, time: str = None):
    await db_manage.get_message_log(ctx, user, time)

@bot.command(name="balance")
async def balance(ctx):
    await db_manage.balance(ctx)

@bot.command(name="casino")
async def casino(ctx, game: str = None, bet: int = None):
    await casino_fun.casino(ctx, game, bet)


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)

    cursor = db_connection.cursor()
    cursor.execute(
        "SELECT score_points FROM users WHERE discord_id = ?", (message.author.id,)
    )
    user_row = cursor.fetchone()

    if user_row:
        current_points = user_row[0]
        cursor.execute(
            "UPDATE users SET score_points = ? WHERE discord_id = ?",
            (current_points + 1, message.author.id)
        )
    else:
        cursor.execute(
        "INSERT INTO users (discord_id, score_points) VALUES (?, ?)",
        (message.author.id, 1)
        )

    db_connection.commit()


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


@bot.event
async def on_member_join(member):
    await db_manage.on_member_join(member)

@bot.event
async def on_member_remove(member):
    await db_manage.on_member_remove(member)

@bot.event
async def on_message_delete(message):
    await db_manage.on_message_delete(message)

@bot.event
async def on_message_edit(before, after):
    await db_manage.on_message_edit(before, after)

@bot.event
async def on_voice_state_update(member, before, after):
    await db_manage.on_voice_state_update(member, before, after)

@bot.command(name="collect_user_info")
@admin_only_command
async def collect_user_info(ctx):
    await db_manage.collect_users(ctx)

bot.run(BOT_TOKEN)
