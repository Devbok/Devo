import asyncio
import importlib
from pyrogram import idle
from pytgcalls.exceptions import NoActiveGroupCall

import config
from AnonXMusic import LOGGER, app, userbot
from AnonXMusic.core.call import Anony
from AnonXMusic.misc import sudo
from AnonXMusic.plugins import ALL_MODULES
from AnonXMusic.utils.database import get_banned_users, get_gbanned
from config import BANNED_USERS

async def init():
    if not any([config.STRING1, config.STRING2, config.STRING3, config.STRING4, config.STRING5]):
        LOGGER(__name__).error("Assistant client variables not defined, exiting...")
        exit()

    await sudo()
    
    # Cleaned Banned Users Logic
    try:
        for db_call in [get_gbanned, get_banned_users]:
            users = await db_call()
            for user_id in users:
                BANNED_USERS.add(user_id)
    except Exception:
        pass

    await app.start()
    for all_module in ALL_MODULES:
        importlib.import_module("AnonXMusic.plugins" + all_module)
    
    LOGGER("AnonXMusic.plugins").info("Successfully Imported Modules...")
    await userbot.start()
    await Anony.start()

    try:
        await Anony.stream_call("https://te.legra.ph/file/29f784eb49d230ab62e9e.mp4")
    except NoActiveGroupCall:
        LOGGER("AnonXMusic").error("Please turn on the videochat of your log group/channel.\n\nStopping Bot...")
        exit()
    except Exception:
        pass

    await Anony.decorators()
    LOGGER("AnonXMusic").info("AnonX Music Bot Started Successfully.")
    await idle()
    await app.stop()
    await userbot.stop()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init())

