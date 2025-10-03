# advanced_chatbot_final.py
# Pyrogram-based Telegram bot implementing advanced group & private features
# Requirements:
#   pip install pyrogram tgcrypto
# Set environment variables: API_ID, API_HASH, BOT_TOKEN, OWNER_ID
# Run: python bot.py

import os
import asyncio
import time
import random
from typing import Dict, Set, List
from pyrogram import Client, filters, enums
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message,
    CallbackQuery,
    ChatPermissions,
)

# --- Config ---
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
OWNER_ID = int(os.environ.get("OWNER_ID", "7589623332"))  # default from your message
BOT_USERNAME = os.environ.get("BOT_USERNAME", None)  # optional, for mentions

# Images URLs you gave
INTRO_IMAGE = "https://iili.io/KVzgS44.jpg"
PING_IMAGE = "https://iili.io/KVzbu4t.jpg"
DEVELOPER_IMAGE = "https://iili.io/KVzmgWl.jpg"

SUPPORT_LINK = "https://t.me/Evara_Support_Chat"
UPDATES_LINK = "https://t.me/Evara_Updates"
OWNER_USERNAME = "@TheXVoren"
OWNER_PROFILE_LINK = f"https://t.me/{OWNER_USERNAME.lstrip('@')}"
OWNER_ID_INT = OWNER_ID

# --- Runtime state ---
start_time = time.time()
chatbot_enabled: Dict[int, bool] = {}  # chat_id -> bool
afk_users: Dict[int, str] = {}  # user_id -> reason or empty
tagging_active: Set[int] = set()  # chat ids where tagall is running (prevent reentrancy)
# store last afk status to detect return: we store a set of afk users; on message from them -> back
afk_set: Set[int] = set()

# Utility keyboard builders (many are nested)
def main_start_kb(bot_mention: str = None):
    # First column: single Add Me button
    kb = [
        [InlineKeyboardButton("+ 𝐀ᴅᴅ ᴍᴇ ʏᴏᴜʀ 𝐆ʀᴏᴜᴘ +", url=f"https://t.me/{BOT_USERNAME or ''}?startgroup=true")],
        [
            InlineKeyboardButton("ᯓ❍ᴡ𝛈ᴇʀ", url=OWNER_PROFILE_LINK),
            InlineKeyboardButton("◉ 𝐀ʙᴏᴜᴛ", callback_data="about_open"),
        ],
        [
            InlineKeyboardButton("◉ 𝐇ᴇʟᴘ & 𝐂ᴏᴍᴍᴀɴᴅs", callback_data="help_open"),
        ],
    ]
    return InlineKeyboardMarkup(kb)

def about_kb():
    kb = [
        [
            InlineKeyboardButton("𝐄ᴠᴀʀᴀ 𝐒ᴜᴘᴘᴏʀᴛ 𝐂ʜᴀᴛ", url=SUPPORT_LINK),
            InlineKeyboardButton("𝐔ρ∂ᴀᴛᴇs", url=UPDATES_LINK),
        ],
        [
            InlineKeyboardButton("𝐁ᴀᴄᴋ", callback_data="back_main"),
            InlineKeyboardButton("𝐂ʟᴏsᴇ", callback_data="close_all"),
        ],
    ]
    return InlineKeyboardMarkup(kb)

def about_text():
    return (
        "**❖ ᴧ ϻɪηɪ ᴄʜᴧᴛ ʙᴏᴛ ғᴏʀ ᴛᴇʟᴇɢʀᴀᴍ ɢʀᴏᴜᴘs & ᴘʀɪᴠᴧᴛᴇ**\n"
        "**● ᴡʀɪᴛᴛᴇη ɪη ᴘʏᴛʜᴏɴ**\n"
        "**● ᴋєєᴘ ʏσᴜʀ ᴧᴄᴛɪᴠє ɢʀσᴜᴘ.**\n"
        "**● ᴧᴅᴅ ϻє ηᴏᴡ ʙᴧʙʏ ɪɴ ʏᴏᴜʀ ɢʀσᴜᴘs.**\n"
        f"\nMade by {OWNER_USERNAME}"
    )

# Help menu keyboard (first level)
def help_main_kb():
    kb = [
        [InlineKeyboardButton("ᴄᴏᴜᴘʟᴇ", callback_data="help_couple"),
         InlineKeyboardButton("ᴄʜᴀᴛʙᴏᴛ", callback_data="help_chatbot"),
         InlineKeyboardButton("ᴛᴏᴏʟs", callback_data="help_tools")],
        [InlineKeyboardButton("ɢᴀᴍᴇs", callback_data="help_games"),
         InlineKeyboardButton("sᴛɪᴄᴋᴇʀs", callback_data="help_stickers"),
         InlineKeyboardButton("ɢʀᴏᴜᴘs", callback_data="help_groups")],
        [InlineKeyboardButton("𝐁ᴀᴄᴋ", callback_data="back_main"),
         InlineKeyboardButton("𝐂ʟᴏsᴇ", callback_data="close_all")],
    ]
    return InlineKeyboardMarkup(kb)

# Submenus keyboards for help pages will include Back & Close and Back to help
def simple_backclose_kb(back_to="help_open"):
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("𝐁ᴀᴄᴋ", callback_data=back_to),
          InlineKeyboardButton("𝐂ʟᴏsᴇ", callback_data="close_all")]]
    )

def couple_kb():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("sᴜᴘᴘᴏʀᴛ", url=SUPPORT_LINK)],
         [InlineKeyboardButton("𝐁ᴀᴄᴋ", callback_data="help_open"),
          InlineKeyboardButton("𝐂ʟᴏsᴇ", callback_data="close_all")]]
    )

def tools_kb():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("𝐁ᴀᴄᴋ", callback_data="help_open"),
             InlineKeyboardButton("𝐂ʟᴏsᴇ", callback_data="close_all")]
        ]
    )

def chat_bot_kb():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("/chatbot enable", callback_data="enable_chatbot_cb"),
             InlineKeyboardButton("/chatbot disable", callback_data="disable_chatbot_cb")],
            [InlineKeyboardButton("𝐁ᴀᴄᴋ", callback_data="help_open"),
             InlineKeyboardButton("𝐂ʟᴏsᴇ", callback_data="close_all")],
        ]
    )

def help_commands_couple_kb():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("sᴜᴘᴘᴏʀᴛ", url=SUPPORT_LINK)],
            [InlineKeyboardButton("𝐁ᴀᴄᴋ", callback_data="help_open"),
             InlineKeyboardButton("𝐂ʟᴏsᴇ", callback_data="close_all")],
        ]
    )

# Help pages text
def help_couple_text():
    return (
        "**/Couples** ~ ᴄʜᴏᴏsᴇ ᴀ ʀᴀɴᴅᴏᴍ ᴄᴏᴜᴘʟᴇ from the group\n"
        "**/cute** ~ ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴄᴜᴛᴇɴᴇss (random %)\n"
        "**/love** ~ ɢɪᴠᴇ ᴛᴡᴏ ɴᴀᴍᴇs first_name + second_name -> love percentage\n\n"
        f"Buttons: support -> {SUPPORT_LINK}"
    )

def help_chatbot_text():
    return (
        "**/chatbot enable|disable** — Enable or disable chatbot replies in the current group.\n"
        "Note: Only owner or admins can use this. Only works in groups."
    )

def help_tools_text():
    return (
        "**/id** — get user's telegram id (reply to user or tag)\n"
        "**/tagall** — tag all members (owner/admin only)\n"
        "**/stop** — stop tagging\n"
        "**/afk** — set yourself AFK (owner/admin can set AFK for others if desired)\n"
    )

def help_games_text():
    return (
        "**/dice** — roll a dice (random 1-6, uses native dice send)\n"
        "**/jackpot** — play a jackpot (simple placeholder game)\n"
        "**/football**, **/basketball** — simple play commands\n    (they run in-group games)"
    )

def help_stickers_text():
    return (
        "**/mmf** — reply to a sticker and add text: `/mmf your text` -> returns a sticker with text (basic implementation returns the original sticker or message acknowledging; sticker image editing would need image editing third-party tools)."
    )

def help_groups_text():
    return (
        "**/staff** — list group admins\n"
        "**/botlist** — list bots in the group\n"
        "**/ping** — ping & uptime\n"
    )

# --- Bot client ---
app = Client("advanced_chat_bot",
             api_id=API_ID,
             api_hash=API_HASH,
             bot_token=BOT_TOKEN,
             workers=20)

# --- Helpers ---
def is_admin_or_owner(chat_id: int, user_id: int):
    # returns True if user is owner or admin in chat (or global owner)
    if user_id == OWNER_ID:
        return True
    try:
        member = app.get_chat_member(chat_id, user_id)
        return member.status in ("administrator", "creator")
    except Exception:
        return False

async def ensure_bot_is_admin(chat_id: int):
    try:
        m = await app.get_chat_member(chat_id, (await app.get_me()).id)
        return m.status in ("administrator", "creator")
    except Exception:
        return False

def uptime_text():
    delta = int(time.time() - start_time)
    m, s = divmod(delta, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    return f"{d}d {h}h {m}m {s}s"

# --- Animated intro: send "ᴅɪɴɢ ᴅᴏɴɢ" then edit to main intro text with photo & keyboard ---
async def send_intro(message: Message):
    # Keep the original "ᴅɪɴɢ ᴅᴏɴɢ" animation effect
    try:
        sent = await message.reply_text("ᴅɪɴɢ  ᴅᴏɴɢ 🔔")
        await asyncio.sleep(0.7)
        await sent.edit_text("ᴅɪɴɢ ᴅᴏɴɢ 🔔  — Booting...")
        await asyncio.sleep(0.6)
        # now send photo with long caption & keyboard (we use owner mention as requested)
        caption = (
            "**ʜєʏ**\n"
            f"**{OWNER_USERNAME}**\n\n"
            "✦ ɪ ᴧϻ ᴧᴅᴠᴧηᴄєᴅ ᴄʜᴧᴛ ʙσᴛ ᴡɪᴛʜ sσϻє ғєᴧᴛᴜʀєs. ✦\n"
            "ʀєᴘʟʏ ɪη ɢʀσᴜᴘs & ᴘʀɪᴠᴧᴛє🥀✦ ηᴏ ᴧʙᴜsɪηɢ & zєʀσ ᴅσᴡɴᴛɪᴍє✦\n"
            "ᴄʟɪᴄᴋ ʜєʟᴘ ʙᴜᴛᴛση ғσʀ ʜєʟᴘs❤️\n\n"
            f"❖ ϻᴧᴅє ʙʏ... {OWNER_USERNAME}"
        )
        kb = main_start_kb(bot_mention=OWNER_USERNAME)
        await message.reply_photo(INTRO_IMAGE, caption=caption, reply_markup=kb)
    except Exception as e:
        await message.reply_text("Error sending intro: " + str(e))

# --- Command handlers ---
@app.on_message(filters.command(["start"]) & (filters.private | filters.group))
async def start_handler(client: Client, message: Message):
    # In groups bot should respond only if bot is admin (as per your ask)
    if message.chat.type in ("group", "supergroup"):
        bot_admin = await ensure_bot_is_admin(message.chat.id)
        if not bot_admin:
            # don't respond in groups if bot is not admin
            return
    # send animated intro in private, and same in group when triggered by admin or allowed
    await send_intro(message)

@app.on_message(filters.command(["Devloper", "developer", "Developer"]) & filters.private | filters.command(["Devloper"]) & filters.group)
async def developer_cmd(client: Client, message: Message):
    # show developer image + button to owner profile
    kb = InlineKeyboardMarkup(
        [[InlineKeyboardButton("𝐃ᴇᴠʟᴏᴘᴇʀ ღ", url=OWNER_PROFILE_LINK)]]
    )
    await message.reply_photo(DEVELOPER_IMAGE, caption="ʙᴏᴛ ᴅᴇᴠʟᴏᴘᴇʀ", reply_markup=kb)

@app.on_message(filters.command(["ping"]) & (filters.private | filters.group))
async def ping_cmd(client: Client, message: Message):
    if message.chat.type in ("group", "supergroup"):
        if not await ensure_bot_is_admin(message.chat.id):
            return
    # simple ping: measure a tiny roundtrip
    t0 = time.time()
    m = await message.reply_text("ᴘɪɴɢɪɴɢ... sᴛᴀʀᴇᴅ..´･ᴗ･`")
    t1 = time.time()
    rtt = int((t1 - t0) * 1000)
    text = f"ᴘɪɴɢ ➳ {rtt} ms\nᴜᴘᴛɪᴍᴇ ➳ {uptime_text()}"
    kb = InlineKeyboardMarkup(
        [[InlineKeyboardButton("+ ᴀᴅᴅ ᴍᴇ +", url=f"https://t.me/{BOT_USERNAME or ''}?startgroup=true"),
          InlineKeyboardButton("sᴜᴘᴘᴏʀᴛ", url=SUPPORT_LINK)]]
    )
    await m.delete()
    await message.reply_photo(PING_IMAGE, caption=text, reply_markup=kb)

@app.on_message(filters.command(["chatbot"]) & filters.group)
async def chatbot_toggle(client: Client, message: Message):
    # Only owner or admin
    if not is_admin_or_owner(message.chat.id, message.from_user.id):
        await message.reply_text("🚫 Only owner or admins can use this.")
        return
    if len(message.command) < 2:
        await message.reply_text("Usage: /chatbot enable|disable")
        return
    action = message.command[1].lower()
    if action == "enable":
        chatbot_enabled[message.chat.id] = True
        await message.reply_text("ᴄʜᴀᴛʙᴏᴛ sᴛᴀᴛᴜs ɪs ᴇɴᴀʙʟᴇ ✰")
    elif action == "disable":
        chatbot_enabled[message.chat.id] = False
        await message.reply_text("ᴄʜᴀᴛʙᴏᴛ sᴛᴀᴛᴜs ɪs ᴅɪsᴀʙʟᴇ ✰")
    else:
        await message.reply_text("Use enable or disable.")

# /couples - choose 2 random members (works in groups)
@app.on_message(filters.command(["Couples", "couples"]) & filters.group)
async def couples_cmd(client: Client, message: Message):
    if not await ensure_bot_is_admin(message.chat.id):
        return
    try:
        members = []
        # get up to 200 non-bot members
        async for m in client.get_chat_members(message.chat.id, limit=200):
            if not (m.user.is_bot):
                members.append(m.user)
        if len(members) < 2:
            await message.reply_text("Not enough members to pick a couple.")
            return
        a, b = random.sample(members, 2)
        await message.reply_text(f"💘 Couple: {a.mention} + {b.mention}\nLooks amazing together!")
    except Exception as e:
        await message.reply_text("Error: " + str(e))

# /cute - random percent
@app.on_message(filters.command(["cute"]) & (filters.group | filters.private))
async def cute_cmd(client: Client, message: Message):
    who = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    percent = random.randint(1, 100)
    await message.reply_text(f"{who.mention}, ʏᴏᴜʀ ᴄᴜᴛᴇɴᴇss ʟᴇᴠᴇʟ ɪs {percent}% 💖")

# /love name1+name2
@app.on_message(filters.command(["love"]) & (filters.group | filters.private))
async def love_cmd(client: Client, message: Message):
    text = message.text.partition(" ")[2]
    if not text or "+" not in text:
        await message.reply_text("Usage: /love name1+name2")
        return
    name1, _, name2 = text.partition("+")
    name1 = name1.strip()
    name2 = name2.strip()
    percent = random.randint(1, 100)
    await message.reply_text(f"💞 Love possibility between **{name1}** and **{name2}** is **{percent}%** 😉")

# /id - get user id
@app.on_message(filters.command(["id"]) & (filters.group | filters.private))
async def id_cmd(client: Client, message: Message):
    target = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    await message.reply_text(f"User: {target.mention}\nID: `{target.id}`", parse_mode="markdown")

# tagall - owner/admin only (be careful with large groups)
@app.on_message(filters.command(["tagall", "Tagall"]) & filters.group)
async def tagall_cmd(client: Client, message: Message):
    if not is_admin_or_owner(message.chat.id, message.from_user.id):
        await message.reply_text("🚫 Only owner or admins can use this.")
        return
    if message.chat.id in tagging_active:
        await message.reply_text("Tagging already in progress. Use /stop to stop.")
        return
    tagging_active.add(message.chat.id)
    await message.reply_text("𝐓ᴀɢɢɪɴɢ sᴛᴀʀᴛᴇᴅ !! ♥")
    members = []
    async for m in client.get_chat_members(message.chat.id, limit=200):
        if not m.user.is_bot:
            members.append(m.user)
    # chunk to avoid extremely long messages (chunks of 20)
    try:
        chunk = []
        for user in members:
            if message.chat.id not in tagging_active:
                break
            chunk.append(user.mention)
            if len(chunk) >= 20:
                await message.reply_text(" ".join(chunk))
                chunk = []
                await asyncio.sleep(1.2)
        if chunk and message.chat.id in tagging_active:
            await message.reply_text(" ".join(chunk))
    except Exception as e:
        await message.reply_text("Error tagging: " + str(e))
    finally:
        if message.chat.id in tagging_active:
            tagging_active.remove(message.chat.id)
            await message.reply_text("ᴛᴀɢɢɪɴɢ ᴄᴏᴍᴘʟᴇᴛᴇᴅ !! ◉‿◉")

# /stop - stop tagging
@app.on_message(filters.command(["stop"]) & filters.group)
async def stop_cmd(client: Client, message: Message):
    if not is_admin_or_owner(message.chat.id, message.from_user.id):
        await message.reply_text("🚫 Only owner or admins can use this.")
        return
    if message.chat.id in tagging_active:
        tagging_active.remove(message.chat.id)
        await message.reply_text("ᴛᴀɢɢɪɴɢ sᴛᴏᴘᴇᴅ !!")
    else:
        await message.reply_text("No tagging in progress.")

# /afk
@app.on_message(filters.command(["afk"]) & (filters.group | filters.private))
async def afk_cmd(client: Client, message: Message):
    # set AFK for the user who uses it (or for a mentioned user if owner/admin)
    reason = message.text.partition(" ")[2].strip()
    target_id = message.from_user.id
    # if owner/admin and they replied to someone, can set AFK for that user
    if message.reply_to_message and is_admin_or_owner(message.chat.id, message.from_user.id):
        target_id = message.reply_to_message.from_user.id
    afk_users[target_id] = reason or "AFK"
    afk_set.add(target_id)
    await message.reply_text(f"ʜᴇʏ, <a href='tg://user?id={target_id}'>user</a> ɪs ᴀғᴋ !!", parse_mode="html")

# detect mentions to AFK users
@app.on_message(filters.group & ~filters.service)
async def afk_detector(client: Client, message: Message):
    # If someone messages who is AFK, announce return
    uid = message.from_user.id
    if uid in afk_set:
        afk_set.remove(uid)
        afk_users.pop(uid, None)
        await message.reply_text(f"ʏᴇᴀʜ, {message.from_user.mention}, ʏᴏᴜ ᴀʀᴇ ʙᴀᴄᴋ , ᴏɴʟʏɴʟɪɴᴇ !! 😉")
    # if message mentions users who are AFK, notify
    if message.entities:
        mentioned_ids = set()
        for ent in message.entities:
            if ent.type == "text_mention" and ent.user:
                mentioned_ids.add(ent.user.id)
    # Also check reply_to_message
    if message.reply_to_message:
        rid = message.reply_to_message.from_user.id
        if rid in afk_users:
            reason = afk_users.get(rid, "AFK")
            await message.reply_text(f"ᴛʜɪs ᴜsᴇʀ ɪs ᴀғᴋ !! ({reason})")

# /mmf - reply to sticker + text (simple echo; actual image sticker editing needs more tools)
@app.on_message(filters.command(["mmf"]) & (filters.group | filters.private))
async def mmf_cmd(client: Client, message: Message):
    if not message.reply_to_message:
        await message.reply_text("Reply to a sticker or image with /mmf your_text")
        return
    text = message.text.partition(" ")[2].strip()
    if not text:
        await message.reply_text("Please provide text to put on sticker.")
        return
    # For now, we will acknowledge and resend the same media with caption (cannot write text onto sticker without image processing)
    try:
        if message.reply_to_message.sticker:
            await message.reply_text(f"Sticker text: {text}\n(note: editing sticker image requires extra tools)")
        elif message.reply_to_message.photo:
            await message.reply_to_message.reply_photo(message.reply_to_message.photo.file_id, caption=text)
        else:
            await message.reply_text("Reply to a sticker or photo.")
    except Exception as e:
        await message.reply_text("Error: " + str(e))

# /staff - list admins
@app.on_message(filters.command(["staff"]) & filters.group)
async def staff_cmd(client: Client, message: Message):
    admins = []
    async for m in client.get_chat_members(message.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS):
        admins.append(f"{m.user.mention}")
    text = "**Group staff members:**\n" + "\n".join(admins)
    await message.reply_text(text)

# /botlist - bots in group
@app.on_message(filters.command(["botlist"]) & filters.group)
async def botlist_cmd(client: Client, message: Message):
    bots = []
    async for m in client.get_chat_members(message.chat.id, limit=200):
        if m.user.is_bot:
            bots.append(m.user.mention)
    await message.reply_text("Bots in this group:\n" + ("\n".join(bots) if bots else "No bots found."))

# Games: dice /jackpot /football /basketball simple implementations
@app.on_message(filters.command(["dice"]) & filters.group)
async def dice_cmd(client: Client, message: Message):
    await message.reply_dice()

@app.on_message(filters.command(["jackpot"]) & filters.group)
async def jackpot_cmd(client: Client, message: Message):
    # simple random winner among active chat members (small sample)
    members = []
    async for m in client.get_chat_members(message.chat.id, limit=200):
        if not m.user.is_bot:
            members.append(m.user)
    if not members:
        await message.reply_text("No participants found.")
        return
    winner = random.choice(members)
    amount = random.randint(10, 500)
    await message.reply_text(f"🎰 Jackpot! Winner: {winner.mention}\nPrize: {amount} coins (virtual)")

@app.on_message(filters.command(["football","basketball"]) & filters.group)
async def sport_game(client: Client, message: Message):
    story = "Game started! (simple group minigame placeholder)"
    await message.reply_text(story)

# Callback query handlers for inline buttons (navigation)
@app.on_callback_query()
async def callbacks(client: Client, cq: CallbackQuery):
    data = cq.data
    try:
        if data == "about_open":
            await cq.message.edit_caption(
                caption=about_text(),
                reply_markup=about_kb()
            )
            await cq.answer()
        elif data == "help_open":
            await cq.message.edit_caption(caption="Help & Commands — Choose a section", reply_markup=help_main_kb())
            await cq.answer()
        elif data == "back_main":
            # revert to main intro page
            caption = (
                "**ʜєʏ**\n"
                f"**{OWNER_USERNAME}**\n\n"
                "✦ ɪ ᴧϻ ᴧᴅᴠᴧηᴄєᴅ ᴄʜᴧᴛ ʙσᴛ ᴡɪᴛʜ sσϻє ғєᴧᴛᴜʀєs. ✦\n"
                "ʀєᴘʟʏ ɪη ɢʀσᴜᴘs & ᴘʀɪᴠᴧᴛє🥀✦ ηᴏ ᴧʙᴜsɪηɢ & zєʀσ ᴅσᴡɴᴛɪᴍє✦\n"
                "ᴄʟɪᴄᴋ ʜєʟᴘ ʙᴜᴛᴛση ғσʀ ʜєʟᴘs❤️\n\n"
                f"❖ ϻᴧᴅє ʙʏ... {OWNER_USERNAME}"
            )
            await cq.message.edit_caption(caption=caption, reply_markup=main_start_kb())
            await cq.answer()
        elif data == "close_all":
            # delete message (close)
            try:
                await cq.message.delete()
            except:
                await cq.message.edit_caption(caption="Closed.")
            await cq.answer()
        elif data == "help_couple":
            await cq.message.edit_caption(caption=help_couple_text(), reply_markup=couple_kb())
            await cq.answer()
        elif data == "help_chatbot":
            await cq.message.edit_caption(caption=help_chatbot_text(), reply_markup=chat_bot_kb())
            await cq.answer()
        elif data == "help_tools":
            await cq.message.edit_caption(caption=help_tools_text(), reply_markup=simple_backclose_kb("help_open"))
            await cq.answer()
        elif data == "help_games":
            await cq.message.edit_caption(caption=help_games_text(), reply_markup=simple_backclose_kb("help_open"))
            await cq.answer()
        elif data == "help_stickers":
            await cq.message.edit_caption(caption=help_stickers_text(), reply_markup=simple_backclose_kb("help_open"))
            await cq.answer()
        elif data == "help_groups":
            await cq.message.edit_caption(caption=help_groups_text(), reply_markup=simple_backclose_kb("help_open"))
            await cq.answer()
        elif data == "enable_chatbot_cb":
            # Try to enable chatbot for this chat (only if admin)
            chat = cq.message.chat
            if not is_admin_or_owner(chat.id, cq.from_user.id):
                await cq.answer("Only owner or admins can do that.", show_alert=True)
                return
            chatbot_enabled[chat.id] = True
            await cq.answer("Chatbot enabled for this group.")
        elif data == "disable_chatbot_cb":
            chat = cq.message.chat
            if not is_admin_or_owner(chat.id, cq.from_user.id):
                await cq.answer("Only owner or admins can do that.", show_alert=True)
                return
            chatbot_enabled[chat.id] = False
            await cq.answer("Chatbot disabled for this group.")
        else:
            await cq.answer()
    except Exception as e:
        try:
            await cq.answer("Error: " + str(e), show_alert=True)
        except:
            pass

# Simple chatbot auto-reply behavior for groups (if enabled and bot is admin)
@app.on_message(filters.group & ~filters.edited & ~filters.bot)
async def group_auto_reply(client: Client, message: Message):
    # Only reply if bot is admin in group
    if not await ensure_bot_is_admin(message.chat.id):
        return
    # check if chatbot is enabled for this chat (defaults to enabled)
    enabled = chatbot_enabled.get(message.chat.id, True)
    if not enabled:
        return
    # simple small talk: respond to mention or random triggers
    text = (message.text or "").lower()
    # respond only when mentioned or keywords seen
    me = await app.get_me()
    mentioned = False
    if message.entities:
        for ent in message.entities:
            if ent.type == "mention":
                ent_text = message.text[ent.offset: ent.offset + ent.length]
                if ent_text.lstrip("@").lower() == (me.username or "").lower():
                    mentioned = True
            if ent.type == "text_mention" and ent.user and ent.user.id == me.id:
                mentioned = True
    if mentioned or any(w in text for w in ["hello", "hi", "bot", "hey"]):
        # reply with a playful message
        await message.reply_text("Hi! I'm an advanced chat bot. Type /Devloper to know my maker.")

# Start the bot
if __name__ == "__main__":
    print("Starting Advanced Chat Bot...")
    app.run()
