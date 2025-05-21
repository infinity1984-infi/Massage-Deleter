# config.py

# Telegram bot token
BOT_TOKEN = "<YOUR_BOT_TOKEN_HERE>"

# Batch channel where you issue /send and /delete
BATCH_CHANNEL = "@MyBatchChannel"

# List of target channels to forward to
target_channels = [
    "@ChannelOne",
    "@ChannelTwo",
    "@ChannelThree",
]

# Path to JSON storage file in Termux home directory
storage_path = "/data/data/com.termux/files/home/sent_messages.json"
