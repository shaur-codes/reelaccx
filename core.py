import instaloader, aiohttp
from json import load,dump


L = instaloader.Instaloader(max_connection_attempts = 10,request_timeout=300)
username = ['astrophysicsmania','wtf_su2']
pre='[bot.CORE] '
query=None


def loadx():
    try:
        with open('records.json','r') as file:
            data = load(file)
            file.close()
            return data
    except Exception as e:
        print(f"{pre}[loadx()] {e}")


def dumpx(data):
    try:
            
        with open('records.json','w') as f:
            dump(data,f,indent=4)
        f.close()
    except Exception as e:
        print(f"{pre}[dumpx()] {e}")


async def update_shortcodes(username):
    print(f"{pre}Updating shortcodes for {username}")
    global shortcodes
    profile = instaloader.Profile.from_username(L.context, username)
    posts = profile.get_posts()
    shortcodes = []
    for post in posts:
        shortcodes.append(post.shortcode)
    data = loadx()
    accounts = data["accounts"]
    user_found = False  
    for account in accounts:
        if account["name"] == username:
            account['shortcodes'] = shortcodes
            user_found = True
            break  
        # ["posts"] can be updated in records using check_for_new_post()
    if user_found:
        dumpx(data=data)
        print(f'{pre}Account {username} has been updated.')
        return len(shortcodes)
    else:
        print(f'{pre}Error: Account {username} not found.')
        return False


def get_latest_post(username):
    data=loadx()
    accounts=data["accounts"]
    for account in accounts:
        if account["name"]==username:
            post=account['shortcodes']
            latest_post=post[0]
            return latest_post

    print(f"{pre} Error: account {username} not found in the records")
    return False


async def update_account_records(query):
    try:
        data=loadx()
        freq=len(data["accounts"])
        thresh=data["thresh"]
        if freq > thresh:
            try:
                updated_account_name = data["accounts"][freq-1]["name"]
                data["thresh"]=freq
                a=await update_shortcodes(username=updated_account_name)-1#-------------------------------> here
                data["posts"]=a
                print(f"{pre}New user '{updated_account_name}' found")
                dumpx(data=data)
                print(f"{pre}Updated threshold to {freq}")
            except Exception as e:
                print(f"{pre}[update_account()][0] {e}")
        else:
            if query=='update':
                print(f"{pre} new account was not found.")
            else:
                print(f"{pre} Everything is up-to-date")
    except Exception as e:
        print(f"{pre}[update_account()][1] {e}")


def account_position(username) -> int:
    accounts=loadx()["accounts"]
    for i,account in enumerate(accounts):
        if account["name"]==username:
            return i
    return -1


async def get_post_url(shortcode) -> str:
    post=instaloader.Post.from_shortcode(L.context,shortcode=shortcode)
    if post.is_video:
        video_url=post.video_url
        return video_url
    else:
        picture_url=post.url
        return picture_url


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
                    print(f"Error: Received status code {response.status}")
                    return False
    except aiohttp.ClientError as e:
        print(f"Error downloading file: {e}")
        return False


async def check_for_new_post(username) -> bool:
    data=loadx()
    position = account_position(username=username)
    if position !=-1:
            old_data=data["accounts"][position]["posts"]
    else:
        print(f"{pre} Error: Account {username} not found. trying to update records...")
        update_account_records(query='update')
    
    new_data=await update_shortcodes(username=username)
    if new_data>old_data:
        old_data=new_data
        data=loadx()
        data["accounts"][position]["posts"]=old_data #here yaha pe latest post 
        dumpx(data=data)
        print(f"{pre}New post found for {username}")
        return True
    else:
        print(f"{pre}New post for {username} NOT FOUND")


def add_new_account(username):
    data=loadx()
    accounts=data["accounts"]
    for account in accounts:
        if account["name"]==username:
            print(f"{pre}Account {username} already present in records")
        else:
            new_account={
                "name":username,
                "posts":0,
                "shortcodes":[],
                "server_count": 0,
                "server":[]
                }
            data["accounts"].append(new_account)
            dumpx(data)
            print(f"{pre}Account {username} has been added in records")
            check_for_new_post(username=username)


def update_server_count(username) -> bool:
    data=loadx()
    accounts=data["accounts"]
    for account in accounts:
        if account["name"]==username:
            position=account_position(username=username)
            count=len(account["server"][position])
            account["server_count"]=count
            datab=account["server_count"]
            data=loadx()
            data["accounts"][position]["server_count"]=count
            dumpx(data=data)
            return True
        else:
            return False


