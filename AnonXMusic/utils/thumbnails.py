import os
import re
import random
import aiofiles
import aiohttp
from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageOps
from youtubesearchpython.__future__ import VideosSearch
from AnonXMusic import app
from config import YOUTUBE_IMG_URL

async def get_thumb(videoid: str, user_id=None, client=None):
    if os.path.isfile(f"cache/{videoid}_{user_id}.png"):
        return f"cache/{videoid}_{user_id}.png"

    url = f"https://www.youtube.com/watch?v={videoid}"
    try:
        results = VideosSearch(url, limit=1)
        for result in (await results.next())["result"]:
            title = re.sub("\W+", " ", result["title"]).title()
            duration = result.get("duration", "Unknown")
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            channel = result["channel"]["name"]

        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(f"cache/thumb{videoid}.png", mode="wb")
                    await f.write(await resp.read())
                    await f.close()

        youtube = Image.open(f"cache/thumb{videoid}.png")
        blurred_thumbnail = youtube.filter(ImageFilter.GaussianBlur(10)).resize((1280, 720))
        
        # --- LEFT SIDE: USER DP CIRCLE ---
        if user_id and client:
            try:
                user_photo = await client.download_media(user_id, file_name=f"cache/u_{user_id}.jpg")
                pfp = Image.open(user_photo).convert("RGBA").resize((300, 300))
            except:
                pfp = youtube.convert("RGBA").resize((300, 300))
        else:
            pfp = youtube.convert("RGBA").resize((300, 300))

        mask = Image.new("L", (300, 300), 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.ellipse((0, 0, 300, 300), fill=255)
        
        # User Photo Paste
        blurred_thumbnail.paste(pfp, (150, 150), mask)
        
        # Neon Border for User DP
        draw = ImageDraw.Draw(blurred_thumbnail)
        draw.ellipse([150, 150, 450, 450], outline=(0, 255, 255), width=10)
        
        # Listening Now Text
        try:
            font_small = ImageFont.truetype("AnonXMusic/AM/f.ttf", 35)
        except:
            font_small = ImageFont.load_default()
        draw.text((180, 480), "Listening Now...", font=font_small, fill=(255, 255, 255))

        # --- RIGHT SIDE: SONG CARD ---
        original_thumbnail = youtube.resize((450, 350))
        # Card Position (Shifted to Right)
        blurred_thumbnail.paste(original_thumbnail, (700, 150))
        
        # Song Info Text
        draw.text((700, 520), f"Title: {title[:25]}...", font=font_small, fill=(0, 255, 255))
        draw.text((700, 570), f"Channel: {channel}", font=font_small, fill=(255, 255, 255))

        try:
            os.remove(f"cache/thumb{videoid}.png")
        except:
            pass
            
        final_path = f"cache/{videoid}_{user_id}.png"
        blurred_thumbnail.save(final_path)
        return final_path
        
    except Exception as e:
        print(f"Thumb Error: {e}")
        return YOUTUBE_IMG_URL
        
