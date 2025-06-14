import os
import re
import random
import aiofiles
import aiohttp
import random
import requests
import os
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageDraw, ImageFont
from unidecode import unidecode
from youtubesearchpython.__future__ import VideosSearch
from AnonXMusic import app
from config import YOUTUBE_IMG_URL

def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage

def clear(text):
    list = text.split(" ")
    title = ""
    for i in list:
        if len(title) + len(i) < 60:
            title += " " + i
    return title.strip()

def random_color():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


def predefined_color():
    colors = [
        (255, 0, 0),
        (255, 255, 255),
        (0, 0, 255),
        (255, 255, 0),
        (0, 255, 0),
        (255, 105, 180),
        (128, 0, 128)
    ]
    return random.choice(colors)

def truncate(text):
    list = text.split(" ")
    text1, text2 = "", ""
    for i in list:
        if len(text1) + len(i) < 30:        
            text1 += " " + i
        elif len(text2) + len(i) < 30:       
            text2 += " " + i
    return [text1.strip(), text2.strip()]

async def get_thumb(videoid: str):
    if os.path.isfile(f"cache/{videoid}.png"):
        return f"cache/{videoid}.png"

    url = f"https://www.youtube.com/watch?v={videoid}"
    try:
        results = VideosSearch(url, limit=1)
        for result in (await results.next())["result"]:
            try:
                title = result["title"]
                title = re.sub("\W+", " ", title)
                title = title.title()
            except:
                title = "Unsupported Title"
            try:
                duration = result["duration"]
            except:
                duration = "Unknown Mins"
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            try:
                views = result["viewCount"]["short"]
            except:
                views = "Unknown Views"
            try:
                channel = result["channel"]["name"]
            except:
                channel = "Unknown Channel"
            try:
                upload_date = result["publishedTime"]
            except:
                upload_date = "Unknown Date"

        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(f"cache/thumb{videoid}.png", mode="wb")
                    await f.write(await resp.read())
                    await f.close()

        youtube = Image.open(f"cache/thumb{videoid}.png")
        blurred_thumbnail = youtube.filter(ImageFilter.GaussianBlur(7))
        icon_path = "AnonXMusic/AM/tt.png"
        icon = Image.open(icon_path)
        icon_size = (850, 800)
        icon = icon.resize(icon_size)
        thumbnail_width, thumbnail_height = blurred_thumbnail.size
        icon_width, icon_height = icon.size
        offset_left = 0
        offset_right = 0
        offset_up = 0
        offset_down = 0
        
        icon_position = (
        (thumbnail_width - icon_width) // 2 + offset_right - offset_left,
        (thumbnail_height - icon_height) // 2 + offset_down - offset_up
    )
        blurred_thumbnail.paste(icon, icon_position, icon.convert('RGBA').split()[3])
        original_thumbnail = youtube.resize((215, 170))
        original_with_border = Image.new("RGBA", original_thumbnail.size, (0, 0, 0, 0))
        original_with_border.paste(original_thumbnail, (0, 0), original_thumbnail.convert('RGBA').split()[3])
        original_offset_left = 165
        original_offset_right = 0
        original_offset_up = 100
        original_offset_down = 0

        original_position = (
        (thumbnail_width - original_with_border.width) // 2 + original_offset_right - original_offset_left, 
        (thumbnail_height - original_with_border.height) // 2 + original_offset_down - original_offset_up
    )
        blurred_thumbnail.paste(original_with_border, original_position)
        try:
            font = ImageFont.truetype("AnonXMusic/AM/f.ttf", 20)
        except IOError:
            font = ImageFont.load_default()
        draw = ImageDraw.Draw(blurred_thumbnail)
        title_words = title.split()[:6] 
        truncated_title = ' '.join(title_words)
        draw.text((600, 190), f"{app.me.first_name}", font=font, fill=predefined_color())
        draw.text((600, 220), f"{truncated_title}", font=font, fill=(255, 255,255))
        draw.text((600, 260), f"{channel}", font=font, fill=(255, 255,255))
        try:
            os.remove(f"cache/thumb{videoid}.png")
        except:
            pass
        blurred_thumbnail.save(f"cache/{videoid}.png")
        return f"cache/{videoid}.png"
    except Exception as e:
        print(e)
        return YOUTUBE_IMG_URL
