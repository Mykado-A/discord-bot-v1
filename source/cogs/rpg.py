from typing import Coroutine

import discord
from discord import Member, ButtonStyle, Embed
from discord.app_commands import describe, guild_only, guild_install
from discord.ext import commands
from discord.ext.commands import has_permissions, hybrid_command
from discord.ui import button


class Class(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.value = None

    @button(label="Warrior", style=ButtonStyle.danger)
    async def warrior(self, b, interaction: discord.Interaction):
        self.value = "warrior"
        self.stop()
    @button(label="Rogue", style=ButtonStyle.blurple)
    async def rogue(self, b, interaction: discord.Interaction):
        self.value = "rogue"
        self.stop()
    @button(label="Mage", style=ButtonStyle.gray)
    async def mage(self, b, interaction: discord.Interaction):
        self.value = "mage"
        self.stop()

class RPGCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot
        self.description: str = "This is Hoshiko's RPG commands."

    async def confirm(self, ctx, e):
        await ctx.send(embed=Embed(title="***???***",
                                   description=f"Are you sure, player?\n\n*(Y/N)*"))

        def check(m: discord.Message):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ["y", "n"]

        msg = await self.bot.wait_for("message", check=check)

        return True if msg.content.lower() == "y" else False


    @hybrid_command(name="test_rpg",
                    description="RPG Intro Test")
    async def new_player(self, ctx: commands.Context):
        e = Embed(title="***???***",
                  description="Hey there, newbie!\n"
                              "You look a little lost..\n"
                              "Let me show you how everything works around here!\n"
                              "First off, let's see... what class are you, dear player?",
                  color=0xFFFFFF)

        view = Class()

        await ctx.send(embed=e, view=view)
        await view.wait()
        user_input = await self.confirm(ctx, e)

        while not user_input:
            await ctx.send(embed=e, view=view)
            await view.wait()
            user_input = await self.confirm(ctx, e)

        e = Embed(title="***???***",
                  description=f"Great, and how is this {view.value} called?"
                              f"\n\n*(Input the name of your character)*",
                  color=0xFFFFFF)

        await ctx.send(embed=e)

        def check(m: discord.Message):
            return m.author == ctx.author and m.channel == ctx.channel

        msg = await self.bot.wait_for("message", check=check)
        user_input = await self.confirm(ctx, e)

        while not user_input:
            await ctx.send(embed=e)
            msg = await self.bot.wait_for("message", check=check)
            user_input = await self.confirm(ctx, e)

        await ctx.send(embed=Embed(title="***???***",
                                   description="Great... simply... great...",
                                   color=0xFFFFFF))



async def setup(bot: commands.Bot):
    await bot.add_cog(RPGCog(bot))
