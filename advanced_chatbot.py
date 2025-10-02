# -*- coding: utf-8 -*-
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
import random, time
from datetime import datetime

# ----------------- CONFIG -----------------
API_ID = 29332974        # Apka API ID
API_HASH = "a5cf51e5143270a60178102b35a43ade"
BOT_TOKEN = "8298863467:AAGQywrOMSu3K6I_vmmEj9-IZi82PNrZZKE"
OWNER_ID = 7589623332
BOT_USERNAME = "@ChattingPro_Bot"

bot = Client("advanced_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

afk_users = {}
chatbot_status = {}

# ----------------- ADMIN CHECK -----------------
async def is_admin(message: Message):
    try:
        member = await bot.get_chat_member(message.chat.id, message.from_user.id)
        return member.status in ("administrator", "creator")
    except:
        return False

# ----------------- INTRO -----------------
@bot.on_message(filters.command("start"))
async def start(client, message: Message):
    if message.chat.type != "private" and not await is_admin(message):
        return
    intro_photo = "https://iili.io/KVzgS44.jpg"
    intro_text = (
        f"ᴅɪɴɢ ᴅᴏɴɢ 🎶\n\n"
        f"ʜєʏ {message.from_user.mention}\n"
        "✦ ɪ ᴧϻ ᴧᴅᴠᴧηᴄєᴅ ᴄʜᴧᴛ ʙσᴛ ᴡɪᴛʜ sσϻє ғєᴧᴛᴜʀєs. ✦\n"
        "✦ ʀєᴘʟʏ ɪη ɢʀσᴜᴘs & ᴘʀɪᴠᴧᴛє🥀\n"
        "✦ ηᴏ ᴧʙᴜsɪηɢ & zєʀσ ᴅσᴡηᴛɪϻє\✦ ᴄʟɪᴄᴋ ʜєʟᴘ ʙᴜᴛᴛση ғσʀ ʜєʟᴘs❤️❖ ϻᴧᴅє ʙʏ {BOT_USERNAME}"
    )
    intro_buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("+ 𝐀ᴅᴅ ᴍᴇ ʏᴏᴜʀ 𝐆ʀᴏᴜᴘ +", url=f"https://t.me/{BOT_USERNAME[1:]}?startgroup=true")],
        [InlineKeyboardButton("ᯓ❍ᴡ𝛈ᴇʀ", url=f"https://t.me/{OWNER_ID}"),
         InlineKeyboardButton("◉ 𝐀ʙᴏᴜᴛ", callback_data="about_section")],
        [InlineKeyboardButton("◉ 𝐇ᴇʟᴘ & 𝐂ᴏᴍᴍᴀɴᴅs", callback_data="help_section")]
    ])
    await message.reply_photo(intro_photo, caption=intro_text, reply_markup=intro_buttons)

# ----------------- ABOUT -----------------
@bot.on_callback_query(filters.regex("about_section"))
async def about_section(client, callback):
    photo = "https://iili.io/KVzgS44.jpg"
    text = (
        "❖ ᴧ ϻɪηɪ ᴄʜᴧᴛ ʙᴏᴛ ғᴏʀ ᴛᴇʟᴇɢʀᴀϻ ɢʀᴏᴜᴘs & ᴘʀɪᴠᴧᴛᴇ\n"
        "● ᴡʀɪᴛᴛᴇη ɪη ᴘʏᴛʜᴏɴ\n"
        "● ᴋєєᴘ ʏσᴜʀ ᴧᴄᴛɪᴠє ɢʀσᴜᴘ. ● ᴧᴅᴅ ϻє ηᴏᴡ ʙʟᴀʙʏ ɪɴ ʏᴏᴜʀ ɢʀσᴜᴘs"
    )
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("𝐄ᴠᴀʀᴀ 𝐒ᴜᴘᴘᴏʀᴛ 𝐂ʜᴀᴛ", url="https://t.me/Evara_Support_Chat"),
         InlineKeyboardButton("𝐔ρ∂ᴀᴛᴇs", url="https://t.me/Evara_Updates")],
        [InlineKeyboardButton("𝐁ᴀᴄᴋ", callback_data="start_back"),
         InlineKeyboardButton("𝐂ʟᴏsᴇ", callback_data="close_section")]
    ])
    await callback.message.edit_media(media=photo, caption=text, reply_markup=buttons)

# ----------------- HELP & COMMANDS -----------------
@bot.on_callback_query(filters.regex("help_section"))
async def help_section(client, callback):
    photo = "https://iili.io/KVzgS44.jpg"
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("ᴄᴏᴜᴘʟᴇ", callback_data="cmd_couple"),
         InlineKeyboardButton("ᴄʜᴀᴛʙᴏᴛ", callback_data="cmd_chatbot")],
        [InlineKeyboardButton("ᴛᴏᴏʟs", callback_data="cmd_tools"),
         InlineKeyboardButton("ɢᴀᴍᴇs", callback_data="cmd_games")],
        [InlineKeyboardButton("sᴛɪᴄᴋᴇʀs", callback_data="cmd_stickers"),
         InlineKeyboardButton("ɢʀᴏᴜᴘs", callback_data="cmd_groups")]
    ])
    await callback.message.edit_media(media=photo, caption="", reply_markup=buttons)

# ----------------- BACK & CLOSE -----------------
@bot.on_callback_query(filters.regex("close_section"))
async def close_section(client, callback):
    await callback.message.delete()

@bot.on_callback_query(filters.regex("start_back"))
async def start_back(client, callback):
    await start(client, callback.message)

# ----------------- AFK -----------------
@bot.on_message(filters.group & filters.text)
async def afk_check(client, message: Message):
    if message.from_user.id in afk_users:
        await message.reply_text(f"ʜᴇʏ {message.from_user.mention}, ʏᴏᴜ ᴀғᴋ !!")
    for user_id in afk_users.keys():
        if message.reply_to_message and message.reply_to_message.from_user.id == user_id:
            await message.reply_text(f"ᴛʜɪs ᴜsᴇʀ ɪs ᴀғᴋ !! ◉‿◉")

# ----------------- FUN COMMANDS -----------------
@bot.on_message(filters.command("Couples") & filters.group)
async def couples_cmd(client, message):
    members = [m.user for m in await client.get_chat_members(message.chat.id)]
    if len(members) < 2: return
    couple = random.sample(members, 2)
    await message.reply_text(f"💞 Couple: {couple[0].mention} ❤️ {couple[1].mention}")

@bot.on_message(filters.command("cute") & filters.group)
async def cute_cmd(client, message):
    percent = random.randint(0, 100)
    await message.reply_text(f"ʏᴏᴜʀ ᴄᴜᴛᴇɴᴇss ʟᴇᴠᴇʟ ɪs {percent}% 😉\n[ᴍᴏʀᴇ ʜᴇʟᴘ](https://t.me/Evara_Support_Chat)")

@bot.on_message(filters.command("love") & filters.group)
async def love_cmd(client, message):
    try:
        names = message.text.split(None, 2)[1:]
        percent = random.randint(0,100)
        await message.reply_text(f"ʟᴏᴠᴇ ᴘᴏssɪʙɪʟɪᴛʏ ɪs {percent}% 😉 for {names[0]} + {names[1]}\n[ᴍᴏʀᴇ ʜᴇʟᴘ](https://t.me/Evara_Support_Chat)")
    except:
        await message.reply_text("Use: /love name1 name2")

# ----------------- CHATBOT -----------------
@bot.on_message(filters.command("chatbot") & filters.group)
async def chatbot_toggle(client, message):
    if len(message.text.split()) < 2:
        await message.reply_text("Use /chatbot enable OR /chatbot disable")
        return
    action = message.text.split()[1].lower()
    if action == "enable":
        chatbot_status[message.chat.id] = True
        await message.reply_text("ᴄʜᴀᴛʙᴏᴛ sᴛᴀᴛᴜs ɪs ᴇɴᴀʙʟᴇ ✰")
    elif action == "disable":
        chatbot_status[message.chat.id] = False
        await message.reply_text("ᴄʜᴀᴛʙᴏᴛ sᴛᴀᴛᴜs ɪs ᴅɪsᴀʙʟᴇ ✰")

# ----------------- /Devloper -----------------
@bot.on_message(filters.command("Devloper"))
async def developer_cmd(client, message):
    photo = "https://iili.io/KVzmgWl.jpg"
    text = "ʙᴏᴛ ᴅᴇᴠʟᴏᴘᴇʀ ɪs"
    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("𝐃ᴇᴠʟᴏᴘᴇʀ ღ", url=f"https://t.me/{BOT_USERNAME[1:]}")]])
    await message.reply_photo(photo, caption=text, reply_markup=buttons)

# ----------------- PING -----------------
@bot.on_message(filters.command("ping") & filters.group)
async def ping_cmd(client, message):
    start_time = time.time()
    msg = await message.reply_text("ᴘɪɴɢɪɴɢ... sᴛᴀʀᴛᴇᴅ.. ´･ᴗ･` ᴘɪɴɢ.. ᴘᴏɴɢ ⚡")
    end_time = time.time()
    uptime = datetime.now().strftime("%H:%M:%S")
    await msg.edit(f"ᴘɪɴɢ ➳ {round((end_time - start_time)*1000)}ms\nᴜᴘᴛɪᴍᴇ ➳ {uptime}")

# ----------------- RUN -----------------
bot.run()
