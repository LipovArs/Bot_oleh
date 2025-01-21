import discord
import asyncio
import re


async def vote(message, bot, author_id):

    try:
        await message.channel.send("Стрворення нового голосування...")
        await message.channel.send("Введіть назву голосування")
        name = await bot.wait_for('message', check=lambda message: message.author.id == author_id, timeout=120)

        await message.channel.send("Введіть варіанти відповіді (тільки смайлами, через пробіл)")
        options = await bot.wait_for('message', check=lambda message: message.author.id == author_id, timeout=120)

        await message.channel.send("Введіть тривалісь (5 min - (5 хвилин), 2 h - (2 години), 3 d - (3 дні), 1 w - (1 тиждень)")
        duration = await bot.wait_for('message', check=lambda message: message.author.id == author_id, timeout=120)

        duration_text = duration.content.lower()
        duration_value = int(re.search(r'\d+', duration_text).group())
        duration_unit = re.search(r'\b[a-zA-Z]+\b', duration_text).group()

        duration_time = 10

        if duration_unit == 'minu':
            duration_time = duration_value * 60
        elif duration_unit == 'h':
            duration_time = (duration_value * 60) * 60
        elif duration_unit == 'd':
            duration_time = ((duration_value * 60) * 60) * 24
        elif duration_unit == 'w':
            duration_time = (((duration_value * 60) * 60) * 24) * 7

        reactions = [option.strip() for option in options.content.split(' ')]
        allowed_reactions = reactions.copy()

        results = {reaction: 0 for reaction in reactions}

        messages_to_delete = [msg async for msg in message.channel.history(limit=8)]

        for msg in messages_to_delete:
            await msg.delete()
            await asyncio.sleep(0.3)

        embed = discord.Embed(
            title=f'Голосування: {name.content}',
            description=f'Час на відповідь ({duration_text})\nВиберіть один з варіантів нижче:',
            color=discord.Color.dark_green()
        )

        vote_message = await message.channel.send(content='@everyone', embed=embed)

        await vote_message.channel.set_permissions(bot.user, add_reactions=True)

        for reaction in reactions:
            await vote_message.add_reaction(reaction)

        while True:
            try:
                reaction, user = await bot.wait_for('reaction_add', check=lambda r, u: u != bot.user and str(
                    r.emoji) in allowed_reactions, timeout=duration_time)
                results[str(reaction.emoji)] += 1
            except asyncio.TimeoutError:
                break

        results_message = '\n'.join([f'{option}: {results[option]}' for option in reactions])
        await message.channel.send(f'Голосування ({name.content}) закрите. Вибір користувачів:\n{results_message}')
        winner = max(results, key=lambda x: results[x])

        draw = False

        max_votes = results[winner]
        for option, votes in results.items():
            if votes == max_votes and option != winner:
                draw = True
                break

        if draw:
            await message.channel.send("Ой-ой... Схоже голосування закінчилось нічиєю.")
        else:
            await message.channel.send(f"Результат голосування: {winner}")

    except asyncio.TimeoutError:
        await message.channel.send(f"TIMEOUT")
