from random import choice

from discord import User, Embed
from discord.app_commands import describe, user_install, guild_install, allowed_contexts
from discord.ext import commands
from discord.ext.commands import hybrid_command
from typing import Optional
import requests
from requests import Response

from source.formatting.settings import embed_class


class RPCog(commands.Cog):
    def __init__(self,
                 bot: commands.Bot):
        self.bot = bot
        self.description = "This is all commands related to SFW rp."

    @staticmethod
    def gif_maker(reaction: str):
        response: Response = requests.get(url=f"https://api.otakugifs.xyz/gif?reaction={reaction}")
        embed = Embed()
        embed.set_image(url=response.json()['url'])
        return embed

    @hybrid_command(name="hug",
                    description="Sends a hug gif/img")
    @describe(member="Member you want to hug")
    @allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def hug(self,
                  ctx: commands.Context,
                  member: Optional[User]):
        reaction = choice(["hug", "cuddle"])
        embed = self.gif_maker(reaction)
        embed.title = f"{ctx.author.name} is hugging someone!" if not member else f"{member.name}, {ctx.author.name} is hugging you! How cute! :3"
        message = member.mention if member else ""
        await ctx.send(content=message, embed=embed_class.EMBED_FORMAT(embed=embed, user=ctx.author))

    @hybrid_command(name="airkiss",
                    description="Sends a airkiss gif/img")
    @describe(member="Member you want to airkiss")
    @allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def airkiss(self,
                      ctx: commands.Context,
                      member: Optional[User]):
        embed = self.gif_maker("airkiss")
        embed.title = f"{ctx.author.name} is giving out a airkiss!" if not member else f"{member.name}, {ctx.author.name} is giving you a airkiss!"
        embed.description = "Quick! Someone catch it!" if not member else "Love is in the air it seems haha :3"
        message = member.mention if member else ""
        await ctx.send(content=message, embed=embed_class.EMBED_FORMAT(embed=embed, user=ctx.author))

    @hybrid_command(name="stare",
                    description="Sends a stare gif/img")
    @describe(member="Member you want to stare at")
    @allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def stare(self,
                    ctx: commands.Context,
                    member: Optional[User]):
        embed = self.gif_maker(choice(["stare", "angrystare"]))
        embed.title = f"{ctx.author.name} is staring at someone..." if not member else f"{member.name}, {ctx.author.name} staring at you..."
        embed.description = "Uh oh, hide everyone!" if not member else "Uh oh, you better apologize and pray for forgiveness..."
        message = member.mention if member else ""
        await ctx.send(content=message, embed=embed_class.EMBED_FORMAT(embed=embed, user=ctx.author))

    @hybrid_command(name="bite",
                    description="Sends a biting gif/img")
    @describe(member="Member you want to bite")
    @allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def bite(self,
                   ctx: commands.Context,
                   member: Optional[User]):
        embed = self.gif_maker("bite")
        embed.title = f"{ctx.author.name} is biting someone..?" if not member else f"{member.name}, {ctx.author.name} is biting you..?"
        embed.description = "Get bitten, you knucklehead :3" if not member else "Is that weird foreplay, or did you make them mad?"
        message = member.mention if member else ""
        await ctx.send(content=message, embed=embed_class.EMBED_FORMAT(embed=embed, user=ctx.author))

    @hybrid_command(name="blush",
                    description="Sends a blushing gif/img")
    @allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def blush(self,
                    ctx: commands.Context):
        embed = self.gif_maker("blush")
        embed.title = f"{ctx.author.name} is blushing!"
        embed.description = "Aw, look at them, how adorable, hehe :3"
        await ctx.send(embed=embed_class.EMBED_FORMAT(embed=embed, user=ctx.author))

    @hybrid_command(name="brofist",
                    description="Sends a brofist gif/img")
    @describe(member="Member you want to brofist")
    @allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def brofist(self,
                      ctx: commands.Context,
                      member: Optional[User]):
        embed = self.gif_maker("brofist")
        embed.title = f"{ctx.author.name} is brofisting with someone!" if not member else f"{member.name}, {ctx.author.name} is brofisting with you!"
        embed.description = "Yo, don't leave him hanging!" if not member else "Hell yeah brothers!"
        message = member.mention if member else ""
        await ctx.send(content=message, embed=embed_class.EMBED_FORMAT(embed=embed, user=ctx.author))

    @hybrid_command(name="celebrate",
                    description="Sends a celebrating gif/img")
    @allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def celebrate(self,
                        ctx: commands.Context):
        reaction = choice(["celebrate", "cheers"])
        embed = self.gif_maker(reaction)
        embed.title = f"{ctx.author.name} is celebrating!"
        embed.description = "Yeah! Victory!"
        await ctx.send(embed=embed_class.EMBED_FORMAT(embed=embed, user=ctx.author))

    @hybrid_command(name="cry",
                    description="Sends a crying gif/img")
    @allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def cry(self,
                  ctx: commands.Context):
        embed = self.gif_maker("cry")
        embed.title = f"{ctx.author.name} is crying..."
        embed.description = "Poor them... try to cheer 'em up please 3:"
        await ctx.send(embed=embed_class.EMBED_FORMAT(embed=embed, user=ctx.author))

    @hybrid_command(name="dance",
                    description="Sends a dancing gif/img")
    @allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def dance(self,
                    ctx: commands.Context):
        embed = self.gif_maker("dance")
        embed.title = f"{ctx.author.name} is dancing!"
        embed.description = "Party party yeah!"
        await ctx.send(embed=embed_class.EMBED_FORMAT(embed=embed, user=ctx.author))

    @hybrid_command(name="facepalm",
                    description="Sends a facepalming gif/img")
    @allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def facepalm(self,
                       ctx: commands.Context):
        embed = self.gif_maker("facepalm")
        embed.title = f"{ctx.author.name} is facepalming..."
        embed.description = "Sigh, look at this chat, filled with IDIOTS."
        await ctx.send(embed=embed_class.EMBED_FORMAT(embed=embed, user=ctx.author))

    @hybrid_command(name="handhold",
                    description="Sends a handholding gif/img")
    @allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def handhold(self,
                       ctx: commands.Context,
                       member: User):
        embed = self.gif_maker("handhold")
        embed.title = f"{ctx.author.name} is holding {member.name}'s hand! ❤️"
        embed.description = "How lewd!"
        await ctx.send(member.mention ,embed=embed_class.EMBED_FORMAT(embed=embed, user=ctx.author))

    @hybrid_command(name="kiss",
                    description="Sends a kissing gif/img")
    @describe(member="Member you want to kiss")
    @allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def kiss(self,
                   ctx: commands.Context,
                   member: Optional[User]):
        embed = self.gif_maker("kiss")
        embed.title = f"{ctx.author.name} is kissing someone!" if not member else f"{member.name}, {ctx.author.name} is kissing you!"
        embed.description = "Anyone?" if not member else "Awww, look at those lovebirds :3"
        message = member.mention if member else ""
        await ctx.send(content=message, embed=embed_class.EMBED_FORMAT(embed=embed, user=ctx.author))

    @hybrid_command(name="hurt",
                    description="Sends a hurt gif/img")
    @describe(member="Member you want to hurt")
    @allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def hurt(self,
                   ctx: commands.Context,
                   member: Optional[User]):
        embed = self.gif_maker(choice(["punch", "slap", "smack"]))
        embed.title = f"{ctx.author.name} is hurting someone...!" if not member else f"{member.name}, {ctx.author.name} wants to hurt you..!"
        embed.description = "Careful yall, someone's in a bad mood..." if not member else "Uh oh, run!"
        message = member.mention if member else ""
        await ctx.send(content=message, embed=embed_class.EMBED_FORMAT(embed=embed, user=ctx.author))

    @hybrid_command(name="lick",
                    description="Sends a licking gif/img")
    @describe(member="Member you want to lick")
    @allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def lick(self,
                   ctx: commands.Context,
                   member: Optional[User]):
        embed = self.gif_maker("lick")
        embed.title = f"{ctx.author.name} is licking someone!" if not member else f"{member.name}, {ctx.author.name} is licking you!"
        embed.description = "Someone's feeling cutesy :3" if not member else "Get a room!"
        message = member.mention if member else ""
        await ctx.send(content=message, embed=embed_class.EMBED_FORMAT(embed=embed, user=ctx.author))

    @hybrid_command(name="nuzzle",
                    description="Sends a nuzzling gif/img")
    @describe(member="Member you want to nuzzle to")
    @allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def nuzzle(self,
                     ctx: commands.Context,
                     member: Optional[User]):
        embed = self.gif_maker("nuzzle")
        embed.title = f"{ctx.author.name} is nuzzling to someone!" if not member else f"{member.name}, {ctx.author.name} is nuzzling to you!"
        embed.description = "Warmth's always nice hehe." if not member else "Lucky you ;3"
        message = member.mention if member else ""
        await ctx.send(content=message, embed=embed_class.EMBED_FORMAT(embed=embed, user=ctx.author))

    @hybrid_command(name="pet",
                    description="Sends a petting gif/img")
    @describe(member="Member you want to pet")
    @allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def pet(self,
                  ctx: commands.Context,
                  member: Optional[User]):
        embed = self.gif_maker("pat")
        embed.title = f"{ctx.author.name} is petting someone!" if not member else f"{member.name}, {ctx.author.name} is petting you!"
        embed.description = "Lucky you!" if not member else "Cute. Very cute."
        message = member.mention if member else ""
        await ctx.send(content=message, embed=embed_class.EMBED_FORMAT(embed=embed, user=ctx.author))

    @hybrid_command(name="poke",
                    description="Sends a poking gif/img")
    @describe(member="Member you want to poke")
    @allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def poke(self,
                   ctx: commands.Context,
                   member: Optional[User]):
        embed = self.gif_maker("poke")
        embed.title = f"{ctx.author.name} is poking someone!" if not member else f"{member.name}, {ctx.author.name} is poking you!"
        embed.description = "Hehe.. :3" if not member else "Pst, I think they want attention!"
        message = member.mention if member else ""
        await ctx.send(content=message, embed=embed_class.EMBED_FORMAT(embed=embed, user=ctx.author))

    @hybrid_command(name="shout",
                    description="Sends a shouting gif/img")
    @describe(member="Member you want to shout at")
    @allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def shout(self,
                    ctx: commands.Context,
                    member: Optional[User]):
        embed = self.gif_maker("shout")
        embed.title = f"{ctx.author.name} is shouting at someone!" if not member else f"{member.name}, {ctx.author.name} is shouting at you!"
        embed.description = "Uh... I think they're mad." if not member else "Apologize."
        message = member.mention if member else ""
        await ctx.send(content=message, embed=embed_class.EMBED_FORMAT(embed=embed, user=ctx.author))

    @hybrid_command(name="wave",
                    description="Sends a waving gif/img")
    @describe(member="Member you want to wave at")
    @allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def wave(self,
                   ctx: commands.Context,
                   member: Optional[User]):
        embed = self.gif_maker("wave")
        embed.title = f"{ctx.author.name} is waving at someone!" if not member else f"{member.name}, {ctx.author.name} is waving at you!"
        embed.description = "Hello stranger!" if not member else "Hello good friend!"
        message = member.mention if member else ""
        await ctx.send(content=message, embed=embed_class.EMBED_FORMAT(embed=embed, user=ctx.author))

    @hybrid_command(name="wink",
                    description="Sends a winking gif/img")
    @describe(member="Member you want to wink at")
    @allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def wink(self,
                   ctx: commands.Context,
                   member: Optional[User]):
        embed = self.gif_maker("wink")
        embed.title = f"{ctx.author.name} is winking at someone!" if not member else f"{member.name}, {ctx.author.name} is winking at you!"
        embed.description = "Secret ;3" if not member else "Himitsu desu ;3"
        message = member.mention if member else ""
        await ctx.send(content=message, embed=embed_class.EMBED_FORMAT(embed=embed, user=ctx.author))

    @hybrid_command(name="sigh",
                    description="Sends a sighing gif/img")
    @allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def sigh(self,
                   ctx: commands.Context):
        embed = self.gif_maker("sigh")
        embed.title = f"{ctx.author.name} is sighing..."
        embed.description = "Tiring..."
        await ctx.send(embed=embed_class.EMBED_FORMAT(embed=embed, user=ctx.author))

    @hybrid_command(name="sleep",
                    description="Sends a sleeping gif/img")
    @allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def sleep(self,
                   ctx: commands.Context):
        embed = self.gif_maker("sleep")
        embed.title = f"{ctx.author.name} is going to sleep.."
        embed.description = "Goodnight chat!"
        await ctx.send(embed=embed_class.EMBED_FORMAT(embed=embed, user=ctx.author))

async def setup(bot: commands.Bot):
    await bot.add_cog(RPCog(bot))