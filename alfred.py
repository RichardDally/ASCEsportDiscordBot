import discord
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
        self.role_assignment_channel_title = "role-assignment"

        self.reaction_to_role = {":LoL:615961262932623399":          613731456556072990,
                                 ":apexlegends:615965083713142784":  614008604961538048,
                                 ":csgo:615965136854712352":         614008371506577408,
                                 ":dota2:615965157838946305":        614009813202108436,
                                 ":fifa:615965174498721798":         614026002888392707,
                                 ":fortnite:615965194727718912":     614372277093400585,
                                 ":hearthstone:615965215086870528":  614009631026708481,
                                 ":overwatch:615965258623746068":    614007383408246899,
                                 ":pes:615965273983287306":          617068726503735296,
                                 ":r6s:615965301535670273":          614009408820609024,
                                 ":rocketleague:615965320019968052": 614181946766917642,
                                 ":switch:615965332825309190":       614181957731090442,
                                 ":wow:615965343105679362":          614006753499283460,
                                 ":cod:617069598730223696":          617069986321530970,
                                 ":battlefield:617069580229148732":  614372546640347147,
                                 ":hots:617069644133695488":         614368339200049152}

    async def on_command_completion(self, ctx):
        logger.debug('On command completion')

    async def create_role_assignment_pinned_message(self):
        id = self.get_channel_id_by_name(self.role_assignment_channel_title)
        channel = self.get_channel(id)
        e = discord.Embed(
            title="React with each of games you play on by clicking on the corresponding platform icon below.")
        await channel.send("Role Assignment", embed=e)
        my_last_message = await channel.history().get(author=self.user)
        await my_last_message.pin()
        return my_last_message

    def get_cleaned_reaction_str(self, reaction):
        return str(reaction).replace('<', '').replace('>', '')

    async def add_missing_reactions(self, role_assignment_message):
        reactions_to_add = list(self.reaction_to_role.keys())

        if role_assignment_message.reactions:
            # Ensure there is no missing reactions (remove already added from reference list)
            for reaction in role_assignment_message.reactions:
                cleaned_reaction = self.get_cleaned_reaction_str(reaction)
                if cleaned_reaction in reactions_to_add:
                    reactions_to_add.remove(cleaned_reaction)

        if reactions_to_add:
            logger.info(f"Missing emojis [{reactions_to_add}]")
            for reaction in reactions_to_add:
                await role_assignment_message.add_reaction(reaction)

    async def send_message(self, channel, message):
        id = self.get_channel_id_by_name(channel)
        channel = self.get_channel(id)
        await channel.send(message)

    async def get_role_assignment_pinned_message(self):
        id = self.get_channel_id_by_name(self.role_assignment_channel_title)
        channel = self.get_channel(id)
        async for message in channel.history():
            if message.author == self.user and message.content == "Role Assignment":
                return message
        return None

    async def add_role_if_necessary(self, member, role):
        if role not in member.roles:
            logger.info(f"Adding [{role.name}] to [{member.name}]")
            await member.add_roles(role)
        else:
            logger.debug(f"Adding [{role.name}] was not necessary for [{member.name}]")

    def log_regular_roles(self):
        roles = self.get_game_roles()
        for role in roles:
            logger.info(f"Role [{role.name}] [{role.id}]")

    def get_role(self, role_name: str):
        """
        Find a role by name
        """
        for guild in self.guilds:
            for role in guild.roles:
                if role.name == role_name:
                    return role
        return None

    async def get_assignment_role_reactions(self, role_assignment_message):
        members_reactions = {}
        logger.debug(f"Reactions size [{len(role_assignment_message.reactions)}]")
        for reaction in role_assignment_message.reactions:
            users = await reaction.users().flatten()

            cleaned_reaction = self.get_cleaned_reaction_str(reaction)
            # logger.debug(f"Current reaction [{cleaned_reaction}]")
            role_to_add = self.reaction_to_role[cleaned_reaction]
            # logger.debug(f"Role to add [{role_to_add}]")

            for member in users:
                if member == self.user:
                    continue

                role_already_assigned = False
                for existing_role in member.roles:
                    if existing_role.id == role_to_add:
                        role_already_assigned = True
                        # logger.debug(f"Role [{existing_role.id}] already exists in member roles [{member.roles}]")
                        break

                if role_already_assigned:
                    continue

                if member not in members_reactions:
                    members_reactions[member] = []
                # Add role to assign for this member
                members_reactions[member].append(role_to_add)
        return members_reactions

    async def on_ready(self):
        logger.debug('On ready')

        # Retrieve role assignment pinned message
        role_assignment_message = await self.get_role_assignment_pinned_message()
        if role_assignment_message is None:
            role_assignment_message = await self.create_role_assignment_pinned_message()

        # Step 2: add missing reactions (e.g. new game added => new channel => new emoji)
        await self.add_missing_reactions(role_assignment_message)

        # Step 3: retrieve only role reactions to apply (compare existing roles with reactions)
        role_reactions = await self.get_assignment_role_reactions(role_assignment_message)
        logger.debug(role_reactions)

        # Debug purpose
        for member, role_identifiers in role_reactions.items():
            # very verbose log
            for role_identifier in role_identifiers:
                for key, value in self.reaction_to_role.items():
                    if value == role_identifier:
                        logger.debug(f"Member [{member.name} should be in [{key}]")

        # Step 4: add role to members that reacted on self-assignment message emojis
        game_roles = self.get_game_roles()
        for member, role_identifiers in role_reactions.items():
            for role_identifier in role_identifiers:
                role = game_roles[role_identifier]
                logger.info(f"Adding role [{role.name}] to [{member.name}]")
                await member.add_roles(role)

        # Display all Guild emojis
        # for emoji in self.get_emojis():
        #     logger.info(emoji)

        # await self.send_message(channel="alfred-safe-house", message="Last test")
        # await self.get_role_assignment_pinned_message()

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
        # id = self.get_channel_id_by_name('accueil-et-annonces')
        # channel = self.get_channel(id)
        # messages = await channel.history(limit=10).flatten()
        # for message in messages:
        #     for reaction in message.reactions:
        #         users = await reaction.users().flatten()
        #         logger.info(f'{reaction.emoji}: [{users}]')

        # EMOJI_POSITIVE = "\U0001F44D"
        # EMOJI_NEGATIVE = "\U0001F44E"
        # id = self.get_channel_id_by_name('alfred-safe-house')
        # channel = self.get_channel(id)
        # await channel.send("Role Assignment", embed=e)
        # e = discord.Embed(title="React with each of games you play on by clicking on the corresponding platform icon below.")
        # await channel.send("Role Assignment", embed=e)
        # my_last_message = await channel.history().get(author=self.user)
        # await my_last_message.pin()
        # await my_last_message.add_reaction(':LoL:615961262932623399')
        # await my_last_message.add_reaction(":apexlegends:615965083713142784")
        # await my_last_message.add_reaction(":csgo:615965136854712352")
        # await my_last_message.add_reaction(":dota2:615965157838946305")
        # await my_last_message.add_reaction(":fifa:615965174498721798")
        # await my_last_message.add_reaction(":fortnite:615965194727718912")
        # await my_last_message.add_reaction(":hearthstone:615965215086870528")
        # await my_last_message.add_reaction(":overwatch:615965258623746068")
        # await my_last_message.add_reaction(":pes:615965273983287306")
        # await my_last_message.add_reaction(":r6s:615965301535670273")
        # await my_last_message.add_reaction(":rocketleague:615965320019968052")
        # await my_last_message.add_reaction(":switch:615965332825309190")
        # await my_last_message.add_reaction(":wow:615965343105679362")


        # Introducing messages history
        # id = self.get_channel_id_by_name('présentations-nouveaux-membres')
        # channel = self.get_channel(id)
        # messages = await channel.history(limit=10).flatten()
        # for message in messages:
        #     logger.info(f'[{message.author}]: [{message.content}]')
        # logger.info('finished')

        # Retrieve users that reacted on message
        # users = await reaction.users().flatten()


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

    def get_emojis(self):
        result = []
        for guild in self.guilds:
            for emoji in guild.emojis:
                result.append(emoji)
        return result

    def get_game_roles(self) -> dict:
        roles = {}
        for guild in self.guilds:
            for role in guild.roles:
                if role.name in ['Admins', '@everyone', 'Majordome']:
                    continue
                roles[role.id] = role
        return roles

    async def on_member_join(self, member):
        """
        Automatically assign "Non présentés" role to new joiners.
        """
        if not member.bot:
            role = self.get_role("Non présentés")
            await member.add_roles(role)
            logger.debug(f'Member [{member.name}] is now assigned to [{role.name}]')


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
