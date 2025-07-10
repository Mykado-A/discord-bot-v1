from datetime import timedelta
from typing import Optional
from discord import Embed, Member, Message, Reaction


class CustomEmbed:

    def __init__(self):
        self.WELCOME_EMBED: Embed = Embed(title="Thank you for adding Hoshiko to your server!",
                                          description="To get started, please define the starboard channel by linking it, or say 'n' if you don't have one. You can change it later by using /setup\n"
                                                      "This bot is still in beta, by a 17 years old student, so expect bugs."
                                                      "Use h!help or /help to aknowledge the bot's functionality.",
                                          color=0x00FF00)
        self.LOGS_CATEGORY: str = "logs"
        self.LOGS_CHANNEL: str = "hoshiko-logs"

    def EMBED_FORMAT(self, embed, user):
        embed.set_author(name=user.display_name, icon_url=user.avatar)
        embed.set_footer(text="Bot made by @mykado.")
        return embed

    def MOD_EMBED(self, user, mod_type: str, reason: str, seconds: Optional[int]):
        e = Embed(title="",
                  description=f"Reason: {reason}",
                  color=0x00A0FF)
        match mod_type:
            case "ban":
                e.title = f"Banned {user.display_name}!"
            case "kick":
                e.title = f"Kicked {user.display_name}!"
            case "timeout":
                e.title = f"Timed out {user.display_name} for {seconds}!"
        return self.EMBED_FORMAT(e, user)




    def LOGS_MEMBER_JOIN(self, member: Member):
        return Embed(title="New member joined!",
                     description=member.mention,
                     color=0x00FF00)
    def LOGS_MEMBER_LEAVE(self, member: Member):
        return Embed(title="A member left...",
                              description=member.mention,
                              color=0x00FF00)
    def LOGS_MEMBER_USERNAME(self, after: Member, before: Member):
        return Embed(title=f"A member changed username!",
                     description=f"{after.mention} : {before.display_name} -> {after.display_name}",
                     color=0x00FF00)
    def LOGS_MEMBER_PFP(self, after: Member):
        return Embed(title=f"A member changed profile picture!",
                     description=f"{after.mention} old pfp :",
                     color=0x00FF00)
    def LOGS_MESSAGE_DELETE(self, message: Message):
        return Embed(title=f"A message was deleted in {message.channel}",
                     description=f"By {message.author.mention} : {message.content}",
                     color=0x00FF00)
    def LOGS_MESSAGE_EDIT(self, before: Message, after: Message):
        return Embed(title=f"A message was edited, {after.jump_url}.",
                     description=f"User :{before.author.mention}\n\n"
                                 f"Before : {before.content}\n"
                                 f"After : {after.content}",
                     color=0x00FF00)

    def STAR_MESSAGE(self, reaction: Reaction):
        return f"{reaction.count} ⭐ | {reaction.message.channel.jump_url}"
    def STAR_EMBED(self, reaction: Reaction):
        return Embed(title="New star post!",
                     description=f"\"{reaction.message.content}\"\n\n"
                                 f"Message sent by {user.display_name}\n"
                                 f"Send at {str(reaction.message.created_at)[11:16]} on {str(reaction.message.created_at)[:10]}\n"
                                 f"Link to message : {reaction.message.jump_url}",
                     colour=0x0000FF)

    def COOLDOWN_EMBED(self, time: timedelta, user: Member):
        return self.EMBED_FORMAT(Embed(title="This command is on cooldown...",
                                 description=f"You can use it again in {time}",
                                 color=0x0000FF),
                                 user=user)

    def BALANCE_EMBED(self, u: Member, bal: int):
        return self.EMBED_FORMAT(Embed(title=f"{u.display_name}'s balance :",
                                       description=f"Money : {bal} 💵",
                                       color=0x0000FF),
                                 user=u)

    def ECO_EMBED(self, user: Member, prompt: str, amount: int):
        return self.EMBED_FORMAT(Embed(title=prompt,
                                       description=f"You earned {amount} 💵!" if amount > 0 else f"You were fined {amount} 💵...",
                                       color=0x0000FF),
                                 user=user)

    def AVATAR_EMBED(self, user: Member):
        e = Embed(title=f"Profile picture of {user.display_name} :",
                  color=0x00A0FF)
        e.set_image(url=user.avatar)
        return self.EMBED_FORMAT(e, user)

    def USER_INFO_EMBED(self, user: Member):
        e = Embed(title=f"Infos of {user.display_name} :",
                  color=0x00A0FF)

        # Tri des serveurs en communs
        g = user.mutual_guilds
        output = []
        for guild in g:
            output.append(guild.name)

        # Affichage pdp du mec demandé, pseudo et pdp du mec qui demande, et la ptite signature
        e.set_thumbnail(url=user.avatar)

        # Date de création compte, et quand la personne à rejoint le serveur
        e.add_field(name="Created:", value=str(user.created_at)[:10])
        e.add_field(name="Joined:", value=str(user.joined_at)[:10])

        # Role le plus haut dans la hiérarchie du mec
        e.add_field(name="Top role:", value=user.top_role.mention)
        # Si l'utilisateur est timeout ou pas, et si oui, jusqu'à quand
        e.add_field(name="Timed out?",
                    value="No" if not user.is_timed_out() else f"Yes, until {str(user.timed_out_until)[:16]}")
        # Serveurs en commun
        e.add_field(name="Mutual servers with bot :", value=", ".join(output), inline=False)

        return self.EMBED_FORMAT(e, user)

embed_class = CustomEmbed()