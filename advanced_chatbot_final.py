# --- Configuration & Imports ---
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.enums import ChatMemberStatus
import random
import time
import asyncio
import re

# --- REPLACE WITH YOUR ACTUAL DETAILS ---
API_ID = 1234567 
API_HASH = "YOUR_API_HASH" 
BOT_TOKEN = "YOUR_BOT_TOKEN" 

# Bot Owner Details 
OWNER_ID = 7589623332
OWNER_USERNAME = "TheXVoren"
OWNER_MENTION_LINK = f"[Vᴏʀᴇɴ](https://t.me/{OWNER_USERNAME})"

# Support & Update Channels
SUPPORT_CHAT_URL = "https://t.me/Evara_Support_Chat"
UPDATES_CHANNEL_URL = "https://t.me/Evara_Updates"

# Image URLs
START_IMG = "https://iili.io/KVzgS44.jpg"
PING_IMG = "https://iili.io/KVzbu4t.jpg"
DEVLOPER_IMG = "https://iili.io/KVzmgWl.jpg"

# --- Client Initialization ---
app = Client(
    "advanced_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Global variables for state management
start_uptime = time.time() # Bot start time for uptime calculation
AFK_USERS = {} # {user_id: afk_start_time, ...}
TAGGING_STATE = {} # {chat_id: True/False} for tagall
# PLACEHOLDER for database content - Used for /stats command
GLOBAL_STATS = {
    "groups": 150,
    "users": 25000,
    "chats_enabled": 100
}

# --- Utility Functions ---

# 1. Check if the bot is an admin in the group
async def is_bot_admin(chat_id):
    try:
        member = await app.get_chat_member(chat_id, app.me.id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except Exception:
        return False

# 2. Check if a user is admin/owner
async def is_admin_or_owner(chat_id, user_id):
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]
    except Exception:
        return False

# 3. Restrict command to only work if bot is admin
def bot_admin_restrict(func):
    async def wrapper(client, message):
        if message.chat.type != ChatMemberStatus.PRIVATE and not await is_bot_admin(message.chat.id):
            return await message.reply("**⚠️ ɪ ᴀᴍ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ʜᴇʀᴇ!** ᴘʟᴇᴀsᴇ ᴍᴀᴋᴇ ᴍᴇ ᴀᴅᴍɪɴ ᴛᴏ ᴡᴏʀᴋ.")
        await func(client, message)
    return wrapper

# 4. Restrict command to Owner only
def owner_only_restrict(func):
    async def wrapper(client, message):
        if message.from_user.id != OWNER_ID:
            return await message.reply("**🚨 ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪs ᴏɴʟʏ ғᴏʀ ᴍʏ ᴏᴡɴᴇʀ!**")
        await func(client, message)
    return wrapper

# --- Callback Data Constants ---
HOME_CMD = "home_menu"
ABOUT_CMD = "about_menu"
HELP_CMD = "help_menu"
HELP_COUPLE = "help_couples"
HELP_CHATBOT = "help_chatbot"
HELP_TOOLS = "help_tools"
HELP_GAMES = "help_games"
HELP_GROUPS = "help_groups" 
CLOSE_CMD = "close_menu"

# --- Keyboard Markup Definitions ---

# 1. Main Start/Home Keyboard
def home_keyboard(user_id):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(text="+ 𝐀ᴅᴅ ᴍᴇ ʏᴏᴜʀ 𝐆ʀᴏᴜᴘ +", url=f"https://t.me/{app.me.username}?startgroup=true")
        ],
        [
            InlineKeyboardButton(text="ᯓ❍ᴡ𝛈ᴇʀ", user_id=user_id),
            InlineKeyboardButton(text="◉ 𝐀ʙᴏᴜᴛ", callback_data=ABOUT_CMD)
        ],
        [
            InlineKeyboardButton(text="◉ 𝐇ᴇʟᴘ & 𝐂ᴏᴍᴍᴀɴᴅs", callback_data=HELP_CMD)
        ]
    ])

# 2. About Keyboard
def about_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(text="𝐄ᴠᴀʀᴀ 𝐒ᴜᴘᴘᴏʀᴛ 𝐂ʜᴀᴛ", url=SUPPORT_CHAT_URL),
            InlineKeyboardButton(text="𝐔ρ∂ᴀᴛᴇs", url=UPDATES_CHANNEL_URL)
        ],
        [
            InlineKeyboardButton(text="𝐁ᴀᴄᴋ", callback_data=HOME_CMD),
            InlineKeyboardButton(text="𝐂ʟᴏsᴇ", callback_data=CLOSE_CMD)
        ]
    ])

# 3. Help Main Keyboard (2 Rows, 3 Columns)
def help_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(text="ᴄᴏᴜᴘʟᴇ", callback_data=HELP_COUPLE),
            InlineKeyboardButton(text="ᴛᴏᴏʟs", callback_data=HELP_TOOLS),
            InlineKeyboardButton(text="sᴛɪᴄᴋᴇʀs", callback_data=HELP_GROUPS)
        ],
        [
            InlineKeyboardButton(text="ᴄʜᴀᴛʙᴏᴛ", callback_data=HELP_CHATBOT),
            InlineKeyboardButton(text="ɢᴀᴍᴇs", callback_data=HELP_GAMES),
            InlineKeyboardButton(text="ɢʀᴏᴜᴘs", callback_data=HELP_GROUPS)
        ],
        [
            InlineKeyboardButton(text="𝐁ᴀᴄᴋ", callback_data=HOME_CMD),
            InlineKeyboardButton(text="𝐂ʟᴏsᴇ", callback_data=CLOSE_CMD)
        ]
    ])

# 4. Help Sub-Menu Keyboard (Common layout)
def sub_help_keyboard(back_to_menu):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(text="𝐁ᴀᴄᴋ", callback_data=back_to_menu),
            InlineKeyboardButton(text="𝐂ʟᴏsᴇ", callback_data=CLOSE_CMD)
        ]
    ])

# 5. Love/Cute Command Support Button
def support_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(text="sᴜᴘᴘᴏʀᴛ", url=SUPPORT_CHAT_URL)
        ]
    ])

# 6. Ping Command Keyboard
def ping_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(text="+ ᴀᴅᴅ ᴍᴇ +", url=f"https://t.me/{app.me.username}?startgroup=true")
        ],
        [
            InlineKeyboardButton(text="sᴜᴘᴘᴏʀᴛ", url=SUPPORT_CHAT_URL)
        ]
    ])

# 7. Devloper Command Keyboard
def devloper_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(text="𝐃ᴇᴠʟᴏᴘᴇʀ ღ", user_id=OWNER_ID)
        ]
    ])

# --- Text Definitions ---

# Start/Home Text
def get_start_text(user_mention):
    return (
        f"ʜєʏ {user_mention}\n"
        f"**✦ ɪ ᴧϻ ᴧᴅᴠᴧηᴄєᴅ ᴄʜᴧᴛ ʙσᴛ ᴡɪᴛʜ sσϻє ғєᴧᴛᴜʀєs. ✦**\n"
        "✦ ʀєᴘʟʏ ɪη ɢʀσᴜᴘs & ᴘʀɪᴠᴧᴛє🥀\n"
        "✦ ηᴏ ᴧʙᴜsɪηɢ & zєʀσ ᴅσᴡηᴛɪϻє\n"
        "✦ ᴄʟɪᴄᴋ ʜєʟᴘ ʙᴜᴛᴛση ғσʀ ʜєʟᴘs❤️\n"
        f"❖ ϻᴧᴅє ʙʏ...{OWNER_MENTION_LINK}"
    )

# About Text
ABOUT_TEXT = (
    "❖ ᴧ ϻɪηɪ ᴄʜᴧᴛ ʙᴏᴛ ғᴏʀ ᴛᴇʟᴇɢʀᴧϻ ɢʀᴏᴜᴘs & ᴘʀɪᴠᴧᴛᴇ\n"
    "● ᴡʀɪᴛᴛєη ɪη ᴘʏᴛʜᴏɴ**\n"
    "● ᴋєєᴘ ʏσᴜʀ ᴧᴄᴛɪᴠє ɢʀσᴜᴘ.\n"
    "● ᴧᴅᴅ ϻє ηᴏᴡ ʙᴧʙʏ ɪɴ ʏᴏᴜʀ ɢʀσᴜᴘs."
)

# Help Sub-Menu Texts
HELP_COUPLE_TEXT = (
    "**/Couples** `~ ᴄʜᴏᴏsᴇ ᴀ ʀᴀɴᴅᴏᴍ ᴄᴏᴜᴘʟᴇ`\n"
    "**/cute** `~ ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴄᴜᴛᴇɴᴇss`\n"
    "**/love** `~ ɢɪᴠᴇ ᴛᴡᴏ ɴᴀᴍᴇs ᴡɪᴛʜ ᴛʜɪs ғᴏʀᴍᴀᴛ: (Name1) + (Name2) ᴛʜᴇɴ sᴇᴇ ʟᴏᴠᴇ ᴘᴏssɪʙɪʟɪᴛʏ`"
)

HELP_CHATBOT_TEXT = (
    "**/chatbot** `<enable/disable>` `~ ᴇɴᴀʙʟᴇ/ᴅɪsᴀʙʟᴇ ᴄʜᴀᴛʙᴏᴛ`\n\n"
    "**ɴᴏᴛᴇ : ᴏɴʟʏ ᴡᴏʀᴋ ɪɴ ɢʀᴏᴜᴘ !! (Admin/Owner Only)**"
)

HELP_TOOLS_TEXT = (
    "**/id** `~ ɢᴇᴛ ᴜsᴇʀ ɪᴅ (Reply or Tag)`\n"
    "**/tagall** `<text>` `~ ᴛᴀɢ ᴀʟʟ ᴍᴇᴍʙᴇʀs ᴡɪᴛʜ ᴛᴇxᴛ (Admin/Owner Only)`\n"
    "**/stop** `~ ᴛᴏ sᴛᴏᴘ ᴛᴀɢɢɪɴɢ (Admin/Owner Only)`\n"
    "**/afk** `~ ᴀᴡᴀʏ ғʀᴏᴍ ᴛʜᴇ ᴋᴇʏʙᴏᴀʀᴅ`\n"
    "**/stats** `~ sʜᴏᴡs ʙᴏᴛ ɢʟᴏʙᴀʟ sᴛᴀᴛs`"
)

HELP_GAMES_TEXT = (
    "**/dice** `~ ʀᴏʟʟ ᴀ ᴅɪᴄᴇ`\n"
    "**/jackpot** `~ ᴊᴀᴄᴋᴘᴏᴛ ᴍᴀᴄʜɪɴᴇ`\n"
    "**/football** `~ ᴘʟᴀʏ ғᴏᴏᴛʙᴀʟʟ`\n"
    "**/basketball** `~ ᴘʟᴀʏ ʙᴀsᴋᴇᴛʙᴀʟʟ`"
)

HELP_GROUPS_TEXT = (
    "**/staff** `~ ᴅɪsᴘʟᴀʏs ɢʀᴏᴜᴘ sᴛᴀғғ ᴍᴇᴍʙᴇʀs`\n"
    "**/botlist** `~ ᴄʜᴇᴄᴋ ʜᴏᴡ ᴍᴀɴʏ ʙᴏᴛs ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ (Admin/Owner Only)`\n"
    "**/ping** `~ ᴄʜᴇᴄᴋ ʙᴏᴛ ʟᴀᴛᴇɴᴄʏ ᴀɴᴅ ᴜᴘᴛɪᴍᴇ`\n"
    "**Voice Chat Notifications** `~ ʙᴏᴛ ᴀᴜᴛᴏ ᴘᴏsᴛs ᴠᴄ sᴛᴀʀᴛ/ᴇɴᴅ ɴᴏᴛɪғɪᴄᴀᴛɪᴏɴs`"
)

DEVLOPER_TEXT = "ʙᴏᴛ ᴅᴇᴠʟᴏᴘᴇʀ ɪs"

# --- Handler: /start command ---

@app.on_message(filters.command("start"))
@bot_admin_restrict
async def start_command(client, message):
    user_mention = message.from_user.mention
    
    await message.reply_photo(
        photo=START_IMG,
        caption=get_start_text(user_mention),
        reply_markup=home_keyboard(message.from_user.id)
    )

# --- Handler: Callbacks (Button Clicks) ---

@app.on_callback_query()
async def callback_handler(client, query):
    data = query.data
    user_mention = query.from_user.mention
    
    # Check if the chat is a group and the bot is not admin (Only for button interactions)
    if query.message.chat.type != ChatMemberStatus.PRIVATE and not await is_bot_admin(query.message.chat.id):
        return await query.answer("⚠️ I'm not an admin here! Please make me admin to work.", show_alert=True)
    
    # Home Menu
    if data == HOME_CMD:
        await query.message.edit_media(
            media=START_IMG,
            caption=get_start_text(user_mention),
            reply_markup=home_keyboard(query.from_user.id)
        )
    
    # About Menu
    elif data == ABOUT_CMD:
        await query.message.edit_caption(
            caption=ABOUT_TEXT,
            reply_markup=about_keyboard()
        )
        
    # Main Help Menu
    elif data == HELP_CMD:
        await query.message.edit_caption(
            caption="**ᴄʟɪᴄᴋ ᴏɴ ᴀ ʙᴜᴛᴛᴏɴ ᴛᴏ sᴇᴇ ᴄᴏᴍᴍᴀɴᴅs:**",
            reply_markup=help_keyboard()
        )

    # Help Sub-Menus
    elif data == HELP_COUPLE:
        await query.message.edit_caption(caption=HELP_COUPLE_TEXT, reply_markup=sub_help_keyboard(HELP_CMD))
    elif data == HELP_CHATBOT:
        await query.message.edit_caption(caption=HELP_CHATBOT_TEXT, reply_markup=sub_help_keyboard(HELP_CMD))
    elif data == HELP_TOOLS:
        await query.message.edit_caption(caption=HELP_TOOLS_TEXT, reply_markup=sub_help_keyboard(HELP_CMD))
    elif data == HELP_GAMES:
        await query.message.edit_caption(caption=HELP_GAMES_TEXT, reply_markup=sub_help_keyboard(HELP_CMD))
    # Using HELP_GROUPS for both GROUPS and the old STICKERS section
    elif data == HELP_GROUPS or data == "help_stickers": 
        await query.message.edit_caption(caption=HELP_GROUPS_TEXT, reply_markup=sub_help_keyboard(HELP_CMD))
        
    elif data == CLOSE_CMD:
        await query.message.delete()
        
    await query.answer()

# --- Handler: /Devloper command ---

@app.on_message(filters.command("Devloper"))
@bot_admin_restrict
async def devloper_command(client, message):
    await message.reply_photo(
        photo=DEVLOPER_IMG,
        caption=DEVLOPER_TEXT,
        reply_markup=devloper_keyboard()
    )

# --- Admin-Only Command: /tagall ---

@app.on_message(filters.command("tagall") & filters.group)
@bot_admin_restrict
async def tag_all_command(client, message):
    if not await is_admin_or_owner(message.chat.id, message.from_user.id):
        return await message.reply("⚠️ **ᴏɴʟʏ ᴀᴅᴍɪɴs/ᴏᴡɴᴇʀ ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ!**")

    tag_text = message.text.split(maxsplit=1)[1] if len(message.command) > 1 else ""
    
    await message.reply("**𝐓ᴀɢɢɪɴɢ sᴛᴀʀᴛᴇᴅ !! ♥**")
    
    TAGGING_STATE[message.chat.id] = True
    
    try:
        async for member in client.get_chat_members(message.chat.id):
            if not TAGGING_STATE.get(message.chat.id, False):
                await message.reply("**ᴛᴀɢɢɪɴɢ sᴛᴏᴘᴇᴅ !!**")
                return

            if member.user.is_bot:
                continue

            # Tagging Logic
            await app.send_message(
                message.chat.id,
                f"[{member.user.first_name}](tg://user?id={member.user.id}) {tag_text}",
                disable_web_page_preview=True
            )
            await asyncio.sleep(1) # Delay to avoid flood limits
        
        await message.reply("**ᴛᴀɢɢɪɴɢ ᴄᴏᴍᴘʟᴇᴛᴇᴅ !! ◉‿◉**")
    except Exception as e:
        print(f"Tagall Error: {e}")
    finally:
        TAGGING_STATE[message.chat.id] = False

# --- Admin-Only Command: /stop ---

@app.on_message(filters.command("stop") & filters.group)
@bot_admin_restrict
async def stop_tagging_command(client, message):
    if not await is_admin_or_owner(message.chat.id, message.from_user.id):
        return await message.reply("⚠️ **ᴏɴʟʏ ᴀᴅᴍɪɴs/ᴏᴡɴᴇʀ ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ!**")
    
    if TAGGING_STATE.get(message.chat.id, False):
        TAGGING_STATE[message.chat.id] = False
        await message.reply("**ᴛᴀɢɢɪɴɢ sᴛᴏᴘᴇᴅ !!**")
    else:
        await message.reply("ɴᴏ ᴀᴄᴛɪᴠᴇ ᴛᴀɢɢɪɴɢ ᴘʀᴏᴄᴇss ᴛᴏ sᴛᴏᴘ.")

# --- Admin-Only Command: /chatbot ---
# Placeholder: Requires DB for persistence

@app.on_message(filters.command("chatbot") & filters.group)
@bot_admin_restrict
async def chatbot_toggle(client, message):
    if not await is_admin_or_owner(message.chat.id, message.from_user.id):
        return await message.reply("⚠️ **ᴏɴʟʏ ᴀᴅᴍɪɴs/ᴏᴡɴᴇʀ ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ!**")

    if len(message.command) < 2:
        return await message.reply("ᴘʟᴇᴀsᴇ sᴘᴇᴄɪғʏ `enable` ᴏʀ `disable`.")

    status = message.command[1].lower()
    
    if status == "enable":
        # Logic to enable chatbot in database
        await message.reply("**ᴄʜᴀᴛʙᴏᴛ sᴛᴀᴛᴜs ɪs ᴇɴᴀʙʟᴇ ✰**")
    elif status == "disable":
        # Logic to disable chatbot in database
        await message.reply("**ᴄʜᴀᴛʙᴏᴛ sᴛᴀᴛᴜs ɪs ᴅɪsᴀʙʟᴇ ✰**")
    else:
        await message.reply("ɪɴᴠᴀʟɪᴅ ᴏᴘᴛɪᴏɴ. ᴜsᴇ `enable` ᴏʀ `disable`.")

# --- Admin-Only Command: /botlist ---

@app.on_message(filters.command("botlist") & filters.group)
@bot_admin_restrict
async def bot_list_command(client, message):
    if not await is_admin_or_owner(message.chat.id, message.from_user.id):
        return await message.reply("⚠️ **ᴏɴʟʏ ᴀᴅᴍɪɴs/ᴏᴡɴᴇʀ ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ!**")

    bots = []
    async for member in client.get_chat_members(message.chat.id):
        if member.user.is_bot and member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
            bots.append(member.user.mention)
    
    if bots:
        bot_list_text = "🤖 **ᴀᴅᴍɪɴ ʙᴏᴛs ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ:**\n" + "\n".join(bots)
    else:
        bot_list_text = "ɴᴏ ᴀᴅᴍɪɴ ʙᴏᴛs ғᴏᴜɴᴅ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ."
        
    await message.reply(bot_list_text)

# --- Owner-Only Command: /broadcast ---

@app.on_message(filters.command("broadcast") & filters.private) # Broadcast is typically initiated from private chat
@owner_only_restrict
async def broadcast_command(client, message):
    if len(message.command) < 2:
        return await message.reply("**⚠️ ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ʙʀᴏᴀᴅᴄᴀsᴛ.**")
    
    # Placeholder: Replace this with logic to get all chat IDs from your database
    broadcast_msg = message.text.split(maxsplit=1)[1]
    
    # Simulate list of chats from database. In a real bot, this would be fetched from DB.
    chat_ids_to_broadcast = [] 
    
    success_count = 0
    failed_count = 0
    
    # Simulate a broadcst process
    await message.reply(f"**📢 ʙʀᴏᴀᴅᴄᴀsᴛ sᴛᴀʀᴛᴇᴅ ᴛᴏ {len(chat_ids_to_broadcast)} ᴄʜᴀᴛs...**")
    
    # In a real scenario, the bot would iterate over `chat_ids_to_broadcast`
    for chat_id in chat_ids_to_broadcast:
        try:
            await app.send_message(chat_id, broadcast_msg)
            success_count += 1
        except Exception:
            failed_count += 1
            await asyncio.sleep(0.1) # Small delay for flood control
            
    await message.reply(
        f"**✅ ʙʀᴏᴀᴅᴄᴀsᴛ ᴄᴏᴍᴘʟᴇᴛᴇᴅ!**\n"
        f"**sᴜᴄᴄᴇssғᴜʟ:** `{success_count}`\n"
        f"**ғᴀɪʟᴇᴅ:** `{failed_count}`"
    )


# --- General Commands ---

# /stats
@app.on_message(filters.command("stats"))
@bot_admin_restrict
async def bot_stats_command(client, message):
    # This uses the global placeholder. In a real bot, this data would be fetched from the database.
    total_groups = GLOBAL_STATS['groups']
    total_users = GLOBAL_STATS['users']
    chats_enabled = GLOBAL_STATS['chats_enabled']
    
    uptime_seconds = int(time.time() - start_uptime)
    days = uptime_seconds // (24 * 3600)
    hours = (uptime_seconds % (24 * 3600)) // 3600
    minutes = (uptime_seconds % 3600) // 60
    uptime_str = f"{days}d {hours}h {minutes}m"
    
    stats_text = (
        "📊 **ɢʟᴏʙᴀʟ ʙᴏᴛ sᴛᴀᴛɪsᴛɪᴄs**\n\n"
        f"**🌐 ᴛᴏᴛᴀʟ ɢʀᴏᴜᴘs:** `{total_groups}`\n"
        f"**👥 ᴛᴏᴛᴀʟ ᴜsᴇʀs:** `{total_users}`\n"
        f"**💬 ᴄʜᴀᴛʙᴏᴛ ᴇɴᴀʙʟᴇᴅ:** `{chats_enabled}`\n"
        f"**⏳ ᴜᴘᴛɪᴍᴇ:** `{uptime_str}`"
    )
    
    await message.reply(stats_text)


# /id
@app.on_message(filters.command("id"))
@bot_admin_restrict
async def id_command(client, message):
    user = None
    if message.reply_to_message:
        user = message.reply_to_message.from_user
    elif len(message.command) > 1 and message.entities:
        entity = message.entities[1] if len(message.entities) > 1 else None
        if entity and entity.type == "text_mention":
            user = entity.user
    else:
        user = message.from_user
        
    if user:
        await message.reply(f"**ᴜsᴇʀ ɪᴅ:** `{user.id}`\n**ᴄʜᴀᴛ ɪᴅ:** `{message.chat.id}`")
    else:
        await message.reply("ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴏʀ ᴛᴀɢ ᴀ ᴜsᴇʀ ᴛᴏ ɢᴇᴛ ɪᴅ.")

# /staff
@app.on_message(filters.command("staff") & filters.group)
@bot_admin_restrict
async def staff_list_command(client, message):
    staff = []
    async for member in client.get_chat_members(message.chat.id):
        if member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR] and not member.user.is_bot:
            title = member.custom_title if member.custom_title else member.status.name.title()
            staff.append(f"[{member.user.first_name}](tg://user?id={member.user.id}) - *{title}*")
            
    if staff:
        staff_text = "👑 **ɢʀᴏᴜᴘ sᴛᴀғғ ᴍᴇᴍʙᴇʀs:**\n" + "\n".join(staff)
    else:
        staff_text = "ɴᴏ sᴛᴀғғ ᴍᴇᴍʙᴇʀs ғᴏᴜɴᴅ."
        
    await message.reply(staff_text)

# /Couples
@app.on_message(filters.command("Couples") & filters.group)
@bot_admin_restrict
async def couples_command(client, message):
    members = []
    async for member in client.get_chat_members(message.chat.id):
        if not member.user.is_bot:
            members.append(member.user.first_name)
    
    if len(members) < 2:
        return await message.reply("ɴᴇᴇᴅ ᴀᴛ ʟᴇᴀsᴛ ᴛᴡᴏ ɴᴏɴ-ʙᴏᴛ ᴍᴇᴍʙᴇʀs ғᴏʀ ᴀ ᴄᴏᴜᴘʟᴇ.")
        
    couple = random.sample(members, 2)
    
    await message.reply(f"**💖 ɴᴇᴡ ᴄᴏᴜᴘʟᴇ ᴀʟᴇᴇʀᴛ! 💖**\n\n**{couple[0]}** 💘 **{couple[1]}**")

# /cute
@app.on_message(filters.command("cute"))
@bot_admin_restrict
async def cute_command(client, message):
    cute_percent = random.randint(10, 100)
    
    await message.reply(
        f"ʏᴏᴜʀ ᴄᴜᴛɴᴇss ʟᴇᴠᴇʟ ɪs **{cute_percent}%**! 😉",
        reply_markup=support_keyboard()
    )

# /love
@app.on_message(filters.command("love"))
@bot_admin_restrict
async def love_command(client, message):
    if len(message.command) < 2:
        return await message.reply("ᴘʟᴇᴀsᴇ sᴘᴇᴄɪғʏ ᴛʜᴇ ғᴏʀᴍᴀᴛ: `/love Name1 + Name2`")

    names_text = message.text.split(maxsplit=1)[1]
    
    match = re.search(r"(.+)\s*\+\s*(.+)", names_text)
    
    if not match:
        return await message.reply("ɪɴᴠᴀʟɪᴅ ғᴏʀᴍᴀᴛ. ᴜsᴇ: `/love Name1 + Name2`")
        
    name1 = match.group(1).strip()
    name2 = match.group(2).strip()
    
    love_percent = random.randint(10, 100)
    
    await message.reply(
        f"**{name1}** 💗 **{name2}**\n\n"
        f"ʟᴏᴠᴇ ᴘᴏssɪʙɪʟɪᴛʏ ɪs **{love_percent}%**! 😉",
        reply_markup=support_keyboard()
    )

# --- Games Commands (Telegram's built-in games) ---

@app.on_message(filters.command("dice"))
@bot_admin_restrict
async def dice_command(client, message):
    await client.send_dice(message.chat.id)

@app.on_message(filters.command("jackpot"))
@bot_admin_restrict
async def jackpot_command(client, message):
    await client.send_dice(message.chat.id, emoji="🎰")

@app.on_message(filters.command("football"))
@bot_admin_restrict
async def football_command(client, message):
    await client.send_dice(message.chat.id, emoji="⚽")

@app.on_message(filters.command("basketball"))
@bot_admin_restrict
async def basketball_command(client, message):
    await client.send_dice(message.chat.id, emoji="🏀")

# --- Voice Chat Notifications ---

@app.on_voice_chat_started()
@bot_admin_restrict
async def vc_started_handler(client, message):
    await app.send_message(
        message.chat.id,
        f"**🎙️ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ sᴛᴀʀᴛᴇᴅ!**\n\n"
        f"**sᴛᴀʀᴛᴇᴅ ʙʏ:** {message.from_user.mention if message.from_user else 'ᴀɴ ᴀᴅᴍɪɴ'}"
    )

@app.on_voice_chat_ended()
@bot_admin_restrict
async def vc_ended_handler(client, message):
    # Pyrogram doesn't explicitly give 'duration' on voice_chat_ended for older versions,
    # but the logic for a simple notification is here.
    await app.send_message(
        message.chat.id,
        "**🛑 ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴇɴᴅᴇᴅ!**\n\n"
        "ᴛʜᴀɴᴋs ғᴏʀ ᴊᴏɪɴɪɴɢ. ᴄᴏᴍᴇ ʙᴀᴄᴋ sᴏᴏɴ!"
    )

@app.on_voice_chat_members_invited()
@bot_admin_restrict
async def vc_member_invited_handler(client, message):
    # Only useful if the bot is the inviter, but good for demonstrating the filter
    invited_users = [user.mention for user in message.users]
    if invited_users:
        await app.send_message(
            message.chat.id,
            f"**📢 ᴜsᴇʀs ɪɴᴠɪᴛᴇᴅ ᴛᴏ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ:** {', '.join(invited_users)}"
        )


# --- /afk (Away From Keyboard) ---

@app.on_message(filters.command("afk"))
@bot_admin_restrict
async def afk_command(client, message):
    user_id = message.from_user.id
    # Use full name if username is not available
    username_display = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
    
    AFK_USERS[user_id] = time.time()
    
    await message.reply(f"ʜᴇʏ, **{username_display}**, ʏᴏᴜ ᴀʀᴇ ᴀғᴋ !!")

@app.on_message(filters.text & filters.group, group=1)
async def afk_detector(client, message):
    user_id = message.from_user.id
    
    # 1. User is Back from AFK
    if user_id in AFK_USERS:
        del AFK_USERS[user_id]
        return await message.reply("ʏᴇᴀʜ, ʏᴏᴜ ᴀʀᴇ ʙᴀᴄᴋ, ᴏɴʟɪɴᴇ !! 😉")
    
    # 2. Check if a tagged user is AFK
    if message.entities:
        for entity in message.entities:
            tagged_user_id = None
            
            if entity.type == ChatMemberStatus.TEXT_MENTION:
                tagged_user_id = entity.user.id
            
            # Additional check for username mention, though getting ID directly requires more complex logic.
            # We stick to TEXT_MENTION for reliable ID.
                
            if tagged_user_id and tagged_user_id in AFK_USERS:
                await message.reply("ᴛʜɪs ᴜsᴇʀ ɪs ᴀғᴋ !! ◉‿◉")
                return

# --- /ping command ---

@app.on_message(filters.command("ping"))
@bot_admin_restrict
async def ping_command(client, message):
    initial_time = time.time()
    
    # 1. Pinging... Animation
    ping_msg = await message.reply("ᴘɪɴɢɪɴɢ...sᴛᴀʀᴇᴅ..´･ᴗ･`")
    await asyncio.sleep(0.5)
    await ping_msg.edit_text("ᴘɪɴɢ..ᴘᴏɴɢ ⚡")
    await asyncio.sleep(0.5)
    
    # 2. Calculate Ping and Uptime
    end_time = time.time()
    ping_time = round((end_time - initial_time) * 1000, 2)
    
    # Uptime calculation
    global start_uptime
    uptime_seconds = int(time.time() - start_uptime)
    days = uptime_seconds // (24 * 3600)
    hours = (uptime_seconds % (24 * 3600)) // 3600
    minutes = (uptime_seconds % 3600) // 60
    uptime_str = f"{days}d {hours}h {minutes}m"
    
    # 3. Final Result
    final_text = (
        f"**ᴘɪɴɢ** ➳ `{ping_time}ms`\n"
        f"**ᴜᴘᴛɪᴍᴇ** ➳ `{uptime_str}`"
    )
    
    # Send the final message with the photo
    await ping_msg.delete() 
    
    await message.reply_photo(
        photo=PING_IMG,
        caption=final_text,
        reply_markup=ping_keyboard()
    )


# --- Start Bot ---

if __name__ == "__main__":
    print("Bot is starting...")
    app.run()
