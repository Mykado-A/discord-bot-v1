from typing import Optional

from discord import (Interaction,
                     Member)
from discord.app_commands import describe
from discord.ext import commands
from discord.ext.commands import hybrid_command, has_permissions, BucketType, hybrid_group
from discord.app_commands import guild_install, guild_only

from random import randint
from source.classes.jsonDB import db
from source.formatting.settings import embed_class
from source.formatting.functions import OnCooldown


class Economy(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.description = "All economy related commands."

    @hybrid_command(name="balance",
                    description="Tells you how much money you have!")
    @describe(user="User you want to check the balance of")
    @guild_install()
    @guild_only()
    async def balance(self,
                      ctx: commands.Context,
                      user: Optional[Member]):
        if user:
            u = user
        else:
            u = ctx.author
        bal = db.get_user(ctx.guild, u)[2]
        await ctx.send(embed=embed_class.BALANCE_EMBED(u, bal))

    @hybrid_group(name='money')
    async def money(self, ctx: commands.Context):
        pass

    @money.command(name="add",
                   description="Adds money to a user!")
    @has_permissions(administrator=True)
    @describe(user="User to add the money to",
              amount="Money to add")
    @guild_install()
    @guild_only()
    async def add(self,
                  ctx: commands.Context,
                  user: Member,
                  amount: int):
        await ctx.send("Y")

    @money.command(name="remove",
                    description="Removes money from a user!")
    @describe(user="User to remove the money from",
              amount="Money to remove")
    @guild_install()
    @guild_only()
    @has_permissions(administrator=True)
    async def remove(self,
                           interaction: Interaction,
                           user: Member,
                           amount: int):
        db.change_value(ctx.guild, user, 2, -amount)
        await ctx.send(f"{amount} 💵 has been removed from {user.display_name}'s account!")

    @hybrid_command(name="work",
                    description="Work for money!")
    @guild_install()
    @guild_only()
    @commands.cooldown(1, 300.0, BucketType.user)
    async def work(self,
                   ctx: commands.Context):
        work_prompts = ["You worked at a ocal bakery!",
                        "You won a videogame tournament!",
                        "You found a bill on the ground!",
                        "You won a chess tournament!",
                        "You worked hard at your job today!"]
        amount = randint(50, 500)
        prompt = work_prompts[randint(0, 4)]
        db.change_value(ctx.guild, ctx.author, 2, amount)
        await ctx.send(embed=embed_class.ECO_EMBED(ctx.author, prompt, amount))


    @hybrid_command(name="crime",
                    description="Commit crimes for money!")
    @guild_install()
    @guild_only()
    @commands.cooldown(1, 600.0, BucketType.user)
    async def crime(self,
                    ctx: commands.Context):
        crime_pos_prompts = ["You stole from the homeless!",
                             "You did a bank heist!",
                             "You committed tax fraud!",
                             "Your rich partner cheated, and you stole half their wealth!",
                             "You killed someone and stole his wallet and his belongings!"]
        crime_neg_prompts = ["You got caught pickpocketting...",
                             "You got caught cheating at an exam...",
                             "You tried to steal from a police officer..."]
        amount = randint(-500, 1000)
        if amount == 0:
            amount = 1
        prompt = crime_pos_prompts[randint(0, 4)] if amount > 0 else crime_neg_prompts[randint(0, 2)]
        db.change_value(ctx.guild, ctx.author, 2, amount)
        return await ctx.send(embed=embed_class.ECO_EMBED(ctx.author, prompt, amount))


    @hybrid_command(name="steal",
                    description="Steal money from someone!")
    @guild_install()
    @guild_only()
    @describe(user="User to steal money from")
    @commands.cooldown(1, 3600.0, BucketType.user)
    async def steal(self,
                    ctx: commands.Context,
                    user: Member):
        amount = randint(-1000, 1000)
        if amount == 0:
            amount = 1
        prompt = f"You successfully stole from {user.display_name}!" if amount > 0 else f"You got caught stealing from {user.display_name}..."
        db.change_value(ctx.guild, ctx.author, 2, amount)
        if amount > 0:
            db.change_value(ctx.guild, user, 2, -amount)
        await ctx.send(embed=embed_class.ECO_EMBED(ctx.author, prompt, amount))

    @hybrid_command(name="hourly",
                    description="Your hourly paycheck!")
    @guild_install()
    @guild_only()
    @commands.cooldown(1, 3600.0, BucketType.user)
    async def hourly(self,
                     ctx: commands.Context):
        amount = randint(1000, 10000)
        prompt = "You redeemed your hourly paycheck!"
        db.change_value(ctx.guild, ctx.author, 2, amount)
        await ctx.send(embed=embed_class.ECO_EMBED(ctx.author, prompt, amount))

    @hybrid_command(name="daily",
                    description="Your daily paycheck!")
    @guild_install()
    @guild_only()
    @commands.cooldown(1, 86400.0, BucketType.user)
    async def daily(self,
                    ctx: commands.Context):
        amount = randint(10000, 100000)
        prompt = "You redeemed your daily paycheck!"
        db.change_value(ctx.guild, ctx.author, 2, amount)
        await ctx.send(embed=embed_class.ECO_EMBED(ctx.author, prompt, amount))

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CommandOnCooldown):
            return await OnCooldown(ctx, error)

async def setup(bot: commands.Bot):
    await bot.add_cog(Economy(bot))