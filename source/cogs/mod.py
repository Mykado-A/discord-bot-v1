from discord import Member, Role
from discord.app_commands import describe, guild_install
from discord.ext import commands
from discord.ext.commands import hybrid_command, has_permissions, is_owner, guild_only

from source.formatting.settings import embed_class


###########################################################################################################
###########################################################################################################

#                                                 MOD COG

###########################################################################################################
###########################################################################################################


class Mod(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot
        self.description: str = "This is Hoshiko's setup/admin commands, used for starboard handling, logs, etc..."

    @hybrid_command(name="ban",
                    description="Bans user!",)
    @describe(user="User to ban",
              reason="Ban reason")
    @has_permissions(ban_members=True)
    async def bannedgg(self,
                       ctx: commands.Context,
                       user: Member,
                       reason: str):
        if not user:
            await ctx.send("Couldn't find user...")
        # Embed
        e = embed_class.MOD_EMBED(user, "ban", reason)

        # Bans user
        try:
            await user.ban(reason=reason)
        except (CommandInvokeError, Forbidden) as er:
            e.title = f"Couldn't ban {user.display_name}..."
            e.description = f"Error : {er}"

        await ctx.send(embed=e)

    @hybrid_command(name="kick",
                    description="Kicks user!",)
    @describe(user="User to kick",
              reason="Kick reason")
    @has_permissions(kick_members=True)
    async def kickedgg(self,
                       ctx: commands.Context,
                       user: Member,
                       reason: str):
        if not user:
            await ctx.send("Couldn't find user...")
        # Embed
        e = embed_class.MOD_EMBED(user, "kick", reason)

        # Kicks user
        try:
            await user.kick(reason=reason)
        except (CommandInvokeError, Forbidden) as er:
            e.title = f"Couldn't kick {user.display_name}..."
            e.description = f"Error : {er}"

        await ctx.send(embed=e)

    @hybrid_command(name="timeout",
                    description="Timeouts user!")
    @describe(user="User to time out",
              reason="Timeout reason",
              seconds="Timeout time")
    @has_permissions(kick_members=True)
    async def timedoutdawg(self,
                           ctx: commands.Context,
                           user: Member,
                           reason: str,
                           seconds: int):
        if not user:
            await ctx.send("Couldn't find user...")
        # Embed
        e = embed_class.MOD_EMBED(user, "timeout", reason, seconds)

        # Timeout user
        try:
            await user.timeout(timedelta(seconds=seconds), reason=reason)
        except (CommandInvokeError, Forbidden) as er:
            e.title = f"Couldn't time out {user.display_name}..."
            e.description = f"Error : {er}"

        await ctx.send(embed=e)


    @hybrid_command(name="massadd",
                    description="Adds role to people who already have a role.")
    @has_permissions(manage_roles=True)
    async def mass_add(self,
                       ctx: commands.Context,
                       role_1: Role,
                       role_2: Role) -> None:
        list_mem = ctx.guild.members
        count = 0
        for member in list_mem:
            if role_2 in member.roles:
                try:
                    await member.add_roles(role_1)
                    count += 1
                except Forbidden:
                    continue
        await ctx.send(f"{role_1} was added to {count} members!")

    @hybrid_command(name='sync')
    @is_owner()
    @guild_install()
    @guild_only()
    async def sync_local(self, ctx: commands.Context):
        await ctx.send('Settings run')
        self.bot.tree.clear_commands(guild=ctx.guild)
        await self.bot.tree.sync(guild=ctx.guild)
        self.bot.tree.clear_commands(guild=None)
        await self.bot.tree.sync(guild=None)

async def setup(bot: commands.Bot):
    await bot.add_cog(Mod(bot))