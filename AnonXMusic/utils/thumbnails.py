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
    # 1. PURANA KACHRA SAAF KARNA (Auto-Delete System)
    if not os.path.exists("cache"): os.mkdir("cache")
    for file in os.listdir("cache"):
        if file.startswith(f"thumb_{videoid}"):
            try: os.remove(os.path.join("cache", file))
            except: pass

    final_path = f"cache/thumb_{videoid}_{random.randint(1000, 9999)}.png"
    temp_path = f"cache/temp_{videoid}.png"
    icons_path = "AnonXMusic/assets/icons.png"

    try:
        url = f"https://www.youtube.com/watch?v={videoid}"
        results = VideosSearch(url, limit=1)
        res = await results.next()
        result = res["result"][0]
        title = result["title"]
        duration = result["duration"]
        thumbnail = result["thumbnails"][0]["url"].split("?")[0]

        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(temp_path, mode="wb")
                    await f.write(await resp.read()); await f.close()

        # 2. BACKGROUND BLUR FIX (Halka aur Saaf)
        youtube = Image.open(temp_path).convert("RGBA")
        # Blur value 25 ki hai taaki 'bhari' na lage
        bg = youtube.resize((1280, 720)).filter(ImageFilter.GaussianBlur(17)) 
        enhancer = Image.new("RGBA", bg.size, (0, 0, 0, 140)) # Dark Overlay
        bg = Image.alpha_composite(bg, enhancer)
        draw = ImageDraw.Draw(bg)

        # 3. DARK GLASS CARD (Glassmorphism)
        # Translucent dark fill jaisa 2150 mein hai
        draw.rounded_rectangle([260, 200, 1020, 520], radius=45, fill=(20, 20, 20, 190), outline=(255, 255, 255, 35), width=1)

        # 4. ROUNDED SONG IMAGE
        s_size = (260, 260)
        song_img = youtube.resize(s_size, Image.LANCZOS)
        s_mask = Image.new("L", s_size, 0)
        ImageDraw.Draw(s_mask).rounded_rectangle([0, 0, 260, 260], radius=40, fill=255)
        bg.paste(song_img, (300, 230), s_mask)

        # 5. PATLI PROGRESS BAR (Width=3)
        # Ekdam sleek look Spotify jaisa
        draw.line([610, 375, 930, 375], fill=(255, 255, 255, 60), width=3) 
        draw.line([610, 375, 780, 375], fill="#FF0000", width=3) # Red Line
        draw.ellipse([776, 371, 784, 379], fill="#FF0000", outline="white", width=1) # Glowing Dot

        # 6. TIMESTAMPS (Time Addition)
        try:
            f_time = ImageFont.truetype("AnonXMusic/AM/f.ttf", 18)
            f_title = ImageFont.truetype("AnonXMusic/AM/f.ttf", 34)
            f_small = ImageFont.truetype("AnonXMusic/AM/f.ttf", 20)
        except: f_time = f_title = f_small = ImageFont.load_default()

        # Left 00:00 aur Right Duration
        draw.text((610, 385), "00:00", font=f_time, fill=(200, 200, 200))
        draw.text((885, 385), f"{duration}", font=f_time, fill=(200, 200, 200))

        # 7. ICONS FIX (Chhote aur Balanced)
        if os.path.exists(icons_path):
            # Size 170x35 kiya taaki space bana rahe
            icons = Image.open(icons_path).convert("RGBA").resize((170, 35))
            bg.paste(icons, (670, 425), icons)

        # 8. TEXT STYLING
        clean_title = title[:22] + "..." if len(title) > 22 else title
        draw.text((610, 255), clean_title, font=f_title, fill="white")
        draw.text((610, 315), "Universal Records • 7.7K views", font=f_small, fill=(170, 170, 170))
        draw.text((610, 475), f"Requested By: {user_name}", font=f_small, fill="#00FFFF")

        # FINAL SAVE
        bg.convert("RGB").save(final_path)
        if os.path.exists(temp_path): os.remove(temp_path)
        return final_path

    except Exception as e:
        print(f"Error: {e}"); return YOUTUBE_IMG_URL
        
