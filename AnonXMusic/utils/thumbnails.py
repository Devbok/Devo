import os
import re
import asyncio
import aiohttp
import aiofiles
from PIL import Image, ImageFilter, ImageDraw, ImageFont
from youtubesearchpython.__future__ import VideosSearch
from AnonXMusic import app
from config import YOUTUBE_IMG_URL

async def get_thumb(videoid: str):
    final_path = f"cache/thumb_{videoid}.png"
    temp_path = f"cache/temp_{videoid}.png"
    frame_path = "AnonXMusic/assets/Oook.png"

    if os.path.isfile(final_path):
        return final_path

    url = f"https://www.youtube.com/watch?v={videoid}"
    try:
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
                    await f.write(await resp.read())
                    await f.close()

        youtube = Image.open(temp_path).convert("RGBA")
        bg = youtube.resize((1280, 720)).filter(ImageFilter.GaussianBlur(20))
        
        if os.path.exists(frame_path):
            frame = Image.open(frame_path).convert("RGBA").resize((1280, 720))
            bg.paste(frame, (0, 0), frame)
        
        pfp_size = (315, 315) 
        pfp = youtube.resize(pfp_size)
        mask = Image.new("L", pfp_size, 0)
        ImageDraw.Draw(mask).ellipse([0, 0, 315, 315], fill=255)
        bg.paste(pfp, (230, 185), mask) 

        draw = ImageDraw.Draw(bg)
        try:
            font_title = ImageFont.truetype("AnonXMusic/AM/f.ttf", 35)
            font_info = ImageFont.truetype("AnonXMusic/AM/f.ttf", 25)
        except:
            font_title = font_info = ImageFont.load_default()

        clean_title = title[:30] + "..." if len(title) > 30 else title
        draw.text((580, 310), clean_title, font=font_title, fill=(255, 255, 255))
        draw.text((580, 380), f"Time: {duration}", font=font_info, fill=(0, 255, 255))
        draw.text((580, 420), f"Playing on {app.me.first_name}", font=font_info, fill=(200, 200, 200))

        bg.convert("RGB").save(final_path)
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return final_path

    except Exception as e:
        print(f"Error: {e}")
        return YOUTUBE_IMG_URL
        
