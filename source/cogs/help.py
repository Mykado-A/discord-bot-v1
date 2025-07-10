import discord
from discord.ext import commands
from discord.ext.commands import hybrid_command


class HelpCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.embed_color = 0x88571B

    @hybrid_command(
        name="help",
        description="Gives the description of every command",
        aliases=["h"]
    )
    async def help(self,
                   ctx: commands.Context) -> None:
        bot_commands = self.bot.tree.get_commands()
        command_description = ""

        for c in bot_commands:
            command_description += f"**`!{c.name}`** or */{c.name}* {c.description}\n"
        commands_embed = discord.Embed(
            title="Commands List",
            description=command_description,
            colour=self.embed_color
        )

        await ctx.send(embed=commands_embed)

async def setup(bot):
    await bot.add_cog(HelpCog(bot))