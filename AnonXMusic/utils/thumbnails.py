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

async def get_thumb(videoid: str, user_id=None, client=None):
    final_path = f"cache/{videoid}_{user_id}.png"
    temp_thumb = f"cache/thumb{videoid}.png"
    
    # 1. Force Clean-up for Instant Update
    if os.path.isfile(final_path):
        os.remove(final_path)

    url = f"https://www.youtube.com/watch?v={videoid}"
    try:
        results = VideosSearch(url, limit=1)
        res = await results.next()
        result = res["result"][0]
        
        # CLEAN UI: Hashtags aur special symbols ko filter kiya
        raw_title = result["title"]
        title = re.sub(r'[#@*]', '', raw_title).strip() 
        thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        channel = result["channel"]["name"]

        # 2. Fast & Robust Download (Black Screen Fix)
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(temp_thumb, mode="wb")
                    await f.write(await resp.read())
                    await f.close()

        # 3. Premium Background Engine (2117.jpg Gradient style)
        base_img = Image.new("RGB", (1280, 720), (10, 15, 22))
        youtube = Image.open(temp_thumb)
        bg_blur = youtube.filter(ImageFilter.GaussianBlur(55)).resize((1280, 720))
        base_img = Image.blend(base_img, bg_blur, alpha=0.45) # Deep Glow
        draw = ImageDraw.Draw(base_img)

        # Fonts Setup
        try:
            font_title = ImageFont.truetype("AnonXMusic/AM/f.ttf", 48)
            font_small = ImageFont.truetype("AnonXMusic/AM/f.ttf", 33)
        except:
            font_title = ImageFont.load_default()
            font_small = ImageFont.load_default()

        # 4. Profile Photo Engine (Automatic Fetch)
        pfp_size = (370, 370)
        pfp_found = False
        if user_id:
            try:
                user_info = await app.get_users(user_id)
                if user_info.photo:
                    # Professional high-res download
                    pfp_path = await app.download_media(user_info.photo.big_file_id, file_name=f"cache/u_{user_id}.jpg")
                    pfp = Image.open(pfp_path).convert("RGBA").resize(pfp_size)
                    pfp_found = True
            except: pass

        if not pfp_found:
            pfp = youtube.convert("RGBA").resize(pfp_size)

        # Gol Masking
        mask = Image.new("L", pfp_size, 0)
        ImageDraw.Draw(mask).ellipse((0, 0, pfp_size[0], pfp_size[1]), fill=255)
        base_img.paste(pfp, (120, 105), mask)
        
        # Neon Cyan Outer Glow
        draw.ellipse([115, 100, 495, 480], outline=(0, 255, 255), width=14)

        # 5. Dynamic Visualizer (Black Bars)
        for i in range(0, 18):
            bar_x = 140 + (i * 24)
            bar_h = random.randint(35, 110)
            draw.rounded_rectangle([bar_x, 565 - bar_h, bar_x + 11, 565], radius=6, fill=(0, 0, 0))
        
        draw.text((185, 590), "Listening Now...", font=font_small, fill=(210, 210, 210))

        # 6. Right Side Rounded Card (Sleek Look)
        song_thumb = youtube.convert("RGBA").resize((530, 300))
        song_mask = Image.new("L", (530, 300), 0)
        ImageDraw.Draw(song_mask).rounded_rectangle([0, 0, 530, 300], radius=45, fill=255)
        base_img.paste(song_thumb, (645, 185), song_mask)

        # NOW PLAYING Header with Glow Circle
        draw.ellipse([645, 130, 672, 157], outline=(0, 255, 255), width=6)
        draw.text((690, 120), "NOW PLAYING", font=font_title, fill=(0, 255, 255))
        
        # Clean Track Info
        draw.text((645, 500), f"Track: {title[:22]}...", font=font_small, fill=(255, 255, 255))
        
        # User Name Fetch logic (Clean)
        try:
            req_name = user_info.first_name[:15] if user_id and user_info else "User"
            draw.text((645, 550), f"Requested By: {req_name}", font=font_small, fill=(0, 255, 255))
        except:
            draw.text((645, 550), "Requested By: Guest", font=font_small, fill=(0, 255, 255))

        # Final Render
        base_img.save(final_path)
        
        if os.path.exists(temp_thumb):
            os.remove(temp_thumb)
            
        return final_path
        
    except Exception as e:
        print(f"Thumb Error: {e}")
        return YOUTUBE_IMG_URL
    
