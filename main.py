import asyncio
import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

from telethon import TelegramClient
from telethon.errors import (
    AuthKeyUnregisteredError,
    FloodWaitError,
    SessionRevokedError,
    UserDeactivatedError,
)
from telethon.sessions import StringSession
from telethon.tl.functions.account import UpdateProfileRequest

API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
SESSION = os.environ.get("SESSION")
TIMEZONE = os.environ.get("TIMEZONE", "Asia/Tehran")
NAME_PREFIX = os.environ.get("NAME_PREFIX", "𝑹𝒆𝒛𝒂")

missing = [k for k, v in
           {"API_ID": API_ID, "API_HASH": API_HASH, "SESSION": SESSION}.items()
           if not v]
if missing:
    print("Missing environment variables:", ", ".join(missing), flush=True)
    sys.exit(1)

tz = ZoneInfo(TIMEZONE)
client = TelegramClient(StringSession(SESSION), int(API_ID), API_HASH)


def log(*args):
    print(*args, flush=True)


async def main():
    await client.connect()

    if not await client.is_user_authorized():
        log("Session is not valid. Generate a new SESSION with generate_session.py")
        sys.exit(1)

    me = await client.get_me()
    log(f"Logged in as: {me.first_name} (id={me.id})")

    last_clock = None

    while True:
        clock = datetime.now(tz).strftime("%H:%M")

        if clock != last_clock:
            try:
                await client(UpdateProfileRequest(first_name=f"{NAME_PREFIX} | {clock}"))
                last_clock = clock
                log("Profile name updated:", clock)
            except FloodWaitError as e:
                log(f"FloodWait: sleeping {e.seconds}s")
                await asyncio.sleep(e.seconds + 1)
                continue
            except (AuthKeyUnregisteredError, SessionRevokedError, UserDeactivatedError):
                log("Session was revoked or account deactivated. Generate a new SESSION.")
                sys.exit(1)
            except Exception as e:
                log("Update failed, retrying:", repr(e))
                await asyncio.sleep(10)
                continue

        await asyncio.sleep(15)


if __name__ == "__main__":
    try:
        client.loop.run_until_complete(main())
    finally:
        client.loop.run_until_complete(client.disconnect())
