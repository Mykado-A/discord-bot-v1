import os
from typing import Any

import discord
from discord import Message, Member, Object, BaseActivity, app_commands, ClientUser
from discord.app_commands import guild_install, allowed_installs
from discord.ext import commands
from discord.ext.commands import is_owner, guild_only
from dotenv import load_dotenv

from classes.jsonDB import db
from formatting.settings import embed_class



# Cooldown pour l'exp donné par les messages
message_cooldown = commands.CooldownMapping.from_cooldown(rate=1.0,
                                                          per=2.0,
                                                          type=commands.BucketType.user)


###########################################################################################################
###########################################################################################################

#                                           CLASSE PRINCIPALE

###########################################################################################################
###########################################################################################################


class Hoshiko(commands.Bot):
    # Initialisation des attribus de la classe héritée
    def __init__(self, command_prefix, *, intents: discord.Intents, **options: Any):
        super().__init__(command_prefix, intents=intents, **options)

    # Fonction qui tourne au démarrage de l'app
    async def startup(self):
        await self.wait_until_ready() # Att la connexion
        await self.tree.sync(guild=Object(id=TEST-SERVER-ID))
        await self.tree.sync() # Sync les commandes à l'arborescence
        # Ajoute les serveurs que le bot a pu rejoindre lors d'un crash ou d'une maintenance
        g = self.guilds
        g2 = db.get_guilds()
        for server in g:
            if str(server.id) not in g2:
                print(f"Added {server.name} to the database!")
                await db.add_guild(server)
                continue
            for member in server.members:
                if str(member.id) not in g2[str(server.id)] :
                    db.add_member(server, member)
                    print(f"Added {member.name} to the database of the server {server.name}")

        # Débug
        print('Sucessfully synced applications commands')
        print(f'Connected as {self.user}')

    # fonction appelé avant que le bot se connecte
    async def setup_hook(self):
        self.remove_command("help") # Retire la fonction help par défault pour en mettre une custom
        # Charge les cogs
        for filename in os.listdir("cogs"):
            if filename.endswith(".py"):
                try:
                    await self.load_extension(f"cogs.{filename[:-3]}")
                    print(f"Loaded {filename}")
                except Exception as e:
                    print(f"Failed to load {filename}")
                    print(f"[ERROR] {e}")

        self.loop.create_task(self.startup())

    @allowed_installs(guilds=True, users=False)
    async def on_message(self,
                         message: Message,
                         /) -> None:
        """
        DESCRIPTION:
            Runs when new message is sent by any user.

        PARAMETERS:
            message: The message that was sent.

        RETURNS:
             None.
        """
        if type(message.author) == ClientUser:
            return
        await self.process_commands(message)
        if db.get_afk(message.author) != "":
            db.set_afk(message.author, "")
            await message.author.edit(nick=message.author.display_name.replace("[AFK] ", ""))
            await message.channel.send(f"Welcome back, {message.author.mention}! I have removed your AFK!")
        bucket = message_cooldown.get_bucket(message)
        retry_after = bucket.update_rate_limit()
        if retry_after or message.author.id == self.user.id:
            return
        else:
            # Ajoute exp + check si le user a assez d'exp pour level up
            db.change_value(guild=message.guild,
                            user=message.author,
                            index=0,
                            value=50)
            if db.get_user(message.guild, message.author)[0] > 500 + (db.get_user(message.guild, message.author)[1] * (50 * 1.1)):
                db.change_value(guild=message.guild,
                                user=message.author,
                                index=0,
                                value=-db.get_user(message.guild, message.author)[0])
                db.change_value(guild=message.guild,
                                user=message.author,
                                index=1,
                                value=1)
                await message.channel.send(f"{message.author.mention} has leveled up to level {db.get_user(message.guild, message.author)[1]}!")


    async def on_guild_join(self,
                            guild: discord.Guild,
                            /) -> None:
        """
        DESCRIPTION:
            Runs when new guild is joined.

        PARAMETERS:
            guild: The guild that was joined.

        RETURNS:
            None.
        """
        await db.add_guild(guild) # Ajoute le serveur à la db

        chan = discord.utils.get(guild.channels,
                                 name=embed_class.LOGS_CHANNEL)

        # Envoie le message d'acceuil
        await chan.send(embed=embed_class.WELCOME_EMBED)

        # Setup le starboard
        def check(m: discord.Message):
            return m.channel == chan and ((m.content.startswith("<#") and m.content.endswith(">")) or m.content.lower() == "n")

        msg = await self.wait_for(event="message",
                                  check=check)
        if m.content.lower() == "n":
            return await chan.send("I see, thank you for using Hoshiko!")
        channel = await self.fetch_channel(int(msg.content[2:-1]))
        db.set_starboard(guild, channel)
        await chan.send(f"Starboard channel was setup as {channel.jump_url}")

    @guild_install()
    async def on_member_join(self,
                             member: Member) -> None:
        """
        DESCRIPTION:
            Runs when new member joins a server the bot is on.

        PARAMETERS:
            member: The member that joined.

        RETURNS:
            None.
        """
        db.add_member(member.guild, member)
        e = embed_class.LOGS_MEMBER_JOIN(member)
        e.set_thumbnail(url=member.avatar)
        e.set_footer(text="Bot made by @mykado.")
        chan = await self.fetch_channel(db.get_logs(member.guild))
        await chan.send(embed=e)

    @guild_install()
    async def on_member_remove(self, member: Member) -> None:
        """
        DESCRIPTION:
            Runs when member leaves.

        PARAMETERS:
            member: The member that left.

        RETURNS:
            None.
        """
        chan = await self.fetch_channel(db.get_logs(member.guild))
        e = embed_class.LOGS_MEMBER_LEAVE(member)
        e.set_thumbnail(url=member.avatar)
        e.set_footer(text="Bot made by @mykado.")
        await chan.send(embed=e)

    @guild_install()
    async def on_member_update(self,
                               before: Member,
                               after: Member) -> None:
        """
        DESCRIPTION:
            Runs when member updates his profile.

        PARAMETERS:
            before: The member before he updated his profile.
            after: The member after profile update.

        RETURNS:
            None.
        """
        e2 = False
        if before.display_name != after.display_name:
            e = embed_class.LOGS_MEMBER_USERNAME(after, before)
            e.set_thumbnail(url=after.avatar)
            e.set_footer(text="Bot made by @mykado.")
        elif before.avatar != after.avatar:
            e2 = embed_class.LOGS_MEMBER_PFP(after)
            e2.set_footer(text="Bot made by @mykado.")
            e2.set_image(url=before.avatar)
            e = Embed(description="New pfp:")
            e.set_image(url=after.avatar)
        else:
            return None
        chan = await self.fetch_channel(db.get_logs(after.guild))
        if e2:
            await chan.send(embed=e2)
        await chan.send(embed=e)

    @guild_install()
    async def on_message_delete(self,
                                message: Message) -> None:
        """
        DESCRIPTION:
            Runs when message is deleted.

        PARAMETERS:
            message: The message that was deleted.

        RETURNS:
            None.
        """
        if message.author.id == self.user.id:
            return None

        chan = await self.fetch_channel(db.get_logs(message.guild))
        e = embed_class.LOGS_MESSAGE_DELETE(message)
        e.set_thumbnail(url=message.author.avatar)
        e.set_footer(text="Bot made by @mykado.")

        # Regarde si il n'y avait pas de pièces jointes au message
        if len(message.attachments) == 1:
            e.set_image(url=message.attachments[0].proxy_url)
        if len(message.attachments) > 1:
            for att in message.attachments:
                e.description += f"{att.proxy_url}\n"

        await chan.send(embed=e)

    @guild_install()
    async def on_message_edit(self,
                              before: Message,
                              after: Message) -> None:
        """
        DESCRIPTION:
            Runs when a message is edited.

        PARAMETERS:
            before: The message before it was edited.
            after: The edited message.

        RETURNS:
            None.
        """
        if before.author.id == bot.user.id:
            return None

        chan = await self.fetch_channel(db.get_logs(after.guild))
        e = embed_class.LOGS_MESSAGE_EDIT(before, after)
        e.set_thumbnail(url=before.author.avatar)
        e.set_footer(text="Bot made by @mykado.")

        await chan.send(embed=e)

    @guild_install()
    async def on_reaction_add(self,
                              reaction: discord.Reaction,
                              user: discord.Member):
        """
        DESCRIPTION:
            Runs when a reaction is added to a message.

        PARAMETERS:
            reaction: The reaction that was added.
            user: The member that added the reaction.

        RETURNS:
            Coroutine or None.
        """
        if reaction.emoji == "⭐":
            # Si le salon est blacklisted, bah on stop
            if reaction.message.channel.id in db.get_blacklist(user.guild):
                return None

            # Si le message a déjà été posté dans le starboard on edit le message original pour changer le nombre d'étoiles
            channel = await self.fetch_channel(db.get_starboard(user.guild))
            for k, v in db.get_guild_users(user.guild):
                if int(k) == reaction.message.id:
                    mess = await channel.fetch_message(v)
                    return await mess.edit(content=embed_class.STAR_MESSAGE(reaction))

            embed = embed_class.STAR_EMBED(reaction)
            embed.set_author(name=user.display_name,
                             icon_url=user.avatar)
            embed.set_footer(text="Bot made by @mykado.")
            mess = await channel.send(embed_class.STAR_MESSAGE(reaction), embed=embed)
            db.add_message(reaction.message, mess)

    @guild_install()
    async def on_reaction_remove(self,
                                 reaction: discord.Reaction,
                                 user: discord.Member):
        """
        DESCRIPTION:
            Runs when a reaction is removed from a message.

        PARAMETERS:
            reaction: The reaction that was removed.
            user: The member that removed the reaction.

        RETURNS:
            Coroutine or None.
        """
        if reaction.emoji == "⭐":
            if str(reaction.message.id) in db.get_guild_users(user.guild):
                channel = await self.fetch_channel(db.get_starboard(user.guild))
                mess = await channel.fetch_message(db.get_guild_users(user.guild)[str(reaction.message.id)])
                await mess.edit(content=embed_class.STAR_MESSAGE(reaction))


# Instanciation de l'objet bot
bot = Hoshiko(command_prefix="h!",
              intents=discord.Intents.all(),
              strip_after_prefix=True, owner_id=YOUR-USER-ID)


# Lancement de la boucle
bot.run(TOKEN, reconnect=True)