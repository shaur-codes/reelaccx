import instaloader
import requests
from json import load, dump
from loguru import logger
from colorama import Fore, Style, init
from dotenv import load_dotenv
import os,time
import asyncio
import aiohttp


pre_bot = f"{Fore.BLUE}[BOT]{Style.RESET_ALL}"
pre_core = f"{Fore.BLUE}[bot.CORE]{Style.RESET_ALL}"
query = None
logger.add("bot.log", format="{time} {level} {message}", level="WARNING")
load_dotenv()
USER,USERB=os.getenv("USER"),os.getenv("USERB")
PASS,PASSB=os.getenv("PASS"),os.getenv("PASSB")
CHOVERFLOW=os.getenv("CHOVERFLOW") #Channel Id of the channel where all of the content will be uploaded
init(autoreset=True)
L = instaloader.Instaloader(max_connection_attempts=3, request_timeout=90)
L.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0"


def failsafe(query):
    session_file = 'session.txt'
    if query.lower()=="a":
        try:
            L.load_session_from_file(USER, session_file)
            logger.success("Session loaded")
            return 104
        except (instaloader.exceptions.BadCredentialsException, FileNotFoundError):
            logger.warning("Loading session failed, trying to log in...")
            for _ in range(3): 
                try:
                    L.login(USER, PASS)
                    L.save_session_to_file(session_file)
                    logger.success("Logged in and session saved")
                    return 104
                except Exception as e:
                    if isinstance(e, instaloader.exceptions.LoginRequiredException):
                        logger.warning(f"Login failed: {e}")
                        time.sleep(5) 
                    else:
                        logger.info(f"{pre_core} The Exception is not Login-Required-Exception, retrying...")
                        time.sleep(3)
            
            try:
                L.login(USERB,PASSB)
                L.save_session_to_file(session_file)  # Save the second account's session as well
                logger.success("Logged in [Fail-Safe was Activated]")
                return 105
            except Exception as e:
                logger.critical(f"BROKEN FAIL-SAFE!!! {e}")
                return 106
    elif query.lower()=="b":
        try:
            L.load_session_from_file(USERB, session_file)
            logger.success("Session loaded")
            return 104
        except (instaloader.exceptions.BadCredentialsException, FileNotFoundError):
            logger.warning("Loading session failed, trying to log in...")
            for _ in range(3): 
                try:
                    L.login(USERB, PASSB)
                    L.save_session_to_file(session_file)
                    logger.success("Logged in and session saved")
                    return 104
                except Exception as e:
                    if isinstance(e, instaloader.exceptions.LoginRequiredException):
                        logger.warning(f"Login failed: {e}")
                        time.sleep(5) 
                    else:
                        logger.info(f"{pre_core} The Exception is not Login-Required-Exception, retrying...")
                        time.sleep(3)
            
            try:
                L.login(USER,PASS)
                L.save_session_to_file(session_file)  # Save the second account's session as well
                logger.success("Logged in [Fail-Safe was Activated]")
                return 105
            except Exception as e:
                logger.critical(f"BROKEN FAIL-SAFE!!! {e}")
                return 106
    else:
        logger.warning(f"{pre_core} this query {query} is not acceptable!!!")

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

def update_shortcodes(username):
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
            # Save updated data
            dumpx(data=data)
            logger.info(f'{pre_core} Account {username} has been updated.')
            return len(shortcodes)
        else:
            logger.error(f'{pre_core} Error: Account {username} not found.')
            return False
    except instaloader.exceptions.ProfileNotExistsException:
        logger.error(f'{pre_core} Error: Profile {username} does not exist.')
        return 107
    except instaloader.exceptions.ConnectionException as e:
        logger.error(f'{pre_core} Connection error: {e}')
        return 108
    except instaloader.exceptions.BadResponseException as e:
        logger.error(f'{pre_core} Bad response from server: {e}')
        return 109
    except instaloader.exceptions.TooManyRequestsException as e:
        logger.error(f'{pre_core} Too many requests: {e}')
        return 110
    except instaloader.exceptions.QueryReturnedNotFoundException as e:
        logger.error(f'{pre_core} Query returned not found: {e}')
        return 111
    except instaloader.exceptions.ConnectionException as e:
        if e.response.status_code == 400:
            logger.error(f"{pre_core} Caught a 400 Bad Request error!")
        elif e.response.status_code == 401:
            logger.error(f"{pre_core} Caught a 401 Unauthorized error!")
        try:
            logger.info(f"{pre_core} recreating a new session...")
            rmfile('session.txt')
            failsafe(query='b')
            return 112
        except Exception as f:
            logger.error(f"{f}")
            return 113

        
    except Exception as e:
        logger.error(f'{pre_core} Unexpected error: {e}')
        return False

def get_latest_post(username):
    try:
        data = loadx()
        accounts = data["accounts"]
        for account in accounts:
            if account["name"] == username:
                post = account['shortcodes']
                latest_post = post[3]  # trying to prevent getting the pinned posts always as latest post.
                return latest_post
        
        logger.error(f"{pre_core} Error: account {username} not found in the records")
        return False
    except Exception as e:
        logger.error(e)
        return False 

def update_account_records(query): #updates threshold
    try:
        data = loadx()
        freq = len(data["accounts"])
        thresh = data["thresh"]
        if freq > thresh:
            try:
                updated_account_name = data["accounts"][freq-1]["name"]
                data["thresh"] = freq
                a = update_shortcodes(username=updated_account_name)
                a=a-1
                data["posts"] = a
                logger.info(f"{pre_core} New user '{updated_account_name}' found")
                dumpx(data=data)
                logger.info(f"{pre_core} Updated threshold to {freq}")
            except Exception as e:
                logger.error(f"{pre_core} [update_account_records()][0] {e}")
        else:
            if query == 'update':
                logger.info(f"{pre_core} new account was not found.")
            else:
                logger.info(f"{pre_core} Everything is up-to-date")
    except Exception as e:
        logger.error(f"{pre_core} [update_account_records()][1] {e}")

def account_position(username) -> int:
    try:
        accounts = loadx()["accounts"]
        for i, account in enumerate(accounts):
            if account["name"] == username:
                return i
        return -1
    except Exception as e:
        logger.error(e)

def get_post_url(shortcode) -> str:
    try:
        post = instaloader.Post.from_shortcode(L.context, shortcode=shortcode)
        if post.is_video:
            return post.video_url
        else:
            return post.url
    except Exception as e:
        logger.error(e)

def dump_post(url: str, filename: str) -> bool:
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(f"temp/{filename}", "wb") as f:
                f.write(response.content)
            return True
        else:
            logger.error(f"{pre_core} Error: Received status code {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"{pre_core} Error downloading file: {e}")
        return False

def check_for_new_post(username) -> bool:
    try:
        data = loadx()
        position = account_position(username=username)
        if position != -1:
            old_data = data["accounts"][position]["posts"]
        else:
            logger.error(f"{pre_core} Error: Account {username} not found. trying to update records...")
            update_account_records(query='update')
            return False

        new_data = update_shortcodes(username=username)

        # Ensure old_data and new_data are not None
        if old_data is None or new_data is None:
            logger.error(f"{pre_core} Error: old_data or new_data is None for account {username}")
            return False
        error_codes=[107 or 108 or 109 or 110 or 111 or 112 or 113]
        if new_data in error_codes:
            return new_data
        else:
            pass
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

def add_new_account(username):
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
            "files":[],
            "shortcodes": [],
            "server_count": 0,
            "server": []
        }
        data["accounts"].append(new_account)
        dumpx(data)
        logger.info(f"{pre_core} Account {username} has been added in records")
        update_account_records(query='update')
        update_shortcodes(username=username)
        add_server(account_name=username,server_name='Reelaccx',channel_id=int(CHOVERFLOW))
        update_server_count(username)

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

def measure_time(func, *args, **kwargs):
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Function '{func.__name__}' took {elapsed_time:.2f} seconds to complete.")
    return result

def update_file(username,file):
    records=loadx()
    for account in records["accounts"]:
        if account["name"]==username:
            account["files"].append(file)
            break
        else:
            logger.error(f"{pre_core} {username} not found in records!!")
    dumpx(records)

async def rmfile(filename):
    try:
        os.remove(f"temp/{filename}")
    except Exception as e:
        logger.error(f"{pre_core} {e}")

def check_and_create():
    if not os.path.exists('temp'):
        os.makedirs('temp')
    records_data = {
        "thresh": 1,
        "sleep_time": 3600,
        "accounts": [
            {
                "name": "wtf_su2",
                "posts": 0,
                "shortcodes": ["C8TdzW7Rlve"],
                "files": [],
                "server_count": 1,
                "server": [
                    {
                        "name": "Reelaccx",
                        "channel": 1251090965398163486
                    }
                ]
            }
        ]
    }
    if not os.path.isfile('records.json'):
        dumpx(records_data)

async def is_connected():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://discord.com") as response:
                if response.status == 200:
                    logger.info("We are up and running")
                else:
                    logger.error(f"Discord returned {response.status}")
    except Exception as e:
        logger.error(f"Couldn't connect to internet, retrying... Error: {e}")
        await asyncio.sleep(5)
        await is_connected()  
