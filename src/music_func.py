import discord
import yt_dlp as youtube_dl
import asyncio

song_queue = []

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'playlist_items': '0-5',
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn -filter:a "volume=0.25"'}



ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.duration = data.get('duration')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False, play=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None,
                                          lambda: ytdl.extract_info(url, download=not stream or play))

        if 'entries' in data:  # Якщо це плейлист
            return [
                cls(discord.FFmpegPCMAudio(entry['url'], **ffmpeg_options), data=entry)
                for entry in data['entries']
            ]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return [cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)]


async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected() and ctx.author.voice:
        await voice_client.disconnect()
    else:
        await ctx.send(f"{ctx.author} Ти або я не приєднані до голосового чату")


async def play(ctx, *, url: str):
    global song_queue
    voice = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
    try:
        if not voice:
            if not ctx.message.author.voice:
                await ctx.send(f"{ctx.message.author.name} is not connected to a voice channel")
                return
            channel = ctx.message.author.voice.channel
            await channel.connect()

        voice_client = ctx.guild.voice_client

        players = await YTDLSource.from_url(url, loop=ctx.bot.loop, stream=True)

        if not voice_client.is_playing():
            song_queue.extend(players)
            await start_playing(ctx)
        else:
            song_queue.extend(players)
            await ctx.send(f"**Queued {len(players)} songs from playlist:**")
            for i, player in enumerate(players, start=1):
                await ctx.send(f"{i}. {player.title}")
    except Exception as e:
        await ctx.send(f"Error occurred: {e}")


async def start_playing(ctx):
    global song_queue
    if not song_queue:
        await ctx.send("Queue is empty.")
        return

    def after_playing(error):
        if error:
            print(f"Player error: {error}")
        if song_queue:
            next_song = song_queue.pop(0)
            ctx.voice_client.play(next_song, after=lambda e: after_playing(e))
            asyncio.run_coroutine_threadsafe(
                ctx.send(f"**Now playing:** {next_song.title}"), asyncio.get_event_loop()
            )

    current_song = song_queue.pop(0)
    ctx.voice_client.play(current_song, after=lambda e: after_playing(e))
    await ctx.send(f"**Now playing:** {current_song.title}")



async def queued(ctx):
    global song_queue
    a = ""
    i = 0
    for f in song_queue:
        if i > 0:
            a = a + str(i) + ". " + f.title + "\n "
        i += 1
    await ctx.send("Queued songs: \n " + a)


async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing() and ctx.author.voice:
        await ctx.send("Paused playing.")
        await voice_client.pause()
    else:
        await ctx.send(f"{ctx.author} Ти або я не приєднані до голосового чату")


async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused() and ctx.author.voice:
        await ctx.send("Resumed playing.")
        await voice_client.resume()
    else:
        await ctx.send(f"{ctx.author} Ти або я не приєднані до голосового чату")


async def stop(ctx):
    global song_queue
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing() and ctx.author.voice:
        song_queue.clear()
        voice_client.stop()
        await ctx.send("Stopped playing.")
    else:
        await ctx.send(f"{ctx.author} Ти або я не приєднані до голосового чату")


async def skip(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing() and ctx.author.voice:
        voice_client.stop()
        await ctx.send("Skipped song.")
    else:
        await ctx.send(f"{ctx.author} Ти або я не приєднані до голосового чату")
