import os
import re
import random
import aiohttp
import aiofiles
from PIL import Image, ImageFilter, ImageDraw, ImageFont
from youtubesearchpython.__future__ import VideosSearch
from config import YOUTUBE_IMG_URL

async def get_thumb(videoid: str, user_id: int, user_name: str):
    # 1. CLEANUP & PATHS
    if not os.path.exists("cache"): os.mkdir("cache")
    final_path = f"cache/thumb_{videoid}.png"
    temp_path = f"cache/temp_{videoid}.png"
    bot_img_path = "AnonXMusic/assets/bot.png" # Bot Profile Circle
    icons_path = "AnonXMusic/assets/icons.png"  # Playback Icons

    try:
        url = f"https://www.youtube.com/watch?v={videoid}"
        results = VideosSearch(url, limit=1)
        res = await results.next()
        result = res["result"][0]
        title, duration = result["title"], result["duration"]
        thumbnail = result["thumbnails"][0]["url"].split("?")[0]

        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(temp_path, mode="wb")
                    await f.write(await resp.read()); await f.close()

        # 2. BACKGROUND (Blur & Depth)
        youtube = Image.open(temp_path).convert("RGBA")
        # GaussianBlur 25 for professional soft look
        bg = youtube.resize((1280, 720)).filter(ImageFilter.GaussianBlur(17))
        enhancer = Image.new("RGBA", bg.size, (0, 0, 0, 160)) # Deep Dark Overlay
        bg = Image.alpha_composite(bg, enhancer)
        draw = ImageDraw.Draw(bg)

        # 3. DASHBOARD CARD (Glass Effect)
        # Dark Translucent Box with subtle border
        draw.rounded_rectangle([260, 200, 1020, 520], radius=45, fill=(15, 15, 15, 190), outline=(255, 255, 255, 30), width=1)

        # 4. BOT LOGO (The Center Piece)
        if os.path.exists(bot_img_path):
            bot_img = Image.open(bot_img_path).convert("RGBA").resize((110, 110))
            b_mask = Image.new("L", (110, 110), 0)
            ImageDraw.Draw(b_mask).ellipse([0, 0, 110, 110], fill=255)
            bg.paste(bot_img, (585, 145), b_mask) 

        # 5. ROUNDED SONG COVER
        s_img = youtube.resize((260, 260), Image.LANCZOS)
        mask = Image.new("L", (260, 260), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, 260, 260], radius=35, fill=255)
        bg.paste(s_img, (300, 230), mask)

        # 6. FONTS & WORD CLARITY
        try:
            f_title = ImageFont.truetype("AnonXMusic/AM/f.ttf", 42) # Big Bold Title
            f_small = ImageFont.truetype("AnonXMusic/AM/f.ttf", 24) # Details
            f_time = ImageFont.truetype("AnonXMusic/AM/f.ttf", 18)  # Timestamp
        except: f_title = f_small = f_time = ImageFont.load_default()

        # Clean Title & Details
        clean_title = title[:20] + "..." if len(title) > 20 else title
        draw.text((610, 245), clean_title, font=f_title, fill="white")
        draw.text((610, 310), "Universal Records • 7.7K views", font=f_small, fill=(180, 180, 180))

        # 7. SLEEK PROGRESS BAR & TIME
        # Thin line (width=3) for premium feel
        draw.line([610, 375, 930, 375], fill=(255, 255, 255, 50), width=3)
        draw.line([610, 375, 780, 375], fill="#FF0000", width=3)
        draw.ellipse([776, 371, 784, 379], fill="#FF0000", outline="white", width=1)
        
        # Timestamps placement
        draw.text((610, 385), "00:00", font=f_time, fill=(200, 200, 200))
        draw.text((895, 385), f"{duration}", font=f_time, fill=(200, 200, 200))

        # 8. THE "CLEAN" ICONS (Transparency & Size)
        if os.path.exists(icons_path):
            # Size chhota aur sleek (145x30)
            icons = Image.open(icons_path).convert("RGBA").resize((145, 30))
            # 80% Opacity for professional blending
            r, g, b, a = icons.split()
            a = a.point(lambda i: i * 0.8) 
            icons = Image.merge('RGBA', (r, g, b, a))
            # Perfect center position
            bg.paste(icons, (655, 415), icons)

        # Requested By: Clear and Bottom-Aligned
        draw.text((610, 485), f"Requested By: {user_name}", font=f_small, fill="white")

        # FINAL RENDER
        bg.convert("RGB").save(final_path)
        if os.path.exists(temp_path): os.remove(temp_path)
        return final_path

    except Exception as e:
        print(f"Error: {e}"); return YOUTUBE_IMG_URL
        
