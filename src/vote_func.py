import discord
import asyncio
import re
from discord import Embed


async def vote(message, bot, author_id):

    try:
        create_message = await message.channel.send("Creating a new poll...")
        create_message_name = await message.channel.send("Enter name of vote")
        name = await bot.wait_for('message', check=lambda message: message.author.id == author_id, timeout=120)

        create_message_option = await message.channel.send("Enter variants vote (space)")
        options = await bot.wait_for('message', check=lambda message: message.author.id == author_id, timeout=120)

        create_message_duration = await message.channel.send("Enter duration (e.g., 5 minutes, 2 hours, 3 days, 1 week)")
        duration = await bot.wait_for('message', check=lambda message: message.author.id == author_id, timeout=120)

        duration_text = duration.content.lower()
        duration_value = int(re.search(r'\d+', duration_text).group())
        duration_unit = re.search(r'\b[a-zA-Z]+\b', duration_text).group()

        duration_time = 10

        if duration_unit == 'minutes':
            duration_time = duration_value * 60
        elif duration_unit == 'hours':
            duration_time = (duration_value * 60) * 60
        elif duration_unit == 'days':
            duration_time = ((duration_value * 60) * 60) * 24
        elif duration_unit == 'week':
            duration_time = (((duration_value * 60) * 60) * 24) * 7

        messages_to_delete = [create_message, message, name, create_message_name, options, create_message_option,
                              duration, create_message_duration]

        reactions = [option.strip() for option in options.content.split(' ')]
        allowed_reactions = reactions.copy()

        results = {reaction: 0 for reaction in reactions}

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
