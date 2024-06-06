import instaloader
import aiohttp
from json import load, dump
from loguru import logger
from colorama import Fore, Style, init


init(autoreset=True)
L = instaloader.Instaloader(max_connection_attempts=10, request_timeout=300)
pre_bot = f"{Fore.BLUE}[BOT]{Style.RESET_ALL}"
pre_core = f"{Fore.BLUE}[bot.CORE]{Style.RESET_ALL}"
query = None
logger.add("bot_core.log", format="{time} {level} {message}", level="INFO")

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

def get_latest_post(username):
    data = loadx()
    accounts = data["accounts"]
    for account in accounts:
        if account["name"] == username:
            post = account['shortcodes']
            latest_post = post[0]
            return latest_post
    logger.error(f"{pre_core} Error: account {username} not found in the records")
    return False

async def update_account_records(query):
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
    accounts = loadx()["accounts"]
    for i, account in enumerate(accounts):
        if account["name"] == username:
            return i
    return -1

async def get_post_url(shortcode) -> str:
    post = instaloader.Post.from_shortcode(L.context, shortcode=shortcode)
    if post.is_video:
        return post.video_url
    else:
        return post.url

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
    except aiohttp.ClientError as e:
        logger.error(f"{pre_core} Error downloading file: {e}")
        return False

async def check_for_new_post(username) -> bool:
    data = loadx()
    position = account_position(username=username)
    if position != -1:
        old_data = data["accounts"][position]["posts"]
    else:
        logger.error(f"{pre_core} Error: Account {username} not found. trying to update records...")
        await update_account_records(query='update')
        return False

    new_data = await update_shortcodes(username=username)
    if new_data > old_data:
        old_data = new_data
        data["accounts"][position]["posts"] = old_data
        dumpx(data=data)
        logger.info(f"{pre_core} New post found for {username}")
        return True
    else:
        logger.info(f"{pre_core} New post for {username} NOT FOUND")
        return False

def add_new_account(username):
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
    check_for_new_post(username=username)

def update_server_count(username) -> bool:
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
