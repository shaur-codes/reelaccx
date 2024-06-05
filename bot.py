import discord
from core import *
import os
import asyncio
import os
from dotenv import load_dotenv



TOKEN=os.getenv("KEY")
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
load_dotenv()
#VARS
#accounts=['losttemplates','wtf_su2']

async def upload_video(channel_id: int, video_file: str) -> bool:
    try:
        channel = await client.fetch_channel(channel_id)
        with open(video_file, 'rb') as file:
            await channel.send(file=discord.File(file))
        print(f"Video '{video_file}' uploaded to {channel.mention}")
        return True
    except discord.NotFound or Exception:
        print("Channel not found. Make sure the channel ID is correct.")
        return False

# Example usage:

#1246055019594121226

async def main():
    await update_account_records(query=None)
    data = loadx()

    #check_post=check_for_new_post()
    for account in data["accounts"]:
        account_name=account["name"]
        check_for_post = await check_for_new_post(account_name)
        if check_for_post:
            latest_post=get_latest_post(account_name)
            if latest_post!=False:
                post_url=await get_post_url(latest_post)
                file=f"{latest_post}.mp4"
                dp= await dump_post(url=post_url,filename=file)
                if dp:
                    for server in account['server']:
                        server_name=server['name']
                        channel=server['channel']
                        load_video= await upload_video(channel_id=channel,video_file=file)
                        print(f"upload has been successful for {server_name}")
                    print(f"deleting file {file}")
                    os.remove(file)
                else:
                    print("E dump_post false")
            else:
                print("E latest post False")
        else:
            print("E no new post")
        



@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    while True:
        await main()
        print("waiting for 1 hour")
        await asyncio.sleep(3600)  # Call the main function here


client.run(TOKEN)