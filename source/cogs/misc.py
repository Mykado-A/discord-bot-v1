import discord
from discord.app_commands import describe, guild_only, guild_install
from discord.ext import commands
from discord.ext.commands import hybrid_command, BucketType
import wikipedia
from discord import Embed, Member
import requests
from typing import Optional
from source.classes.jsonDB import db
from source.formatting.settings import embed_class
from PIL import Image, ImageFont, ImageDraw
from io import BytesIO
import textwrap

class MiscCog(commands.Cog):
    def __init__(self,
                 bot: commands.Bot):
        self.bot = bot
        self.description = "This is all the miscellanious commands."

    @hybrid_command(name="wikipedia",
                    description="Wikipedia summary!")
    @describe(query="What you want to look up")
    async def wiki(self,
                   ctx: commands.Context,
                   query: str):
        wikipedia.set_lang("en")
        try:
            page = wikipedia.page(query, auto_suggest=True)
        except wikipedia.PageError:
            return await ctx.send(f"Couldn't find a wiki page of {query}, please retry, with the exact name of the page.", ephemeral=True)
        if len(page.summary) <= 4096:
            text = page.summary
        else:
            text: str = page.summary[:4096]
            last_dot = text.rfind(".")
            text = text[:last_dot+1]
        e = Embed(title=query.title(),
                  url=page.url,
                  description=text,
                  color=0x00FF00)
        return await ctx.send(embed=embed_class.EMBED_FORMAT(e, ctx.author))

    @hybrid_command(name="rank",
                    description="Shows level and exp!")
    @describe(user="Member you want to see the rank of")
    @commands.cooldown(1, 10.0, BucketType.user)
    @guild_only()
    @guild_install()
    async def rank(self,
                   ctx: commands.Context,
                   user: Optional[Member]):
        u = ctx.author
        if user:
            u = user
        data = (db.get_user(ctx.guild, u)[0], db.get_user(ctx.guild, u)[1])
        xp, lvl = data
        disp_name = u.name
        img = Image.open("img/banner.png")
        edit = ImageDraw.Draw(img)
        font = ImageFont.truetype("font.ttf", 16)
        font2 = ImageFont.truetype("font.ttf", 25)
        edit.text((400, 150), disp_name, (255, 255, 255), font=font)
        edit.text((190, 120), str(lvl), (0, 0, 0), font=font2)
        edit.text((169, 180), str(xp) + " / " + str(int(500 + (lvl * (50 * 1.1)))), (0, 0, 0), font=font)
        with BytesIO() as img_bytes:
            img.save(img_bytes, format=img.format)
            final = img_bytes.getvalue()
        await ctx.send(file=discord.File(BytesIO(final), filename=f"{u.name}-rank.png"))

    @hybrid_command(name="afk",
                    description="Makes you afk!")
    @describe(message="The reason for your afk")
    @guild_only()
    @guild_install()
    async def afk(self,
                  ctx: commands.Context,
                  message: Optional[str]):
        if db.get_afk(ctx.author) != "":
            return await ctx.send("You are already afk! Please get out of afk before being afk again!")
        else:
            await ctx.author.edit(nick=f"[AFK] {ctx.author.display_name}")
            mess = "AFK!" if not message else message
            db.set_afk(ctx.author, mess)
            await ctx.send(f"{ctx.author.mention} is AFK'ing! Message from them : {mess}")

    @hybrid_command(name="caption",
                    description="Captions an attachment.")
    @describe(caption="Text you want to put as a caption",
              img="Image you want to caption")
    async def caption(self,
                      ctx: commands.Context,
                      caption: str,
                      img: discord.Attachment):
        if not caption:
            await ctx.send(
                "Please include some caption text after the `h!caption` command. For example `h!caption \"Hello world!\"`")
            return

        # Check if an image is attached
        if not img:
            await ctx.send("Please attach an image for me to caption.")
            return

        # Get the image URL
        image_url = img.url

        image_width = img.width

        # Fetch the image file
        response = requests.get(image_url)

        # Store the image file name
        image_filename = img.filename

        image_bytes = BytesIO(response.content)

        img = Image.open(image_bytes)


        font_size = int(img.width / 16)
        font = ImageFont.truetype("arial.ttf", font_size)

        caption = textwrap.fill(text=caption, width=img.width / (font_size / 2))

        caption_h = font_size * len(caption.split('\n'))

        rect_height = img.height // 8

        new = Image.new("RGB", (img.width, img.height + caption_h + rect_height), "white")
        new.paste(img, (0, caption_h + rect_height))
        draw = ImageDraw.Draw(new)

        caption_w = draw.textlength(caption, font=font)

        draw.text(((new.width - caption_w) / 2, caption_h),  # position
                  caption,  # text
                  (0, 0, 0),  # color
                  font=font)

        with BytesIO() as img_bytes:
            new.save(img_bytes, format=img.format)
            final = img_bytes.getvalue()

        # Send the captioned image
        await ctx.send(file=discord.File(BytesIO(final), filename=f"captioned-{image_filename}"))


async def setup(bot: commands.Bot):
    await bot.add_cog(MiscCog(bot))