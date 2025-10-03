from pyrogram import Client, filters, enums from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message from pyrogram.errors import UserNotParticipant import os, json, random, threading, asyncio, time from http.server import BaseHTTPRequestHandler, HTTPServer from datetime import datetime

-------- Env Vars --------

NOTE: OWNER_ID must be set to your actual ID (7589623332) in your environment variables.

API_ID = int(os.environ.get("API_ID", "0")) API_HASH = os.environ.get("API_HASH", "") BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

Please ensure you set this to 7589623332 in your environment

OWNER_ID = int(os.environ.get("OWNER_ID", "7589623332"))

DEVELOPER_USERNAME = "Vᴏʀᴇɴ" DEVELOPER_HANDLE = "@TheXVoren" SUPPORT_CHAT = "https://t.me/Evara_Support_Chat" UPDATES_CHANNEL = "https://t.me/Evara_Updates"

-------- Bot Client --------

app = Client("advanced_chatbot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

-------- Global Vars --------

START_TIME = datetime.now() CHATBOT_STATUS = {} TAGGING = {} AFK_USERS = {} # {user_id: {"reason": str, "chat_id": int, "username": str, "time": float}}

New image URLs and text

START_PHOTO = "https://iili.io/KVzgS44.jpg" PING_PHOTO = "https://iili.io/KVzbu4t.jpg" DEVELOPER_PHOTO = "https://iili.io/KVzmgWl.jpg"

--- FIXED: Removed non-printable characters (U+00A0) ---

INTRO_TEXT_TEMPLATE = ( "ʜєʏ {mention_name}\n" "✦ ɪ ᴧϻ ᴧᴅᴠᴧηᴄєᴅ ᴄʜᴧᴛ ʙσᴛ ᴡɪᴛʜ sσϻє ғєᴧᴛᴜʀєs. \n" "✦ ʀєᴘʟʏ ɪη ɢʀσᴜᴘs & ᴘʀɪᴠᴧᴛє🥀\n" "✦ ηᴏ ᴧʙᴜsɪηɢ & zєʀσ ᴅσᴡηᴛɪϻє\n" "✦ ᴄʟɪᴄᴋ ʜєʟᴘ ʙᴜᴛᴛση ғσʀ ʜєʟᴘs❤️\n" "❖ ϻᴧᴅє ʙʏ...{developer}" )

ABOUT_TEXT = ( "❖ ᴧ ϻɪηɪ ᴄʜᴧᴛ ʙᴏᴛ ғᴏʀ ᴛᴇʟᴇɢʀᴧϻ ɢʀᴏᴜᴘs & ᴘʀɪᴠᴧᴛᴇ\n" "● ᴡʀɪᴛᴛᴇη ɪη ᴘʏᴛʜᴏɴ \n" "● ᴋєєᴘ ʏσᴜʀ ᴧᴄᴛɪᴠє ɢʀσᴜᴘ.\n" "● ᴧᴅᴅ ϻє ηᴏᴡ ʙᴧʙʏ ɪɴ ʏᴏᴜʀ ɢʀσᴜᴘs. " )

--- Load Replies & Known Chats ---

try: with open("conversation.json", "r", encoding="utf-8") as f: DATA = json.load(f) except: DATA = {}

if "daily" not in DATA: DATA["daily"] = ["Hello 👋", "Hey there!", "Hi!"]

CHAT_IDS_FILE = "chats.json" if os.path.exists(CHAT_IDS_FILE): with open(CHAT_IDS_FILE, "r") as f: KNOWN_CHATS = json.load(f) else: KNOWN_CHATS = {"groups": [], "privates": []}

KEYWORDS = { "love": "love", "i love you": "love", "miss": "love", "sad": "sad", "cry": "sad", "depressed": "sad", "happy": "happy", "mast": "happy", "hello": "daily", "hi": "daily", "hey": "daily", "bye": "bye", "goodbye": "bye", "thanks": "thanks", "thank you": "thanks", "gm": "morning", "good morning": "morning", "gn": "night", "good night": "night", "chutiya": "abuse", "bc": "abuse", "mc": "abuse" }

-------- Utility Functions --------

def get_reply(text: str): text = text.lower() for word, cat in KEYWORDS.items(): if word in text and cat in DATA: return random.choice(DATA[cat]) return random.choice(DATA.get("daily", ["Hello 👋"]))

def get_readable_time(seconds: int) -> str: result = '' (days, remainder) = divmod(seconds, 86400) (hours, remainder) = divmod(remainder, 3600) (minutes, seconds) = divmod(remainder, 60) if days > 0: result += f"{days}d " if hours > 0: result += f"{hours}h " if minutes > 0: result += f"{minutes}m " if seconds > 0: result += f"{seconds}s" return result.strip()

async def is_admin(chat_id, user_id): try: member = await app.get_chat_member(chat_id, user_id) return member.status in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR] except Exception: return False

async def is_bot_admin(chat_id): try: me = await app.get_me() member = await app.get_chat_member(chat_id, me.id) return member.status in [enums.ChatMemberStatus.OWNER, enums.ChatMemberStatus.ADMINISTRATOR] except Exception: return False

async def save_chat_id(chat_id, type_): if chat_id not in KNOWN_CHATS[type_]: KNOWN_CHATS[type_].append(chat_id) with open(CHAT_IDS_FILE, "w") as f: json.dump(KNOWN_CHATS, f)

-------- Inline Button Handlers & Menus --------

--- Menu Builder Functions ---

def get_start_buttons(bot_username): """Returns the main start button layout.""" return InlineKeyboardMarkup([ [InlineKeyboardButton("➕ 𝐀ᴅᴅ ᴍᴇ ʏᴏᴜʀ 𝐆ʀᴏᴜᴘ ➕", url=f"https://t.me/{bot_username}?startgroup=true")], [ InlineKeyboardButton("ᯓ❍ᴡ𝛈ᴇʀ", user_id=OWNER_ID), InlineKeyboardButton("◉ 𝐀ʙᴏᴜᴛ", callback_data="about") ], [InlineKeyboardButton("◉ 𝐇ᴇʟᴘ & 𝐂ᴏᴍᴍᴀɴᴅs", callback_data="help_main")] ])

def get_about_buttons(): """Returns the About section button layout.""" return InlineKeyboardMarkup([ [ InlineKeyboardButton("𝐄ᴠᴀʀᴀ 𝐒ᴜᴘᴘᴏʀᴛ 𝐂ʜᴀᴛ", url=SUPPORT_CHAT), InlineKeyboardButton("𝐔ρ∂ᴀᴛᴇs", url=UPDATES_CHANNEL) ], [ InlineKeyboardButton("𝐁ᴀᴄᴋ", callback_data="start_back"), InlineKeyboardButton("𝐂ʟᴏsᴇ", callback_data="close") ] ])

def get_help_main_buttons(): """Returns the main Help & Commands button layout.""" return InlineKeyboardMarkup([ [ InlineKeyboardButton("ᴄᴏᴜᴘʟᴇ", callback_data="help_couple"), InlineKeyboardButton("ᴄʜᴀᴛʙᴏᴛ", callback_data="help_chatbot") ], [ InlineKeyboardButton("ᴛᴏᴏʟs", callback_data="help_tools"), InlineKeyboardButton("ɢᴀᴍᴇs", callback_data="help_games") ], [InlineKeyboardButton("ɢʀᴏᴜᴘ", callback_data="help_group")], [ InlineKeyboardButton("𝐁ᴀᴄᴋ", callback_data="start_back"), InlineKeyboardButton("𝐂ʟᴏsᴇ", callback_data="close") ] ])

--- Sub-Help Menu Content ---

HELP_COMMANDS_TEXT_MAP = { "couple": ( "📜 𝐂ᴏᴜᴘʟᴇ & 𝐋ᴏᴠᴇ 𝐂ᴏᴍᴍᴀɴᴅs:\n" "/couples ~ ᴄʜᴏᴏsᴇ ᴀ ʀᴀɴᴅᴏᴍ ᴄᴏᴜᴘʟᴇ\n" "/cute ~ ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴄᴜᴛᴇɴᴇss\n" "/love name1 + name2 ~ sᴇᴇ ʟᴏᴠᴇ ᴘᴏssɪʙɪʟɪᴛʏ\n" "\n_All these commands are available to everyone." ), "chatbot": ( "📜 𝐂ʜᴀᴛʙᴏᴛ 𝐂ᴏᴍᴍᴀɴᴅ:\n" "/chatbot enable/disable ~ ᴇɴᴀʙʟᴇ/ᴅɪsᴀʙʟᴇ ᴄʜᴀᴛʙᴏᴛ\n" "\n" "ɴᴏᴛᴇ: ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘ ᴀɴᴅ ᴏɴʟʏ ғᴏʀ ᴀᴅᴍɪɴs/ᴏᴡɴᴇʀ.\n" "Example: /chatbot enable" ), "tools": ( "📜 𝐓ᴏᴏʟs 𝐂ᴏᴍᴍᴀɴᴅs:\n" "/id ~ ɢᴇᴛ ᴜsᴇʀ ɪᴅ (reply or tag)\n" "/tagall  ~ ᴛᴀɢ ᴀʟʟ ᴍᴇᴍʙᴇʀs (Admin Only)\n" "/stop ~ ᴛᴏ sᴛᴏᴘ ᴛᴀɢɢɪɴɢ (Admin Only)\n" "/afk reason ~ ᴀᴡᴀʏ ғʀᴏᴍ ᴛʜᴇ ᴋᴇʏʙᴏᴀʀᴅ\n" "\n_Tagall/Stop requires Admin. Others are for everyone." ), "games": ( "📜 𝐆ᴀᴍᴇs 𝐂ᴏᴍᴍᴀɴᴅs:\n" "/dice ~ ʀᴏʟʟ ᴀ ᴅɪᴄᴇ\n" "/jackpot ~ ᴊᴀᴄᴋᴘᴏᴛ ᴍᴀᴄʜɪɴᴇ\n" "/football ~ ᴘʟᴀʏ ғᴏᴏᴛʙᴀʟʟ\n" "/basketball ~ ᴘʟᴀʏ ʙᴀsᴋᴇᴛʙᴀʟʟ\n" "\n_All these games are available to everyone." ), "group": ( "📜 𝐆ʀᴏᴜᴘ 𝐔ᴛɪʟɪᴛʏ 𝐂ᴏᴍᴍᴀɴᴅs:\n" "/mmf text ~ ᴄʀᴇᴀᴛᴇ ᴀ sᴛɪᴄᴋᴇʀ ᴡɪᴛʜ ᴛᴇxᴛ (Reply to a sticker)\n" "/staff ~ ᴅɪsᴘʟᴀʏs ɢʀᴏᴜᴘ sᴛᴀғғ ᴍᴇᴍʙᴇʀs\n" "/botlist ~ ᴄʜᴇᴄᴋ ʜᴏᴡ ᴍᴀɴʏ ʙᴏᴛs ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ (Admin Only)" "\n_Botlist requires Admin. Others are for everyone." ) }

--- Callbacks Handler ---

@app.on_callback_query() async def callbacks_handler(client, query): data = query.data user = query.from_user me = await app.get_me()
developer_link = DEVELOPER_HANDLE.strip('@')    if data == "about":       await query.message.edit_caption(           caption=ABOUT_TEXT,           reply_markup=get_about_buttons()       )   elif data == "start_back":       await query.message.edit_caption(           caption=INTRO_TEXT_TEMPLATE.format(               mention_name=f"[{user.first_name}](tg://user?id={user.id})",               developer=DEVELOPER_USERNAME,               developer_link=developer_link           ),           reply_markup=get_start_buttons(me.username)       )   elif data == "help_main":       await query.message.edit_caption(           caption="📜 𝐂ᴏᴍᴍᴀɴᴅs 𝐌ᴇɴᴜ:\n\nChoose a category below:",           reply_markup=get_help_main_buttons()       )   elif data.startswith("help_"):       category = data.split("_")[1]       text = HELP_COMMANDS_TEXT_MAP.get(category, "Error: Unknown Category")        # Custom button logic for sub-menus       buttons = []       if category in ["couple", "cute", "love"]:           buttons.append(InlineKeyboardButton("sᴜᴘᴘᴏʀᴛ", url=SUPPORT_CHAT))        # Ensure buttons is a list of lists for InlineKeyboardMarkup       buttons_markup_rows = []       if buttons:           buttons_markup_rows.append(buttons)                  buttons_markup_rows.append([           InlineKeyboardButton("𝐁ᴀᴄᴋ", callback_data="help_main"),           InlineKeyboardButton("𝐂ʟᴏsᴇ", callback_data="close")       ])        await query.message.edit_caption(           caption=text,           reply_markup=InlineKeyboardMarkup(buttons_markup_rows)       )   elif data == "close":       await query.message.delete()   else:       await query.answer("This button is not yet functional.")   

-------- Commands --------

-------- /start Command --------

@app.on_message(filters.command("start") & filters.private) async def start_cmd(client, message): user = message.from_user me = await app.get_me() developer_link = DEVELOPER_HANDLE.strip('@')
# Ding Dong Animation   anim_text = "ᴅɪɴɢ...ᴅᴏɴɢ 💥....ʙᴏᴛ ɪs sᴛᴀʀᴛɪɴɢ"   msg = await message.reply_text("Starting...")   current = ""   for ch in anim_text:       current += ch       try:           await msg.edit(current)       except: pass       await asyncio.sleep(0.05)   await asyncio.sleep(0.5)   await msg.delete()    await message.reply_photo(       START_PHOTO,       caption=INTRO_TEXT_TEMPLATE.format(           mention_name=f"[{user.first_name}](tg://user?id={user.id})",           developer=DEVELOPER_USERNAME,           developer_link=developer_link       ),       reply_markup=get_start_buttons(me.username)   )   await save_chat_id(message.chat.id, "privates")   

-------- /developer Command --------

@app.on_message(filters.command("developer")) async def developer_cmd(client, message): # Animation anim_text = "ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴋɴᴏᴡ, ᴛʜɪs ʙᴏᴛ ᴅᴇᴠʟᴏᴘᴇʀ 💥..ʜᴇʀᴇ" m = await message.reply_text("Searching...") current = "" for ch in anim_text: current += ch try: await m.edit(current) except: pass await asyncio.sleep(0.05) await asyncio.sleep(0.5)
# Try to delete the animation message   try:       await m.delete()   except:       pass # Ignore if the animation message is already deleted/edited/not found    buttons = InlineKeyboardMarkup([       [InlineKeyboardButton("𝐃ᴇᴠʟᴏᴘᴇʀ ღ", url=f"https://t.me/{DEVELOPER_HANDLE.strip('@')}")]   ])      caption_text = f"ʙᴏᴛ ᴅᴇᴠʟᴏᴘᴇʀ ɪs **[{DEVELOPER_USERNAME}](t.me/{DEVELOPER_HANDLE.strip('@')})**"      try:       # 1. Try to send the photo response       await message.reply_photo(           DEVELOPER_PHOTO,           caption=caption_text,           reply_markup=buttons,           parse_mode=enums.ParseMode.MARKDOWN       )   except Exception as e:       # 2. Fallback to text message if photo sending fails (ensures a response)       await message.reply_text(           caption_text,           reply_markup=buttons,           parse_mode=enums.ParseMode.MARKDOWN       )       print(f"Error sending developer photo: {e}") # Log the error   

-------- /ping Command --------

@app.on_message(filters.command("ping")) async def ping_cmd(client, message): start = time.time() # Ping animation m = await message.reply_text("ᴘɪɴɢɪɴɢ...sᴛᴀʀᴇᴅ..´･ᴗ･") await asyncio.sleep(0.5) await m.edit_text("ᴘɪɴɢ..ᴘᴏɴɢ ⚡") await asyncio.sleep(0.5)
end = time.time()   ping_ms = round((end-start)*1000)   uptime_seconds = (datetime.now() - START_TIME).total_seconds()   uptime_readable = get_readable_time(int(uptime_seconds))    me = await client.get_me()    buttons = InlineKeyboardMarkup([       [InlineKeyboardButton("➕ ᴀᴅᴅ ᴍᴇ ➕", url=f"https://t.me/{me.username}?startgroup=true")],       [InlineKeyboardButton("sᴜᴘᴘᴏʀᴛ", url=SUPPORT_CHAT)]   ])    await m.delete() # Delete the animation message   await message.reply_photo(       PING_PHOTO,       caption=f"**ᴘɪɴɢ** ➳ {ping_ms} ms\n"               f"**ᴜᴘᴛɪᴍᴇ** ➳ {uptime_readable}",       reply_markup=buttons   )   

-------- /id Command --------

@app.on_message(filters.command("id")) async def id_cmd(client, message): user = message.reply_to_message.from_user if message.reply_to_message else message.from_user await message.reply_text(f"👤 {user.first_name}\n🆔 {user.id}")

-------- /stats Command (Owner Only) --------

@app.on_message(filters.command("stats") & filters.user(OWNER_ID)) async def stats_cmd(client, message): await message.reply_text(f"📊 ʙᴏᴛ sᴛᴀᴛs:\n👥 𝐆ʀᴏᴜᴘs: {len(KNOWN_CHATS['groups'])}\n👤 𝐏ʀɪᴠᴀᴛᴇs: {len(KNOWN_CHATS['privates'])}")

-------- /broadcast (Owner Only) --------

@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID)) async def broadcast_cmd(client, message): if not (message.reply_to_message or len(message.command) > 1): return await message.reply_text("Usage: /broadcast  or reply to a message.") text = message.text.split(None, 1)[1] if len(message.command) > 1 else None sent = 0 failed = 0 m = await message.reply_text("Starting broadcast...") for chat_type in ["privates", "groups"]: for chat_id in KNOWN_CHATS[chat_type]: try: if message.reply_to_message: await message.reply_to_message.copy(chat_id) else: await app.send_message(chat_id, text) sent += 1 except: failed += 1 continue await m.edit_text(f"✅ Broadcast Done!\nSent to {sent} chats.\nFailed in {failed} chats.")

-------- /chatbot Toggle --------

@app.on_message(filters.command("chatbot") & filters.group) async def chatbot_toggle(client, message): if not await is_admin(message.chat.id, message.from_user.id): return await message.reply_text("❗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴀɴᴅ ᴏᴡɴᴇʀ ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")
if len(message.command) < 2:       return await message.reply_text("Usage: /chatbot enable or /chatbot disable")    mode = message.command[1].lower()   if mode in ["on", "enable"]:       CHATBOT_STATUS[message.chat.id] = True       status_text = "ᴇɴᴀʙʟᴇ"       await message.reply_text(f"ᴄʜᴀᴛʙᴏᴛ sᴛᴀᴛᴜs ɪs {status_text.upper()} ✰")   elif mode in ["off", "disable"]:       CHATBOT_STATUS[message.chat.id] = False       status_text = "ᴅɪsᴀʙʟᴇ"       await message.reply_text(f"ᴄʜᴀᴛʙᴏᴛ sᴛᴀᴛᴜs ɪs {status_text.upper()} ✰")   else:       return await message.reply_text("Usage: /chatbot enable or /chatbot disable")          await save_chat_id(message.chat.id, "groups")   

-------- /tagall Command --------

@app.on_message(filters.command("tagall") & filters.group) async def tagall_cmd(client, message): if not await is_admin(message.chat.id, message.from_user.id): return if not await is_bot_admin(message.chat.id): return await message.reply_text("❗ ɪ ɴᴇᴇᴅ ᴀᴅᴍɪɴ ᴘᴇʀᴍɪssɪᴏɴs (ᴛᴀɢ ᴍᴇᴍʙᴇʀs) ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")
chat_id = message.chat.id      if TAGGING.get(chat_id):       return await message.reply_text("❗ ᴀʟʀᴇᴀᴅʏ ᴛᴀɢɢɪɴɢ ɪɴ ᴛʜɪs ᴄʜᴀᴛ. ᴜsᴇ /stop ᴛᴏ ᴄᴀɴᴄᴇʟ.")    TAGGING[chat_id] = True   # Get message content   if len(message.command) > 1:       msg = message.text.split(None, 1)[1]   elif message.reply_to_message:       msg = "Tagging from replied message!"   else:       msg = "Attention!"      m = await message.reply_text("𝐓ᴀɢɢɪɴɢ sᴛᴀʀᴛᴇᴅ !! ♥")      member_list = []   # Collect all members first   try:       async for member in app.get_chat_members(chat_id):           if not (member.user.is_bot or member.user.is_deleted):               member_list.append(member.user)   except Exception:       TAGGING[chat_id] = False       return await m.edit_text("🚫 ᴇʀʀᴏʀ ɪɴ ғᴇᴛᴄʜɪɴɢ ᴍᴇᴍʙᴇʀs: ᴍᴀʏʙᴇ ᴛʜɪs ɢʀᴏᴜᴘ ɪs ᴛᴏᴏ ʙɪɢ ᴏʀ ɪ ᴅᴏɴ'T ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴs.")    # Start tagging in chunks   chunk_size = 5   for i in range(0, len(member_list), chunk_size):       if not TAGGING.get(chat_id):           break              chunk = member_list[i:i + chunk_size]       tag_text = f"**{msg}**\n"       for user in chunk:           tag_text += f"[{user.first_name}](tg://user?id={user.id}) "              try:           # Send the tag chunk           await app.send_message(chat_id, tag_text, disable_web_page_preview=True)           await asyncio.sleep(2) # Delay to avoid flooding limits       except: continue          # Final message update   if TAGGING.get(chat_id):       await m.edit_text("ᴛᴀɢɢɪɴɢ ᴄᴏᴍᴘʟᴇᴛᴇᴅ !! ◉‿◉")      TAGGING[chat_id] = False   

-------- /stop Tagging --------

@app.on_message(filters.command("stop") & filters.group) async def stop_tag(client, message): if not await is_admin(message.chat.id, message.from_user.id): return if TAGGING.get(message.chat.id): TAGGING[message.chat.id] = False await message.reply_text("ᴛᴀɢɢɪɴɢ sᴛᴏᴘᴇᴅ !!") else: await message.reply_text("❗ ɴᴏ ᴛᴀɢɢɪɴɢ ɪs ᴄᴜʀʀᴇɴᴛʟʏ ʀᴜɴɴɪɴɢ.")

-------- /couples, /cute, /love Commands --------

@app.on_message(filters.command("couples") & filters.group) async def couples_cmd(client, message): member_list = [] try: async for member in app.get_chat_members(message.chat.id): if not (member.user.is_bot or member.user.is_deleted): member_list.append(member.user) except Exception: return await message.reply_text("🚫 ᴄᴀɴɴᴏᴛ ғᴇᴛᴄʜ ᴍᴇᴍʙᴇʀs ᴅᴜᴇ ᴛᴏ ʀᴇsᴛʀɪᴄᴛɪᴏɴs.")
if len(member_list) < 2:       return await message.reply_text("❗ ɴᴇᴇᴅ ᴀᴛ ʟᴇᴀsᴛ ᴛᴡᴏ ᴍᴇᴍʙᴇʀs ᴛᴏ ғᴏʀᴍ ᴀ ᴄᴏᴜᴘʟᴇ.")    # Pick two random unique members   couple = random.sample(member_list, 2)   user1 = couple[0]   user2 = couple[1]      # Calculate a random love percentage (just for fun)   love_percent = random.randint(30, 99)    await message.reply_text(       f"**💘 ɴᴇᴡ ᴄᴏᴜᴘʟᴇ ᴏғ ᴛʜᴇ ᴅᴀʏ!**\n\n"       f"**{user1.first_name}** 💖 **{user2.first_name}**\n"       f"ʟᴏᴠᴇ ʟᴇᴠᴇʟ ɪs **{love_percent}%**! 🎉"   )   
@app.on_message(filters.command("cute")) async def cute_cmd(client, message): cute_level = random.randint(30, 99) user = message.from_user text = f"{user.first_name}'s ᴄᴜᴛɴᴇss ʟᴇᴠᴇʟ ɪs {cute_level}% 💖" buttons = InlineKeyboardMarkup([[InlineKeyboardButton("sᴜᴘᴘᴏʀᴛ", url=SUPPORT_CHAT)]]) await message.reply_text(text, reply_markup=buttons)

@app.on_message(filters.command("love")) async def love_cmd(client, message): if len(message.command) < 2 or "+" not in message.text: return await message.reply_text("Usage: /love First Name + Second Name")
# Split the argument and clean it up   arg_text = message.text.split(None, 1)[1]   names = [n.strip() for n in arg_text.split("+") if n.strip()]    if len(names) < 2:       return await message.reply_text("Please provide two names separated by a '+' (e.g., /love Alice + Bob)")    # The rest of the logic is fine   love_percent = random.randint(1, 100)   text = f"**❤️ ʟᴏᴠᴇ ᴘᴏssɪʙɪʟɪᴛʏ**\n" \          f"**{names[0]}** & **{names[1]}**'s ʟᴏᴠᴇ ʟᴇᴠᴇʟ ɪs **{love_percent}%** 😉"      buttons = InlineKeyboardMarkup([[InlineKeyboardButton("sᴜᴘᴘᴏʀᴛ", url=SUPPORT_CHAT)]])   await message.reply_text(text, reply_markup=buttons)   

-------- /afk Command --------

@app.on_message(filters.command("afk")) async def afk_cmd(client, message): user_id = message.from_user.id user_name = message.from_user.first_name
# Check if user is already AFK (meaning they are typing /afk to return)   if user_id in AFK_USERS:       # User is coming back       afk_data = AFK_USERS.pop(user_id)       time_afk = get_readable_time(int(time.time() - afk_data["time"]))              await message.reply_text(           f"ʏᴇᴀʜ, [{user_name}](tg://user?id={user_id}), ʏᴏᴜ ᴀʀᴇ **ʙᴀᴄᴋ**, ᴏɴʟɪɴᴇ! (AFK for: {time_afk}) 😉",           parse_mode=enums.ParseMode.MARKDOWN       )       return # Stop execution after returning    # If user is not AFK, they are setting AFK status   reason = message.text.split(None, 1)[1] if len(message.command) > 1 else "No reason given."   AFK_USERS[user_id] = {"reason": reason, "chat_id": message.chat.id, "username": user_name, "time": time.time()}      # Send the AFK message   await message.reply_text(       f"ʜᴇʏ, [{user_name}](tg://user?id={user_id}), ʏᴏᴜ ᴀʀᴇ **ᴀғᴋ**! (Reason: {reason})",       parse_mode=enums.ParseMode.MARKDOWN   )   # The automatic "I'm back" message when they send a non-/afk message is handled in group_reply_and_afk_checker   

-------- /mmf Command (FIXED - Simple reply) --------

@app.on_message(filters.command("mmf") & filters.group) async def mmf_cmd(client, message): # This feature requires complex external tools/logic (e.g., Pillow). # Since the full functionality is not implemented, we provide a clean, non-buggy error/status message. if not message.reply_to_message or not message.reply_to_message.sticker: return await message.reply_text("❗ ʀᴇᴘʟʏ ᴛᴏ ᴀ sᴛɪᴄᴋᴇʀ ᴀɴᴅ ᴘʀᴏᴠɪᴅᴇ ᴛᴇxᴛ ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.\n\n*(Nᴏᴛᴇ: ᴛʜɪs ғᴇᴀᴛᴜʀᴇ ɪs ᴄᴜʀʀᴇɴᴛʟʏ ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ)*")
if len(message.command) < 2:       return await message.reply_text("❗ ᴘʀᴏᴠɪᴅᴇ ᴛʜᴇ **ᴛᴇxᴛ** ʏᴏᴜ ᴡᴀɴᴛ ᴏɴ ᴛʜᴇ sᴛɪᴄᴋᴇʀ.")          await message.reply_text(       "❌ **Sticker Text Feature Unavailable**\n"       "ᴘʟᴇᴀsᴇ ɴᴏᴛᴇ: ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪs ᴛᴇᴍᴘᴏʀᴀʀɪʟʏ **ᴅɪsᴀʙʟᴇᴅ** ᴅᴜᴇ ᴛᴏ ᴍɪssɪɴɢ ɪᴍᴀɢᴇ ᴘʀᴏᴄᴇssɪɴɢ ʟɪʙʀᴀʀɪᴇs. "       "ɪ ᴀᴍ ᴡᴏʀᴋɪɴɢ ᴏɴ ɪᴛ!"   )   

-------- /staff, /botlist Commands --------

@app.on_message(filters.command("staff") & filters.group) async def staff_cmd(client, message): # Logic confirmed from previous fix try: admins = [ admin async for admin in app.get_chat_members(message.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS) ]
   staff_list = "👑 **ɢʀᴏᴜᴘ sᴛᴀғғ ᴍᴇᴍʙᴇʀs:**\n"       for admin in admins:           if not admin.user.is_bot:               tag = f"[{admin.user.first_name}](tg://user?id={admin.user.id})"               status = admin.status.name.replace("_", " ").title()               staff_list += f"• {tag} ({status})\n"              await message.reply_text(staff_list, disable_web_page_preview=True)   except Exception as e:       await message.reply_text(f"🚫 ᴇʀʀᴏʀ ɪɴ ғᴇᴛᴄʜɪɴɢ sᴛᴀғғ: {e}")  
@app.on_message(filters.command("botlist") & filters.group) async def botlist_cmd(client, message): if not await is_admin(message.chat.id, message.from_user.id): return
# Logic confirmed from previous fix   try:       bots = [           bot           async for bot in app.get_chat_members(message.chat.id, filter=enums.ChatMembersFilter.BOTS)       ]        bot_list = "🤖 **ʙᴏᴛs ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ:**\n"       for bot in bots:           tag = f"[{bot.user.first_name}](tg://user?id={bot.user.id})"           # Ensure username exists before trying to access it           username_part = f" (@{bot.user.username})" if bot.user.username else ""           bot_list += f"• {tag}{username_part}\n"                  await message.reply_text(bot_list, disable_web_page_preview=True)   except Exception as e:       # Catch any remaining fetch errors       await message.reply_text(f"🚫 ᴇʀʀᴏʀ ɪɴ ғᴇᴛᴄʜɪɴɢ ʙᴏᴛ ʟɪsᴛ: {e}")   

-------- Game Commands --------

@app.on_message(filters.command("dice")) async def dice_cmd(client, message): await app.send_dice(message.chat.id, "🎲")

@app.on_message(filters.command("jackpot")) async def jackpot_cmd(client, message): await app.send_dice(message.chat.id, "🎰")

@app.on_message(filters.command("football")) async def football_cmd(client, message): await app.send_dice(message.chat.id, "⚽")

@app.on_message(filters.command("basketball")) async def basketball_cmd(client, message): await app.send_dice(message.chat.id, "🏀")

-------- Private Auto Reply --------

@app.on_message(filters.text & filters.private, group=0) async def private_reply(client, message): await save_chat_id(message.chat.id, "privates") reply = get_reply(message.text) await message.reply_text(reply)

-------- Group Auto Reply & AFK Checker --------

@app.on_message(filters.text & filters.group, group=1) async def group_reply_and_afk_checker(client, message: Message): await save_chat_id(message.chat.id, "groups")
# 1. Check if the user sending a regular message is AFK (Coming back)   # This prevents the double message when they type a message after /afk   if message.from_user and message.from_user.id in AFK_USERS and message.text and not message.text.startswith("/afk"):       user_id = message.from_user.id              # Calculate time before deleting       afk_data = AFK_USERS.pop(user_id) # Remove user from AFK list       time_afk = get_readable_time(int(time.time() - afk_data["time"]))       user_name = afk_data["username"]        # Send the "I'm back" message       await message.reply_text(           f"ʏᴇᴀʜ, [{user_name}](tg://user?id={user_id}), ʏᴏᴜ ᴀʀᴇ **ʙᴀᴄᴋ**, ᴏɴʟɪɴᴇ! (AFK for: {time_afk}) 😉",           parse_mode=enums.ParseMode.MARKDOWN       )    # 2. AFK Tag/Reply Check   users_to_check = []      # Check replied user   if message.reply_to_message and message.reply_to_message.from_user:       replied_user_id = message.reply_to_message.from_user.id       if replied_user_id in AFK_USERS:           users_to_check.append(replied_user_id)              # Check text mentions   if message.text and message.entities:       for entity in message.entities:           if entity.type == enums.MessageEntityType.TEXT_MENTION and entity.user and entity.user.id in AFK_USERS:               if entity.user.id not in users_to_check:                   users_to_check.append(entity.user.id)    for afk_id in users_to_check:       afk_data = AFK_USERS.get(afk_id)       if afk_data:           user_name = afk_data["username"]           reason = afk_data["reason"]           time_afk = get_readable_time(int(time.time() - afk_data["time"]))                      await message.reply_text(               f"⚠️ **[{user_name}](tg://user?id={afk_id}) ɪs ᴀғᴋ**! ◉‿◉\n"               f"**Reason:** *{reason}*\n"               f"**Time:** *{time_afk}*",               parse_mode=enums.ParseMode.MARKDOWN           )           # Only send one AFK notice per message to avoid spam           break    # 3. Chatbot Auto-Reply Logic   me = await client.get_me()      # CRITICAL: Bot must be an admin to reply (as requested)   if message.chat.type != enums.ChatType.PRIVATE and not await is_bot_admin(message.chat.id):       return    is_chatbot_on = CHATBOT_STATUS.get(message.chat.id, True)   is_reply_to_bot = message.reply_to_message and message.reply_to_message.from_user and message.reply_to_message.from_user.id == me.id   is_direct_mention = message.text and me.username in message.text if me.username else False      if is_chatbot_on:       if is_reply_to_bot or is_direct_mention:           # Always reply if the bot is directly addressed           reply = get_reply(message.text)           await message.reply_text(reply)       elif random.random() < 0.2:            # Low chance (20%) for general group conversation           # Don't reply if it's a reply to another non-bot user, to avoid conversation hijacking           is_reply_to_other_user = message.reply_to_message and message.reply_to_message.from_user and message.reply_to_message.from_user.id != me.id and not message.reply_to_message.from_user.is_bot           if not is_reply_to_other_user:               reply = get_reply(message.text)               await message.reply_text(reply)   

-------- Voice Chat Notifications (FIXED) --------

We use the corrected 'video_chat' filters and message attributes here.

@app.on_message(filters.video_chat_started | filters.video_chat_ended | filters.video_chat_members_invited, group=2) async def voice_chat_events(client, message): # Ensure this only runs in groups/supergroups if message.chat.type not in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]: return
if message.video_chat_started:       await message.reply_text("🎤 **Voice Chat Started!** ᴛɪᴍᴇ ᴛᴏ ᴊᴏɪɴ!")   elif message.video_chat_ended:       # Get duration safely       duration = get_readable_time(message.video_chat_ended.duration) if message.video_chat_ended.duration else "short time"       await message.reply_text(f"❌ **Voice Chat Ended!** ɪᴛ ʟᴀsᴛᴇᴅ ғᴏʀ {duration}.")   elif message.video_chat_members_invited:       invited_users_count = len(message.video_chat_members_invited.users)       inviter = message.from_user.mention              # Check if the bot was invited (optional, for specific reply)       me = await client.get_me()       if me.id in [u.id for u in message.video_chat_members_invited.users]:            await message.reply_text(f"📣 ʜᴇʏ {inviter}, ᴛʜᴀɴᴋs ғᴏʀ ɪɴᴠɪᴛɪɴɢ ᴍᴇ ᴛᴏ ᴛʜᴇ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ!")       else:            await message.reply_text(f"🗣️ {inviter} ɪɴᴠɪᴛᴇᴅ **{invited_users_count}** ᴍᴇᴍʙᴇʀs ᴛᴏ ᴛʜᴇ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ!")   

-------- Health Check --------

PORT = int(os.environ.get("PORT", 8080)) class _H(BaseHTTPRequestHandler): def do_GET(self): self.send_response(200) self.end_headers() self.wfile.write(b"OK") def _start_http(): HTTPServer(("0.0.0.0", PORT), _H).serve_forever() threading.Thread(target=_start_http, daemon=True).start()

print("✅ Advanced Chatbot is running...") app.run()

