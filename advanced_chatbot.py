from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os, json, random, threading, asyncio, time
from http.server import BaseHTTPRequestHandler, HTTPServer

# -------- Env Vars --------
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
OWNER_ID = int(os.environ.get("OWNER_ID", "7589623332"))

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
INTRO_TEXT = (
    "ʜᴇʏ 👋 {name}\n\n"
    "ɪ ᴀᴍ ᴀɴ ᴀᴅᴠᴀɴᴄᴇᴅ ᴄʜᴀᴛʙᴏᴛ 🤖\n"
    "ᴀᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘs 🚀\n\n"
    "🌟 ғᴇᴀᴛᴜʀᴇs: ᴀᴜᴛᴏ ʀᴇᴘʟʏ, ᴛᴀɢᴀʟʟ, ʙʀᴏᴀᴅᴄᴀsᴛ, sᴛᴀᴛs, sᴛɪᴄᴋᴇʀ ʀᴇᴘʟʏ"
)
OWNER_PANEL_TEXT = "ʜᴇʏ 👋 I am your bot! 🔒"

# -------- Utility --------
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
        [
            InlineKeyboardButton("❍ᴡɳᴇʀ", url="https://t.me/TheXVoren"),
            InlineKeyboardButton("𝐒ᴜρρᴏʀᴛ", url="https://t.me/Nova_Support_Chat")
        ],
        [InlineKeyboardButton("𝐂ᴏᴍᴍᴀɴᴅs 🛠", callback_data="commands")]
    ])
    await message.reply_photo(
        "https://i.ibb.co/rKJDYmVM/IMG-20250917-111838.jpg",
        caption=INTRO_TEXT.format(name=user.first_name),
        reply_markup=buttons
    )
    await save_chat_id(message.chat.id, "privates")

# -------- Commands Panel --------
@app.on_callback_query(filters.regex("commands"))
async def commands_cb(client, cq):
    text = (
        f"📜 Bot Commands:\n\n{OWNER_PANEL_TEXT}\n\n"
        "/start, /help, /ping, /id, /broadcast, /stats, /chatbot on/off, /tagall <msg>, /stop"
    )
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("𝐁ᴀᴄᴋ", callback_data="back"), InlineKeyboardButton("𝐂ʟᴏsᴇ", callback_data="close")]
    ])
    await cq.answer()
    await cq.message.edit(text, reply_markup=buttons)

@app.on_callback_query(filters.regex("back"))
async def back_cb(client, cq):
    await start_cmd(client, cq.message)

@app.on_callback_query(filters.regex("close"))
async def close_cb(client, cq):
    await cq.message.delete()
    await cq.answer("Closed ✅")

# -------- /help Command --------
@app.on_message(filters.command("help") & filters.private)
async def help_cmd(client, message):
    text = (
        "📜 **Bot Commands:**\n"
        "/start - Start Bot\n"
        "/help - Show this message\n"
        "/ping - Check Bot Speed\n"
        "/id - Get User ID\n"
        "/broadcast - Broadcast Message (Owner Only)\n"
        "/stats - Bot Stats (Owner Only)\n"
        "/chatbot on/off - Toggle AI in Groups\n"
        "/tagall <msg> - Tag All Members\n"
        "/stop - Stop Tagging\n"
        "/paneltext <text> - Change Owner Panel Text (Owner Only)"
    )
    await message.reply_text(text)

# -------- /ping Command --------
@app.on_message(filters.command("ping"))
async def ping_cmd(client, message):
    start = time.time()
    m = await message.reply_text("🏓 Pinging...")
    end = time.time()
    await m.edit_text(f"✅ Bot is Alive!\n⚡ {round((end-start)*1000)} ms")

# -------- /id Command --------
@app.on_message(filters.command("id"))
async def id_cmd(client, message):
    user = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    await message.reply_text(f"👤 {user.first_name}\n🆔 {user.id}")

# -------- /stats Command --------
@app.on_message(filters.command("stats") & filters.user(OWNER_ID))
async def stats_cmd(client, message):
    await message.reply_text(f"📊 Bot Stats:\n👥 Groups: {len(KNOWN_CHATS['groups'])}\n👤 Privates: {len(KNOWN_CHATS['privates'])}")

# -------- /broadcast Command --------
@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast_cmd(client, message):
    if not (message.reply_to_message or len(message.command) > 1):
        return await message.reply_text("Usage: /broadcast <msg> or reply to a message.")
    text = message.text.split(None, 1)[1] if len(message.command) > 1 else None
    sent = 0
    for chat_type in ["privates", "groups"]:
        for chat_id in KNOWN_CHATS[chat_type]:
            try:
                if message.reply_to_message:
                    await message.reply_to_message.copy(chat_id)
                else:
                    await app.send_message(chat_id, text)
                sent += 1
            except: continue
    await message.reply_text(f"✅ Broadcast sent to {sent} chats.")

# -------- /paneltext Command (Owner Only) --------
@app.on_message(filters.command("paneltext") & filters.user(OWNER_ID))
async def paneltext_cmd(client, message):
    global OWNER_PANEL_TEXT
    text = message.text.split(None, 1)[1] if len(message.command) > 1 else None
    if not text:
        return await message.reply_text("Usage: /paneltext <text>")
    OWNER_PANEL_TEXT = text
    await message.reply_text(f"✅ Owner panel text updated!")

# -------- /chatbot Toggle --------
@app.on_message(filters.command("chatbot") & filters.group)
async def chatbot_toggle(client, message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return
    mode = message.command[1].lower() if len(message.command) > 1 else ""
    CHATBOT_STATUS[message.chat.id] = (mode == "on")
    await save_chat_id(message.chat.id, "groups")
    await message.reply_text(f"🤖 Chatbot is now {'ON ✅' if CHATBOT_STATUS[message.chat.id] else 'OFF ❌'}")

# -------- /tagall Command --------
@app.on_message(filters.command("tagall") & filters.group)
async def tagall_cmd(client, message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return
    chat_id = message.chat.id
    TAGGING[chat_id] = True
    msg = message.text.split(None, 1)[1] if len(message.command) > 1 else "Tagging All!"
    await message.reply_text("✅ Tagging Started...")
    async for member in app.get_chat_members(chat_id):
        if not TAGGING.get(chat_id):
            break
        try:
            await app.send_message(chat_id, f"{msg}\n[{member.user.first_name}](tg://user?id={member.user.id})")
            await asyncio.sleep(0.5)
        except: continue
    await message.reply_text("✅ Tagging Done!")

# -------- /stop Command --------
@app.on_message(filters.command("stop") & filters.group)
async def stop_tag(client, message):
    TAGGING[message.chat.id] = False
    await message.reply_text("❌ Tagging Stopped!")

# -------- Private Auto Reply --------
@app.on_message(filters.text & filters.private)
async def private_reply(client, message):
    await save_chat_id(message.chat.id, "privates")
    reply = get_reply(message.text)
    await message.reply_text(reply)

# -------- Group Auto Reply --------
@app.on_message(filters.text & filters.group)
async def group_reply(client, message):
    await save_chat_id(message.chat.id, "groups")
    if CHATBOT_STATUS.get(message.chat.id, True) and random.random() < 0.7:
        reply = get_reply(message.text)
        await message.reply_text(reply)

# -------- Voice Chat Notifications --------
@app.on_message(filters.group)
async def voice_chat_events(client, message):
    if getattr(message, "video_chat_started", False):
        await message.reply_text("🎤 Voice Chat Started!")
    elif getattr(message, "video_chat_ended", False):
        await message.reply_text("❌ Voice Chat Ended!")
    elif getattr(message, "video_chat_invite", False):
        await message.reply_text("📣 You've been invited to a Voice Chat!")

# -------- Health Check --------
PORT = int(os.environ.get("PORT", 8080))
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
