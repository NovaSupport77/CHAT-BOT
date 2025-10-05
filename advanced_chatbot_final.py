import os
import json
import time
import asyncio
import random
from datetime import datetime

from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait

# --- 1. CONFIGURATION AND GLOBAL CONSTANTS ---

# NOTE: Replace these placeholders with your actual values
API_ID = 12345678 # Your API ID
API_HASH = "YOUR_API_HASH" # Your API Hash
BOT_TOKEN = "YOUR_BOT_TOKEN" # Your Bot Token
OWNER_ID = 123456789 # Replace with the developer's Telegram ID
DEVELOPER_HANDLE = "@Your_Developer_Username"
DEVELOPER_USERNAME = "DeveloperName"
SUPPORT_CHAT = "https://t.me/YourSupportChat" # Link to support group
UPDATES_CHANNEL = "https://t.me/YourUpdatesChannel" # Link to updates channel

# File for persistent storage
CHAT_IDS_FILE = "known_chats.json"

# Placeholders for media files (Replace with actual file_ids or URLs)
START_PHOTO = "https://placehold.co/600x400/2563eb/ffffff?text=Start+Image"
PING_PHOTO = "https://placehold.co/600x400/10b981/ffffff?text=Ping+Stats"
DEVELOPER_PHOTO = "https://placehold.co/600x400/f59e0b/ffffff?text=Developer+Info"

# Start time for Uptime calculation
START_TIME = datetime.now()

# Load/Initialize global data structures
try:
    with open(CHAT_IDS_FILE, "r") as f:
        KNOWN_CHATS = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    KNOWN_CHATS = {"groups": [], "privates": []}

# Status dictionary for the chatbot toggle
CHATBOT_STATUS = {}
# Status dictionary for tagall command
TAGGING = {}
# Status dictionary for AFK users
AFK_USERS = {}

# --- 2. TEMPLATES ---

INTRO_TEXT_TEMPLATE = (
    "👋 𝐇ᴇʟʟᴏ, {mention_name}!\n\n"
    "𝐼 𝑎𝑚 𝐀ᴅᴠᴀɴᴄᴇᴅ 𝐁ᴏᴛ, 𝑎 𝑓𝑢𝑙𝑙𝑦 𝑓𝑒𝑎𝑡𝑢𝑟𝑒𝑑 𝑎𝑛𝑑 𝑝𝑜𝑤𝑒𝑟𝑓𝑢𝑙 𝑏𝑜𝑡 𝑏𝑢𝑖𝑙𝑡 𝑓𝑜𝑟 𝑦𝑜𝑢𝑟 𝑐ℎ𝑎𝑡 𝑔𝑟𝑜𝑢𝑝𝑠 𝑎𝑛𝑑 𝑝𝑟𝑖𝑣𝑎𝑡𝑒 𝑢𝑠𝑒.\n\n"
    "✨ **𝐊ᴇʏ 𝐅ᴇᴀᴛᴜʀᴇs**:\n"
    "  ‣ 𝐀𝐮𝐭𝐨𝐦𝐚𝐭𝐢𝐜 𝐂𝐡𝐚𝐭𝐛𝐨𝐭 𝐑𝐞𝐩𝐥𝐢𝐞𝐬.\n"
    "  ‣ 𝐆𝐫𝐨𝐮𝐩 𝐌𝐚𝐧𝐚𝐠𝐞𝐦𝐞𝐧𝐭 𝐓𝐨𝐨𝐥𝐬.\n"
    "  ‣ 𝐅𝐮𝐧 𝐂𝐨𝐦𝐦𝐚𝐧𝐝𝐬 (𝐥𝐢𝐤𝐞 /𝐜𝐨𝐮𝐩𝐥𝐞𝐬, /𝐚𝐟𝐤).\n\n"
    "⚙️ 𝐃𝐞𝐯𝐞𝐥𝐨𝐩𝐞𝐫: @{developer}"
)

ABOUT_TEXT = (
    "✨ 𝐀ʙᴏᴜᴛ 𝐌ᴇ\n\n"
    "𝐼 𝑎𝑚 𝐀ᴅᴠᴀɴᴄᴇᴅ 𝐁ᴏᴛ, 𝑎 𝑏𝑜𝑡 𝑐𝑟𝑒𝑎𝑡𝑒𝑑 𝑡𝑜 𝑘𝑒𝑒𝑝 𝑦𝑜𝑢𝑟 𝑔𝑟𝑜𝑢𝑝𝑠 𝑙𝑖𝑣𝑒𝑙𝑦 𝑎𝑛𝑑 𝑒𝑛𝑔𝑎𝑔𝑒𝑑 𝑡ℎ𝑟𝑜𝑢𝑔ℎ 𝑎𝑢𝑡𝑜𝑚𝑎𝑡𝑖𝑐 𝑐ℎ𝑎𝑡𝑏𝑜𝑡 𝑖𝑛𝑡𝑒𝑟𝑎𝑐𝑡𝑖𝑜𝑛𝑠 𝑎𝑛𝑑 𝑢𝑡𝑖𝑙𝑖𝑡𝑦 𝑐𝑜𝑚𝑚𝑎𝑛𝑑𝑠.\n\n"
    "📚 **𝐓𝐞𝐜𝐡𝐧𝐨𝐥𝐨𝐠𝐲**:\n"
    "  ‣ 𝐋𝐚𝐧𝐠𝐮𝐚𝐠𝐞: 𝐏𝐲𝐭𝐡𝐨𝐧\n"
    "  ‣ 𝐅𝐫𝐚𝐦𝐞𝐰𝐨𝐫𝐤: 𝐏𝐲𝐫𝐨𝐠𝐫𝐚𝐦\n\n"
    "💌 𝐓𝐡𝐚𝐧𝐤𝐬 𝐟𝐨𝐫 𝐮𝐬𝐢𝐧𝐠 𝐦𝐞!"
)

HELP_COMMANDS_TEXT_MAP = {
    "couple": "💘 **𝐂ᴏᴜᴘʟᴇ & 𝐋ᴏᴠᴇ 𝐂ᴏᴍᴍᴀɴᴅs**:\n/couples - Get a random couple of the day.\n/cute - Check your cuteness level.\n/love <Name1> + <Name2> - Check love possibility.",
    "chatbot": "🤖 **𝐂ʜᴀᴛʙᴏᴛ 𝐂ᴏᴍᴍᴀɴᴅs**:\n/chatbot enable - Turn the chatbot ON in the group.\n/chatbot disable - Turn the chatbot OFF in the group.\n*(Chatbot is always ON in private chats.)*",
    "tools": "🛠️ **𝐔ᴛɪʟɪᴛʏ 𝐂ᴏᴍᴍᴀɴᴅs**:\n/id - Get your or replied user's ID.\n/ping - Check bot's response time and uptime.\n/afk <reason> - Set yourself as Away From Keyboard.",
    "games": "🎲 **𝐆ᴀᴍᴇs 𝐂ᴏᴍᴍᴀɴᴅs**:\n/dice - Roll a dice.\n/jackpot - Roll the slot machine.\n/football, /basketball, /bowling - Roll sports dice.",
    "group": "🛡️ **𝐆ʀᴏᴜᴘ 𝐀ᴅᴍɪɴ 𝐂ᴏᴍᴍᴀɴᴅs**:\n/tagall <message> - Tag all members in the group (Admin only).\n/stop - Stop ongoing /tagall.\n/staff - Get a list of all group admins.",
}

# --- 3. CHATBOT DATA AND LOGIC ---

# Placeholder chatbot data
DATA = {
    "hello": ["Hello there! 👋", "Hi! What's up?", "Hey, nice to meet you."],
    "how_are_you": ["I'm a bot, but I'm doing great! How about you?", "Excellent, thanks for asking!"],
    "sticker_cute": ["CAACAgUAAxkBAAEq-BxmT9tA6r9f_o_gYx-t_8v_i5vIqwACgQIAAlnS_gD-hX6fWfX7uBgE",
                     "CAACAgUAAxkBAAEq-B1mT9tWf2k5kU3V3J-9gU4hV7VzcwAC8AIAAqE4sQYp34W5n_mCaxgE"],
    "sticker_anger": ["CAACAgUAAxkBAAEq-CHmT9tlhL-gXgD9Vl3597l0Y-0GAAI1AAYE-qf91c9L5Yg90s8YBA",
                      "CAACAgUAAxkBAAEq-CNmT9tq-3oOqD0y07o1o7-L1B_5qQACrAEAAqE4sQaB34g1qQ40qRgE"],
    "daily": ["That's interesting!", "I see what you mean.", "Tell me more about that."],
}

# Simple keyword matching map (case-insensitive)
KEYWORDS = {
    "hi": "hello",
    "hello": "hello",
    "how are you": "how_are_you",
    "cute": "sticker_cute",
    "love": "sticker_cute",
    "anger": "sticker_anger",
    "abuse": "sticker_anger",
}

# Map to find corresponding text if a sticker fails (simplified, as exact text isn't stored for stickers)
TEXT_TO_STICKER_MAP = {
    "cute": "sticker_cute",
    "anger": "sticker_anger",
}

def get_reply(text: str):
    """
    Decides on a text or sticker reply based on keywords and 70/30 chance.
    Returns (response, is_sticker)
    """
    text_lower = text.lower()
    
    # Check for keywords
    category = "daily"
    for word, cat in KEYWORDS.items():
        if word in text_lower:
            category = cat
            break
            
    possible_replies = DATA.get(category, DATA["daily"])
    
    # 70% chance for sticker if the category is a sticker type
    is_sticker_category = category.startswith("sticker_")
    
    if is_sticker_category and random.randint(1, 100) <= 70:
        return (random.choice(possible_replies), True)
    
    # Otherwise, return text (or 30% of the time for sticker categories)
    if is_sticker_category:
        # Fallback to a text category if sticker chance is missed, using the non-sticker version of the category if available
        text_category = category.replace("sticker_", "")
        text_replies = DATA.get(text_category, DATA["daily"])
        return (random.choice(text_replies), False)
    
    return (random.choice(possible_replies), False)


# --- 4. UTILITY FUNCTIONS ---

def get_readable_time(seconds: int) -> str:
    """Converts seconds into human-readable time format."""
    count = 0
    up_time = ""
    time_list = []
    time_suffix = ["s", "m", "h", "days"]
    
    # Calculate days, hours, minutes, seconds
    
    # Seconds
    time_list.append(seconds % 60)
    seconds //= 60
    
    # Minutes
    time_list.append(seconds % 60)
    seconds //= 60
    
    # Hours
    time_list.append(seconds % 24)
    seconds //= 24
    
    # Days
    time_list.append(seconds)
    
    time_list.reverse()
    
    for x in time_list:
        if x == 0:
            continue
        up_time += f"{x}{time_suffix[count]} "
        count += 1
        
    return up_time.strip() if up_time else "0s"


async def is_admin(chat_id, user_id):
    """Checks if a user is an admin or owner in a group."""
    global app
    if user_id == OWNER_ID:
        return True
    try:
        member = await app.get_chat_member(chat_id, user_id)
        if member.status in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR]:
            return True
    except Exception:
        # Ignore errors like chat not found, etc.
        pass
    return False

async def is_bot_admin(chat_id):
    """Checks if the bot is an admin with required permissions (for tagall: tag members)."""
    global app
    try:
        me = await app.get_me()
        member = await app.get_chat_member(chat_id, me.id)
        if member.status in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR]:
            # Specifically check for can_pin_messages or similar simple right for basic admin status
            # For tagall, we implicitly trust basic admin status for get_chat_members and mention
            return True
    except Exception:
        pass
    return False

async def save_chat_id(chat_id, type_):
    """Saves the chat ID to the known chats list."""
    global KNOWN_CHATS, CHAT_IDS_FILE
    chat_id_str = str(chat_id)

    if chat_id_str not in KNOWN_CHATS[type_]:
        KNOWN_CHATS[type_].append(chat_id_str)
        # Use an executor for file I/O to avoid blocking the event loop
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: json.dump(KNOWN_CHATS, open(CHAT_IDS_FILE, "w"), indent=4))

# Custom filter for checking chatbot status
def is_chatbot_enabled(_, __, message: Message):
    """Returns True if chatbot is enabled for this group. Always True for private chats."""
    # Use global CHATBOT_STATUS
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        # Default is False, so only True if explicitly set to True
        return CHATBOT_STATUS.get(message.chat.id, False)
    return True # Always allow in private chats

# --- 5. MENU BUILDER FUNCTIONS ---
def get_start_buttons(bot_username):
    """Returns the main start button layout."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ 𝐀ᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ 𝐆ʀᴏᴜᴘ ➕", url=f"https://t.me/{bot_username}?startgroup=true")],
        [
            InlineKeyboardButton("ᯓ𝐃ᴇᴠᴇʟᴏρᴇя", user_id=OWNER_ID),
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

# --- 6. HANDLERS AND COMMANDS ---

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
            reply_markup=InlineKeyboardMarkup(buttons_markup_rows),
            parse_mode=enums.ParseMode.MARKDOWN
        )
    elif data == "close":
        await query.message.delete()
    else:
        await query.answer("𝐓ʜɪs ʙᴜᴛᴛᴏɴ ɪs ɴᴏᴛ ʏᴇᴛ 𝐅ᴜɴᴄᴛɪᴏɴᴀʟ.")

# -------- /start Command --------
@app.on_message(filters.command("start"))
async def start_cmd(client, message):
    user = message.from_user
    me = await app.get_me()
    
    if message.chat.type == enums.ChatType.PRIVATE:
        # Ding Dong Animation
        anim_text = "ᴅɪɴɢ...ᴅᴏɴɢ 💥..ʙᴏᴛ ɪs sᴛᴀʀᴛɪɴɢ"
        msg = await message.reply_text("Starting...")
        
        current = ""
        for ch in anim_text:
            current += ch
            try:
                await msg.edit(current)
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except Exception:
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
            parse_mode=enums.ParseMode.MARKDOWN
        )
        await save_chat_id(message.chat.id, "privates")
    else:
        # Group start message
        await message.reply_text(
            f"𝐻𝑒𝑦, [{user.first_name}](tg://user?id={user.id})! 𝐼 𝑎𝑚 𝐀ᴅᴠᴀɴᴄᴇᴅ 𝐁ᴏᴛ. 𝐶𝑙𝑖𝑐𝑘 /help 𝑓𝑜𝑟 𝑚𝑜𝑟𝑒 𝑖𝑛𝑓𝑜.",
            parse_mode=enums.ParseMode.MARKDOWN
        )
        await save_chat_id(message.chat.id, "groups")

# -------- /developer Command --------
@app.on_message(filters.command("developer"))
async def developer_cmd(client, message):
    # Animation
    anim_text = "𝐘ᴏᴜ 𝐖ᴀɳᴛ ᴛᴏ 𝐊ɳᴏᴡ..𝐓ʜɪs 𝐁ᴏᴛ 𝐃ᴇᴠᴇʟᴏᴘᴇʀ 💥."
    m = await message.reply_text("𝐒earching...")
    
    current = ""
    for ch in anim_text:
        current += ch
        try:
            await m.edit(current)
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception:
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
    
    # Get chat ID only if it's a group or supergroup
    chat_id_text = f"\n𝐆ʀᴏᴜᴘ 𝐈𝐃 ➳ {message.chat.id}" if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP] else ""
    
    await message.reply_text(f"👤 {user.first_name}\n𝐔𝐬ᴇʀ 𝐈𝐃 ➳ {user.id}{chat_id_text}")

# -------- /stats Command (Owner Only) --------
@app.on_message(filters.command("stats") & filters.user(OWNER_ID))
async def stats_cmd(client, message):
    await message.reply_text(
        f"📊 𝐁ᴏᴛ 𝐒ᴛᴀᴛs:\n"
        f"👥 𝐆ʀᴏᴜᴘs: {len(KNOWN_CHATS['groups'])}\n"
        f"👤 𝐏ʀɪᴠᴀᴛᴇs: {len(KNOWN_CHATS['privates'])}"
    )

# -------- /broadcast (Owner Only) --------
@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast_cmd(client, message):
    if not (message.reply_to_message or len(message.command) > 1):
        return await message.reply_text("ᴜsᴀɢᴇ: /ʙʀᴏᴀᴅᴄᴀsᴛ ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ.")
    
    # Extract content to broadcast
    if message.reply_to_message:
        content_to_send = message.reply_to_message
        text = None
    elif len(message.command) > 1:
        text = message.text.split(None, 1)[1]
        content_to_send = None
    else:
        return 

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
                    # Use client.copy_message for reliable forwarding/copying
                    await client.copy_message(chat_id, message.chat.id, content_to_send.id)
                elif text:
                    await app.send_message(chat_id, text)
                sent += 1
            except FloodWait as e:
                print(f"FloodWait encountered: {e.value} seconds. Sleeping.")
                await asyncio.sleep(e.value)
                # Try sending again after sleeping
                try:
                    if content_to_send:
                        await client.copy_message(chat_id, message.chat.id, content_to_send.id)
                    elif text:
                        await app.send_message(chat_id, text)
                    sent += 1
                except Exception:
                    failed += 1
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
        
    await save_chat_id(message.chat.id, "groups") # Ensure group is saved if not already

# -------- /tagall Command --------
@app.on_message(filters.command("tagall") & filters.group)
async def tagall_cmd(client, message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply_text("❗ Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ /ᴛᴀɢᴀʟʟ.")
    
    if not await is_bot_admin(message.chat.id):
        return await message.reply_text("❗ 𝐈 ɴᴇᴇᴅ ᴀᴅᴍɪɴ ᴘᴇʀᴍɪssɪᴏɴ (ᴛᴀɢ ᴍᴇᴍʙᴇʀs) ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")

    chat_id = message.chat.id
    
    if TAGGING.get(chat_id):
        return await message.reply_text("❗ 𝐀ʟʀᴇᴀᴅʏ ᴛᴀɢɢɪɴɢ ɪɴ ᴛʜɪs ᴄʜᴀᴛ. 𝐔sᴇ /sᴛᴏᴘ ᴛᴏ ᴄᴀɴᴄᴇʟ.")
        
    TAGGING[chat_id] = True
    
    # Get message content
    if len(message.command) > 1:
        msg = message.text.split(None, 1)[1]
    elif message.reply_to_message and message.reply_to_message.text:
        # Preview of replied message text (max 50 chars)
        msg = f"{message.reply_to_message.text[:50]}{'...' if len(message.reply_to_message.text) > 50 else ''}" 
    else:
        msg = "𝐀ᴛᴛᴇɴᴛɪᴏɴ!"
        
    m = await message.reply_text("𝐓ᴀɢɢɪɴɢ 𝐒ᴛᴀʀᴛᴇᴅ !! ♥")
    
    member_list = []
    # Collect all members first
    try:
        async for member in app.get_chat_members(chat_id):
            if not (member.user.is_bot or member.user.is_deleted):
                member_list.append(member.user)
    except Exception:
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
            # Send the tag chunk
            await app.send_message(chat_id, tag_text, disable_web_page_preview=True, parse_mode=enums.ParseMode.MARKDOWN)
            await asyncio.sleep(2) # Delay to avoid flooding limits
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception:
            continue
            
    # Final message update
    if TAGGING.get(chat_id):
        await m.edit_text("𝐓ᴀɢɢɪɴɢ 𝐂ᴏᴍᴘʟᴇᴛᴇᴅ !! ◉‿◉")
    else:
        # This handles the case where /stop was used
        await m.edit_text("𝐓ᴀɢ𝐠𝐢𝐧𝐠 𝐂𝐚𝐧𝐜𝐞𝐥𝐥𝐞𝐝.")
        
    TAGGING[chat_id] = False

# -------- /stop Tagging --------
@app.on_message(filters.command("stop") & filters.group)
async def stop_tagging_cmd(client, message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply_text("❗ Oɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ /sᴛᴏᴘ.")
        
    if TAGGING.get(message.chat.id):
        TAGGING[message.chat.id] = False # Corrected logic
        await message.reply_text("𝐓ᴀɢɢɪɴɢ 𝐒ᴛᴏᴘᴘᴇᴅ !!")
    else:
        await message.reply_text("❗ 𝐍ᴏ 𝐓ᴀɢɢɪɴɢ ɪs 𝐂ᴜʀʀᴇɴᴛʟʏ 𝐑ᴜɴɴɪɴɢ.")

# -------- /afk Command --------
@app.on_message(filters.command("afk"))
async def afk_cmd(client, message):
    user = message.from_user
    reason = "No reason given."
    if len(message.command) > 1:
        # Use message.text.split(None, 1)[1] to get all text after the command
        reason = message.text.split(None, 1)[1] 

    AFK_USERS[user.id] = {
        "reason": reason,
        "first_name": user.first_name,
        "time": time.time()
    }

    text = f"[{user.first_name}](tg://user?id={user.id}) is 𝐀𝐅𝐊! 💤\n"
    text += f"📝 𝐑𝐞𝐚𝐬𝐨𝐧: *{reason}*"

    await message.reply_text(text, parse_mode=enums.ParseMode.MARKDOWN)

# -------- /couples, /cute, /love Commands --------
@app.on_message(filters.command("couples") & filters.group)
async def couples_cmd(client, message):
    member_list = []
    try:
        # Fetch all non-bot, non-deleted users
        async for member in app.get_chat_members(message.chat.id):
            if not (member.user.is_bot or member.user.is_deleted):
                member_list.append(member.user)
    except Exception:
        return await message.reply_text("🚫 𝐂𝐚𝐧𝐧𝐨𝐭 𝐟𝐞𝐭𝐜𝐡 𝐦𝐞𝐦𝐛𝐞𝐫s. 𝐈 𝐦𝐚𝐲 𝐧𝐨𝐭 𝐡𝐚𝐯𝐞 𝐩𝐞𝐫𝐦𝐢𝐬𝐬𝐢𝐨𝐧s 𝐨𝐫 𝐭𝐡𝐞 𝐠𝐫𝐨𝐮𝐩 𝐢s 𝐭𝐨𝐨 l𝐚𝐫𝐠𝐞.")

    if len(member_list) < 2:
        return await message.reply_text("❗ 𝐍ᴇᴇᴅ ᴀᴛ ʟᴇᴀsᴛ ᴛᴡᴏ ᴍᴇᴍʙᴇʀs ᴛᴏ ғᴏʀᴍ ᴀ 𝐂ᴏᴜᴘ𝐥ᴇ.")
        
    # Pick two random members
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
        return await message.reply_text("𝐏ʟᴇᴀsᴇ ᴘʀᴏ𝐯ɪᴅᴇ ᴛᴡᴏ ɴᴀᴍᴇs sᴇᴘʀᴀᴛᴇᴅ ʙʏ ᴀ '+' (ᴇ.ɢ., /ʟᴏᴠᴇ 𝐀ʟɪᴄᴇ + 𝐁ᴏʙ)")
        
    # Calculate a random love percentage (just for fun)
    love_percent = random.randint(30, 99)

    text = f"❤️ 𝐋ᴏᴠᴇ 𝐏ᴏssɪʙʟɪᴛʏ\n" \
           f"{names[0]} & {names[1]}’𝐬 ʟᴏᴠᴇ ʟᴇᴠᴇʟ ɪs {love_percent}% 😉"
           
    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("𝐒ᴜᴘᴘᴏʀᴛ", url=SUPPORT_CHAT)]])
    await message.reply_text(text, reply_markup=buttons)

# -------- Game Commands --------
@app.on_message(filters.command("dice"))
async def dice_cmd(client, message):
    await message.reply_dice(emoji="🎲")

@app.on_message(filters.command("jackpot"))
async def jackpot_cmd(client, message):
    await message.reply_dice(emoji="🎰")

@app.on_message(filters.command("football"))
async def football_cmd(client, message):
    await message.reply_dice(emoji="⚽")

@app.on_message(filters.command("basketball"))
async def basketball_cmd(client, message):
    await message.reply_dice(emoji="🏀")

@app.on_message(filters.command("bowling"))
async def bowling_cmd(client, message):
    await message.reply_dice(emoji="🎳")
    
# -------- Group Utility Commands --------
@app.on_message(filters.command("staff") & filters.group)
async def staff_cmd(client, message):
    admin_list = []
    owner = None
    try:
        # Fetch administrators only
        async for member in app.get_chat_members(message.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
            if member.user.is_bot:
                continue
            
            if member.status == enums.ChatMemberStatus.OWNER:
                owner = member.user
            elif member.status == enums.ChatMemberStatus.ADMINISTRATOR: 
                admin_list.append(member.user)
    except Exception:
        return await message.reply_text("🚫 𝐈 𝐜𝐚𝐧'𝐭 𝐟𝐞𝐭𝐜𝐡 𝐚𝐝𝐦𝐢𝐧s. 𝐈 𝐦𝐚𝐲 𝐧𝐨𝐭 be 𝐚𝐧 𝐚𝐝𝐦𝐢𝐧 𝐡𝐞𝐫𝐞.")

    if not owner and not admin_list:
        return await message.reply_text("🚫 𝐍𝐨 𝐬𝐭𝐚𝐟𝐟 𝐟𝐨𝐮𝐧𝐝 𝐢𝐧 𝐭𝐡𝐢𝐬 𝐠𝐫𝐨𝐮𝐩.") 

    staff_text = "👑 𝐆ʀᴏᴜᴘ 𝐒ᴛᴀғғ:\n\n"
    if owner:
        staff_text += f"**𝐎ᴡɴᴇʀ**: [{owner.first_name}](tg://user?id={owner.id})\n"
    
    if admin_list:
        staff_text += "\n**𝐀ᴅᴍɪɴs**:\n"
        for admin in admin_list:
            staff_text += f"- [{admin.first_name}](tg://user?id={admin.id})\n"
            
    await message.reply_text(staff_text, parse_mode=enums.ParseMode.MARKDOWN, disable_web_page_preview=True)

# --- 7. CHAT & AFK HANDLERS (The main logic) ---

# 1. AFK Status Check (Must run before chatbot reply)
@app.on_message(filters.text & filters.incoming & ~filters.bot & filters.group)
async def afk_handler(client, message: Message):
    # Check if the user is AFK and is now back (by sending a message)
    user = message.from_user
    if user and user.id in AFK_USERS:
        data = AFK_USERS.pop(user.id)
        uptime = get_readable_time(int(time.time() - data["time"]))
        return await message.reply_text(
            f"𝐖ᴇʟᴄᴏᴍᴇ ʙᴀᴄᴋ, [{user.first_name}](tg://user?id={user.id})! 💖\n"
            f"𝐘ᴏᴜ ᴡᴇʀᴇ ᴀғᴋ ғᴏʀ: **{uptime}**\n"
            f"𝐘ᴏᴜʀ ʀᴇᴀsᴏɴ ᴡᴀs: *{data['reason']}*",
            parse_mode=enums.ParseMode.MARKDOWN
        )

    # Check if an AFK user was tagged (in replies or mentions)
    if message.reply_to_message and message.reply_to_message.from_user and message.reply_to_message.from_user.id in AFK_USERS:
        mentioned_user_id = message.reply_to_message.from_user.id
    elif message.entities:
        # Check through entities for mentions
        mentioned_user_id = next((
            entity.user.id for entity in message.entities 
            if (entity.type == enums.MessageEntityType.TEXT_MENTION or entity.type == enums.MessageEntityType.MENTION) 
            and entity.user and entity.user.id in AFK_USERS
        ), None)
    else:
        mentioned_user_id = None


    if mentioned_user_id and mentioned_user_id in AFK_USERS:
        data = AFK_USERS[mentioned_user_id]
        uptime = get_readable_time(int(time.time() - data["time"]))
        return await message.reply_text(
            f"❗ 𝐀ғᴋ ᴀʟᴇʀᴛ: **{data['first_name']}** is AFK!\n"
            f"⏰ 𝐒ɪɴᴄᴇ: {uptime} ago.\n"
            f"📝 𝐑ᴇᴀsᴏɴ: *{data['reason']}*",
            parse_mode=enums.ParseMode.MARKDOWN
        )


# 2. Chatbot Reply Handler
@app.on_message(filters.text & filters.incoming & is_chatbot_enabled & ~filters.via_bot & ~filters.edited)
async def chatbot_reply_handler(client, message: Message):
    me = await client.get_me()
    text = message.text
    
    # Remove bot mention from text for better keyword matching if present
    if me.username and f"@{me.username.lower()}" in text.lower():
        text = text.replace(f"@{me.username}", "").replace(f"@{me.username.lower()}", "").strip()

    # Condition for reply:
    # 1. Private chat (handled by is_chatbot_enabled returning True)
    # 2. Group chat AND reply to the bot
    # 3. Group chat AND bot is mentioned
    is_private = message.chat.type == enums.ChatType.PRIVATE
    is_reply_to_bot = message.reply_to_message and message.reply_to_message.from_user and message.reply_to_message.from_user.id == me.id
    is_mention = me.username and f"@{me.username.lower()}" in message.text.lower()

    if is_private or is_reply_to_bot or is_mention:
        
        # Get response using the 70/30 logic (Sticker or Text)
        response, is_sticker = get_reply(text)

        try:
            if is_sticker:
                await message.reply_sticker(response)
            else:
                await message.reply_text(response)
        except Exception as e:
            # Fallback to text if sticker sending fails
            print(f"Chatbot failed to send sticker/message: {e}. Falling back to text.")
            
            # Send the text version if the sticker failed or if text sending failed
            if is_sticker:
                # Try to get the corresponding text/default text
                matching_cat = next((cat for word, cat in KEYWORDS.items() if word in text.lower() and not cat.startswith("sticker_")), "daily")
                
                # If it was an 'anger' sticker failure, use the 'daily' text fallback or general text
                text_to_send = random.choice(DATA.get(matching_cat, DATA["daily"]))
                
                await message.reply_text(text_to_send)
            else:
                # If it wasn't a sticker and failed, something else is wrong, but reply the intended text anyway
                await message.reply_text(response)

# --- 8. GROUP ENTRY/EXIT HANDLERS ---

# Welcome Message (Permanent, not deleted)
@app.on_message(filters.new_chat_members & filters.group)
async def welcome_handler(client, message: Message):
    for user in message.new_chat_members:
        # Check if the bot itself was added
        if user.is_self:
            # Bot was added to the group
            await message.reply_text(
                f"**𝐓ʜᴀɴᴋs** ғᴏʀ ᴀᴅᴅɪɴɢ ᴍᴇ ᴛᴏ *{message.chat.title}*! 🎉\n"
                f"I ᴀᴍ ʜᴇʀᴇ ᴛᴏ ᴋᴇᴇᴘ ᴛʜᴇ ᴄʜᴀᴛ ᴀᴄᴛɪᴠᴇ. Use /chatbot enable to activate auto replies.",
                parse_mode=enums.ParseMode.MARKDOWN
            )
            await save_chat_id(message.chat.id, "groups")
        else:
            # New member joined
            mention = f"[{user.first_name}](tg://user?id={user.id})"
            await message.reply_text(
                f"👋 𝐇ᴇʏ, {mention} ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ➳ *{message.chat.title}*! ʜᴀᴠᴇ ᴀ ғᴀɴᴛᴀsᴛɪᴄ ᴅᴀʏ♡.",
                parse_mode=enums.ParseMode.MARKDOWN
            )

# Voice Chat Started Notification
@app.on_message(filters.video_chat_started & filters.group)
async def vc_started_handler(client, message: Message):
    text = f"🎙️ ➳𝐕ᴏɪᴄᴇ 𝐂ʜᴀᴛ 𝐒ᴛᴀʀᴛᴇᴅ! Come join the fun."
    await client.send_message(message.chat.id, text, reply_to_message_id=message.id)

# Voice Chat Ended Notification
@app.on_message(filters.video_chat_ended & filters.group)
async def vc_ended_handler(client, message: Message):
    # Duration is in message.video_chat_ended.duration
    duration = get_readable_time(message.video_chat_ended.duration)
    text = f"❌ ➳𝐕ᴏɪᴄᴇ 𝐂ʜᴀᴛ 𝐄ɴᴅᴇᴅ! \n⏱️ Duration: **{duration}**."
    await client.send_message(message.chat.id, text, parse_mode=enums.ParseMode.MARKDOWN)

# Voice Chat Members Invited Notification
@app.on_message(filters.video_chat_members_invited & filters.group)
async def vc_invited_handler(client, message: Message):
    inviter = message.from_user
    invited_users = message.video_chat_members_invited.users
    
    invited_mentions = ", ".join(
        [f"[{u.first_name}](tg://user?id={u.id})" for u in invited_users]
    )
    
    inviter_mention = f"[{inviter.first_name}](tg://user?id={inviter.id})"
    
    text = (
        f"📣 {inviter_mention} invited the following users to the Voice Chat:\n"
        f"➡️ {invited_mentions}"
    )
    
    await client.send_message(message.chat.id, text, parse_mode=enums.ParseMode.MARKDOWN)


# --- 9. BOT INITIALIZATION ---

# Create the Pyrogram Client instance
app = Client(
    "advanced_chatbot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="handlers") # Optional: Structure if you use external handlers
)

# Start the bot
if __name__ == "__main__":
    print("Bot starting up...")
    app.run()
    print("Bot shut down.")
