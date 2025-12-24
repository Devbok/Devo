import os
import re
import random
import asyncio
import aiohttp
import aiofiles
from PIL import Image, ImageFilter, ImageDraw, ImageFont
from youtubesearchpython.__future__ import VideosSearch
from AnonXMusic import app
from config import YOUTUBE_IMG_URL

async def get_thumb(videoid: str, user_id: int, user_name: str):
    # 🔥 Sabse Pehle Purana Kachra Saaf Karo (Delete System)
    if not os.path.exists("cache"):
        os.mkdir("cache")
    
    for file in os.listdir("cache"):
        if file.startswith(f"thumb_{videoid}") or file.startswith(f"user_{user_id}"):
            try: os.remove(os.path.join("cache", file))
            except: pass

    # Unique path taaki Telegram cache ko bypass kiya ja sake
    final_path = f"cache/thumb_{videoid}_{random.randint(1000, 9999)}.png"
    temp_path = f"cache/temp_{videoid}.png"
    user_pfp_path = f"cache/user_{user_id}.png"
    
    frame_path = "AnonXMusic/assets/Krish.png"
    icons_path = "AnonXMusic/assets/icons.png"

    url = f"https://www.youtube.com/watch?v={videoid}"
    try:
        results = VideosSearch(url, limit=1)
        res = await results.next()
        result = res["result"][0]
        title = result["title"]
        thumbnail = result["thumbnails"][0]["url"].split("?")[0]

        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(temp_path, mode="wb")
                    await f.write(await resp.read())
                    await f.close()

        # User photo download
        try:
            pfp = await app.get_profile_photos(user_id, limit=1)
            if pfp:
                await app.download_media(pfp[0].file_id, file_name=user_pfp_path)
            else:
                user_pfp_path = None
        except:
            user_pfp_path = None

        # Processing Background
        youtube = Image.open(temp_path).convert("RGBA")
        bg = youtube.resize((1280, 720)).filter(ImageFilter.GaussianBlur(30))
        
        # Frame placement (Krish.png)
        if os.path.exists(frame_path):
            frame = Image.open(frame_path).convert("RGBA").resize((1280, 720))
            bg.paste(frame, (0, 0), frame)

        # 📍 FIXED COORDINATES (Galti Sudhari):
        # Gaane ki photo ko circle mein (Position adjustment)
        pfp_size = (315, 315)
        song_img = youtube.resize(pfp_size, Image.LANCZOS)
        mask = Image.new("L", pfp_size, 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.ellipse([0, 0, 315, 315], fill=255)
        bg.paste(song_img, (130, 185), mask) # Thoda shift kiya hai frame ke andar lane ke liye

        # Icons placement
        if os.path.exists(icons_path):
            icons = Image.open(icons_path).convert("RGBA").resize((300, 70))
            bg.paste(icons, (550, 380), icons)

        # User photo placement (Requested By Photo)
        if user_pfp_path and os.path.exists(user_pfp_path):
            u_size = (80, 80)
            u_img = Image.open(user_pfp_path).convert("RGBA").resize(u_size, Image.LANCZOS)
            u_mask = Image.new("L", u_size, 0)
            ImageDraw.Draw(u_mask).ellipse([0, 0, 80, 80], fill=255)
            bg.paste(u_img, (550, 480), u_mask) # User photo ki position fix ki

        # Text Drawing
        draw = ImageDraw.Draw(bg)
        try:
            font_title = ImageFont.truetype("AnonXMusic/AM/f.ttf", 40)
            font_req = ImageFont.truetype("AnonXMusic/AM/f.ttf", 25)
        except:
            font_title = font_req = ImageFont.load_default()

        clean_title = title[:25] + "..." if len(title) > 25 else title
        draw.text((550, 280), clean_title, font=font_title, fill="white")
        draw.text((650, 505), f"By: {user_name}", font=font_req, fill="#00FFFF")

        # Save and return
        bg.convert("RGB").save(final_path)
        
        # Cleanup
        if os.path.exists(temp_path): os.remove(temp_path)
        
        return final_path

    except Exception as e:
        print(f"Error: {e}")
        return YOUTUBE_IMG_URL
        
