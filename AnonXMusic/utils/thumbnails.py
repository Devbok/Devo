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
    final_path = f"cache/{videoid}_{user_id}.png"
    
    # --- FIXED: FORCE REFRESH ---
    # Purana file delete karna taaki naya design (2114.jpg) apply ho sake
    if os.path.isfile(final_path):
        os.remove(final_path)

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

        # --- PREMIUM BACKGROUND ---
        # Dark Charcoal Gradient look
        base_img = Image.new("RGB", (1280, 720), (15, 15, 25))
        draw = ImageDraw.Draw(base_img)
        
        youtube = Image.open(f"cache/thumb{videoid}.png")
        # Background mein halka sa blur reflection
        bg_blur = youtube.filter(ImageFilter.GaussianBlur(40)).resize((1280, 720))
        base_img = Image.blend(base_img, bg_blur, alpha=0.4)
        draw = ImageDraw.Draw(base_img)

        # Fonts
        try:
            font_title = ImageFont.truetype("AnonXMusic/AM/f.ttf", 45)
            font_small = ImageFont.truetype("AnonXMusic/AM/f.ttf", 32)
        except:
            font_title = ImageFont.load_default()
            font_small = ImageFont.load_default()

        # --- LEFT SIDE: GOL DP (USER ID FIX) ---
        pfp_size = (350, 350)
        if user_id and client:
            try:
                # Direct user fetch for photo (username ignore)
                user = await client.get_users(user_id)
                if user.photo:
                    user_photo = await client.download_media(user.photo.big_file_id, file_name=f"cache/u_{user_id}.jpg")
                    pfp = Image.open(user_photo).convert("RGBA").resize(pfp_size)
                else:
                    pfp = youtube.convert("RGBA").resize(pfp_size)
            except:
                pfp = youtube.convert("RGBA").resize(pfp_size)
        else:
            pfp = youtube.convert("RGBA").resize(pfp_size)

        mask = Image.new("L", pfp_size, 0)
        ImageDraw.Draw(mask).ellipse((0, 0, pfp_size[0], pfp_size[1]), fill=255)
        base_img.paste(pfp, (140, 120), mask)
        
        # Neon Glow Circle
        draw.ellipse([135, 115, 495, 475], outline=(0, 255, 255), width=10)

        # --- DYNAMIC BLACK BARS (ANIMATION FEEL) ---
        for i in range(0, 15):
            bar_x = 150 + (i * 25)
            bar_h = random.randint(20, 90)
            # Black bars on gradient bg
            draw.rounded_rectangle([bar_x, 560 - bar_h, bar_x + 12, 560], radius=5, fill=(0, 0, 0))
        
        draw.text((180, 580), "Listening Now...", font=font_small, fill=(200, 200, 200))

        # --- RIGHT SIDE: GOLAKAR (ROUNDED) SONG COVER ---
        # Chaukor hatakar Rounded Rectangle kiya hai
        song_thumb = youtube.convert("RGBA").resize((500, 280))
        song_mask = Image.new("L", (500, 280), 0)
        ImageDraw.Draw(song_mask).rounded_rectangle([0, 0, 500, 280], radius=35, fill=255)
        base_img.paste(song_thumb, (650, 180), song_mask)

        # "NOW PLAYING" with Small Neon Circle
        draw.ellipse([650, 125, 675, 150], outline=(0, 255, 255), width=5)
        draw.text((690, 115), "NOW PLAYING", font=font_title, fill=(0, 255, 255))
        
        # Song Details
        draw.text((650, 480), f"Track: {title[:22]}...", font=font_small, fill=(255, 255, 255))
        draw.text((650, 530), f"Requested By: {user_id}", font=font_small, fill=(0, 255, 255))

        # Progress Bar
        draw.rounded_rectangle([140, 660, 1140, 672], radius=6, fill=(40, 40, 50))
        draw.rounded_rectangle([140, 660, 700, 672], radius=6, fill=(0, 255, 255))

        try:
            os.remove(f"cache/thumb{videoid}.png")
        except:
            pass
            
        base_img.save(final_path)
        return final_path
        
    except Exception as e:
        print(f"Thumb Error: {e}")
        return YOUTUBE_IMG_URL
            
