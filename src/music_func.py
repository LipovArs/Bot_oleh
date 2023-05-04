import os
import youtube_dl
import asyncio
from discord import FFmpegPCMAudio
from discord import utils
from discord.ext import commands
from typing import List
import asyncio


songs = []
skip_current = False


async def play(message):
    if message.author.voice is None:
        await message.channel.send("You are not in a voice channel!")
        return
    if message.guild.voice_client and message.author.voice.channel != message.guild.voice_client.channel:
        await message.channel.send("I'm already playing music in another channel!")
        return
    channel = message.author.voice.channel
    url = message.content.split(' ')[1]

    if message.guild.voice_client is not None:
        await message.guild.voice_client.move_to(channel)
    else:
        voice = await channel.connect()

    ydl_opts = {
        'format': 'bestaudio/best',
        'extract_flat': 'in_playlist',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    if 'playlist' in url:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            playlist_dict = ydl.extract_info(url, download=False)
            for video in playlist_dict['entries']:
                title = video.get('title', None)
                duration = video.get('duration', None)
                video_url = video.get('url', None)
                if video_url:
                    songs.append({'url': video_url, 'title': title, 'duration': duration})
        await message.channel.send(f"Added playlist to the queue.")
    elif '?list=' in url and 'playlist' not in url:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            playlist_dict = ydl.extract_info(url, download=False)
            for video in playlist_dict['entries']:
                title = video.get('title', None)
                duration = video.get('duration', None)
                video_url = video.get('url', None)
                if video_url:
                    songs.append({'url': video_url, 'title': title, 'duration': duration})
        await message.channel.send(f"Added playlist to the queue.")
    else:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            title = info_dict.get('title', None)
            duration = info_dict.get('duration', None)
            songs.append({'url': url, 'title': title, 'duration': duration})
        await message.channel.send(f"Added {title} to the queue.")

    if not message.guild.voice_client.is_playing():
        await play_song(message)


async def skip(message):
    if message.author.voice is None:
        await message.channel.send("You are not in a voice channel!")
        return
    if message.guild.voice_client is None:
        await message.channel.send("I'm not in a voice channel!")
        return
    if message.author.voice.channel != message.guild.voice_client.channel:
        await message.channel.send("You must to be is same channel with me!")
        return
    if message.guild.voice_client is None or not message.guild.voice_client.is_playing():
        await message.channel.send("Nothing to skip!")
        return
    if message.guild.voice_client.is_paused():
        pass
    elif not message.guild.voice_client.is_playing():
        await message.channel.send("I am not playing anything right now.")
        return

    message.guild.voice_client.stop()
    await message.channel.send("Skipping...")


async def leave(message):
    if message.author.voice is None:
        await message.channel.send("You are not in a voice channel!")
        return
    if message.guild.voice_client is None:
        await message.channel.send("I'm not in a voice channel!")
        return
    if message.author.voice.channel != message.guild.voice_client.channel:
        await message.channel.send("You must to be is same channel with me!")
        return
    message.guild.voice_client.stop()
    await message.guild.voice_client.disconnect()
    songs.clear()
    await message.channel.send("Disconnected")


async def queue(message):
    queue_list = ""
    for i, song in enumerate(songs):
        queue_list += f"{i + 1}. {song['title']} ({song['duration']}s)\n"
    await message.channel.send(f"Current Queue:\n{queue_list}")


async def pause(message):
    if message.author.voice is None:
        await message.channel.send("You are not in a voice channel!")
        return
    if message.guild.voice_client is None:
        await message.channel.send("I'm not in a voice channel!")
        return
    if message.author.voice.channel != message.guild.voice_client.channel:
        await message.channel.send("You must to be is same channel with me!")
        return
    if not message.guild.voice_client.is_playing():
        await message.channel.send("I am not playing anything right now.")
        return
    else:
        message.guild.voice_client.pause()
        await message.channel.send('Pause the music.')


async def resume(message):
    if message.author.voice is None:
        await message.channel.send("You are not in a voice channel!")
        return
    if message.guild.voice_client is None:
        await message.channel.send("I'm not in a voice channel!")
        return
    if message.author.voice.channel != message.guild.voice_client.channel:
        await message.channel.send("You must to be is same channel with me!")
        return
    if message.guild.voice_client.is_playing():
        await message.channel.send("I am playing right now.")
        return
    else:
        message.guild.voice_client.resume()
        await message.channel.send('Resume the music.')


async def play_song(message):
    global skip_current

    if len(songs) > 0:
        song = songs.pop(0)
        song_url = song["url"]
        song_title = song['title']

        ydl_opts = {
            'format': 'bestaudio/best',
            'extractor_retries': 'auto',
            'extract_flat': False,
            'extract_playlist': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        ffmpg_opts = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }

        if message.guild.voice_client and message.guild.voice_client.is_playing():
            await message.channel.send("Already playing song")
            return
        else:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(song_url, download=False)
                URL = info['formats'][0]['url']
            if message.guild.voice_client is None:
                return
            message.guild.voice_client.play(FFmpegPCMAudio(URL, **ffmpg_opts))
            message.guild.voice_client.is_playing()
            await message.channel.send(f"Playing {song_title}")
            while message.guild.voice_client and (message.guild.voice_client.is_playing() or message.guild.voice_client.is_paused()):
                await asyncio.sleep(1)

            if not skip_current and len(songs) > 0 and message.guild.voice_client:
                await message.channel.send("Playing next song...")
                await play_song(message)
            else:
                skip_current = False
                await asyncio.sleep(300)
                await message.guild.voice_client.disconnect()
                await message.channel.send("Disconnected")
    else:
        await message.channel.send("Queue is empty")

