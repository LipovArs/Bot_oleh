import sqlite3
import os
from openpyxl import Workbook
from openpyxl.styles import Alignment
from io import BytesIO
import discord
import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "models", "database.db")

db_connection = sqlite3.connect(DATABASE_PATH)

async def collect_users(ctx):
    guild = ctx.guild
    for member in guild.members:
        discord_id = member.id
        username = str(member)

        cursor = db_connection.cursor()
        cursor.execute(
            "INSERT INTO users (discord_id, discord_name) VALUES (?, ?) ON CONFLICT(discord_id) DO UPDATE SET discord_name = ?",
            (discord_id, username, username)
        )
        db_connection.commit()

    await ctx.channel.send(f"Інформація про {len(guild.members)} користувачів зібрана!")

async def on_member_join(member):
    discord_id = member.id
    username = str(member)

    cursor = db_connection.cursor()
    cursor.execute(
        "INSERT INTO users (discord_id, discord_name) VALUES (?, ?) ON CONFLICT(discord_id) DO UPDATE SET discord_name = ?",
        (discord_id, username, username)
    )
    db_connection.commit()

async def on_member_remove(member):
    discord_id = member.id

    cursor = db_connection.cursor()
    cursor.execute(
        "DELETE FROM users WHERE discord_id = ?",
        (discord_id,)
    )
    db_connection.commit()


async def on_message_delete(message):
    discord_id = message.author.id
    username = str(message.author)
    message_ctx = message.content

    if message.author.bot:
        return

    cursor = db_connection.cursor()
    cursor.execute(
        "INSERT INTO message_log (user_id, user_name, context) VALUES (?, ?, ?)",
        (discord_id, username, message_ctx)
    )
    db_connection.commit()


async def on_message_edit(before, after):
    discord_id = before.author.id
    username = str(before.author)
    before_message = before.content
    after_message = after.content

    if before.author.bot or before.content == after.content:
        return

    cursor = db_connection.cursor()
    cursor.execute(
        "INSERT INTO message_log (user_id, user_name, context, context_after_change) VALUES (?, ?, ?, ?)",
        (discord_id, username, before_message, after_message)
    )
    db_connection.commit()


async def get_message_log(ctx, user, time):
    cursor = db_connection.cursor()

    query = "SELECT * FROM message_log"
    condition = []
    params = []

    if user and user.lower() != "all":
        condition.append("user_name LIKE ?")
        params.append(f"%{user}%")

    if time:
        current_time = datetime.datetime.now()
        if time.lower() == "last day":
            start_date = current_time - datetime.timedelta(days=1)
        elif time.lower() == "last week":
            start_date = current_time - datetime.timedelta(weeks=1)
        elif time.lower() == "last month":
            start_date = current_time - datetime.timedelta(days=30)
        elif time.lower() is None:
            start_date = None
        else:
            await ctx.send("Invalid time period. Use 'all', 'last day', or 'last week' or 'last month'." + time)
            return

        if start_date:
            condition.append("registration_time >= ?")
            params.append(start_date.strftime('%Y-%m-%d %H:%M:%S'))


    if condition:
        query += " WHERE " + " AND ".join(condition)

    try:
        cursor.execute(query, params)
        rows = cursor.fetchall()

        if not rows:
            await ctx.send("No messages found for the given filters." + time)
            return

        wb = Workbook()
        ws = wb.active
        ws.title = "Message Log"

        headers = ["ID", "User ID","Username", "Before Message", "After Message (If edited)", "Time"]
        ws.append(headers)

        for row in rows:
            ws.append(row)

        for col in ws.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = (max_length + 2)
            ws.column_dimensions[column].width = adjusted_width

        for row in ws.iter_rows(min_row=2, min_col=3, max_col=4):
            for cell in row:
                cell.alignment = Alignment(wrap_text=True)
                cell.font = cell.font.copy(size=14)

        file_stream = BytesIO()
        wb.save(file_stream)
        file_stream.seek(0)

        await ctx.send(file=discord.File(file_stream, f"message_log_{user}_{time}.xlsx"))
    except sqlite3.ProgrammingError as e:
        await ctx.send(f"An error occurred: {str(e)}")


async def on_voice_state_update(member, before, after):
    user_id = member.id
    current_time = datetime.datetime.now()

    cursor = db_connection.cursor()

    if before.channel is None and after.channel is not None:
        cursor.execute(
            "INSERT INTO voice_time (user_id, last_join) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET last_join = ?",
            (user_id, current_time, current_time)
        )
    elif before.channel is not None and after.channel is None:
        cursor.execute("SELECT last_join FROM voice_time WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()

        if row and row[0]:
            last_join = datetime.datetime.strptime(row[0].split('.')[0], '%Y-%m-%d %H:%M:%S')
            duration = (current_time - last_join).total_seconds()

            points_earned = int(duration // 60)
            cursor.execute(
                "SELECT score_points FROM users WHERE discord_id = ?", (user_id,)
            )
            user_row = cursor.fetchone()

            if user_row:
                current_points = user_row[0]
                cursor.execute(
                    "UPDATE users SET score_points = ? WHERE discord_id = ?",
                    (current_points + points_earned, user_id)
                )
            else:
                cursor.execute(
                    "INSERT INTO users (discord_id, points) VALUES (?, ?)",
                    (user_id, points_earned)
                )

            cursor.execute(
                "UPDATE voice_time SET total_time = total_time + ?, last_join = NULL WHERE user_id = ?",
                (int(duration), user_id)
            )
    elif before.channel != after.channel:
        cursor.execute("SELECT last_join FROM voice_time WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()

        if row and row[0]:
            last_join = datetime.datetime.strptime(row[0].split('.')[0], '%Y-%m-%d %H:%M:%S')
            duration = (current_time - last_join).total_seconds()

            points_earned = int(duration // 60)
            cursor.execute(
                "SELECT score_points FROM users WHERE discord_id = ?", (user_id,)
            )
            user_row = cursor.fetchone()

            if user_row:
                current_points = user_row[0]
                cursor.execute(
                    "UPDATE users SET score_points = ? WHERE discord_id = ?",
                    (current_points + points_earned, user_id)
                )
            else:
                cursor.execute(
                    "INSERT INTO users (discord_id, score_points) VALUES (?, ?)",
                    (user_id, points_earned)
                )

            cursor.execute(
                "UPDATE voice_time SET total_time = total_time + ?, last_join = ? WHERE user_id = ?",
                (int(duration), current_time, user_id)
            )

    db_connection.commit()


async def top_voice_users(ctx):
    cursor = db_connection.cursor()
    cursor.execute("SELECT user_id, total_time FROM voice_time ORDER BY total_time DESC LIMIT 10")
    rows = cursor.fetchall()

    if not rows:
        await ctx.send("Немає даних про час користувачів у голосових кімнатах.")
        return

    embed = discord.Embed(title="Топ користувачів за часом у голосових каналах", color=discord.Color.blue())

    for i, (user_id, total_time) in enumerate(rows, start=1):
        user = await ctx.bot.fetch_user(user_id)
        formatted_time = str(datetime.timedelta(seconds=total_time))
        embed.add_field(name=f"{i}. {user.name}", value=f"Проведений час: {formatted_time}", inline=False)

    await ctx.send(embed=embed)


async def balance(ctx):
    cursor = db_connection.cursor()
    cursor.execute("SELECT score_points FROM users WHERE discord_id = ?", (ctx.author.id,))
    result = cursor.fetchone()
    await ctx.send(f"{ctx.author.mention}, у вас {result[0]} балів.")