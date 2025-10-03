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

# --- FIXED: Sanitized strings to remove problematic Unicode characters ---
INTRO_TEXT_TEMPLATE = (
    "Hey {mention_name}\n"
    "✦ I am an advanced chat bot with some features. \n"
    "✦ Reply in groups & private messages 🥀\n"
    "✦ No abusing & zero downtime\n"
    "✦ Click Help button for commands ❤️\n"
    "❖ Made by...{developer}"
)

ABOUT_TEXT = (
    "❖ A mini chat bot for Telegram groups & private messages\n"
    "● Written in Python \n"
    "● Keep your group active.\n"
    "● Add me now baby in your groups."
)

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
        [InlineKeyboardButton("➕ Add Me To Your Group ➕", url=f"https://t.me/{bot_username}?startgroup=true")],
        [
            InlineKeyboardButton("Owner", user_id=OWNER_ID),
            InlineKeyboardButton("About", callback_data="about")
        ],
        [InlineKeyboardButton("Help & Commands", callback_data="help_main")]
    ])

def get_about_buttons():
    """Returns the About section button layout."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Evara Support Chat", url=SUPPORT_CHAT),
            InlineKeyboardButton("Updates", url=UPDATES_CHANNEL)
        ],
        [
            InlineKeyboardButton("Back", callback_data="start_back"),
            InlineKeyboardButton("Close", callback_data="close")
        ]
    ])

def get_help_main_buttons():
    """Returns the main Help & Commands button layout."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Couple", callback_data="help_couple"),
            InlineKeyboardButton("Chatbot", callback_data="help_chatbot")
        ],
        [
            InlineKeyboardButton("Tools", callback_data="help_tools"),
            InlineKeyboardButton("Games", callback_data="help_games")
        ],
        [InlineKeyboardButton("Group", callback_data="help_group")],
        [
            InlineKeyboardButton("Back", callback_data="start_back"),
            InlineKeyboardButton("Close", callback_data="close")
        ]
    ])

# --- Sub-Help Menu Content ---
HELP_COMMANDS_TEXT_MAP = {
    "couple": (
        "📜 Couple & Love Commands:\n"
        "/couples ~ Choose a random couple\n"
        "/cute ~ Check your cuteness\n"
        "/love name1 + name2 ~ See love possibility\n"
        "\n_All these commands are available to everyone."
    ),
    "chatbot": (
        "📜 Chatbot Command:\n"
        "/chatbot enable/disable ~ Enable/disable chatbot\n"
        "\n"
        "Note: Only works in group and only for admins/owner.\n"
        "Example: /chatbot enable"
    ),
    "tools": (
        "📜 Tools Commands:\n"
        "/id ~ Get user ID (reply or tag)\n"
        "/tagall ~ Tag all members (Admin Only)\n"
        "/stop ~ To stop tagging (Admin Only)\n"
        "/afk reason ~ Away from the keyboard\n"
        "\n_Tagall/Stop requires Admin. Others are for everyone."
    ),
    "games": (
        "📜 Games Commands:\n"
        "/dice ~ Roll a dice\n"
        "/jackpot ~ Jackpot machine\n"
        "/football ~ Play football\n"
        "/basketball ~ Play basketball\n"
        "\n_All these games are available to everyone."
    ),
    "group": (
        "📜 Group Utility Commands:\n"
        "/mmf text ~ Create a sticker with text (Reply to a sticker)\n"
        "/staff ~ Displays group staff members\n"
        "/botlist ~ Check how many bots in your group (Admin Only)"
        "\n_Botlist requires Admin. Others are for everyone."
    )
}

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
            caption="📜 Commands Menu:\n\nChoose a category below:",
            reply_markup=get_help_main_buttons()
        )
    elif data.startswith("help_"):
        category = data.split("_")[1]
        text = HELP_COMMANDS_TEXT_MAP.get(category, "Error: Unknown Category")
        
        # Custom button logic for sub-menus
        buttons = []
        if category in ["couple", "cute", "love"]:
            buttons.append(InlineKeyboardButton("Support", url=SUPPORT_CHAT))
            
        # Ensure buttons is a list of lists for InlineKeyboardMarkup
        buttons_markup_rows = []
        if buttons:
            buttons_markup_rows.append(buttons)
        buttons_markup_rows.append([
            InlineKeyboardButton("Back", callback_data="help_main"),
            InlineKeyboardButton("Close", callback_data="close")
        ])
        
        await query.message.edit_caption(
            caption=text,
            reply_markup=InlineKeyboardMarkup(buttons_markup_rows)
        )
    elif data == "close":
        await query.message.delete()
    else:
        await query.answer("This button is not yet functional.") 

# -------- Commands --------

# -------- /start Command --------
@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    user = message.from_user
    me = await app.get_me()
    developer_link = DEVELOPER_HANDLE.strip('@')
    
    # Ding Dong Animation
    anim_text = "DING...DONG 💥....BOT IS STARTING"
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
    anim_text = "YOU WANT TO KNOW, THIS BOT DEVELOPER 💥..HERE"
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
        [InlineKeyboardButton("Developer ღ", url=f"https://t.me/{DEVELOPER_HANDLE.strip('@')}")]
    ])
    
    caption_text = f"Bot developer is **[{DEVELOPER_USERNAME}](t.me/{DEVELOPER_HANDLE.strip('@')})**"
    
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
    m = await message.reply_text("Pinging...started..´･ᴗ･")
    await asyncio.sleep(0.5)
    await m.edit_text("Ping..Pong ⚡")
    await asyncio.sleep(0.5)
    
    end = time.time()
    ping_ms = round((end-start)*1000)
    uptime_seconds = (datetime.now() - START_TIME).total_seconds()
    uptime_readable = get_readable_time(int(uptime_seconds))
    me = await client.get_me()
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ Add Me ➕", url=f"https://t.me/{me.username}?startgroup=true")],
        [InlineKeyboardButton("Support", url=SUPPORT_CHAT)]
    ])
    
    try:
        await m.delete() # Delete the animation message
    except:
        pass
        
    await message.reply_photo(
        PING_PHOTO,
        caption=f"**Ping** ➳ {ping_ms} ms\n"
                f"**Uptime** ➳ {uptime_readable}",
        reply_markup=buttons
    ) 

# -------- /id Command --------
@app.on_message(filters.command("id"))
async def id_cmd(client, message):
    user = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    await message.reply_text(f"👤 {user.first_name}\n🆔 `{user.id}`")

# -------- /stats Command (Owner Only) --------
@app.on_message(filters.command("stats") & filters.user(OWNER_ID))
async def stats_cmd(client, message):
    await message.reply_text(f"📊 Bot Stats:\n👥 Groups: {len(KNOWN_CHATS['groups'])}\n👤 Privates: {len(KNOWN_CHATS['privates'])}")

# -------- /broadcast (Owner Only) --------
@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast_cmd(client, message):
    if not (message.reply_to_message or len(message.command) > 1):
        return await message.reply_text("Usage: /broadcast or reply to a message.")
    
    text = message.text.split(None, 1)[1] if len(message.command) > 1 else None
    
    sent = 0
    failed = 0
    m = await message.reply_text("Starting broadcast...")
    
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
                
    await m.edit_text(f"✅ Broadcast Done!\nSent to {sent} chats.\nFailed in {failed} chats.")

# -------- /chatbot Toggle --------
@app.on_message(filters.command("chatbot") & filters.group)
async def chatbot_toggle(client, message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply_text("❗ Only admins and owner can use this command.")
    
    if len(message.command) < 2:
        return await message.reply_text("Usage: /chatbot enable or /chatbot disable")
        
    mode = message.command[1].lower()
    
    if mode in ["on", "enable"]:
        CHATBOT_STATUS[message.chat.id] = True
        status_text = "enabled"
        await message.reply_text(f"Chatbot status is {status_text.upper()} ✰")
    elif mode in ["off", "disable"]:
        CHATBOT_STATUS[message.chat.id] = False
        status_text = "disabled"
        await message.reply_text(f"Chatbot status is {status_text.upper()} ✰")
    else:
        return await message.reply_text("Usage: /chatbot enable or /chatbot disable")
        
    await save_chat_id(message.chat.id, "groups") 

# -------- /tagall Command --------
@app.on_message(filters.command("tagall") & filters.group)
async def tagall_cmd(client, message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply_text("❗ Only admins can use /tagall.")
    
    if not await is_bot_admin(message.chat.id):
        return await message.reply_text("❗ I need admin permissions (tag members) to use this command.")

    chat_id = message.chat.id
    
    if TAGGING.get(chat_id):
        return await message.reply_text("❗ Already tagging in this chat. Use /stop to cancel.")
        
    TAGGING[chat_id] = True
    
    # Get message content
    if len(message.command) > 1:
        msg = message.text.split(None, 1)[1]
    elif message.reply_to_message:
        msg = "Tagging from replied message!"
    else:
        msg = "Attention!"
        
    m = await message.reply_text("Tagging started !! ♥")
    
    member_list = []
    # Collect all members first
    try:
        async for member in app.get_chat_members(chat_id):
            if not (member.user.is_bot or member.user.is_deleted):
                member_list.append(member.user)
    except Exception:
        TAGGING[chat_id] = False
        return await m.edit_text("🚫 Error in fetching members: Maybe this group is too big or I don't have permissions.")

    # Start tagging in chunks
    chunk_size = 5
    for i in range(0, len(member_list), chunk_size):
        if not TAGGING.get(chat_id):
            break
            
        chunk = member_list[i:i + chunk_size]
        tag_text = f"**{msg}**\n"
        
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
        await m.edit_text("Tagging completed !! ◉‿◉")
        TAGGING[chat_id] = False 

# -------- /stop Tagging --------
@app.on_message(filters.command("stop") & filters.group)
async def stop_tag(client, message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply_text("❗ Only admins can use /stop.")
        
    if TAGGING.get(message.chat.id):
        TAGGING[message.chat.id] = False
        await message.reply_text("Tagging stopped !!")
    else:
        await message.reply_text("❗ No tagging is currently running.")

# -------- /couples, /cute, /love Commands --------
@app.on_message(filters.command("couples") & filters.group)
async def couples_cmd(client, message):
    member_list = []
    try:
        async for member in app.get_chat_members(message.chat.id):
            if not (member.user.is_bot or member.user.is_deleted):
                member_list.append(member.user)
    except Exception:
        return await message.reply_text("🚫 Cannot fetch members due to restrictions.")

    if len(member_list) < 2:
        return await message.reply_text("❗ Need at least two members to form a couple.")
        
    # Pick two random unique members
    couple = random.sample(member_list, 2)
    user1 = couple[0]
    user2 = couple[1]
    
    # Calculate a random love percentage (just for fun)
    love_percent = random.randint(30, 99)
    
    await message.reply_text(
        f"**💘 New Couple of the Day!**\n\n"
        f"**{user1.first_name}** 💖 **{user2.first_name}**\n"
        f"Love level is **{love_percent}%**! 🎉"
    )

@app.on_message(filters.command("cute"))
async def cute_cmd(client, message):
    cute_level = random.randint(30, 99)
    user = message.from_user
    text = f"{user.first_name}'s cuteness level is {cute_level}% 💖"
    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("Support", url=SUPPORT_CHAT)]])
    await message.reply_text(text, reply_markup=buttons)

@app.on_message(filters.command("love"))
async def love_cmd(client, message):
    if len(message.command) < 2 or "+" not in message.text:
        return await message.reply_text("Usage: /love First Name + Second Name")

    # Split the argument and clean it up
    arg_text = message.text.split(None, 1)[1]
    names = [n.strip() for n in arg_text.split("+") if n.strip()]
    
    if len(names) < 2:
        return await message.reply_text("Please provide two names separated by a '+' (e.g., /love Alice + Bob)")
        
    # The rest of the logic is fine
    love_percent = random.randint(1, 100)
    text = f"**❤️ Love Possibility**\n" \
           f"**{names[0]}** & **{names[1]}**'s love level is **{love_percent}%** 😉"
           
    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("Support", url=SUPPORT_CHAT)]])
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
            f"Yeah, [{user_name}](tg://user?id={user_id}), you are **back**, online! (AFK for: {time_afk}) 😉",
            parse_mode=enums.ParseMode.MARKDOWN
        )
        return # Stop execution after returning
        
    # If user is not AFK, they are setting AFK status
    reason = message.text.split(None, 1)[1] if len(message.command) > 1 else "No reason given."
    
    AFK_USERS[user_id] = {"reason": reason, "chat_id": message.chat.id, "username": user_name, "time": time.time()}
    
    # Send the AFK message
    await message.reply_text(
        f"Hey, [{user_name}](tg://user?id={user_id}), you are **AFK**! (Reason: {reason})",
        parse_mode=enums.ParseMode.MARKDOWN
    )
    # The automatic "I'm back" message when they send a non-/afk message is handled in group_reply_and_afk_checker 

# -------- /mmf Command (FIXED - Simple reply) --------
@app.on_message(filters.command("mmf") & filters.group)
async def mmf_cmd(client, message):
    # This feature requires complex external tools/logic (e.g., Pillow).
    # Since the full functionality is not implemented, we provide a clean, non-buggy error/status message.
    
    if not message.reply_to_message or not message.reply_to_message.sticker:
        return await message.reply_text("❗ Reply to a sticker and provide text to use this command.\n\n*(Note: this feature is currently under maintenance)*")
        
    if len(message.command) < 2:
        return await message.reply_text("❗ Provide the **text** you want on the sticker.")
        
    await message.reply_text(
        "❌ **Sticker Text Feature Unavailable**\n"
        "Please note: This command is temporarily **disabled** due to missing image processing libraries. "
        "I am working on it!"
    ) 

# -------- /staff, /botlist Commands --------
@app.on_message(filters.command("staff") & filters.group)
async def staff_cmd(client, message):
    # Logic confirmed from previous fix
    try:
        admins = [
            admin async for admin in app.get_chat_members(message.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS)
        ]
        
        staff_list = "👑 **Group Staff Members:**\n"
        for admin in admins:
            if not admin.user.is_bot:
                tag = f"[{admin.user.first_name}](tg://user?id={admin.user.id})"
                status = admin.status.name.replace("_", " ").title()
                staff_list += f"• {tag} ({status})\n"
                
        await message.reply_text(staff_list, disable_web_page_preview=True)
        
    except Exception as e:
        await message.reply_text(f"🚫 Error in fetching staff: {e}")

@app.on_message(filters.command("botlist") & filters.group)
async def botlist_cmd(client, message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply_text("❗ Only admins can use /botlist.")
        
    # Logic confirmed from previous fix
    try:
        bots = [
            bot async for bot in app.get_chat_members(message.chat.id, filter=enums.ChatMembersFilter.BOTS)
        ]
        
        bot_list = "🤖 **Bots in this group:**\n"
        for bot in bots:
            tag = f"[{bot.user.first_name}](tg://user?id={bot.user.id})"
            # Ensure username exists before trying to access it
            username_part = f" (@{bot.user.username})" if bot.user.username else ""
            bot_list += f"• {tag}{username_part}\n"
            
        await message.reply_text(bot_list, disable_web_page_preview=True)
        
    except Exception as e:
        # Catch any remaining fetch errors
        await message.reply_text(f"🚫 Error in fetching bot list: {e}") 

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
            f"Yeah, [{user_name}](tg://user?id={user_id}), you are **back**, online! (AFK for: {time_afk}) 😉",
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
                f"⚠️ **[{user_name}](tg://user?id={afk_id}) is AFK**! ◉‿◉\n"
                f"**Reason:** *{reason}*\n"
                f"**Time:** *{time_afk}*",
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
        await message.reply_text("🎤 **Voice Chat Started!** Time to join!")
        
    elif message.video_chat_ended:
        # Get duration safely
        duration = get_readable_time(message.video_chat_ended.duration) if message.video_chat_ended.duration else "a short time"
        await message.reply_text(f"❌ **Voice Chat Ended!** It lasted for {duration}.")
        
    elif message.video_chat_members_invited:
        invited_users_count = len(message.video_chat_members_invited.users)
        inviter = message.from_user.mention
        
        # Check if the bot was invited (optional, for specific reply)
        me = await client.get_me()
        if me.id in [u.id for u in message.video_chat_members_invited.users]:
            await message.reply_text(f"📣 Hey {inviter}, thanks for inviting me to the voice chat!")
        else:
            await message.reply_text(f"🗣️ {inviter} invited **{invited_users_count}** members to the voice chat!") 

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
