# -*- coding: utf-8 -*-
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import UserNotParticipant
import os, json, random, threading, asyncio, time
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime
import re # For advanced text processing

# -------- Env Vars --------
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# Please ensure you set this to 7589623332 in your environment
OWNER_ID = int(os.environ.get("OWNER_ID", "7589623332"))

DEVELOPER_USERNAME = "Voren"
DEVELOPER_HANDLE = "@TheXVoren"
SUPPORT_CHAT = "https://t.me/Evara_Support_Chat"
UPDATES_CHANNEL = "https://t.me/Evara_Updates"

# -------- Bot Client --------
app = Client("advanced_chatbot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# -------- Global Vars --------
START_TIME = datetime.now()
CHATBOT_STATUS = {}
TAGGING = {}
AFK_USERS = {} # {user_id: {"reason": str, "chat_id": int, "username": str, "time": float}}

# New image URLs and text
START_PHOTO = "https://iili.io/KVzgS44.jpg"
PING_PHOTO = "https://iili.io/KVzbu4t.jpg"
DEVELOPER_PHOTO = "https://iili.io/KVzmgWl.jpg"

# ----------------- NEW FANCY FONTS APPLIED HERE -----------------
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

# --- Sub-Help Menu Content (Applied Font) ---
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
        "/dice ~ 𝐑ᴏʟʟ ᴧ ᴅɪᴄᴇ\n"
        "/jackpot ~ 𝐉ᴧᴄᴋᴘᴏᴛ ᴍᴀᴄʜɪɴᴇ\n"
        "/football ~ 𝐏ʟᴀʏ ғᴏᴏᴛʙᴧʟʟ\n"
        "/basketball ~ 𝐏ʟᴀʏ ʙᴧsᴋᴇᴛʙᴀʟʟ\n"
        "\n_𝐀ʟʟ ᴛʜᴇsᴇ ɢᴀᴍᴇs ᴀʀᴇ ᴀᴠᴀɪʟᴀʙʟᴇ ᴛᴏ ᴇᴠᴇʀʏᴏɴᴇ."
    ),
    "group": (
        "📜 𝐆ʀᴏᴜᴘ 𝐔ᴛɪʟɪᴛʏ 𝐂ᴏᴍᴍᴧɴᴅs:\n"
        "/mmf text ~ 𝐂ʀᴇᴀᴛᴇ ᴀ sᴛɪᴄᴋᴇʀ ᴡɪᴛʜ ᴛᴇxᴛ (ʀᴇᴘʟʏ ᴛᴏ ᴀ sᴛɪᴄᴋᴇʀ)\n"
        "/staff ~ 𝐃ɪsᴘʟᴧʏs ɢʀᴏᴜᴘ sᴛᴧғғ ᴍᴇᴍʙᴇʀs\n"
        "/botlist ~ 𝐂ʜᴇᴄᴋ ʜᴏᴡ ᴍᴀɴʏ ʙᴏᴛs ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ (𝐀ᴅᴍɪɴ ᴏɴʟʏ)"
        "\n_ʙᴏᴛʟɪsᴛ ʀᴇǫᴜɪʀᴇs ᴀᴅᴍɪɴ. ᴏᴛʜᴇʀs ᴀʀᴇ ғᴏʀ ᴇᴠᴇʀʏᴏɴᴇ."
    )
}
# ----------------- FANCY FONTS END -----------------

# -------- NEW STICKER IDS (FIXED) --------
# Sticker IDs provided by the user are now centralized and used for defaults.
NEW_STICKER_IDS = {
    "sticker_cute": [
        "CAACAgEAAxkBAAEPgu9o4USg2JWyq8EjIQcHKAJxTISKnAAChwADUSkNOdIrExvjme5qNgQ",
        "CAACAgUAAxkBAAEPgvFo4USiv1_Mf9-45IeDMN5kETeB7AACzQ4AAsp_IVSL99zOZVfZeTYE"
    ],
    "sticker_funny": [
        "CAACAgQAAxkBAAEPguto4USNgkueY_8UUvG1qR0HO8pVJAAC8hEAAuKyeVAr0E__1DsLxTYE",
        "CAACAgUAAxkBAAEPgvFo4USiv1_Mf9-45IeDMN5kETeB7AACzQ4AAsp_IVSL99zOZVfZeTYE"
    ],
    "sticker_anger": [
        "CAACAgUAAxkBAAEPgudo4UR5HlLeS-qX6SPZa68uWVYxXAACNBAAAvyQWFdWZPeCGuC2gjYE",
        "CAACAgUAAxkBAAEPgulo4USHqBw08BmrpRAczQX6nqkQXQACsQIAAmfVCVXVlV0wAWPSXDYE"
    ],
    "sticker_anime": [
        # Using one of the "baki" stickers as a general default/fallback for 'anime' if the list is empty
        "CAACAgQAAxkBAAEPgu1o4USZaO5ewrgQV8bLpU6Y8z0d9AACXA4AAj9T-FN3FZM9W24oiTYE"
    ]
}

# --- Load Replies & Known Chats ---
try:
    with open("conversation.json", "r", encoding="utf-8") as f:
        DATA = json.load(f)
except:
    # If the JSON file is missing, use a minimal default structure and inject new stickers
    DATA = {
        "daily": ["Hello 👋", "Hey there!", "Hi!", "I am listening..."],
        "love": ["I love you too!", "Aww, sending virtual hugs.", "Be my Valentine! <3"],
        "sad": ["I'm here for you.", "Don't be sad.", "Cheer up!"],
        "happy": ["That's great!", "Keep smiling! :D", "Awesome news!"],
        "bye": ["See ya!", "Bye for now.", "Take care!"],
        "thanks": ["You're welcome!", "Anytime, happy to help."],
        "morning": ["Good morning sunshines!", "Gm to you too!"],
        "night": ["Sweet dreams!", "Good night!", "Sleep tight!"],
        "abuse": ["That's not nice!", "Please be polite.", "Abusing is forbidden."],
        "question": ["I'm a chatbot! How can I help?", "I am here to serve you.", "What do you want to know?"],
        "anger": ["Take a deep breath.", "Stay calm.", "I'm sorry if I made you angry."],
        # Inject new sticker IDs into the default DATA structure
        **NEW_STICKER_IDS
    }

# Ensure required sticker categories exist even if JSON loads by merging
for key, values in NEW_STICKER_IDS.items():
    if key not in DATA or not isinstance(DATA[key], list) or not DATA[key]:
        DATA[key] = values

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

    # Sticker Replies
    "hahaha": "sticker_funny", "lol": "sticker_funny", "rofl": "sticker_funny", "funny": "sticker_funny",
    "cute": "sticker_cute", "aww": "sticker_cute", "so sweet": "sticker_cute", "baby": "sticker_cute",
    "anime": "sticker_anime", "manga": "sticker_anime",
    "i hate you": "sticker_anger", "go away": "sticker_anger", "mad": "sticker_anger",
    "wow": "sticker_anime", # Using a generic sticker category for wow/nice
    "nice": "sticker_anime",
}

# -------- Utility Functions --------
def get_reply(text: str):
    """
    Determines the response (text or sticker ID) based on the input text.
    Returns (response, is_sticker)
    """
    text = text.lower()
    
    # Simple normalization: remove non-alphanumeric except spaces for better keyword matching
    text = re.sub(r'[^\w\s]', '', text) 
    
    for word, cat in KEYWORDS.items():
        if word in text:
            if cat.startswith("sticker_") and cat in DATA and DATA[cat]: # Check if list is not empty
                # Returns a random sticker ID from the category
                sticker_id = random.choice(DATA[cat])
                return (sticker_id, True) 
            elif cat in DATA:
                # Returns a random text reply
                return (random.choice(DATA[cat]), False)
    
    # Default daily reply
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
        return member.status in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR]
    except Exception:
        return False

async def save_chat_id(chat_id, type_):
    """Saves the chat ID to the known chats list."""
    if chat_id not in KNOWN_CHATS[type_]:
        KNOWN_CHATS[type_].append(chat_id)
        with open(CHAT_IDS_FILE, "w") as f:
            json.dump(KNOWN_CHATS, f)

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
    developer_link = DEVELOPER_HANDLE.strip('@')
    
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
                developer_link=developer_link
            ),
            reply_markup=get_start_buttons(me.username)
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
        await query.answer("𝐓ʜɪs ʙᴜᴛᴛᴏɴ ɪs ɴᴏᴛ ʏᴇᴛ 𝐅ᴜɴᴄᴛɪᴏɴᴀʟ.") 

# -------- Commands --------

# -------- /start Command --------
@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    user = message.from_user
    me = await app.get_me()
    developer_link = DEVELOPER_HANDLE.strip('@')
    
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
        pass # Ignore if already deleted/edited
        
    await message.reply_photo(
        START_PHOTO,
        caption=INTRO_TEXT_TEMPLATE.format(
            mention_name=f"[{user.first_name}](tg://user?id={user.id})",
            developer=DEVELOPER_USERNAME,
            developer_link=developer_link
        ),
        reply_markup=get_start_buttons(me.username)
    )
    await save_chat_id(message.chat.id, "privates") 

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
        pass # Ignore if the animation message is already deleted/edited/not found
        
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
    user = message.reply_to_message.from_user if message.reply_to_message else message.from_user
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
    
    text = message.text.split(None, 1)[1] if len(message.command) > 1 else None
    
    sent = 0
    failed = 0
    m = await message.reply_text("𝐒ᴛᴀʀᴛɪɴɢ 𝐁ʀᴏᴀᴅᴄᴀsᴛ...")
    
    for chat_type in ["privates", "groups"]:
        for chat_id in KNOWN_CHATS[chat_type]:
            try:
                if message.reply_to_message:
                    await message.reply_to_message.copy(chat_id)
                else:
                    await app.send_message(chat_id, text)
                sent += 1
            except Exception as e:
                # print(f"Failed to broadcast to {chat_id}: {e}") # Debugging line
                failed += 1
                continue
                
    await m.edit_text(f"✅ 𝐁ʀᴏᴀᴅᴄᴀsᴛ ᴅᴏɴᴇ!\n𝐒ᴇɴᴛ ᴛᴏ {sent} ᴄʜᴀᴛs.\n𝐅ᴀɪʟᴇᴅ ɪɴ {failed} ᴄʜᴀᴛs.")

# -------- /chatbot Toggle --------
@app.on_message(filters.command("chatbot") & filters.group)
async def chatbot_toggle(client, message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply_text("❗ Oɴʟʏ ᴀᴅᴍɪɴs ᴀɴᴅ ᴏᴡɴᴇʀ ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")
    
    if len(message.command) < 2:
        return await message.reply_text("𝐔sᴀɢᴇ: /ᴄʜᴀᴛʙᴏᴛ ᴇɴᴀʙʟᴇ ᴏʀ /ᴄʜᴀᴛʙᴏᴛ ᴅɪsᴀʙʟᴇ")
        
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
        return await message.reply_text("❗ 𝐈 ɴᴇᴇᴅ ᴀᴅᴍɪɴ ᴘᴇʀᴍɪssɪᴏɴ (ᴛᴀɢ ᴍᴇᴍʙᴇʀs) ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")

    chat_id = message.chat.id
    
    if TAGGING.get(chat_id):
        return await message.reply_text("❗ 𝐀ʟʀᴇᴀᴅʏ ᴛᴀɢɢɪɴɢ ɪɴ ᴛʜɪs ᴄʜᴀᴛ. 𝐔sᴇ /sᴛᴏᴘ ᴛᴏ ᴄᴀɴᴄᴇʟ.")
        
    TAGGING[chat_id] = True
    
    # Get message content
    if len(message.command) > 1:
        msg = message.text.split(None, 1)[1]
    elif message.reply_to_message:
        msg = "𝐓ᴀɢɢɪɴɢ ғʀᴏᴍ ʀᴇᴘʟɪᴇᴅ ᴍᴇssᴀɢᴇ!"
    else:
        msg = "𝐀ᴛᴛᴇɴᴛɪᴏ𝐍!"
        
    m = await message.reply_text("𝐓ᴀɢɢɪɴɢ 𝐒ᴛᴀʀᴛᴇᴅ !! ♥")
    
    member_list = []
    # Collect all members first
    try:
        async for member in app.get_chat_members(chat_id):
            if not (member.user.is_bot or member.user.is_deleted):
                member_list.append(member.user)
    except Exception:
        TAGGING[chat_id] = False
        return await m.edit_text("🚫 𝐄𝐫𝐫𝐨𝐫 𝐢𝐧 𝐟𝐞𝐭𝐜𝐡𝐢𝐧𝐠 𝐦𝐞𝐦𝐛𝐞𝐫s: 𝐌𝐚𝐲𝐛𝐞 𝐭𝐡𝐢𝐬 𝐠𝐫𝐨𝐮𝐩 𝐢s 𝐭𝐨𝐨 𝐛𝐢𝐠 𝐨𝐫 𝐈 𝐝𝐨𝐧'𝐭 𝐡𝐚𝐯𝐞 𝐩𝐞𝐫𝐦𝐢𝐬𝐬𝐢𝐨𝐧s.")

    # Start tagging in chunks
    chunk_size = 5
    for i in range(0, len(member_list), chunk_size):
        if not TAGGING.get(chat_id):
            break
            
        chunk = member_list[i:i + chunk_size]
        tag_text = f"{msg}\n"
        
        for user in chunk:
            tag_text += f"[{user.first_name}](tg://user?id={user.id}) "
            
        try:
            # Send the tag chunk
            await app.send_message(chat_id, tag_text, disable_web_page_preview=True)
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

# -------- /couples, /cute, /love Commands --------
@app.on_message(filters.command("couples") & filters.group)
async def couples_cmd(client, message):
    member_list = []
    try:
        async for member in app.get_chat_members(message.chat.id):
            if not (member.user.is_bot or member.user.is_deleted):
                member_list.append(member.user)
    except Exception:
        return await message.reply_text("🚫 𝐂𝐚𝐧𝐧𝐨𝐭 𝐟𝐞𝐭𝐜𝐡 𝐦𝐞𝐦𝐛𝐞𝐫s 𝐝𝐮𝐞 𝐭𝐨 𝐫𝐞𝐬𝐭𝐫𝐢𝐜𝐭𝐢𝐨𝐧s.")

    if len(member_list) < 2:
        return await message.reply_text("❗ 𝐍ᴇᴇᴅ ᴀᴛ ʟᴇᴀsᴛ ᴛᴡᴏ ᴍᴇᴍʙᴇʀs ᴛᴏ ғᴏʀᴍ ᴀ 𝐂ᴏᴜᴘʟᴇ.")
        
    # Pick two random unique members
    couple = random.sample(member_list, 2)
    user1 = couple[0]
    user2 = couple[1]
    
    # Calculate a random love percentage (just for fun)
    love_percent = random.randint(30, 99)
    
    await message.reply_text(
        f"💘 𝐍ᴇᴡ 𝐂ᴏᴜᴘʟᴇ ᴏғ ᴛʜᴇ 𝐃ᴀʏ!\n\n"
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
    text = f"{user_mention}'𝐬 ᴄᴜᴛᴇɴᴇss ʟᴇᴠᴇʟ ɪs {cute_level}% 💖"
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
        
    # The rest of the logic is fine
    love_percent = random.randint(1, 100)
    text = f"❤️ 𝐋ᴏᴠᴇ 𝐏ᴏssɪʙʟɪᴛʏ\n" \
               f"{names[0]} & {names[1]}'𝐬 ʟᴏᴠᴇ ʟᴇᴠᴇʟ ɪs {love_percent}% 😉"
              
    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("𝐒ᴜᴘᴘᴏʀᴛ", url=SUPPORT_CHAT)]])
    await message.reply_text(text, reply_markup=buttons) 

# -------- /afk Command --------
@app.on_message(filters.command("afk"))
async def afk_cmd(client, message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    # Check if user is already AFK (meaning they are typing /afk to return)
    if user_id in AFK_USERS:
        # User is coming back (handled in group_reply_and_afk_checker for better UX)
        if message.chat.type == enums.ChatType.PRIVATE:
            afk_data = AFK_USERS.pop(user_id)
            time_afk = get_readable_time(int(time.time() - afk_data["time"]))
            await message.reply_text(
                f"𝐘ᴇᴀʜ, [{user_name}](tg://user?id={user_id}), ʏᴏᴜ ᴀʀᴇ ʙᴀᴄᴋ, ᴏɴʟɪɴᴇ! (𝐀ғᴋ ғᴏʀ: {time_afk}) 😉",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return # Stop execution after returning
        
    # If user is not AFK, they are setting AFK status
    try:
        reason = message.text.split(None, 1)[1]
    except IndexError:
        reason = "𝐍ᴏ ʀᴇᴀsᴏɴ ɢɪᴠᴇɴ."
    
    AFK_USERS[user_id] = {"reason": reason, "chat_id": message.chat.id, "username": user_name, "time": time.time()}
    
    # Send the AFK message
    await message.reply_text(
        f"𝐇ᴇʏ, [{user_name}](tg://user?id={user_id}), ʏᴏᴜ ᴀʀᴇ 𝐀ғᴋ! (𝐑ᴇᴀsᴏɴ: {reason})",
        parse_mode=enums.ParseMode.MARKDOWN
    )

# -------- /mmf Command (FIXED - Simple reply) --------
@app.on_message(filters.command("mmf") & filters.group)
async def mmf_cmd(client, message):
    # This feature requires complex external tools/logic (e.g., Pillow).
    
    if not message.reply_to_message or not message.reply_to_message.sticker:
        return await message.reply_text("❗ 𝐑ᴇᴘʟʏ ᴛᴏ ᴀ sᴛɪᴄᴋᴇʀ ᴀɴᴅ ᴘʀᴏᴠɪᴅᴇ ᴛᴇxᴛ ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.\n\n*(𝐍ᴏᴛᴇ: ᴛʜɪs ғᴇᴀᴛᴜʀᴇ ɪs ᴄᴜʀʀᴇɴᴛʟʏ ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴀɴᴄᴇ)*")
        
    if len(message.command) < 2:
        return await message.reply_text("❗ 𝐏𝐫𝐨𝐯𝐢𝐝𝐞 𝐭𝐡𝐞 𝐭𝐞𝐱𝐭 𝐲𝐨𝐮 w𝐚𝐧𝐭 𝐨𝐧 𝐭𝐡𝐞 𝐬𝐭𝐢𝐜𝐤𝐞𝐫.")
        
    await message.reply_text(
        "❌ 𝐒𝐭𝐢𝐜𝐤𝐞𝐫 𝐓𝐞𝐱𝐭 𝐅𝐞𝐚𝐭𝐮𝐫𝐞 𝐔𝐧𝐚𝐯𝐚𝐢𝐥𝐚𝐛𝐥𝐞\n"
        "𝐏𝐥𝐞𝐚𝐬𝐞 𝐧𝐨𝐭𝐞: 𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐢s 𝐭𝐞𝐦𝐩𝐨𝐫𝐚𝐫𝐢𝐥𝐲 𝐝𝐢𝐬𝐚𝐛𝐥𝐞𝐝 𝐝𝐮𝐞 𝐭𝐨 𝐦𝐢𝐬𝐬𝐢𝐧𝐠 𝐢𝐦𝐚𝐠𝐞 𝐩𝐫𝐨𝐜𝐞𝐬𝐬𝐢𝐧𝐠 𝐥𝐢𝐛𝐫𝐚𝐫𝐢𝐞s. "
        "𝐈 ᴀᴍ ᴡᴏʀᴋɪɴɢ ᴏɴ ɪᴛ!"
    ) 

# -------- /staff, /botlist Commands --------
@app.on_message(filters.command("staff") & filters.group)
async def staff_cmd(client, message):
    # Logic confirmed from previous fix
    try:
        admins = [
            admin async for admin in app.get_chat_members(message.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS)
        ]
        
        staff_list = "👑 𝐆ʀᴏᴜᴘ 𝐒ᴛᴀғғ 𝐌ᴇᴍʙᴇʀs:\n"
        for admin in admins:
            if not admin.user.is_bot:
                tag = f"[{admin.user.first_name}](tg://user?id={admin.user.id})"
                status = admin.status.name.replace("_", " ").title()
                staff_list += f"• {tag} ({status})\n"
                
        await message.reply_text(staff_list, disable_web_page_preview=True, parse_mode=enums.ParseMode.MARKDOWN)
        
    except Exception as e:
        await message.reply_text(f"🚫 𝐄𝐫𝐫𝐨𝐫 𝐢𝐧 𝐟𝐞𝐭𝐜𝐡𝐢𝐧𝐠 𝐬𝐭𝐚𝐟𝐟: {e}")

@app.on_message(filters.command("botlist") & filters.group)
async def botlist_cmd(client, message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply_text("❗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ /ʙᴏᴛʟɪsᴛ.")
        
    # Logic confirmed from previous fix
    try:
        bots = [
            bot async for bot in app.get_chat_members(message.chat.id, filter=enums.ChatMembersFilter.BOTS)
        ]
        
        bot_list = "🤖 𝐁ᴏᴛs ɪɴ ᴛʜɪs 𝐆ʀᴏᴜᴘ:\n"
        for bot in bots:
            tag = f"[{bot.user.first_name}](tg://user?id={bot.user.id})"
            # Ensure username exists before trying to access it
            username_part = f" (@{bot.user.username})" if bot.user.username else ""
            bot_list += f"• {tag}{username_part}\n"
            
        await message.reply_text(bot_list, disable_web_page_preview=True, parse_mode=enums.ParseMode.MARKDOWN)
        
    except Exception as e:
        # Catch any remaining fetch errors
        await message.reply_text(f"🚫 𝐄𝐫𝐫𝐨𝐫 𝐢𝐧 𝐟𝐞𝐭𝐜𝐡𝐢𝐧𝐠 𝐛𝐨𝐭 𝐥𝐢𝐬𝐭: {e}") 

# -------- Game Commands --------
@app.on_message(filters.command("dice"))
async def dice_cmd(client, message):
    await app.send_dice(message.chat.id, "🎲")

@app.on_message(filters.command("jackpot"))
async def jackpot_cmd(client, message):
    await app.send_dice(message.chat.id, "🎰")

@app.on_message(filters.command("football"))
async def football_cmd(client, message):
    await app.send_dice(message.chat.id, "⚽")

@app.on_message(filters.command("basketball"))
async def basketball_cmd(client, message):
    await app.send_dice(message.chat.id, "🏀")

# -------- Private Auto Reply (FIXED) --------
@app.on_message(filters.text & filters.private, group=0)
async def private_reply(client, message):
    # FIX: Missing the call to get_reply and assignment of response/is_sticker
    response, is_sticker = get_reply(message.text)
    
    if is_sticker:
        await message.reply_sticker(response)
    else:
        await message.reply_text(response)

# -------- Group Auto Reply & AFK Checker (FIXED) --------
@app.on_message(filters.text & filters.group, group=1)
async def group_reply_and_afk_checker(client, message: Message):
    await save_chat_id(message.chat.id, "groups")
    
    # --- 1. User is returning from AFK (FIXED LOGIC) ---
    if (message.from_user.id in AFK_USERS and 
        message.text and 
        not message.text.lower().startswith("/afk")):
        
        user_id = message.from_user.id
        
        # Calculate time before deleting
        afk_data = AFK_USERS.pop(user_id) # Remove user from AFK list
        time_afk = get_readable_time(int(time.time() - afk_data["time"]))
        user_name = afk_data["username"]
        
        # Send the "I'm back" message
        await message.reply_text(
            f"𝐘ᴇᴀʜ, [{user_name}](tg://user?id={user_id}), ʏᴏᴜ ᴀʀᴇ ʙᴀᴄᴋ, ᴏɴʟɪɴᴇ! (𝐀ғᴋ ғᴏʀ: {time_afk}) 😉",
            parse_mode=enums.ParseMode.MARKDOWN
        )

    # --- 2. AFK Tag/Reply Check (Checking mentions and replies) ---
    users_to_check = []
    
    # Check reply
    if message.reply_to_message:
        # Check if the replied message author is AFK
        replied_user = message.reply_to_message.from_user
        if replied_user and replied_user.id in AFK_USERS:
            users_to_check.append(replied_user.id)
            
    # Check text mentions (FIXED LOGIC)
    if message.text and message.entities:
        for entity in message.entities:
            # Check for TEXT_MENTION (user object is available)
            if entity.type == enums.MessageEntityType.TEXT_MENTION and entity.user:
                if entity.user.id in AFK_USERS:
                    users_to_check.append(entity.user.id)
            
    # Send AFK notice for checked users
    for afk_id in set(users_to_check):
        if afk_id in AFK_USERS:
            afk_data = AFK_USERS[afk_id]
            reason = afk_data["reason"]
            user_name = afk_data["username"]
            time_afk = get_readable_time(int(time.time() - afk_data["time"]))

            await message.reply_text(
                f"⚠️ [{user_name}](tg://user?id={afk_id}) 𝐢s 𝐀ғᴋ! ◉‿◉\n"
                f"𝐑ᴇᴀsᴏɴ: *{reason}*\n"
                f"𝐓ɪᴍᴇ: *{time_afk}*",
                parse_mode=enums.ParseMode.MARKDOWN
            )
            # Only send one AFK notice per message to avoid spam
            break 
            
    # --- 3. Chatbot Auto-Reply Logic (FIXED - This was missing) ---
    me = await client.get_me()
    
    is_chatbot_enabled = CHATBOT_STATUS.get(message.chat.id, False)
    is_reply_to_bot = message.reply_to_message and message.reply_to_message.from_user.id == me.id
    
    # Check for explicit mention of the bot in the message text
    is_bot_mentioned = (
        message.text and me.username and (
            f"@{me.username.lower()}" in message.text.lower() or
            me.first_name.lower() in message.text.lower()
        )
    )

    # The bot replies if the chatbot is enabled OR if the message is a reply/mention to the bot
    if is_chatbot_enabled or is_reply_to_bot or is_bot_mentioned:
        
        # Determine the text to reply to (use message text for general keywords)
        text_for_reply = message.text
        
        response, is_sticker = get_reply(text_for_reply)
        
        # Reply only if a meaningful response was generated
        if response: 
            if is_sticker:
                await message.reply_sticker(response)
            else:
                await message.reply_text(response)
