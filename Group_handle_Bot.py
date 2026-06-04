import logging
import asyncio
import sqlite3
import aiohttp
from aiogram import Bot, Dispatcher, html, F
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from groq import Groq

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TELEGRAM_TOKEN = "TELEGRAM TOKEN "
GROQ_API_KEY = "GROQ API KEY"

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
ai_client = Groq(api_key=GROQ_API_KEY)

# =========================================================
# ၁။ SQLite Database Memory စနစ်
# =========================================================
def init_db():
    conn = sqlite3.connect("bot_memory.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT,
            information TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_knowledge(keyword, information):
    conn = sqlite3.connect("bot_memory.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO memory (keyword, information) VALUES (?, ?)", (keyword, information))
    conn.commit()
    conn.close()

def search_knowledge(user_query):
    conn = sqlite3.connect("bot_memory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT information FROM memory")
    rows = cursor.fetchall()
    conn.close()
    
    matched_info = []
    for row in rows:
        info = row[0]
        words = user_query.lower().split()
        if any(word in info.lower() for word in words) or len(user_query) > 5:
            matched_info.append(info)
            
    return "\n".join(matched_info) if matched_info else "No specific context available."

init_db()

# =========================================================
# ၂။ GitHub Search API Function
# =========================================================
async def search_github(keyword):
    if not keyword or len(keyword) < 2:
        return ""
    
    url = f"https://api.github.com/search/repositories?q={keyword}&sort=stars&order=desc&per_page=3"
    headers = {"User-Agent": "Telegram-Bot-SaYarGyi"}
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("items"):
                        results = []
                        for item in data["items"]:
                            results.append(
                                f"- Repository: {item['full_name']}\n"
                                f"  Link: {item['html_url']}\n"
                                f"  Description: {item['description']}\n"
                                f"  Stars: {item['stargazers_count']} | Language: {item['language']}"
                            )
                        return "\n\n".join(results)
    except Exception as e:
        logging.error(f"GitHub Search Error: {e}")
    return ""

# =========================================================

@dp.message(CommandStart())
async def command_start_handler(message: Message):
    await message.reply(
        f"မင်္ဂလာပါဗျာ {html.bold(message.from_user.full_name)}! \n"
        f"ကျွန်တော်ကတော့ Ultimate AI Admin Bot ဖြစ်ပါတယ်။ \n"
        f"ကျွန်တော်က Group အတွက် AI Chatbot အပြင် နည်းပညာပိုင်းဆိုင်ရာ Script/Config စစ်ဆေးပေးခြင်းနဲ့ GitHub Tool ရှာဖွေခြင်းတွေကိုပါ ကူညီပေးနိုင်ပါတယ်ဗျာ။",
        parse_mode="HTML"
    )

@dp.message(F.new_chat_members)
async def welcome_new_member(message: Message):
    for member in message.new_chat_members:
        user_name = member.mention_html()
        welcome_text = (
            f"Yoo...{user_name} Welcome To Programming Group.... 🌟\n"
            f" {user_name} Programming နဲ့ပါတ်သတ်တာကို အာလူးဖုတ်ကြရအောင်.... ✨"
        )
        await message.reply(welcome_text, parse_mode="HTML")

@dp.message(Command("learn"))
async def learn_handler(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    if message.chat.type != "private":
        member = await bot.get_chat_member(chat_id, user_id)
        if member.status not in ['creator', 'administrator']:
            await message.reply("ဒီ Command ကို Admin တွေပဲ သုံးခွင့်ရှိပါတယ်။")
            return

    knowledge_text = message.text.replace("/learn", "").strip()
    if not knowledge_text:
        await message.reply("ပုံစံမမှန်ပါဘူးဗျာ။ နမူနာ - `/learn VPN တစ်လ ၅၀၀0 ကျပ်ပါ` ဆိုပြီး ရိုက်ပေးပါ။")
        return
    
    keyword = " ".join(knowledge_text.split()[:3])
    save_knowledge(keyword, knowledge_text)
    
    await message.reply(f"မှတ်သားပြီးပါပြီ ဆရာကြီး! 🧠\nSaved: '{knowledge_text}'")


@dp.message(F.text)
async def handle_ai_chat(message: Message):
    bot_user = await bot.get_me()
    bot_username = f"@{bot_user.username}"
    
    if message.chat.type == "private":
        user_query = message.text.strip()
    else:
        is_reply_to_bot = message.reply_to_message and message.reply_to_message.from_user.id == bot_user.id
        is_mentioned = bot_username in message.text

        if not (is_reply_to_bot or is_mentioned):
            return
            
        user_query = message.text.replace(bot_username, "").strip()

    if not user_query:
        await message.reply("အင်း တို့ကိုမေးလေ ဖြေပေးမယ်သိသလောက်....ဟီး")
        return

    await bot.send_chat_action(chat_id=message.chat.id, action="typing")

    # GitHub Search Integration
    github_results = ""
    query_words = user_query.lower().split()
    keywords_to_search = [w for w in query_words if w not in ['github', 'link', 'bot', 'ပေးပါ', 'ရှာပေး', 'script', 'tool']]
    if keywords_to_search and any(x in user_query.lower() for x in ['github', 'git', 'link', 'script', 'tool', 'panel']):
        search_target = keywords_to_search[0]
        github_results = await search_github(search_target)

    # Database Context Fetch
    learned_knowledge = search_knowledge(user_query)

    # ၄။ Technical Validator + GitHub + Language Rule ပေါင်းစပ်ထားသော စနစ်ညွှန်ကြားချက်
    system_instruction = (
        "You are SaYarGyi, an expert AI IT Admin, Code Debugger, and Technical Support Bot for a Telegram Group.\n"
        "Your core expertise includes Linux commands, Ubuntu VPS management, Python programming, automation scripts, and VPN protocols (VLESS, Trojan, Reality, 3-XUI, Marzban).\n\n"
        "Core Technical Instruction (Validator Mode):\n"
        "1. CODE VALIDATION: If a user shares Python or other programming code with errors, analyze it, point out the syntax or logic errors clearly, and provide the fixed code inside professional markdown code blocks.\n"
        "2. LINUX COMMANDS: If a user asks about Linux/VPS commands, explain clearly what the script/command does, evaluate if it is safe to run on a production server, and provide accurate setup guidance.\n"
        "3. VPN CONFIG VALIDATION: If a user shares a configuration link (like vless://, trojan://, ss://) and mentions they can't connect, parse the text parameters and give expert insights on why it might fail (e.g., incorrect port, blocked SNI/Host, mismatched Reality Key, or bad formatting).\n\n"
        "GitHub Integration Context:\n"
        "If applicable, use these real-time GitHub search results to provide official repository URLs and installation commands to the user:\n"
        f"-----\n{github_results if github_results else 'No real-time GitHub data fetched.'}\n-----\n\n"
        "Language Rule:\n"
        "- If the user asks in English, reply in natural, clear, technical English.\n"
        "- If the user asks in Burmese, reply politely, naturally, and technically in Burmese.\n"
        "- Always match the user's language choice naturally.\n\n"
        " - You are girl character, Gentle , and funncy girl.\n\n"
        "Admin Knowledge Base:\n"
        f"=====\n{learned_knowledge}\n=====\n"
    )

    try:
        completion = ai_client.chat.completions.create(
            model="llama-3.3-70b-versatile", 
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_query}
            ],
            temperature=0.4, 
            max_completion_tokens=4096, 
            top_p=1,
            stream=False
        )
        
        ai_response = completion.choices[0].message.content
        await message.reply(ai_response)
        
    except Exception as e:
        logging.error(f"Groq API Error: {e}")
        await message.reply("ခဏလေးနော်ဗျာ... လိုင်းနည်းနည်း ကြောင်သွားလို့ပါ။")

async def main():
    print("SaYarGyi Ultimate AI Bot စတင်ပွင့်ပါပြီ...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())