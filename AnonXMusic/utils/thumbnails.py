import os
import random
import asyncio
import aiohttp
import aiofiles
from PIL import Image, ImageFilter, ImageDraw, ImageFont
from youtubesearchpython.__future__ import VideosSearch
from AnonXMusic import app
from config import YOUTUBE_IMG_URL

async def get_thumb(videoid: str, user_id: int, user_name: str):
    # 1. Automatic Cache Reset (Har baar purana file hatane ka system)
    if not os.path.exists("cache"): os.mkdir("cache")
    for file in os.listdir("cache"):
        if file.startswith(f"thumb_{videoid}"):
            try: os.remove(os.path.join("cache", file))
            except: pass

    # Unique path taaki Telegram refresh ho sake
    final_path = f"cache/thumb_{videoid}_{random.randint(1000, 9999)}.png"
    temp_path = f"cache/temp_{videoid}.png"
    user_pfp_path = f"cache/user_{user_id}.png"
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

        # User Profile Photo download
        try:
            pfp = await app.get_profile_photos(user_id, limit=1)
            if pfp: await app.download_media(pfp[0].file_id, file_name=user_pfp_path)
            else: user_pfp_path = None
        except: user_pfp_path = None

        # 2. Background: Blurred YouTube Thumbnail
        youtube = Image.open(temp_path).convert("RGBA")
        bg = youtube.resize((1280, 720)).filter(ImageFilter.GaussianBlur(45))
        draw = ImageDraw.Draw(bg)

        # 3. Glassmorphism Card (White Glowing Box)
        # Position aur Size ko 2135 ke mutabik balance kiya hai
        card_coords = [250, 160, 1030, 560]
        draw.rounded_rectangle(card_coords, radius=50, fill=(255, 255, 255, 25), outline=(255, 255, 255, 70), width=2)

        # 4. Rounded Song Image (Left Side inside card)
        s_size = (320, 320)
        song_img = youtube.resize(s_size, Image.LANCZOS)
        s_mask = Image.new("L", s_size, 0)
        ImageDraw.Draw(s_mask).rounded_rectangle([0, 0, 320, 320], radius=45, fill=255)
        bg.paste(song_img, (300, 200), s_mask)

        # 5. Top Center User PFP (Like Screenshot 2135)
        if user_pfp_path and os.path.exists(user_pfp_path):
            u_size = (115, 115)
            u_img = Image.open(user_pfp_path).convert("RGBA").resize(u_size, Image.LANCZOS)
            u_mask = Image.new("L", u_size, 0)
            ImageDraw.Draw(u_mask).ellipse([0, 0, 115, 115], fill=255)
            bg.paste(u_img, (582, 45), u_mask)
            draw.ellipse([578, 41, 702, 164], outline=(255, 255, 255, 120), width=4)

        # 6. DYNAMIC PROGRESS BAR (White & Red)
        # White Background Line
        draw.line([660, 380, 960, 380], fill=(255, 255, 255, 100), width=8)
        # Red Progress Line (60% Progress for professional feel)
        draw.line([660, 380, 840, 380], fill="#FF0000", width=8)
        # Red Glow Dot (Current position)
        draw.ellipse([835, 375, 845, 385], fill="#FF0000", outline="white", width=2)

        # 7. Icons Placement (Under the bar)
        if os.path.exists(icons_path):
            icons = Image.open(icons_path).convert("RGBA").resize((250, 60))
            bg.paste(icons, (685, 410), icons)

        # 8. Text & Title
        try:
            f_title = ImageFont.truetype("AnonXMusic/AM/f.ttf", 34)
            f_small = ImageFont.truetype("AnonXMusic/AM/f.ttf", 22)
        except: f_title = f_small = ImageFont.load_default()

        clean_title = title[:22] + "..." if len(title) > 22 else title
        draw.text((660, 240), clean_title, font=f_title, fill="white")
        draw.text((660, 300), "YouTube Music Streaming", font=f_small, fill=(200, 200, 200))
        draw.text((660, 490), f"Requested By: {user_name}", font=f_small, fill="#00FFFF")

        # Save and Cleanup
        bg.convert("RGB").save(final_path)
        if os.path.exists(temp_path): os.remove(temp_path)
        if user_pfp_path and os.path.exists(user_pfp_path): os.remove(user_pfp_path)
        
        return final_path

    except Exception as e:
        print(f"Error: {e}"); return YOUTUBE_IMG_URL
        
