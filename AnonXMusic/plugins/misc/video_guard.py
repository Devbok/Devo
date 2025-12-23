
from pyrogram import filters
from AnonXMusic import app

# Sirf Video Play wali commands ko monitor karenge
VIDEO_COMMANDS = ["vplay", "cvplay", "vstream", "cvstream"]

@app.on_message(filters.command(VIDEO_COMMANDS))
async def block_uploaded_video_stream(client, message):
    
    # 1. Check karein agar kisi ne Video/Document/GIF file ko 'REPLY' karke vplay bola hai
    if message.reply_to_message:
        replied = message.reply_to_message
        if replied.video or replied.document or replied.animation:
            return await message.reply_text(
                "❌ **Video Security:**\n\nMain direct upload ki gayi files ko video mode mein play nahi kar sakta. Kripya YouTube link ka use karein."
            )

    # 2. Check karein agar Video file ke 'CAPTION' mein vplay likha hai
    if message.video or message.document or message.animation:
        return await message.reply_text(
            "❌ **Video Security:**\n\nDirect video uploads allow nahi hain. Kripya YouTube se stream karein."
        )

    # Agar normal text query ya link hai, to bot normal tarike se YouTube se play karega
    
