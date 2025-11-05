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
from pathlib import Path

import aiogram
from tqdm import tqdm


async def main(
    mailing_list_path: Path,
    already_sent_path: Path,
    bot_token: str,
    from_chat_id: str,
    message_id: int,
):
    with mailing_list_path.open() as file:  # should contain telegram ids line by line
        ids = [int(line.strip()) for line in file.readlines()]

    if already_sent_path.exists():
        with already_sent_path.open() as file:
            already_sent = [int(line.strip()) for line in file.readlines()]
    else:
        already_sent = []

    tg_bot = aiogram.Bot(token=bot_token)
    to_send = [user_id for user_id in ids if user_id not in already_sent]

    for user_id in tqdm(to_send, desc="Sending messages"):
        try:
            if user_id in already_sent:
                tqdm.write(f"Skipping {user_id} because it's already sent")
                continue
            tqdm.write(f"Sending message to {user_id} from {from_chat_id}, {message_id}")
            await tg_bot.forward_message(chat_id=user_id, from_chat_id=from_chat_id, message_id=message_id)
            with already_sent_path.open("a+") as file:
                file.write(str(user_id) + "\n")
            already_sent.append(user_id)
            await asyncio.sleep(0.5)
        except Exception as e:
            print(f"Error sending message to {user_id}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--chat_id", type=str, required=False, default="@one_zero_eight")
    parser.add_argument("--message_id", type=int, required=True)
    parser.add_argument("--mailing_list_path", type=Path, required=False, default=Path("mailing_list.txt"))
    parser.add_argument("--already_sent_path", type=Path, required=False, default=Path("already_sent.txt"))
    parser.add_argument("--bot_token", type=str, required=False, default=os.getenv("TELEGRAM_BOT_TOKEN"))
    args = parser.parse_args()

    asyncio.run(
        main(
            mailing_list_path=args.mailing_list_path,
            already_sent_path=args.already_sent_path,
            bot_token=args.bot_token,
            from_chat_id=args.chat_id,
            message_id=args.message_id,
        )
    )
