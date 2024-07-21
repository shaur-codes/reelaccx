import discord
from discord.ext import commands
import os
from async_timeout import timeout
import asyncio
from dotenv import load_dotenv
from core import *
from discord import app_commands
from discord.ext.commands import Bot
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
APP_ID=os.getenv("APP_ID")
intents = discord.Intents.default()
intents.message_content = True
pre = f"{Fore.BLUE}[BOT]{Style.RESET_ALL}"
logger.add("bot.log", format="{time} {level} {message}", level="INFO")
bot = Bot(command_prefix="/", intents=intents,application_id=APP_ID)


async def send_message(channel_id, message):
    await bot.wait_until_ready()
    channel = await bot.fetch_channel(channel_id)
    if channel:
        await channel.send(message)
    else:
        print(f"Could not find channel with ID: {channel_id}")

# Commands
@bot.tree.command(name="hello")
@app_commands.describe(say_hi = "say hi")
async def hello(interaction:discord.Interaction,say_hi:str):
    if not interaction.response.is_done():
        await interaction.response.defer()
        await interaction.followup.send(f"hi {interaction.user.mention}",ephemeral=True)
        #await interaction.edit_original_response(const)

@bot.tree.command(name="temprature")
@app_commands.describe()
async def temprature(interaction:discord.Interaction):
    if not interaction.response.is_done():
        await interaction.response.defer()
        try:
            #await interaction.response.send_message("recieving info...")
            temprature=get_cpu_temperature()
            await interaction.followup.send(f"{temprature} *C")
            logger.info(f" get_cpu_temprature was called, returned -> {temprature} *C")
        except Exception as e:
            logger.warning(f"{pre} {e}")
            await interaction.followup.send(e)

@bot.tree.command(name="uptime", description="return the uptime of the server")
@app_commands.describe()
async def uptime(interaction: discord.Interaction):
    if not interaction.response.is_done():
        await interaction.response.defer()
        try:
            uptime = get_server_uptime()
            await interaction.followup.send(f"{uptime}")
            logger.info(f"get_server_uptime() was called, returned -> {uptime}")
        except Exception as e:
            logger.warning(f"{e}")
            await interaction.followup.send(str(e))


@bot.tree.command(name="storage",description="get storage info")
@app_commands.describe()
async def storage(interaction:discord.Interaction):
    if not interaction.response.is_done():
        await interaction.response.defer()

        try:
            total,used,free=get_available_storage()
            await interaction.followup.send(f"total={total} GB, used={used} GB, free={free} GB")
            logger.info(f"{pre} get_available_storage was called, returned -> free={free},total={total},used={used}")
        except Exception as e:
            logger.warning(f"{pre} {e}")
            await interaction.followup.send(e)
            
@bot.tree.command(name="rmuser", description="Remove an IG username from the records")
@app_commands.describe(username="the IG username that you want to remove from records",member_id="your verification id (for MODs only)")
async def removeuser(interaction: discord.Interaction, username: str, member_id: str):
    if not interaction.response.is_done():
        await interaction.response.defer()

        try:
            if member_id == VERIFIED_MEMBER_ID:
                await interaction.followup.send(f"Trying to remove {username} from records")
                try:
                    success = await remove_account(username)
                    if success:
                        await interaction.followup.send(f"User {username} removed successfully!")
                    else:
                        await interaction.followup.send(f"User {username} was not removed (see logs for more info)")
                except Exception as e:
                    await interaction.followup.send("there was an unexpected error (the username was maybe removed but... see logs for more info)")
                    logger.warning(f"{pre} {e}")
            else:
                await interaction.followup.send("Invalid member ID. You are not authorized to remove users.")
        except Exception as e:
            logger.warning(f"{pre_bot} {e}")
            await interaction.followup.send(e)

@bot.tree.command(name="adduser", description="Add an IG username to get reels from")
@app_commands.describe(username="the IG username that you want to add",member_id="your verification ID (for MODs only)")
async def adduser(interaction: discord.Interaction,username: str, member_id: str):
    if not interaction.response.is_done():

        try:
            if member_id == VERIFIED_MEMBER_ID:
                await interaction.followup.send(f"Trying to add {username} in records")
                success = await add_new_account(username)
                if success:
                    latest_post = get_latest_post(username)
                    if latest_post:
                        post_url = get_post_url(latest_post)
                        file = f"{latest_post}.mp4"
                        dp = dump_post(url=post_url, filename=file)
                        if dp:
                            update_file(username=username, file=file)
                            data = loadx()
                            if data:
                                for account in data["accounts"]:
                                    if account["name"] == username:
                                        for server in account["server"]:
                                            channel_id = server["channel"]
                                            if channel_id:
                                                upload_success = await upload_video(bot, channel_id=channel_id, video_file=f'temp/{file}')
                                                if upload_success:
                                                    await send_message(channel_id=LOGCHANNEL, message=f"Uploaded the latest post for {username} to channel {channel_id} successfully.")
                                                else:
                                                    await send_message(channel_id=LOGCHANNEL, message=f"Failed to upload the latest post for {username} to channel {channel_id}.")
                            await interaction.followup.send(f"User {username} added successfully and latest post uploaded!")
                        else:
                            await interaction.followup.send(f"User {username} added, but failed to download the latest post.")
                    else:
                        await interaction.followup.send(f"User {username} added, but no posts found.")
                else:
                    await interaction.followup.send(f"User {username} was not added (see logs for more info)")
            else:
                await interaction.followup.send("Invalid member ID. You are not authorized to add users.")
        except Exception as e:
            logger.warning(f"{pre_bot} {e}")
            await interaction.followup.send(e)


@bot.tree.command(name="addchannel", description="Add a channel along with its server's name")
@app_commands.describe(username="the IG username in which you wanna add this channel(case sensitive)",server_name="the name of the server that you wanna add in records",channel_id="id of the channel that you wanna add into records",member_id="your verification id (for MODs only)")
async def addchannel(interaction:discord.Interaction, username: str, server_name: str, channel_id: int, member_id: str):
    try:
        if member_id == VERIFIED_MEMBER_ID:
            success = add_server(account_name=username, server_name=server_name, channel_id=channel_id)
            if success == 102:
                await interaction.followup.send(f"account {username} has been added in channel {channel_id} of server {server_name}")
                try:
                    await send_message(channel_id=channel_id,message=f'Congrats {server_name}!! this channel will now recieve posts from {username} ')
                except Exception as e:
                    logger.warning(f"{pre_bot} {e}")
            elif success == 101:
                await interaction.followup.send(f"server {server_name} already exists in records by channel id {channel_id}")
            elif success == 103:
                await interaction.followup.send(f"No account found named {username} in records. [TIP: consider adding one]")
            else:
                logger.warning("Unexpected case in addchannel")
                await interaction.followup.send("An unexpected error occurred.")
        else:
            await interaction.followup.send("Entered member ID is wrong.")
    except Exception as e:
        logger.warning(f"{pre_bot} {e}")
        await interaction.followup.send(e)


@bot.command(name="rmchannel", description="Remove a channel from the records")
@app_commands.describe(usernname="the IG username from where you wanna remove the channel in records",server_name="name of the server from where you wanna remove the channel",channel_id="id of the channel that you wanna remove",member_id="your verification id (MODs only)")
async def removechannel(interaction: discord.Interaction, username: str, server_name: str, channel_id: int, member_id: str):
    try:
        if member_id == VERIFIED_MEMBER_ID:
            success = remove_server(account_name=username, server_name=server_name, channel_id=channel_id)
            if success:
                await interaction.followup.send(f"Channel {channel_id} of server {server_name} removed for account {username}")
            else:
                await interaction.followup.send(f"No matching record found for server {server_name} and channel {channel_id}")
        else:
            await interaction.followup.send("Entered member ID is wrong.")
    except Exception as e:
        logger.warning(f"{pre_bot} {e}")
        await interaction.followup.send(e)


@bot.command(name="lsaccounts",description="list all accounts and their respective servers")
@app_commands.describe()
async def lsaccounts(interaction: discord.Interaction, member_id: str):
    if member_id == VERIFIED_MEMBER_ID:
        data = loadx()
        if data is None:
            await interaction.response.send_message("No data found.")
            return

        response = "Accounts and their respective servers:\n"
        for account in data["accounts"]:
            account_name = account["name"]
            server_names = [server["name"] for server in account["server"]]
            response += f"- {account_name}: {', '.join(server_names)}\n"
        await interaction.response.send_message(response)
    else:
        await interaction.response.send_message("Invalid member ID. You are not authorized to list accounts.")

@bot.command(name="hlp", description="Description of all commands")
@app_commands.describe(member_id="your verification id (MODs only)")
async def help(interaction: discord.Interaction, member_id: str):
    if member_id == VERIFIED_MEMBER_ID:
        await interaction.response.send_message("/adduser <insta-username> <category> <verification-id> - Add an IG username to get reels from")
        await interaction.followup.send("/addchannel <insta-username>/<category> <name-of-the-server> <channel-id-of-the-server> <verification-id> - Add a channel along with its server's name")
        await interaction.followup.send("/rmuser <insta-username> <verification-id> - Remove an IG username from the records")
        await interaction.followup.send("/rmchannel <insta-username> <name-of-the-server> <channel-id-of-the-server> <verification-id> - Remove a channel from the records")
        await interaction.followup.send("/lsaccounts <verification-id> - List all accounts and their respective servers")
        await interaction.followup.send("/temprature - Return the temperature of the server")
        await interaction.followup.send("/uptime - Return the uptime of the server")
        await interaction.followup.send("/storage - Get storage info")
    else:
        await interaction.response.send_message("Please enter a correct verification ID")
async def upload_video(bot, channel_id, video_file):
    channel = await bot.fetch_channel(channel_id)
    try:

        if channel:
            message=await channel.send(file=discord.File(video_file))
            await message.add_reaction("😂")
            await message.add_reaction("💀")
            await message.add_reaction("🗿")
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
    update_account_records(query=None)
    data = loadx()
    if data is None:  
        return

    for account in data["accounts"]:
        account_name = account["name"]
        logger.info(f"{pre} Checking for new post for {account_name}")
        check_for_post = check_for_new_post(account_name)
        if check_for_post:
            latest_post = get_latest_post(account_name)
            if latest_post:
                post_url = get_post_url(latest_post)
                if is_image(post_url):
                    file="f{latest_post}.png"
                else:
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

    files_to_remove = {}
    for account in data["accounts"]:
        account_files_to_remove = []
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
                        server_name = server['name']
                        all_servers_uploaded = False
                        logger.warning(f"Upload failed for {file} in server {server_name}, channel_ID: {channel_id}")
                        break
                    else:
                        await send_message(LOGCHANNEL, message=f"Task file-upload for {file} has been successful in {server['name']}, channel_ID: {channel_id}")
            if all_servers_uploaded:
                await send_message(LOGCHANNEL, message=f"{file} has been uploaded in it's respective servers without any issue")
                account_files_to_remove.append(file)
                await send_message(LOGCHANNEL, message=f"Marked {file} for removal")
                logger.info(f"Marked {file} for removal")

        files_to_remove[account["name"]] = account_files_to_remove

    for account in data["accounts"]:
        account_files_to_remove = files_to_remove.get(account["name"], [])
        for file in account_files_to_remove:
            try:
                account["files"].remove(file)
                await rmfile(f"{file}")
                logger.info(f"Removed {file}")
                await send_message(LOGCHANNEL, message=f"Removed {file}")
            except Exception as e:
                logger.error(f"Error removing file {file}: {e}")
                await send_message(LOGCHANNEL, message=f"Error removing file {file}: {e}")

    dumpx(data)

async def combined_task():
    loop = asyncio.get_event_loop()
    logger.info(f"{pre} initiating backend task")
    await loop.run_in_executor(None, backend_task)
    logger.info(f"{pre} initiating frontend task")
    await frontend_task(bot=bot)
        
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        logger.info(f"synced {len(synced)} times")
    except Exception as e:
        logger.error(e)
    scheduler = AsyncIOScheduler()
    scheduler.add_job(combined_task, 'interval', hours=3,next_run_time=datetime.now())
    scheduler.start()

check_and_create()
failsafe(query='a')
bot.run(TOKEN)
