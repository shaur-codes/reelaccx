import discord
from discord.ext import commands
import os
import asyncio
import aiohttp
from dotenv import load_dotenv
from core import *
from loguru import logger
from colorama import Fore, Style, init


#vars
init(autoreset=True)
load_dotenv()
TOKEN = os.getenv("KEY")
VERIFIED_MEMBER_ID=os.getenv("MEMBER_ID")
intents = discord.Intents.default()
intents.message_content = True
pre = f"{Fore.BLUE}[BOT]{Style.RESET_ALL}"
logger.add("bot.log", format="{time} {level} {message}", level="INFO")
# bot = commands.Bot(command_prefix="/",intents=intents)
bot = commands.AutoShardedBot(command_prefix="/", intents=intents)


#COMMAND
@bot.command(name="adduser", description="add an IG username to get reels from ")
async def adduser(ctx, username: str, member_id: str):
    if member_id == VERIFIED_MEMBER_ID:
        await add_new_account(username)
        await ctx.send(f"User {username} added successfully!")
    else:
        await ctx.send("Invalid member ID. You are not authorized to add users.")

@bot.command(name="addchannel",description="add a channel along with its server's name")
async def addchannel(ctx, username:str, server_name: str, channel_id: int, member_id: str):
    try:
        if member_id == VERIFIED_MEMBER_ID:
            try:
                success = add_server(account_name=username, server_name=server_name, channel_id=channel_id)
                if success==102:
                    await ctx.send(f"{username} has been added in {channel_id} of {server_name}")
                elif success==101:
                    await ctx.send(f"{server_name} already exists in records by channel id {channel_id}")
                elif success==103:
                    await ctx.send(f"no account found named as {username} in records.[TIP:consider adding one]")
                else:
                    logger.warning(f"kuchh to scene ho gaya hai bhai!!!")
                    await ctx.send(f"KUCHH TO HO GAYA HAI")
                    await ctx.send(f"https://discord.com/channels/1246054708716769321/1246055019594121226/1248612026335498292")
            except Exception as e:
                raise Exception(f"Error adding server: {e}")
        else:
            await ctx.send("Entered member ID is wrong.")
    except Exception as e:
        raise Exception(f"Error: {e}")

@bot.command(name="hlp", description="description of all commands")
async def help(ctx,member_id:str):
    try:

        if member_id==VERIFIED_MEMBER_ID:
            await ctx.send("/adduser <insta-username> <verification-id>")
            await ctx.send("/addchannel <insta-username-i.e.-present-in-records> <name-of-the-server> <channel-id-of-the-server> <verification-id>")
        else:
            await ctx.send("please enter a correct verification ID")
    except Exception as e:
        await ctx.send(e)


#EVENT
async def upload_video(channel_id: int, video_file: str) -> bool:
    try:
        channel = await bot.fetch_channel(channel_id)
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

async def dump_pending(username,channel,filename):
    data = loadx()
    data["pending"].append({
        "account_name": username,
        "channels": channel,
        "pending_shortcodes": [filename.replace(".mp4", "")]
    })
    dumpx(data)

async def retry_pending_uploads(): #posts that were not downloaded for some reason and therefore not uploaded
    logger.info(f"{pre_bot} retrying to upload pending files")
    data = loadx()
    for pending in data["pending"]:
        account_name = pending["username"]
        channels = pending["channels"]
        for shortcode in pending["pending_shortcodes"]:
            post_url = await get_post_url(shortcode)
            file = f"{shortcode}.mp4"
            dp = await dump_post(url=post_url, filename=file, account_name=account_name, channels=channels)
            if dp:
                for channel in channels:
                    load_video = await upload_video(channel_id=channel, video_file=file)
                    if load_video:
                        logger.info(f"{pre} Upload has been successful for {channel}")
                logger.info(f"{pre} Deleting file {file}")
                os.remove(file)
                pending["pending_shortcodes"].remove(shortcode)
    dumpx(data)

async def is_connected():
    url = 'https://discord.com'
    logger.info(f"{pre} Checking the connectivity of internet...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    logger.info(f"{pre} We are up and running")
                else:
                    logger.warning(f"{pre} Received non-200 status code: {response.status}")
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
                    logger.warning(f"{pre} Error in -> dump_post ~ false")
                    dump_pending(username=account_name,channel=channel,filename=file)
            else:
                logger.info(f"{pre} No new post found for account {account_name}")
        else:
            logger.info(f"{pre} No new post to check for account {account_name}")

@bot.event
async def on_ready():
    logger.info(f"{pre} We have logged in as {bot.user}")
    bot.loop.create_task(main_loop())

async def main_loop():
    while True:
        try:
            await is_connected()
            await main()
            logger.info(f"{pre} Waiting for 1 hour")
            await asyncio.sleep(30)
        except Exception as e:
            logger.error(f"{pre} Error in main loop: {e}")
            await asyncio.sleep(60) 

bot.run(TOKEN)
