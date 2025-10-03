# -*- coding: utf-8 -*-
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import UserNotParticipant
import os, json, random, threading, asyncio, time
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime

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
    "𝐇𝐞𝐲 {mention_name}\n"
    "✦ 𝐈 𝐚𝐦 𝐚𝐧 𝐚𝐝𝐯𝐚𝐧𝐜𝐞𝐝 𝐜𝐡𝐚𝐭 𝐛𝐨𝐭 𝐰𝐢𝐭𝐡 𝐬𝐨𝐦𝐞 𝐟𝐞𝐚𝐭𝐮𝐫𝐞𝐬. \n"
    "✦ 𝐑𝐞𝐩𝐥𝐲 𝐢𝐧 𝐠𝐫𝐨𝐮𝐩𝐬 & 𝐩𝐫𝐢𝐯𝐚𝐭𝐞 𝐦𝐞𝐬𝐬𝐚𝐠𝐞𝐬 🥀\n"
    "✦ 𝐍𝐨 𝐚𝐛𝐮𝐬𝐢𝐧𝐠 & 𝐳𝐞𝐫𝐨 𝐝𝐨𝐰𝐧𝐭𝐢𝐦𝐞\n"
    "✦ 𝐂𝐥𝐢𝐜𝐤 𝐇𝐞𝐥𝐩 𝐛𝐮𝐭𝐭𝐨𝐧 𝐟𝐨𝐫 𝐜𝐨𝐦𝐦𝐚𝐧𝐝𝐬 ❤️\n"
    "❖ 𝐌𝐚𝐝𝐞 𝐛𝐲...{developer}"
)

ABOUT_TEXT = (
    "❖ 𝐀 𝐦𝐢𝐧𝐢 𝐜𝐡𝐚𝐭 𝐛𝐨𝐭 𝐟𝐨𝐫 𝐓𝐞𝐥𝐞𝐠𝐫𝐚𝐦 𝐠𝐫𝐨𝐮𝐩𝐬 & 𝐩𝐫𝐢𝐯𝐚𝐭𝐞 𝐦𝐞𝐬𝐬𝐚𝐠𝐞𝐬\n"
    "● 𝐖𝐫𝐢𝐭𝐭𝐞𝐧 𝐢𝐧 𝐏𝐲𝐭𝐡𝐨𝐧 \n"
    "● 𝐊𝐞𝐞𝐩 𝐲𝐨𝐮𝐫 𝐠𝐫𝐨𝐮𝐩 𝐚𝐜𝐭𝐢𝐯𝐞.\n"
    "● 𝐀𝐝𝐝 𝐦𝐞 𝐧𝐨𝐰 𝐛𝐚𝐛𝐲 𝐢𝐧 𝐲𝐨𝐮𝐫 𝐠𝐫𝐨𝐮𝐩𝐬."
)

# --- Sub-Help Menu Content (Applied Font) ---
HELP_COMMANDS_TEXT_MAP = {
    "couple": (
        "📜 𝐂𝐨𝐮𝐩𝐥𝐞 & 𝐋𝐨𝐯𝐞 𝐂𝐨𝐦𝐦𝐚𝐧𝐝𝐬:\n"
        "/couples ~ 𝐂𝐡𝐨𝐨𝐬𝐞 𝐚 𝐫𝐚𝐧𝐝𝐨𝐦 𝐜𝐨𝐮𝐩𝐥𝐞\n"
        "/cute ~ 𝐂𝐡𝐞𝐜𝐤 𝐲𝐨𝐮𝐫 𝐜𝐮𝐭𝐞𝐧𝐞𝐬𝐬\n"
        "/love name1 + name2 ~ 𝐒𝐞𝐞 𝐥𝐨𝐯𝐞 𝐩𝐨𝐬𝐬𝐢𝐛𝐢𝐥𝐢𝐭𝐲\n"
        "\n_𝐀𝐥𝐥 𝐭𝐡𝐞𝐬𝐞 𝐜𝐨𝐦𝐦𝐚𝐧𝐝𝐬 𝐚𝐫𝐞 𝐚𝐯𝐚𝐢𝐥𝐚𝐛𝐥𝐞 𝐭𝐨 𝐞𝐯𝐞𝐫𝐲𝐨𝐧𝐞."
    ),
    "chatbot": (
        "📜 𝐂𝐡𝐚𝐭𝐛𝐨𝐭 𝐂𝐨𝐦𝐦𝐚𝐧𝐝:\n"
        "/chatbot enable/disable ~ 𝐄𝐧𝐚𝐛𝐥𝐞/𝐝𝐢𝐬𝐚𝐛𝐥𝐞 𝐜𝐡𝐚𝐭𝐛𝐨𝐭\n"
        "\n"
        "𝐍𝐨𝐭𝐞: 𝐎𝐧𝐥𝐲 𝐰𝐨𝐫𝐤𝐬 𝐢𝐧 𝐠𝐫𝐨𝐮𝐩 𝐚𝐧𝐝 𝐨𝐧𝐥𝐲 𝐟𝐨𝐫 𝐚𝐝𝐦𝐢𝐧𝐬/𝐨𝐰𝐧𝐞𝐫.\n"
        "𝐄𝐱𝐚𝐦𝐩𝐥𝐞: /chatbot enable"
    ),
    "tools": (
        "📜 𝐓𝐨𝐨𝐥𝐬 𝐂𝐨𝐦𝐦𝐚𝐧𝐝𝐬:\n"
        "/id ~ 𝐆𝐞𝐭 𝐮𝐬𝐞𝐫 𝐈𝐃 (𝐫𝐞𝐩𝐥𝐲 𝐨𝐫 𝐭𝐚𝐠)\n"
        "/tagall ~ 𝐓𝐚𝐠 𝐚𝐥𝐥 m𝐞𝐦𝐛𝐞𝐫𝐬 (𝐀𝐝𝐦𝐢𝐧 𝐎𝐧𝐥𝐲)\n"
        "/stop ~ 𝐓𝐨 𝐬𝐭𝐨𝐩 𝐭𝐚𝐠𝐠𝐢𝐧𝐠 (𝐀𝐝𝐦𝐢𝐧 𝐎𝐧𝐥𝐲)\n"
        "/afk reason ~ 𝐀𝐰𝐚𝐲 𝐟𝐫𝐨𝐦 𝐭𝐡𝐞 𝐤𝐞𝐲𝐛𝐨𝐚𝐫𝐝\n"
        "\n_𝐓𝐚𝐠𝐚𝐥𝐥/𝐒𝐭𝐨𝐩 𝐫𝐞𝐪𝐮𝐢𝐫𝐞𝐬 𝐀𝐝𝐦𝐢𝐧. 𝐎𝐭𝐡𝐞𝐫𝐬 𝐚𝐫𝐞 𝐟𝐨𝐫 𝐞𝐯𝐞𝐫𝐲𝐨𝐧𝐞."
    ),
    "games": (
        "📜 𝐆𝐚𝐦𝐞𝐬 𝐂𝐨𝐦𝐦𝐚𝐧𝐝𝐬:\n"
        "/dice ~ 𝐑𝐨𝐥𝐥 𝐚 𝐝𝐢𝐜𝐞\n"
        "/jackpot ~ 𝐉𝐚𝐜𝐤𝐩𝐨𝐭 𝐦𝐚𝐜𝐡𝐢𝐧𝐞\n"
        "/football ~ 𝐏𝐥𝐚𝐲 𝐟𝐨𝐨𝐭𝐛𝐚𝐥𝐥\n"
        "/basketball ~ 𝐏𝐥𝐚𝐲 𝐛𝐚𝐬𝐤𝐞𝐭𝐛𝐚𝐥𝐥\n"
        "\n_𝐀𝐥𝐥 𝐭𝐡𝐞𝐬𝐞 𝐠𝐚𝐦𝐞𝐬 𝐚𝐫𝐞 𝐚𝐯𝐚𝐢𝐥𝐚𝐛𝐥𝐞 𝐭𝐨 𝐞𝐯𝐞𝐫𝐲𝐨𝐧𝐞."
    ),
    "group": (
        "📜 𝐆𝐫𝐨𝐮𝐩 𝐔𝐭𝐢𝐥𝐢𝐭𝐲 𝐂𝐨𝐦𝐦𝐚𝐧𝐝𝐬:\n"
        "/mmf text ~ 𝐂𝐫𝐞𝐚𝐭𝐞 𝐚 𝐬𝐭𝐢𝐜𝐤𝐞𝐫 𝐰𝐢𝐭𝐡 𝐭𝐞𝐱𝐭 (𝐑𝐞𝐩𝐥𝐲 𝐭𝐨 𝐚 𝐬𝐭𝐢𝐜𝐤𝐞𝐫)\n"
        "/staff ~ 𝐃𝐢𝐬𝐩𝐥𝐚𝐲𝐬 𝐠𝐫𝐨𝐮𝐩 𝐬𝐭𝐚𝐟𝐟 𝐦𝐞𝐦𝐛𝐞𝐫𝐬\n"
        "/botlist ~ 𝐂𝐡𝐞𝐜𝐤 𝐡𝐨𝐰 𝐦𝐚𝐧𝐲 𝐛𝐨𝐭𝐬 𝐢𝐧 𝐲𝐨𝐮𝐫 𝐠𝐫𝐨𝐮𝐩 (𝐀𝐝𝐦𝐢𝐧 𝐎𝐧𝐥𝐲)"
        "\n_𝐁𝐨𝐭𝐥𝐢𝐬𝐭 𝐫𝐞𝐪𝐮𝐢𝐫𝐞𝐬 𝐀𝐝𝐦𝐢𝐧. 𝐎𝐭𝐡𝐞𝐫𝐬 𝐚𝐫𝐞 𝐟𝐨𝐫 𝐞𝐯𝐞𝐫𝐲𝐨𝐧𝐞."
    )
}
# ----------------- FANCY FONTS END -----------------


# --- Load Replies & Known Chats ---
try:
    with open("conversation.json", "r", encoding="utf-8") as f:
        DATA = json.load(f)
except:
    DATA = {}

if "daily" not in DATA:
    DATA["daily"] = ["Hello 👋", "Hey there!", "Hi!"]

CHAT_IDS_FILE = "chats.json"
if os.path.exists(CHAT_IDS_FILE):
    with open(CHAT_IDS_FILE, "r") as f:
        KNOWN_CHATS = json.load(f)
else:
    KNOWN_CHATS = {"groups": [], "privates": []}

KEYWORDS = {
    "love": "love", "i love you": "love", "miss": "love",
    "sad": "sad", "cry": "sad", "depressed": "sad",
    "happy": "happy", "mast": "happy",
    "hello": "daily", "hi": "daily", "hey": "daily",
    "bye": "bye", "goodbye": "bye",
    "thanks": "thanks", "thank you": "thanks",
    "gm": "morning", "good morning": "morning",
    "gn": "night", "good night": "night",
    "chutiya": "abuse", "bc": "abuse", "mc": "abuse"
}

# -------- Utility Functions --------
def get_reply(text: str):
    text = text.lower()
    for word, cat in KEYWORDS.items():
        if word in text and cat in DATA:
            return random.choice(DATA[cat])
    return random.choice(DATA.get("daily", ["Hello 👋"]))

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
    return result.strip()

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
            InlineKeyboardButton("𝐎𝐰𝐧𝐞𝐫", user_id=OWNER_ID),
            InlineKeyboardButton("𝐀𝐛𝐨𝐮𝐭", callback_data="about")
        ],
        [InlineKeyboardButton("𝐇𝐞𝐥𝐩 & 𝐂𝐨𝐦𝐦𝐚𝐧𝐝𝐬", callback_data="help_main")]
    ])

def get_about_buttons():
    """Returns the About section button layout."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("𝐄𝐯𝐚𝐫𝐚 𝐒𝐮𝐩𝐩𝐨𝐫𝐭 𝐂𝐡𝐚𝐭", url=SUPPORT_CHAT),
            InlineKeyboardButton("𝐔𝐩𝐝𝐚𝐭𝐞𝐬", url=UPDATES_CHANNEL)
        ],
        [
            InlineKeyboardButton("𝐁𝐚𝐜𝐤", callback_data="start_back"),
            InlineKeyboardButton("𝐂𝐥𝐨𝐬𝐞", callback_data="close")
        ]
    ])

def get_help_main_buttons():
    """Returns the main Help & Commands button layout."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("𝐂𝐨𝐮𝐩𝐥𝐞", callback_data="help_couple"),
            InlineKeyboardButton("𝐂𝐡𝐚𝐭𝐛𝐨𝐭", callback_data="help_chatbot")
        ],
        [
            InlineKeyboardButton("𝐓𝐨𝐨𝐥𝐬", callback_data="help_tools"),
            InlineKeyboardButton("𝐆𝐚𝐦𝐞𝐬", callback_data="help_games")
        ],
        [InlineKeyboardButton("𝐆𝐫𝐨𝐮𝐩", callback_data="help_group")],
        [
            InlineKeyboardButton("𝐁𝐚𝐜𝐤", callback_data="start_back"),
            InlineKeyboardButton("𝐂𝐥𝐨𝐬𝐞", callback_data="close")
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
            caption="📜 𝐂𝐨𝐦𝐦𝐚𝐧𝐝𝐬 𝐌𝐞𝐧𝐮:\n\n𝐂𝐡𝐨𝐨𝐬𝐞 𝐚 𝐜𝐚𝐭𝐞𝐠𝐨𝐫𝐲 𝐛𝐞𝐥𝐨𝐰:",
            reply_markup=get_help_main_buttons()
        )
    elif data.startswith("help_"):
        category = data.split("_")[1]
        text = HELP_COMMANDS_TEXT_MAP.get(category, "𝐄𝐫𝐫𝐨𝐫: 𝐔𝐧𝐤𝐧𝐨𝐰𝐧 𝐂𝐚𝐭𝐞𝐠𝐨𝐫𝐲")
        
        # Custom button logic for sub-menus
        buttons = []
        if category in ["couple", "cute", "love"]:
            buttons.append(InlineKeyboardButton("𝐒𝐮𝐩𝐩𝐨𝐫𝐭", url=SUPPORT_CHAT))
            
        # Ensure buttons is a list of lists for InlineKeyboardMarkup
        buttons_markup_rows = []
        if buttons:
            buttons_markup_rows.append(buttons)
        buttons_markup_rows.append([
            InlineKeyboardButton("𝐁𝐚𝐜𝐤", callback_data="help_main"),
            InlineKeyboardButton("𝐂𝐥𝐨𝐬𝐞", callback_data="close")
        ])
        
        await query.message.edit_caption(
            caption=text,
            reply_markup=InlineKeyboardMarkup(buttons_markup_rows)
        )
    elif data == "close":
        await query.message.delete()
    else:
        await query.answer("𝐓𝐡𝐢𝐬 𝐛𝐮𝐭𝐭𝐨𝐧 𝐢𝐬 𝐧𝐨𝐭 𝐲𝐞𝐭 𝐟𝐮𝐧𝐜𝐭𝐢𝐨𝐧𝐚𝐥.") 

# -------- Commands --------

# -------- /start Command --------
@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    user = message.from_user
    me = await app.get_me()
    developer_link = DEVELOPER_HANDLE.strip('@')
    
    # Ding Dong Animation
    anim_text = "𝐃𝐈𝐍𝐆...𝐃𝐎𝐍𝐆 💥....𝐁𝐎𝐓 𝐈𝐒 𝐒𝐓𝐀𝐑𝐓𝐈𝐍𝐆"
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
    anim_text = "𝐘𝐎𝐔 𝐖𝐀𝐍𝐓 𝐓𝐎 𝐊𝐍𝐎𝐖, 𝐓𝐇𝐈𝐒 𝐁𝐎𝐓 𝐃𝐄𝐕𝐄𝐋𝐎𝐏𝐄𝐑 💥..𝐇𝐄𝐑𝐄"
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
        [InlineKeyboardButton("𝐃𝐞𝐯𝐞𝐥𝐨𝐩𝐞𝐫 ღ", url=f"https://t.me/{DEVELOPER_HANDLE.strip('@')}")]
    ])
    
    caption_text = f"𝐁𝐨𝐭 𝐝𝐞𝐯𝐞𝐥𝐨𝐩𝐞𝐫 𝐢𝐬 [{DEVELOPER_USERNAME}](t.me/{DEVELOPER_HANDLE.strip('@')})"
    
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
    m = await message.reply_text("𝐏𝐢𝐧𝐠𝐢𝐧𝐠...𝐬𝐭𝐚𝐫𝐭𝐞𝐝..´･ᴗ･")
    await asyncio.sleep(0.5)
    await m.edit_text("𝐏𝐢𝐧𝐠..𝐏𝐨𝐧𝐠 ⚡")
    await asyncio.sleep(0.5)
    
    end = time.time()
    ping_ms = round((end-start)*1000)
    uptime_seconds = (datetime.now() - START_TIME).total_seconds()
    uptime_readable = get_readable_time(int(uptime_seconds))
    me = await client.get_me()
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ 𝐀𝐝𝐝 𝐌𝐞 ➕", url=f"https://t.me/{me.username}?startgroup=true")],
        [InlineKeyboardButton("𝐒𝐮𝐩𝐩𝐨𝐫𝐭", url=SUPPORT_CHAT)]
    ])
    
    try:
        await m.delete() # Delete the animation message
    except:
        pass
        
    await message.reply_photo(
        PING_PHOTO,
        caption=f"𝐏𝐢𝐧𝐠 ➳ {ping_ms} 𝐦𝐬\n"
                f"𝐔𝐩𝐭𝐢𝐦𝐞 ➳ {uptime_readable}",
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
    await message.reply_text(f"📊 𝐁𝐨𝐭 𝐒𝐭𝐚𝐭𝐬:\n👥 𝐆𝐫𝐨𝐮𝐩𝐬: {len(KNOWN_CHATS['groups'])}\n👤 𝐏𝐫𝐢𝐯𝐚𝐭𝐞𝐬: {len(KNOWN_CHATS['privates'])}")

# -------- /broadcast (Owner Only) --------
@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast_cmd(client, message):
    if not (message.reply_to_message or len(message.command) > 1):
        return await message.reply_text("𝐔𝐬𝐚𝐠𝐞: /𝐛𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭 𝐨𝐫 𝐫𝐞𝐩𝐥𝐲 𝐭𝐨 𝐚 m𝐞𝐬𝐬𝐚𝐠𝐞.")
    
    text = message.text.split(None, 1)[1] if len(message.command) > 1 else None
    
    sent = 0
    failed = 0
    m = await message.reply_text("𝐒𝐭𝐚𝐫𝐭𝐢𝐧𝐠 𝐛𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭...")
    
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
                
    await m.edit_text(f"✅ 𝐁𝐫𝐨𝐚𝐝𝐜𝐚𝐬𝐭 𝐃𝐨𝐧𝐞!\n𝐒𝐞𝐧𝐭 𝐭𝐨 {sent} 𝐜𝐡𝐚𝐭𝐬.\n𝐅𝐚𝐢𝐥𝐞𝐝 𝐢𝐧 {failed} 𝐜𝐡𝐚𝐭𝐬.")

# -------- /chatbot Toggle --------
@app.on_message(filters.command("chatbot") & filters.group)
async def chatbot_toggle(client, message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply_text("❗ 𝐎𝐧𝐥𝐲 𝐚𝐝𝐦𝐢𝐧𝐬 𝐚𝐧𝐝 𝐨𝐰𝐧𝐞𝐫 𝐜𝐚𝐧 𝐮𝐬𝐞 𝐭𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝.")
    
    if len(message.command) < 2:
        return await message.reply_text("𝐔𝐬𝐚𝐠𝐞: /𝐜𝐡𝐚𝐭𝐛𝐨𝐭 𝐞𝐧𝐚𝐛𝐥𝐞 𝐨𝐫 /𝐜𝐡𝐚𝐭𝐛𝐨𝐭 𝐝𝐢𝐬𝐚𝐛𝐥𝐞")
        
    mode = message.command[1].lower()
    
    if mode in ["on", "enable"]:
        CHATBOT_STATUS[message.chat.id] = True
        status_text = "enabled"
        await message.reply_text(f"𝐂𝐡𝐚𝐭𝐛𝐨𝐭 𝐬𝐭𝐚𝐭𝐮𝐬 𝐢𝐬 {status_text.upper()} ✰")
    elif mode in ["off", "disable"]:
        CHATBOT_STATUS[message.chat.id] = False
        status_text = "disabled"
        await message.reply_text(f"𝐂𝐡𝐚𝐭𝐛𝐨𝐭 𝐬𝐭𝐚𝐭𝐮𝐬 𝐢𝐬 {status_text.upper()} ✰")
    else:
        return await message.reply_text("𝐔𝐬𝐚𝐠𝐞: /𝐜𝐡𝐚𝐭𝐛𝐨𝐭 𝐞𝐧𝐚𝐛𝐥𝐞 𝐨𝐫 /𝐜𝐡𝐚𝐭𝐛𝐨𝐭 𝐝𝐢𝐬𝐚𝐛𝐥𝐞")
        
    await save_chat_id(message.chat.id, "groups") 

# -------- /tagall Command --------
@app.on_message(filters.command("tagall") & filters.group)
async def tagall_cmd(client, message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply_text("❗ 𝐎𝐧𝐥𝐲 𝐚𝐝𝐦𝐢𝐧𝐬 𝐜𝐚𝐧 𝐮𝐬𝐞 /𝐭𝐚𝐠𝐚𝐥𝐥.")
    
    if not await is_bot_admin(message.chat.id):
        return await message.reply_text("❗ 𝐈 𝐧𝐞𝐞𝐝 𝐚𝐝𝐦𝐢𝐧 𝐩𝐞𝐫𝐦𝐢𝐬𝐬𝐢𝐨𝐧𝐬 (𝐭𝐚𝐠 𝐦𝐞𝐦𝐛𝐞𝐫𝐬) 𝐭𝐨 𝐮𝐬𝐞 𝐭𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝.")

    chat_id = message.chat.id
    
    if TAGGING.get(chat_id):
        return await message.reply_text("❗ 𝐀𝐥𝐫𝐞𝐚𝐝𝐲 𝐭𝐚𝐠𝐠𝐢𝐧𝐠 𝐢𝐧 𝐭𝐡𝐢𝐬 𝐜𝐡𝐚𝐭. 𝐔𝐬𝐞 /𝐬𝐭𝐨𝐩 𝐭𝐨 𝐜𝐚𝐧𝐜𝐞𝐥.")
        
    TAGGING[chat_id] = True
    
    # Get message content
    if len(message.command) > 1:
        msg = message.text.split(None, 1)[1]
    elif message.reply_to_message:
        msg = "𝐓𝐚𝐠𝐠𝐢𝐧𝐠 𝐟𝐫𝐨𝐦 𝐫𝐞𝐩𝐥𝐢𝐞𝐝 m𝐞𝐬𝐬𝐚𝐠𝐞!"
    else:
        msg = "𝐀𝐭𝐭𝐞𝐧𝐭𝐢𝐨𝐧!"
        
    m = await message.reply_text("𝐓𝐚𝐠𝐠𝐢𝐧𝐠 𝐬𝐭𝐚𝐫𝐭𝐞𝐝 !! ♥")
    
    member_list = []
    # Collect all members first
    try:
        async for member in app.get_chat_members(chat_id):
            if not (member.user.is_bot or member.user.is_deleted):
                member_list.append(member.user)
    except Exception:
        TAGGING[chat_id] = False
        return await m.edit_text("🚫 𝐄𝐫𝐫𝐨𝐫 𝐢𝐧 𝐟𝐞𝐭𝐜𝐡𝐢𝐧𝐠 𝐦𝐞𝐦𝐛𝐞𝐫𝐬: 𝐌𝐚𝐲𝐛𝐞 𝐭𝐡𝐢𝐬 𝐠𝐫𝐨𝐮𝐩 𝐢𝐬 𝐭𝐨𝐨 𝐛𝐢𝐠 𝐨𝐫 𝐈 𝐝𝐨𝐧'𝐭 𝐡𝐚𝐯𝐞 𝐩𝐞𝐫𝐦𝐢𝐬𝐬𝐢𝐨𝐧𝐬.")

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
        await m.edit_text("𝐓𝐚𝐠𝐠𝐢𝐧𝐠 𝐜𝐨𝐦𝐩𝐥𝐞𝐭𝐞𝐝 !! ◉‿◉")
        TAGGING[chat_id] = False 

# -------- /stop Tagging --------
@app.on_message(filters.command("stop") & filters.group)
async def stop_tag(client, message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply_text("❗ 𝐎𝐧𝐥𝐲 𝐚𝐝𝐦𝐢𝐧𝐬 𝐜𝐚𝐧 𝐮𝐬𝐞 /𝐬𝐭𝐨𝐩.")
        
    if TAGGING.get(message.chat.id):
        TAGGING[message.chat.id] = False
        await message.reply_text("𝐓𝐚𝐠𝐠𝐢𝐧𝐠 𝐬𝐭𝐨𝐩𝐩𝐞𝐝 !!")
    else:
        await message.reply_text("❗ 𝐍𝐨 𝐭𝐚𝐠𝐠𝐢𝐧𝐠 𝐢𝐬 𝐜𝐮𝐫𝐫𝐞𝐧𝐭𝐥𝐲 𝐫𝐮𝐧𝐧𝐢𝐧𝐠.")

# -------- /couples, /cute, /love Commands --------
@app.on_message(filters.command("couples") & filters.group)
async def couples_cmd(client, message):
    member_list = []
    try:
        async for member in app.get_chat_members(message.chat.id):
            if not (member.user.is_bot or member.user.is_deleted):
                member_list.append(member.user)
    except Exception:
        return await message.reply_text("🚫 𝐂𝐚𝐧𝐧𝐨𝐭 𝐟𝐞𝐭𝐜𝐡 𝐦𝐞𝐦𝐛𝐞𝐫𝐬 𝐝𝐮𝐞 𝐭𝐨 𝐫𝐞𝐬𝐭𝐫𝐢𝐜𝐭𝐢𝐨𝐧𝐬.")

    if len(member_list) < 2:
        return await message.reply_text("❗ 𝐍𝐞𝐞𝐝 𝐚𝐭 𝐥𝐞𝐚𝐬𝐭 𝐭𝐰𝐨 𝐦𝐞𝐦𝐛𝐞𝐫𝐬 𝐭𝐨 𝐟𝐨𝐫𝐦 𝐚 𝐜𝐨𝐮𝐩𝐥𝐞.")
        
    # Pick two random unique members
    couple = random.sample(member_list, 2)
    user1 = couple[0]
    user2 = couple[1]
    
    # Calculate a random love percentage (just for fun)
    love_percent = random.randint(30, 99)
    
    await message.reply_text(
        f"💘 𝐍𝐞𝐰 𝐂𝐨𝐮𝐩𝐥𝐞 𝐨𝐟 𝐭𝐡𝐞 𝐃𝐚𝐲!\n\n"
        f"{user1.first_name} 💖 {user2.first_name}\n"
        f"𝐋𝐨𝐯𝐞 𝐥𝐞𝐯𝐞𝐥 𝐢𝐬 {love_percent}%! 🎉"
    )

@app.on_message(filters.command("cute"))
async def cute_cmd(client, message):
    cute_level = random.randint(30, 99)
    user = message.from_user
    text = f"{user.first_name}'𝐬 𝐜𝐮𝐭𝐞𝐧𝐞𝐬𝐬 𝐥𝐞𝐯𝐞𝐥 𝐢𝐬 {cute_level}% 💖"
    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("𝐒𝐮𝐩𝐩𝐨𝐫𝐭", url=SUPPORT_CHAT)]])
    await message.reply_text(text, reply_markup=buttons)

@app.on_message(filters.command("love"))
async def love_cmd(client, message):
    if len(message.command) < 2 or "+" not in message.text:
        return await message.reply_text("𝐔𝐬𝐚𝐠𝐞: /𝐥𝐨𝐯𝐞 𝐅𝐢𝐫𝐬𝐭 𝐍𝐚𝐦𝐞 + 𝐒𝐞𝐜𝐨𝐧𝐝 𝐍𝐚𝐦𝐞")

    # Split the argument and clean it up
    arg_text = message.text.split(None, 1)[1]
    names = [n.strip() for n in arg_text.split("+") if n.strip()]
    
    if len(names) < 2:
        return await message.reply_text("𝐏𝐥𝐞𝐚𝐬𝐞 𝐩𝐫𝐨𝐯𝐢𝐝𝐞 𝐭𝐰𝐨 𝐧𝐚𝐦𝐞𝐬 𝐬𝐞𝐩𝐚𝐫𝐚𝐭𝐞𝐝 𝐛𝐲 𝐚 '+' (𝐞.𝐠., /𝐥𝐨𝐯𝐞 𝐀𝐥𝐢𝐜𝐞 + 𝐁𝐨𝐛)")
        
    # The rest of the logic is fine
    love_percent = random.randint(1, 100)
    text = f"❤️ 𝐋𝐨𝐯𝐞 𝐏𝐨𝐬𝐬𝐢𝐛𝐢𝐥𝐢𝐭𝐲\n" \
           f"{names[0]} & {names[1]}'𝐬 𝐥𝐨𝐯𝐞 𝐥𝐞𝐯𝐞𝐥 𝐢𝐬 {love_percent}% 😉"
           
    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("𝐒𝐮𝐩𝐩𝐨𝐫𝐭", url=SUPPORT_CHAT)]])
    await message.reply_text(text, reply_markup=buttons) 

# -------- /afk Command --------
@app.on_message(filters.command("afk"))
async def afk_cmd(client, message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    # Check if user is already AFK (meaning they are typing /afk to return)
    if user_id in AFK_USERS:
        # User is coming back
        afk_data = AFK_USERS.pop(user_id)
        time_afk = get_readable_time(int(time.time() - afk_data["time"]))
        await message.reply_text(
            f"𝐘𝐞𝐚𝐡, [{user_name}](tg://user?id={user_id}), 𝐲𝐨𝐮 𝐚𝐫𝐞 𝐛𝐚𝐜𝐤, 𝐨𝐧𝐥𝐢𝐧𝐞! (𝐀𝐅𝐊 𝐟𝐨𝐫: {time_afk}) 😉",
            parse_mode=enums.ParseMode.MARKDOWN
        )
        return # Stop execution after returning
        
    # If user is not AFK, they are setting AFK status
    reason = message.text.split(None, 1)[1] if len(message.command) > 1 else "𝐍𝐨 𝐫𝐞𝐚𝐬𝐨𝐧 𝐠𝐢𝐯𝐞𝐧."
    
    AFK_USERS[user_id] = {"reason": reason, "chat_id": message.chat.id, "username": user_name, "time": time.time()}
    
    # Send the AFK message
    await message.reply_text(
        f"𝐇𝐞𝐲, [{user_name}](tg://user?id={user_id}), 𝐲𝐨𝐮 𝐚𝐫𝐞 𝐀𝐅𝐊! (𝐑𝐞𝐚𝐬𝐨𝐧: {reason})",
        parse_mode=enums.ParseMode.MARKDOWN
    )
    # The automatic "I'm back" message when they send a non-/afk message is handled in group_reply_and_afk_checker 

# -------- /mmf Command (FIXED - Simple reply) --------
@app.on_message(filters.command("mmf") & filters.group)
async def mmf_cmd(client, message):
    # This feature requires complex external tools/logic (e.g., Pillow).
    # Since the full functionality is not implemented, we provide a clean, non-buggy error/status message.
    
    if not message.reply_to_message or not message.reply_to_message.sticker:
        return await message.reply_text("❗ 𝐑𝐞𝐩𝐥𝐲 𝐭𝐨 𝐚 𝐬𝐭𝐢𝐜𝐤𝐞𝐫 𝐚𝐧𝐝 𝐩𝐫𝐨𝐯𝐢𝐝𝐞 𝐭𝐞𝐱𝐭 𝐭𝐨 𝐮𝐬𝐞 𝐭𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝.\n\n*(𝐍𝐨𝐭𝐞: 𝐭𝐡𝐢𝐬 𝐟𝐞𝐚𝐭𝐮𝐫𝐞 𝐢𝐬 𝐜𝐮𝐫𝐫𝐞𝐧𝐭𝐥𝐲 𝐮𝐧𝐝𝐞𝐫 𝐦𝐚𝐢𝐧𝐭𝐞𝐧𝐚𝐧𝐜𝐞)*")
        
    if len(message.command) < 2:
        return await message.reply_text("❗ 𝐏𝐫𝐨𝐯𝐢𝐝𝐞 𝐭𝐡𝐞 𝐭𝐞𝐱𝐭 𝐲𝐨𝐮 𝐰𝐚𝐧𝐭 𝐨𝐧 𝐭𝐡𝐞 𝐬𝐭𝐢𝐜𝐤𝐞𝐫.")
        
    await message.reply_text(
        "❌ 𝐒𝐭𝐢𝐜𝐤𝐞𝐫 𝐓𝐞𝐱𝐭 𝐅𝐞𝐚𝐭𝐮𝐫𝐞 𝐔𝐧𝐚𝐯𝐚𝐢𝐥𝐚𝐛𝐥𝐞\n"
        "𝐏𝐥𝐞𝐚𝐬𝐞 𝐧𝐨𝐭𝐞: 𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐢𝐬 𝐭𝐞𝐦𝐩𝐨𝐫𝐚𝐫𝐢𝐥𝐲 𝐝𝐢𝐬𝐚𝐛𝐥𝐞𝐝 𝐝𝐮𝐞 𝐭𝐨 𝐦𝐢𝐬𝐬𝐢𝐧𝐠 𝐢𝐦𝐚𝐠𝐞 𝐩𝐫𝐨𝐜𝐞𝐬𝐬𝐢𝐧𝐠 𝐥𝐢𝐛𝐫𝐚𝐫𝐢𝐞𝐬. "
        "𝐈 𝐚𝐦 𝐰𝐨𝐫𝐤𝐢𝐧𝐠 𝐨𝐧 𝐢𝐭!"
    ) 

# -------- /staff, /botlist Commands --------
@app.on_message(filters.command("staff") & filters.group)
async def staff_cmd(client, message):
    # Logic confirmed from previous fix
    try:
        admins = [
            admin async for admin in app.get_chat_members(message.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS)
        ]
        
        staff_list = "👑 𝐆𝐫𝐨𝐮𝐩 𝐒𝐭𝐚𝐟𝐟 𝐌𝐞𝐦𝐛𝐞𝐫𝐬:\n"
        for admin in admins:
            if not admin.user.is_bot:
                tag = f"[{admin.user.first_name}](tg://user?id={admin.user.id})"
                status = admin.status.name.replace("_", " ").title()
                staff_list += f"• {tag} ({status})\n"
                
        await message.reply_text(staff_list, disable_web_page_preview=True)
        
    except Exception as e:
        await message.reply_text(f"🚫 𝐄𝐫𝐫𝐨𝐫 𝐢𝐧 𝐟𝐞𝐭𝐜𝐡𝐢𝐧𝐠 𝐬𝐭𝐚𝐟𝐟: {e}")

@app.on_message(filters.command("botlist") & filters.group)
async def botlist_cmd(client, message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply_text("❗ 𝐎𝐧𝐥𝐲 𝐚𝐝𝐦𝐢𝐧𝐬 𝐜𝐚𝐧 𝐮𝐬𝐞 /𝐛𝐨𝐭𝐥𝐢𝐬𝐭.")
        
    # Logic confirmed from previous fix
    try:
        bots = [
            bot async for bot in app.get_chat_members(message.chat.id, filter=enums.ChatMembersFilter.BOTS)
        ]
        
        bot_list = "🤖 𝐁𝐨𝐭𝐬 𝐢𝐧 𝐭𝐡𝐢𝐬 𝐠𝐫𝐨𝐮𝐩:\n"
        for bot in bots:
            tag = f"[{bot.user.first_name}](tg://user?id={bot.user.id})"
            # Ensure username exists before trying to access it
            username_part = f" (@{bot.user.username})" if bot.user.username else ""
            bot_list += f"• {tag}{username_part}\n"
            
        await message.reply_text(bot_list, disable_web_page_preview=True)
        
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

# -------- Private Auto Reply --------
@app.on_message(filters.text & filters.private, group=0)
async def private_reply(client, message):
    await save_chat_id(message.chat.id, "privates")
    reply = get_reply(message.text)
    await message.reply_text(reply)

# -------- Group Auto Reply & AFK Checker --------
@app.on_message(filters.text & filters.group, group=1)
async def group_reply_and_afk_checker(client, message: Message):
    await save_chat_id(message.chat.id, "groups")
    
    # 1. Check if the user sending a regular message is AFK (Coming back)
    # This prevents the double message when they type a message after /afk
    if (message.from_user and 
        message.from_user.id in AFK_USERS and 
        message.text and 
        not message.text.startswith("/afk")):
        
        user_id = message.from_user.id
        
        # Calculate time before deleting
        afk_data = AFK_USERS.pop(user_id) # Remove user from AFK list
        time_afk = get_readable_time(int(time.time() - afk_data["time"]))
        user_name = afk_data["username"]
        
        # Send the "I'm back" message
        await message.reply_text(
            f"𝐘𝐞𝐚𝐡, [{user_name}](tg://user?id={user_id}), 𝐲𝐨𝐮 𝐚𝐫𝐞 𝐛𝐚𝐜𝐤, 𝐨𝐧𝐥𝐢𝐧𝐞! (𝐀𝐅𝐊 𝐟𝐨𝐫: {time_afk}) 😉",
            parse_mode=enums.ParseMode.MARKDOWN
        )
        # Note: We don't return here, as the message might still need to trigger other actions (like AFK tagging)

    # 2. AFK Tag/Reply Check
    users_to_check = []
    
    # Check replied user
    if message.reply_to_message and message.reply_to_message.from_user:
        replied_user_id = message.reply_to_message.from_user.id
        if replied_user_id in AFK_USERS:
            users_to_check.append(replied_user_id)
            
    # Check text mentions
    if message.text and message.entities:
        for entity in message.entities:
            if entity.type == enums.MessageEntityType.TEXT_MENTION and entity.user and entity.user.id in AFK_USERS:
                if entity.user.id not in users_to_check:
                    users_to_check.append(entity.user.id)
                    
    for afk_id in users_to_check:
        afk_data = AFK_USERS.get(afk_id)
        if afk_data:
            user_name = afk_data["username"]
            reason = afk_data["reason"]
            time_afk = get_readable_time(int(time.time() - afk_data["time"]))
            
            await message.reply_text(
                f"⚠️ [{user_name}](tg://user?id={afk_id}) 𝐢𝐬 𝐀𝐅𝐊! ◉‿◉\n"
                f"𝐑𝐞𝐚𝐬𝐨𝐧: *{reason}*\n"
                f"𝐓𝐢𝐦𝐞: *{time_afk}*",
                parse_mode=enums.ParseMode.MARKDOWN
            )
            # Only send one AFK notice per message to avoid spam
            break 
            
    # 3. Chatbot Auto-Reply Logic
    me = await client.get_me()
    
    # CRITICAL: Bot must be an admin to reply (as requested)
    if message.chat.type != enums.ChatType.PRIVATE and not await is_bot_admin(message.chat.id):
        # The bot cannot reply even if CHATBOT_STATUS is True if it's not an admin.
        return 
        
    is_chatbot_on = CHATBOT_STATUS.get(message.chat.id, True)
    is_reply_to_bot = message.reply_to_message and message.reply_to_message.from_user and message.reply_to_message.from_user.id == me.id
    is_direct_mention = message.text and me.username in message.text if me.username else False
    
    if is_chatbot_on:
        if is_reply_to_bot or is_direct_mention:
            # Always reply if the bot is directly addressed
            reply = get_reply(message.text)
            await message.reply_text(reply)
            
        elif random.random() < 0.2: # Low chance (20%) for general group conversation
            # Don't reply if it's a reply to another non-bot user, to avoid conversation hijacking
            is_reply_to_other_user = (
                message.reply_to_message and 
                message.reply_to_message.from_user and 
                message.reply_to_message.from_user.id != me.id and 
                not message.reply_to_message.from_user.is_bot
            )
            
            if not is_reply_to_other_user:
                reply = get_reply(message.text)
                await message.reply_text(reply) 

# -------- Voice Chat Notifications (FIXED) --------
@app.on_message(filters.video_chat_started | filters.video_chat_ended | filters.video_chat_members_invited, group=2)
async def voice_chat_events(client, message):
    # Ensure this only runs in groups/supergroups
    if message.chat.type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        return

    if message.video_chat_started:
        await message.reply_text("🎤 𝐕𝐨𝐢𝐜𝐞 𝐂𝐡𝐚𝐭 𝐒𝐭𝐚𝐫𝐭𝐞𝐝! 𝐓𝐢𝐦𝐞 𝐭𝐨 𝐣𝐨𝐢𝐧!")
        
    elif message.video_chat_ended:
        # Get duration safely
        duration = get_readable_time(message.video_chat_ended.duration) if message.video_chat_ended.duration else "𝐚 𝐬𝐡𝐨𝐫𝐭 𝐭𝐢𝐦𝐞"
        await message.reply_text(f"❌ 𝐕𝐨𝐢𝐜𝐞 𝐂𝐡𝐚𝐭 𝐄𝐧𝐝𝐞𝐝! 𝐈𝐭 𝐥𝐚𝐬𝐭𝐞𝐝 𝐟𝐨𝐫 {duration}.")
        
    elif message.video_chat_members_invited:
        invited_users_count = len(message.video_chat_members_invited.users)
        inviter = message.from_user.mention
        
        # Check if the bot was invited (optional, for specific reply)
        me = await client.get_me()
        if me.id in [u.id for u in message.video_chat_members_invited.users]:
            await message.reply_text(f"📣 𝐇𝐞𝐲 {inviter}, 𝐭𝐡𝐚𝐧𝐤𝐬 𝐟𝐨𝐫 𝐢𝐧𝐯𝐢𝐭𝐢𝐧𝐠 𝐦𝐞 𝐭𝐨 𝐭𝐡𝐞 𝐯𝐨𝐢𝐜𝐞 𝐜𝐡𝐚𝐭!")
        else:
            await message.reply_text(f"🗣️ {inviter} 𝐢𝐧𝐯𝐢𝐭𝐞𝐝 {invited_users_count} 𝐦𝐞𝐦𝐛𝐞𝐫𝐬 𝐭𝐨 𝐭𝐡𝐞 𝐯𝐨𝐢𝐜𝐞 𝐜𝐡𝐚𝐭!") 

# -------- Health Check --------
PORT = int(os.environ.get("PORT", 8080))
class _H(BaseHTTPRequestHandler):
    """Simple HTTP server handler for health checks."""
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
        
def _start_http():
    """Starts the HTTP server in a separate thread."""
    try:
        HTTPServer(("0.0.0.0", PORT), _H).serve_forever()
    except Exception as e:
        print(f"Health check server failed to start: {e}")

# Start the health check server in a background thread
threading.Thread(target=_start_http, daemon=True).start()

print("✅ Advanced Chatbot is running...")
app.run()
