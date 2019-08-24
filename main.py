import os
import discord
from loguru import logger
from dotenv import load_dotenv

load_dotenv()
client = discord.Client()

@client.event
async def on_ready():
    logger.info(f'[{client.user.name}] has connected to Discord!')


@client.event
async def on_member_join(member):
    logger.info(f'[{member}] just joined')


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    logger.info(f'[{message.author}] just messaged')

# counter = 0
# async for message in channel.history(limit=200):
#     if message.author == client.user:
#         counter += 1


# async def task():
#     await client.wait_until_ready()
#     while True:
#         await asyncio.sleep(1)
#         logger.info('Running')

# client.loop.create_task(task())
# try:
#     client.loop.run_until_complete(client.start(os.getenv("TOKEN")))
# except KeyboardInterrupt:
#     logger.debug('Exiting properly')
#     client.loop.run_until_complete(client.logout())
#     client.loop.close()




import discord
from discord.ext import commands
import asyncio

loop = asyncio.get_event_loop()
bot = commands.Bot(loop=loop)

error = False
error_message = ""
try:
    loop.run_until_complete(bot.run())
except discord.LoginFailure:
    error = True
    error_message = 'Invalid credentials'
except KeyboardInterrupt:
    loop.run_until_complete(bot.logout())
except Exception as exception:
    error = True
    error_message = exception
    loop.run_until_complete(bot.logout())
finally:
    if error:
        print(error_message)
