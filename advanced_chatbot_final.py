# -*- coding: utf-8 -*-
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
import os, json, random, threading, asyncio, time
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime
import re

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
# Using minimal default values to prevent runtime errors if not set
API_ID = int(os.environ.get("API_ID", "12345")) 
API_HASH = os.environ.get("API_HASH", "abcdef0123456789abcdef0123456789")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "1234567890:AAAAAAAAAAAAAAAAAAAAAAAAA_AAA")

# Please ensure you set this to your actual Telegram User ID
# Using a placeholder ID that is highly unlikely to be real
OWNER_ID = int(os.environ.get("OWNER_ID", "7589623332")) 

DEVELOPER_USERNAME = "Voren"
DEVELOPER_HANDLE = "@TheXVoren"
# UPDATED SUPPORT CHAT LINK
SUPPORT_CHAT = "https://t.me/EvaraSupportChat" 
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

# --- Help Menu Content (Games section removed as requested) ---
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
    "group": (
        "📜 𝐆ʀᴏᴜᴘ 𝐔ᴛɪʟɪᴛʏ 𝐂ᴏᴍᴍᴧɴᴅs:\n"
        "/staff ~ 𝐃ɪsᴘʟᴧʏs ɢʀᴏᴜᴘ sᴛᴧғғ ᴍᴇᴍʙᴇʀs (𝐀ʟʟ)\n"
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
# Using a try/except for conversation.json for robustness
try:
    with open("conversation.json", "r", encoding="utf-8") as f:
        DATA = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    # If the JSON file is missing or corrupt, use a minimal default structure
    print("Warning: conversation.json not found or invalid. Using default replies.")
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
        "question": ["I am a bot designed to help and chat with you!","What would you like to know?"],
        "anger": ["Take a deep breath. It's okay.","Sending calm vibes your way. 🧘"],

        # Sticker categories using user-provided IDs
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


CHAT_IDS_FILE = "chats.json"
if os.path.exists(CHAT_IDS_FILE):
    try:
        with open(CHAT_IDS_FILE, "r") as f:
            KNOWN_CHATS = json.load(f)
    except json.JSONDecodeError:
        KNOWN_CHATS = {"groups": [], "privates": []}
else:
    KNOWN_CHATS = {"groups": [], "privates": []}

# Combined Text and Sticker Keywords
KEYWORDS = {
    # Text Replies (from JSON)
    "love": "love", "i love you": "love", "miss you": "love", "crush": "love", "heart": "love",
    "sad": "sad", "cry": "sad", "depressed": "sad", "broken": "sad", "alone": "sad",
    "happy": "happy", "mast": "happy", "fun": "happy", "great": "happy", "cheers": "happy",
    "hello": "daily", "hi": "daily", "hey": "daily", "yaar": "daily", "kya haal": "daily", "bhai": "daily", "kya ho rha": "daily",
    "bye": "bye", "goodbye": "bye", "see ya": "bye", "tata": "bye",
    "thanks": "thanks", "thank you": "thanks", "tysm": "thanks", "shukriya": "thanks",
    "gm": "morning", "good morning": "morning", "subah": "morning",
    "gn": "night", "good night": "night", "shubh ratri": "night", "sleep": "night",
    "chutiya": "abuse", "bc": "abuse", "mc": "abuse", "pagal": "abuse", "idiot": "abuse", "madar": "abuse", "sister": "abuse",
    "kaisa hai": "question", "kya kar raha": "question", "who are you": "question", "bot": "question",
    "gussa": "anger", "angry": "anger", "gali": "anger",

    # Sticker Replies (New Categories) - using simpler keywords to improve random match
    "hahaha": "sticker_funny", "lol": "sticker_funny", "rofl": "sticker_funny", "funny": "sticker_funny",
    "cute": "sticker_cute", "aww": "sticker_cute", "so sweet": "sticker_cute", "baby": "sticker_cute",
    "anime": "sticker_anime", "manga": "sticker_anime",
    "i hate you": "sticker_anger", "go away": "sticker_anger", "mad": "sticker_anger",
    "love": "sticker_love", "heart": "sticker_love", # Adding love text to potentially trigger a love sticker
}

# -------- Utility Functions --------
def get_reply(text: str):
    """
    Determines the response (text or sticker ID) based on the input text.
    Returns (response, is_sticker)
    """
    if not text:
        # Fall back to daily text
        return (random.choice(DATA.get("daily", ["Hello 👋"])), False)

    text = text.lower()
    
    # Simple normalization: remove non-alphanumeric except spaces for better keyword matching
    text = re.sub(r'[^\w\s]', '', text) 
    
    # Combined reply logic: Check for keyword match first
    matched_category = None
    for word, cat in KEYWORDS.items():
        # Check if keyword is a substring of the message text
        if word in text:
            matched_category = cat
            break # Take the first match
            
    if matched_category:
        cat = matched_category
        is_sticker_category = cat.startswith("sticker_")
        
        # 50/50 chance to send a sticker if it's a sticker category and it exists
        if is_sticker_category and cat in DATA and DATA[cat] and random.random() < 0.5:
            return (random.choice(DATA[cat]), True) 
            
        # If it's a text category, or if the sticker chance failed, send text
        elif cat in DATA and DATA[cat]:
            # For "love", we also include a chance of getting a love sticker text reply
            return (random.choice(DATA[cat]), False)
    
    # 10% chance to send a general/daily reply even if no specific keyword is found (to keep the chat active)
    if random.random() < 0.1:
        return (random.choice(DATA.get("daily", ["Hello 👋"])), False)
        
    # If no specific keyword is found and the random check failed, return None
    return (None, False)


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

# FIX: Added try/except for get_chat_member
async def is_admin(chat_id, user_id):
    """Checks if a user is an admin or owner of the chat."""
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return member.status in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR]
    except Exception:
        return False

# FIX: Added try/except for get_chat_member
async def is_bot_admin(chat_id):
    """Checks if the bot is an admin in the chat."""
    try:
        me = await app.get_me()
        member = await app.get_chat_member(chat_id, me.id)
        return member.status in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR]
    except Exception:
        return False

async def save_chat_id(chat_id, type_):
    """Saves the chat ID to the known chats list."""
    chat_id_str = str(chat_id)
    
    if chat_id_str not in KNOWN_CHATS[type_]:
        KNOWN_CHATS[type_].append(chat_id_str)
        with open(CHAT_IDS_FILE, "w") as f:
            json.dump(KNOWN_CHATS, f, indent=4) # Added indent for readability

# -------- Inline Button Handlers & Menus --------

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
            # FIXED: Support Chat Link
            InlineKeyboardButton("𝐄ᴠᴀʀᴀ 𝐒ᴜᴘᴘᴏʀᴛ 𝐂ʜᴀᴛ", url=SUPPORT_CHAT),
            InlineKeyboardButton("𝐔ᴘᴅᴀᴛᴇs", url=UPDATES_CHANNEL)
        ],
        [
            InlineKeyboardButton("• 𝐁ᴀᴄᴋ", callback_data="start_back"),
            InlineKeyboardButton("• 𝐂ʟᴏsᴇ", callback_data="close")
        ]
    ])

def get_help_main_buttons():
    """Returns the main Help & Commands button layout (Games button removed)."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("ᴄᴏᴜᴘʟᴇ", callback_data="help_couple"),
            InlineKeyboardButton("ᴄʜᴀᴛʙᴏᴛ", callback_data="help_chatbot")
        ],
        [
            InlineKeyboardButton("ᴛᴏᴏʟs", callback_data="help_tools"),
            InlineKeyboardButton("ɢʀᴏᴜᴘ", callback_data="help_group") # Changed position
        ],
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
    
    try:
        if data == "about":
            await query.message.edit_caption(
                caption=ABOUT_TEXT,
                reply_markup=get_about_buttons()
            )
        elif data == "start_back":
            # RE-APPLY SPOILER effect for start photo
            await query.message.edit_caption(
                caption=INTRO_TEXT_TEMPLATE.format(
                    mention_name=f"[{user.first_name}](tg://user?id={user.id})",
                    developer=DEVELOPER_USERNAME,
                ),
                reply_markup=get_start_buttons(me.username),
                parse_mode=enums.ParseMode.MARKDOWN,
                has_spoiler=True
            )
        elif data == "help_main":
            # REMOVE SPOILER effect for help menu
            await query.message.edit_caption(
                caption="📜 𝐂ᴏᴍᴍᴀɴᴅs 𝐌ᴇɴᴜ:\n\n𝐂ʜᴏᴏsᴇ ᴀ ᴄᴀᴛᴇɢᴏʀʏ ʙᴇʟᴏᴡ:",
                reply_markup=get_help_main_buttons(),
                has_spoiler=False
            )
        elif data.startswith("help_"):
            category = data.split("_")[1]
            text = HELP_COMMANDS_TEXT_MAP.get(category, "𝐄ʀʀᴏʀ: 𝐔ɴᴋɴᴏᴡɴ 𝐂ᴀᴛᴇɢᴏʀʏ")
            
            # Custom button logic for sub-menus (always include back and close)
            buttons = []
            # Check if we should add the support button
            if category in ["couple", "cute", "love"]:
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
    except Exception as e:
        print(f"Callback error: {e}")
        await query.answer("An error occurred while processing the request.")

# -------- Handlers for New Group/Channel/Bot Adds --------
@app.on_message(filters.new_chat_members)
async def new_member_handler(client, message):
    me = await client.get_me()
    for user in message.new_chat_members:
        if user.id == me.id:
            # Bot was added to the group
            await message.reply_text("ᴛʜᴀɴᴋs ғᴏʀ ᴀᴅᴅɪɴɢ ᴍᴇ! 💖 𝐂𝐥𝐢𝐜𝐤 /start 𝐟𝐨𝐫 𝐦𝐲 𝐟𝐞𝐚𝐭𝐮𝐫𝐞𝐬.")
            # Ensure the chat is saved as a group
            await save_chat_id(message.chat.id, "groups")

# -------- Commands --------

# -------- /start Command --------
@app.on_message(filters.command("start"))
async def start_cmd(client, message):
    user = message.from_user
    me = await app.get_me()
    
    if message.chat.type == enums.ChatType.PRIVATE:
        # Ding Dong Animation FIX
        anim_text = "ᴅɪɴɢ...ᴅᴏɴɢ 💥....ʙᴏᴛ ɪs sᴛᴀʀᴛɪɴɢ"
        msg = await message.reply_text("Starting...")
        
        current = ""
        for ch in anim_text:
            current += ch
            try:
                # FIX: Edit the message text with a slight delay
                await msg.edit_text(current)
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

# -------- /help Command --------
@app.on_message(filters.command("help"))
async def help_cmd(client, message):
    me = await client.get_me()
    
    # Use the same main help menu for the /help command
    if message.chat.type == enums.ChatType.PRIVATE:
        # Send photo in private chat with main help menu
        await message.reply_photo(
            START_PHOTO, # Using start photo for consistency
            caption="📜 𝐂ᴏᴍᴍᴀɴᴅs 𝐌ᴇɴᴜ:\n\n𝐂ʜᴏᴏsᴇ ᴀ ᴄᴀᴛᴇɢᴏʀʏ ʙᴇʟᴏᴡ:",
            reply_markup=get_help_main_buttons(),
            has_spoiler=False
        )
        await save_chat_id(message.chat.id, "privates")
    else:
        # Group chat: send a simple text message with the button
        await message.reply_text(
            "📜 𝐂ᴏᴍᴍᴀɴᴅs 𝐌ᴇɴᴜ:\n\n𝐂ʟɪᴄᴋ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ᴠɪᴇᴡ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("◉ 𝐇ᴇʟᴘ & 𝐂ᴏᴍᴍᴀɴᴅs", callback_data="help_main")]
            ])
        )
        await save_chat_id(message.chat.id, "groups")

# -------- /developer Command --------
@app.on_message(filters.command("developer"))
async def developer_cmd(client, message):
    # Animation FIX
    anim_text = "𝐘ᴏᴜ 𝐖ᴀɳᴛ ᴛᴏ 𝐊ɳᴏᴡ..𝐓ʜɪs 𝐁ᴏᴛ 𝐃ᴇᴠᴇʟᴏᴘᴇʀ 💥..𝐇ᴇʀᴇ"
    m = await message.reply_text("Searching...")
    
    current = ""
    for ch in anim_text:
        current += ch
        try:
            await m.edit_text(current) # FIX: Use edit_text
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
        # Send photo response with SPOILER
        await message.reply_photo(
            DEVELOPER_PHOTO,
            caption=caption_text,
            reply_markup=buttons,
            parse_mode=enums.ParseMode.MARKDOWN,
            has_spoiler=True # Apply spoiler effect to the developer photo
        )
    except Exception as e:
        # Fallback to text message if photo sending fails
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
    
    # Ping animation FIX
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
        caption=f"𝐏ɪɴɢ ➳ **{ping_ms}** 𝐦𝐬\n" # Added bold
              f"𝐔ᴘᴛɪᴍᴇ ➳ **{uptime_readable}**", # Added bold
        reply_markup=buttons,
        parse_mode=enums.ParseMode.MARKDOWN
    ) 

# -------- /id Command (FIXED) --------
@app.on_message(filters.command("id"))
async def id_cmd(client, message):
    # Check if replied message exists, otherwise use the sender
    if message.reply_to_message:
        user = message.reply_to_message.from_user
    elif len(message.command) > 1 and message.command[1].startswith('@'):
        # Try to resolve username if provided
        try:
            user = await app.get_users(message.command[1])
        except:
            user = message.from_user # Fallback
    else:
        user = message.from_user
        
    if user:
        await message.reply_text(f"👤 **{user.first_name}**\n🆔 `{user.id}`", parse_mode=enums.ParseMode.MARKDOWN)

# -------- /stats Command (Owner Only) --------
@app.on_message(filters.command("stats") & filters.user(OWNER_ID))
async def stats_cmd(client, message):
    await message.reply_text(f"📊 𝐁ᴏᴛ 𝐒ᴛᴀᴛs:\n👥 𝐆ʀᴏᴜᴘs: **{len(KNOWN_CHATS['groups'])}**\n👤 𝐏ʀɪᴠᴀᴛᴇs: **{len(KNOWN_CHATS['privates'])}**", parse_mode=enums.ParseMode.MARKDOWN)

# -------- /broadcast (Owner Only) --------
@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast_cmd(client, message):
    if not (message.reply_to_message or len(message.command) > 1):
        return await message.reply_text("ᴜsᴀɢᴇ:\n`/broadcast <text>`\nᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴡɪᴛʜ `/broadcast`.", parse_mode=enums.ParseMode.MARKDOWN)
    
    # Extract content to broadcast
    content_to_send = message.reply_to_message
    text = None
    if not content_to_send and len(message.command) > 1:
        text = message.text.split(None, 1)[1]
    
    if not content_to_send and not text:
        return # Should be redundant, but keeps logic clean

    sent = 0
    failed = 0
    m = await message.reply_text("𝐒ᴛᴀʀᴛɪɴɢ 𝐁ʀᴏᴀᴅᴄᴀsᴛ...")
    
    for chat_type in ["privates", "groups"]:
        for chat_id_str in KNOWN_CHATS[chat_type]:
            try:
                chat_id = int(chat_id_str) 
            except ValueError:
                continue 
                
            try:
                if content_to_send:
                    await app.copy_message(chat_id, message.chat.id, content_to_send.id)
                elif text:
                    await app.send_message(chat_id, text)
                sent += 1
            except Exception:
                # Bot blocked, chat left, etc.
                failed += 1
                continue 
                
    await m.edit_text(f"✅ 𝐁ʀᴏᴀᴅᴄᴀsᴛ ᴅᴏɴᴇ!\n𝐒ᴇɴᴛ ᴛᴏ **{sent}** ᴄʜᴀᴛs.\n𝐅ᴀɪʟᴇᴅ ɪɴ **{failed}** ᴄʜᴀᴛs.", parse_mode=enums.ParseMode.MARKDOWN)


# -------- /chatbot Toggle (FIXED) --------
@app.on_message(filters.command("chatbot") & filters.group)
async def chatbot_toggle_cmd(client, message):
    # Check for admin
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply_text("❗ Oɴʟʏ ᴀᴅᴍɪɴs ᴀɴᴅ ᴏᴡɴᴇʀ ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")
    
    if len(message.command) < 2:
        # Show current status if no argument given
        current_status = "𝐄𝐍𝐀𝐁𝐋𝐄𝐃" if CHATBOT_STATUS.get(message.chat.id, False) else "𝐃𝐈𝐒𝐀𝐁𝐋𝐄𝐃"
        return await message.reply_text(f"𝐂ʜᴀᴛʙᴏᴛ ɪs ᴄᴜʀʀᴇɴᴛʟʏ **{current_status}** ✰\n𝐔sᴀɢᴇ: /ᴄʜᴀᴛʙᴏᴛ ᴇɴᴀʙʟᴇ ᴏʀ /ᴄʜᴀᴛʙᴏᴛ ᴅɪsᴀʙʟᴇ", parse_mode=enums.ParseMode.MARKDOWN)
        
    mode = message.command[1].lower()
    
    if mode in ["on", "enable"]:
        CHATBOT_STATUS[message.chat.id] = True
        status_text = "enabled"
        await message.reply_text(f"𝐂ʜᴀᴛʙᴏᴛ sᴛᴀᴛᴜs ɪs **{status_text.upper()}** ✰", parse_mode=enums.ParseMode.MARKDOWN)
    elif mode in ["off", "disable"]:
        CHATBOT_STATUS[message.chat.id] = False
        status_text = "disabled"
        await message.reply_text(f"𝐂ʜᴀᴛʙᴏᴛ sᴛᴀᴛᴜs ɪs **{status_text.upper()}** ✰", parse_mode=enums.ParseMode.MARKDOWN)
    else:
        return await message.reply_text("𝐔sᴀɢᴇ: /ᴄʜᴀᴛʙᴏᴛ ᴇɴᴀʙʟᴇ ᴏʀ /ᴄʜᴀᴛʙᴏᴛ ᴅɪsᴀʙʟᴇ")
        
    await save_chat_id(message.chat.id, "groups") 

# -------- /tagall Command (FIXED) --------
@app.on_message(filters.command("tagall") & filters.group)
async def tagall_cmd(client, message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply_text("❗ 𝐎ɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ /ᴛᴀɢᴀʟʟ.")
    
    if not await is_bot_admin(message.chat.id):
        return await message.reply_text("❗ 𝐈 ɴᴇᴇᴅ **ᴀᴅᴍɪɴ ᴘᴇʀᴍɪssɪᴏɴ** (ᴛᴀɢ ᴍᴇᴍʙᴇʀs/ᴍᴇɴᴛɪᴏɴ ᴇᴠᴇʀʏᴏɴᴇ) ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.", parse_mode=enums.ParseMode.MARKDOWN)

    chat_id = message.chat.id
    
    if TAGGING.get(chat_id):
        return await message.reply_text("❗ 𝐀ʟʀᴇᴀᴅʏ ᴛᴀɢɢɪɴɢ ɪɴ ᴛʜɪs ᴄʜᴀᴛ. 𝐔sᴇ /sᴛᴏᴘ ᴛᴏ ᴄᴀɴᴄᴇʟ.")
        
    TAGGING[chat_id] = True
    
    # Get message content
    if len(message.command) > 1:
        msg = message.text.split(None, 1)[1]
    elif message.reply_to_message and (message.reply_to_message.text or message.reply_to_message.caption):
        # Use the replied message text or caption
        text = message.reply_to_message.text or message.reply_to_message.caption
        msg = f"{text[:50]}{'...' if len(text) > 50 else ''}" 
    else:
        msg = "𝐀ᴛᴛᴇɴᴛɪᴏɴ!"
        
    m = await message.reply_text("𝐓ᴀɢɢɪɴɢ 𝐒ᴛᴀʀᴛᴇᴅ !! ♥")
    
    member_list = []
    # Collect all members first
    try:
        # Filter out bots and deleted accounts
        async for member in app.get_chat_members(message.chat.id):
            if not (member.user.is_bot or member.user.is_deleted):
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
        
    if TAGGING.get(message.chat.id):
        TAGGING[message.chat.id] = False
        await message.reply_text("𝐓ᴀɢɢɪɴɢ 𝐒ᴛᴏᴘᴘᴇᴅ !!")
    else:
        await message.reply_text("❗ 𝐍ᴏ 𝐓ᴀɢɢɪɴɢ ɪs 𝐂ᴜʀʀᴇɴᴛ𝐥𝐲 𝐑ᴜ𝐍𝐍ɪɴɢ.")

# -------- NEW FEATURE: /staff Command (COMPLETED) --------
@app.on_message(filters.command("staff") & filters.group)
async def staff_cmd(client, message):
    owner = []
    admins = []
    
    try:
        async for member in app.get_chat_members(message.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
            if member.user.is_bot:
                continue # Skip bots
            
            user_mention = f"[{member.user.first_name}](tg://user?id={member.user.id})"
            
            if member.status == enums.ChatMemberStatus.OWNER:
                owner.append(user_mention)
            elif member.status == enums.ChatMemberStatus.ADMINISTRATOR:
                admins.append(user_mention)
    except Exception:
        return await message.reply_text("🚫 𝐂𝐚𝐧𝐧𝐨𝐭 𝐟𝐞𝐭𝐜𝐡 𝐬𝐭𝐚𝐟𝐟 𝐝𝐮𝐞 𝐭𝐨 𝐫𝐞𝐬𝐭𝐫𝐢𝐜𝐭𝐢𝐨𝐧𝐬.")

    if not owner and not admins:
        return await message.reply_text("❗ 𝐍ᴏ 𝐚𝐝𝐦𝐢𝐧𝐬 𝐟𝐨𝐮𝐧𝐝 𝐢𝐧 𝐭𝐡𝐢𝐬 𝐠𝐫𝐨𝐮𝐩.")

    staff_message = "👑 𝐆𝐫𝐨𝐮𝐩 𝐒𝐭𝐚𝐟𝐟 𝐋𝐢𝐬𝐭 👑\n\n"
    
    if owner:
        staff_message += "✨ **𝐎ᴡɴᴇʀ(s):**\n"
        staff_message += "\n".join([f"  • {o}" for o in owner]) + "\n\n"
        
    if admins:
        staff_message += "🌟 **𝐀ᴅᴍɪɴ(s):**\n"
        staff_message += "\n".join([f"  • {a}" for a in admins])
        
    await message.reply_text(staff_message, parse_mode=enums.ParseMode.MARKDOWN)

# -------- NEW FEATURE: /botlist Command (COMPLETED) --------
@app.on_message(filters.command("botlist") & filters.group)
async def botlist_cmd(client, message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply_text("❗ 𝐎ɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ /ʙᴏᴛʟɪsᴛ.")

    bots = []
    try:
        async for member in app.get_chat_members(message.chat.id):
            if member.user.is_bot:
                # Add bot name and mention/username
                bot_info = f"[{member.user.first_name}](tg://user?id={member.user.id})"
                if member.user.username:
                    bot_info += f" @{member.user.username}"
                bots.append(bot_info)
    except Exception:
        return await message.reply_text("🚫 𝐂𝐚𝐧𝐧𝐨𝐭 𝐟𝐞𝐭𝐜𝐡 𝐦𝐞𝐦𝐛𝐞𝐫𝐬 𝐝𝐮𝐞 𝐭𝐨 𝐫𝐞𝐬𝐭𝐫𝐢𝐜𝐭𝐢𝐨𝐧s.")
        
    if not bots:
        return await message.reply_text("✅ 𝐍𝐨 𝐛𝐨𝐭𝐬 𝐟𝐨𝐮𝐧𝐝 𝐢𝐧 𝐭𝐡𝐢𝐬 𝐠𝐫𝐨𝐮𝐩.")

    bot_message = f"🤖 **{len(bots)} 𝐁𝐨𝐭𝐬 𝐅𝐨𝐮𝐧𝐝:**\n\n"
    bot_message += "\n".join([f"  • {b}" for b in bots])
    
    await message.reply_text(bot_message, parse_mode=enums.ParseMode.MARKDOWN)


# -------- /couples, /cute, /love Commands (FIXED) --------
@app.on_message(filters.command("couples") & filters.group)
async def couples_cmd(client, message):
    member_list = []
    try:
        # Use only USERS in the group, excluding bots and deleted accounts
        async for member in app.get_chat_members(message.chat.id):
            if not (member.user.is_bot or member.user.is_deleted):
                member_list.append(member.user)
    except Exception:
        return await message.reply_text("🚫 𝐂𝐚𝐧𝐧𝐨𝐭 𝐟𝐞𝐭𝐜𝐡 𝐦𝐞𝐦𝐛𝐞𝐫s 𝐝𝐮𝐞 𝐭𝐨 𝐫𝐞𝐬𝐭𝐫𝐢𝐜𝐭𝐢𝐨𝐧s.")

    if len(member_list) < 2:
        return await message.reply_text("❗ 𝐍ᴇᴇᴅ 𝐚𝐭 𝐥𝐞𝐚𝐬𝐭 𝐭𝐰𝐨 𝐦𝐞𝐦𝐛𝐞𝐫𝐬 𝐭𝐨 𝐟𝐨𝐫𝐦 𝐚 𝐂ᴏᴜ𝐩𝐥ᴇ.")
        
    # Pick two random unique members
    couple = random.sample(member_list, 2)
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
    # FIX: Ensure user mention works and parse_mode is set
    user_mention = f"[{user.first_name}](tg://user?id={user.id})"
    text = f"{user_mention}’𝐬 ᴄᴜᴛᴇɴᴇss ʟᴇᴠᴇʟ ɪs **{cute_level}%** 💖"
    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("𝐒ᴜᴘᴘᴏʀᴛ", url=SUPPORT_CHAT)]])
    await message.reply_text(text, reply_markup=buttons, parse_mode=enums.ParseMode.MARKDOWN) # FIXED the reply line

@app.on_message(filters.command("love"))
async def love_cmd(client, message):
    if len(message.command) < 2 or "+" not in message.text:
        return await message.reply_text("𝐔sᴀɢᴇ: /ʟᴏᴠᴇ 𝐅ɪʀsᴛ 𝐍ᴀᴍᴇ + 𝐒ᴇᴄᴏɴᴅ 𝐍ᴀᴍᴇ")

    # Split the command text, remove the command itself, then split by '+'
    text_parts = message.text.split(None, 1)
    if len(text_parts) < 2:
        return await message.reply_text("𝐔sᴀɢᴇ: /ʟᴏᴠᴇ 𝐅ɪʀsᴛ 𝐍ᴀᴍᴇ + 𝐒ᴇᴄᴏɴᴅ 𝐍ᴀᴍᴇ")

    names = [n.strip() for n in text_parts[1].split('+')]
    
    if len(names) < 2 or not all(names): # Check if both names are non-empty
        return await message.reply_text("𝐏ʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ 𝐭𝐰𝐨 ɴᴀᴍᴇs sᴇᴘʀᴀᴛᴇᴅ ʙʏ ᴀ '+' (ᴇ.ɢ., /ʟᴏᴠᴇ 𝐀ʟɪᴄᴇ + 𝐁ᴏʙ)")
        
    # FIX: Ensure love_percent calculation is done
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
            f"𝐘ᴇᴀʜ, [{user_name}](tg://user?id={user_id}), ʏᴏᴜ 𝐚𝐫𝐞 ʙᴀᴄᴋ, ᴏɴʟɪɴᴇ! (𝐀ғᴋ ғᴏʀ: **{time_afk}**) 😉",
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

# -------- AFK Trigger Handler (COMPLETED) --------
@app.on_message(filters.group & ~filters.command(["afk"]) & ~filters.bot)
async def afk_trigger_handler(client, message):
    user_id = message.from_user.id
    
    # 1. Check if the message sender is returning from AFK
    if user_id in AFK_USERS:
        # If the message is not /afk (which is filtered out anyway, but good to double check)
        afk_data = AFK_USERS.pop(user_id)
        time_afk = get_readable_time(int(time.time() - afk_data["time"]))
        
        # Announce return
        await message.reply_text(
            f"𝐖ᴇʟᴄᴏᴍᴇ ʙᴀᴄᴋ, [{message.from_user.first_name}](tg://user?id={user_id})! ʏᴏᴜ 𝐰𝐞𝐫𝐞 𝐀ғᴋ ғᴏʀ: **{time_afk}**",
            parse_mode=enums.ParseMode.MARKDOWN
        )
        # Do NOT return here, as the user might be returning *and* mentioning another AFK user

    # 2. Check for AFK users mentioned in the message or reply
    mentions_to_check = set()

    # Check reply-to user
    if message.reply_to_message and message.reply_to_message.from_user:
        mentions_to_check.add(message.reply_to_message.from_user.id)
    
    # Check for text mentions (entities)
    if message.entities and message.text:
        for entity in message.entities:
            # Check for user mentions via ID (tg://user?id=...)
            if entity.type == enums.MessageEntityType.TEXT_MENTION and entity.user:
                mentions_to_check.add(entity.user.id)
            # Check for @username mentions and try to resolve them (only if they are in the message text itself)
            elif entity.type == enums.MessageEntityType.MENTION:
                 # Extract username from text
                 username = message.text[entity.offset:entity.offset + entity.length]
                 try:
                     user_obj = await app.get_users(username)
                     mentions_to_check.add(user_obj.id)
                 except:
                     pass # Cannot resolve username

    for afk_user_id in mentions_to_check:
        if afk_user_id in AFK_USERS and afk_user_id != user_id: # Ensure we don't reply to the user who just returned
            afk_data = AFK_USERS[afk_user_id]
            time_afk = get_readable_time(int(time.time() - afk_data["time"]))
            
            await message.reply_text(
                f"[{afk_data['first_name']}](tg://user?id={afk_user_id}) 𝐢𝐬 𝐀ғᴋ!\n"
                f"☞ 𝐑ᴇᴀsᴏɴ: **{afk_data['reason']}**\n"
                f"☞ 𝐓𝐢𝐦𝐞: **{time_afk}** 𝐚𝐠𝐨",
                parse_mode=enums.ParseMode.MARKDOWN
            )

# -------- Chatbot Reply Handler (FIXED LOGIC) --------
@app.on_message(filters.text & ~filters.private & ~filters.command(["start", "help", "developer", "ping", "id", "stats", "broadcast", "chatbot", "tagall", "stop", "afk", "couples", "cute", "love", "staff", "botlist"]) & ~filters.bot)
async def group_chatbot_handler(client, message: Message):
    chat_id = message.chat.id
    
    # Check if chatbot is enabled for this group
    if not CHATBOT_STATUS.get(chat_id, False):
        return

    # Determine if the bot was mentioned, replied to, or should reply randomly
    mentioned = False
    replied_to_me = False
    should_reply_randomly = False
    me = await client.get_me()

    if message.reply_to_message and message.reply_to_message.from_user and message.reply_to_message.from_user.id == me.id:
        replied_to_me = True
    
    if message.text and f"@{me.username.lower()}" in message.text.lower():
        mentioned = True
    
    # Logic:
    # 1. Always reply if mentioned or replied to.
    if mentioned or replied_to_me:
        reply_chance = 1.0 # 100% chance to reply
        text_to_analyze = message.text or message.caption or ""
    # 2. Randomly reply if not mentioned/replied (e.g., 5% chance)
    elif random.random() < 0.05:
        reply_chance = 1.0 # The initial random check already passed
        should_reply_randomly = True
        text_to_analyze = message.text or message.caption or ""
    else:
        return # Do not reply

    # Get the reply
    response, is_sticker = get_reply(text_to_analyze)

    if response:
        try:
            if is_sticker:
                await message.reply_sticker(response)
            else:
                await message.reply_text(response)
        except Exception as e:
            print(f"Chatbot reply failed: {e}")

# -------- Private Chat Reply Handler (FIXED) --------
@app.on_message(filters.text & filters.private & ~filters.command(["start", "help", "developer", "ping", "id", "stats", "broadcast", "chatbot", "tagall", "stop", "afk", "couples", "cute", "love", "staff", "botlist"]) & ~filters.bot)
async def private_chatbot_handler(client, message: Message):
    # In private chat, always reply (100% chance)
    text_to_analyze = message.text or message.caption or ""
    
    # Get the reply
    response, is_sticker = get_reply(text_to_analyze)

    if response:
        try:
            if is_sticker:
                await message.reply_sticker(response)
            else:
                await message.reply_text(response)
        except Exception as e:
            print(f"Private chat reply failed: {e}")


# -------- Bot Run --------
if __name__ == "__main__":
    print("Bot is starting...")
    app.run()
