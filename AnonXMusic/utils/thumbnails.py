import os
import re
import asyncio
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageFont
from youtubesearchpython.__future__ import VideosSearch
from config import YOUTUBE_IMG_URL

# --- SUPER SAFE CLEANER: Sirf isi bot ki files target karega ---
def safe_clean_cache():
    if os.path.exists("cache"):
        for file in os.listdir("cache"):
            # Humne sirf 'thumb_olivia_' prefix wali files ko target kiya hai
            # Isse baaki bots ki files ko koi khatra nahi hai
            if file.startswith("thumb_olivia_") or file.startswith("temp_olivia_"):
                try:
                    os.remove(os.path.join("cache", file))
                except:
                    pass

# Bot start hote hi sirf apna kachra saaf karega
safe_clean_cache()

async def get_thumb(videoid: str, user_id=None, client=None):
    # Filenames mein unique prefix add kiya
    final_path = f"cache/thumb_olivia_{videoid}_{user_id}.png"
    temp_thumb = f"cache/temp_olivia_{videoid}.png"
    
    if os.path.isfile(final_path):
        return final_path

    try:
        url = f"https://www.youtube.com/watch?v={videoid}"
        results = VideosSearch(url, limit=1)
        res = await results.next()
        result = res["result"][0]
        
        # Title clean (No Hashtags)
        title = re.sub(r'[^a-zA-Z0-9 ]', '', result["title"]).strip()
        thumbnail = result["thumbnails"][0]["url"].split("?")[0]

        # FAST DOWNLOAD logic
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(temp_thumb, mode="wb")
                    await f.write(await resp.read())
                    await f.close()

        # BLACK SCREEN FIX: File ready hone ka wait
        for _ in range(12):
            if os.path.exists(temp_thumb): break
            await asyncio.sleep(0.5)

        # DESIGN (Pure YouTube Thumbnail Focus)
        img = Image.open(temp_thumb).convert("RGB").resize((1280, 720))
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("AnonXMusic/AM/f.ttf", 50)
        except:
            font = ImageFont.load_default()

        # Bottom Bar for Title
        draw.rectangle([0, 600, 1280, 720], fill=(0, 0, 0, 180))
        draw.text((50, 630), f"Now Playing: {title[:42]}...", font=font, fill=(0, 255, 255))

        img.save(final_path)
        
        # Temp file delete
        if os.path.exists(temp_thumb):
            os.remove(temp_thumb)
            
        return final_path

    except Exception as e:
        print(f"Safe Thumb Error: {e}")
        return YOUTUBE_IMG_URL
        
