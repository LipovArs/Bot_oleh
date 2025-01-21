import discord
from discord.ui import Button, View
from discord.ext import commands
import sqlite3
import os
import random
import asyncio

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "models", "database.db")

db_connection = sqlite3.connect(DATABASE_PATH)

async def get_user_score(user_id):
    cursor = db_connection.cursor()
    cursor.execute("SELECT score_points FROM users WHERE discord_id = ?", (user_id,))
    row = cursor.fetchone()

    if row:
        return row[0]
    return 0

def update_user_score(user_id, amount):
    cursor = db_connection.cursor()
    cursor.execute("UPDATE users SET score_points = score_points + ? WHERE discord_id = ?", (amount, user_id))
    db_connection.commit()

async def casino(ctx, game, bet):

    user_id = ctx.author.id
    score_points = await get_user_score(user_id)

    try:
        if game is None and bet is None:
            casino_help = discord.Embed(
                title="Вітаю у куточку гемблінгу. Тут ти можеш випробувати свою удачу)",
                description=
                "**.casino <game_name> <bet>** - Основна команда, що викликає певну гру `<game_name>` із вказаною ставкою `<bet>`\n\n"
                "\n**ІГРИ**\n"
                """
                **slot** - Слоти :slot_machine: Крути барабани щоб отримати вийграшку комбінацію символів!
                
                **КОМБІНАЦІЇ:**
                
                :seven::seven::seven: - x20
                
                :gem::gem::gem: - x10
                
                :lemon::lemon::lemon: - x5
                
                :grapes::grapes::grapes: - x3
                
                :cherries::cherries::cherries: - x2
                
                :lemon::lemon::cherries: - x1\n
                """
                """
                **roulette** - Рулетка :black_circle: :red_circle: . Вгадай який колір випаде наступним!
                
                **КОЛЬОРИ:**
                
                :black_circle: - x2
                
                :red_circle: - x2
                
                :green_circle: - x14
                """,
                color=discord.Color.blurple()
            )
            await ctx.send(embed=casino_help)
        elif game == "slot" and bet is not None:
            if bet <= 0:
                await ctx.send("Ставка повинна бути більшою за нуль.")
            elif score_points < bet:
                await ctx.send("Ваш баланс замалий для такої ставки")
            else:
                await slots_game(ctx, bet)
        elif game == "roulette" and bet is not None:
            if bet <= 0:
                await ctx.send("Ставка повинна бути більшою за нуль.")
            elif score_points < bet:
                await ctx.send("Ваш баланс замалий для такої ставки")
            else:
                await roulette_game(ctx, bet)
    except:
        await ctx.send("Ви вказали неправильне значення для гри або ставки")


active_users = {}

async def check_if_active(ctx):
    user_id = ctx.author.id

    if user_id in active_users:
        await ctx.send("Ви вже граєте, почекайте, поки гра закінчиться!")
        return False

    active_users[user_id] = True

    return True


async def slots_game(ctx, bet: int):
    if not await check_if_active(ctx):
        return

    symbols = ["🍒", "🍋", "🍇", "💎", "7️⃣"]
    weights = [50, 30, 10, 5, 5]
    slots = ["", "", ""]


    def weighted_random(symbols, weights):
        return random.choices(symbols, weights, k=1)[0]


    def check_win(slots):
        if slots[0] == slots[1] == slots[2]:
            if slots[0] == "7️⃣":
                update_user_score(ctx.author.id, bet * 20)
                return f"Виграш! {slots[0]} x20"
            elif slots[0] == "💎":
                update_user_score(ctx.author.id, bet * 10)
                return f"Виграш! {slots[0]} x10"
            elif slots[0] == "🍋":
                update_user_score(ctx.author.id, bet * 5)
                return f"Виграш! {slots[0]} x5"
            elif slots[0] == "🍇":
                update_user_score(ctx.author.id, bet * 3)
                return f"Виграш! {slots[0]} x3"
            elif slots[0] == "🍒":
                update_user_score(ctx.author.id, bet * 2)
                return f"Виграш! {slots[0]} x2"
        elif slots.count("🍒") == 1 and len(set(slots)) == 2:
            return f"Виграш! 🍒 дає x1"
        else:
            cursor = db_connection.cursor()
            cursor.execute("UPDATE users SET score_points = score_points - ? WHERE discord_id = ?",
                           (bet, ctx.author.id))
            db_connection.commit()
            return f"Немає виграшу"

    message = await ctx.channel.send("🎰 Обертання слотів...")

    num_spins = 4
    final_result = []

    for _ in range(num_spins):
        for i in range(len(slots)):
            slots[i] = random.choice(symbols)
        await message.edit(content=f"🎰 {' | '.join(slots)}")
        await asyncio.sleep(0.3)

    final_result = [weighted_random(symbols, weights) for _ in range(3)]
    result = check_win(final_result)

    score_points = await get_user_score(ctx.author.id)
    await message.edit(content=f"🎰 Результат: {' | '.join(final_result)}\n{result + " | Ваш баланс - "}{score_points}")

    await asyncio.sleep(1.55)
    del active_users[ctx.author.id]


class ColorButtons(View):
    def __init__(self, author_id):
        super().__init__()
        self.value = None
        self.author_id = author_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            return False
        return True


    @discord.ui.button(label="⚫ Black", style=discord.ButtonStyle.primary)
    async def black_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.result = "⚫"
        await interaction.response.send_message(f"Ви обрали {self.result}. Рулетка обертається...")
        self.stop()

    @discord.ui.button(label="🔴 Red", style=discord.ButtonStyle.primary)
    async def red_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.result = "🔴"
        await interaction.response.send_message(f"Ви обрали {self.result}. Рулетка обертається...")
        self.stop()

    @discord.ui.button(label="🟢 Green", style=discord.ButtonStyle.primary)
    async def green_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.result = "🟢"
        await interaction.response.send_message(f"Ви обрали {self.result}. Рулетка обертається...")
        self.stop()


async def roulette_game(ctx, bet: int):
    if not await check_if_active(ctx):
        return

    view = ColorButtons(author_id=ctx.author.id)

    embed = discord.Embed(title="На який колір поставиш?")
    await ctx.channel.send(embed=embed, view=view)

    await view.wait()

    if view.result is None:
        await ctx.send("Час вибору закінчився. Спробуйте ще раз.")
        return


    symbols = ["⚫", "🔴", "🟢"]
    weights = [50, 50, 10]

    def weighted_random(symbols, weights):
        return random.choices(symbols, weights, k=1)[0]

    result = weighted_random(symbols, weights)

    green_gifs = [os.path.join(BASE_DIR, "assets", "Roulette_wheel_green.gif")]
    red_gifs = [os.path.join(BASE_DIR, "assets", 'Roulette_wheel_red_1.gif'), os.path.join(BASE_DIR, "assets", 'Roulette_wheel_red_2.gif'), os.path.join(BASE_DIR, "assets", 'Roulette_wheel_red_3.gif')]
    black_gifs = [os.path.join(BASE_DIR, "assets", 'Roulette_wheel_black_1.gif'), os.path.join(BASE_DIR, "assets", 'Roulette_wheel_black_2.gif'), os.path.join(BASE_DIR, "assets", 'Roulette_wheel_black_3.gif')]

    def get_random_gif(result):
        if result == "🟢":
            return random.choice(green_gifs)
        elif result == "🔴":
            return random.choice(red_gifs)
        elif result == "⚫":
            return random.choice(black_gifs)
        else:
            return None

    def check_win(result):
        if view.result == result:
            if result == "⚫" or "🔴":
                update_user_score(ctx.author.id, bet * 2)
                return f"Виграш! {result} x2"
            elif result == "🟢":
                update_user_score(ctx.author.id, bet * 14)
                return f"Виграш! {result} x14"
        else:
            cursor = db_connection.cursor()
            cursor.execute("UPDATE users SET score_points = score_points - ? WHERE discord_id = ?",
                           (bet, ctx.author.id))
            db_connection.commit()
            return f"Нажаль ви помилились. Кулька випала на {result}"


    gif_path = get_random_gif(result)

    try:
        await ctx.send("",file=discord.File(gif_path))

        await asyncio.sleep(5.3)

        res_message = check_win(result)

        score_points = await get_user_score(ctx.author.id)
        await ctx.send(f"🎲 Результат: {res_message} | Ваш баланс - {score_points}")

    except Exception as e:
        await ctx.send(e)


    await asyncio.sleep(1.55)
    del active_users[ctx.author.id]
