import random
import string
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

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

# --- Naya Dynamic Thumbnail Function (Neon Style) ---
async def generate_dynamic_thumb(title, requester, user_id, thumb_url, client):
    width, height = 1280, 720
    # Background logic: Aapki choice ke hisab se 10x10x15 dark theme
    img = Image.new('RGB', (width, height), color=(10, 10, 15))
    
    if not os.path.exists("cache"):
        os.makedirs("cache")

    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("AnonXMusic/AM/f.ttf", 40)
        font_large = ImageFont.truetype("AnonXMusic/AM/f.ttf", 60)
    except:
        font = ImageFont.load_default()
        font_large = ImageFont.load_default()

    # 1. Left Side: User DP Circle
    try:
        user_photo = await client.download_media(user_id, file_name=f"cache/u_{user_id}.jpg")
        if user_photo:
            pfp = Image.open(user_photo).convert("RGBA").resize((300, 300))
            mask = Image.new("L", (300, 300), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, 300, 300), fill=255)
            img.paste(pfp, (150, 150), mask)
            # Neon Circle Border
            draw.ellipse([150, 150, 450, 450], outline=(0, 255, 255), width=10)
            draw.text((180, 480), "Listening Now...", font=font, fill=(255, 255, 255))
    except:
        draw.ellipse([150, 150, 450, 450], outline=(0, 255, 255), width=5)

    # 2. Right Side: Song Details
    draw.text((650, 200), "NOW PLAYING", font=font_large, fill=(0, 255, 255))
    draw.text((650, 300), f"Title: {title[:20]}...", font=font, fill=(255, 255, 255))
    draw.text((650, 400), f"Requested By: {requester}", font=font, fill=(200, 200, 200))

    # Progress Bar (Bottom)
    draw.rounded_rectangle([150, 610, 1130, 625], radius=10, fill=(40, 40, 40))
    draw.rounded_rectangle([150, 610, 500, 625], radius=10, fill=(0, 255, 255))

    thumb_path = f"cache/play_{user_id}_{random.randint(1,1000)}.jpg"
    img.save(thumb_path)
    return thumb_path

@app.on_message(
    filters.command(["play", "vplay", "cplay", "cvplay", "playforce", "vplayforce", "cplayforce", "cvplayforce"])
    & filters.group & ~BANNED_USERS
)
@PlayWrapper
async def play_commnd(client, message: Message, _, chat_id, video, channel, playmode, url, fplay):
    mystic = await message.reply_text(_["play_2"].format(channel) if channel else _["play_1"])
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    # ... (Baki ka Telegram Audio/Video logic same rahega) ...

    if url:
        if await YouTube.exists(url):
            if "playlist" in url:
                # Playlist Logic
                details = await YouTube.playlist(url, config.PLAYLIST_FETCH_LIMIT, message.from_user.id)
                streamtype, plist_type, img = "playlist", "yt", config.PLAYLIST_IMG_URL
                cap = _["play_9"]
            else:
                # Single Track Logic
                details, track_id = await YouTube.track(url)
                streamtype = "youtube"
                img = await generate_dynamic_thumb(details["title"], user_name, user_id, details["thumb"], client)
                cap = _["play_10"].format(details["title"], details["duration_min"])
        
        # ... (Spotify Logic Same Rahega) ...

    else:
        # Search Query Logic
        query = message.text.split(None, 1)[1]
        details, track_id = await YouTube.track(query)
        streamtype = "youtube"
        img = await generate_dynamic_thumb(details["title"], user_name, user_id, details["thumb"], client)

    # Final Stream Call
    await stream(_, mystic, user_id, details, chat_id, user_name, message.chat.id, video=video, streamtype=streamtype, forceplay=fplay, thumb=img)
    
