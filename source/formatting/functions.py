from datetime import timedelta

from discord.ext import commands

from source.formatting.settings import embed_class


async def OnCooldown(ctx: commands.Context,
                     error):
    time: timedelta = timedelta(seconds=int(error.retry_after))
    return await ctx.send(embed=embed_class.COOLDOWN_EMBED(time, ctx.author),
                          ephemeral=True)