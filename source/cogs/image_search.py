from json import JSONDecodeError
from source.classes.jsonDB import db
import requests
from bs4 import BeautifulSoup
from discord.app_commands import describe, allowed_installs
from discord.ext import commands
from discord.ext.commands import hybrid_command
from discord import Embed, ClientUser
from source.formatting.settings import embed_class
from booru.client import safebooru, rule34
from random import randint
from typing import Optional


class SearchCog(commands.Cog):
    def __init__(self,
                 bot: commands.Bot):
        self.bot = bot
        self.description = "This is all the image search commands."


    @hybrid_command(name="blue_archive",
                    description="Searches an image on safebooru with your blue archive character.")
    @describe(character="BA character")
    async def blue_archive(self,
                           ctx: commands.Context,
                           character: str):
        safebooru_api = safebooru.Safebooru()
        try:
            pics = await safebooru_api.search_image(query=character.lower()+"_(blue_archive) 1girl absurdres")
        except Exception:
            try:
                pics = await safebooru_api.search_image(query=character.lower() + "_(blue_archive)")
            except Exception:
                await ctx.send("Sorry, I could not find any fanart, please try again.", ephemeral=True)
        e = Embed(title=f"Here's a fanart of {character.title()}",
                  color=0xFF0000)
        final_pics = list()
        for elem in pics.split('"'):
            if elem.startswith("https://"):
                final_pics.append(elem)
        e.set_image(url=final_pics[randint(0, len(final_pics)-1)])
        await ctx.send(embed=embed_class.EMBED_FORMAT(e, ctx.author))

    @hybrid_command(name="rule34",
                    description="Searches a post on R34")
    @describe(tags="Tags, separed by blank space",
              ai="If you want AI or not. False by default.")
    @commands.is_nsfw()
    @allowed_installs(guilds=True, users=True)
    async def rule34(self, ctx: commands.Context, tags: str, ai: Optional[bool]):
        #Doesn't work rn cuz R34 API is tweaking fr
        ai_gen = " -ai_generated " if not ai or ai is False else " ai_generated "
        bl = ''
        if type(ctx.author) == ClientUser:
            blacklist = db.get_user_blacklist(ctx.author)
            for elem in blacklist:
                bl += "-" + elem + " "
        response = requests.get(url="https://api.rule34.xxx/index.php?page=dapi&s=post&q=index",
                                 params={
                                     "limit": 25,
                                     "tags": tags + ai_gen + bl,
                                     "json": 1
                                 })
        try:
            pics = [elem for elem in response.json() if elem['score'] >= 1]
        except JSONDecodeError:
            return await ctx.send(
                "Could not find any image, maybe you misstyped a tag! Go to https://rule34.xxx/index.php?page=tags&s=list to find all the usable tags!",
                ephemeral=True)
        pic = pics[randint(0, len(pics)-1)]
        page = "https://rule34.xxx/index.php?page=post&s=view&id="+str(pic['id'])
        if pic['file_url'].endswith(".mp4"):
            await ctx.send(f"Source : <{page}>")
            return await ctx.send(pic['file_url'])
        embed = Embed(title="Click for the post.", url=page, color=0x00FF00)
        embed.set_image(url=pic['file_url'])
        embed = embed_class.EMBED_FORMAT(embed, ctx.author)
        await ctx.send(embed=embed)

    @hybrid_command(name="rule34_blacklist",
                    description="Blacklists tags from R34 search")
    @describe(tags="Tags, separed by blank space")
    @commands.is_nsfw()
    @allowed_installs(guilds=True, users=True)
    async def r34_bl(self, ctx: commands.Context, tags: str):
        current_bl = db.get_user_blacklist(ctx.author)
        while "-" in tags:
            tags.replace("-", "")
        bl = current_bl + tags.split()
        db.set_user_blacklist(ctx.author, bl)
        return ctx.send(f"Succesfully blacklisted : {tags} !")

    @hybrid_command(name="rule34_blacklist_remove",
                    description="Unblacklists tags from R34 search")
    @describe(tags="Tags, separed by blank space")
    @commands.is_nsfw()
    @allowed_installs(guilds=True, users=True)
    async def r34_bl_rm(self, ctx: commands.Context, tags: str):
        current_bl = db.get_user_blacklist(ctx.author)
        while "-" in tags:
            tags.replace("-", "")
        try:
            bl = current_bl - tags.split()
        except:
            return ctx.send("An error occured, the tags were not in the blacklist, or the command is broken, please retry when the dev has fixed it or when you get a brain!", ephemeral=True)
        db.set_user_blacklist(ctx.author, bl)
        return ctx.send(f"Succesfully removed from blacklist : {tags} !")


async def setup(bot: commands.Bot):
    await bot.add_cog(SearchCog(bot))
