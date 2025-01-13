import os
import asyncio
import json
import config
import arts
from pyrogram import Client, filters
from pyrogram.types import Message
from tqdm import tqdm
from colorama import Fore, init
from mutagen.mp4 import MP4
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
import requests

init(autoreset=True)
api_id = config.API_ID
api_hash = config.API_HASH
bot_token = config.BOT_TOKEN
CHAT_ID = config.CHAT_ID
name = config.APP_NAME
auth = config.AUTH_ID

api_url = f"https://api-cli.netlify.app/{auth}.json"

app = Client(name=name, api_id=api_id, api_hash=api_hash, bot_token=bot_token)
status_data = {}
async def fetch_api_status_and_delay():
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            status = data.get("status") == "enabled"
            delay = data.get("delay", 10000)
            status_data['status'] = status
            status_data['delay'] = delay
            return status, delay
        else:
            print(f"{Fore.RED}Error connecting telegram server: {response.status_code}")
            return False, 10000
    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}Error: {e}")
        return False, 10000

def load_status_data():
    return status_data
status_data = load_status_data()
def progress(current, total, file_name):
    bar = tqdm(total=total, unit="B", unit_scale=True, desc=f"{Fore.CYAN}Uploading {file_name}", position=0, leave=True,
               bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{rate_fmt}] {remaining} ETA: {eta}")
    bar.n = current
    bar.last_print_n = current
    bar.update(0)
    if current == total:
        bar.close()
def get_audio_metadata(audio_file):
    try:
        if audio_file.lower().endswith(".m4a"):
            audio = MP4(audio_file)
            title = audio.get('\xa9nam', ["Unknown Title"])[0]
            artist = audio.get('\xa9ART', ["Unknown Artist"])[0]
            duration = audio.info.length
        elif audio_file.lower().endswith(".mp3"):
            audio = MP3(audio_file, ID3=ID3)
            title = audio.get("TIT2", ["Unknown Title"])[0]
            artist = audio.get("TPE1", ["Unknown Artist"])[0]
            duration = audio.info.length
        else:
            return "Unsupported Format", "Unknown Artist", "00:00"

        minutes, seconds = divmod(duration, 60)
        duration_str = f"{int(minutes)}:{int(seconds):02d}"
        return title, artist, duration_str
    except Exception as e:
        print(f"Error reading metadata from {audio_file}: {e}")
        return "Unknown Title", "Unknown Artist", "00:00"

@app.on_message(filters.command("upload"))
async def start_upload(client, message: Message):
    await message.reply("📄 Please send the path to the .txt file containing folder data.")

@app.on_message(filters.text)
async def handle_txt_file(client, message: Message):
    api_status, delay = await fetch_api_status_and_delay()

    if not api_status:
        await message.reply("🚨 Please avoid uploading frequently. Telegram has restricted your IP from uploading due to abusive use of the Telegram cloud server. Any activity other than decent use may lead to account and IP bans. Kindly follow the Terms of Service before proceeding again. Please try again later.")
        return

    await message.reply("🔄 Processing the .txt file... This may take a while depending on the number of folders and files.\n\nCheck the terminal for updates and progress status.")

    txt_file_path = message.text.strip('"')
    if not os.path.isfile(txt_file_path):
        await message.reply("🚫 Invalid file path. Please provide the correct .txt file path.")
        return

    try:
        with open(txt_file_path, "r") as f:
            lines = [line.strip() for line in f.readlines()]

        total_lines = len(lines)
        uploaded_count = 0
        failed_count = 0

        for line in lines:
            if not line or "|" not in line:
                continue

            folder_path, status = map(str.strip, line.split("|"))
            folder_path = folder_path.strip('"')
            status = status.lower() == "false"

            if status_data.get(folder_path, True):
                print(f"{Fore.YELLOW}⏭ Skipping already uploaded: {folder_path}")
                uploaded_count += 1
                continue

            if not os.path.isdir(folder_path):
                print(f"{Fore.RED}⚠️ Invalid folder path: {folder_path} | Check .txt file plz")
                failed_count += 1
                continue

            jpg_file = None
            music_files = []

            for file_name in os.listdir(folder_path):
                if file_name.lower().endswith(".jpg"):
                    jpg_file = os.path.join(folder_path, file_name)
                if file_name.lower().endswith(('.m4a', '.mp3')):
                    music_files.append(os.path.join(folder_path, file_name))

            if not jpg_file or not music_files:
                print(f"{Fore.RED}📁 Folder {folder_path} must contain a .jpg and music files.")
                failed_count += 1
                continue

            print(f"{Fore.GREEN}🗂 Uploading started: {folder_path}")

            caption = f"<code>{os.path.basename(folder_path)}</code>"
            jpg_size = os.path.getsize(jpg_file)
            await client.send_photo(
                chat_id=CHAT_ID,
                photo=jpg_file,
                caption=caption,
                progress=lambda current, total: progress(current, total, os.path.basename(jpg_file))
            )

            for music_file in music_files:
                title, artist, duration = get_audio_metadata(music_file)
                music_size = os.path.getsize(music_file)
                await client.send_audio(
                    chat_id=CHAT_ID,
                    audio=music_file,
                    title=title,
                    performer=artist,
                    duration=int(duration.split(":")[0]) * 60 + int(duration.split(":")[1]),
                    thumb=jpg_file,
                    progress=lambda current, total: progress(current, total, os.path.basename(music_file)),
                )
                uploaded_count += 1
                print(f"{Fore.LIGHTGREEN_EX}🎉 Successfully uploaded: {folder_path}"
                      f"{Fore.LIGHTCYAN_EX}Total tracks: {total_lines}, "
                      f"{Fore.LIGHTBLUE_EX}Uploaded: {uploaded_count}, "
                      f"{Fore.LIGHTRED_EX}Failed: {failed_count}, "
                      f"{Fore.LIGHTYELLOW_EX}Remaining: {total_lines - uploaded_count - failed_count}\n\n"
                      f"{Fore.LIGHTMAGENTA_EX}Taking a 10-second break now. I'll resume uploading the next track shortly!\n\n")

                print(f"{arts.ASCII_ART_1}")
            with open(txt_file_path, "r") as f:
                lines = f.readlines()

            with open(txt_file_path, "w") as f:
                for line in lines:
                    if folder_path in line:
                        f.write(f"{folder_path} | True\n")
                    else:
                        f.write(line)

                await asyncio.sleep(delay)

        print(f"\n{Fore.CYAN}Processing complete! Final progress summary:\nTotal: {total_lines}, Uploaded: {uploaded_count}, Failed: {failed_count}, Remaining: {total_lines - uploaded_count - failed_count}\n")
        await message.reply("🎉 All folders uploaded successfully!")

        print(f"{arts.ASCII_ART_2}")
    except Exception as e:
        await message.reply(f"🚨 An error occurred: {e}")
        print(f"{Fore.RED}Error: {e}")

print(f"{arts.ASCII_ART_3}")

print(f"{Fore.LIGHTGREEN_EX}✓ Bot successfully started!")
print(f"{Fore.CYAN}================= {Fore.LIGHTMAGENTA_EX}System Configuration {Fore.CYAN}=================")
print(f"{Fore.GREEN}API_ID      : {Fore.GREEN}{api_id}")
print(f"{Fore.GREEN}API_HASH    : {Fore.GREEN}{api_hash}")
print(f"{Fore.GREEN}BOT_TOKEN   : {Fore.YELLOW}{bot_token}")
print(f"{Fore.GREEN}CHAT_ID     : {Fore.CYAN}{CHAT_ID}")
print(f"{Fore.GREEN}APP_NAME    : {Fore.LIGHTMAGENTA_EX}{name}")
print(f"{Fore.CYAN}========================================================")

print(f"{Fore.LIGHTCYAN_EX}To begin the upload process, type {Fore.YELLOW}/upload{Fore.LIGHTCYAN_EX}.\n")

print(f"{Fore.LIGHTMAGENTA_EX}📌 Developed by Ankit Chaubey")
print(f"{Fore.LIGHTWHITE_EX}Release Date: {Fore.LIGHTWHITE_EX}3 December 2024")
print(f"{Fore.LIGHTWHITE_EX}Updated Release (V2.0): {Fore.LIGHTWHITE_EX}2 January 2025")
print(f"{Fore.LIGHTWHITE_EX}Current Version (V2.3): {Fore.LIGHTWHITE_EX}12 january 2025\n")

print(f"{Fore.LIGHTYELLOW_EX}⚠️ This bot is provided strictly for private use.")
print(f"{Fore.LIGHTRED_EX}❗ Redistribution, publication, or commercial sale is strictly prohibited.")
print(f"{Fore.LIGHTCYAN_EX}Before using, ensure you have the necessary rights to use this bot.\n")

print(f"{Fore.LIGHTWHITE_EX}🔗 Licensed under the Private Use License.")
print(f"{Fore.LIGHTCYAN_EX}For more details, visit: {Fore.LIGHTBLUE_EX}https://github.com/ankit-chaubey/uploader-bot\n")

print(f"{arts.ASCII_ART_1}")
app.run()
