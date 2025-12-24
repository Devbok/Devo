import random
import string
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InputMediaPhoto, Message
from pytgcalls.exceptions import NoActiveGroupCall

import config
from AnonXMusic import Apple, Resso, SoundCloud, Spotify, Telegram, YouTube, app
from AnonXMusic.core.call import Anony
from AnonXMusic.utils import seconds_to_min, time_to_seconds
from AnonXMusic.utils.channelplay import get_channeplayCB
from AnonXMusic.utils.decorators.language import languageCB
from AnonXMusic.utils.decorators.play import PlayWrapper
from AnonXMusic.utils.formatters import formats
from AnonXMusic.utils.inline import (
    botplaylist_markup,
    livestream_markup,
    playlist_markup,
    slider_markup,
    track_markup,
)
from AnonXMusic.utils.logger import play_logs
from AnonXMusic.utils.stream.stream import stream
from config import BANNED_USERS, lyrical

async def generate_dynamic_thumb(title, requester, user_id, thumb_url, client):
    width, height = 1280, 720
    img = Image.new('RGB', (width, height), color=(10, 10, 15))
    
    if not os.path.exists("cache"):
        os.makedirs("cache")

    draw = ImageDraw.Draw(img)

    try:
        user_photo = await client.download_media(user_id, file_name=f"cache/u_{user_id}.jpg")
        if user_photo:
            pfp = Image.open(user_photo).convert("RGBA").resize((280, 280))
            mask = Image.new("L", (280, 280), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, 280, 280), fill=255)
            img.paste(pfp, (900, 160), mask)
            draw.ellipse([900, 160, 1180, 440], outline=(0, 255, 255), width=8)
    except:
        draw.ellipse([900, 160, 1180, 440], outline=(0, 255, 255), width=5)

    draw.text((70, 180), "NOW PLAYING", fill=(0, 255, 255))
    draw.text((70, 260), f"{title[:25]}...", fill=(255, 255, 255))
    draw.text((70, 560), f"By: {requester}", fill=(200, 200, 200))
    draw.rounded_rectangle([70, 610, 1210, 625], radius=10, fill=(40, 40, 40))
    draw.rounded_rectangle([70, 610, 550, 625], radius=10, fill=(0, 255, 255))

    thumb_path = f"cache/play_{user_id}.jpg"
    img.save(thumb_path)
    return thumb_path

@app.on_message(
    filters.command(["play", "vplay", "cplay", "cvplay", "playforce", "vplayforce", "cplayforce", "cvplayforce"])
    & filters.group & ~BANNED_USERS
)
@PlayWrapper
async def play_commnd(client, message: Message, _, chat_id, video, channel, playmode, url, fplay):
    mystic = await message.reply_text(_["play_2"].format(channel) if channel else _["play_1"])
    plist_id, slider, plist_type, spotify = None, None, None, None
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    audio_telegram = (message.reply_to_message.audio or message.reply_to_message.voice) if message.reply_to_message else None
    video_telegram = (message.reply_to_message.video or message.reply_to_message.document) if message.reply_to_message else None

    if audio_telegram:
        file_path = await Telegram.get_filepath(audio=audio_telegram)
        if await Telegram.download(_, message, mystic, file_path):
            details = {"title": "Telegram Audio", "link": await Telegram.get_link(message), "path": file_path, "dur": audio_telegram.duration}
            try:
                await stream(_, mystic, user_id, details, chat_id, user_name, message.chat.id, streamtype="telegram", forceplay=fplay)
            except Exception as e:
                return await mystic.edit_text(str(e))
            return await mystic.delete()

    elif video_telegram:
        file_path = await Telegram.get_filepath(video=video_telegram)
        if await Telegram.download(_, message, mystic, file_path):
            details = {"title": "Telegram Video", "link": await Telegram.get_link(message), "path": file_path, "dur": video_telegram.duration}
            try:
                await stream(_, mystic, user_id, details, chat_id, user_name, message.chat.id, video=True, streamtype="telegram", forceplay=fplay)
            except Exception as e:
                return await mystic.edit_text(str(e))
            return await mystic.delete()

    elif url:
        if await YouTube.exists(url):
            if "playlist" in url:
                try:
                    details = await YouTube.playlist(url, config.PLAYLIST_FETCH_LIMIT, message.from_user.id)
                    streamtype, plist_type, img = "playlist", "yt", config.PLAYLIST_IMG_URL
                    cap = _["play_9"]
                except:
                    return await mystic.edit_text(_["play_3"])
            else:
                try:
                    details, track_id = await YouTube.track(url)
                    streamtype = "youtube"
                    img = await generate_dynamic_thumb(details["title"], user_name, user_id, details["thumb"], client)
                    cap = _["play_10"].format(details["title"], details["duration_min"])
                except:
                    return await mystic.edit_text(_["play_3"])
        
        elif await Spotify.valid(url):
            spotify = True
            try:
                details, track_id = await Spotify.track(url)
                streamtype = "youtube"
                img = await generate_dynamic_thumb(details["title"], user_name, user_id, details["thumb"], client)
                cap = _["play_10"].format(details["title"], details["duration_min"])
            except:
                return await mystic.edit_text(_["play_3"])
    else:
        if len(message.command) < 2:
            return await mystic.edit_text(_["play_18"], reply_markup=InlineKeyboardMarkup(botplaylist_markup(_)))
        query = message.text.split(None, 1)[1].replace("-v", "")
        try:
            details, track_id = await YouTube.track(query)
            streamtype = "youtube"
            img = await generate_dynamic_thumb(details["title"], user_name, user_id, details["thumb"], client)
        except:
            return await mystic.edit_text(_["play_3"])

    if str(playmode) == "Direct":
        try:
            await stream(_, mystic, user_id, details, chat_id, user_name, message.chat.id, video=video, streamtype=streamtype, spotify=spotify, forceplay=fplay)
        except Exception as e:
            return await mystic.edit_text(str(e))
        await mystic.delete()
    else:
        if plist_type:
            ran_hash = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
            lyrical[ran_hash] = (url.split("=")[1]).split("&")[0] if "&" in url else url.split("=")[1]
            buttons = playlist_markup(_, ran_hash, user_id, plist_type, "c" if channel else "g", "f" if fplay else "d")
            await mystic.delete()
            await message.reply_photo(photo=img, caption=cap, reply_markup=InlineKeyboardMarkup(buttons))
        else:
            buttons = track_markup(_, track_id, user_id, "c" if channel else "g", "f" if fplay else "d")
            await mystic.delete()
            await message.reply_photo(photo=img, caption=_["play_10"].format(details["title"], details["duration_min"]), reply_markup=InlineKeyboardMarkup(buttons))
            
