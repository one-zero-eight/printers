# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "aiogram",
#     "tqdm",
# ]
# ///
import argparse
import asyncio
import os

import aiogram
from tqdm import tqdm


async def main(
    to_chat_id: str,
    bot_token: str,
    message_text: str,
):
    tg_bot = aiogram.Bot(token=bot_token)
    to_send = [to_chat_id]

    for to_chat_id in tqdm(to_send, desc="Sending messages"):
        try:
            tqdm.write(f"Sending message to {to_chat_id}")
            await tg_bot.send_message(chat_id=to_chat_id, text=message_text)
            await asyncio.sleep(0.5)
        except Exception as e:
            print(f"Error sending message to {to_chat_id}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--chat_id", type=str, required=True)
    parser.add_argument("--message_text", type=str, required=True)
    parser.add_argument("--bot_token", type=str, required=False, default=os.getenv("TELEGRAM_BOT_TOKEN"))
    args = parser.parse_args()

    asyncio.run(
        main(
            to_chat_id=args.chat_id,
            bot_token=args.bot_token,
            message_text=args.message_text,
        )
    )
