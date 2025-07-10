import json

import discord
import datetime
from discord import Member, ClientUser, User
from datetime import datetime
from source.formatting.settings import embed_class

"""
DB PARAMETERS INDEX :
0 = exp
1 = level
2 = money
3 = afk 

Channel = starboard channel
Logs = logs channel
Blacklist = blacklisted channels
"""

class JsonDB:
    def __init__(self, file: str):
        self.file = file
        self.__data = self.get_data()

    def get_data(self) -> dict[str]:
        with open(self.file) as data:
            return json.load(data)

    def __save(self) -> None:
        with open(self.file, 'w', encoding='utf-8') as f:
            return json.dump(self.__data, f, ensure_ascii=False, indent=4)

    def get_guilds(self) -> list[str]:
        return self.__data["Guilds"]

    def get_guild_users(self, guild: discord.Guild) -> list[str]:
        return list(self.__data["Guilds"][str(guild.id)].keys())

    def get_user(self, guild: discord.Guild, user: discord.Member) -> list:
        return self.__data["Guilds"][str(guild.id)][str(user.id)]

    def get_client_users(self):
        return self.__data["Users"]

    def get_logs(self, guild: discord.Guild) -> int:
        return self.__data["Guilds"][str(guild.id)]["Logs"]

    def get_starboard(self, guild: discord.Guild):
        return self.__data["Guilds"][str(guild.id)]["Channel"]

    def get_blacklist(self, guild: discord.Guild) -> list[int]:
        return self.__data["Guilds"][str(guild.id)]["Blacklist"]

    def get_queue(self, guild: discord.Guild) -> list:
        return self.__data["Guilds"][str(guild.id)]["Queue"]

    def get_partner(self, user: User):
        return self.__data["Users"][str(user.id)]["Partner"]

    def get_exes(self, user: User):
        return self.__data["Users"][str(user.id)]["Exes"]

    def get_afk(self, user: Member):
        return self.__data["Guilds"][str(user.guild.id)][str(user.id)][3]

    def get_user_blacklist(self, user: User):
        if str(user.id) not in self.__data["Users"]:
            self.__data["Users"][str(user.id)] = []
        return self.__data["Users"][str(user.id)]

    def set_user_blacklist(self, user: User, tags: list):
        self.__data["Users"][str(user.id)]["Tag_Blacklist"] == tags
        return self.__save()

    def is_guild(self, guild: discord.Guild) -> bool:
        return str(guild.id) in self.__data["Guilds"]

    def is_user_in_guild(self, guild: discord.Guild, user: discord.Member) -> bool:
        return str(user.id) in self.get_guild_users(guild)

    def set_starboard(self, guild: discord.Guild, channel: discord.TextChannel) -> None:
        self.__data["Guilds"][str(guild.id)]["Channel"] = channel.id
        return self.__save()

    def set_blacklist(self, guild: discord.Guild, channel: discord.TextChannel) -> None:
        self.__data["Guilds"][str(guild.id)]["Blacklist"].append(channel.id)
        return self.__save()

    def set_logs(self, guild: discord.Guild, channel: discord.TextChannel) -> None:
        self.__data["Guilds"][str(guild.id)]["Logs"] = channel.id
        return self.__save()

    def set_queue(self, guild: discord.Guild, song: dict) -> None:
        self.__data["Guilds"][str(guild.id)]["Queue"].append(song)
        return self.__save()

    def set_partner(self, user: User, partner: User) -> None:
        date = str(datetime.now())
        self.__data["Users"][str(user.id)]["Partner"] = [partner.id, date]
        self.__data["Users"][str(partner.id)]["Partner"] = [user.id, date]
        return self.__save()

    def set_afk(self, user: discord.Member, afk_message: str):
        self.__data["Guilds"][str(user.guild.id)][str(user.id)][3] = afk_message
        return self.__save()

    def change_value(self, guild: discord.Guild, user: discord.Member, index: int, value: int) -> None:
        self.__data["Guilds"][str(guild.id)][str(user.id)][index] += value
        return self.__save()

    def add_message(self, reacted_message: discord.Message, star_message: discord.Message) -> None:
        self.__data["Guilds"][str(reacted_message.guild.id)][str(reacted_message.id)] = star_message.id
        return self.__save()

    async def add_guild(self, guild: discord.Guild) -> None:
        self.__data["Guilds"][str(guild.id)] = {"Channel": 0, "Logs": 0, "Blacklist": [], "Queue": []} | {str(m.id): [0, 1, 0, ""] for m in guild.members}
        logs = discord.utils.get(guild.categories,
                                 name=embed_class.LOGS_CATEGORY)
        if logs is None:
            await guild.create_category(embed_class.LOGS_CATEGORY)
            logs = discord.utils.get(guild.categories,
                                     name=embed_class.LOGS_CATEGORY)
        perms = logs.overwrites_for(obj=guild.default_role)
        perms.view_channel = False
        await logs.set_permissions(guild.default_role,
                                   overwrite=perms)

        chan = discord.utils.get(guild.channels,
                                 name=embed_class.LOGS_CHANNEL)
        if chan is None:
            await logs.create_text_channel(embed_class.LOGS_CHANNEL)
        self.set_logs(guild, chan)
        return self.__save()

    def add_member(self, guild: discord.Guild, user: discord.Member) -> None:
        self.__data["Guilds"][str(guild.id)][str(user.id)] = [0, 1, 0, ""]
        return self.__save()

    def add_client_user(self, user: User):
        self.__data["Users"][str(user.id)] = {"Partner": [], "Tag_Blacklist": [], "Exes": [0]}
        return self.__save()

    def remove_blacklist(self, guild: discord.Guild, channel: discord.TextChannel) -> None:
        self.__data["Guilds"][str(guild.id)]["Blacklist"].remove(channel.id)
        return self.__save()

    def remove_queue(self, guild: discord.Guild):
        self.__data["Guilds"][str(guild.id)]["Queue"].pop(0)
        return self.__save()

    def clear_queue(self, guild: discord.Guild):
        while self.__data["Guilds"][str(guild.id)]["Queue"]:
            self.__data["Guilds"][str(guild.id)]["Queue"].pop()
        return self.__save()

    def divorce(self, user: User, partner: User):
        self.__data["Users"][str(user.id)]["Partner"] = []
        self.__data["Users"][str(partner.id)]["Partner"] = []
        self.__data["Users"][str(user.id)]["Exes"][0] += 1
        self.__data["Users"][str(partner.id)]["Exes"][0] += 1
        self.__data["Users"][str(user.id)]["Exes"].append(partner.name)
        self.__data["Users"][str(partner.id)]["Exes"].append(user.name)
        return self.__save()

#Insert database path
db = JsonDB("database-path-here")