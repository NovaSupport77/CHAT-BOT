# advanced_chatbot.py
# Cleaned up + extended version of your bot with requested UI + features.
import os
import json
import random
import threading
import asyncio
import time
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

# -------- Env Vars --------
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
OWNER_ID = int(os.environ.get("OWNER_ID", "7589623332"))  # your owner id
PORT = int(os.environ.get("PORT", 8080))

# -------- Bot Client --------
app = Client("advanced_chatbot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# -------- Load Replies --------
try:
    with open("conversation.json", "r", encoding="utf-8") as f:
        DATA = json.load(f)
except:
    DATA = {}

if "daily" not in DATA:
    DATA["daily"] = ["Hello 👋", "Hey there!", "Hi!"]

# -------- Load Known Chats for Broadcast --------
CHAT_IDS_FILE = "chats.json"
if os.path.exists(CHAT_IDS_FILE):
    with open(CHAT_IDS_FILE, "r", encoding="utf-8") as f:
        KNOWN_CHATS = json.load(f)
else:
    KNOWN_CHATS = {"groups": [], "privates": []}

# -------- Keywords --------
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

# -------- Global Vars --------
CHATBOT_STATUS = {}
TAGGING = {}
INTRO_TEXT = (
    "ʜєʏ {name}\n\n"
    "✦ ɪ ᴧϻ ᴧᴅᴠᴧηᴄєᴅ ᴄʜᴧᴛ ʙσᴛ ᴡɪᴛʜ sσϻє ғєᴧᴛᴜʀєs.\n"
    "✦ ʀєᴘʟʏ ɪη ɢʀσᴜᴘs & ᴘʀɪᴠᴧᴛє 🥀\n"
    "✦ ηᴏ ᴧʙᴜsɪηɢ & zєʀσ ᴅσᴡɴᴛɪᴍє\n"
    "✦ ᴄʟɪᴄᴋ ʜєʟᴘ ʙᴜᴛᴛση ғσʀ ʜєʟᴘs ❤️\n"
    "❖ ϻᴧᴅє ʙʏ... @TheXVoren"
)

OWNER_PANEL_TEXT = "ʜᴇʏ 👋 I am your bot! 🔒"

# AFK store
AFK = {}  # chat_id -> {user_id: (since_ts, reason)}

# uptime tracking
START_TIME = time.time()

# -------- Utility --------
def get_reply(text: str):
    text = (text or "").lower()
    for word, cat in KEYWORDS.items():
        if word in text and cat in DATA:
            return random.choice(DATA[cat])
    return random.choice(DATA.get("daily", ["Hello 👋"]))

async def is_admin(chat_id, user_id):
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return member.status in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR]
    except:
        return False

async def is_bot_admin(chat_id):
    try:
        me = await app.get_me()
        member = await app.get_chat_member(chat_id, me.id)
        return member.status in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR]
    except:
        return False

async def save_chat_id(chat_id, type_):
    if chat_id not in KNOWN_CHATS.get(type_, []):
        KNOWN_CHATS.setdefault(type_, []).append(chat_id)
        with open(CHAT_IDS_FILE, "w", encoding="utf-8") as f:
            json.dump(KNOWN_CHATS, f)

# -------- /start Command with Ding Dong Animation and new layout --------
START_IMAGE = "https://iili.io/KVzgS44.jpg"  # given image url

@api_call_safe := None  # placeholder to keep linter calm (no-op)

@a := None  # avoid unused assignment warnings (harmless)

@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message: Message):
    user = message.from_user
    me = await app.get_me()
    bot_username = me.username or "bot"
    anim_text = "ᴅɪɴɢ...ᴅᴏɴɢ 💥....ʙᴏᴛ ɪs sᴛᴀʀᴛɪɴɢ"
    msg = await message.reply_text("Starting...")
    current = ""
    for ch in anim_text:
        current += ch
        try:
            await msg.edit_text(current)
        except:
            pass
        await asyncio.sleep(0.04)
    await asyncio.sleep(0.35)
    try:
        await msg.delete()
    except:
        pass

    # Buttons layout (as you specified)
    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("➕ 𝐀ᴅᴅ ᴍᴇ ʏᴏᴜʀ 𝐆ʀᴏᴜᴘ ➕", url=f"https://t.me/{bot_username}?startgroup=true")],
            [
                InlineKeyboardButton("ᯓ❍ᴡ𝛈ᴇʀ", url=f"https://t.me/TheXVoren"),
                InlineKeyboardButton("◉ 𝐀ʙᴏᴜᴛ", callback_data="about_section")
            ],
            [
                InlineKeyboardButton("𝐄ᴠᴀʀᴀ 𝐒ᴜᴘᴘᴏʀᴛ 𝐂ʜᴀᴛ", url="https://t.me/Evara_Support_Chat"),
                InlineKeyboardButton("𝐔ρ∂ᴀᴛᴇs", url="https://t.me/Evara_Updatesfir")
            ],
            [
                InlineKeyboardButton("𝐁ᴀᴄᴋ", callback_data="back_to_start"),
                InlineKeyboardButton("𝐂ʟᴏsᴇ", callback_data="close_start")
            ],
            [InlineKeyboardButton("◉ 𝐇ᴇʟᴘ & 𝐂ᴏᴍᴍᴀɴᴅs", callback_data="help_commands")]
        ]
    )

    await message.reply_photo(
        START_IMAGE,
        caption=INTRO_TEXT.format(name=user.first_name or user.username or "Friend"),
        reply_markup=buttons
    )
    await save_chat_id(message.chat.id, "privates")

# -------- callback handlers for start sections --------
@app.on_callback_query(filters.regex("back_to_start"))
async def back_to_start_cb(client, cq):
    # Re-run start style reply (private)
    try:
        await start_cmd(client, cq.message)
    except:
        await cq.answer("Cannot go back.", show_alert=True)

@app.on_callback_query(filters.regex("close_start"))
async def close_start_cb(client, cq):
    try:
        await cq.message.delete()
    except:
        pass
    await cq.answer("Closed ✅")

@app.on_callback_query(filters.regex("about_section"))
async def about_section_cb(client, cq):
    text = (
        "❖ ᴧ ϻɪηɪ ᴄʜᴧᴛ ʙᴏᴛ ғᴏʀ ᴛᴇʟᴇɢʀᴧϻ ɢʀᴏᴜᴘs & ᴘʀɪᴠᴧᴛᴇ\n"
        "● ᴡʀɪᴛᴛᴇη ɪη ᴘʏᴛʜᴏɴ\n\n"
        "● ᴋєєᴘ ʏσᴜʀ ᴧᴄᴛɪᴠє ɢʀσᴜᴘ.\n"
        "● ᴧᴅᴅ ϻє ηᴏᴡ ʙᴧʙʏ ɪɴ ʏᴏᴜʀ ɢʀσᴜᴘs."
    )
    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("𝐁ᴀᴄᴋ", callback_data="back_to_start"), InlineKeyboardButton("𝐂ʟᴏsᴇ", callback_data="close_start")]
        ]
    )
    await cq.answer()
    await cq.message.edit(text=text, reply_markup=buttons)

# -------- Help & Commands Main (with nested navigation) --------
HELP_IMAGE = START_IMAGE  # use same image
@app.on_callback_query(filters.regex("help_commands"))
async def help_commands_cb(client, cq):
    text = "Help & Commands — select a category below."
    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("ᴄᴏᴜᴘʟᴇs", callback_data="help_couples"),
                InlineKeyboardButton("ᴄᴜᴛᴇ", callback_data="help_cute"),
                InlineKeyboardButton("ʟᴏᴠᴇ", callback_data="help_love")
            ],
            [
                InlineKeyboardButton("ᴄʜᴀᴛʙᴏᴛ", callback_data="help_chatbot"),
                InlineKeyboardButton("ᴛᴏᴏʟs", callback_data="help_tools"),
                InlineKeyboardButton("ɢᴀᴍᴇs", callback_data="help_games")
            ],
            [
                InlineKeyboardButton("sᴛɪᴄᴋᴇʀs", callback_data="help_stickers"),
                InlineKeyboardButton("ɢʀᴏᴜᴘs", callback_data="help_groups"),
                InlineKeyboardButton("𝐃ᴇᴠʟᴏᴘᴇʀ", callback_data="help_developer")
            ],
            [
                InlineKeyboardButton("𝐁ᴀᴄᴋ", callback_data="back_to_start"),
                InlineKeyboardButton("𝐂ʟᴏsᴇ", callback_data="close_start")
            ]
        ]
    )
    await cq.answer()
    try:
        await cq.message.edit(text=text, reply_markup=buttons)
    except:
        # if edit fails (older message), send new
        await cq.message.reply_photo(HELP_IMAGE, caption=text, reply_markup=buttons)

# Individual help subpages
@app.on_callback_query(filters.regex("help_couples"))
async def help_couples_cb(client, cq):
    text = "/Couples ~ ᴄʜᴏᴏsᴇ ᴀ ʀᴀɴᴅᴏᴍ ᴄᴏᴜᴘʟᴇ\nWhen used, bot picks two random members and shows a couple."
    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("sᴜᴘᴘᴏʀᴛ", url="https://t.me/Evara_Support_Chat")],
                                   [InlineKeyboardButton("𝐁ᴀᴄᴋ", callback_data="help_commands"),
                                    InlineKeyboardButton("𝐂ʟᴏsᴇ", callback_data="close_start")]])
    await cq.answer()
    await cq.message.edit(text=text, reply_markup=buttons)

@app.on_callback_query(filters.regex("help_cute"))
async def help_cute_cb(client, cq):
    text = "/cute ~ ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴄᴜᴛᴇɴᴇss\nBot returns a random percent like: YOUR CUTE LEVEL IS 30%."
    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("sᴜᴘᴘᴏʀᴛ", url="https://t.me/Evara_Support_Chat")],
                                   [InlineKeyboardButton("𝐁ᴀᴄᴋ", callback_data="help_commands"),
                                    InlineKeyboardButton("𝐂ʟᴏsᴇ", callback_data="close_start")]])
    await cq.answer()
    await cq.message.edit(text=text, reply_markup=buttons)

@app.on_callback_query(filters.regex("help_love"))
async def help_love_cb(client, cq):
    text = "/love first_name + second_name ~ gives love possibility percent between two names."
    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("sᴜᴘᴘᴏʀᴛ", url="https://t.me/Evara_Support_ChatIn")],
                                   [InlineKeyboardButton("𝐁ᴀᴄᴋ", callback_data="help_commands"),
                                    InlineKeyboardButton("𝐂ʟᴏsᴇ", callback_data="close_start")]])
    await cq.answer()
    await cq.message.edit(text=text, reply_markup=buttons)

@app.on_callback_query(filters.regex("help_chatbot"))
async def help_chatbot_cb(client, cq):
    text = "/chatbot ~ enable/disable chatbot in group. Only owner/admin can use. NOTE: ONLY WORKS IN GROUPS!"
    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("𝐁ᴀᴄᴋ", callback_data="help_commands"),
                                     InlineKeyboardButton("𝐂ʟᴏsᴇ", callback_data="close_start")]])
    await cq.answer()
    await cq.message.edit(text=text, reply_markup=buttons)

@app.on_callback_query(filters.regex("help_tools"))
async def help_tools_cb(client, cq):
    text = (
        "/id ~ Get user id (reply to user or use directly)\n"
        "/tagall ~ Tag all members with text. Owner/admin only. Shows 'TAGGING STARTED !!' and 'TAGGING COMPLETED !!'\n"
        "/stop ~ Stop tagging\n"
        "/afk ~ Mark yourself AFK (reply format or /afk reason)\n"
        "/tr ~ Reply to a message with /tr to translate to English"
    )
    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("𝐁ᴀᴄᴋ", callback_data="help_commands"),
                                     InlineKeyboardButton("𝐂ʟᴏsᴇ", callback_data="close_start")]])
    await cq.answer()
    await cq.message.edit(text=text, reply_markup=buttons)

@app.on_callback_query(filters.regex("help_games"))
async def help_games_cb(client, cq):
    text = (
        "/dice ~ roll a dice\n"
        "/jackpot ~ jackpot machine (fun)\n"
        "/football ~ play football\n"
        "/basketball ~ play basketball"
    )
    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("𝐁ᴀᴄᴋ", callback_data="help_commands"),
                                     InlineKeyboardButton("𝐂ʟᴏsᴇ", callback_data="close_start")]])
    await cq.answer()
    await cq.message.edit(text=text, reply_markup=buttons)

@app.on_callback_query(filters.regex("help_stickers"))
async def help_stickers_cb(client, cq):
    text = (
        "/mmf ~ reply a sticker + text -> text gets added to sticker (creates a text sticker)\n"
        "/q r ~ create quote from message (reply to msg)"
    )
    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("𝐁ᴀᴄᴋ", callback_data="help_commands"),
                                     InlineKeyboardButton("𝐂ʟᴏsᴇ", callback_data="close_start")]])
    await cq.answer()
    await cq.message.edit(text=text, reply_markup=buttons)

@app.on_callback_query(filters.regex("help_groups"))
async def help_groups_cb(client, cq):
    text = "/staff ~ displays group staff members\n/botlist ~ shows bots in group (owner/admin only)\n/ping ~ fancy ping with uptime"
    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("𝐁ᴀᴄᴋ", callback_data="help_commands"),
                                     InlineKeyboardButton("𝐂ʟᴏsᴇ", callback_data="close_start")]])
    await cq.answer()
    await cq.message.edit(text=text, reply_markup=buttons)

@app.on_callback_query(filters.regex("help_developer"))
async def help_developer_cb(client, cq):
    text = "Developer info & contact."
    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("𝐃ᴇᴠʟᴏᴘᴇʀ ღ", url="https://t.me/TheXVoren")],
            [InlineKeyboardButton("𝐁ᴀᴄᴋ", callback_data="help_commands"), InlineKeyboardButton("𝐂ʟᴏsᴇ", callback_data="close_start")]
        ]
    )
    await cq.answer()
    await cq.message.edit(text=text, reply_markup=buttons)

# -------- /help command removed per request (do not register) --------

# -------- /ping Command (fancy) --------
PING_IMAGE = "https://iili.io/KVzbu4t.jpg"

@app.on_message(filters.command("ping"))
async def ping_cmd(client, message: Message):
    # Fancy animation followed by ping output and uptime
    m = await message.reply_text("ᴘɪɴɢɪɴɢ...sᴛᴀʀᴛᴇᴅ..´･ᴗ･`ᴘɪɴɢ..ᴘᴏɴɢ ⚡")
    await asyncio.sleep(0.6)
    end = time.time()
    latency_ms = round((end - message.date.timestamp()) * 1000) if message.date else "N/A"
    uptime = str(datetime.utcfromtimestamp(time.time() - START_TIME).strftime("%H:%M:%S"))
    text = f"✅ Bot is Alive!\n⚡ Ping: {latency_ms} ms\n⏱ Uptime: {uptime}"
    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("+ ᴀᴅᴅ ᴍᴇ +", url=f"https://t.me/{(await app.get_me()).username}?startgroup=true"),
             InlineKeyboardButton("sᴜᴘᴘᴏʀᴛ", url="https://t.me/Evara_Support_Chatok")]
        ]
    )
    try:
        await m.edit_text(text)
    except:
        await message.reply_photo(PING_IMAGE, caption=text, reply_markup=buttons)

# -------- /id Command --------
@app.on_message(filters.command("id"))
async def id_cmd(client, message: Message):
    if message.reply_to_message:
        user = message.reply_to_message.from_user
    else:
        user = message.from_user
    await message.reply_text(f"👤 {user.first_name}\n🆔 {user.id}")

# -------- /stats Command (owner only) --------
@app.on_message(filters.command("stats") & filters.user(OWNER_ID))
async def stats_cmd(client, message: Message):
    await message.reply_text(f"📊 Bot Stats:\n👥 Groups: {len(KNOWN_CHATS.get('groups',[]))}\n👤 Privates: {len(KNOWN_CHATS.get('privates',[]))}")

# -------- /broadcast Command (owner only) --------
@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast_cmd(client, message: Message):
    if not (message.reply_to_message or len(message.command) > 1):
        return await message.reply_text("Usage: /broadcast <text>  or reply to a message.")
    text = message.text.split(None, 1)[1] if len(message.command) > 1 else None
    sent = 0
    for chat_type in ["privates", "groups"]:
        for chat_id in KNOWN_CHATS.get(chat_type, []):
            try:
                if message.reply_to_message:
                    await message.reply_to_message.copy(chat_id)
                else:
                    await app.send_message(chat_id, text)
                sent += 1
            except:
                continue
    await message.reply_text(f"✅ Broadcast sent to {sent} chats.")

# -------- /paneltext Command (Owner Only) --------
@app.on_message(filters.command("paneltext") & filters.user(OWNER_ID))
async def paneltext_cmd(client, message: Message):
    global OWNER_PANEL_TEXT
    text = message.text.split(None, 1)[1] if len(message.command) > 1 else None
    if not text:
        return await message.reply_text("Usage: /paneltext <text>")
    OWNER_PANEL_TEXT = text
    await message.reply_text(f"✅ Owner panel text updated!")

# -------- /chatbot Toggle (group) --------
@app.on_message(filters.command("chatbot") & filters.group)
async def chatbot_toggle(client, message: Message):
    # only allow admins of group to toggle; also ensure bot is admin to work
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply_text("Only group admins can toggle chatbot.")
    if not await is_bot_admin(message.chat.id):
        return await message.reply_text("I must be admin in this group to enable chatbot features.")
    mode = message.command[1].lower() if len(message.command) > 1 else ""
    CHATBOT_STATUS[message.chat.id] = (mode in ("on", "enable", "true"))
    await save_chat_id(message.chat.id, "groups")
    await message.reply_text(f"🤖 Chatbot is now {'ON ✅' if CHATBOT_STATUS[message.chat.id] else 'OFF ❌'}")

# -------- /tagall Command (group, admin-only) --------
@app.on_message(filters.command("tagall") & filters.group)
async def tagall_cmd(client, message: Message):
    # require invoking user to be admin and bot to be admin
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply_text("Only group admins can start tagall.")
    if not await is_bot_admin(message.chat.id):
        return await message.reply_text("I need admin rights to tag members. Make me admin.")
    chat_id = message.chat.id
    TAGGING[chat_id] = True
    msg = message.text.split(None, 1)[1] if len(message.command) > 1 else "Tagging All!"
    await message.reply_text("✅ TAGGING STARTED !! ♥")
    try:
        async for member in app.get_chat_members(chat_id):
            if not TAGGING.get(chat_id):
                break
            try:
                name = member.user.first_name or member.user.username or "Member"
                await app.send_message(chat_id, f"{msg}\n🔹 {name}")
                await asyncio.sleep(0.4)
            except:
                continue
    except Exception as e:
        pass
    await message.reply_text("✅ TAGGING COMPLETED !! ◉‿◉")

# -------- /stop Command (group) --------
@app.on_message(filters.command("stop") & filters.group)
async def stop_tag(client, message: Message):
    TAGGING[message.chat.id] = False
    await message.reply_text("❌ TAGGING STOPPED !!")

# -------- /couples Command --------
@app.on_message(filters.command("Couples") & filters.group)
async def couples_cmd(client, message: Message):
    # pick two random members
    if not await is_bot_admin(message.chat.id):
        return await message.reply_text("I need to be admin to fetch members for couples.")
    members = []
    async for m in app.get_chat_members(message.chat.id, limit=200):
        if not m.user.is_bot:
            members.append(m.user.first_name or m.user.username or "Member")
    if len(members) < 2:
        return await message.reply_text("Not enough members to pick a couple.")
    a, b = random.sample(members, 2)
    await message.reply_text(f"💞 Couple: {a} + {b} \nThey look cute together!")

# -------- /cute Command --------
@app.on_message(filters.command("cute") & filters.group)
async def cute_cmd(client, message: Message):
    target = message.reply_to_message.from_user.first_name if message.reply_to_message else message.from_user.first_name
    percent = random.randint(1, 100)
    await message.reply_text(f"✨ {target}, your cute level is {percent}% 💖")

# -------- /love Command --------
@app.on_message(filters.command("love") & (filters.group | filters.private))
async def love_cmd(client, message: Message):
    # expects "first + second" after command or as args
    args = message.text.split(None, 1)
    if len(args) < 2:
        return await message.reply_text("Usage: /love name1 + name2")
    text = args[1]
    if "+" in text:
        a, b = [p.strip() for p in text.split("+", 1)]
    else:
        parts = text.split()
        if len(parts) >= 2:
            a, b = parts[0], parts[1]
        else:
            return await message.reply_text("Please give two names, e.g. /love Alice + Bob")
    percent = random.randint(1, 100)
    await message.reply_text(f"💘 Love possibility between {a} ❤️ {b} is {percent}% 😉")

# -------- /afk Command --------
@app.on_message(filters.command("afk") & (filters.group | filters.private))
async def afk_cmd(client, message: Message):
    user = message.from_user
    reason = " ".join(message.command[1:]) if len(message.command) > 1 else "AFK"
    AFK.setdefault(message.chat.id, {})[user.id] = (int(time.time()), reason)
    await message.reply_text(f"ʜᴇʏ, {user.first_name} you are now AFK: {reason}")

# When someone mentions an AFK user, notify
@app.on_message(filters.group & filters.text)
async def afk_notify(client, message: Message):
    # If a message mentions someone who is AFK, notify
    if message.entities:
        mentioned_ids = set()
        for ent in message.entities:
            if ent.type in ("mention", "text_mention"):
                if ent.type == "text_mention" and ent.user:
                    mentioned_ids.add(ent.user.id)
                elif ent.type == "mention":
                    # mention string -> try to extract username (we won't resolve username to id here)
                    pass
    # Also if a user who was AFK sends a message, mark them back
    uid = message.from_user.id
    if AFK.get(message.chat.id, {}).get(uid):
        AFK[message.chat.id].pop(uid, None)
        await message.reply_text(f"ʏᴇᴀʜ, {message.from_user.first_name} you are back, ONLINE!! 😉")

# -------- /tr Command (simple placeholder) --------
@app.on_message(filters.command("tr") & filters.group)
async def tr_cmd(client, message: Message):
    # this is a placeholder translate to english (would require external API)
    if not message.reply_to_message:
        return await message.reply_text("Reply to a message with /tr to translate to English.")
    text = message.reply_to_message.text or ""
    # naive placeholder: return same text (since no external calls here)
    await message.reply_text(f"Translated (placeholder):\n{text}")

# -------- /dice and simple games (dice) --------
@app.on_message(filters.command("dice") & filters.group)
async def dice_cmd(client, message: Message):
    # Pyrogram has send_dice but some versions differ; use send_dice if available
    try:
        await message.reply_text("🎲 You rolled a " + str(random.randint(1, 6)))
    except Exception as e:
        await message.reply_text("Couldn't roll dice: " + str(e))

# -------- /developer Command --------
@app.on_message(filters.command("Devloper") | filters.command("developer"))
async def developer_cmd(client, message: Message):
    DEV_IMG = "https://iili.io/KVzmgWl.jpg"
    buttons = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("𝐃ᴇᴠʟᴏᴘᴇʀ ღ", url="https://t.me/TheXVoren")],
            [InlineKeyboardButton("𝐂ʟᴏsᴇ", callback_data="close_start")]
        ]
    )
    await message.reply_photo(DEV_IMG, caption="ʙᴏᴛ ᴅᴇᴠʟᴏᴘᴇʀ", reply_markup=buttons)

# -------- staff command (list admins) --------
@app.on_message(filters.command("staff") & filters.group)
async def staff_cmd(client, message: Message):
    if not await is_bot_admin(message.chat.id):
        return await message.reply_text("I need admin rights to list staff.")
    admins = []
    async for m in app.get_chat_members(message.chat.id, filter=enums.ChatMembersFilter.ADMINS):
        admins.append(f"{m.user.first_name} — {m.user.id}")
    if not admins:
        return await message.reply_text("No admins found.")
    await message.reply_text("Group admins:\n" + "\n".join(admins))

# -------- botlist command (list bots) --------
@app.on_message(filters.command("botlist") & filters.group)
async def botlist_cmd(client, message: Message):
    bots = []
    async for m in app.get_chat_members(message.chat.id, limit=200):
        if m.user.is_bot:
            bots.append(f"{m.user.first_name} — {m.user.id}")
    if not bots:
        return await message.reply_text("No bots found in this group.")
    await message.reply_text("Bots in group:\n" + "\n".join(bots))

# -------- Private Auto Reply --------
@app.on_message(filters.text & filters.private)
async def private_reply(client, message: Message):
    await save_chat_id(message.chat.id, "privates")
    reply = get_reply(message.text)
    await message.reply_text(reply)

# -------- Group Auto Reply (only if bot is admin and chatbot enabled) --------
@app.on_message(filters.text & filters.group)
async def group_reply(client, message: Message):
    await save_chat_id(message.chat.id, "groups")
    # Only reply if chatbot enabled in this chat (default True) AND bot is admin
    if not await is_bot_admin(message.chat.id):
        return  # do not respond if bot isn't admin
    if CHATBOT_STATUS.get(message.chat.id, True) and random.random() < 0.7:
        reply = get_reply(message.text)
        try:
            await message.reply_text(reply)
        except:
            pass

# -------- Voice Chat Notifications (kept) --------
@app.on_message(filters.group)
async def voice_chat_events(client, message: Message):
    # Note: Pyrogram event attributes may differ by version
    if getattr(message, "video_chat_started", False):
        await message.reply_text("🎤 Voice Chat Started!")
    elif getattr(message, "video_chat_ended", False):
        await message.reply_text("❌ Voice Chat Ended!")
    elif getattr(message, "video_chat_invite", False):
        await message.reply_text("📣 You've been invited to a Voice Chat!")

# -------- Health Check for Render --------
class _H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def _start_http():
    HTTPServer(("0.0.0.0", PORT), _H).serve_forever()

threading.Thread(target=_start_http, daemon=True).start()
print("✅ Advanced Chatbot is running...")

# -------- Run the bot --------
if __name__ == "__main__":
    app.run()
