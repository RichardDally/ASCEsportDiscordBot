import os
import asyncio
import discord
from discord.ext import commands
from loguru import logger
from dotenv import load_dotenv


class GenericBot(commands.Bot):
    def __init__(self, command_prefix='$', help_command=None, description=None):
        super().__init__(command_prefix, help_command, description)
        self.tasks = {}
        self.extra_tasks = {}
        self._stopped = asyncio.Event(loop=self.loop)
        load_dotenv()

    def get_channel_id_by_name(self, channel_name):
        for channel in self.get_all_channels():
            if channel.name == channel_name:
                return channel.id
        return None

    async def logout(self):
        logger.debug('Logout')
        await super().logout()
        self.stop()

    def stop(self):
        def silence_gathered(future):
            try:
                future.result()
            except Exception as exception:
                logger.exception(exception)

        # cancel lingering tasks
        if self.tasks or self.extra_tasks:
            tasks = set()
            for task in self.tasks:
                tasks.add(task)
            for _, extra_tasks in self.extra_tasks:
                for task in extra_tasks:
                    tasks.add(task)
            gathered = asyncio.gather(*tasks, loop=self.loop)
            gathered.add_done_callback(silence_gathered)
            gathered.cancel()

        self._stopped.set()

    def clear(self):
        super().clear()

        self.recursively_remove_all_commands()
        self.extra_events.clear()
        self.tasks.clear()
        self.extra_tasks.clear()
        self.extensions.clear()
        self._stopped.clear()
        self._checks.clear()
        self._check_once.clear()
        self._before_invoke = None
        self._after_invoke = None

    def get_oauth_url(self):
        return discord.utils.oauth_url(self.user.id)

    async def run(self, reconnect=True):
        await self.start(os.getenv("TOKEN"), reconnect=reconnect)
        await self._stopped.wait()
