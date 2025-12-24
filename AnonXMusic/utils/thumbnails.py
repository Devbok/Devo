import os
import random
import asyncio
import aiohttp
import aiofiles
from PIL import Image, ImageFilter, ImageDraw, ImageFont
from youtubesearchpython.__future__ import VideosSearch
from AnonXMusic import app
from config import YOUTUBE_IMG_URL

async def get_thumb(videoid: str, user_id: int, user_name: str):
    # 1. Reset System (Purana cache saaf karna)
    if not os.path.exists("cache"): os.mkdir("cache")
    for file in os.listdir("cache"):
        if file.startswith(f"thumb_{videoid}"):
            try: os.remove(os.path.join("cache", file))
            except: pass

    final_path = f"cache/thumb_{videoid}_{random.randint(1000, 9999)}.png"
    temp_path = f"cache/temp_{videoid}.png"
    user_pfp_path = f"cache/user_{user_id}.png"
    frame_path = "AnonXMusic/assets/Krish.png"

    try:
        results = VideosSearch(f"https://www.youtube.com/watch?v={videoid}", limit=1)
        res = await results.next()
        result = res["result"][0]
        title, thumbnail = result["title"], result["thumbnails"][0]["url"].split("?")[0]

        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(temp_path, mode="wb")
                    await f.write(await resp.read()); await f.close()

        # User photo download
        try:
            pfp = await app.get_profile_photos(user_id, limit=1)
            if pfp: await app.download_media(pfp[0].file_id, file_name=user_pfp_path)
            else: user_pfp_path = None
        except: user_pfp_path = None

        # Background & Frame
        youtube = Image.open(temp_path).convert("RGBA")
        bg = youtube.resize((1280, 720)).filter(ImageFilter.GaussianBlur(40))
        if os.path.exists(frame_path):
            frame = Image.open(frame_path).convert("RGBA").resize((1280, 720))
            bg.paste(frame, (0, 0), frame)

        # 2. Main Song Image (Rounded Box - Dashboard Style)
        # Screenshot 2135 ke hisaab se position adjustment
        s_size = (280, 280)
        song_img = youtube.resize(s_size, Image.LANCZOS)
        # Rounded corner mask
        mask = Image.new("L", s_size, 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.rounded_rectangle([0, 0, 280, 280], radius=40, fill=255)
        bg.paste(song_img, (320, 220), mask) # Center-Left floating

        # 3. Requester PFP (Top Center Circle - Like 2135)
        if user_pfp_path and os.path.exists(user_pfp_path):
            u_size = (100, 100)
            u_img = Image.open(user_pfp_path).convert("RGBA").resize(u_size, Image.LANCZOS)
            u_mask = Image.new("L", u_size, 0)
            ImageDraw.Draw(u_mask).ellipse([0, 0, 100, 100], fill=255)
            bg.paste(u_img, (590, 80), u_mask) # Top center placement

        # 4. Text & Title (Professional Alignment)
        draw = ImageDraw.Draw(bg)
        try:
            f_title = ImageFont.truetype("AnonXMusic/AM/f.ttf", 35)
            f_small = ImageFont.truetype("AnonXMusic/AM/f.ttf", 20)
        except: f_title = f_small = ImageFont.load_default()

        clean_title = title[:25] + "..." if len(title) > 25 else title
        draw.text((630, 250), clean_title, font=f_title, fill="white")
        draw.text((630, 310), f"Requested By: {user_name}", font=f_small, fill="#00FFFF")

        bg.convert("RGB").save(final_path)
        if os.path.exists(temp_path): os.remove(temp_path)
        return final_path

    except Exception as e:
        print(f"Error: {e}"); return YOUTUBE_IMG_URL
        
