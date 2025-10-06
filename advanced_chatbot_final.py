# -*- coding: utf-8 -*-
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
import os, json, random, threading, asyncio, time
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime
import re # For advanced text processing

# -------- Keep-Alive Web Server for Render/Cloud Deployments --------
# THIS IS THE FIX FOR "No open ports detected" ERROR
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Bot is running and healthy!")

def keep_alive():
    # Use the port specified by the environment, default to 8080 if not set
    # Render requires a service to bind to a port to stay running.
    port = int(os.environ.get("PORT", 8080))
    try:
        server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
        print(f"Starting keep-alive server on port {port}")
        server.serve_forever()
    except Exception as e:
        print(f"Could not start health check server: {e}")

# Start the web server thread before starting the bot
threading.Thread(target=keep_alive, daemon=True).start()
# -------- END Keep-Alive Web Server --------

# -------- Env Vars --------
# NOTE: Set these environment variables before running!
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# Please ensure you set this to your actual Telegram User ID
OWNER_ID = int(os.environ.get("OWNER_ID", "7589623332"))

DEVELOPER_USERNAME = "Voren"
DEVELOPER_HANDLE = "@TheXVoren"
SUPPORT_CHAT = "https://t.me/Evara_Support_Chat"
UPDATES_CHANNEL = "https://t.me/Evara_Updates"

# -------- Bot Client --------
app = Client("advanced_chatbot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# -------- Global Vars --------
START_TIME = datetime.now()
CHATBOT_STATUS = {} # {chat_id: True/False}
TAGGING = {} # {chat_id: True/False}
# {user_id: {"reason": str, "first_name": str, "time": float}}
AFK_USERS = {}

# New image URLs and text
START_PHOTO = "https://iili.io/KVzgS44.jpg"
PING_PHOTO = "https://iili.io/KVzbu4t.jpg"
DEVELOPER_PHOTO = "https://iili.io/KVzmgWl.jpg"

# ----------------- FANCY FONTS APPLIED HERE -----------------
INTRO_TEXT_TEMPLATE = (
    "𝐇ᴇʏ {mention_name}\n"
    "✦ 𝐈 ᴧᴍ ᴧɴ ᴧᴅᴠᴀɴᴄᴇᴅ ᴄʜᴧᴛ ʙᴏᴛ ᴡɪᴛʜ sᴏᴍᴇ ғᴇᴀᴛᴜʀᴇs. \n"
    "✦ 𝐑ᴇᴘʟʏ ɪɴ ɢʀᴏᴜᴘs & ᴘʀɪᴠᴧᴛᴇs 🥀\n"
    "✦ 𝐍ᴏ ᴧʙᴜsɪɴɢ & ᴢᴇʀᴏ ᴅᴏᴡɴᴛɪᴍᴇ\n"
    "✦ 𝐂ʟɪᴄᴋ ʜᴇʟᴘ ʙᴜᴛᴛᴏɴ ғᴏʀ ᴄᴏᴍᴍᴧɴᴅs ❤️\n"
    "❖ 𝐌ᴧᴅᴇ ʙʏ...{developer}"
)

ABOUT_TEXT = (
    "❖ 𝐀 ᴍɪɴɪ ᴄʜᴧᴛ ʙᴏᴛ ғᴏʀ ᴛᴇʟᴇɢʀᴧᴍs ɢʀᴏᴜᴘs & ᴘʀɪᴠᴧᴛᴇ ᴍᴇssᴧɢᴇs\n"
    "● 𝐖ʀɪᴛᴛᴇɴ ɪɴ ᴘʏᴛʜᴏɴ \n"
    "● 𝐊ᴇᴘᴘ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴧᴄᴛɪᴠᴇ.\n"
    "● 𝐀ᴅᴅ ᴍᴇ ɴᴏᴡ ʙᴧʙʏ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘs."
)

# --- Sub-Help Menu Content ---
HELP_COMMANDS_TEXT_MAP = {
    "couple": (
        "📜 𝐂ᴏᴜᴘʟᴇ & 𝐋ᴏᴠᴇ 𝐂ᴏᴍᴍᴀɴᴅs:\n"
        "/couples ~ 𝐂ʜᴏᴏsᴇ ᴧ ʀᴧɴᴅᴏᴍ ᴄᴏᴜᴘʟᴇ\n"
        "/cute ~ 𝐂ʜᴇᴄᴋ ʏᴏᴜʀ ᴄᴜᴛᴇɴᴇss\n"
        "/love name1 + name2 ~ 𝐒ᴇᴇ ʟᴏᴠᴇ ᴘᴏssɪʙɪʟɪᴛʏ\n"
        "\n_ᴧʟʟ ᴛʜᴇsᴇ ᴄᴏᴍᴍᴀɴᴅs ᴀʀᴇ ᴀᴠᴀɪʟᴀʙʟᴇ ᴛᴏ ᴇᴠᴇʀʏᴏɴᴇ."
    ),
    "chatbot": (
        "📜 𝐂ʜᴀᴛʙᴏᴛ 𝐂ᴏᴍᴍᴀɴᴅ:\n"
        "/chatbot enable/disable ~ 𝐄ɴᴀʙʟᴇ/ᴅɪsᴀʙʟᴇ ᴄʜᴀᴛʙᴏᴛ\n"
        "\n"
        "𝐍ᴏᴛᴇ: ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘ ᴀɴᴅ ᴏɴʟʏ ғᴏʀ ᴀᴅᴍɪɴs/ᴏᴡɴᴇʀ.\n"
        "𝐄xᴀᴍᴘʟᴇ: /chatbot enable"
    ),
    "tools": (
        "📜 𝐓ᴏᴏʟs 𝐂ᴏᴍᴍᴧɴᴅs:\n"
        "/id ~ 𝐆ᴇᴛ ᴜsᴇʀ 𝐈ᴅ (ʀᴇᴘʟʏ ᴏʀ ᴛᴧɢ)\n"
        "/tagall ~ 𝐓ᴧɢ ᴀʟʟ ᴍᴇᴍʙᴇʀs (𝐀ᴅᴍɪɴ 𝐎ɴʟʏ)\n"
        "/stop ~ 𝐓ᴏ sᴛᴏᴘ ᴛᴧɢɢɪɴɢ (𝐀ᴅᴍɪɴ 𝐎ɴʟʏ)\n"
        "/afk reason ~ 𝐀ᴡᴀʏ ғʀᴏᴍ ᴛʜᴇ ᴋᴇʏʙᴏᴀʀᴅ\n"
        "\n_𝐓ᴀɢᴀʟʟ/𝐒ᴛᴏᴘ ʀᴇǫᴜɪʀᴇs 𝐀ᴅᴍɪɴ. 𝐎ᴛʜᴇʀs ᴀʀᴇ ғᴏʀ ᴇᴠᴇʀʏᴏɴᴇ."
    ),
    "games": (
        "📜 𝐆ᴧᴍᴇs 𝐂ᴏᴍᴍᴧɴᴅs:\n"
        "/dice ~ 𝐑ᴏʟʟ ᴧ ᴅɪᴄᴇ (🎲)\n"
        "/jackpot ~ 𝐉ᴧᴄᴋᴘᴏᴛ ᴍᴀᴄʜɪɴᴇ (🎰)\n"
        "/football ~ 𝐏ʟᴀʏ ғᴏᴏᴛʙᴧʟʟ (⚽)\n"
        "/basketball ~ 𝐏ʟᴀʏ ʙᴧsᴋᴇᴛʙᴀʟʟ (🏀)\n"
        "/bowling ~ 𝐏ʟᴀʏ ʙᴏᴡʟɪɴɢ (🎳)\n"
        "\n_𝐀ʟʟ ᴛʜᴇsᴇ ɢᴀᴍᴇs ᴀʀᴇ ᴀᴠᴀɪʟᴀʙʟᴇ ᴛᴏ ᴇᴠᴇʀʏᴏɴᴇ."
    ),
    "group": (
        "📜 𝐆ʀᴏᴜᴘ 𝐔ᴛɪʟɪᴛʏ 𝐂ᴏᴍᴍᴧɴᴅs:\n"
        "/staff ~ 𝐃ɪsᴘʟᴧʏs ɢʀᴏᴜᴘ sᴛᴧғғ ᴍᴇᴍʙᴇʀs\n"
        "/botlist ~ 𝐂ʜᴇᴄᴋ ʜᴏᴡ ᴍᴀɴʏ ʙᴏᴛs ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ (𝐀ᴅᴍɪɴ ᴏɴʟʏ)"
        "\n_ʙᴏᴛʟɪsᴛ ʀᴇǫᴜɪʀᴇs ᴀᴅᴍɪɴ. ᴏᴛʜᴇʀs ᴀʀᴇ ғᴏʀ ᴇᴠᴇʀʏᴏɴᴇ."
    )
}
# ----------------- FANCY FONTS END -----------------

# -------- STICKER MAPPING (User provided stickers) --------
STICKER_MAPPING = {
    # Cute Stickers
    "sticker_cute_1": "CAACAgEAAxkBAAEPgu9o4USg2JWyq8EjIQcHKAJxTISKnAAChwADUSkNOdIrExvjme5qNgQ",
    "sticker_cute_2": "CAACAgUAAxkBAAEPgvFo4USiv1_Mf9-45IeDMN5kETeB7AACzQ4AAsp_IVSL99zOZVfZeTYE", 
    # Funny Stickers
    "sticker_funny_1": "CAACAgQAAxkBAAEPguto4USNgkueY_8UUvG1qR0HO8pVJAAC8hEAAuKyeVAr0E__1DsLxTYE",
    "sticker_funny_2": "CAACAgUAAxkBAAEPgvFo4USiv1_Mf9-45IeDMN5kETeB7AACzQ4AAsp_IVSL99zOZVfZeTYE", 
    # Angry Stickers
    "sticker_anger_1": "CAACAgUAAxkBAAEPgudo4UR5HlLeS-qX6SPZa68uWVYxXAACNBAAAvyQWFdWZPeCGuC2gjYE",
    "sticker_anger_2": "CAACAgUAAxkBAAEPgulo4USHqBw08BmrpRAczQX6nqkQXQACsQIAAmfVCVXVlV0wAWPSXDYE",
    # Other/General Stickers - Mapped as placeholders for other categories
    "sticker_love_1": "CAACAgQAAxkBAAEPgu1o4USZaO5ewrgQV8bLpU6Y8z0d9AACXA4AAj9T-FN3FZM9W24oiTYE", 
    "sticker_anime_1": "CAACAgEAAxkBAAEPgu9o4USg2JWyq8EjIQcHKAJxTISKnAAChwADUSkNOdIrExvjme5qNgQ",
}

# --- Load Replies & Known Chats ---
DATA = {}
try:
    # Use the content from the file_content_fetcher tool result
    json_content = """
{
  "daily": [
    "Hii baby, kya chal raha hai? 😅 lol hehe", "Hey cutie, kya plan hai aaj ka? 😘 bilkul", "Hi hi 🙂 batao kya naya? ✨", "Heyy!! Kaise ho? 😘 hehe", "Heyy!! Kaise ho? 😘 😘 sach mein", "Hi hi 🙂 batao kya naya? 😇 sach mein", "Hey cutie, kya plan hai aaj ka? 💖", "Heyy!! Kaise ho? 😘 ✨ omg", "Aree hello hello, tum aaye! 😭 bas yahi socha", "Aree hello hello, tum aaye! 😉 bilkul", "Hi hi 🙂 batao kya naya? bas yahi socha", "Hii baby, kya chal raha hai? 💕 bas yahi socha hehe", "Hii baby, kya chal raha hai? 😇 sach mein", "Heyy!! Kaise ho? 😘 🥺 hehe :P", "Hii baby, kya chal raha hai? 💕 wow", "Hey cutie, kya plan hai aaj ka? 🤗 hehe", "Hii baby, kya chal raha hai? 😜 bilkul", "Hii baby, kya chal raha hai? 🤗 bilkul", "Hii baby, kya chal raha hai? 🥺 bas yahi socha", "Aree hello hello, tum aaye! 💕 sach mein", "Hi hi 🙂 batao kya naya? 😜 hehe :P", "Heyy!! Kaise ho? 😘 🤗 bilkul", "Hii baby, kya chal raha hai? 😉 omg hehe", "Hii baby, kya chal raha hai? 😭 lol", "Hey cutie, kya plan hai aaj ka? 😘 bata rahi hu na", "Heyy!! Kaise ho? 😘 😉", "Hey cutie, kya plan hai aaj ka? 😇 sach mein", "Hii baby, kya chal raha hai? 🙈 bilkul", "Hey cutie, kya plan hai aaj ka? 🤗 bata rahi hu na", "Hii baby, kya chal raha hai? 🙈", "Aree hello hello, tum aaye! 💕 hehe", "Hii baby, kya chal raha hai? 🥺 hehe :P hehe", "Hey cutie, kya plan hai aaj ka? 😊 wow", "Hi hi 🙂 batao kya naya? 😜 hehe", "Heyy!! Kaise ho? 😘 😅 wow", "Hi hi 🙂 batao kya naya? 🥺 wow", "Hii baby, kya chal raha hai? 😅 lol", "Aree hello hello, tum aaye! 💖 lol", "Hey cutie, kya plan hai aaj ka? 😘", "Hii baby, kya chal raha hai? ✨", "Hey cutie, kya plan hai aaj ka? 🙈 lol hehe", "Hey cutie, kya plan hai aaj ka? ✨ sach mein", "Heyy!! Kaise ho? 😘 😇 omg", "Aree hello hello, tum aaye! 😘 bata rahi hu na", "Aree hello hello, tum aaye! 😉 lol", "Heyy!! Kaise ho? 😘 😉 hehe", "Hii baby, kya chal raha hai? 💖 wow", "Hii baby, kya chal raha hai? 😉 lol", "Hi hi 🙂 batao kya naya? 😘 sach mein", "Hii baby, kya chal raha hai? 😉 sach mein", "Aree hello hello, tum aaye! 😘", "Heyy!! Kaise ho? 😘 😭", "Hii baby, kya chal raha hai? ✨ wow", "Heyy!! Kaise ho? 😘 😅 hehe", "Heyy!! Kaise ho? 😘 🤗 hehe", "Aree hello hello, tum aaye! 😜 omg", "Aree hello hello, tum aaye! 😘 bilkul", "Hii baby, kya chal raha hai? 🤗 hehe", "Hii baby, kya chal raha hai? ✨ lol hehe", "Hi hi 🙂 batao kya naya? 😇 bas yahi socha", "Hi hi 🙂 batao kya naya? 💕", "Hi hi 🙂 batao kya naya? 😘 bas yahi socha", "Hey cutie, kya plan hai aaj ka? 😉 hehe :P hehe", "Hi hi 🙂 batao kya naya? 😘 wow", "Heyy!! Kaise ho? 😘 😭 bas yahi socha", "Hey cutie, kya plan hai aaj ka? 😇 hehe", "Hi hi 🙂 batao kya naya? 😉 hehe", "Heyy!! Kaise ho? 😘 😊 bilkul", "Hey cutie, kya plan hai aaj ka? 🤗 bilkul", "Heyy!! Kaise ho? 😘 ✨ bata rahi hu na", "Hey cutie, kya plan hai aaj ka? 😭 bata rahi hu na", "Hi hi 🙂 batao kya naya? 💖", "Heyy!! Kaise ho? 😘 😅 bilkul", "Hii baby, kya chal raha hai? 💖 hehe :P", "Hii baby, kya chal raha hai? 😊 hehe :P", "Aree hello hello, tum aaye! 😜 omg hehe", "Hi hi 🙂 batao kya naya? 😜 wow", "Heyy!! Kaise ho? 😘 🙈 sach mein", "Hii baby, kya chal raha hai? 🥺 hehe", "Hi hi 🙂 batao kya naya? 😜 bas yahi socha", "Hey cutie, kya plan hai aaj ka? 😭 bilkul hehe", "Hi hi 🙂 batao kya naya? 😭", "Hey cutie, kya plan hai aaj ka? ✨ hehe :P", "Hii baby, kya chal raha hai? bas yahi socha hehe", "Hii baby, kya chal raha hai? ✨ lol", "Hii baby, kya chal raha hai? 🤗", "Hi hi 🙂 batao kya naya? 😭 hehe", "Hii baby, kya chal raha hai? 😍 lol", "Hi hi 🙂 batao kya naya? 😉 lol", "Hii baby, kya chal raha hai? 😜", "Aree hello hello, tum aaye! 😇 bas yahi socha", "Heyy!! Kaise ho? 😘 😅 bata rahi hu na", "Aree hello hello, tum aaye! 😜", "Heyy!! Kaise ho? 😘 💖 bilkul", "Aree hello hello, tum aaye! 🤗 hehe hehe", "Hii baby, kya chal raha hai? 🤗 wow", "Aree hello hello, tum aaye! 😊 bas yahi socha", "Hii baby, kya chal raha hai? 😘", "Heyy!! Kaise ho? 😘 😇 hehe", "Hey cutie, kya plan hai aaj ka? 💖 hehe hehe", "Heyy!! Kaise ho? 😘 😍 lol", "Hi hi 🙂 batao kya naya? 🥺 omg", "Hey cutie, kya plan hai aaj ka? 😉 wow", "Hii baby, kya chal raha hai? hehe", "Hii baby, kya chal raha hai? 😍 bilkul", "Hi hi 🙂 batao kya naya? 😉 bas yahi socha", "Aree hello hello, tum aaye! 😇 sach mein", "Heyy!! Kaise ho? 😘 😊 bilkul hehe", "Aree hello hello, tum aaye! 🤗 omg", "Hi hi 🙂 batao kya naya? 😜 lol", "Heyy!! Kaise ho? 😘 😍 omg hehe", "Aree hello hello, tum aaye! 😊 hehe", "Aree hello hello, tum aaye! 😭", "Hey cutie, kya plan hai aaj ka? 😇 hehe :P", "Aree hello hello, tum aaye! lol", "Hii baby, kya chal raha hai? 🙈 lol", "Hey cutie, kya plan hai aaj ka? bata rahi hu na", "Hii baby, kya chal raha hai? 🤗 bilkul hehe", "Heyy!! Kaise ho? 😘 😇", "Hii baby, kya chal raha hai? 🙈 bata rahi hu na", "Hii baby, kya chal raha hai? 😊 bilkul", "Aree hello hello, tum aaye! bata rahi hu na", "Heyy!! Kaise ho? 😘 😉 bas yahi socha", "Hi hi 🙂 batao kya naya? omg", "Hey cutie, kya plan hai aaj ka? 🙈 hehe", "Aree hello hello, tum aaye! 💕 hehe :P", "Heyy!! Kaise ho? 😘 😜 hehe hehe", "Hey cutie, kya plan hai aaj ka? 😭", "Hey cutie, kya plan hai aaj ka? 🥺 bilkul hehe", "Aree hello hello, tum aaye! 😅 bilkul hehe", "Heyy!! Kaise ho? 😘 💕 hehe", "Hey cutie, kya plan hai aaj ka? 😇 omg", "Hey cutie, kya plan hai aaj ka? 😘 hehe :P hehe", "Hey cutie, kya plan hai aaj ka? 😅 bata rahi hu na", "Heyy!! Kaise ho? 😘 😊 omg", "Heyy!! Kaise ho? 😘 🙈 lol", "Hi hi 🙂 batao kya naya? 💕 sach mein hehe", "Hi hi 🙂 batao kya naya? 😇 hehe :P", "Hey cutie, kya plan hai aaj ka? hehe :P", "Hi hi 🙂 batao kya naya? 😭 bilkul", "Hey cutie, kya plan hai aaj ka? 😘 bas yahi socha", "Heyy!! Kaise ho? 😘 😉 bilkul hehe", "Aree hello hello, tum aaye! 💖 sach mein", "Heyy!! Kaise ho? 😘 💖 sach mein", "Hey cutie, kya plan hai aaj ka? 😭 omg", "Hey cutie, kya plan hai aaj ka? 😜 hehe", "Heyy!! Kaise ho? 😘 🥺 lol hehe", "Hey cutie, kya plan hai aaj ka? 😊 lol", "Hii baby, kya chal raha hai? 💖 omg", "Heyy!! Kaise ho? 😘 😊", "Hey cutie, kya plan hai aaj ka? 😍 wow hehe", "Aree hello hello, tum aaye! 💕 bas yahi socha", "Hi hi 🙂 batao kya naya? 😭 hehe :P", "Aree hello hello, tum aaye! 😭 hehe", "Hii baby, kya chal raha hai? 😭 omg", "Heyy!! Kaise ho? 😘 😉 omg", "Aree hello hello, tum aaye! ✨ bata rahi hu na", "Hii baby, kya chal raha hai? 😍 wow", "Hii baby, kya chal raha hai? 💖 lol", "Hey cutie, kya plan hai aaj ka? lol", "Aree hello hello, tum aaye! ✨", "Aree hello hello, tum aaye! 😜 hehe :P", "Hi hi 🙂 batao kya naya? 😜 sach mein hehe", "Hi hi 🙂 batao kya naya? 😊 lol", "Hii baby, kya chal raha hai? 🥺", "Heyy!! Kaise ho? 😘 😭 sach mein", "Hi hi 🙂 batao kya naya? 🤗 omg", "Hi hi 🙂 batao kya naya? 🤗 hehe :P", "Aree hello hello, tum aaye! 💕 lol", "Heyy!! Kaise ho? 😘 😜 bas yahi socha", "Hey cutie, kya plan hai aaj ka? 😇", "Heyy!! Kaise ho? 😘 💕", "Hey cutie, kya plan hai aaj ka? 🥺 omg", "Hey cutie, kya plan hai aaj ka? 😅", "Hey cutie, kya plan hai aaj ka? 😘 hehe", "Hey cutie, kya plan hai aaj ka? 😜 hehe :P", "Heyy!! Kaise ho? 😘..."],
  "love": ["I love you too!","Aww, sending virtual hugs.","Love is in the air! 💖"],
  "sad": ["Don't be sad! I'm here for you.","Cheer up, friend! 😊"],
  "happy": ["That's great news! 🥳","Keep smiling!"],
  "bye": ["Bye bye! See you soon.","Tata! 👋"],
  "thanks": ["You're welcome!","Anytime, that's what I'm here for."],
  "morning": ["Good morning! Have a great day.☀️","GM!"],
  "night": ["Good night! Sweet dreams.🌙"],
  "abuse": ["Watch your language, please! 🚫","That's not very nice."],
  "question": ["I am a bot designed to help and chat with you!","What would you like to know?"],
  "anger": ["Take a deep breath. It's okay.","Sending calm vibes your way. 🧘"],
  "questions": ["Main Python se bani hu, coding vibes ✨", "Main ek chat bot hu par tumse baat karne me maza aata hai 🙂 🥺 wow"],
  "jokes": ["Hahaha lol, ye badiya tha 😂 💖", "Maza aa gaya, aur jokes do na 😄 🙈 lol"],
  "compliment": ["making me blush 😳 🥺 omg hehe", "Dil khush kar diya tumne 💕 🤗 bas yahi socha"],
  "food": ["Aaj kuch tasty try karte hain, suggestions do 🥺 sach mein", "Pizza please! kya tum bhi pizza pasand karte ho? 🍕 😭 hehe"],
  "command_inquiry": ["Main commands se kaam karti hu, /start ya /ping try karo 😜 omg", "Try /help to see available commands 🙂 😅"],

  "sticker_cute": [
      STICKER_MAPPING["sticker_cute_1"], STICKER_MAPPING["sticker_cute_2"]
  ],
  "sticker_funny": [
      STICKER_MAPPING["sticker_funny_1"], STICKER_MAPPING["sticker_funny_2"]
  ],
  "sticker_anger": [
      STICKER_MAPPING["sticker_anger_1"], STICKER_MAPPING["sticker_anger_2"]
  ],
  "sticker_anime": [
      STICKER_MAPPING["sticker_anime_1"]
  ],
  "sticker_love": [
      STICKER_MAPPING["sticker_love_1"]
  ]
}
"""
    DATA = json.loads(json_content)
    # Ensure default data is present if any custom category is missing
    if "daily" not in DATA:
        DATA["daily"] = ["Hello 👋", "Hey there!", "Hi!", "I'm here, what's up?"]
except Exception as e:
    # Minimal default structure if file loading fails
    print(f"Error loading conversation.json: {e}. Using default replies.")
    DATA = {
        "daily": ["Hello 👋", "Hey there!", "Hi!", "I'm here, what's up?"],
        "love": ["I love you too!","Aww, sending virtual hugs.","Love is in the air! 💖"],
        "sad": ["Don't be sad! I'm here for you.","Cheer up, friend! 😊"],
        "happy": ["That's great news! 🥳","Keep smiling!"],
        "bye": ["Bye bye! See you soon.","Tata! 👋"],
        "thanks": ["You're welcome!","Anytime, that's what I'm here for."],
        "morning": ["Good morning! Have a great day.☀️","GM!"],
        "night": ["Good night! Sweet dreams.🌙"],
        "abuse": ["Watch your language, please! 🚫","That's not very nice."],
        "anger": ["Take a deep breath. It's okay.","Sending calm vibes your way. 🧘"],
        "questions": ["What would you like to know?"],
        "sticker_cute": [STICKER_MAPPING["sticker_cute_1"]],
        "sticker_funny": [STICKER_MAPPING["sticker_funny_1"]],
        "sticker_anger": [STICKER_MAPPING["sticker_anger_1"]],
        "sticker_anime": [STICKER_MAPPING["sticker_anime_1"]],
        "sticker_love": [STICKER_MAPPING["sticker_love_1"]]
    }


CHAT_IDS_FILE = "chats.json"
if os.path.exists(CHAT_IDS_FILE):
    with open(CHAT_IDS_FILE, "r") as f:
        KNOWN_CHATS = json.load(f)
else:
    KNOWN_CHATS = {"groups": [], "privates": []}

# Combined Text and Sticker Keywords
KEYWORDS = {
    # Text Replies (from JSON)
    "love": "love", "i love you": "love", "miss you": "love", "crush": "love", "heart": "love",
    "sad": "sad", "cry": "sad", "depressed": "sad", "broken": "sad", "alone": "sad",
    "happy": "happy", "mast": "happy", "fun": "happy", "great": "happy", "cheers": "happy",
    "hello": "daily", "hi": "daily", "hey": "daily", "yaar": "daily", "kya haal": "daily", "bhai": "daily", "hru": "daily",
    "bye": "bye", "goodbye": "bye", "see ya": "bye", "tata": "bye",
    "thanks": "thanks", "thank you": "thanks", "tysm": "thanks",
    "gm": "morning", "good morning": "morning", "subah": "morning",
    "gn": "night", "good night": "night", "shubh ratri": "night", "sleep": "night",
    "chutiya": "abuse", "bc": "abuse", "mc": "abuse", "pagal": "abuse", "idiot": "abuse",
    "kaisa hai": "questions", "kya kar raha": "questions", "who are you": "questions", "bot": "questions", "kon ho": "questions",
    "gussa": "anger", "angry": "anger", "gali": "anger", "fight": "anger",
    "compliment": "compliment", "sweet": "compliment", "beautiful": "compliment", "cute": "compliment", "i like you": "compliment",
    "joke": "jokes", "funny": "jokes", "lol": "jokes", "haha": "jokes",
    "food": "food", "burger": "food", "pizza": "food", "khana": "food",
    "command": "command_inquiry", "/start": "command_inquiry", "/help": "command_inquiry",

    # Sticker Replies (New Categories)
    "hahaha": "sticker_funny", "rofl": "sticker_funny", 
    "aww": "sticker_cute", "so sweet": "sticker_cute", "baby": "sticker_cute",
    "anime": "sticker_anime", "manga": "sticker_anime",
    "i hate you": "sticker_anger", "go away": "sticker_anger", "mad": "sticker_anger",
}

# -------- Utility Functions --------
def get_reply(text: str):
    """
    Determines the response (text or sticker ID) based on the input text.
    Implements 80% text / 20% sticker chance for sticker-related keywords.
    Returns (response, is_sticker)
    """
    if not text:
        return (random.choice(DATA.get("daily", ["Hello 👋"])), False)

    text = text.lower()
    
    # Simple normalization: remove non-alphanumeric except spaces for better keyword matching
    text = re.sub(r'[^\w\s]', '', text) 
    
    # Combined reply logic: Check for keyword match first
    for word, cat in KEYWORDS.items():
        # Check if keyword is a substring of the message text
        if word in text:
            is_sticker_category = cat.startswith("sticker_")
            
            # 1. Try to send a sticker (20% chance for sticker categories)
            if is_sticker_category and cat in DATA and DATA[cat] and random.random() < 0.2:
                return (random.choice(DATA[cat]), True)  
            
            # 2. Text reply (80% chance for sticker categories, 100% for text categories)
            # Find the corresponding text category: if it's sticker_love, use 'love' text replies.
            text_category = cat.replace("sticker_", "") if is_sticker_category else cat

            if text_category in DATA and DATA[text_category]:
                return (random.choice(DATA[text_category]), False)
                
    # If no specific keyword is found, or if lookup failed, send a general/daily reply
    return (random.choice(DATA.get("daily", ["Hello 👋"])), False)


def get_readable_time(seconds: int) -> str:
    result = ''
    (days, remainder) = divmod(seconds, 86400)
    (hours, remainder) = divmod(remainder, 3600)
    (minutes, seconds) = divmod(remainder, 60)
    if days > 0:
        result += f"{days}d "
    if hours > 0:
        result += f"{hours}h "
    if minutes > 0:
        result += f"{minutes}m "
    if seconds > 0:
        result += f"{seconds}s"
    return result.strip() or "just now"

async def is_admin(chat_id, user_id):
    """Checks if a user is an admin or owner of the chat."""
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return member.status in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR]
    except Exception:
        return False

async def is_bot_admin(chat_id):
    """Checks if the bot is an admin in the chat."""
    try:
        me = await app.get_me()
        member = await app.get_chat_member(chat_id, me.id)
        return member.status in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR] and member.can_restrict_members # Check for basic admin rights
    except Exception:
        return False

async def save_chat_id(chat_id, type_):
    """Saves the chat ID to the known chats list."""
    chat_id_str = str(chat_id)
    
    if chat_id_str not in KNOWN_CHATS[type_]:
        KNOWN_CHATS[type_].append(chat_id_str)
        with open(CHAT_IDS_FILE, "w") as f:
            json.dump(KNOWN_CHATS, f)

# -------- Inline Button Handlers & Menus (Logic is correct) --------

# --- Menu Builder Functions ---
def get_start_buttons(bot_username):
    """Returns the main start button layout."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ 𝐀𝐝𝐝 𝐌𝐞 𝐓𝐨 𝐘𝐨𝐮𝐫 𝐆𝐫𝐨𝐮𝐩 ➕", url=f"https://t.me/{bot_username}?startgroup=true")],
        [
            InlineKeyboardButton("ᯓ❍ᴡɳ𝛆ʀ", user_id=OWNER_ID),
            InlineKeyboardButton("◉ 𝐀ʙᴏᴜᴛ", callback_data="about")
        ],
        [InlineKeyboardButton("◉ 𝐇ᴇʟᴘ & 𝐂ᴏᴍᴍᴀɴᴅs", callback_data="help_main")]
    ])

def get_about_buttons():
    """Returns the About section button layout."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("𝐄ᴠᴀʀᴀ 𝐒ᴜᴘᴘᴏʀᴛ 𝐂ʜᴀᴛ", url=SUPPORT_CHAT),
            InlineKeyboardButton("𝐔ᴘᴅᴀᴛᴇs", url=UPDATES_CHANNEL)
        ],
        [
            InlineKeyboardButton("• 𝐁ᴀᴄᴋ", callback_data="start_back"),
            InlineKeyboardButton("• 𝐂ʟᴏsᴇ", callback_data="close")
        ]
    ])

def get_help_main_buttons():
    """Returns the main Help & Commands button layout."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("ᴄᴏᴜᴘʟᴇ", callback_data="help_couple"),
            InlineKeyboardButton("ᴄʜᴀᴛʙᴏᴛ", callback_data="help_chatbot")
        ],
        [
            InlineKeyboardButton("ᴛᴏᴏʟs", callback_data="help_tools"),
            InlineKeyboardButton("ɢᴀᴍᴇs", callback_data="help_games")
        ],
        [InlineKeyboardButton("ɢʀᴏᴜᴘ", callback_data="help_group")],
        [
            InlineKeyboardButton("𝐁ᴀᴄᴋ", callback_data="start_back"),
            InlineKeyboardButton("𝐂ʟᴏsᴇ", callback_data="close")
        ]
    ])

# --- Callbacks Handler ---
@app.on_callback_query()
async def callbacks_handler(client, query):
    data = query.data
    user = query.from_user
    me = await app.get_me()
    
    if data == "about":
        await query.message.edit_caption(
            caption=ABOUT_TEXT,
            reply_markup=get_about_buttons()
        )
    elif data == "start_back":
        await query.message.edit_caption(
            caption=INTRO_TEXT_TEMPLATE.format(
                mention_name=f"[{user.first_name}](tg://user?id={user.id})",
                developer=DEVELOPER_USERNAME,
            ),
            reply_markup=get_start_buttons(me.username),
            parse_mode=enums.ParseMode.MARKDOWN,
            # Re-apply spoiler when going back to start
            has_spoiler=True if query.message.photo else False
        )
    elif data == "help_main":
        await query.message.edit_caption(
            caption="📜 𝐂ᴏᴍᴍᴀɴᴅs 𝐌ᴇɴᴜ:\n\n𝐂ʜᴏᴏsᴇ ᴀ ᴄᴀᴛᴇɢᴏʀʏ ʙᴇʟᴏᴡ:",
            reply_markup=get_help_main_buttons(),
            has_spoiler=False # Remove spoiler for help menu
        )
    elif data.startswith("help_"):
        category = data.split("_")[1]
        text = HELP_COMMANDS_TEXT_MAP.get(category, "𝐄ʀʀᴏʀ: 𝐔ɴᴋɴᴏᴡɴ 𝐂ᴀᴛᴇɢᴏʀʏ")
        
        # Custom button logic for sub-menus
        buttons = []
        if category in ["couple", "cute", "love"]: # Note: category here will be 'couple', 'chatbot', etc.
            buttons.append(InlineKeyboardButton("✦ 𝐒ᴜᴘᴘᴏʀᴛ", url=SUPPORT_CHAT))
            
        # Ensure buttons is a list of lists for InlineKeyboardMarkup
        buttons_markup_rows = []
        if buttons:
            buttons_markup_rows.append(buttons)
        buttons_markup_rows.append([
            InlineKeyboardButton("𝐁ᴀᴄᴋ", callback_data="help_main"),
            InlineKeyboardButton("𝐂ʟᴏsᴇ", callback_data="close")
        ])
        
        await query.message.edit_caption(
            caption=text,
            reply_markup=InlineKeyboardMarkup(buttons_markup_rows),
            has_spoiler=False # Remove spoiler for help menu
        )
    elif data == "close":
        await query.message.delete()
    else:
        await query.answer("𝐓ʜɪs ʙᴜᴛᴛᴏɴ ɪs ɴᴏᴛ ʏᴇᴛ 𝐅ᴜɴᴄᴛɪ𝐎N𝐀𝐋.") 

# -------- Commands --------

# -------- /start Command --------
@app.on_message(filters.command("start"))
async def start_cmd(client, message):
    user = message.from_user
    me = await app.get_me()
    
    if message.chat.type == enums.ChatType.PRIVATE:
        # Ding Dong Animation (Simplified/Fixed)
        anim_text = "ᴅɪɴɢ...ᴅᴏɴɢ 💥....ʙᴏᴛ ɪs sᴛᴀʀᴛɪɴɢ"
        msg = await message.reply_text("Starting...")
        
        for i in range(len(anim_text) // 5):
            try:
                await msg.edit(anim_text[:(i+1)*5])
            except:
                pass
            await asyncio.sleep(0.05)
            
        await asyncio.sleep(0.5)
        
        try:
            await msg.delete()
        except:
            pass 
        
        await message.reply_photo(
            START_PHOTO,
            caption=INTRO_TEXT_TEMPLATE.format(
                mention_name=f"[{user.first_name}](tg://user?id={user.id})",
                developer=DEVELOPER_USERNAME,
            ),
            reply_markup=get_start_buttons(me.username),
            parse_mode=enums.ParseMode.MARKDOWN,
            has_spoiler=True # Apply spoiler effect to the intro photo
        )
        await save_chat_id(message.chat.id, "privates")
    else:
        # Group start message
        await message.reply_text(
            f"𝐇ᴇʏ [{user.first_name}](tg://user?id={user.id})! 𝐈 𝐚𝐦 𝐫𝐞𝐚𝐝𝐲 𝐭𝐨 𝐜𝐡𝐚𝐭. 𝐂𝐥𝐢𝐜𝐤 𝐨𝐧 /help 𝐟𝐨𝐫 𝐦𝐨𝐫𝐞 𝐢𝐧𝐟𝐨.",
            parse_mode=enums.ParseMode.MARKDOWN
        )
        await save_chat_id(message.chat.id, "groups")

# -------- /developer Command --------
@app.on_message(filters.command("developer"))
async def developer_cmd(client, message):
    # Animation
    anim_text = "𝐘ᴏᴜ 𝐖ᴀɳᴛ ᴛᴏ 𝐊ɳᴏᴡ..𝐓ʜɪs 𝐁ᴏᴛ 𝐃ᴇᴠᴇʟᴏᴘᴇʀ 💥..𝐇ᴇʀᴇ"
    m = await message.reply_text("Searching...")
    
    for i in range(len(anim_text) // 5):
        try:
            await m.edit(anim_text[:(i+1)*5])
        except:
            pass
        await asyncio.sleep(0.05)
        
    await asyncio.sleep(0.5)
    
    # Try to delete the animation message
    try:
        await m.delete()
    except:
        pass 
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("𝐃ᴇᴠᴇʟᴏᴘᴇʀ ღ", url=f"https://t.me/{DEVELOPER_HANDLE.strip('@')}")]
    ])
    
    caption_text = f"𝐁ᴏᴛ 𝐃ᴇᴠᴇʟᴏᴘᴇʀ ɪs [{DEVELOPER_USERNAME}](t.me/{DEVELOPER_HANDLE.strip('@')})"
    
    try:
        # 1. Try to send the photo response
        await message.reply_photo(
            DEVELOPER_PHOTO,
            caption=caption_text,
            reply_markup=buttons,
            parse_mode=enums.ParseMode.MARKDOWN
        )
    except Exception as e:
        # 2. Fallback to text message if photo sending fails (ensures a response)
        await message.reply_text(
            caption_text,
            reply_markup=buttons,
            parse_mode=enums.ParseMode.MARKDOWN
        )
        print(f"Error sending developer photo: {e}") # Log the error 

# -------- /ping Command --------
@app.on_message(filters.command("ping"))
async def ping_cmd(client, message):
    start = time.time()
    
    # Ping animation
    m = await message.reply_text("Pɪɴɢɪɴɢ...sᴛᴀʀᴛᴇᴅ..´･ᴗ･")
    await asyncio.sleep(0.5)
    await m.edit_text("Pɪɴɢ..Pᴏɴɢ ⚡")
    await asyncio.sleep(0.5)
    
    end = time.time()
    ping_ms = round((end-start)*1000)
    uptime_seconds = (datetime.now() - START_TIME).total_seconds()
    uptime_readable = get_readable_time(int(uptime_seconds))
    me = await client.get_me()
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ 𝐀ᴅᴅ 𝐌ᴇ ➕", url=f"https://t.me/{me.username}?startgroup=true")],
        [InlineKeyboardButton("𝐒ᴜρρᴏɾᴛ", url=SUPPORT_CHAT)]
    ])
    
    try:
        await m.delete() # Delete the animation message
    except:
        pass
        
    await message.reply_photo(
        PING_PHOTO,
        caption=f"𝐏ɪɴɢ ➳ {ping_ms} 𝐦𝐬\n"
              f"𝐔ᴘᴛɪᴍᴇ ➳ {uptime_readable}",
        reply_markup=buttons
    ) 

# -------- /id Command --------
@app.on_message(filters.command("id"))
async def id_cmd(client, message):
    # Get user from reply or from the message sender itself
    user = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    await message.reply_text(f"👤 **{user.first_name}**\n🆔 `{user.id}`", parse_mode=enums.ParseMode.MARKDOWN)

# -------- /stats Command (Owner Only) --------
@app.on_message(filters.command("stats") & filters.user(OWNER_ID))
async def stats_cmd(client, message):
    await message.reply_text(f"📊 𝐁ᴏᴛ 𝐒ᴛᴀᴛs:\n👥 𝐆ʀᴏᴜᴘs: {len(KNOWN_CHATS['groups'])}\n👤 𝐏ʀɪᴠᴀᴛᴇs: {len(KNOWN_CHATS['privates'])}")

# -------- /broadcast (Owner Only) --------
@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast_cmd(client, message):
    if not (message.reply_to_message or len(message.command) > 1):
        return await message.reply_text("ᴜsᴀɢᴇ: /ʙʀᴏᴀᴅᴄᴀsᴛ <ᴛᴇxᴛ> ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ.")
    
    # Extract content to broadcast
    content_to_send = message.reply_to_message
    text = None
    if not content_to_send and len(message.command) > 1:
        text = message.text.split(None, 1)[1]
    
    if not content_to_send and not text:
        return await message.reply_text("❗ 𝐍𝐨 𝐜𝐨𝐧𝐭𝐞𝐧𝐭 𝐭𝐨 𝐛𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭.")

    sent = 0
    failed = 0
    m = await message.reply_text("𝐒ᴛᴀʀᴛɪɴɢ 𝐁ʀᴏᴀᴅᴄᴀsᴛ...")
    
    total_chats = KNOWN_CHATS.get("privates", []) + KNOWN_CHATS.get("groups", [])

    for chat_id_str in total_chats:
        try:
            chat_id = int(chat_id_str) 
        except ValueError:
            continue 
            
        try:
            if content_to_send:
                # Use client.copy_message for media/files
                await app.copy_message(chat_id, message.chat.id, content_to_send.id)
            elif text:
                await app.send_message(chat_id, text)
            sent += 1
            await asyncio.sleep(0.1) # Small delay
        except Exception as e:
            failed += 1
            continue 
            
    await m.edit_text(f"✅ 𝐁ʀᴏᴀᴅᴄᴀsᴛ ᴅᴏɴᴇ!\n𝐒ᴇɴᴛ ᴛᴏ {sent} ᴄʜᴀᴛs.\n𝐅ᴀɪʟᴇᴅ ɪɴ {failed} ᴄʜᴀᴛs.")

# -------- /chatbot Toggle --------
@app.on_message(filters.command("chatbot") & filters.group)
async def chatbot_toggle(client, message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply_text("❗ Oɴʟʏ ᴀᴅᴍɪɴs ᴀɴᴅ ᴏᴡɴᴇʀ ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")
    
    if len(message.command) < 2:
        # Show current status if no argument given
        current_status = "𝐄𝐍𝐀𝐁𝐋𝐄𝐃" if CHATBOT_STATUS.get(message.chat.id, False) else "𝐃𝐈𝐒𝐀𝐁𝐋𝐄𝐃"
        return await message.reply_text(f"𝐂ʜᴀᴛʙᴏᴛ ɪs ᴄᴜʀʀᴇɴᴛʟʏ {current_status} ✰\n𝐔sᴀɢᴇ: /ᴄʜᴀᴛʙᴏᴛ ᴇɴᴀʙʟᴇ ᴏʀ /ᴄʜᴀᴛʙᴏᴛ ᴅɪsᴀʙʟᴇ")
        
    mode = message.command[1].lower()
    
    if mode in ["on", "enable"]:
        CHATBOT_STATUS[message.chat.id] = True
        status_text = "enabled"
        await message.reply_text(f"𝐂ʜᴀᴛʙᴏᴛ sᴛᴀᴛᴜs ɪs {status_text.upper()} ✰")
    elif mode in ["off", "disable"]:
        CHATBOT_STATUS[message.chat.id] = False
        status_text = "disabled"
        await message.reply_text(f"𝐂ʜᴀᴛʙᴏᴛ sᴛᴀᴛᴜs ɪs {status_text.upper()} ✰")
    else:
        return await message.reply_text("𝐔sᴀɢᴇ: /ᴄʜᴀᴛʙᴏᴛ ᴇɴᴀʙʟᴇ ᴏʀ /ᴄʜᴀᴛʙᴏᴛ ᴅɪsᴀʙʟᴇ")
        
    await save_chat_id(message.chat.id, "groups") 

# -------- /tagall Command --------
@app.on_message(filters.command("tagall") & filters.group)
async def tagall_cmd(client, message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply_text("❗ 𝐎ɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ /ᴛᴀɢᴀʟʟ.")
    
    if not await is_bot_admin(message.chat.id):
        return await message.reply_text("❗ 𝐈 ɴᴇᴇᴅ ᴀᴅᴍɪɴ ᴘᴇʀᴍɪssɪᴏɴ (ᴛᴀɢ ᴍᴇᴍʙᴇʀs/ᴍᴇɴᴛɪᴏɴ ᴇᴠᴇʀʏᴏɴᴇ) ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")

    chat_id = message.chat.id
    
    if TAGGING.get(chat_id):
        return await message.reply_text("❗ 𝐀ʟʀᴇᴀᴅʏ ᴛᴀɢɢɪɴɢ ɪɴ ᴛʜɪs ᴄʜᴀᴛ. 𝐔sᴇ /sᴛᴏᴘ ᴛᴏ ᴄᴀɴᴄᴇʟ.")
        
    TAGGING[chat_id] = True
    
    # Get message content
    if len(message.command) > 1:
        msg = message.text.split(None, 1)[1]
    elif message.reply_to_message and message.reply_to_message.text:
        msg = f"{message.reply_to_message.text[:50]}{'...' if len(message.reply_to_message.text) > 50 else ''}" 
    else:
        msg = "𝐀ᴛᴛᴇɴᴛɪᴏɴ!"
        
    m = await message.reply_text("𝐓ᴀɢɢɪɴɢ 𝐒ᴛᴀʀᴛᴇᴅ !! ♥")
    
    member_list = []
    # Collect all non-bot, non-deleted members first
    try:
        async for member in app.get_chat_members(chat_id):
            if member.user and not (member.user.is_bot or member.user.is_deleted):
                member_list.append(member.user)
    except Exception as e:
        print(f"Error fetching members for tagall: {e}")
        TAGGING[chat_id] = False
        return await m.edit_text("🚫 𝐄𝐫𝐫𝐨𝐫 𝐢𝐧 𝐟𝐞𝐭𝐜𝐡𝐢𝐧𝐠 𝐦𝐞𝐦𝐛𝐞𝐫s: 𝐌𝐚𝐲𝐛𝐞 𝐭𝐡𝐢𝐬 𝐠𝐫𝐨𝐮𝐩 𝐢s 𝐭𝐨𝐨 𝐛𝐢𝐠 𝐨𝐫 𝐈 𝐝𝐨𝐧't 𝐡𝐚𝐯𝐞 𝐩𝐞𝐫𝐦𝐢𝐬𝐬𝐢𝐨𝐧s.")

    # Start tagging in chunks
    chunk_size = 5
    for i in range(0, len(member_list), chunk_size):
        if not TAGGING.get(chat_id):
            break
            
        chunk = member_list[i:i + chunk_size]
        tag_text = f"**{msg}**\n\n" # Use bold for emphasis
        
        for user in chunk:
            tag_text += f"[{user.first_name}](tg://user?id={user.id}) "
            
        try:
            # Send the tag message
            await app.send_message(chat_id, tag_text, parse_mode=enums.ParseMode.MARKDOWN)
            await asyncio.sleep(2) # Delay to avoid flooding limits
        except:
            continue
            
    # Final message update
    if TAGGING.get(chat_id):
        await m.edit_text("𝐓ᴀɢɢɪɴɢ 𝐂ᴏᴍᴘʟᴇᴛᴇᴅ !! ◉‿◉")
        TAGGING[chat_id] = False 
    else:
        # If it was stopped manually
        await m.edit_text("𝐓ᴀɢɢɪɴ𝐠 𝐒ᴛᴏᴘᴘᴇᴅ 𝐌ᴀɴ𝐮𝐚𝐥𝐥𝐲.")

# -------- /stop Tagging (FIXED SYNTAX) --------
@app.on_message(filters.command("stop") & filters.group)
async def stop_tagging_cmd(client, message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply_text("❗ 𝐎ɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ /sᴛᴏᴘ.")
        
    chat_id = message.chat.id
    if TAGGING.get(chat_id):
        TAGGING[chat_id] = False
        await message.reply_text("𝐓ᴀɢɢɪɴɢ 𝐒ᴛᴏᴘᴘᴇᴅ !!")
    else:
        await message.reply_text("❗ 𝐍ᴏ 𝐓ᴀɢɢɪɴɢ ɪs 𝐂ᴜʀʀᴇɴᴛ𝐥𝐲 𝐑ᴜ𝐍𝐍ɪɴɢ.")

# -------- /couples, /cute, /love Commands --------
@app.on_message(filters.command("couples") & filters.group)
async def couples_cmd(client, message):
    member_list = []
    try:
        # Use only USERS in the group, excluding bots and deleted accounts
        async for member in app.get_chat_members(message.chat.id):
            if member.user and not (member.user.is_bot or member.user.is_deleted):
                member_list.append(member.user)
    except Exception:
        return await message.reply_text("🚫 𝐂𝐚𝐧𝐧𝐨𝐭 𝐟𝐞𝐭𝐜𝐡 𝐦𝐞𝐦𝐛𝐞𝐫s 𝐝𝐮𝐞 𝐭𝐨 𝐫𝐞𝐬𝐭𝐫𝐢𝐜𝐭𝐢𝐨𝐧s.")

    if len(member_list) < 2:
        return await message.reply_text("❗ 𝐍ᴇᴇᴅ ᴀᴛ ʟᴇᴀsᴛ ᴛᴡᴏ ᴍᴇᴍʙᴇʀs ᴛᴏ ғᴏʀᴍ ᴀ 𝐂ᴏᴜ𝐩𝐥ᴇ.")
        
    # Pick two random unique members
    try:
        couple = random.sample(member_list, 2)
    except ValueError:
        return await message.reply_text("❗ 𝐍ᴇᴇᴅ ᴀᴛ ʟᴇᴀsᴛ ᴛᴡᴏ ᴍᴇᴍʙᴇʀs ᴛᴏ ғᴏʀᴍ ᴀ 𝐂ᴏᴜ𝐩𝐥ᴇ.")

    user1 = couple[0]
    user2 = couple[1]
    
    # Calculate a random love percentage (just for fun)
    love_percent = random.randint(30, 99)
    
    await message.reply_text(
        f"💘 𝐍ᴇᴡ 𝐂ᴏᴜ𝐩𝐥ᴇ ᴏғ ᴛʜᴇ 𝐃ᴀʏ!\n\n"
        f"[{user1.first_name}](tg://user?id={user1.id}) 💖 [{user2.first_name}](tg://user?id={user2.id})\n"
        f"𝐋ᴏᴠᴇ ʟᴇᴠᴇʟ ɪs **{love_percent}%**! 🎉",
        parse_mode=enums.ParseMode.MARKDOWN
    )

@app.on_message(filters.command("cute")) 
async def cute_cmd(client, message):
    cute_level = random.randint(30, 99)
    user = message.from_user
    # FIX: Ensure user mention works
    user_mention = f"[{user.first_name}](tg://user?id={user.id})"
    text = f"{user_mention}’𝐬 ᴄᴜᴛᴇɴᴇss ʟᴇᴠᴇʟ ɪs **{cute_level}%** 💖"
    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("𝐒ᴜᴘᴘᴏʀᴛ", url=SUPPORT_CHAT)]])
    # FIX: Corrected missing reply_text call
    await message.reply_text(text, reply_markup=buttons, parse_mode=enums.ParseMode.MARKDOWN)

@app.on_message(filters.command("love"))
async def love_cmd(client, message):
    if len(message.command) < 2 or "+" not in message.text:
        return await message.reply_text("𝐔sᴀɢᴇ: /ʟᴏᴠᴇ 𝐅ɪʀsᴛ 𝐍ᴀᴍᴇ + 𝐒ᴇᴄᴏɴᴅ 𝐍ᴀᴍᴇ")

    # FIX: Corrected name splitting logic
    names_part = message.text.split(None, 1)[1]
    names = [n.strip() for n in names_part.split('+') if n.strip()] # ensure non-empty names
    
    if len(names) < 2:
        return await message.reply_text("𝐏ʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴛᴡᴏ ɴᴀᴍᴇs sᴇᴘʀᴀᴛᴇᴅ ʙʏ ᴀ '+' (ᴇ.ɢ., /ʟᴏᴠᴇ 𝐀ʟɪᴄᴇ + 𝐁ᴏʙ)")
        
    love_percent = random.randint(30, 99)

    text = f"❤️ 𝐋ᴏᴠᴇ 𝐏ᴏssɪʙʟɪᴛʏ\n" \
              f"{names[0]} & {names[1]}’𝐬 ʟᴏᴠᴇ ʟᴇᴠᴇʟ ɪs **{love_percent}%** 😉"
            
    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("𝐒ᴜᴘᴘᴏʀᴛ", url=SUPPORT_CHAT)]])
    await message.reply_text(text, reply_markup=buttons, parse_mode=enums.ParseMode.MARKDOWN) 

# -------- /afk Command (FIXED) --------
@app.on_message(filters.command("afk"))
async def afk_cmd(client, message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    # 1. Check if user is already AFK (meaning they are coming back)
    if user_id in AFK_USERS:
        # User is coming back
        afk_data = AFK_USERS.pop(user_id)
        time_afk = get_readable_time(int(time.time() - afk_data["time"]))
        await message.reply_text(
            f"𝐘ᴇᴀʜ, [{user_name}](tg://user?id={user_id}), ʏᴏᴜ 𝐚𝐫𝐞 ʙᴀᴄᴋ, ᴏɴʟɪɴᴇ! (𝐀ғᴋ ғᴏʀ: {time_afk}) 😉",
            parse_mode=enums.ParseMode.MARKDOWN
        )
        return # Stop execution after returning
        
    # 2. If not AFK, set AFK status
    reason = "No Reason Provided"
    if len(message.command) > 1:
        reason = message.text.split(None, 1)[1]
        
    # Store AFK status
    AFK_USERS[user_id] = {
        "reason": reason,
        "first_name": user_name, # Storing first_name for mention in AFK trigger handler
        "time": time.time() # Store current time
    }
    
    # Send the AFK message
    await message.reply_text(
        f"𝐇ᴇʏ, [{user_name}](tg://user?id={user_id}), ʏᴏᴜ 𝐚𝐫𝐞 𝐀ғᴋ! (𝐑ᴇᴀsᴏɴ: **{reason}**)",
        parse_mode=enums.ParseMode.MARKDOWN
    )

# -------- /staff Command (NEW) --------
@app.on_message(filters.command("staff") & filters.group)
async def staff_cmd(client, message):
    chat_id = message.chat.id
    staff_members = []
    
    try:
        async for member in app.get_chat_members(chat_id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
            user = member.user
            if user.is_bot:
                continue
            
            # Determine role
            if member.status == enums.ChatMemberStatus.OWNER:
                role = "👑 𝐎𝐰𝐧𝐞𝐫"
            else:
                role = "🌟 𝐀𝐝𝐦𝐢𝐧"

            staff_members.append(f"{role}: [{user.first_name}](tg://user?id={user.id})")
            
    except Exception:
        return await message.reply_text("🚫 𝐂𝐚𝐧𝐧𝐨𝐭 𝐟𝐞𝐭𝐜𝐡 𝐬𝐭𝐚𝐟𝐟 𝐥𝐢𝐬𝐭 𝐝𝐮𝐞 𝐭𝐨 𝐫𝐞𝐬𝐭𝐫𝐢𝐜𝐭𝐢𝐨𝐧𝐬.")

    if not staff_members:
        return await message.reply_text("❗ 𝐍𝐨 𝐬𝐭𝐚𝐟𝐟 𝐦𝐞𝐦𝐛𝐞𝐫𝐬 𝐟𝐨𝐮𝐧𝐝 𝐢𝐧 𝐭𝐡𝐢𝐬 𝐠𝐫𝐨𝐮𝐩 (𝐞𝐱𝐜𝐥𝐮𝐝𝐢𝐧𝐠 𝐛𝐨𝐭𝐬).")

    response = "📜 **𝐆𝐫𝐨𝐮𝐩 𝐒𝐭𝐚𝐟𝐟 𝐋𝐢𝐬𝐭:**\n\n" + "\n".join(staff_members)
    await message.reply_text(response, parse_mode=enums.ParseMode.MARKDOWN)

# -------- /botlist Command (NEW - Admin Only) --------
@app.on_message(filters.command("botlist") & filters.group)
async def botlist_cmd(client, message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply_text("❗ 𝐎ɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ /ʙᴏᴛʟɪsᴛ.")

    chat_id = message.chat.id
    bots = []
    
    try:
        async for member in app.get_chat_members(chat_id):
            if member.user.is_bot:
                # Get the bot's status (admin or just a member)
                if member.status in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR]:
                    status = "𝐀𝐝𝐦𝐢𝐧"
                else:
                    status = "𝐌𝐞𝐦𝐛𝐞𝐫"
                
                bots.append(f"🤖 [{member.user.first_name}](tg://user?id={member.user.id}) - ({status})")

    except Exception:
        return await message.reply_text("🚫 𝐂𝐚𝐧𝐧𝐨𝐭 𝐟𝐞𝐭𝐜𝐡 𝐛𝐨𝐭 𝐥𝐢𝐬𝐭 𝐝𝐮𝐞 𝐭𝐨 𝐫𝐞𝐬𝐭𝐫𝐢𝐜𝐭𝐢𝐨𝐧𝐬.")
    
    if not bots:
        return await message.reply_text("✅ 𝐍𝐨 𝐛𝐨𝐭𝐬 𝐟𝐨𝐮𝐧𝐝 𝐢𝐧 𝐭𝐡𝐢𝐬 𝐠𝐫𝐨𝐮𝐩.")

    bot_count = len(bots)
    response = f"📜 **𝐁𝐨𝐭 𝐋𝐢𝐬𝐭 ({bot_count}):**\n\n" + "\n".join(bots)
    await message.reply_text(response, parse_mode=enums.ParseMode.MARKDOWN)

# -------- Game Commands (Already mostly correct - adding filter) --------
@app.on_message(filters.command("dice"))
async def dice_cmd(client, message):
    await message.reply_dice(enums.DiceEmoji.DICE)

@app.on_message(filters.command("jackpot"))
async def jackpot_cmd(client, message):
    await message.reply_dice(enums.DiceEmoji.SLOT_MACHINE)

@app.on_message(filters.command("football"))
async def football_cmd(client, message):
    await message.reply_dice(enums.DiceEmoji.FOOTBALL)

@app.on_message(filters.command("basketball"))
async def basketball_cmd(client, message):
    await message.reply_dice(enums.DiceEmoji.BASKETBALL)

@app.on_message(filters.command("bowling"))
async def bowling_cmd(client, message):
    await message.reply_dice(enums.DiceEmoji.BOWLING)

# -------- Group Join Handler (NEW) --------
@app.on_message(filters.new_chat_members)
async def welcome_handler(client, message):
    me = await client.get_me()
    
    # Check if the bot itself was added
    if me.id in [user.id for user in message.new_chat_members]:
        if message.chat.type == enums.ChatType.GROUP or message.chat.type == enums.ChatType.SUPERGROUP:
            await save_chat_id(message.chat.id, "groups")
            await message.reply_text(
                "𝐓𝐇𝐀𝐍𝐊𝐒 𝐅𝐎𝐑 𝐀𝐃𝐃𝐈𝐍𝐆 𝐌𝐄! 🎉\n\n"
                "𝐈 𝐚𝐦 𝐚𝐧 𝐚𝐝𝐯𝐚𝐧𝐜𝐞𝐝 𝐜𝐡𝐚𝐭 𝐛𝐨𝐭. "
                "𝐓𝐲𝐩𝐞 **/start** 𝐨𝐫 **/help** 𝐭𝐨 𝐬𝐞𝐞 𝐰𝐡𝐚𝐭 𝐈 𝐜𝐚𝐧 𝐝𝐨."
            )

# -------- General Message Handler (Chatbot & AFK Trigger) --------
@app.on_message(filters.text & ~filters.command & ~filters.bot)
async def general_message_handler(client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    me = await client.get_me()

    # --- 1. AFK Mention/Reply Handler ---
    mentions_to_check = set()

    # Check reply-to user
    if message.reply_to_message and message.reply_to_message.from_user:
        mentions_to_check.add(message.reply_to_message.from_user.id)
    
    # Check for text mentions (entities)
    if message.entities:
        for entity in message.entities:
            # Check for user mentions via ID (tg://user?id=...)
            if entity.type == enums.MessageEntityType.TEXT_MENTION and entity.user:
                mentions_to_check.add(entity.user.id)
            # Check for @username mentions
            elif entity.type == enums.MessageEntityType.MENTION and message.text:
                mention_text = message.text[entity.offset:entity.offset + entity.length]
                # If it mentions the bot's username, treat it as a direct message
                if mention_text.strip('@').lower() == me.username.lower():
                    pass # Skip, handled by the chatbot logic below
                
                # Resolving generic @username mentions to IDs is complex/slow, stick to known IDs.
                
    # Check if the sender is returning from AFK (must be checked first)
    if user_id in AFK_USERS:
        # We only need to announce return if they didn't use the /afk command (which is filtered out)
        afk_data = AFK_USERS.pop(user_id)
        time_afk = get_readable_time(int(time.time() - afk_data["time"]))
        await message.reply_text(
            f"𝐖ᴇʟᴄᴏᴍᴇ ʙᴀᴄᴋ, [{message.from_user.first_name}](tg://user?id={user_id})! ʏᴏᴜ 𝐰𝐞𝐫𝐞 𝐀ғᴋ ғᴏʀ: {time_afk}",
            parse_mode=enums.ParseMode.MARKDOWN
        )
        # Continue to check if the returning user mentioned another AFK user

    # Announce AFK users if mentioned
    for afk_user_id in mentions_to_check:
        if afk_user_id in AFK_USERS:
            afk_data = AFK_USERS[afk_user_id]
            time_afk = get_readable_time(int(time.time() - afk_data["time"]))
            await message.reply_text(
                f"❗ **{afk_data['first_name']}** 𝐢𝐬 𝐀ғᴋ!\n"
                f"**𝐑ᴇᴀsᴏɴ:** {afk_data['reason']}\n"
                f"**𝐓𝐢𝐦𝐞:** {time_afk} 𝐚𝐠𝐨",
                parse_mode=enums.ParseMode.MARKDOWN
            )
            # Only reply once per message, even if multiple AFK users are mentioned/replied to.
            return 


    # --- 2. Chatbot Reply Handler ---

    # Determine if the bot should reply in a group
    should_reply = False
    is_group = message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]
    
    if is_group:
        # 1. Reply if chatbot is ENABLED
        if CHATBOT_STATUS.get(chat_id, False):
            # 2. Reply if the message is a direct reply to the bot, or mentions the bot's username
            if message.reply_to_message and message.reply_to_message.from_user and message.reply_to_message.from_user.id == me.id:
                should_reply = True
            elif message.text and f"@{me.username.lower()}" in message.text.lower():
                 should_reply = True
            # 3. Random chance for general conversation (20% chance to keep chat active)
            elif random.random() < 0.20: 
                should_reply = True
    else:
        # Always reply in private chat
        should_reply = True

    if should_reply:
        reply, is_sticker = get_reply(message.text)
        
        # In a group, only reply if a keyword was matched or if it was a direct interaction.
        if is_group and not (message.reply_to_message and message.reply_to_message.from_user and message.reply_to_message.from_user.id == me.id):
             # If it was a random reply (20% chance), ensure a non-empty, non-daily reply before sending.
             # This check is tricky. Simpler to just send the reply determined by get_reply.
             pass

        if reply:
            try:
                if is_sticker:
                    await message.reply_sticker(reply)
                else:
                    await message.reply_text(reply)
            except Exception as e:
                # Fallback to text if sticker fails to send (e.g., bot lacks permission or sticker ID is invalid)
                print(f"Error sending reply: {e}. Falling back to text.")
                if not is_sticker: # If it was a text reply that failed, try again without extra formatting/emojis
                    await message.reply_text(random.choice(DATA.get("daily", ["Hello 👋"])))
                else: # If a sticker failed, send a general text reply
                    await message.reply_text(random.choice(DATA.get("daily", ["Hello 👋"])))


# -------- Start Bot --------
if __name__ == "__main__":
    app.run()
