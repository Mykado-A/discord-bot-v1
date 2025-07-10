from discord import Member
from discord.app_commands import guild_only, guild_install
from discord.ext import commands
from discord.ext.commands import hybrid_command, hybrid_group

from source.formatting.settings import embed_class


class InfoCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot
        self.description: str = "This is Hoshiko's info commands."

    @hybrid_group(name="discord")
    async def discord(self, ctx: commands.Context):
        pass

    @discord.command(name="avatar",
                     description="Gives avatar of a user!")
    async def avatar(self,
                     ctx: commands.Context,
                     user: Member):
        e = embed_class.AVATAR_EMBED(user)
        await ctx.send(embed=e)

    @discord.command(name="info",
                     description="Gives infos about a user!")
    @guild_only()
    @guild_install()
    async def info(self,
                   ctx: commands.Context,
                   user: Member):
        e = embed_class.USER_INFO_EMBED(user)
        await interaction.response.send_message(embed=e)

async def setup(bot: commands.Bot):
    await bot.add_cog(InfoCog(bot))
