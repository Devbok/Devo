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
    # 1. Sabse Pehle Purana Kachra Saaf Karo (Delete System)
    if not os.path.exists("cache"): os.mkdir("cache")
    for file in os.listdir("cache"):
        if file.startswith(f"thumb_{videoid}"):
            try: os.remove(os.path.join("cache", file))
            except: pass

    # Unique path taaki Telegram purana cache na dikhaye
    final_path = f"cache/thumb_{videoid}_{random.randint(1000, 9999)}.png"
    temp_path = f"cache/temp_{videoid}.png"
    icons_path = "AnonXMusic/assets/icons.png"

    try:
        url = f"https://www.youtube.com/watch?v={videoid}"
        results = VideosSearch(url, limit=1)
        res = await results.next()
        result = res["result"][0]
        title, thumbnail = result["title"], result["thumbnails"][0]["url"].split("?")[0]

        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(temp_path, mode="wb")
                    await f.write(await resp.read()); await f.close()

        # 2. Dark Premium Background
        youtube = Image.open(temp_path).convert("RGBA")
        # Background ko thoda dark rakhenge jaisa 2150 mein hai
        bg = youtube.resize((1280, 720)).filter(ImageFilter.GaussianBlur(18))
        enhancer = Image.new("RGBA", bg.size, (0, 0, 0, 100)) # Dark layer
        bg = Image.alpha_composite(bg, enhancer)
        draw = ImageDraw.Draw(bg)

        # 3. Dark Glass Dashboard Card (2150 Style)
        # Coordinates ko balance kiya hai taaki card bich mein floating lage
        card_coords = [260, 200, 1020, 520]
        # Dark translucent fill
        draw.rounded_rectangle(card_coords, radius=45, fill=(20, 20, 20, 180), outline=(255, 255, 255, 30), width=1)

        # 4. Rounded Song Image (Left Side)
        s_size = (260, 260)
        song_img = youtube.resize(s_size, Image.LANCZOS)
        s_mask = Image.new("L", s_size, 0)
        ImageDraw.Draw(s_mask).rounded_rectangle([0, 0, 260, 260], radius=40, fill=255)
        bg.paste(song_img, (300, 230), s_mask)

        # 5. Elegant Progress Bar (White & Glowing Red)
        # Position Title ke niche (610 x 360)
        # Background line (White)
        draw.line([610, 365, 930, 365], fill=(255, 255, 255, 50), width=4)
        # Progress line (Red) - 45% Progress for visual balance
        draw.line([610, 365, 760, 365], fill="#FF0000", width=4)
        # Glowing Red Dot
        draw.ellipse([756, 361, 764, 369], fill="#FF0000", outline="white", width=1)

        # 6. Playback Icons (Line ke niche)
        if os.path.exists(icons_path):
            icons = Image.open(icons_path).convert("RGBA").resize((210, 45))
            bg.paste(icons, (650, 405), icons)

        # 7. Professional Text Styling
        try:
            f_title = ImageFont.truetype("AnonXMusic/AM/f.ttf", 36)
            f_small = ImageFont.truetype("AnonXMusic/AM/f.ttf", 20)
        except: f_title = f_small = ImageFont.load_default()

        clean_title = title[:20] + "..." if len(title) > 20 else title
        draw.text((610, 250), clean_title, font=f_title, fill="white")
        draw.text((610, 310), "Universal Records • 7.7K views", font=f_small, fill=(180, 180, 180))
        draw.text((610, 470), f"Requested By: {user_name}", font=f_small, fill="#00FFFF")

        # Final Save
        bg.convert("RGB").save(final_path)
        if os.path.exists(temp_path): os.remove(temp_path)
        
        return final_path

    except Exception as e:
        print(f"Error: {e}"); return YOUTUBE_IMG_URL
        
