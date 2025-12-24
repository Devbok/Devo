import os
import re
import random
import aiofiles
import aiohttp
import requests
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageDraw, ImageFont
from unidecode import unidecode
from youtubesearchpython.__future__ import VideosSearch
from AnonXMusic import app
from config import YOUTUBE_IMG_URL

# --- Aapke Original Functions ---
def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    return image.resize((newWidth, newHeight))

def clear(text):
    list = text.split(" ")
    title = ""
    for i in list:
        if len(title) + len(i) < 60:
            title += " " + i
    return title.strip()

def predefined_color():
    colors = [(255, 255, 255), (255, 0, 0)]
    return random.choice(colors)

# --- Updated Get Thumb with Auto-Delete ---
async def get_thumb(videoid: str, user_id: int, user_name: str):
    # 1. AUTO-DELETE LOGIC: Purana kachra saaf karna
    if not os.path.exists("cache"): 
        os.mkdir("cache")
    else:
        # Har call par cache folder ke purane thumbnails delete honge
        for file in os.listdir("cache"):
            if file.endswith(".png") or file.endswith(".jpg"):
                try: os.remove(os.path.join("cache", file))
                except: pass

    final_path = f"cache/{videoid}.png"
    temp_path = f"cache/temp_{videoid}.png"
    bot_img_path = "AnonXMusic/assets/bot.png"
    icons_path = "AnonXMusic/assets/icons.png"

    url = f"https://www.youtube.com/watch?v={videoid}"
    try:
        results = VideosSearch(url, limit=1)
        res = await results.next()
        result = res["result"][0]
        
        title, duration = result["title"], result["duration"]
        thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        channel = result["channel"]["name"]

        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(temp_path, mode="wb")
                    await f.write(await resp.read()); await f.close()

        # 2. DESIGN: Professional Background (Blur 25)
        youtube = Image.open(temp_path).convert("RGBA")
        bg = youtube.resize((1280, 720)).filter(ImageFilter.GaussianBlur(25))
        enhancer = Image.new("RGBA", (1280, 720), (0, 0, 0, 160)) 
        bg = Image.alpha_composite(bg, enhancer)
        draw = ImageDraw.Draw(bg)

        # 3. DESIGN: Dashboard & Logo
        draw.rounded_rectangle([260, 200, 1020, 520], radius=45, fill=(15, 15, 15, 190), outline=(255, 255, 255, 30), width=1)
        
        if os.path.exists(bot_img_path):
            bot_img = Image.open(bot_img_path).convert("RGBA").resize((110, 110))
            b_mask = Image.new("L", (110, 110), 0)
            ImageDraw.Draw(b_mask).ellipse([0, 0, 110, 110], fill=255)
            bg.paste(bot_img, (585, 145), b_mask)

        # 4. DESIGN: Rounded Cover Image
        song_img = youtube.resize((260, 260), Image.LANCZOS)
        s_mask = Image.new("L", (260, 260), 0)
        ImageDraw.Draw(s_mask).rounded_rectangle([0, 0, 260, 260], radius=35, fill=255)
        bg.paste(song_img, (300, 230), s_mask)

        # 5. DESIGN: Crystal Clean Text (Title 42px, Details 24px)
        try:
            f_title, f_small, f_time = ImageFont.truetype("AnonXMusic/AM/f.ttf", 42), ImageFont.truetype("AnonXMusic/AM/f.ttf", 24), ImageFont.truetype("AnonXMusic/AM/f.ttf", 18)
        except: f_title = f_small = f_time = ImageFont.load_default()

        draw.text((610, 245), title[:20] + "...", font=f_title, fill="white")
        draw.text((610, 310), f"{channel} • YouTube", font=f_small, fill=(180, 180, 180))

        # 6. DESIGN: Sleek Progress Bar & Icons
        draw.line([610, 375, 930, 375], fill=(255, 255, 255, 50), width=3)
        draw.line([610, 375, 780, 375], fill="#FF0000", width=3)
        draw.ellipse([776, 371, 784, 379], fill="#FF0000", outline="white", width=1)
        draw.text((610, 385), "00:00", font=f_time, fill=(200, 200, 200))
        draw.text((895, 385), f"{duration}", font=f_time, fill=(200, 200, 200))

        if os.path.exists(icons_path):
            icons = Image.open(icons_path).convert("RGBA").resize((150, 35))
            r, g, b, a = icons.split(); a = a.point(lambda i: i * 0.8) # 80% Transparency
            icons = Image.merge('RGBA', (r, g, b, a))
            bg.paste(icons, (655, 415), icons)

        draw.text((610, 485), f"Requested By: {user_name}", font=f_small, fill="white")

        bg.convert("RGB").save(final_path)
        if os.path.exists(temp_path): os.remove(temp_path)
        return final_path

    except Exception as e:
        print(f"Error: {e}"); return YOUTUBE_IMG_URL
        
