# -*- coding: utf-8 -*-
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
# The pyrogram.errors import is necessary for catching exceptions during broadcast
from pyrogram.errors import FloodWait, UserNotParticipant, ChatWriteForbidden, PeerIdInvalid, RPCError
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
# Owner ID is crucial for owner-only commands (stats, broadcast)
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
# {user_id: {"reason": str, "chat_id": int, "username": str, "first_name": str, "time": float}}
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
    "group": (
        "📜 𝐆ʀᴏᴜᴘ 𝐔ᴛɪʟɪᴛʏ 𝐂ᴏᴍᴍᴧɴᴅs:\n"
        "/staff ~ 𝐃ɪsᴘʟᴧʏs ɢʀᴏᴜᴘ sᴛᴧғғ ᴍᴇᴍʙᴇʀs\n"
        "/botlist ~ 𝐂ʜᴇᴄᴋ ʜᴏᴡ ᴍᴀɴʏ ʙᴏᴛs ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ (𝐀ᴅᴍɪɴ ᴏɴʟʏ)\n"
        "/chatbot ~ 𝐄ɴᴀʙʟᴇ/ᴅɪsᴀʙʟᴇ ᴄʜᴀᴛʙᴏᴛ (𝐀ᴅᴍɪɴ ᴏɴʟʏ)\n"
        "\n_ʙᴏᴛʟɪsᴛ/ᴄʜᴀᴛʙᴏᴛ ʀᴇǫᴜɪʀᴇs ᴀᴅᴍɪɴ. ᴏᴛʜᴇʀs ᴀʀᴇ ғᴏʀ ᴇᴠᴇʀʏᴏɴᴇ."
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
try:
    with open("conversation.json", "r", encoding="utf-8") as f:
        DATA = json.load(f)
except:
    # If the JSON file is missing, use a minimal default structure with the new sticker IDs
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

if "daily" not in DATA:
    DATA["daily"] = ["Hello 👋", "Hey there!", "Hi!"]


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
    "hello": "daily", "hi": "daily", "hey": "daily", "yaar": "daily", "kya haal": "daily", "bhai": "daily",
    "bye": "bye", "goodbye": "bye", "see ya": "bye", "tata": "bye",
    "thanks": "thanks", "thank you": "thanks", "tysm": "thanks",
    "gm": "morning", "good morning": "morning", "subah": "morning",
    "gn": "night", "good night": "night", "shubh ratri": "night", "sleep": "night",
    "chutiya": "abuse", "bc": "abuse", "mc": "abuse", "pagal": "abuse", "idiot": "abuse",
    "kaisa hai": "question", "kya kar raha": "question", "who are you": "question", "bot": "question",
    "gussa": "anger", "angry": "anger", "gali": "anger",

    # Sticker Replies (New Categories)
    "hahaha": "sticker_funny", "lol": "sticker_funny", "rofl": "sticker_funny", "funny": "sticker_funny",
    "cute": "sticker_cute", "aww": "sticker_cute", "so sweet": "sticker_cute", "baby": "sticker_cute",
    "anime": "sticker_anime", "manga": "sticker_anime",
    "i hate you": "sticker_anger", "go away": "sticker_anger", "mad": "sticker_anger",
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
    
    for word, cat in KEYWORDS.items():
        # Check if keyword is a substring of the message text
        if word in text:
            if cat.startswith("sticker_") and cat in DATA and DATA[cat]:
                # Returns a random sticker ID from the category (is_sticker=True)
                sticker_id = random.choice(DATA[cat])
                return (sticker_id, True) 
            elif cat in DATA and DATA[cat]:
                # Returns a random text reply (is_sticker=False)
                return (random.choice(DATA[cat]), False)
    
    # If no specific keyword is found, return None to indicate a general reply should not be sent
    # This logic is shifted to the main message handler to implement the 80% rule for general chat.
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

async def is_admin(chat_id, user_id):
    """Checks if a user is an admin or owner of the chat."""
    # Check if the user is the bot owner first (global admin)
    if user_id == OWNER_ID:
        return True
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
        return member.status in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR]
    except Exception:
        return False

async def save_chat_id(chat_id, type_):
    """Saves the chat ID to the known chats list."""
    chat_id_str = str(chat_id)
    
    if chat_id_str not in KNOWN_CHATS[type_]:
        KNOWN_CHATS[type_].append(chat_id_str)
        # Write to file asynchronously in an ideal scenario, but synchronous for simplicity here
        with open(CHAT_IDS_FILE, "w") as f:
            json.dump(KNOWN_CHATS, f)

# Custom filter for checking chatbot status
def is_chatbot_enabled(_, __, message: Message):
    """Returns True if chatbot is enabled for this group."""
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        # Default is False, so only True if explicitly set to True
        return CHATBOT_STATUS.get(message.chat.id, False)
    return False # Chatbot should run in private chats via the main handler

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
            InlineKeyboardButton("ɢʀᴏᴜᴘ", callback_data="help_group") # Replaced 'games' with 'group' in this row
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
    
    # Simple check for the user who initiated the command in groups
    if query.message.chat.type != enums.ChatType.PRIVATE:
        try:
            # Check if the user is the one who pressed the button (optional security)
            # You might want to remove this if you want anyone to press the menu buttons.
            # if query.message.reply_to_message and query.from_user.id != query.message.reply_to_message.from_user.id:
            #     return await query.answer("This menu is not for you.", show_alert=True)
            pass
        except Exception:
            pass # Ignore if no reply to message

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
            parse_mode=enums.ParseMode.MARKDOWN
        )
    elif data == "help_main":
        await query.message.edit_caption(
            caption="📜 𝐂ᴏᴍᴍᴀɴᴅs 𝐌ᴇɴᴜ:\n\n𝐂ʜᴏᴏsᴇ ᴀ ᴄᴀᴛᴇɢᴏʀʏ ʙᴇʟᴏᴡ:",
            reply_markup=get_help_main_buttons()
        )
    elif data.startswith("help_"):
        category = data.split("_")[1]
        text = HELP_COMMANDS_TEXT_MAP.get(category, "𝐄ʀʀᴏʀ: 𝐔ɴᴋɴᴏᴡɴ 𝐂ᴀᴛᴇɢᴏʀʏ")
        
        # Custom button logic for sub-menus
        buttons = []
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
            reply_markup=InlineKeyboardMarkup(buttons_markup_rows)
        )
    elif data == "close":
        await query.message.delete()
    else:
        await query.answer("𝐓ʜɪs ʙᴜᴛᴛᴏɴ ɪs ɴᴏᴛ ʏᴇᴛ 𝐅ᴜɴᴄᴛɪ𝐎N𝐀𝐋.") 

# -------- Commands --------

# -------- New Member Welcome Handler (FIXED & ADDED) --------
@app.on_message(filters.new_chat_members & filters.group)
async def welcome_new_member(client, message):
    me = await client.get_me()
    for user in message.new_chat_members:
        if user.id == me.id:
            # Bot was added to the group
            await message.reply_text("𝐓ʜᴀɴᴋs ғᴏʀ ᴀᴅᴅɪɴɢ ᴍᴇ !! 💖\n\n𝐈 ᴀᴍ ᴀɴ ᴀᴅᴠᴀɴᴄᴇᴅ ᴄʜᴀᴛʙᴏᴛ. 𝐔sᴇ /help ᴛᴏ ɢᴇᴛ sᴛᴀʀᴛᴇᴅ.\n\n_𝐍𝐎𝐓𝐄: 𝐏𝐥𝐞𝐚𝐬𝐞 𝐦𝐚𝐤𝐞 𝐦𝐞 𝐀𝐃𝐌𝐈𝐍 𝐟𝐨𝐫 𝐟𝐮𝐥𝐥 𝐟𝐮𝐧𝐜𝐭𝐢𝐨𝐧𝐚𝐥𝐢𝐭𝐲._")
            await save_chat_id(message.chat.id, "groups")
            # Default to chatbot disabled
            CHATBOT_STATUS[message.chat.id] = False 
            break
        else:
            # A user was added
            mention = f"[{user.first_name}](tg://user?id={user.id})"
            await message.reply_text(f"👋 𝐖ᴇʟᴄᴏᴍᴇ {mention} ᴛᴏ ᴛʜᴇ ɢʀᴏᴜᴘ! 𝐄ɴᴊᴏʏ ʏᴏᴜʀ sᴛᴀʏ.")
    
# -------- /start Command --------
# Combined start handler for both private and groups
@app.on_message(filters.command("start"))
async def start_cmd(client, message):
    user = message.from_user
    me = await app.get_me()
    
    if message.chat.type == enums.ChatType.PRIVATE:
        # Ding Dong Animation
        anim_text = "ᴅɪɴɢ...ᴅᴏɴɢ 💥....ʙᴏᴛ ɪs sᴛᴀʀᴛɪɴɢ"
        msg = await message.reply_text("Starting...")
        
        current = ""
        for ch in anim_text:
            current += ch
            try:
                await msg.edit(current)
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
            has_spoiler=True # Added spoiler effect
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
    
    current = ""
    for ch in anim_text:
        current += ch
        try:
            await m.edit(current)
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
    # Get the user to check ID for: replied user or message sender
    user = message.reply_to_message.from_user if message.reply_to_message and message.reply_to_message.from_user else message.from_user 
    await message.reply_text(f"👤 {user.first_name}\n🆔 {user.id}")

# -------- /stats Command (Owner Only) --------
@app.on_message(filters.command("stats") & filters.user(OWNER_ID))
async def stats_cmd(client, message):
    await message.reply_text(f"📊 𝐁ᴏᴛ 𝐒ᴛᴀᴛs:\n👥 𝐆ʀᴏᴜᴘs: {len(KNOWN_CHATS['groups'])}\n👤 𝐏ʀɪᴠᴀᴛᴇs: {len(KNOWN_CHATS['privates'])}")

# -------- /broadcast (Owner Only) --------
@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast_cmd(client, message):
    if not (message.reply_to_message or len(message.command) > 1):
        return await message.reply_text("ᴜsᴀɢᴇ: /ʙʀᴏᴀᴅᴄᴀsᴛ ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ.")
    
    # Extract content to broadcast
    content_to_send = None
    text = None
    if message.reply_to_message:
        content_to_send = message.reply_to_message
    elif len(message.command) > 1:
        text = message.text.split(None, 1)[1]
    else:
        return # Should be caught by the first check, but for safety

    sent = 0
    failed = 0
    m = await message.reply_text("𝐒ᴛᴀʀᴛɪɴɢ 𝐁ʀᴏᴀᴅᴄᴀsᴛ...")
    
    # Iterate over a combined list of chat IDs
    for chat_id_str in KNOWN_CHATS["privates"] + KNOWN_CHATS["groups"]:
        try:
            chat_id = int(chat_id_str) 
            
            if content_to_send:
                # Use client.copy_message for reliable forwarding/copying
                await client.copy_message(chat_id, message.chat.id, content_to_send.id)
            elif text:
                await app.send_message(chat_id, text)
            
            sent += 1
            # Simple rate limiting for large broadcasts
            await asyncio.sleep(0.2) 
        except (FloodWait, UserNotParticipant, ChatWriteForbidden, PeerIdInvalid, RPCError):
            # Log specific Pyrogram errors that often happen during broadcast
            failed += 1
            continue
        except Exception:
            # Catch other potential errors
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

# -------- /tagall Command (FIXED) --------
@app.on_message(filters.command("tagall") & filters.group)
async def tagall_cmd(client, message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply_text("❗ 𝐎ɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ /ᴛᴀɢᴀʟʟ.")
    
    if not await is_bot_admin(message.chat.id):
        return await message.reply_text("❗ 𝐈 ɴᴇᴇᴅ ᴀᴅᴍɪɴ ᴘᴇʀᴍɪssɪᴏɴ (ᴛᴀɢ ᴍᴇᴍʙᴇʀs) ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")

    chat_id = message.chat.id # FIX: Correctly get chat_id
    
    if TAGGING.get(chat_id): # FIX: Check for current tagging status
        return await message.reply_text("❗ 𝐀ʟʀᴇᴀᴅʏ ᴛᴀɢɢɪɴɢ ɪɴ ᴛʜɪs ᴄʜᴀᴛ. 𝐔sᴇ /sᴛᴏᴘ ᴛᴏ ᴄᴀɴᴄᴇʟ.")
        
    TAGGING[chat_id] = True
    
    # Get message content
    if len(message.command) > 1:
        msg = message.text.split(None, 1)[1]
    elif message.reply_to_message and message.reply_to_message.text:
        msg = f"{message.reply_to_message.text[:50]}{'...' if len(message.reply_to_message.text) > 50 else ''}" # Preview of replied message text
    else:
        msg = "𝐀ᴛᴛᴇɴᴛɪᴏɴ!"
        
    m = await message.reply_text("𝐓ᴀɢɢɪɴɢ 𝐒ᴛᴀʀᴛᴇᴅ !! ♥")
    
    member_list = []
    # Collect all members first
    try:
        # Use get_chat_members(limit=0) to get all members efficiently
        async for member in app.get_chat_members(chat_id, limit=0):
            if not (member.user.is_bot or member.user.is_deleted):
                member_list.append(member.user)
    except Exception:
        TAGGING[chat_id] = False
        return await m.edit_text("🚫 𝐄𝐫𝐫𝐨𝐫 𝐢𝐧 𝐟𝐞𝐭𝐜𝐡𝐢𝐧𝐠 𝐦𝐞𝐦𝐛𝐞𝐫s: 𝐌𝐚𝐲𝐛𝐞 𝐭𝐡𝐢s 𝐠𝐫𝐨𝐮𝐩 𝐢s 𝐭𝐨𝐨 𝐛𝐢𝐠 𝐨𝐫 𝐈 𝐝𝐨𝐧't 𝐡𝐚𝐯𝐞 𝐩𝐞𝐫𝐦𝐢𝐬𝐬𝐢𝐨𝐧s.")

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
            # Send the tag chunk
            await app.send_message(chat_id, tag_text, disable_web_page_preview=True, parse_mode=enums.ParseMode.MARKDOWN)
            await asyncio.sleep(2) # Delay to avoid flooding limits
        except:
            continue
            
    # Final message update
    if TAGGING.get(chat_id):
        await m.edit_text("𝐓ᴀɢɢɪɴɢ 𝐂ᴏᴍᴘʟᴇᴛᴇᴅ !! ◉‿◉")
        TAGGING[chat_id] = False 

# -------- /stop Tagging --------
@app.on_message(filters.command("stop") & filters.group)
async def stop_tag(client, message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply_text("❗ 𝐎ɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ /sᴛᴏᴘ.")
        
    if TAGGING.get(message.chat.id):
        TAGGING[message.chat.id] = False
        await message.reply_text("𝐓ᴀɢɢɪɴɢ 𝐒ᴛᴏᴘᴘᴇᴅ !!")
    else:
        await message.reply_text("❗ 𝐍ᴏ 𝐓ᴀɢɢɪɴɢ ɪs 𝐂ᴜʀʀᴇɴᴛ𝐥𝐲 𝐑ᴜ𝐍𝐍ɪɴɢ.")

# -------- /couples, /cute, /love Commands (FIXED) --------
@app.on_message(filters.command("couples") & filters.group) # FIX: Added the decorator
async def couples_cmd(client, message):
    member_list = []
    try:
        # Use only USERS in the group, excluding bots and deleted accounts
        async for member in app.get_chat_members(message.chat.id, limit=0):
            if not (member.user.is_bot or member.user.is_deleted):
                member_list.append(member.user)
    except Exception:
        return await message.reply_text("🚫 𝐂𝐚𝐧𝐧𝐨𝐭 𝐟𝐞𝐭𝐜𝐡 𝐦𝐞𝐦𝐛𝐞𝐫s 𝐝𝐮𝐞 𝐭𝐨 𝐫𝐞𝐬𝐭𝐫𝐢𝐜𝐭𝐢𝐨𝐧s.")

    if len(member_list) < 2:
        return await message.reply_text("❗ 𝐍ᴇᴇᴅ ᴀᴛ ʟᴇᴀsᴛ ᴛᴡᴏ ᴍᴇᴍʙᴇʀs ᴛᴏ ғᴏʀᴍ ᴀ 𝐂ᴏᴜᴘ𝐥ᴇ.")
        
    # Pick two random unique members
    couple = random.sample(member_list, 2)
    user1 = couple[0]
    user2 = couple[1]
    
    # Calculate a random love percentage (just for fun)
    love_percent = random.randint(30, 99)
    
    await message.reply_text(
        f"💘 𝐍ᴇᴡ 𝐂ᴏᴜᴘ𝐥ᴇ ᴏғ ᴛʜᴇ 𝐃ᴀʏ!\n\n"
        f"[{user1.first_name}](tg://user?id={user1.id}) 💖 [{user2.first_name}](tg://user?id={user2.id})\n"
        f"𝐋ᴏᴠᴇ ʟᴇᴠᴇʟ ɪs {love_percent}%! 🎉",
        parse_mode=enums.ParseMode.MARKDOWN
    )

@app.on_message(filters.command("cute"))
async def cute_cmd(client, message): 
    cute_level = random.randint(30, 99)
    user = message.from_user
    # FIX: Ensure user mention works
    user_mention = f"[{user.first_name}](tg://user?id={user.id})"
    text = f"{user_mention}’𝐬 ᴄᴜᴛᴇɴᴇss ʟᴇᴠᴇʟ ɪs {cute_level}% 💖"
    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("𝐒ᴜᴘᴘᴏʀᴛ", url=SUPPORT_CHAT)]])
    await message.reply_text(text, reply_markup=buttons, parse_mode=enums.ParseMode.MARKDOWN)

@app.on_message(filters.command("love"))
async def love_cmd(client, message):
    if len(message.command) < 2 or "+" not in message.text:
        return await message.reply_text("𝐔sᴀɢᴇ: /ʟᴏᴠᴇ 𝐅ɪʀsᴛ 𝐍ᴀᴍᴇ + 𝐒ᴇᴄᴏɴᴅ 𝐍ᴀᴍᴇ")

    # Split the argument and clean it up
    arg_text = message.text.split(None, 1)[1]
    names = [n.strip() for n in arg_text.split("+") if n.strip()]
    
    if len(names) < 2:
        return await message.reply_text("𝐏ʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴛᴡᴏ ɴᴀᴍᴇs sᴇᴘʀᴀᴛᴇᴅ ʙʏ ᴀ '+' (ᴇ.ɢ., /ʟᴏᴠᴇ 𝐀ʟɪᴄᴇ + 𝐁ᴏʙ)")
        
    # FIX: Added love_percent calculation
    love_percent = random.randint(30, 99)

    text = f"❤️ 𝐋ᴏᴠᴇ 𝐏ᴏssɪʙ𝐥ɪᴛʏ\n" \
               f"{names[0]} & {names[1]}’𝐬 ʟᴏᴠᴇ ʟᴇᴠᴇʟ ɪs {love_percent}% 😉"
            
    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("𝐒ᴜᴘᴘᴏʀᴛ", url=SUPPORT_CHAT)]])
    await message.reply_text(text, reply_markup=buttons) 

# -------- /afk Command (FIXED) --------
@app.on_message(filters.command("afk")) 
async def afk_cmd(client, message): 
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    # 1. Check if user is already AFK (meaning they are typing /afk to return)
    if user_id in AFK_USERS:
        # User is coming back
        afk_data = AFK_USERS.pop(user_id)
        time_afk = get_readable_time(int(time.time() - afk_data["time"]))
        await message.reply_text(
            f"𝐘ᴇᴀʜ, [{user_name}](tg://user?id={user_id}), ʏᴏᴜ 𝐚𝐫𝐞 ʙᴀᴄᴋ, ᴏɴʟɪɴᴇ! (𝐀ғᴋ ғᴏʀ: {time_afk}) 😉",
            parse_mode=enums.ParseMode.MARKDOWN
        )
        return # Stop execution after returning
        
    # 2. If not returning, user is setting AFK status
    try:
        # Get the reason if provided
        reason = message.text.split(None, 1)[1] 
    except IndexError:
        reason = "𝐍ᴏ ʀᴇᴀsᴏɴ ɢɪᴠᴇɴ."
    
    # Store AFK status
    AFK_USERS[user_id] = {
        "reason": reason,
        "chat_id": message.chat.id,
        "username": message.from_user.username or user_name,
        "first_name": user_name,
        "time": time.time()
    }
    
    # Send the AFK message
    await message.reply_text(
        f"𝐇ᴇʏ, [{user_name}](tg://user?id={user_id}), ʏᴏᴜ 𝐚𝐫𝐞 𝐀ғᴋ! (𝐑ᴇᴀsᴏɴ: {reason})",
        parse_mode=enums.ParseMode.MARKDOWN
    )

# -------- /mmf Command (Disabled) --------
@app.on_message(filters.command("mmf"))
async def mmf_cmd(client, message):
    # This command is intentionally simplified to a disabled message as image manipulation libraries
    # are often complex to set up in cloud environments.
    
    await message.reply_text(
        "❌ 𝐒𝐭𝐢𝐜𝐤𝐞𝐫 𝐓𝐞𝐱𝐭 𝐅𝐞𝐚𝐭𝐮𝐫𝐞 𝐔𝐧𝐚𝐯𝐚𝐢𝐥𝐚𝐛𝐥𝐞\n"
        "𝐏𝐥𝐞𝐚𝐬𝐞 𝐧𝐨𝐭𝐞: 𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐢𝐬 𝐭𝐞𝐦𝐩𝐨𝐫𝐚𝐫𝐢𝐥𝐲 𝐝𝐢𝐬𝐚𝐛𝐥𝐞𝐝 𝐝𝐮𝐞 𝐭𝐨 𝐦𝐢𝐬𝐬𝐢𝐧𝐠 𝐢𝐦𝐚𝐠𝐞 𝐩𝐫𝐨𝐜𝐞𝐬𝐬𝐢𝐧𝐠 𝐥𝐢𝐛𝐫𝐚𝐫𝐢𝐞s. "
        "𝐈 ᴀᴍ ᴡᴏʀᴋɪɴɢ ᴏɴ ɪᴛ!"
    ) 

# -------- /staff Command (FIXED) --------
@app.on_message(filters.command("staff") & filters.group)
async def staff_cmd(client, message):
    try:
        admins = []
        # FIX: Correct loop for fetching members and applying the filter
        async for admin in app.get_chat_members(message.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
            admins.append(admin)
        
        staff_list = "👑 𝐆ʀᴏᴜᴘ 𝐒ᴛᴀғғ 𝐌ᴇᴍʙᴇʀs:\n\n"
        
        if not admins:
            staff_list += "𝐍ᴏ 𝐚𝐝𝐦𝐢𝐧s 𝐟𝐨𝐮𝐧𝐝."
        else:
            for admin in admins: 
                # Skip deleted accounts
                if admin.user.is_deleted:
                    continue
                    
                tag = f"[{admin.user.first_name}](tg://user?id={admin.user.id})"
                
                # Determine status and append to list
                if admin.status == enums.ChatMemberStatus.OWNER:
                    staff_list += f"• 👑 {tag} (Owner)\n"
                elif admin.user.is_bot:
                    # Exclude the bot itself from the 'human' staff list
                    if admin.user.id == (await client.get_me()).id:
                        continue 
                    staff_list += f"• 🤖 {tag} (Bot Admin)\n"
                else: # Regular human administrator
                    staff_list += f"• 🛡️ {tag} (Admin)\n"
                
        await message.reply_text(staff_list, parse_mode=enums.ParseMode.MARKDOWN)
        
    except Exception as e:
        print(f"Error fetching staff: {e}")
        await message.reply_text(f"🚫 𝐄𝐫𝐫𝐨𝐫 𝐢𝐧 𝐟𝐞𝐭𝐜𝐡𝐢𝐧𝐠 𝐬𝐭𝐚𝐟𝐟: 𝐌𝐚𝐲𝐛𝐞 𝐈 𝐝𝐨𝐧't 𝐡𝐚𝐯𝐞 𝐚𝐝𝐦𝐢𝐧 𝐩𝐞𝐫𝐦𝐢𝐬𝐬𝐢𝐨𝐧s.")

# -------- /botlist Command (NEW & FIXED) --------
@app.on_message(filters.command("botlist") & filters.group)
async def botlist_cmd(client, message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply_text("❗ Oɴʟʏ ᴀᴅᴍɪɴs ᴀɴᴅ ᴏᴡɴᴇʀ ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")
    
    bot_count = 0
    bot_list = "🤖 𝐁𝐨𝐭𝐬 𝐢𝐧 𝐓𝐡𝐢𝐬 𝐆𝐫𝐨𝐮𝐩:\n\n"
    
    try:
        # Get all members
        async for member in app.get_chat_members(message.chat.id, limit=0):
            if member.user.is_bot and not member.user.is_deleted:
                bot_count += 1
                bot_list += f"• {member.user.first_name} (@{member.user.username or 'No Username'})\n"
        
        bot_list = f"📊 𝐓𝐨𝐭𝐚𝐥 𝐁𝐨𝐭𝐬 𝐅𝐨𝐮𝐧𝐝: **{bot_count}**\n\n" + bot_list
        await message.reply_text(bot_list, parse_mode=enums.ParseMode.MARKDOWN)

    except Exception as e:
        print(f"Error fetching bot list: {e}")
        await message.reply_text(f"🚫 𝐄𝐫𝐫𝐨𝐫 𝐢𝐧 𝐟𝐞𝐭𝐜𝐡𝐢𝐧𝐠 𝐛𝐨𝐭 𝐥𝐢𝐬𝐭: 𝐌𝐚𝐲𝐛𝐞 𝐈 𝐝𝐨𝐧't 𝐡𝐚𝐯𝐞 𝐩𝐞𝐫𝐦𝐢𝐬𝐬𝐢𝐨𝐧𝐬.")

# -------- AFK Mentions Handler (FIXED) --------
@app.on_message(filters.mentioned | filters.reply & ~filters.bot, group=1) # Group 1 to process before the main chat handler
async def afk_reply_handler(client, message):
    # Check if the message is a reply to an AFK user
    if message.reply_to_message and message.reply_to_message.from_user.id in AFK_USERS:
        afk_user_id = message.reply_to_message.from_user.id
        user_data = AFK_USERS.get(afk_user_id)
    
    # Check if the message mentions an AFK user
    elif message.entities:
        for entity in message.entities:
            if entity.user and entity.user.id in AFK_USERS:
                afk_user_id = entity.user.id
                user_data = AFK_USERS.get(afk_user_id)
                break
        else:
            return # No AFK user mentioned or replied to

    else:
        return # No mention or reply to check

    if user_data:
        time_afk = get_readable_time(int(time.time() - user_data["time"]))
        reason = user_data["reason"]
        afk_mention = f"[{user_data['first_name']}](tg://user?id={afk_user_id})"
        
        reply_text = f"❗ 𝐒ᴏʀʀʏ, {afk_mention} ɪs 𝐀ғᴋ!\n" \
                     f"🕰️ 𝐓ɪᴍᴇ: {time_afk} ᴀɢᴏ\n" \
                     f"📝 𝐑ᴇᴀsᴏɴ: {reason}"
        
        await message.reply_text(reply_text, parse_mode=enums.ParseMode.MARKDOWN)

# -------- General Chatbot/AFK Return Handler (FIXED to prevent TypeError) --------

# This filter now correctly handles:

# 1. Is a text message (filters.text)

# 2. Is in a group or supergroup ((filters.group | filters.supergroup))

# 3. Is NOT a command (& ~filters.command)

@app.on_message(filters.text & (filters.group | filters.supergroup) & ~filters.command)

async def general_chat_group(client, message):

    # 1. AFK Return Check

    user_id = message.from_user.id

    if user_id in AFK_USERS:

        # User is coming back by sending a message

        afk_data = AFK_USERS.pop(user_id)

        time_afk = get_readable_time(int(time.time() - afk_data["time"]))

        await message.reply_text(

            f"𝐖ᴇʟᴄᴏᴍᴇ 𝐁ᴀᴄᴋ, [{message.from_user.first_name}](tg://user?id={user_id})! 𝐘ᴏᴜ 𝐚𝐫𝐞 𝐎ɴʟɪɴᴇ ɴᴏᴡ. (𝐀ғᴋ ғᴏʀ: {time_afk})",

            parse_mode=enums.ParseMode.MARKDOWN

        )

        return



    # 2. Chatbot Logic for Groups (Only runs if CHATBOT_STATUS is True)

    if not CHATBOT_STATUS.get(message.chat.id, False):

        return # Chatbot is disabled for this group



    me = await client.get_me()

    text = message.text



    # Check if the message is a reply to the bot

    is_reply_to_bot = message.reply_to_message and message.reply_to_message.from_user.id == me.id

    

    # Check if the message mentions the bot's username

    is_mention_bot = me.username.lower() in text.lower() if text and me.username else False

    

    response, is_sticker = get_reply(text)



    # Keyword match found (specific or general, but not None)

    if response:

        # For a specific keyword, reply immediately.

        pass

    else:

        # No specific keyword found, use general chat logic.

        

        # If it's a direct reply/mention, fall back to a generic 'daily' reply if no keyword was matched.

        if is_reply_to_bot or is_mention_bot:

            response = random.choice(DATA.get("daily", ["Hello 👋"]))

            is_sticker = False

        

        # If it's general, non-replied/non-mentioned chat, apply the 80% chance.

        elif not is_reply_to_bot and not is_mention_bot and random.random() > 0.20:

             # 80% chance to reply with a general 'daily' message

            response = random.choice(DATA.get("daily", ["Hello 👋"]))

            is_sticker = False

        else:

            # Drop the message (20% chance for non-replied chat)

            return

    

    # Send the final response

    if response:

        if is_sticker:

            await message.reply_sticker(response)

        else:

            await message.reply_text(response)





# -------- General Chatbot Handler for Private Messages (FIXED) --------

# Filter: filters.text & filters.private (always runs in private chats for non-commands)

@app.on_message(filters.text & filters.private & ~filters.command) 

async def general_chat_private(client, message):

    # 1. AFK Return Check (for consistency)

    user_id = message.from_user.id

    if user_id in AFK_USERS:

        # User is coming back by sending a message

        afk_data = AFK_USERS.pop(user_id)

        time_afk = get_readable_time(int(time.time() - afk_data["time"]))

        await message.reply_text(

            f"𝐖ᴇʟᴄᴏᴍᴇ 𝐁ᴀᴄᴋ, [{message.from_user.first_name}](tg://user?id={user_id})! 𝐘ᴏᴜ 𝐚𝐫𝐞 𝐎ɴʟɪɴᴇ ɴᴏᴡ. (𝐀ғᴋ ғᴏʀ: {time_afk})",

            parse_mode=enums.ParseMode.MARKDOWN

        )

        return



    # 2. Chatbot Logic for Private Chats (Always runs if not an AFK return)

    text = message.text

    response, is_sticker = get_reply(text)



    # In private chat, always reply, so if no keyword is found, default to 'daily'

    if not response:

        response = random.choice(DATA.get("daily", ["Hello 👋"]))

        is_sticker = False



    if response:

        if is_sticker:

            await message.reply_sticker(response)

        else:

            await message.reply_text(response)



# [ ... all your final code remains the same ... ]

# ...

if __name__ == "__main__":

    print("Starting bot...")

    app.run()
