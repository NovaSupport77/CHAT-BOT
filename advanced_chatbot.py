# -*- coding: utf-8 -*-
import os, json, random, threading, asyncio, time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# -------- Env Vars --------
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
OWNER_ID = int(os.environ.get("OWNER_ID", "7589623332"))
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

# -------- Load Known Chats --------
CHAT_IDS_FILE = "chats.json"
if os.path.exists(CHAT_IDS_FILE):
    with open(CHAT_IDS_FILE, "r") as f:
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
AFK_USERS = {}
OWNER_PANEL_TEXT = "ʜᴇʏ 👋 I am your bot! 🔒"
INTRO_TEXT = (
    "**ʜєʏ {name}**\n"
    "✦ ɪ ᴧϻ ᴧᴅᴠᴧηᴄєᴅ ᴄʜᴧᴛ ʙσᴛ ᴡɪᴛʜ sσϻє ғєᴧᴛᴜʀєs. ✦ ʀєᴘʟʏ ɪη ɢʀσᴜᴘs & ᴘʀɪᴠᴧᴛє🥀\n"
    "✦ ηᴏ ᴧʙᴜsɪηɢ & zєʀσ ᴅσᴡηᴛɪϻє\n"
    "✦ ᴄʟɪᴄᴋ ʜєʟᴘ ʙᴜᴛᴛση ғσʀ ʜєʟᴘs❤️\n"
    "❖ ϻᴧᴅє ʙʏ [Vᴏʀᴇɴ](https://t.me/TheXVoren)"
)

# -------- Utility Functions --------
def get_reply(text: str):
    text = text.lower()
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

async def save_chat_id(chat_id, type_):
    if chat_id not in KNOWN_CHATS[type_]:
        KNOWN_CHATS[type_].append(chat_id)
        with open(CHAT_IDS_FILE, "w") as f:
            json.dump(KNOWN_CHATS, f)

# -------- /start Command with Ding Dong Animation --------
@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    user = message.from_user
    me = await app.get_me()
    bot_username = me.username
    anim_text = "ᴅɪɴɢ...ᴅᴏɴɢ 💥....ʙᴏᴛ ɪs sᴛᴀʀᴛɪɴɢ"
    msg = await message.reply_text("Starting...")
    current = ""
    for ch in anim_text:
        current += ch
        try: await msg.edit_text(current)
        except: pass
        await asyncio.sleep(0.05)
    await asyncio.sleep(0.5)
    await msg.delete()

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ 𝐀ᴅᴅ ᴍᴇ ʏᴏᴜʀ 𝐆ʀᴏᴜᴘ ➕", url=f"https://t.me/{bot_username}?startgroup=true")],
        [InlineKeyboardButton("ᯓ❍ᴡ𝛈ᴇʀ", url="https://t.me/TheXVoren"),
         InlineKeyboardButton("◉ 𝐀ʙᴏᴜᴛ", callback_data="about_section")],
        [InlineKeyboardButton("◉ 𝐇ᴇʟᴘ & 𝐂ᴏᴍᴍᴀɴᴅs", callback_data="help_section")]
    ])
    await message.reply_photo(
        "https://iili.io/KVzgS44.jpg",
        caption=INTRO_TEXT.format(name=user.first_name),
        reply_markup=buttons
    )
    await save_chat_id(message.chat.id, "privates")

# -------- About Section --------
@app.on_callback_query(filters.regex("about_section"))
async def about_cb(client, cq):
    text = (
        "**❖ ᴧ ϻɪηɪ ᴄʜᴧᴛ ʙᴏᴛ ғᴏʀ ᴛᴇʟᴇɢʀᴧϻ ɢʀᴏᴜᴘs & ᴘʀɪᴠᴧᴛᴇ**\n"
        "● ᴡʀɪᴛᴛᴇη ɪη **ᴘʏᴛʜᴏɴ**\n"
        "● ᴋєєᴘ ʏσᴜʀ ᴧᴄᴛɪᴠє ɢʀσᴜᴘ\n"
        "● ᴧᴅᴅ ϻє ηᴏᴡ ʙʟᴀʙʏ ɪɴ ʏᴏᴜʀ ɢʀσᴜᴘs"
    )
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("𝐄ᴠᴀʀᴀ 𝐒ᴜᴘᴘᴏʀᴛ 𝐂ʜᴀᴛ", url="https://t.me/Evara_Support_Chat"),
         InlineKeyboardButton("𝐔ρ∂ᴀᴛᴇs", url="https://t.me/Evara_Updates")],
        [InlineKeyboardButton("𝐁ᴀᴄᴋ", callback_data="start_cmd"),
         InlineKeyboardButton("𝐂ʟᴏsᴇ", callback_data="close_section")]
    ])
    await cq.answer()
    await cq.message.edit(text=text, reply_markup=buttons)

# -------- Help & Commands Section --------
@app.on_callback_query(filters.regex("help_section"))
async def help_cb(client, cq):
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("ᴄᴏᴜᴘʟᴇ", callback_data="cmd_couples"),
         InlineKeyboardButton("ᴄʜᴀᴛʙᴏᴛ", callback_data="cmd_chatbot"),
         InlineKeyboardButton("ᴛᴏᴏʟs", callback_data="cmd_tools")],
        [InlineKeyboardButton("ɢᴀᴍᴇs", callback_data="cmd_games"),
         InlineKeyboardButton("sᴛɪᴄᴋᴇʀs", callback_data="cmd_stickers"),
         InlineKeyboardButton("ɢʀᴏᴜᴘs", callback_data="cmd_groups")],
        [InlineKeyboardButton("𝐂ʟᴏsᴇ", callback_data="close_section")]
    ])
    await cq.answer()
    await cq.message.edit(text="**Help & Commands Section**", reply_markup=buttons)

# -------- /Devloper Command --------
@app.on_message(filters.command("Devloper") & filters.private)
async def dev_cmd(client, message):
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("𝐃ᴇᴠʟᴏᴘᴇʀ ღ", url="https://t.me/TheXVoren")]
    ])
    await message.reply_photo(
        "https://iili.io/KVzmgWl.jpg",
        caption="**ʙᴏᴛ ᴅᴇᴠʟᴏᴘᴇʀ**",
        reply_markup=buttons
    )

# -------- Ping Command with Animation --------
@app.on_message(filters.command("ping"))
async def ping_cmd(client, message):
    start = time.time()
    m = await message.reply_text("ᴘɪɴɢɪɴɢ...sᴛᴀʀᴇᴅ..´･ᴗ･`ᴘɪɴɢ..ᴘᴏɴɢ ⚡")
    end = time.time()
    uptime = round(time.time() - app.start_time)
    await m.edit_text(f"ᴘɪɴɢ ➳ {round((end-start)*1000)} ms\nᴜᴘᴛɪᴍᴇ ➳ {uptime} sec")

# -------- Private & Group Auto Reply --------
@app.on_message(filters.text & filters.private)
async def private_reply(client, message):
    await save_chat_id(message.chat.id, "privates")
    reply = get_reply(message.text)
    await message.reply_text(reply)

@app.on_message(filters.text & filters.group)
async def group_reply(client, message):
    me_id = (await app.get_me()).id
    if not await is_admin(message.chat.id, me_id):
        return
    await save_chat_id(message.chat.id, "groups")
    if CHATBOT_STATUS.get(message.chat.id, True) and random.random() < 0.7:
        reply = get_reply(message.text)
        await message.reply_text(reply)

# -------- AFK Mention --------
@app.on_message(filters.group & filters.mentioned)
async def afk_notify(client, message):
    user = message.reply_to_message.from_user if message.reply_to_message else None
    if user and user.id in AFK_USERS:
        await message.reply_text(f'Hey, {user.mention} you are AFK! ◉‿◉')

# -------- Health Check --------
class _H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

def _start_http():
    HTTPServer(("0.0.0.0", PORT), _H).serve_forever()

threading.Thread(target=_start_http, daemon=True).start()

print("✅ Advanced Chatbot is running...")
app.run()
