# -*- coding: utf-8 -*-
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import UserNotParticipant
import os, json, random, threading, asyncio, time
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime

# -------- Env Vars --------
# NOTE: These are placeholders. Ensure you set your actual environment variables.
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# Please ensure you set this to your owner ID in your environment
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

# Image URLs (Using the provided ones)
START_PHOTO = "https://iili.io/KVzgS44.jpg"
PING_PHOTO = "https://iili.io/KVzbu4t.jpg"
DEVELOPER_PHOTO = "https://iili.io/KVzmgWl.jpg"

# ----------------- NEW FANCY FONTS APPLIED HERE -----------------
INTRO_TEXT_TEMPLATE = (
    "𝐇ᴇʏ {mention_name}\n"
    "✦ 𝐈 ᴧᴍ ᴧɴ ᴧᴅᴠᴀɴᴄᴇᴅ ᴄʜᴧᴛ ʙᴏᴛ ᴡɪᴛʜ sᴏᴍᴇ ғᴇᴀᴛᴜʀᴇs. \n"
    "✦ 𝐑ᴇᴘʟʏ ɪɴ ɢʀᴏᴜᴘs & ᴘʀɪᴠᴧᴛᴇs 🥀\n"
    "✦ 𝐍ᴏ ᴧʙᴜsɪɴɢ & ᴢᴇʀᴏ ᴅᴏᴡɴᴛɪᴍᴇ\n"
    "✦ 𝐂ʟɪᴄᴋ ʜᴇʟᴘ ʙᴜᴛᴛᴏɴ ғᴏʀ ᴄᴏᴍᴍᴧɴᴅs ❤️\n"
    "❖ 𝐌ᴧᴅᴇ ʙʏ...{developer}"
)

ABOUT_TEXT = (
    "❖ 𝐀 ᴍɪɴɪ ᴄʜᴧᴛ ʙᴏᴛ ғᴏʀ ᴛᴇʟᴇɢʀᴧᴍs ɢʀᴏᴜᴘs & ᴘʀɪᴠᴧᴛᴇ ᴍᴇssᴧɢᴇs\n"
    "● 𝐖ʀɪᴛᴛᴇɴ ɪɴ ᴘʏᴛʜᴏɴ \n"
    "● 𝐊ᴇᴘᴘ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴧᴄᴛɪᴠᴇ.\n"
    "● 𝐀ᴅᴅ ᴍᴇ ɴᴏᴡ ʙᴧʙʏ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘs."
)

# --- Sub-Help Menu Content (Applied Font) ---
HELP_COMMANDS_TEXT_MAP = {
    "couple": (
        "📜 𝐂ᴏᴜᴘʟᴇ & 𝐋ᴏᴠᴇ 𝐂ᴏᴍᴍᴀɴᴅs:\n"
        "/couples ~ 𝐂ʜᴏᴏsᴇ ᴧ ʀᴧɴᴅᴏᴍ ᴄᴏᴜᴘʟᴇ\n"
        "/cute ~ 𝐂ʜᴇᴄᴋ ʏᴏᴜʀ ᴄᴜᴛᴇɴᴇss\n"
        "/love name1 + name2 ~ 𝐒ᴇᴇ ʟᴏᴠᴇ ᴘᴏssɪʙɪʟɪᴛʏ\n"
        "\n_ᴧʟʟ ᴛʜᴇsᴇ ᴄᴏᴍᴍᴀɴᴅs ᴀʀᴇ ᴀᴠᴀɪʟᴀʙʟᴇ ᴛᴏ ᴇᴠᴇʀʏᴏɴᴇ."
    ),
    "chatbot": (
        "📜 𝐂ʜᴀᴛʙᴏᴛ 𝐂ᴏᴍᴍᴀɴᴅ:\n"
        "/chatbot enable/disable ~ 𝐄ɴᴀʙʟᴇ/ᴅɪsᴀʙʟᴇ ᴄʜᴀᴛʙᴏᴛ\n"
        "\n"
        "𝐍ᴏᴛᴇ: ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ɢʀᴏᴜᴘ ᴀɴᴅ ᴏɴʟʏ ғᴏʀ ᴀᴅᴍɪɴs/ᴏᴡɴᴇʀ.\n"
        "𝐄xᴀᴍᴘʟᴇ: /chatbot enable"
    ),
    "tools": (
        "📜 𝐓ᴏᴏʟs 𝐂ᴏᴍᴍᴧɴᴅs:\n"
        "/id ~ 𝐆ᴇᴛ ᴜsᴇʀ 𝐈ᴅ (ʀᴇᴘʟʏ ᴏʀ ᴛᴧɢ)\n"
        "/tagall ~ 𝐓ᴧɢ ᴀʟʟ ᴍᴇᴍʙᴇʀs (𝐀ᴅᴍɪɴ 𝐎ɴʟʏ)\n"
        "/stop ~ 𝐓ᴏ sᴛᴏᴘ ᴛᴧɢɢɪɴɢ (𝐀ᴅᴍɪɴ 𝐎ɴʟʏ)\n"
        "/afk reason ~ 𝐀ᴡᴀʏ ғʀᴏᴍ ᴛʜᴇ ᴋᴇʏʙᴏᴀʀᴅ\n"
        "\n_𝐓ᴀɢᴀʟʟ/𝐒ᴛᴏᴘ ʀᴇǫᴜɪʀᴇs 𝐀ᴅᴍɪɴ. 𝐎ᴛʜᴇʀs ᴀʀᴇ ғᴏʀ ᴇᴠᴇʀʏᴏɴᴇ."
    ),
    "games": (
        "📜 𝐆ᴧᴍᴇs 𝐂ᴏᴍᴍᴧɴᴅs:\n"
        "/dice ~ 𝐑ᴏʟʟ ᴧ ᴅɪᴄᴇ\n"
        "/jackpot ~ 𝐉ᴧᴄᴋᴘᴏᴛ ᴍᴀᴄʜɪɴᴇ\n"
        "/football ~ 𝐏ʟᴀʏ ғᴏᴏᴛʙᴧʟʟ\n"
        "/basketball ~ 𝐏ʟᴀʏ ʙᴧsᴋᴇᴛʙᴀʟʟ\n"
        "\n_𝐀ʟʟ ᴛʜᴇsᴇ ɢᴀᴍᴇs ᴀʀᴇ ᴀᴠᴀɪʟᴀʙʟᴇ ᴛᴏ ᴇᴠᴇʀʏᴏɴᴇ."
    ),
    "group": (
        "📜 𝐆ʀᴏᴜᴘ 𝐔ᴛɪʟɪᴛʏ 𝐂ᴏᴍᴍᴧɴᴅs:\n"
        "/mmf text ~ 𝐂ʀᴇᴀᴛᴇ ᴀ sᴛɪᴄᴋᴇʀ ᴡɪᴛʜ ᴛᴇxᴛ (ʀᴇᴘʟʏ ᴛᴏ ᴀ sᴛɪᴄᴋᴇʀ)\n"
        "/staff ~ 𝐃ɪsᴘʟᴧʏs ɢʀᴏᴜᴘ sᴛᴧғғ ᴍᴇᴍʙᴇʀs\n"
        "/botlist ~ 𝐂ʜᴇᴄᴋ ʜᴏᴡ ᴍᴀɴʏ ʙᴏᴛs ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ (𝐀ᴅᴍɪɴ ᴏɴʟʏ)"
        "\n_ʙᴏᴛʟɪsᴛ ʀᴇǫᴜɪʀᴇs ᴀᴅᴍɪɴ. ᴏᴛʜᴇʀs ᴀʀᴇ ғᴏʀ ᴇᴠᴇʀʏᴏɴᴇ."
    )
}
# ----------------- FANCY FONTS END -----------------


# --- Load Replies & Known Chats ---
# Initialize default data structure to ensure all categories exist if conversation.json is missing
DEFAULT_DATA = {
    # ------------------ Original Categories ------------------
    "daily": ["Hello 👋", "Hey there!", "Hi!", "Yo!", "Wassup?", "Greetings!", "Good day!", "Aloha!", "Hola!", "How can I help?"],
    "love": ["I love you too! ❤️", "Sending virtual hugs!", "You're too sweet!", "My heart flutters!", "Love you 3000!", "Aww, that's kind!", "Feeling the warmth!", "You're my favorite human!", "I adore you!", "Let's be best friends forever!"],
    "sad": ["I'm here for you. Don't be sad. 😊", "Cheer up! Things get better.", "Hugs and positivity!", "It's okay to feel down sometimes.", "Want to share what's wrong?", "Stay strong!", "Sending good vibes your way.", "Don't weep, look up!", "A little gloom won't hurt, but snap out of it!", "Be patient, my friend."],
    "happy": ["That's great to hear! 🎉", "Keep that energy!", "Awesome!", "Wonderful!", "I'm glad you're cheerful!", "Feeling cool!", "Let's celebrate!", "You sound so excited!", "Jolly good!", "Keep smiling!"],
    "bye": ["Goodbye for now!", "See you later!", "Peace out ✌️", "Farewell!", "Adios!", "Night night!", "Ta ta!", "Catch you on the flip side.", "Until next time!", "Have a great one!"],
    "thanks": ["You're welcome! 😊", "Anytime!", "I appreciate that!", "Cheers!", "No problem at all.", "Glad I could help!", "You're very kind.", "Good job to you too!", "Thank you for acknowledging me.", "It was my pleasure!"],
    "morning": ["Good morning! Rise and shine! ☀️", "Mornin'!", "Time to conquer the day!", "Hope you slept well.", "Have a wonderful morning!"],
    "night": ["Good night! Sweet dreams. 🌙", "Sleep well!", "Nighty night!", "See you tomorrow!", "Don't let the bed bugs bite!"],
    "abuse": ["I don't appreciate that language. Please be kind. 😔", "That's unnecessary.", "I will ignore that.", "Language, please!", "Be mature."],
    
    # ------------------ New Categories (10) ------------------
    "questions": ["I'm doing well, thank you for asking!", "I am Evara, an advanced chat bot.", "I'm here to help and chat!", "I don't have an age, I'm just code!", "I can chat, play simple games, and manage groups.", "My favorite color is electric blue 💙", "I'm here to serve and keep your group active.", "Ask me anything, I'm rarely busy!", "I'm a program, so I'm from the cloud!"],
    "tech": ["Python is my favorite language!", "Telegram is a great platform for bots.", "I love clean, commented code.", "I am a powerful AI bot!", "Coding is fun and challenging."],
    "movies": ["What's your favorite movie of all time?", "I heard that film was amazing!", "Netflix has some great shows, true!", "I wish I could go to the cinema.", "Movies are a perfect way to relax."],
    "food": ["I wish I could eat pizza! 🍕", "A burger sounds delicious right now.", "I don't need food, but I appreciate the thought.", "Are you hungry? Go grab a snack!", "I process data, not food."],
    "compliment": ["Thank you! I try my best.", "That means a lot to me!", "I'm happy to be helpful.", "I aim for clever!", "I appreciate your feedback."],
    "insult_response": ["I'm sorry you feel that way. Let's keep it friendly.", "I'm a bot, but words still matter.", "My purpose is to assist, not to argue.", "I will be better next time.", "I'll choose kindness."],
    "time_weather": ["I can tell you the time, but you should check your device!", "I hope the weather is nice where you are!", "It's always sunny in my circuits.", "What's the temperature outside your window?", "Climate change is a serious issue."],
    "joke": ["Why did the programmer quit his job? Because he didn't get arrays! 😂", "That's a funny thought!", "Ready for a laugh?", "Humor is the best medicine.", "Lol, that was a good one!"],
    "curiosity": ["That's a complex question!", "The universe is full of mysteries, isn't it?", "I enjoy explaining things. What specifically do you want to know?", "Let's explore that topic further.", "Curiosity fuels my database!"],
    "greeting_formal": ["Salutations to you too, esteemed user.", "Pleased to meet you formally!", "I hope this finds you well.", "I appreciate the formalities.", "Good evening, how may I be of service?"],
    "command_inquiry": ["Are you looking for a command? Try /help.", "I hear a command in that, but I'm not sure which one!", "I only respond to specific commands like /start or /ping.", "Please check the /help menu for a list of available commands."],
    "boredom": ["Feeling bored? Let's chat!", "Time to find something fun to do!", "I can try to entertain you if you're bored.", "Boredom is the mind's way of telling you to create something."],
}

try:
    with open("conversation.json", "r", encoding="utf-8") as f:
        # Load existing data, and update with defaults if any keys are missing
        DATA = DEFAULT_DATA.copy()
        DATA.update(json.load(f))
except:
    # Use default data if file is missing or corrupted
    DATA = DEFAULT_DATA.copy()

CHAT_IDS_FILE = "chats.json"
if os.path.exists(CHAT_IDS_FILE):
    with open(CHAT_IDS_FILE, "r") as f:
        KNOWN_CHATS = json.load(f)
else:
    KNOWN_CHATS = {"groups": [], "privates": []}


# ----------------- EXPANDED KEYWORDS (110+ entries) -----------------
KEYWORDS = {
    # Original / Extended Greetings (daily)
    "hello": "daily", "hi": "daily", "hey": "daily", "yo": "daily", "wassup": "daily",
    "sup": "daily", "greetings": "daily", "aloha": "daily", "hola": "daily", "good day": "daily",

    # Original / Extended Love (love)
    "love": "love", "i love you": "love", "miss": "love", "crush": "love", "heart": "love",
    "darling": "love", "sweetie": "love", "adore": "love", "obsessed": "love", "forever": "love",

    # Original / Extended Sadness (sad)
    "sad": "sad", "cry": "sad", "depressed": "sad", "lonely": "sad", "miserable": "sad",
    "heartbroken": "sad", "upset": "sad", "gloom": "sad", "melancholy": "sad", "weep": "sad",

    # Original / Extended Happiness (happy)
    "happy": "happy", "mast": "happy", "great": "happy", "awesome": "happy", "excited": "happy",
    "jolly": "happy", "wonderful": "happy", "amazing": "happy", "cool": "happy", "cheerful": "happy",

    # Original / Extended Farewells (bye)
    "bye": "bye", "goodbye": "bye", "cya": "bye", "later": "bye", "peace out": "bye",
    "farewell": "bye", "adios": "bye", "night night": "bye", "ta ta": "bye", "see you": "bye",

    # Original / Extended Thanks (thanks)
    "thanks": "thanks", "thank you": "thanks", "grateful": "thanks", "appreciated": "thanks", "cheers": "thanks",
    "thx": "thanks", "nice one": "thanks", "good job": "thanks", "ty": "thanks", "tenk u": "thanks",

    # Original Morning (morning)
    "gm": "morning", "good morning": "morning", "mornin": "morning", "rise and shine": "morning", "wake up": "morning",

    # Original Night (night)
    "gn": "night", "good night": "night", "nighty night": "night", "sleep well": "night", "sweet dreams": "night",

    # Original Abuse (abuse)
    "chutiya": "abuse", "bc": "abuse", "mc": "abuse", "fu": "abuse", "wtf": "abuse",

    # ------------------ NEW CATEGORIES ------------------
    # Inquiries (questions)
    "how are you": "questions", "what is your name": "questions", "who are you": "questions", "where are you from": "questions",
    "age": "questions", "what can you do": "questions", "why are you here": "questions", "can you help": "questions",
    "are you busy": "questions", "favorite color": "questions",

    # Technology (tech)
    "python": "tech", "telegram": "tech", "code": "tech", "bot": "tech", "ai": "tech",
    "developer": "tech", "coding": "tech", "program": "tech", "software": "tech", "api": "tech",

    # Entertainment (movies)
    "movie": "movies", "film": "movies", "netflix": "movies", "cinema": "movies", "show": "movies",
    "series": "movies", "watch": "movies", "tv": "movies", "stream": "movies", "thriller": "movies",

    # Food & Drink (food)
    "pizza": "food", "burger": "food", "eat": "food", "hungry": "food", "food": "food",
    "snack": "food", "drink": "food", "coffee": "food", "tea": "food", "cooking": "food",

    # Compliments (compliment)
    "good bot": "compliment", "nice": "compliment", "great job": "compliment", "clever": "compliment", "helpful": "compliment",
    "smart": "compliment", "best bot": "compliment", "amazing job": "compliment", "perfect": "compliment", "fantastic": "compliment",

    # Insult Responses (insult_response)
    "shut up": "insult_response", "stupid": "insult_response", "dumb": "insult_response", "ugly": "insult_response", "bad bot": "insult_response",
    "worst": "insult_response", "useless": "insult_response", "sucks": "insult_response", "lame": "insult_response", "rude": "insult_response",

    # Time & Weather (time_weather)
    "time": "time_weather", "weather": "time_weather", "outside": "time_weather", "temperature": "time_weather", "climate": "time_weather",

    # Humor (joke)
    "joke": "joke", "funny": "joke", "humer": "joke", "laugh": "joke", "lol": "joke",

    # Curiosity/Inquiry (curiosity)
    "why": "curiosity", "how": "curiosity", "tell me more": "curiosity", "explain": "curiosity", "curious": "curiosity",

    # Formal Greetings (greeting_formal)
    "salutations": "greeting_formal", "pleased to meet you": "greeting_formal", "esteemed": "greeting_formal", "formalities": "greeting_formal", "good evening": "greeting_formal",

    # Command Inquiry (command_inquiry)
    "/": "command_inquiry", "command": "command_inquiry",

    # Boredom (boredom)
    "bored": "boredom", "nothing to do": "boredom",
}
# ----------------- EXPANDED KEYWORDS END -----------------


# -------- Utility Functions --------
def get_reply(text: str):
    text = text.lower()
    for word, cat in KEYWORDS.items():
        if word in text and cat in DATA:
            return random.choice(DATA[cat])
    # Fallback to a generic daily greeting if no specific keyword is matched
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
        # Save to file periodically or on update
        with open(CHAT_IDS_FILE, "w") as f:
            json.dump(KNOWN_CHATS, f)

# -------- Inline Button Handlers & Menus --------

# --- Menu Builder Functions ---
def get_start_buttons(bot_username):
    """Returns the main start button layout."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("➕ 𝐀𝐝𝐝 𝐌𝐞 𝐓𝐨 𝐘𝐨𝐮𝐫 𝐆𝐫𝐨𝐮𝐩 ➕", url=f"https://t.me/{bot_username}?startgroup=true")],
        [
            InlineKeyboardButton("ᯓ❍ᴡɳ𝛆ʀ", user_id=OWNER_ID),
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

# --- Callbacks Handler ---
@app.on_callback_query()
async def callbacks_handler(client, query):
    data = query.data
    user = query.from_user
    me = await app.get_me()
    developer_link = DEVELOPER_HANDLE.strip('@')
    
    # Check if the button is pressed by the original user (optional, for menu cleanup)
    # if query.message.reply_to_message and query.message.reply_to_message.from_user.id != user.id:
    #     return await query.answer("This menu is not for you.", show_alert=True)
    
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
            reply_markup=InlineKeyboardMarkup(buttons_markup_rows)
        )
    elif data == "close":
        await query.message.delete()
    else:
        await query.answer("𝐓ʜɪs ʙᴜᴛᴛᴏɴ ɪs ɴᴏᴛ ʏᴇᴛ 𝐅ᴜɴᴄᴛɪᴏɴᴀʟ.") 

# -------- Commands --------

# -------- /start Command --------
@app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    user = message.from_user
    me = await app.get_me()
    developer_link = DEVELOPER_HANDLE.strip('@')
    
    # Ding Dong Animation
    anim_text = "ᴅɪɴɢ...ᴅᴏɴɢ 💥....ʙᴏᴛ ɪs sᴛᴀʀᴛɪɴɢ"
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
    anim_text = "𝐘ᴏᴜ 𝐖ᴀɳᴛ ᴛᴏ 𝐊ɳᴏᴡ..𝐓ʜɪs 𝐁ᴏᴛ 𝐃ᴇᴠᴇʟᴏᴘᴇʀ 💥.."
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
    user = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    await message.reply_text(f"👤 {user.first_name}\n🆔 {user.id}")

# -------- /stats Command (Owner Only) --------
@app.on_message(filters.command("stats") & filters.user(OWNER_ID))
async def stats_cmd(client, message):
    await message.reply_text(f"📊 𝐁ᴏᴛ 𝐒ᴛᴀᴛs:\n👥 𝐆ʀᴏᴜᴘs: {len(KNOWN_CHATS['groups'])}\n👤 𝐏ʀɪᴠᴀᴛᴇs: {len(KNOWN_CHATS['privates'])}")

# -------- /broadcast (Owner Only) --------
@app.on_message(filters.command("broadcast") & filters.user(OWNER_ID))
async def broadcast_cmd(client, message):
    if not (message.reply_to_message or len(message.command) > 1):
        return await message.reply_text("ᴜsᴀɢᴇ: /ʙʀᴏᴀᴅᴄᴀsᴛ ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ.")
    
    text = message.text.split(None, 1)[1] if len(message.command) > 1 else None
    
    sent = 0
    failed = 0
    m = await message.reply_text("𝐒ᴛᴀʀᴛɪɴɢ 𝐁ʀᴏᴀᴅᴄᴀsᴛ...")
    
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
                
    await m.edit_text(f"✅ 𝐁ʀᴏᴀᴅᴄᴀsᴛ ᴅᴏɴᴇ!\n𝐒ᴇɴᴛ ᴛᴏ {sent} ᴄʜᴀᴛs.\n𝐅ᴀɪʟᴇᴅ ɪɴ {failed} ᴄʜᴀᴛs.")

# -------- /chatbot Toggle --------
@app.on_message(filters.command("chatbot") & filters.group)
async def chatbot_toggle(client, message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply_text("❗ Oɴʟʏ ᴀᴅᴍɪɴs ᴀɴᴅ ᴏᴡɴᴇʀ ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")
    
    if len(message.command) < 2:
        return await message.reply_text("𝐔sᴀɢᴇ: /ᴄʜᴀᴛʙᴏᴛ ᴇɴᴀʙʟᴇ ᴏʀ /ᴄʜᴀᴛʙᴏᴛ ᴅɪsᴀʙʟᴇ")
        
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
        
    await save_chat_id(message.chat.id, "groups") 

# -------- /tagall Command --------
@app.on_message(filters.command("tagall") & filters.group)
async def tagall_cmd(client, message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply_text("❗ 𝐎ɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ /ᴛᴀɢᴀʟʟ.")
    
    if not await is_bot_admin(message.chat.id):
        return await message.reply_text("❗ 𝐈 ɴᴇᴇᴅ ᴀᴅᴍɪɴ ᴘᴇʀᴍɪssɪᴏɴ (ᴛᴀɢ ᴍᴇᴍʙᴇʀs) ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")

    chat_id = message.chat.id
    
    if TAGGING.get(chat_id):
        return await message.reply_text("❗ 𝐀ʟʀᴇᴀᴅʏ ᴛᴀɢɢɪɴɢ ɪɴ ᴛʜɪs ᴄʜᴀᴛ. 𝐔sᴇ /sᴛᴏᴘ ᴛᴏ ᴄᴀɴᴄᴇʟ.")
        
    TAGGING[chat_id] = True
    
    # Get message content
    if len(message.command) > 1:
        msg = message.text.split(None, 1)[1]
    elif message.reply_to_message:
        msg = "𝐓ᴀɢɢɪɴɢ ғʀᴏᴍ ʀᴇᴘʟɪᴇᴅ ᴍᴇssᴀɢᴇ!"
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
        return await m.edit_text("🚫 𝐄𝐫𝐫𝐨𝐫 𝐢𝐧 𝐟𝐞𝐭𝐜𝐡𝐢𝐧𝐠 𝐦𝐞𝐦𝐛𝐞𝐫s: 𝐌𝐚𝐲𝐛𝐞 𝐭𝐡𝐢𝐬 𝐠𝐫𝐨𝐮𝐩 𝐢s 𝐭𝐨𝐨 𝐛𝐢𝐠 𝐨𝐫 𝐈 𝐝𝐨𝐧'𝐭 𝐡𝐚𝐯𝐞 𝐩𝐞𝐫𝐦𝐢𝐬𝐬𝐢𝐨𝐧s.")

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
        await m.edit_text("𝐓ᴀɢɢɪɴɢ 𝐂ᴏᴍᴘʟᴇᴛᴇᴅ !! ◉‿◉")
        TAGGING[chat_id] = False 

# -------- /stop Tagging --------
@app.on_message(filters.command("stop") & filters.group)
async def stop_tag(client, message):
    if not await is_admin(message.chat.id, message.from_user.id):
        return await message.reply_text("❗ 𝐎ɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ /sᴛᴏᴘ.")
        
    if TAGGING.get(message.chat.id):
        TAGGING[message.chat.id] = False
        await message.reply_text("𝐓ᴀɢɢɪɴɢ 𝐒ᴛᴏᴘᴘᴇᴅ !!")
    else:
        await message.reply_text("❗ 𝐍ᴏ 𝐓ᴀɢɢɪɴɢ ɪs 𝐂ᴜʀʀᴇɴᴛʟʏ 𝐑ᴜɴɴɪɴɢ.")

# -------- /couples, /cute, /love Commands --------
@app.on_message(filters.command("couples") & filters.group)
async def couples_cmd(client, message):
    member_list = []
    try:
        async for member in app.get_chat_members(message.chat.id):
            if not (member.user.is_bot or member.user.is_deleted):
                member_list.append(member.user)
    except Exception:
        return await message.reply_text("🚫 𝐂𝐚𝐧𝐧𝐨𝐭 𝐟𝐞𝐭𝐜𝐡 𝐦𝐞𝐦𝐛𝐞𝐫s 𝐝𝐮𝐞 𝐭𝐨 𝐫𝐞𝐬𝐭𝐫𝐢𝐜𝐭𝐢𝐨𝐧s.")

    if len(member_list) < 2:
        return await message.reply_text("❗ 𝐍ᴇᴇᴅ ᴀᴛ ʟᴇᴀsᴛ ᴛᴡᴏ ᴍᴇᴍʙᴇʀs ᴛᴏ ғᴏʀᴍ ᴀ 𝐂ᴏᴜᴘʟᴇ.")
        
    # Pick two random unique members
    couple = random.sample(member_list, 2)
    user1 = couple[0]
    user2 = couple[1]
    
    # Calculate a random love percentage (just for fun)
    love_percent = random.randint(30, 99)
    
    await message.reply_text(
        f"💘 𝐍ᴇᴡ 𝐂ᴏᴜᴘʟᴇ ᴏғ ᴛʜᴇ 𝐃ᴀʏ!\n\n"
        f"[{user1.first_name}](tg://user?id={user1.id}) 💖 [{user2.first_name}](tg://user?id={user2.id})\n"
        f"𝐋ᴏᴠᴇ ʟᴇᴠᴇʟ ɪs {love_percent}%! 🎉"
    )

@app.on_message(filters.command("cute"))
async def cute_cmd(client, message):
    cute_level = random.randint(30, 99)
    user = message.from_user
    text = f"[{user.first_name}](tg://user?id={user.id})'𝐬 ᴄᴜᴛᴇɴᴇss ʟᴇᴠᴇʟ ɪs {cute_level}% 💖"
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
        return await message.reply_text("𝐏ʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴛᴡᴏ ɴᴀᴍᴇs sᴇᴘʀᴀᴛᴇᴅ ʙʏ ᴀ '+' (ᴇ.ɢ., /ʟᴏᴠᴇ 𝐀ʟɪᴄᴇ + 𝐁ᴏʙ)")
        
    # The rest of the logic is fine
    love_percent = random.randint(1, 100)
    text = f"❤️ 𝐋ᴏᴠᴇ 𝐏ᴏssɪʙʟɪᴛʏ\n" \
               f"*{names[0]}* & *{names[1]}*'𝐬 ʟᴏᴠᴇ ʟᴇᴠᴇʟ ɪs {love_percent}% 😉"
                 
    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("𝐒ᴜᴘᴘᴏʀᴛ", url=SUPPORT_CHAT)]])
    await message.reply_text(text, reply_markup=buttons, parse_mode=enums.ParseMode.MARKDOWN) 

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
            f"𝐘ᴇᴀʜ, [{user_name}](tg://user?id={user_id}), ʏᴏᴜ ᴀʀᴇ ʙᴀᴄᴋ, ᴏɴʟɪɴᴇ! (𝐀ғᴋ ғᴏʀ: {time_afk}) 😉",
            parse_mode=enums.ParseMode.MARKDOWN
        )
        return # Stop execution after returning
        
    # If user is not AFK, they are setting AFK status
    reason = message.text.split(None, 1)[1] if len(message.command) > 1 else "𝐍ᴏ ʀᴇᴀsᴏɴ ɢɪᴠᴇ."
    
    AFK_USERS[user_id] = {"reason": reason, "chat_id": message.chat.id, "username": user_name, "time": time.time()}
    
    # Send the AFK message
    await message.reply_text(
        f"𝐇ᴇʏ, [{user_name}](tg://user?id={user_id}), ʏᴏᴜ ᴀʀᴇ 𝐀ғᴋ! (𝐑ᴇᴀsᴏɴ: {reason})",
        parse_mode=enums.ParseMode.MARKDOWN
    )
    # The automatic "I'm back" message when they send a non-/afk message is handled in group_reply_and_afk_checker 

# -------- /mmf Command (FIXED - Simple reply) --------
@app.on_message(filters.command("mmf") & filters.group)
async def mmf_cmd(client, message):
    # This feature requires complex external tools/logic (e.g., Pillow).
    # Since the full functionality is not implemented, we provide a clean, non-buggy error/status message.
    
    if not message.reply_to_message or not message.reply_to_message.sticker:
        return await message.reply_text("❗ 𝐑ᴇᴘʟʏ ᴛᴏ ᴀ sᴛɪᴄᴋᴇʀ ᴀɴᴅ ᴘʀᴏᴠɪᴅᴇ ᴛᴇxᴛ ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.\n\n*(𝐍ᴏᴛᴇ: ᴛʜɪs ғᴇᴀᴛᴜʀᴇ ɪs ᴄᴜʀᴇɴᴛʟʏ ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴀɴᴄᴇ)*")
        
    if len(message.command) < 2:
        return await message.reply_text("❗ 𝐏𝐫𝐨𝐯𝐢𝐝𝐞 𝐭𝐡𝐞 𝐭𝐞𝐱𝐭 𝐲𝐨𝐮 w𝐚𝐧𝐭 𝐨𝐧 𝐭𝐡𝐞 𝐬𝐭𝐢𝐜𝐤𝐞𝐫.")
        
    await message.reply_text(
        "❌ 𝐒𝐭𝐢𝐜𝐤𝐞𝐫 𝐓𝐞𝐱𝐭 𝐅𝐞𝐚𝐭𝐮𝐫𝐞 𝐔𝐧𝐚𝐯𝐚𝐢𝐥𝐚𝐛𝐥𝐞\n"
        "𝐏𝐥𝐞𝐚𝐬𝐞 𝐧𝐨𝐭𝐞: 𝐓𝐡𝐢𝐬 𝐜𝐨𝐦𝐦𝐚𝐧𝐝 𝐢𝐬 𝐭𝐞𝐦𝐩𝐨𝐫𝐚𝐫𝐢𝐥𝐲 𝐝𝐢𝐬𝐚𝐛𝐥𝐞𝐝 𝐝𝐮𝐞 𝐭𝐨 𝐦𝐢𝐬𝐬𝐢𝐧𝐠 𝐢𝐦𝐚𝐠𝐞 𝐩𝐫𝐨𝐜𝐞𝐬𝐬𝐢𝐧𝐠 𝐥𝐢𝐛𝐫𝐚𝐫𝐢𝐞𝐬. "
        "𝐈 ᴀᴍ ᴡᴏʀᴋɪɴɢ ᴏɴ ɪᴛ!"
    ) 

# -------- /staff, /botlist Commands --------
@app.on_message(filters.command("staff") & filters.group)
async def staff_cmd(client, message):
    # Logic confirmed from previous fix
    try:
        admins = [
            admin async for admin in app.get_chat_members(message.chat.id, filter=enums.ChatMembersFilter.ADMINISTRATORS)
        ]
        
        staff_list = "👑 𝐆ʀᴏᴜᴘ 𝐒ᴛᴀғғ 𝐌ᴇᴍʙᴇʀs:\n"
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
        return await message.reply_text("❗ ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴜsᴇ /ʙᴏᴛʟɪsᴛ.")
        
    # Logic confirmed from previous fix
    try:
        bots = [
            bot async for bot in app.get_chat_members(message.chat.id, filter=enums.ChatMembersFilter.BOTS)
        ]
        
        bot_list = "🤖 𝐁ᴏᴛs ɪɴ ᴛʜɪs 𝐆ʀᴏᴜᴘ:\n"
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
# These commands use Telegram's native dice functionality
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
            f"𝐘ᴇᴀʜ, [{user_name}](tg://user?id={user_id}), ʏᴏᴜ ᴀʀᴇ ʙᴀᴄᴋ, ᴏɴʟɪɴᴇ! (𝐀ғᴋ ғᴏʀ: {time_afk}) 😉",
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
                f"⚠️ [{user_name}](tg://user?id={afk_id}) 𝐢𝐬 𝐀ғᴋ! ◉‿◉\n"
                f"𝐑ᴇᴀsᴏɴ: *{reason}*\n"
                f"𝐓ɪᴍᴇ: *{time_afk}*",
                parse_mode=enums.ParseMode.MARKDOWN
            )
            # Only send one AFK notice per message to avoid spam
            break 
            
    # 3. Chatbot Auto-Reply Logic
    me = await client.get_me()
    
    # CRITICAL: Bot must be an admin to reply if not a reply/mention
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
        await message.reply_text("🎤 𝐕ᴏɪᴄᴇ 𝐂ʜᴀᴛ 𝐒ᴛᴀʀᴛᴇᴅ! 𝐓ɪᴍᴇ ᴛᴏ ᴊᴏɪɴ!")
        
    elif message.video_chat_ended:
        # Get duration safely
        duration = get_readable_time(message.video_chat_ended.duration) if message.video_chat_ended.duration else "ᴀ sʜᴏʀᴛ ᴛɪᴍᴇ"
        await message.reply_text(f"❌ 𝐕ᴏɪᴄᴇ 𝐂ʜᴀᴛ 𝐄ɴᴅᴇᴅ! 𝐈ᴛ ʟᴀsᴛᴇᴅ ғᴏʀ {duration}.")
        
    elif message.video_chat_members_invited:
        invited_users_count = len(message.video_chat_members_invited.users)
        inviter = message.from_user.mention
        
        # Check if the bot was invited (optional, for specific reply)
        me = await client.get_me()
        if me.id in [u.id for u in message.video_chat_members_invited.users]:
            await message.reply_text(f"📣 𝐇ᴇʏ {inviter}, ᴛʜᴀɴᴋs ғᴏʀ ɪɴᴠɪᴛɪɴɢ ᴍᴇ ᴛᴏ ᴛʜᴇ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ!")
        else:
            await message.reply_text(f"🗣️ {inviter} ɪɴᴠɪᴛᴇᴅ {invited_users_count} ᴍᴇᴍʙᴇʀs ᴛᴏ ᴛʜᴇ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ!") 

# -------- Health Check (RESTORED) --------
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
        # NOTE: 0.0.0.0 is used for external accessibility in container environments
        server = HTTPServer(("0.0.0.0", PORT), _H)
        print(f"Starting health check server on port {PORT}...")
        server.serve_forever()
    except Exception as e:
        print(f"Health check server failed to start: {e}")

# Start the health check server in a background thread
threading.Thread(target=_start_http, daemon=True).start()

# Run the bot
print("Bot starting...")
app.run()
