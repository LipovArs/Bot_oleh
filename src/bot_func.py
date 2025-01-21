import message_control
from discord.ext.commands import DefaultHelpCommand

import discord

class CustomHelpCommand(DefaultHelpCommand):
    async def send_bot_help(self, mapping):
        ctx = self.context
        user_is_admin = ctx.author.guild_permissions.administrator

        help_message = discord.Embed(
            title=f'Ось деяка інформація про бота:',
            description=
            "**.stats** - Отримати статистику активності сервера\n\n"
            "**.play <url>** - Відтворення музики\n\n"
            "**.pause** - Поставити трек на паузу\n\n"
            "**.resume** - Відновити трек\n\n"
            "**.skip** - Пропустити трек\n\n"
            "**.stop** - Зупинка треку\n\n"
            "**.leave** - Вихід бота з голосового каналу\n\n"
            "**.queue** - Отримання черги треків\n\n"
            "**.vote** - Почати голосування\n\n"
            "**.top_voice_users** - Вивести топ користувачів за часом у голосових каналах\n\n"
            "**.balance** - Переглянути свій баланс\n\n"
            "**.casino** - Потрапити в чарівний GAMBLE-світ",
            color=discord.Color.dark_grey()
        )

        admin_tip = discord.Embed(
            title=f'Щоб переглянути команди адміністратора -.help_admin',
            color=discord.Color.dark_gold()
        )

        if not user_is_admin:
            await ctx.send(embed = help_message)
        else:
            await ctx.send(embeds = [help_message, admin_tip])



async def help_admin(ctx):
    admin_command = discord.Embed(
        title=f'Ось команди лише для адміністратора:',
        description=
        "**.check_all_ban_words** - Отримайте всі заборонені слова на цьому сервері\n\n"
        "**.inf <nickname>** - Отримання інформації про учасників сервера\n\n"
        "**.collect_user_info** - Збереження/оновлення інформації про користувачів в базу даних\n\n"
        """
        **.get_message_log** - Показує лог видалених або змінених повідомлень з певними фільтрами.

        **Використання:**

        `.get_message_log <user_name> <time_period>`

    - `<user_name>`: (необов'язково) Ім'я користувача для фільтрації.
    - `<time_period>`: (необов'язково) Період часу для фільтрації:
    - **all** - Усі повідомлення.
    - **last day** - Повідомлення за останній день.
    - **last week** - Повідомлення за останній тиждень.
    - **last month** - Повідомлення за останній місяць.

        **Приклад використання:**

    - `.get_message_log all` — Показує всі повідомлення.
    - `.get_message_log user last day` — Показує повідомлення користувача `user` за останній день.
    - `.get_message_log all last month` — Показує всі повідомлення за останній місяць.
        """'\n\n',
        color=discord.Color.dark_gold()
    )
    await ctx.send(embed = admin_command)

def message_view(msg, roles):
    return message_control.check(msg, roles)


def stat_msg(message):
    members = message.guild.members
    activities = {}
    for member in members:
        for activity in member.activities:
            if activity.type == discord.ActivityType.playing:
                game_name = activity.name
                member_nick = member.nick or member.name
                activities[f"{member_nick} - {game_name}"] = ''
            elif activity.type == discord.ActivityType.listening:
                listen_name = activity.name
                member_nick = member.nick or member.name
                activities[f"{member_nick} - {listen_name}"] = ''

    output = "Activity Stats:\n"
    formatted_activities = "\n".join(f"{key} {value}" for key, value in activities.items())

    res = output + formatted_activities

    return res


async def user_info(ctx):
    moderator_role = discord.utils.get(ctx.guild.roles, name='Moderator')
    if ctx.author.guild_permissions.administrator or moderator_role in ctx.author.roles:
        user_input = ctx.message.content
        parts = user_input.split()
        if parts[0] == '.inf':
            user_input_processed = ' '.join(parts[:1] + [part.replace(' ', '_') for part in parts[1:]])
            user_input_processed = user_input_processed.replace('.inf_', '.inf ')
            parts_processed = user_input_processed.split()
            user_enter_nick = " ".join(parts_processed[1:])
            if len(parts_processed) < 2:
                await ctx.channel.send('Недостатньо аргументів.')
            else:
                guild = ctx.guild
                users_found = []
                for member in guild.members:
                    if member.nick == user_enter_nick or member.name == user_enter_nick:
                        users_found.append(member)
                if users_found:
                    for user in users_found:
                        user_name = user.nick or user.name
                        if not user_name:
                            user_name = user.name or user.nick
                        user_role = str([role.name for role in user.roles if role.id != 1026612675830099988])
                        joined_at = user.joined_at
                        user_avatar_url = None
                        created_at = user.created_at
                        user_id = user.id
                        try:
                            if not user.avatar.url == 'NoneType':
                                user_avatar_url = user.avatar.url
                        except:
                            print("None Avatar")
                        await ctx.channel.send(
                            f"User - {user}\nNick - {user_name}\nID - {user_id}\nRoles - {user_role}\nJoined at - {joined_at}\n" +
                            f"Created at - {created_at}\nAvatar URL - {user_avatar_url}")
                else:
                    await ctx.channel.send('Користувача не знайдено. Спробуйте ввести User name користувача, якщо його Nickname має нестандартний шрифт.')
    else:
        await ctx.channel.send("В вас недостатньо прав.")
