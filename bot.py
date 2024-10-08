#m.0.6.1
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
from discord.ext.commands import Bot


init(autoreset=True)
load_dotenv()
TOKEN = os.getenv("KEY")
VERIFIED_MEMBER_ID = os.getenv("MEMBER_ID")
LOGCHANNEL=os.getenv("LOGCHANNEL")
APP_ID=os.getenv("APP_ID")
UID=os.getenv("UID")
intents = discord.Intents.default()
intents.message_content = True
pre = f"{Fore.BLUE}[BOT]{Style.RESET_ALL}"
logger.add("log.log", format="{time} {level} {message}", level="INFO")
bot = commands.AutoShardedBot(command_prefix="!", intents=intents)
client = Bot(command_prefix="/", intents=intents,application_id=APP_ID)


async def send_message(channel_id, message):
    await bot.wait_until_ready()
    channel = await bot.fetch_channel(channel_id)
    if channel:
        await channel.send(message)
    else:
        print(f"Could not find channel with ID: {channel_id}")

# Commands
@bot.tree.command(name="temprature")
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

@bot.tree.command(name="backup", description="create a backup of important files")
async def backup_command(interaction: discord.Interaction,member_id:str):
    if member_id!=VERIFIED_MEMBER_ID:
        await interaction.response.send_message("you entered a wrong one!!")
    if not interaction.response.is_done():
        await interaction.response.defer()
        try:
            await create_backup(time=False)
            await interaction.followup.send(f"Done!!")
            logger.info(f"backup_command() was called.")
        except Exception as e:
            logger.warning(e)
            await interaction.followup.send(str(e))


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

@bot.command(name="adduser", description="Add an IG username to get reels from")
async def adduser(ctx, username: str, member_id: str):
    try:
        if member_id == VERIFIED_MEMBER_ID:
            await ctx.send(f"Trying to add {username} in records")
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
                        await ctx.send(f"User {username} added successfully and latest post uploaded!")
                    else:
                        await ctx.send(f"User {username} added, but failed to download the latest post.")
                else:
                    await ctx.send(f"User {username} added, but no posts found.")
            else:
                await ctx.send(f"User {username} was not added (see logs for more info)")
        else:
            await ctx.send("Invalid member ID. You are not authorized to add users.")
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
                    await send_message(channel_id=channel_id,message=f'Congrats {server_name}!! this channel will now recieve posts from {username} ')
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
        
@bot.command(name="rmchannel", description="Remove a channel from the records")
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

@bot.command(name="lsaccounts",description="list all accounts and their respective servers")
#@app_commands.describe()
async def lsaccounts(ctx,member_id:str):#(interaction: discord.Interaction, member_id: str):
    if member_id == VERIFIED_MEMBER_ID:
        data = loadx()
        if data is None:
            await ctx.send("no data found")#interaction.response.send_message("No data found.")
            return

        response = "Accounts and their respective servers:\n"
        for account in data["accounts"]:
            account_name = account["name"]
            server_names = [server["name"] for server in account["server"]]
            response += f"- {account_name}: {', '.join(server_names)}\n"
        await ctx.message.delete()
        await ctx.send(response)#interaction.response.send_message(response)
    else:
        await ctx.send("Invalid member ID")#interaction.response.send_message("Invalid member ID. You are not authorized to list accounts.")

@bot.command(name="hlp", description="Description of all commands")
async def help(ctx, member_id: str):
    if member_id == VERIFIED_MEMBER_ID:
        await ctx.send("/adduser <insta-username> <verification-id>")
        await ctx.send("/addchannel <insta-username> <name-of-the-server> <channel-id-of-the-server> <verification-id>")
    else:
        await ctx.send("Please enter a correct verification ID")


async def is_sent(channel_id: str, filename: str) -> bool:
    channel = bot.get_channel(int(channel_id))
    if not channel:
        logger.warning(f"Channel:{channel_id} not found!!")
        await send_message(channel_id=LOGCHANNEL,message=f"[Is_sent()] Channel {channel_id} not found!!")
        return False
    elif channel is None:
        print(f"Channel with ID {channel_id} not found or bot lacks permissions.")
        await send_message(channel_id=LOGCHANNEL, message=f"[Is_sent()] Channel {channel_id} not found or bot lacks permissions.")
    else:
        pass
    last_messages = [msg async for msg in channel.history(limit=10)]

    for msg in last_messages:
        if msg.attachments:
            for attachment in msg.attachments:
                if attachment.filename == filename:
                    logger.info(f"{pre_bot} {filename} was already sent.")
                    await send_message(channel_id=LOGCHANNEL,message=f"{filename} was already sent in {channel_id}. Skipping")
                    return True
    logger.info(f"{pre_bot} {filename} wasn't found in the last 10 posts.")
    await send_message(channel_id=LOGCHANNEL,message=f"{filename} is ready to be sent.")
    return False
           
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

async def backup():
    user = await bot.fetch_user(UID)
    files_to_upload=['.env','records.json','log.log', 'bot.py','core.py']
    dm_channel = await user.create_dm()
    all_sent=True
    for file in files_to_upload:
        if os.path.exists(file):
            await dm_channel.send(file=discord.File(file))
            logger.info(f"{pre_bot} sent {file} to {user.name}")
        else:
            all_sent=False
            await dm_channel.send(f"File {file} not found")
            if file==".env":
                pseudonym="memes_compressed.tar.xz"
            elif file=="records.json":
                pseudonym="logfile.log"
            elif file=="log.log":
                pseudonym="compressed.tar.xz"
            else:
                pseudonym="bullshit.txt"
            await send_message(channel_id=LOGCHANNEL,message=f"task: Backup\nSuccess:False\nReason:File {pseudonym} not found!!")
    if all_sent:
        await send_message(channel_id=LOGCHANNEL,message="task: Backup\nSuccess:True")

    else:
        pass

async def create_backup(time:bool):
    try:
        data=loadx()
        if time:
            ct=datetime.now().strftime("%H%M")
            if int(ct) >= 2359 and int(ct) < 200 or int(ct) >= 1200 and int(ct) < 1400:
                await backup()
                data["backed_up"] = True
                dumpx(data)
            else:
                data["backed_up"] = False
        else:
            await backup()
    except Exception as e:
        logger.warning(f"{pre_bot}{e}")

def task_download():
    try:
        ct=int(current_time("h"))
        data=loadx()
        tt=int(data["initiated_at"])
        if ct-tt >= 3:
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
                        ct=current_time(format="h")
                        data["initiated_at"]=ct
                        post_url = get_post_url(latest_post)
                        if is_image(post_url):
                            file=f"{latest_post}.png"
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
        else:
            pass
    except Exception as e:
        logger.error(e)


async def task_upload(bot):
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
                    already_sent = await is_sent(channel_id=channel_id,filename=f'temp/{file}')
                    if already_sent:
                        continue
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
    logger.info(f"{pre} initiating backup")
    await create_backup(time=True)
    logger.info(f"{pre} initiating backend task")
    await loop.run_in_executor(None, task_download)
    logger.info(f"{pre} initiating frontend task")
    await task_upload(bot=bot)
        
@bot.event
async def on_ready():
    times_synced=await bot.tree.sync()
    logger.info(f"synced {times_synced} commands")
    print(f'We have logged in as {bot.user}')
    scheduler = AsyncIOScheduler()
    scheduler.add_job(combined_task, 'interval', hours=2,next_run_time=datetime.now())
    scheduler.start()

check_and_create()
failsafe(query='a')
bot.run(TOKEN)
