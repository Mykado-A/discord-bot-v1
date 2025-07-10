import discord

from discord.app_commands import guild_install, guild_only, describe, allowed_contexts, allowed_installs
from discord.ext import commands
from discord.ext.commands import hybrid_command
from source.classes.jsonDB import db
from discord import Member, Embed, User
from typing import Optional
from source.formatting.settings import embed_class
from PIL import Image, ImageFont, ImageDraw
import datetime
from datetime import datetime
import asyncio
from io import BytesIO


class MarriageCog(commands.Cog):
    def __init__(self,
                 bot: commands.Bot):
        self.bot = bot
        self.description = "This is all commands related to marriage."

    @hybrid_command(name="marry",
                    description="Marry someone!")
    @describe(member="The user you want to marry")
    @allowed_contexts(guilds=True, dms=True, private_channels=True)
    @allowed_installs(guilds= True, users= True)
    async def marry(self,
                    ctx: commands.Context,
                    member: User):
        if member.id == ctx.author.id:
            return await ctx.send("You can't marry yourself.")
        if str(member.id) in db.get_client_users():
            if len(db.get_partner(member)) != 0:
                return await ctx.send(f"{member.display_name} is already married...")
        else:
            db.add_client_user(member)
            print(f"Added {member.name} to db")
        if str(ctx.author.id) not in db.get_client_users():
            db.add_client_user(ctx.author)
            print(f"Added {ctx.author.name} to db")

        nb_exes1 = db.get_exes(member)[0]
        nb_exes2 = db.get_exes(ctx.author)[0]
        exes = db.get_exes(member)
        e = Embed(title=f"You proposed to {member.display_name}!",
                  description=f"They had {nb_exes1} exes and you have {nb_exes2}!\nThey have 15 seconds to answer (Y/N)",
                  color=0x0000FF)
        if ctx.author.name in exes:
            e.description += "\n\nCareful! You are exes..."
        view = discord.ui.View(timeout=15.0)
        button = discord.ui.Button(label="Yes!", style=discord.ButtonStyle.primary, custom_id="1")
        button2 = discord.ui.Button(label="No!", style=discord.ButtonStyle.danger, custom_id="2")

        async def on_timeout(interaction: discord.Interaction):
            print("Timed out!")
            view.stop()
            return await current_embed.edit(content="The proposal vanished in thin air.", embed=None)

        async def button_callback(interaction: discord.Interaction):
            if interaction.user.id == member.id:
                if interaction.data['custom_id'] == "1":
                    em = Embed(title="Congratulations! 💍",
                              description=f"{interaction.user.display_name} just married {member.display_name}\n",
                              color=0x0000FF)
                    img = Image.open("img/proposal.png")
                    edit = ImageDraw.Draw(img)
                    font = ImageFont.truetype("font.ttf", 16)
                    x1 = 400
                    x2 = 69
                    edit.text((x1, 150), member.name, (255, 255, 255), font=font)
                    edit.text((x2, 150), ctx.author.name, (255, 255, 255), font=font)
                    with BytesIO() as img_bytes:
                        img.save(img_bytes, format=img.format)
                        final = img_bytes.getvalue()
                    file = discord.File(BytesIO(final), filename="image.png")
                    em.set_image(url="attachment://image.png")
                    em = embed_class.EMBED_FORMAT(em, ctx.author)
                    db.set_partner(ctx.author, member)
                    return await current_embed.edit(attachments=[file], embed=em)
                else:
                    em = Embed(title="Your proposal was denied...",
                              description=f"{ctx.author.display_name} got rejected by {member.display_name}...",
                              color=0x0000FF)
                    em = embed_class.EMBED_FORMAT(em, ctx.author)
                    return await current_embed.edit(embed=em)
                view.stop()
            else:
                await interaction.response.send_message("You're not the one asked!", ephemeral=True)

        view.on_timeout = on_timeout
        button.callback = button_callback
        button2.callback = button_callback
        view.add_item(button)
        view.add_item(button2)

        current_embed = await ctx.send(embed=embed_class.EMBED_FORMAT(e, ctx.author), view=view)

    @hybrid_command(name="partner",
                    description="Gives infos about the person you're married with")
    @guild_install()
    @guild_only()
    async def partnerinfo(self,
                          ctx: commands.Context):
        #WIP
        u = ctx.author

        if db.get_partner(u) is []:
            return await ctx.send(f"{u.display_name} is not married...")

        partner = await self.bot.fetch_user(db.get_partner(u)[0])
        wealth = db.get_user(ctx.guild, ctx.author)[2] + db.get_user(ctx.guild, partner)[2]
        date = datetime.strptime(db.get_partner(ctx.guild, ctx.author)[1], "%Y-%m-%d %H:%M:%S.%f")
        e = Embed(title=f"{u.display_name} is married to {partner.display_name}",
                  description=f"Happily married since {date.strftime('%a %d %b %Y, %I:%M%p')}\n\n"
                              f"Collective wealth : {wealth} 💵",
                  color=0x00FF00)
        e.set_image(url=partner.avatar)
        e = embed_class.EMBED_FORMAT(e, ctx.author)
        return await ctx.send(embed=e)

    @hybrid_command(name="divorce",
                    description="Divorce your partner...")
    @allowed_contexts(guilds=True, dms=True, private_channels=True)
    @allowed_installs(guilds=True, users=True)
    async def divorce(self,
                      ctx: commands.Context):
        if len(db.get_partner(member)) == 0:
            return await ctx.send(f"{ctx.author.display_name} is not married...")

        partner = await self.bot.fetch_user(db.get_partner(ctx.author)[0])

        e = Embed(title=f"Do you really want to divorce {partner.display_name}!",
                  description="You have 15 seconds to answer (Y/N)",
                  color=0x0000FF)
        e = embed_class.EMBED_FORMAT(e, ctx.author)
        await ctx.send(embed=e)

        def check(m: discord.Message):
            return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ["y", "n", "yes", "no"]

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=15.0)
        except asyncio.TimeoutError:
            return await ctx.channel.send("The divorce was cancelled.")
        else:
            if msg.content.lower() in ["y", "yes"]:
                date = datetime.strptime(db.get_partner(ctx.author)[1],
                                         "%Y-%m-%d %H:%M:%S.%f")
                e = Embed(title=f"{ctx.author.display_name} divorced {partner.display_name}",
                          description=f"They were married since {date.strftime('%a %d %b %Y, %I:%M%p')}",
                          color=0x0000FF)
                e = embed_class.EMBED_FORMAT(e, ctx.author)
                db.divorce(ctx.author, partner)
                return await ctx.channel.send(embed=e)
            else:
                return await ctx.channel.send("The divorce was cancelled.")

async def setup(bot: commands.Bot):
    await bot.add_cog(MarriageCog(bot))