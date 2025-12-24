import os
import re
import random
import asyncio
import aiofiles
import aiohttp
from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageOps
from youtubesearchpython.__future__ import VideosSearch
from AnonXMusic import app
from config import YOUTUBE_IMG_URL

# --- FAST CACHE CLEANER (Baaki bots ke liye safe) ---
def safe_clean_cache():
    if os.path.exists("cache"):
        for file in os.listdir("cache"):
            if file.startswith("thumb_olivia_"):
                try: os.remove(os.path.join("cache", file))
                except: pass

safe_clean_cache()

async def get_thumb(videoid: str):
    # Jerry ka standard path logic
    final_path = f"cache/thumb_olivia_{videoid}.png"
    temp_path = f"cache/temp_olivia_{videoid}.png"

    if os.path.isfile(final_path):
        return final_path

    url = f"https://www.youtube.com/watch?v={videoid}"
    try:
        results = VideosSearch(url, limit=1)
        res = await results.next()
        result = res["result"][0]
        
        title = re.sub("\W+", " ", result["title"]).title()
        thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        channel = result["channel"]["name"]

        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(temp_path, mode="wb")
                    await f.write(await resp.read())
                    await f.close()

        # --- ⚡ NO DELAY / NO BLACK SCREEN CHECK ---
        # Sirf 0.5 sec ka check taaki file system sync ho jaye
        for _ in range(10):
            if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                break
            await asyncio.sleep(0.1)

        # Jerry's Fast Image Processing
        youtube = Image.open(temp_path).convert("RGBA")
        
        # Background: Blurred YouTube Image (Jerry style)
        bg = youtube.resize((1280, 720)).filter(ImageFilter.GaussianBlur(20))
        draw = ImageDraw.Draw(bg)

        # --- 🟢 PREMIUM DESIGN (Rounded Square + Ring) ---
        # 1. Neon Ring (Cyan/Blue)
        draw.ellipse([430, 70, 850, 490], outline=(0, 255, 255), width=10)

        # 2. Rounded Square Thumbnail
        thumb_size = (380, 380)
        pfp = youtube.resize(thumb_size)
        mask = Image.new("L", thumb_size, 0)
        # Corners ko 80 radius se round kiya (Joker look)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, 380, 380], radius=80, fill=255)
        bg.paste(pfp, (450, 90), mask)

        # Font (Jerry's default font path)
        try:
            font = ImageFont.truetype("AnonXMusic/AM/f.ttf", 40)
            font_small = ImageFont.truetype("AnonXMusic/AM/f.ttf", 28)
        except:
            font = ImageFont.load_default()
            font_small = ImageFont.load_default()

        # --- 📝 TEXT (Niche Clean Look) ---
        title_text = title[:35] + "..." if len(title) > 35 else title
        draw.text((640, 540), f"{app.me.first_name}", font=font, fill=(0, 255, 255), anchor="ms")
        draw.text((640, 595), title_text, font=font_small, fill=(255, 255, 255), anchor="ms")

        # Jerry style save (Fast)
        bg.convert("RGB").save(final_path)
        
        if os.path.exists(temp_path):
            os.remove(temp_path)
            
        return final_path

    except Exception as e:
        print(f"Jerry-Mixed Error: {e}")
        return YOUTUBE_IMG_URL
        
