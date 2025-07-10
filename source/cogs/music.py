import asyncio
import re
from urllib import parse, request

import discord
from discord import Embed, Member
from discord.app_commands import guild_install, guild_only
from discord.ext import commands
from discord.ext.commands import hybrid_command
from yt_dlp import YoutubeDL

from source.classes.jsonDB import db


class MusicCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.YOUTUBE_DL_OPTIONS = {'format': 'bestaudio/best',
                                   'postprocessors': [{
                                        'key': 'FFmpegExtractAudio',
                                        'preferredcodec': 'mp3',
                                        'preferredquality': '192',
                                         }],
                                   }
        self.FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}

        self.embedBlue = 0x2c76dd
        self.embedRed = 0xdf1141
        self.embedGreen = 0x0eaa51

        self.vc = {}

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            print("BOT IS RUNNINGGG")
            guild_id: int = guild.id
            self.vc[guild_id] = None

    @commands.Cog.listener()
    async def on_voice_state_update(self,
                                    member: discord.Member,
                                    before: discord.VoiceState,
                                    after: discord.VoiceState):
        guild_id = member.guild.id
        if self.vc[guild_id] is not None:
            if self.bot.user.id not in [m.id for m in before.channel.members]:
                db.clear_queue(member.guild)
                self.vc[guild_id] = None
            if len(before.channel.members) == 1 and before.channel.members[0].id == self.bot.user.id:
                db.clear_queue(member.guild)
                await before.send(embed=Embed(title=f"Leaving {before.channel.name}...",
                                             description="Every member left the channel, the queue has been cleared",
                                             color=0x000000))
                return await self.vc[guild_id].disconnect()


    def now_playing_embed(self,
                          ctx: commands.Context,
                          song: dict) -> Embed:
        title = song['title']
        link = song['link']
        thumbnail = song['thumbnail']
        author: Member = song['user']
        avatar = author.avatar.url

        embed = discord.Embed(
            title="Now Playing",
            description=f'[{title}]({link})',
            colour=self.embedBlue,
        )
        embed.set_thumbnail(url=thumbnail)
        embed.set_footer(text=f'Song added by: {str(author)}', icon_url=avatar)
        return embed

    def added_song_embed(self,
                         ctx: commands.Context,
                         song: dict) -> Embed:
        title = song['title']
        link = song['link']
        thumbnail = song['thumbnail']
        author = song['user']
        avatar = author.avatar.url

        embed = Embed(
            title="Song Added To Queue!",
            description=f'[{title}]({link})',
            colour=self.embedRed,
        )
        embed.set_thumbnail(url=thumbnail)
        embed.set_footer(text=f'Song added by: {str(author)}', icon_url=avatar)
        return embed

    def removed_song_embed(self,
                           ctx: commands.Context,
                           song: dict) -> Embed:
        title = song['title']
        link = song['link']
        thumbnail = song['thumbnail']
        author = song['user']
        avatar = author.avatar.url

        embed = Embed(
            title="Song removed from queue!",
            description=f'[{title}]({link})',
            colour=self.embedRed,
        )
        embed.set_thumbnail(url=thumbnail)
        embed.set_footer(
            text=f'Song removed by: {str(author)}', icon_url=avatar)
        return embed

    async def join_VC(self,
                      ctx: commands.Context,
                      channel: discord.VoiceChannel):
        guild_id: int = ctx.guild.id
        if self.vc[guild_id] is None or not self.vc[guild_id].is_connected():
            try:
                await channel.connect(self_deaf=True)
            except (TimeoutError, discord.ClientException):
                return await ctx.send("Could not connect to the voice channel.")
            self.vc[guild_id] = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
            return True
        else:
            return await ctx.interaction.response.send_message("I am already connected to a voice channel...")

    def extract_YT(self,
                   search: str,
                   user: Member) -> dict:
        if not search.startswith("https://youtube.com/watch?v="):
            queryString = parse.urlencode({'search_query': search})
            html_content = request.urlopen(
                'http://www.youtube.com/results?' + queryString)
            search_results: list = re.findall(r'/watch\?v=(.{11})', html_content.read().decode())
            url = search_results[0]
        else:
            url = search
        with YoutubeDL(self.YOUTUBE_DL_OPTIONS) as ydl:
            try:
                info: dict = ydl.extract_info(url, download=False)
            except ExtractorError as e:
                print(e)
        return {
            'link': 'https://www.youtube.com/watch?v=' + url,
            'thumbnail': 'https://i.ytimg.com/vi/' + url + '/hqdefault.jpg?sqp=-oaymwEcCOADEI4CSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLD5uL4xKN-IUfez6KIW_j5y70mlig',
            'source': info.get('url', None),
            'title': info.get('title', None),
            'user': user
        }

    def play_next(self,
                  ctx: commands.Context) -> None:
        guild_id = ctx.guild.id
        db.remove_queue(ctx.guild)

        if not self.vc[guild_id].is_playing():
            return None

        if 1 < len(db.get_queue(ctx.guild)):
            song = db.get_queue(ctx.guild)[0]
            message = self.now_playing_embed(ctx, song)
            coro = ctx.send(embed=message)
            asyncio.run_coroutine_threadsafe(coro, self.bot.loop)

            self.vc[guild_id].play(discord.FFmpegPCMAudio(
                song['source'], **self.FFMPEG_OPTIONS), after=lambda e: self.play_next(ctx))
            print(song['source'])
        else:
            db.clear_queue(ctx.guild)

    async def play_music(self,
                         ctx: commands.Context) -> None:
        guild_id = ctx.guild.id
        if 0 < len(db.get_queue(ctx.guild)):

            if self.vc[guild_id] is None:
                await self.join_VC(ctx, ctx.author.voice.channel)

            song = db.get_queue(ctx.guild)[0]
            message = self.now_playing_embed(ctx, song)
            await ctx.send(embed=message)

            self.vc[guild_id].play(discord.FFmpegPCMAudio(
                song['source'], **self.FFMPEG_OPTIONS), after=lambda e: self.play_next(ctx))
        else:
            await ctx.send("There are no songs in the queue to be played.")

    @commands.command(
        name="play",
        description="Plays the audio of a specified YouTube video",
        aliases=["p"]
    )
    @commands.guild_only()
    async def pl(self,
                   ctx: commands.Context,
                   *args: str):
        print("aaaaaaaaaaa")
        search = " ".join(args)
        guild_id = ctx.guild.id
        try:
            userChannel = ctx.author.voice.channel
        except AttributeError:
            return await ctx.send("You must be connected to a voice channel.")
        if not args:
            await ctx.send("Please input a song, along with its artist for more accuracy with the command.")
        else:
            song = self.extract_YT(search)
            if type(song) == type(True):
                await ctx.send("Could not download the song. Incorrect format, try some different keywords.")
            else:

                db.set_queue(ctx.guild, song)
                if self.vc[guild_id] is None:
                    await self.join_VC(ctx, userChannel)
                if not self.vc[guild_id].is_playing():
                    await self.play_music(ctx)
                else:
                    message = self.added_song_embed(ctx, song)
                    await ctx.send(embed=message)

    @hybrid_command(
        name="pause",
        description="Pauses the current song being played"
    )
    @guild_install()
    @guild_only()
    async def pause(self,
                    ctx: commands.Context) -> None:
        guild_id = ctx.guild.id
        if not self.vc[guild_id]:
            await ctx.send("You are not in a voice channel.")
        if self.vc[guild_id].is_playing():
            self.vc[guild_id].pause()
            await ctx.send("Audio paused!")
        else:
            await ctx.send("There is no audio to be paused at the moment.")

    @hybrid_command(
        name="resume",
        aliases=["re", "r"],
        description="Resumes a paused song"
    )
    @guild_install()
    @guild_only()
    async def resume(self,
                     ctx: commands.Context) -> None:
        id = ctx.guild.id
        if not self.vc[id]:
            await ctx.send("There is no audio to be played at the moment.")
        elif self.vc[id].is_paused():
            await ctx.send("The audio is now playing!")
            self.vc[id].resume()


    @hybrid_command(
        name="skip",
        aliases=["sk", "s"],
        description="Skips to the next song in the queue."
    )
    @guild_install()
    @guild_only()
    async def skip(self,
                   ctx: commands.Context):
        guild_id = ctx.guild.id
        try:
            user_channel = ctx.author.voice.channel
        except AttributeError:
            return await ctx.send("You need to be in a VC to use this command.")
        if self.vc[guild_id] is None:
            return await ctx.send("Hoshiko is not in VC.")
        if user_channel == self.vc[guild_id].channel:
            self.vc[guild_id].pause()
            db.remove_queue(ctx.guild)
            await ctx.send(embed=Embed(description="The song was skipped."))
            await self.play_music(ctx)

    @hybrid_command(
        name="queue",
        aliases=["list", "q"],
        description="Lists the next few songs in the queue."
    )
    @guild_install()
    @guild_only()
    async def queue(self,
                    ctx: commands.Context) -> None:
        guild_id = ctx.guild.id
        return_value = ""
        if not db.get_queue(ctx.guild):
            await ctx.send("There are no songs in the queue.")
            return None

        for i in range(0, len(db.get_queue(ctx.guild))):
            up_next_songs = len(db.get_queue(ctx.guild))
            if i > 5 + up_next_songs:
                break
            return_index = i
            if return_index == 0:
                return_index = "Playing"
            elif return_index == 1:
                return_index = "Next"
            return_value += f"{return_index} - [{db.get_queue(ctx.guild)[i]['title']}]({db.get_queue(ctx.guild)[i]['link']})\n"

            if return_value == "":
                await ctx.send("There are no songs in the queue.")
                return None

        queue = discord.Embed(
            title="Current Queue",
            description=return_value,
            colour=self.embedGreen
        )
        await ctx.send(embed=queue)

    @hybrid_command(
        name="clear",
        aliases=["cl"],
        description="Clears all of the songs from the queue"
    )
    @guild_install()
    @guild_only()
    async def clear(self,
                    ctx: commands.Context) -> None:
        guild_id = ctx.guild.id
        if self.vc[guild_id] is not None and self.vc[guild_id].is_playing():
            self.vc[guild_id].stop()
        if db.get_queue(ctx.guild):
            await ctx.send("The music queue has been cleared.")
            db.clear_queue(ctx.guild)
        else:
            await ctx.send("There is no songs to clear.")

    @hybrid_command(
        name="join",
        aliases=["j"],
        description="Connects Hoshiko to the voice channel"
    )
    @guild_install()
    @guild_only()
    async def join(self,
                   ctx: commands.Context) -> None:
        if ctx.author.voice:
            if self.vc[ctx.guild.id] is not None and self.vc[ctx.guild.id].is_connected():
                return await ctx.send("Hoshiko is already connected to a voice channel.")
            user_channel: discord.VoiceChannel = ctx.author.voice.channel
            await self.join_VC(ctx, user_channel)
            await ctx.send(f'Hoshiko has joined {user_channel}')
        else:
            await ctx.send("You need to be connected to a voice channel.")

    @hybrid_command(
        name="leave",
        aliases=["l", "stop"],
        description="Removes Hoshiko from the voice channel and clears the queue"
    )
    @guild_install()
    @guild_only()
    async def leave(self,
                    ctx: commands.Context) -> None:
        guild_id = ctx.guild.id
        db.clear_queue(ctx.guild)

        if self.vc[guild_id] is not None:
            await ctx.send("Hoshiko has left the channel.")
            await self.vc[guild_id].disconnect()
            self.vc[guild_id] = None
        else:
            await ctx.send("Hoshiko is not in a voice channel.")

async def setup(bot: commands.Bot):
    await bot.add_cog(MusicCog(bot))