import asyncio
import math
import sys
import traceback
import types
import discord
from discord.ext import commands
from loguru import logger
from generic_bot import GenericBot


class ASCEsportMember:
    def __init__(self, unique_identifier, name):
        self.unique_identifier = unique_identifier
        self.name = name
        self.roles = []
        self.games = []
        self.mail_pro = None


class Alfred(GenericBot):
    def __init__(self):
        super().__init__(description='Alfred the butler')

    async def on_command_completion(self, ctx):
        logger.debug('On command completion')

    async def on_ready(self):
        logger.debug('On ready')

        # async for guild in self.fetch_guilds():
        #     logger.info(f'Guild [{guild.name}]')
        #     for role in guild.roles:
        #         logger.info(f'Role [{role}]')

        # ascesport_members = {}
        # discord_members = self.get_all_members()
        # for discord_member in discord_members:
        #     if discord_member.id not in ascesport_members.keys():
        #         if discord_member.name == 'JohnRambu':
        #             logger.info(f'JohnRambu [{discord_member}]')
        #         ascesport_member = ASCEsportMember(discord_member.id, discord_member.name)
        #         # Add roles
        #         for role in discord_member.roles:
        #             if role.name != '@everyone':
        #                 logger.info(f'Adding role [{role}] to [{discord_member.name}#{discord_member.id}]')
        #                 ascesport_member.roles.append(role)
        #         ascesport_members[discord_member.id] = ascesport_member
        # for ascesport_member in ascesport_members.values():
        #     if not ascesport_member.roles:
        #         logger.info(f'[{ascesport_member.name}] has no role !')

        # Get count of emoji on pinned message
        id = self.get_channel_id_by_name('accueil-et-annonces')
        channel = self.get_channel(id)
        messages = await channel.history(limit=10).flatten()
        for message in messages:
            for reaction in message.reactions:
                users = await reaction.users().flatten()
                logger.info(f'{reaction.emoji}: [{users}]')



        # Introducing messages history
        # id = self.get_channel_id_by_name('présentations-nouveaux-membres')
        # channel = self.get_channel(id)
        # messages = await channel.history(limit=10).flatten()
        # for message in messages:
        #     logger.info(f'[{message.author}]: [{message.content}]')
        # logger.info('finished')

    async def on_reaction_add(self, reaction, user):
        logger.info(f'[{user}] added [{reaction.emoji}] on [{reaction.message}]')

    async def on_reaction_remove(self, reaction, user):
        logger.info(f'[{user}] removed [{reaction.emoji}] on [{reaction.message}]')

    async def on_reaction_clear(self, message, reactions):
        logger.info(f'[{reactions}] has been removed from [{message}]')

    async def on_restart_message(self, _):
        print("Restarting...")
        await self.logout()

    async def on_message(self, message):
        if message.author == self.user:
            return
        logger.info(f'[{message.author}] says [{message.content}]')

if __name__ == '__main__':
    bot = Alfred()
    error = False
    error_message = ""
    try:
        bot.loop.run_until_complete(bot.run())
    except discord.LoginFailure:
        error = True
        error_message = 'Invalid credentials'
    except KeyboardInterrupt:
        bot.loop.run_until_complete(bot.logout())
    except Exception as exception:
        error = True
        error_message = exception
        bot.loop.run_until_complete(bot.logout())
    finally:
        if error:
            logger.error(error_message)
