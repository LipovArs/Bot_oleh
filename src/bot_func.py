import gaussian_sollution
import message_control
import discord
from discord import Game

CONTENT_WORDS = ["жид", "жиди", "жидо-бандерівець", "жидо-бандеравець", "жидобор", "жидо-бандера", "жидобандерівець",
                 "jid", "жидів", "жидами", "жида", "жидах", "жидом", "жиду", "жидам", "жиді", ";bl", ":bl", ";blb",
                 ":blb"]


def help_fun():
    """"Help function"""
    return 'Here is some help about bot\n' \
           '.check_all_ban_words - get all ban words on this server\n' \
           '.gauss - gaussian elimination\n' \
           '.stats - get activity stat of server\n' \
           '.inf - get info about server members (admin/moderator only)\n' \
           '.play - play music\n' \
           '.pause - pause the track\n' \
           '.resume - resume the track\n' \
           '.skip - skip track\n' \
           '.leave - stop playing music and leave bot from voice channel\n' \



def get_ban_words():
    return CONTENT_WORDS


def gaussian_method(msg):
    msg = msg.split(" ", 1)
    formula = msg[1]

    return gaussian_sollution.final_res(formula)


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


async def user_info(message):
    moderator_role = discord.utils.get(message.guild.roles, name='Moderator')
    if message.author.guild_permissions.administrator or moderator_role in message.author.roles:
        user_input = message.content
        parts = user_input.split()
        if parts[0] == '.inf':
            user_input_processed = ' '.join(parts[:1] + [part.replace(' ', '_') for part in parts[1:]])
            user_input_processed = user_input_processed.replace('.inf_', '.inf ')
            parts_processed = user_input_processed.split()
            user_enter_nick = " ".join(parts_processed[1:])
            if len(parts_processed) < 2:
                await message.channel.send('Недостатньо аргументів.')
            else:
                guild = message.guild
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
                        try:
                            if not user.avatar.url == 'NoneType':
                                user_avatar_url = user.avatar.url
                        except:
                            print("None Avatar")
                        await message.channel.send(
                            f"User - {user}\nNick - {user_name}\nRoles - {user_role}\nJoined at - {joined_at}\n" +
                            f"Created at - {created_at}\nAvatar URL - {user_avatar_url}")
                else:
                    await message.channel.send('Nope')
    else:
        await message.channel.send("В вас недостатньо прав.")
