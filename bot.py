import discord
from discord.ext import commands
import os
from async_timeout import timeout
import asyncio
from dotenv import load_dotenv
from core import *
import logging
import logging.handlers
from colorama import Fore, Style, init
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
# Initialize environment and bot settings
init(autoreset=True)
load_dotenv()
TOKEN = os.getenv("KEY")
VERIFIED_MEMBER_ID = os.getenv("MEMBER_ID")
LOGCHANNEL=os.getenv("LOGCHANNEL")
intents = discord.Intents.default()
intents.message_content = True
pre = f"{Fore.BLUE}[BOT]{Style.RESET_ALL}"
#logger.add("bot.log", format="{time} {level} {message}", level="INFO")
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
logging.getLogger('discord.http').setLevel(logging.INFO)
handler = logging.handlers.RotatingFileHandler(
    filename='discord.log',
    encoding='utf-8',
    maxBytes=32 * 1024 * 1024,  # 32 MiB
    backupCount=5,  # Rotate through 5 files
)
dt_fmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
handler.setFormatter(formatter)
logger.addHandler(handler)
bot = commands.AutoShardedBot(command_prefix="/", intents=intents)


async def send_message(channel_id, message):
    await bot.wait_until_ready()
    channel = bot.fetch_channel(channel_id)
    if channel:
        await channel.send(message)
    else:
        print(f"Could not find channel with ID: {channel_id}")

# Commands
@bot.command(name="temprature",description="return the temprature of the server",category="server configuration")
async def temprature(ctx):
    try:
        await ctx.send("recieving info...")
        temprature=get_cpu_temperature()
        await ctx.send(f"{temprature} *C")
        logger.info(f" get_cpu_temprature was called, returned -> {temprature} *C")
    except Exception as e:
        logger.warning(f"{pre} {e}")
        await ctx.send(e)

@bot.commmand(name="uptime",description="return the uptime of the server",category="server configuration")
async def uptime(ctx):
    try:
        await ctx.send("recieving info...")
        uptime = get_server_uptime()
        await ctx.send(f"{uptime}")
        logger.info(f"{pre} get_server_uptime() was called, returned -> {uptime}")
    except Exception as e:
        logger.warning(f"{pre} {e}")
        await ctx.send(e)

@bot.command(name="storage",description="get storage info",category="server configuration")
async def storage(ctx):
    try:
        await ctx.send("recieving info...")
        total,used,free=get_available_storage()
        await ctx.send(f"total={total} GB, used={used} GB, free={free} GB")
        logger.info(f"{pre} get_available_storage was called, returned -> free={free},total={total},used={used}")
    except Exception as e:
        logger.warning(f"{pre} {e}")
        await ctx.send(e)

@bot.command(name="adduser", description="Add an IG username to get reels from")
async def adduser(ctx, username: str, member_id: str):
    try:

        if member_id == VERIFIED_MEMBER_ID:
            await ctx.send(f"trying to add {username} in records")
            try:
                success=add_new_account(username)
                if success:
                    await ctx.send(f"User {username} added successfully!")
                    logger.info(f"User {username} added successfully!")
            except Exception as e:
                await ctx.send(f"{e}")
                logger.warning(f"{pre} {e}")
        else:
            await ctx.send("Invalid member ID. You are not authorized to add users.")
    except Exception as e:
        logger.warning(f"{pre_bot} {e}")
        await ctx.send(e)

@bot.command(name="rmuser", description="Remove an IG username from the records")
async def removeuser(ctx, username: str, member_id: str):
    try:
        if member_id == VERIFIED_MEMBER_ID:
            await ctx.send(f"Trying to remove {username} from records")
            try:
                success = await remove_account(username)
                if success:
                    await ctx.send(f"User {username} removed successfully!")
                else:
                    await ctx.send(f"User {username} was not removed (see logs for more info)")
            except Exception as e:
                await ctx.send("there was an unexpected error (see logs for more info)")
                logger.warning(f"{pre} {e}")
        else:
            await ctx.send("Invalid member ID. You are not authorized to remove users.")
    except Exception as e:
        logger.warning(f"{pre_bot} {e}")
        await ctx.send(e)

@bot.command(name="addchannel", description="Add a channel along with its server's name")
async def addchannel(ctx, username: str, server_name: str, channel_id: int, member_id: str):
    try:
        if member_id == VERIFIED_MEMBER_ID:
            success = add_server(account_name=username, server_name=server_name, channel_id=channel_id)
            if success == 102:
                await ctx.send(f"account {username} has been added in channel {channel_id} of server {server_name}")
                try:
                    await send_message(channel_id=channel_id,message=f'Congrats {server_name}!! We have added {username}. ')
                except Exception as e:
                    logger.warning(f"{pre_bot} {e}")
            elif success == 101:
                await ctx.send(f"server {server_name} already exists in records by channel id {channel_id}")
            elif success == 103:
                await ctx.send(f"No account found named {username} in records. [TIP: consider adding one]")
            else:
                logger.warning("Unexpected case in addchannel")
                await ctx.send("An unexpected error occurred.")
        else:
            await ctx.send("Entered member ID is wrong.")
    except Exception as e:
        logger.warning(f"{pre_bot} {e}")
        await ctx.send(e)

@bot.command(name="removechannel", description="Remove a channel from the records")
async def removechannel(ctx, username: str, server_name: str, channel_id: int, member_id: str):
    try:
        if member_id == VERIFIED_MEMBER_ID:
            success = remove_server(account_name=username, server_name=server_name, channel_id=channel_id)
            if success:
                await ctx.send(f"Channel {channel_id} of server {server_name} removed for account {username}")
            else:
                await ctx.send(f"No matching record found for server {server_name} and channel {channel_id}")
        else:
            await ctx.send("Entered member ID is wrong.")
    except Exception as e:
        logger.warning(f"{pre_bot} {e}")
        await ctx.send(e)

@bot.command(name="hlp", description="Description of all commands")
async def help(ctx, member_id: str):
    if member_id == VERIFIED_MEMBER_ID:
        await ctx.send("/adduser <insta-username> <verification-id>")
        await ctx.send("/addchannel <insta-username> <name-of-the-server> <channel-id-of-the-server> <verification-id>")
    else:
        await ctx.send("Please enter a correct verification ID")

@bot.command(name="sendnotice", description="Send notice to all servers")
async def sendnotice(ctx,notice:str):
    try:
        data = loadx()
        if data is None:
            await ctx.send("Error: Unable to load data from records.json")
            return

        for account in data["accounts"]:
            for server in account["server"]:
                channel_id = server["channel"]
                name=server['name']
                try:
                    channel = await bot.fetch_channel(channel_id)
                    if channel:
                        await channel.send(notice)
                        await ctx.send(f"Notice sent to server {name} (Channel ID: {channel_id})")
                        logger.info(f"Notice sent to server {name} (Channel ID: {channel_id})")
                    else:
                        await ctx.send(f"Channel with ID {channel_id} not found.")
                        logger.warning(f"Channel with ID {channel_id} not found.")
                except Exception as e:
                    await ctx.send(f"Error sending notice to server {name}: {e}")
                    logger.warning(f"Error sending notice to server {name}: {e}")
    except Exception as e:
        await ctx.send(f"Error: {e}")
        logger.warning(f"{pre} {e}")

async def upload_video(bot, channel_id, video_file):
    channel = await bot.fetch_channel(channel_id)
    try:

        if channel:
            message=await channel.send(file=discord.File(video_file))
            await message.add_reaction("👍")
            await message.add_reaction("🌟")
            await message.add_reaction("💀")
            logger.success(f"{pre_bot} upload has been successfull for {video_file} in Channel ID: {channel_id}")
            return True
        else:
            logger.warning(f"{pre_bot} channel {channel} not found in records!!")
            return False
    except FileNotFoundError as f:
        logger.error(f"{pre_bot} {f}")
    except Exception as e:
        logger.error(f"{pre_bot} {e}")

def backend_task():
    logger.info("[check_new_posts] Starting check_new_posts")
    update_account_records(query=None)
    update_server_count()
    data = loadx()
    if data is None:  # Check if data is loaded properly.
        return

    for account in data["accounts"]:
        account_name = account["name"]
        logger.info(f"[check_new_posts] Checking for new post for {account_name}")
        check_for_post = check_for_new_post(account_name)
        if check_for_post:
            latest_post = get_latest_post(account_name)
            if latest_post:
                post_url = get_post_url(latest_post)
                file = f"{latest_post}.mp4"
                dp = dump_post(url=post_url, filename=file)
                if dp:
                    update_file(username=account_name, file=file)
                else:
                    logger.warning(f"Error in dump_post ~ false")
            else:
                logger.info(f"No new post found for account {account_name}")
        else:
            logger.info(f"No new post to check for account {account_name}")

async def frontend_task(bot):
    data = loadx()
    if data is None:  
        return

    for account in data["accounts"]:
        files_to_remove = []
        for file in account["files"]:
            all_servers_uploaded = True
            for server in account["server"]:
                channel_id = server["channel"]
                if channel_id is None:
                    all_servers_uploaded = False
                    break  
                else:
                    upload_success = await upload_video(bot, channel_id=channel_id, video_file=f'temp/{file}')
                    if not upload_success:
                        all_servers_uploaded = False
                        break  
                    elif upload_success:
                        await send_message(channel_id=LOGCHANNEL,message=f"task file-upload for {file} has been successful in {server["name"]}, channel_ID: {channel_id}")
                    else:
                        logger.warning(f"something unexpected happened while sending file:{file} in server:{server['name']}, channel_ID:{channel_id}")
                        await send_message(channel_id=LOGCHANNEL,message=f"something unexpected happened while sending file:{file} in server:{server['name']}, channel_ID:{channel_id}")
            if all_servers_uploaded:
                files_to_remove.append(file)

        for file in files_to_remove:
            account["files"].remove(file)
            await rmfile(file)

        dumpx(data)  

async def combined_task():
    loop = asyncio.get_event_loop()
    logger.info(f"{pre} Initiating backend task")
    await loop.run_in_executor(None, backend_task)
    logger.info(f"{pre} Initiatingfrontend task")
    await frontend_task(bot=bot)
        
@bot.event
async def on_ready():
    logger.info(f'We have logged in as {bot.user}')
    scheduler = AsyncIOScheduler()
    scheduler.add_job(combined_task, 'interval', hours=4,next_run_time=datetime.now())
    scheduler.start()

check_and_create()
failsafe(query='a')
bot.run(TOKEN)
