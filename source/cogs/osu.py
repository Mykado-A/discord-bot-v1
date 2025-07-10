from discord.app_commands import describe, Group
from discord.ext import commands
from discord.ext.commands import hybrid_command
from discord import Embed
from source.formatting.settings import embed_class
import os
from ossapi import Ossapi


class OsuCog(commands.Cog):
    def __init__(self,
                 bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.description = "This is all the osu commands."
        self.OSU_SECRET = os.getenv("OSU_SECRET")
        self.OSU_ID = os.getenv("OSU_ID")

        self.api = Ossapi(self.OSU_ID, self.OSU_SECRET)

    @commands.hybrid_group(name="osu")
    async def osu(self, ctx: commands.Context):
        pass

    @osu.command(name="profile",
                       description="Gives infos about a osu user")
    @describe(user="Name of osu user you want to check out")
    async def osu_profile(self,
                          ctx: commands.Context,
                          user: str):
        try:
            osu_user = self.api.user(user)
        except ValueError:
            return await ctx.send(f"Could not find {user}...", ephemeral=True)
        e = Embed(title=f"Infos about {user}'s osu profile :",
                  color=0x00FF00)
        e.set_thumbnail(url=osu_user.avatar_url)

        e.add_field(name="Highest rank :", value=f"#{osu_user.rank_highest.rank}")
        e.add_field(name="Country :", value=osu_user.country.name)
        e.add_field(name="Achievements :",
                    value=len(osu_user.user_achievements) if osu_user.user_achievements is not None else 0)
        e.add_field(name="Friends :", value=len(osu_user.friends) if osu_user.friends is not None else 0)
        e.add_field(name="Created account on :", value=osu_user.join_date.strftime('%a %d %b %Y'))

        if osu_user.discord:
            e.add_field(name="Discord :", value=osu_user.discord, inline=False)
        if osu_user.twitter:
            e.add_field(name="Twitter :", value=osu_user.twitter, inline=False)
        if osu_user.website:
            e.add_field(name="Website :", value=osu_user.website, inline=False)
        return await ctx.send(embed=embed_class.EMBED_FORMAT(e, ctx.author))

    @osu.command(name="ranking",
                       description="Osu rankings!")
    @describe(mode="Gamemode you want the leaderboards of")
    async def ranking(self,
                      ctx: commands.Context,
                      mode: str):
        if mode.lower() in ["standard", "std", "osu"]:
            mode = "osu"
        elif mode.lower() == "catch":
            mode = "fruits"
        else:
            return await ctx.send(
                f"Couldn't understand the mode you inputted. Available roles : standard, catch, mania, taiko",
                ephemeral=True)
        ranks_list = self.api.ranking(mode=mode.lower(), type="performance").ranking
        res = ""
        for i in range(10):
            res += f"#{i + 1}: {ranks_list[i].user.username}, {ranks_list[i].pp}pp\n"
        e = Embed(title=f"Current top 10 {mode.title()} players :",
                  description=res,
                  color=0x00FF00)
        e = embed_class.EMBED_FORMAT(e, ctx.author)
        return await ctx.send(embed=e)

async def setup(bot: commands.Bot):
    await bot.add_cog(OsuCog(bot))