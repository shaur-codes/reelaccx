import discord
import os
import asyncio
import requests
from dotenv import load_dotenv
from core import *
from loguru import logger
from colorama import Fore, Style, init


init(autoreset=True)
load_dotenv()
TOKEN = os.getenv("KEY")


intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
pre = f"{Fore.BLUE}[BOT]{Style.RESET_ALL}"
logger.add("bot.log", format="{time} {level} {message}", level="INFO")


async def upload_video(channel_id: int, video_file: str) -> bool:
    try:
        channel = await client.fetch_channel(channel_id)
        with open(video_file, 'rb') as file:
            await channel.send(file=discord.File(file))
        logger.info(f"{pre} Video '{video_file}' uploaded to {channel.mention}")
        return True
    except discord.NotFound:
        logger.error(f"{pre} Channel not found. Make sure the channel ID is correct.")
        return False
    except Exception as e:
        logger.error(f"{pre} Error uploading video: {e}")
        return False


async def is_connected():
    url = 'https://google.com'
    logger.info(f"{pre} Checking the connectivity of internet...")
    try:
        requests.get(url)
        logger.info(f"{pre} We are up and running")
    except Exception as e:
        logger.warning(f"{pre} We are not connected to internet... Trying again in 30 seconds")
        await asyncio.sleep(30)
        await is_connected()


async def main():
    await update_account_records(query=None)
    data = loadx()

    for account in data["accounts"]:
        account_name = account["name"]
        check_for_post = await check_for_new_post(account_name)
        if check_for_post:
            latest_post = get_latest_post(account_name)
            if latest_post:
                post_url = await get_post_url(latest_post)
                file = f"{latest_post}.mp4"
                dp = await dump_post(url=post_url, filename=file)
                if dp:
                    for server in account['server']:
                        server_name = server['name']
                        channel = server['channel']
                        load_video = await upload_video(channel_id=channel, video_file=file)
                        if load_video:
                            logger.info(f"{pre} Upload has been successful for {server_name}")
                    logger.info(f"{pre} Deleting file {file}")
                    os.remove(file)
                else:
                    logger.error(f"{pre} Error in -> dump_post ~ false")
            else:
                logger.info(f"{pre} No new post found for account {account_name}")
        else:
            logger.info(f"{pre} No new post to check for account {account_name}")

@client.event
async def on_ready():
    logger.info(f"{pre} We have logged in as {client.user}")
    await is_connected()
    while True:
        await main()
        logger.info(f"{pre} Waiting for 1 hour")
        await asyncio.sleep(3600)

client.run(TOKEN)
