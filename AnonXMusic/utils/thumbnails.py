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

        # --- 1. PREMIUM BACKGROUND (Midnight Gradient) ---
        # Pure black ki jagah deep gradient taaki bars dikhein
        base_img = Image.new("RGB", (1280, 720), (10, 10, 20)) 
        draw = ImageDraw.Draw(base_img)
        
        # Halka sa vignette effect (Optional but looks pro)
        try:
            youtube = Image.open(f"cache/thumb{videoid}.png")
            bg_blur = youtube.filter(ImageFilter.GaussianBlur(50)).resize((1280, 720))
            base_img = Image.blend(base_img, bg_blur, alpha=0.3)
            draw = ImageDraw.Draw(base_img)
        except:
            pass

        # Fonts
        try:
            font_title = ImageFont.truetype("AnonXMusic/AM/f.ttf", 45)
            font_small = ImageFont.truetype("AnonXMusic/AM/f.ttf", 30)
        except:
            font_title = ImageFont.load_default()
            font_small = ImageFont.load_default()

        # --- 2. LEFT SIDE: USER DP FIX (No Username Needed) ---
        pfp_size = (340, 340)
        if user_id and client:
            try:
                # Big file id logic for better quality
                user = await client.get_users(user_id)
                if user.photo:
                    user_photo = await client.download_media(user.photo.big_file_id, file_name=f"cache/u_{user_id}.jpg")
                    pfp = Image.open(user_photo).convert("RGBA").resize(pfp_size)
                else:
                    pfp = Image.new("RGBA", pfp_size, (30, 30, 40))
            except:
                pfp = Image.new("RGBA", pfp_size, (30, 30, 40))
        else:
            pfp = Image.new("RGBA", pfp_size, (30, 30, 40))

        mask = Image.new("L", pfp_size, 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0, pfp_size[0], pfp_size[1]), fill=255)
        base_img.paste(pfp, (150, 130), mask)
        
        # Neon Cyan Glow Circle
        draw.ellipse([145, 125, 495, 475], outline=(0, 255, 255), width=10)

        # --- 3. DYNAMIC BLACK BARS (Visualizer) ---
        # "Listening Now" ke upar dynamic bars
        for i in range(0, 12):
            bar_x = 160 + (i * 28)
            bar_h = random.randint(20, 80)
            # Black bars with a subtle cyan glow behind them
            draw.rounded_rectangle([bar_x, 540 - bar_h, bar_x + 12, 540], radius=4, fill=(0, 0, 0)) 
        
        draw.text((200, 560), "Listening Now...", font=font_small, fill=(200, 200, 200))

        # --- 4. RIGHT SIDE: SLEEK LANDSCAPE COVER ---
        # Rounded Rectangle Song Cover
        try:
            song_thumb = youtube.convert("RGBA").resize((480, 270)) # 16:9 ratio
            song_mask = Image.new("L", (480, 270), 0)
            ImageDraw.Draw(song_mask).rounded_rectangle([0, 0, 480, 270], radius=20, fill=255)
            base_img.paste(song_thumb, (650, 180), song_mask)
        except:
            pass

        # Now Playing Text with Neon Circle
        draw.ellipse([650, 130, 675, 155], outline=(0, 255, 255), width=5) # Small Circle
        draw.text((690, 120), "NOW PLAYING", font=font_title, fill=(0, 255, 255))
        
        # Track Info (Clean)
        draw.text((650, 470), f"Track: {title[:25]}...", font=font_small, fill=(255, 255, 255))
        draw.text((650, 510), f"By: {channel[:20]}", font=font_small, fill=(180, 180, 180))

        # Bottom Progress Bar (Sleek)
        draw.rounded_rectangle([150, 650, 1130, 660], radius=5, fill=(40, 40, 50))
        draw.rounded_rectangle([150, 650, 750, 660], radius=5, fill=(0, 255, 255))

        try:
            os.remove(f"cache/thumb{videoid}.png")
        except:
            pass
            
        final_path = f"cache/{videoid}_{user_id}.png"
        base_img.save(final_path)
        return final_path
        
    except Exception as e:
        print(f"Thumb Error: {e}")
        return YOUTUBE_IMG_URL
        
