from typing import Coroutine

import discord
from discord.app_commands import describe, guild_install, guild_only
from discord.ext import commands
from discord.ext.commands import has_permissions, hybrid_command

from source.classes.jsonDB import db


class Setup(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot
        self.description: str = "This is Hoshiko's setup/admin commands, used for starboard handling, logs, etc..."


    @hybrid_command(name="blacklist",
                    description="Blacklists a channel from starboard!",
                    aliases=["star blacklist"])
    @describe(channel="The channel to blacklist using #CHANNEL_NAME")
    @has_permissions(administrator=True)
    @guild_install()
    @guild_only()
    async def star_blacklist(self,
                             ctx: commands.Context,
                             channel: str) -> Coroutine:
        try:
            chan: discord.TextChannel = self.bot.get_channel(int(channel[2:-1]))
            if chan is None:
                raise ValueError
        except ValueError:
            return await ctx.send("Unvalid channel.")
        if chan in db.get_blacklist(ctx.guild):
            return await ctx.send("Channel already in the blacklist!")
        db.set_blacklist(ctx.guild, chan)
        return await ctx.send("Channel added to the blacklist!")

    @hybrid_command(name="unblacklist",
                    description="Unblacklists a channel from starboard!",
                    aliases=["star blacklistRemove"])
    @describe(channel="The channel to remove from blacklist using #CHANNEL_NAME")
    @has_permissions(administrator=True)
    @guild_install()
    @guild_only()
    async def star_unblacklist(self,
                               ctx: commands.Context,
                               channel: str) -> Coroutine:
        try:
            chan: discord.TextChannel = self.bot.get_channel(int(channel[2:-1]))
            if chan is None:
                raise ValueError
        except ValueError:
            return await ctx.send("Unvalid channel.")
        if chan in db.get_blacklist(ctx.guild):
            return await ctx.send("Channel not in the blacklist!")
        db.remove_blacklist(ctx.guild, chan)
        return await ctx.send("Channel removed from the blacklist!")

async def setup(bot: commands.Bot):
    await bot.add_cog(Setup(bot))