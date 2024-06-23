import discord
from discord.ext import commands
import os
from async_timeout import timeout
import asyncio
from dotenv import load_dotenv
from core import *
from colorama import Fore, Style, init
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Initialize environment and bot settings
init(autoreset=True)
load_dotenv()
TOKEN = os.getenv("KEY")
VERIFIED_MEMBER_ID = os.getenv("MEMBER_ID")
LOGCHANNEL = int(os.getenv("LOGCHANNEL"))
ERRORCHANNEL = int(os.getenv("ERRORCHANNEL"))
intents = discord.Intents.default()
intents.message_content = True
pre = f"{Fore.BLUE}[BOT]{Style.RESET_ALL}"
logger.add("bot.log", format="{time} {level} {message}", level="INFO")
bot = commands.AutoShardedBot(command_prefix="/", intents=intents)


async def send(channel_id, message):
    try:
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.send(message)
        else:
            logger.error(f"Could not find channel with ID: {channel_id}")
    except Exception as e:
        logger.error(f"Error sending message: {e}")


# Commands

@bot.command(name="temp",description="get CPU temprature of the server")
async def temp(ctx):
    try:
        temprature=get_cpu_temperature()
        if temprature:
            await ctx.send(temprature)
        else:
            await ctx.send("something unexpected happened while retrieving temprature")
    except Exception as e:
        logger.warning(f"{pre} {e}")
        await ctx.send(e)

@bot.command(name="storage",description="get storage info about server")
async def storage(ctx):
    try:
        storage = get_available_storage()
        logger.info(f"{pre} retrieving server storage info...")
        await ctx.send(storage)
    except Exception as e:
        logger.warning(f"{pre} {e}")
        await ctx.send(e)

@bot.command(name="uptime",description="get server uptime")
async def uptime(ctx):
    try:
        uptime = get_server_uptime()
        await ctx.send(uptime)
    except Exception as e:
        logger.warning(f"{pre} {e}")
        await ctx.send(e)

@bot.command(name="adduser", description="Add an IG username to get reels from")
async def adduser(ctx, username: str, member_id: str):
    try:
        if member_id == VERIFIED_MEMBER_ID:
            await ctx.send(f"trying to add {username} in records")
            await add_new_account(username)
            await ctx.send(f"User {username} added successfully!")
        else:
            await ctx.send("Invalid member ID. You are not authorized to add users.")
    except Exception as e:
        logger.warning(f"{pre} {e}")
        await ctx.send(e)


@bot.command(name="addchannel", description="Add a channel along with its server's name")
async def addchannel(ctx, username: str, server_name: str, channel_id: int, member_id: str):
    try:
        if member_id == VERIFIED_MEMBER_ID:
            success = add_server(account_name=username, server_name=server_name, channel_id=channel_id)
            if success == 102:
                await ctx.send(f"Account {username} has been added in channel {channel_id} of server {server_name}")
                try:
                    await send(channel_id=channel_id, message=f'Congrats {server_name}!! This Channel is now added in our records.')
                except Exception as e:
                    logger.warning(f"{pre} {e}")
            elif success == 101:
                await ctx.send(f"Server {server_name} already exists in records by channel ID {channel_id}")
            elif success == 103:
                await ctx.send(f"No account found named {username} in records. [TIP: consider adding one]")
            else:
                logger.warning("Unexpected case in addchannel")
                await ctx.send("An unexpected error occurred.")
        else:
            await ctx.send("Entered member ID is wrong.")
    except Exception as e:
        logger.warning(f"{pre} {e}")
        await ctx.send(e)


@bot.command(name="hlp", description="Description of all commands")
async def help(ctx, member_id: str):
    if member_id == VERIFIED_MEMBER_ID:
        await ctx.send("/adduser <insta-username> <verification-id>")
        await ctx.send("/addchannel <insta-username> <name-of-the-server> <channel-id-of-the-server> <verification-id>")
    else:
        await ctx.send("Please enter a correct verification ID")


async def upload_video(bot, channel_id, video_file):
    channel = await bot.fetch_channel(channel_id)
    try:
        if channel:
            await channel.send(file=discord.File(video_file))
            logger.success(f"{pre} Upload has been successful for {video_file}")
            return True
        else:
            logger.warning(f"{pre} Channel {channel_id} not found in records!!")
            return False
    except FileNotFoundError as f:
        logger.error(f"{pre} {f}")
    except Exception as e:
        logger.error(f"{pre} {e}")


async def backend_task():
    update_account_records(query=None)
    data = loadx()
    if data is None:
        await send(ERRORCHANNEL, message=f"loadx() returned None after calling backend_task()")
        return

    for account in data["accounts"]:
        account_name = account["name"]
        msg = f"{pre} Checking for new post for {account_name}"
        await asyncio.sleep(20)
        logger.info(msg)
        await send(LOGCHANNEL, message=msg.replace(f"{pre}",""))
        check_for_post = check_for_new_post(account_name)
        if check_for_post:
            msg = f"{pre} New post found for {account_name}"
            await send(LOGCHANNEL, message=msg.replace(f"{pre}",""))
            latest_post = get_latest_post(account_name)
            if latest_post:
                post_url = get_post_url(latest_post)
                file = f"{latest_post}.mp4"
                dp = dump_post(url=post_url, filename=file)
                if dp:
                    msg = f"Successfully downloaded {file} from {account_name}"
                    await send(LOGCHANNEL, message=msg)
                    update_file(username=account_name, file=file)
                else:
                    e = f"{pre} dump_post() returned False!!!"
                    logger.warning(e)
                    await send(ERRORCHANNEL, message=f"dump_post() returned False while downloading {file} from {account_name}")
            else:
                await send(LOGCHANNEL, message=f"No new post found for {account_name}")
        else:
            await send(LOGCHANNEL, message=f"No new post from {account_name}")


async def frontend_task(bot):
    data = loadx()
    if data is None:
        return

    for account in data["accounts"]:
        files_to_remove = []
        for file in account["files"]:
            all_servers_uploaded = True
            for server in account["server"]:
                server_name = server["name"]
                channel_id = server["channel"]

                if channel_id is None:
                    all_servers_uploaded = False
                    break
                else:
                    upload_success = await upload_video(bot, channel_id=channel_id, video_file=f'temp/{file}')
                    if not upload_success:
                        await send(LOGCHANNEL, message=f"Task file-upload for {file} was not completed in {server_name}, Channel_ID: {channel_id}")
                        all_servers_uploaded = False
                        break
                    elif upload_success:
                        await send(LOGCHANNEL, message=f"Task file-upload for {file} has been successful in {server_name}, Channel_ID: {channel_id}")
                    else:
                        logger.warning(f"Something unexpected happened while sending file:{file} in server:{server['name']}, Channel_ID:{channel_id}")
                        await send(LOGCHANNEL, message=f"Something unexpected happened while sending file:{file} in server:{server_name}, Channel_ID:{channel_id}")
            if all_servers_uploaded:
                await send(LOGCHANNEL, message=f"All files were uploaded in their respective servers without any issue.")
                files_to_remove.append(file)

        for file in files_to_remove:
            account["files"].remove(file)
            await rmfile(file)

        dumpx(data)


async def combined_task():
    msg = "Initiating Backend Task..."
    logger.info(msg)
    await send(LOGCHANNEL, message=msg)
    await backend_task()
    msg = "Initiating Frontend Task..."
    logger.info(msg)
    await send(LOGCHANNEL, message=msg)
    await frontend_task(bot=bot)


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    scheduler = AsyncIOScheduler()
    scheduler.add_job(combined_task, 'interval', hours=3, next_run_time=datetime.now())
    scheduler.start()

check_and_create()
failsafe(query='a')
bot.run(TOKEN, log_handler=None)
