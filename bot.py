# bot.py
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext
import json
import threading
from pathlib import Path
from config import BOT_TOKEN, BATCH_CHANNEL, target_channels, storage_path

# Thread-safe lock for file operations
_lock = threading.Lock()
_store_file = Path(storage_path)

# Load or initialize storage
if _store_file.exists():
    with _store_file.open("r") as f:
        _store = json.load(f)
else:
    _store = {}


def save_record(original_id: int, records: list[tuple[str, int]]):
    with _lock:
        _store[str(original_id)] = records
        with _store_file.open("w") as f:
            json.dump(_store, f, indent=2)


def load_record(original_id: int) -> list[tuple[str, int]]:
    return _store.get(str(original_id), [])


def start(update: Update, context: CallbackContext):
    update.message.reply_text("🤖 Bot is online!")


def send(update: Update, context: CallbackContext):
    if update.effective_chat.username != BATCH_CHANNEL.lstrip("@"):
        return
    orig = update.message.reply_to_message
    if not orig:
        return update.message.reply_text("❌ Reply to a message in batch channel with /send.")

    sent_entries = []
    for chat in target_channels:
        sent = context.bot.copy_message(
            chat_id=chat,
            from_chat_id=orig.chat_id,
            message_id=orig.message_id
        )
        sent_entries.append((chat, sent.message_id))

    save_record(orig.message_id, sent_entries)

    lines = ["✅ Forwarded to channels:"]
    lines += [f"• `{c}` → `{m}`" for c, m in sent_entries]
    context.bot.send_message(
        chat_id=BATCH_CHANNEL,
        text="\n".join(lines),
        parse_mode=ParseMode.MARKDOWN
    )


def delete(update: Update, context: CallbackContext):
    if update.effective_chat.username != BATCH_CHANNEL.lstrip("@"):
        return
    orig_id = update.message.reply_to_message.message_id
    sent_entries = load_record(orig_id)
    if not sent_entries:
        return update.message.reply_text("❌ No records found for that message.")

    deleted = 0
    for c, m in sent_entries:
        try:
            context.bot.delete_message(chat_id=c, message_id=m)
            deleted += 1
        except Exception:
            pass
    update.message.reply_text(f"✅ Deleted {deleted} messages.")


def main():
    updater = Updater(BOT_TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("send", send))
    dp.add_handler(CommandHandler("delete", delete))
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
