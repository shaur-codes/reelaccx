import instaloader
import aiohttp
from json import load, dump
from loguru import logger
from colorama import Fore, Style, init
from dotenv import load_dotenv
import os



pre_bot = f"{Fore.BLUE}[BOT]{Style.RESET_ALL}"
pre_core = f"{Fore.BLUE}[bot.CORE]{Style.RESET_ALL}"
query = None
logger.add("bot_core.log", format="{time} {level} {message}", level="INFO")
load_dotenv()
USER,USERB=os.getenv("USER"),os.getenv("USERB")
PASS,PASSB=os.getenv("PASS"),os.getenv("PASSB")
init(autoreset=True)
L = instaloader.Instaloader(max_connection_attempts=10, request_timeout=300)

def failsafe():
    try:
        L.login(USER,PASS)
        logger.success("Logged in")
        return 104                                           #LOGGED IN without any problem
    except Exception as e:
        logger.warning(f"Activating Fail-Safe {e}")
        try:
            L.login(USERB,PASSB)
            logger.success("Logged in [Fail-Safe has been activated]")
            return 105                                      #logged in using sencond token (Report this message on development server)
        except Exception as e:
            logger.critical(f"BROKEN FAIL-SAFE!!! {e}")
            return 106                                      # fail-safe not working (immidiately report this on development server)
        
failsafe()


def loadx():
    try:
        with open('records.json', 'r') as file:
            data = load(file)
            return data
    except Exception as e:
        logger.error(f"{pre_core} [loadx()] {e}")

def dumpx(data):
    try:
        with open('records.json', 'w') as f:
            dump(data, f, indent=4)
    except Exception as e:
        logger.error(f"{pre_core} [dumpx()] {e}")

async def update_shortcodes(username):
    try:

        logger.info(f"{pre_core} Updating shortcodes for {username}")
        global shortcodes
        profile = instaloader.Profile.from_username(L.context, username)
        posts = profile.get_posts()
        shortcodes = [post.shortcode for post in posts]
        data = loadx()
        accounts = data["accounts"]
        user_found = False  
        for account in accounts:
            if account["name"] == username:
                account['shortcodes'] = shortcodes
                user_found = True
                break  
        if user_found:
            dumpx(data=data)
            logger.info(f'{pre_core} Account {username} has been updated.')
            return len(shortcodes)
        else:
            logger.error(f'{pre_core} Error: Account {username} not found.')
            return False
    except Exception as e:
        logger.error(e)
       
def get_latest_post(username):
    try:
        data = loadx()
        accounts = data["accounts"]
        for account in accounts:
            if account["name"] == username:
                post = account['shortcodes']
                latest_post = post[0]
                return latest_post
        logger.error(f"{pre_core} Error: account {username} not found in the records")
        return False
    except Exception as e:
        logger.error(e)

async def update_account_records(query): #updates threshold
    try:
        data = loadx()
        freq = len(data["accounts"])
        thresh = data["thresh"]
        if freq > thresh:
            try:
                updated_account_name = data["accounts"][freq-1]["name"]
                data["thresh"] = freq
                a = await update_shortcodes(username=updated_account_name) - 1
                data["posts"] = a
                logger.info(f"{pre_core} New user '{updated_account_name}' found")
                dumpx(data=data)
                logger.info(f"{pre_core} Updated threshold to {freq}")
            except Exception as e:
                logger.error(f"{pre_core} [update_account()][0] {e}")
        else:
            if query == 'update':
                logger.info(f"{pre_core} new account was not found.")
            else:
                logger.info(f"{pre_core} Everything is up-to-date")
    except Exception as e:
        logger.error(f"{pre_core} [update_account()][1] {e}")

def account_position(username) -> int:
    try:
        accounts = loadx()["accounts"]
        for i, account in enumerate(accounts):
            if account["name"] == username:
                return i
        return -1
    except Exception as e:
        logger.error(e)

async def get_post_url(shortcode) -> str:
    try:
        post = instaloader.Post.from_shortcode(L.context, shortcode=shortcode)
        if post.is_video:
            return post.video_url
        else:
            return post.url
    except Exception as e:
        logger.error(e)

async def dump_post(url: str, filename: str) -> bool:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    content = await response.read()
                    with open(filename, "wb") as f:
                        f.write(content)
                    return True
                else:
                    logger.error(f"{pre_core} Error: Received status code {response.status}")
                    return False
    except Exception as e:
        logger.error(f"{pre_core} Error downloading file: {e}")
        return False

async def check_for_new_post(username) -> bool:
    try:
        data = loadx()
        position = account_position(username=username)
        if position != -1:
            old_data = data["accounts"][position]["posts"]
        else:
            logger.error(f"{pre_core} Error: Account {username} not found. trying to update records...")
            await update_account_records(query='update')
            return False

        new_data = await update_shortcodes(username=username)

        # Ensure old_data and new_data are not None
        if old_data is None or new_data is None:
            logger.error(f"{pre_core} Error: old_data or new_data is None for account {username}")
            return False

        if new_data > old_data:
            data["accounts"][position]["posts"] = new_data
            dumpx(data=data)
            logger.info(f"{pre_core} New post found for {username}")
            return True
        else:
            logger.info(f"{pre_core} New post for {username} NOT FOUND")
            return False
    except Exception as e:
        logger.error(e)
        return False

def update_server_count(username) -> bool:
    try:
        data = loadx()
        accounts = data["accounts"]
        for account in accounts:
            if account["name"] == username:
                position = account_position(username=username)
                count = len(account["server"])
                account["server_count"] = count
                data["accounts"][position]["server_count"] = count
                dumpx(data=data)
                return True
        return False    
    except Exception as e:
        logger.error(e)

async def add_new_account(username):
    try:
        data = loadx()
        accounts = data["accounts"]
        for account in accounts:
            if account["name"] == username:
                logger.info(f"{pre_core} Account {username} already present in records")
                return
        new_account = {
            "name": username,
            "posts": 0,
            "shortcodes": [],
            "server_count": 0,
            "server": []
        }
        data["accounts"].append(new_account)
        dumpx(data)
        logger.info(f"{pre_core} Account {username} has been added in records")
        await update_account_records(query='update')
        await update_server_count(username)
    except Exception as e:
        logger.error(e)

def add_server(account_name, server_name, channel_id) -> int:
    try:
        data = loadx()
        accounts = data["accounts"]
        for account in accounts:
            if account["name"] == account_name:
                for server in account["server"]:
                    if server["channel"] == channel_id:
                        logger.error(f"{server} already present by channel id {channel_id}")
                        return 101
                account["server"].append({"name": server_name, "channel": channel_id})
                dumpx(data)
                update_server_count(account)
                logger.success(f"added {server_name} for {account_name}")
                return 102
        logger.error(f"no account found named as {account_name}")
        return 103
    except Exception as e:
        logger.error(e)
