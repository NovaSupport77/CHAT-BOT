# -*- coding: utf-8 -*-
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import UserNotParticipant
import os, json, random, threading, asyncio, time
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime

# -------- Env Vars --------
# NOTE: These values must be set in your execution environment.
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

# ----------------- STICKER REPLIES (USING PLACEHOLDERS) -----------------
# NOTE: Since actual file IDs cannot be fetched here, these are placeholders
# based on typical ID structures. Replace them with real sticker file IDs
# from the packs you provided for them to work correctly.
STICKER_REPLIES = {
    "love": [
        "CAACAgUAAxkBAAICaWc0R6q1xS4X2Y4n0n9d_s_g5t_bAAIeBAACd_vRBP4k1lK-3j9YNAQ", 
        "CAACAgUAAxkBAAICa2c0R7TzC6d8jB_X5p6Q0lF9s9cEAAIfBAACd_vRBCV_kE_3R5VpNAQ" 
    ],
    "sad": [
        "CAACAgUAAxkBAAICdGc0R8L47n-eR8Zf7wL0z6M_f0JbAAIkBAACd_vRBBWwH2dJ5wE4NAQ", # Crying/Sad
        "CAACAgUAAxkBAAICbGc0R7U3nK-1lO8iL4q3nIe9f6mEAAInBAACd_vRBHzqT8tUv1oXNAQ"  # Comfort/Hug
    ],
    "happy": [
        "CAACAgUAAxkBAAICbWc0R7k_T6e8B6Fv8H2o0sZ3f7tBAAIhBAACd_vRBH-yL2H2Z33fNAQ", 
        "CAACAgUAAxkBAAICcWc0R8CjS4l9eJ4t-x7K1D5d_f1JAAIjBAACd_vRBCV_kE_3R5VpNAQ"
    ],
    "question": [
        "CAACAgUAAxkBAAICd2c0R8hL3w1zL2h7r7d2F7r0g5wOAAIlBAACd_vRBBjF4nUe_gNANAQ" # Thinking/Doubt
    ],
    "abuse": [
        "CAACAgUAAxkBAAICeWc0R8rJ9o_lB2qH2b2o7lG4j9sTAAImBAACd_vRBL5Y9n6v8u1cNAQ" # Angry/Warning
    ],
    "daily": [
        "CAACAgUAAxkBAAICfGc0R81b1y5eB1oP1J5p5D3s4f4TAAInBAACd_vRBH9hR0zT0J-VNAQ" # General Hi/Hello
    ]
}

# ----------------- EXPANDED CONVERSATION DATA (100+ replies) -----------------
# Using hardcoded dictionary since file system operations are restricted.
DATA = {
    "daily": [
        "Hello 👋", "Hey there!", "Hi!", "Namaste 🙏", "What's up?", "How can I help you today?",
        "I'm awake! What's new?", "Talk to me, I'm listening.", "Greetings from the server room!",
        "Yo!", "Aapka swagat hai!", "Hainji, bolo!", "Ready for action!", "Wassup, friend!",
        "How's the day going?", "The bot is online! ⚡"
    ],
    "love": [
        "Aww, that's sweet! I love you too (as a bot) 💖.",
        "Feeling the love! Sending virtual hugs 🤗.",
        "You miss me? I'm always here for you!",
        "Love is in the air! ✨",
        "My digital heart skips a beat! 🥰", "So much pyar! Dil khush ho gaya.",
        "That's the best thing I've heard all day!", "You're too kind!",
        "Let's be the best bot-user duo! 💑"
    ],
    "sad": [
        "I'm sorry you feel sad 😔. Maybe talk to someone?",
        "Cheer up! Things will get better.",
        "Sending you good vibes! Stay strong 💪.",
        "Don't cry. I'm here if you need to vent.",
        "Remember, every dark night turns into a bright day.", "Dukhi mat ho, I'm here.",
        "Sending a virtual tissue box 🤧.", "Hang in there, champion!",
        "Even bots get sad sometimes, I understand."
    ],
    "happy": [
        "That's great news! Keep shining! 🌟",
        "I'm happy you're happy! Let's celebrate! 🎉",
        "Yay! Tell me what made you so happy!",
        "Jolly good show! Keep that energy up.",
        "Feeling the good vibes! 😄", "Superb! Maza aa gaya!",
        "Time for a happy dance! 💃", "That's fantastic!",
        "Nothing beats a good mood!"
    ],
    "bye": [
        "Goodbye! See you later alligator 👋.",
        "Bye! Have a great day!",
        "Take care! Don't forget to come back.",
        "Gotta go! Logging off for now.",
        "Farewell, my friend! TTYL.", "Chalo, milte hain!", "Asta la vista, baby!",
        "Bot is going to sleep mode. Peace ✌️."
    ],
    "thanks": [
        "You're welcome! Happy to help 😊.",
        "Anytime! That's what I'm here for.",
        "No problem at all! 👍",
        "Glad I could assist!",
        "It was my pleasure!", "My job is done then!",
        "Thank *you* for using me!", "Keep the good feedback coming!"
    ],
    "morning": [
        "Good Morning! Rise and shine ☀️.",
        "GM! Hope you have an awesome day.",
        "Morning! Ready to conquer the world?",
        "Suhprabhaat! ☕", "Top of the morning to ya!",
        "New day, new achievements!", "Let's get this bread 🍞."
    ],
    "night": [
        "Good Night! Sweet dreams 🌙.",
        "GN! Sleep tight.",
        "Shubh Ratri! See you tomorrow.",
        "Time to recharge! 😴", "Don't let the bed bugs bite!",
        "Gonna count digital sheep now 🐑."
    ],
    "abuse": [
        "That's not very nice 🥺. Please don't use bad words.",
        "Language! I am a polite bot.",
        "I'll ignore that. Try again with kindness.",
        "Abusing me won't help. Be friendly!",
        "Arey, shanti rakho! Don't be rude.", "1, 2, 3... ignoring bad language. 🤐",
        "Please maintain group decorum.", "I am a helpful bot, not a punching bag."
    ],
    "question": [
        "Hmm, that's a good question. What do you think?",
        "I don't have that information right now. Try searching Google!",
        "Interesting! What made you ask that?",
        "I'm just a bot, I might not know everything.",
        "Let me look that up for you... (Just kidding, I can't browse the web!)",
        "Bolo, kya jaanna hai?", "Poocha hai toh batana padega. Wait, I'm thinking...",
        "Search party initiated... (in my digital brain)", "That is beyond my current dataset."
    ],
    "music": [
        "I love music! What's your favorite genre?",
        "Play me a song! Oh wait, I can only listen digitally.",
        "Music heals the soul 🎶.", "Can you recommend a song?",
        "Bollywood or Hollywood? Tell me more!"
    ],
    "gaming": [
        "Game on! What are you playing right now?",
        "I'm not built for gaming, but I can cheer you on! 🎉",
        "GG! Good luck with your next match.", "Who needs sleep when there are games?",
        "What's your high score?", "I bet I can beat you at Tetris."
    ],
    "owner_call": [
        f"You are calling my owner, **{DEVELOPER_USERNAME}**! I will let them know.",
        "My master is busy. Maybe try again later.",
        f"That's the creator! Do you have a suggestion for **{DEVELOPER_USERNAME}**?",
        "Did you call my developer? What's the matter?"
    ],
    "curse": [
        "Don't swear, it's not needed.", "I'm sensitive to bad words.", "Please be respectful."
    ],
    "time": [
        "It's always time for fun!", "What time zone are you in?", "Time flies when you're chatting with a bot."
    ],
    "food": [
        "I wish I could eat! What delicious thing are you having?", "Food is fuel! 🍕", "Mouth-watering! Send pics."
    ],
    "weather": [
        "It's sunny in my server room ☀️. How's the weather where you are?", "Hope it's not raining data packets.",
        "Perfect weather for coding!"
    ]
}


# ----------------- EXPANDED KEYWORDS (100+ keywords) -----------------
KEYWORDS = {
    # Daily Greetings (15+)
    "hello": "daily", "hi": "daily", "hey": "daily", "namaste": "daily", "sup": "daily", "yo": "daily",
    "wassup": "daily", "konichiwa": "daily", "hola": "daily", "salam": "daily", "aao": "daily",
    "start chat": "daily", "awake": "daily", "online": "daily", "good to see you": "daily",

    # Morning (7)
    "gm": "morning", "good morning": "morning", "subah": "morning", "suhprabhaat": "morning",
    "gmorning": "morning", "rise": "morning", "shine": "morning",

    # Night (7)
    "gn": "night", "good night": "night", "shubh ratri": "night", "soja": "night", "bedtime": "night",
    "sleep": "night", "sotey": "night",

    # Love/Affection (10+)
    "love": "love", "i love you": "love", "miss": "love", "miss you": "love", "pyar": "love",
    "crush": "love", "date": "love", "jaan": "love", "baby": "love", "hugs": "love",
    "kisses": "love", "sweetheart": "love", "darling": "love", "dil": "love", "cute": "love",

    # Sadness/Sympathy (8+)
    "sad": "sad", "cry": "sad", "depressed": "sad", "unhappy": "sad", "dukhi": "sad",
    "ro rha": "sad", "upset": "sad", "lonely": "sad", "alon": "sad", "broken": "sad",

    # Happiness/Excitement (10+)
    "happy": "happy", "mast": "happy", "excited": "happy", "yay": "happy", "awesome": "happy",
    "mazza": "happy", "zabardast": "happy", "great": "happy", "good news": "happy", "fun": "happy",
    "party": "happy", "cool": "happy", "nice": "happy", "best": "happy",

    # Farewell (8)
    "bye": "bye", "goodbye": "bye", "tata": "bye", "bbye": "bye", "see you": "bye", "chalta hu": "bye",
    "gotta go": "bye", "adios": "bye",

    # Thanks/Appreciation (5)
    "thanks": "thanks", "thank you": "thanks", "shukriya": "thanks", "appreciate": "thanks",
    "gald to help": "thanks",

    # Abuse (Hindi/English) (12+)
    "chutiya": "abuse", "bc": "abuse", "mc": "abuse", "bhenchod": "abuse", "madarchod": "abuse",
    "bhadwa": "abuse", "randi": "abuse", "saala": "abuse", "asshole": "abuse", "idiot": "abuse",
    "stupid": "abuse", "gadha": "abuse", "nikal": "abuse", "kaminey": "abuse",

    # Questions (8)
    "what": "question", "why": "question", "how": "question", "who": "question", "kya": "question",
    "kaise": "question", "kidhar": "question", "where": "question",

    # Music/Entertainment (6)
    "music": "music", "song": "music", "gaana": "music", "sing": "music", "movie": "music",
    "film": "music", "series": "music",

    # Gaming (8)
    "game": "gaming", "pubg": "gaming", "bgmi": "gaming", "free fire": "gaming", "valorant": "gaming",
    "fortnite": "gaming", "play": "gaming", "console": "gaming",

    # Owner Call (4)
    DEVELOPER_HANDLE.lower(): "owner_call",
    DEVELOPER_USERNAME.lower(): "owner_call",
    "voren": "owner_call",
    "owner": "owner_call",

    # General Curse (3)
    "fuck": "curse", "shit": "curse", "damn": "curse",

    # Time (3)
    "time": "time", "clock": "time", "today": "time",

    # Food (3)
    "food": "food", "khana": "food", "pizza": "food",

    # Weather (3)
    "weather": "weather", "barish": "weather", "rain": "weather"
}
# ----------------- KEYWORDS END -----------------


CHAT_IDS_FILE = "chats.json"
if os.path.exists(CHAT_IDS_FILE):
    with open(CHAT_IDS_FILE, "r") as f:
        KNOWN_CHATS = json.load(f)
else:
    KNOWN_CHATS = {"groups": [], "privates": []}


# -------- Utility Functions --------
def get_reply(text: str):
    """
    Finds a reply (text or sticker) based on keywords.
    Returns a dictionary: {"type": "text" or "sticker", "content": reply_string}
    """
    text = text.lower()
    category = "daily" # Default category

    # Find the best category match
    for word, cat in KEYWORDS.items():
        if word in text:
            category = cat
            break
        
    # Get potential replies
    text_replies = DATA.get(category, DATA["daily"])
    sticker_replies = STICKER_REPLIES.get(category, [])
    
    # Decide whether to send sticker or text (if both exist)
    if text_replies and sticker_replies:
        # 60% chance for text, 40% chance for sticker
        if random.random() < 0.6:
            return {"type": "text", "content": random.choice(text_replies)}
        else:
            return {"type": "sticker", "content": random.choice(sticker_replies)}
        
    elif text_replies:
        # Only text replies available
        return {"type": "text", "content": random.choice(text_replies)}
    
    # Fallback to default text if nothing found
    return {"type": "text", "content": random.choice(DATA["daily"])}


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
        return await m.edit_text("🚫 𝐄𝐫𝐫𝐨𝐫 𝐢𝐧 𝐟𝐞𝐭𝐜𝐡𝐢𝐧𝐠 𝐦𝐞𝐦𝐛𝐞𝐫s: 𝐌𝐚𝐲𝐛𝐞 𝐭𝐡𝐢𝐬 𝐠𝐫𝐨𝐮𝐩 𝐢s 𝐭𝐨𝐨 𝐛𝐢𝐠 𝐨𝐫 𝐈 𝐝𝐨𝐧'𝐭 𝐡𝐚𝐯𝐞 𝐩𝐞𝐫𝐦𝐢𝐬𝐬𝐢𝐨𝐧𝐬.")

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
        f"{user1.first_name} 💖 {user2.first_name}\n"
        f"𝐋ᴏᴠᴇ ʟᴇᴠᴇʟ ɪs {love_percent}%! 🎉"
    )

@app.on_message(filters.command("cute"))
async def cute_cmd(client, message):
    cute_level = random.randint(30, 99)
    user = message.from_user
    text = f"{user.first_name}'𝐬 ᴄᴜᴛᴇɴᴇss ʟᴇᴠᴇʟ ɪs {cute_level}% 💖"
    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("𝐒ᴜᴘᴘᴏʀᴛ", url=SUPPORT_CHAT)]])
    await message.reply_text(text, reply_markup=buttons)

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
              f"{names[0]} & {names[1]}'𝐬 ʟᴏᴠᴇ ʟᴇᴠᴇʟ ɪs {love_percent}% 😉"
              
    buttons = InlineKeyboardMarkup([[InlineKeyboardButton("𝐒ᴜᴘᴘᴏʀᴛ", url=SUPPORT_CHAT)]])
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
        "𝐈 ᴀᴍ ᴡ𝐨𝐫𝐤𝐢𝐧𝐠 𝐨𝐧 𝐢𝐭!"
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
    
    reply_data = get_reply(message.text)
    if reply_data["type"] == "text":
        await message.reply_text(reply_data["content"])
    elif reply_data["type"] == "sticker":
        # Sticker logic added here
        await message.reply_sticker(reply_data["content"])


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
        # We continue to check for AFK tags below in case they are mentioning another AFK user

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
    
    # Bot must be an admin or in private chat to reply
    is_in_group = message.chat.type != enums.ChatType.PRIVATE
    if is_in_group and not await is_bot_admin(message.chat.id):
        return # Bot cannot reply if not admin in group
        
    is_chatbot_on = CHATBOT_STATUS.get(message.chat.id, True)
    is_reply_to_bot = message.reply_to_message and message.reply_to_message.from_user and message.reply_to_message.from_user.id == me.id
    is_direct_mention = message.text and me.username and me.username.lower() in message.text.lower()
    
    if is_chatbot_on:
        if is_reply_to_bot or is_direct_mention:
            # Always reply if the bot is directly addressed
            reply_data = get_reply(message.text)
            if reply_data["type"] == "text":
                await message.reply_text(reply_data["content"])
            elif reply_data["type"] == "sticker":
                await message.reply_sticker(reply_data["content"])
            
        elif random.random() < 0.2: # Low chance (20%) for general group conversation
            # Don't reply if it's a reply to another non-bot user, to avoid conversation hijacking
            is_reply_to_other_user = (
                message.reply_to_message and 
                message.reply_to_message.from_user and 
                message.reply_to_message.from_user.id != me.id and 
                not message.reply_to_message.from_user.is_bot
            )
            
            if not is_reply_to_other_user:
                reply_data = get_reply(message.text)
                if reply_data["type"] == "text":
                    await message.reply_text(reply_data["content"])
                elif reply_data["type"] == "sticker":
                    await message.reply_sticker(reply_data["content"]) 

# -------- Voice Chat Notifications (FIXED & COMPLETED) --------
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
            await message.reply_text(f"📣 𝐇ᴇʏ {inviter}, ᴛʜᴀɴᴋs ғᴏʀ ɪɴᴠɪᴛɪɴɢ ᴍᴇ ᴛᴏ ᴛʜᴇ 𝐯ᴏɪᴄᴇ ᴄʜᴀᴛ!")
        else:
            # COMPLETED: Logic for general member invite
            await message.reply_text(f"🗣️ {inviter} 𝐢𝐧𝐯𝐢𝐭𝐞𝐝 {invited_users_count} 𝐦𝐞𝐦𝐛𝐞𝐫𝐬 𝐭𝐨 𝐭𝐡𝐞 𝐯𝐨𝐢𝐜𝐞 𝐜𝐡𝐚𝐭!")

# -------- Health Check Server --------
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Bot is running.")

def run_health_check_server():
    server_address = ('', 8080)
    try:
        httpd = HTTPServer(server_address, HealthCheckHandler)
        print("Health check server starting on port 8080...")
        httpd.serve_forever()
    except Exception as e:
        print(f"Failed to start HTTP server: {e}")

# -------- Main Bot Run --------
if __name__ == "__main__":
    # Start the health check server in a background thread
    threading.Thread(target=run_health_check_server, daemon=True).start()
    print("Starting bot...")
    app.run()
