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
    # Unique paths taaki cache ka koi chakkar na rahe
    random_id = random.randint(100, 999)
    final_path = f"cache/thumb_{videoid}_{random_id}.png"
    temp_path = f"cache/temp_{videoid}.png"
    user_pfp_path = f"cache/user_{user_id}.png"
    
    frame_path = "AnonXMusic/assets/Krish.png"
    icons_path = "AnonXMusic/assets/icons.png"

    # 1. Purani files saaf karna (Delete System)
    # Isse hamesha naya design hi load hoga
    for file in os.listdir("cache"):
        if file.startswith(f"thumb_{videoid}"):
            try: os.remove(os.path.join("cache", file))
            except: pass

    url = f"https://www.youtube.com/watch?v={videoid}"
    try:
        # YouTube details nikalna
        results = VideosSearch(url, limit=1)
        res = await results.next()
        result = res["result"][0]
        title = result["title"]
        thumbnail = result["thumbnails"][0]["url"].split("?")[0]

        # 2. Song Thumbnail Download karna
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(temp_path, mode="wb")
                    await f.write(await resp.read())
                    await f.close()

        # 3. User (Requester) ki photo fetch karna
        try:
            pfp = await app.get_profile_photos(user_id, limit=1)
            if pfp:
                await app.download_media(pfp[0].file_id, file_name=user_pfp_path)
            else:
                user_pfp_path = None
        except:
            user_pfp_path = None

        # 4. Background aur Frame processing
        youtube = Image.open(temp_path).convert("RGBA")
        bg = youtube.resize((1280, 720)).filter(ImageFilter.GaussianBlur(25))
        
        if os.path.exists(frame_path):
            frame = Image.open(frame_path).convert("RGBA").resize((1280, 720))
            bg.paste(frame, (0, 0), frame)

        # 5. Main Song Image (Circular placement)
        pfp_size = (315, 315)
        song_img = youtube.resize(pfp_size, Image.LANCZOS)
        mask = Image.new("L", pfp_size, 0)
        ImageDraw.Draw(mask).ellipse([0, 0, 315, 315], fill=255)
        bg.paste(song_img, (230, 185), mask)

        # 6. Icons placement
        if os.path.exists(icons_path):
            icons = Image.open(icons_path).convert("RGBA").resize((350, 80))
            bg.paste(icons, (600, 380), icons)

        # 7. User Profile Photo (Small circular corner)
        if user_pfp_path and os.path.exists(user_pfp_path):
            u_size = (70, 70)
            u_img = Image.open(user_pfp_path).convert("RGBA").resize(u_size, Image.LANCZOS)
            u_mask = Image.new("L", u_size, 0)
            ImageDraw.Draw(u_mask).ellipse([0, 0, 70, 70], fill=255)
            bg.paste(u_img, (585, 480), u_mask)

        # 8. Text drawing (Title & Requester Name)
        draw = ImageDraw.Draw(bg)
        try:
            font_title = ImageFont.truetype("AnonXMusic/AM/f.ttf", 35)
            font_req = ImageFont.truetype("AnonXMusic/AM/f.ttf", 22)
        except:
            font_title = font_req = ImageFont.load_default()

        clean_title = title[:30] + "..." if len(title) > 30 else title
        draw.text((585, 300), clean_title, font=font_title, fill=(255, 255, 255))
        draw.text((670, 500), f"Requested By: {user_name}", font=font_req, fill=(0, 255, 255))

        # Final Save
        bg.convert("RGB").save(final_path)
        
        # Cleanup temp files
        if os.path.exists(temp_path): os.remove(temp_path)
        if user_pfp_path and os.path.exists(user_pfp_path): os.remove(user_pfp_path)
        
        return final_path

    except Exception as e:
        print(f"Error: {e}")
        return YOUTUBE_IMG_URL
        
