import asyncio
import math
import sys
import traceback
import types
import discord
from discord.ext import commands
from loguru import logger
from generic_bot import GenericBot


class Alfred(GenericBot):
    def __init__(self):
        super().__init__(description='Alfred the butler')



    async def on_command_completion(self, ctx):
        logger.debug('On command completion')

    async def on_ready(self):
        logger.debug('On ready')
        id = self.get_channel_id_by_name('présentations-nouveaux-membres')
        channel = self.get_channel(id)
        messages = await channel.history(limit=10).flatten()
        for message in messages:
            logger.info(f'[{message.author}]: [{message.content}]')

    async def on_restart_message(self, _):
        print("Restarting...")
        await self.logout()

    async def on_message(self, message):
        if message.author == self.user:
            return
        logger.info(f'[{message.author}] says [{message.content}]')

    async def wait_for_response(self, ctx, message_check=None, timeout=60):
        def response_check(message):
            is_response = ctx.message.author == message.author and ctx.message.channel == message.channel
            return is_response and message_check(message) if callable(message_check) else True

        try:
            response = await self.wait_for('message', check=response_check, timeout=timeout)
        except asyncio.TimeoutError:
            return None
        return response.content

    async def wait_for_answer(self, ctx, timeout=60):
        def is_answer(message):
            return message.content.lower().startswith('y') or message.content.lower().startswith('n')

        answer = await self.wait_for_response(ctx, message_check=is_answer, timeout=timeout)
        if answer is None:
            return None
        if answer.lower().startswith('y'):
            return True
        if answer.lower().startswith('n'):
            return False

    async def wait_for_choice(self, ctx, choices, timeout=60):
        if isinstance(choices, types.GeneratorType):
            choices = list(choices)

        choice_format = "**{}**: {}"

        def choice_check(message):
            try:
                return int(message.content.split(maxsplit=1)[0]) <= len(choices)
            except ValueError:
                return False

        paginator = commands.Paginator(prefix='', suffix='')
        for i, _choice in enumerate(choices, 1):
            paginator.add_line(choice_format.format(i, _choice))

        for page in paginator.pages:
            await ctx.send(page)

        choice = await self.wait_for_response(ctx, message_check=choice_check, timeout=timeout)
        if choice is None:
            return None
        return int(choice.split(maxsplit=1)[0])

    async def send_command_help(self, ctx):
        if ctx.invoked_subcommand:
            pages = await self.formatter.format_help_for(ctx, ctx.invoked_subcommand)
            for page in pages:
                await ctx.send(page)
        else:
            pages = await self.formatter.format_help_for(ctx, ctx.command)
            for page in pages:
                await ctx.send(page)

    async def on_command_error(self, ctx, error, ignore_local_handlers=False):
        if not ignore_local_handlers:
            if hasattr(ctx.command, 'on_error'):
                return

        # get the original exception
        error = getattr(error, 'original', error)

        if isinstance(error, commands.CommandNotFound):
            return

        if isinstance(error, commands.BotMissingPermissions):
            missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in error.missing_perms]
            if len(missing) > 2:
                fmt = '{}, and {}'.format("**, **".join(missing[:-1]), missing[-1])
            else:
                fmt = ' and '.join(missing)
            _message = 'I need the **{}** permission(s) to run this command.'.format(fmt)
            await ctx.send(_message)
            return

        if isinstance(error, commands.DisabledCommand):
            await ctx.send('This command has been disabled.')
            return

        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send("This command is on cooldown, please retry in {}s.".format(math.ceil(error.retry_after)))
            return

        if isinstance(error, commands.MissingPermissions):
            missing = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in error.missing_perms]
            if len(missing) > 2:
                fmt = '{}, and {}'.format("**, **".join(missing[:-1]), missing[-1])
            else:
                fmt = ' and '.join(missing)
            _message = 'You need the **{}** permission(s) to use this command.'.format(fmt)
            await ctx.send(_message)
            return

        if isinstance(error, commands.UserInputError):
            await ctx.send("Invalid input.")
            await self.send_command_help(ctx)
            return

        if isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send('This command cannot be used in direct messages.')
            except discord.HTTPException:
                pass
            return

        if isinstance(error, commands.CheckFailure):
            await ctx.send("You do not have permission to use this command.")
            return

        # ignore all other exception types, but print them to stderr
        # and send it to ctx if settings.DEBUG is True
        await ctx.send("An error occured while running the command **{0}**.".format(ctx.command))

        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


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
