# Telegram-Group- AI -Handle-Bot-
This Bot will be help you to control your telegram Groups 


🤖 SaYarGyi Ultimate AI Admin Bot
SaYarGyi is an intelligent, multi-functional Telegram AI assistant designed specifically for programming and IT technical support groups. It combines LLM-powered logic (via Groq) with real-time GitHub search and a custom persistent knowledge base.

🌟 Key Features
🧠 Smart Features
AI Chatbot (Llama 3.3): Powered by Groq's fast inference, the bot acts as a girl-persona, gentle, technical, and funny assistant.

Knowledge Memory (SQLite): Admins can "teach" the bot specific information (e.g., pricing, rules) using the /learn command, which it remembers and uses to answer future questions.

Real-time GitHub Search: Automatically searches GitHub for repositories, tools, and scripts when keywords are detected in the chat.

🛠 Technical Support (Validator Mode)
Code Debugging: Analyzes shared code, pinpoints syntax/logic errors, and provides corrected snippets in professional markdown.

Linux/VPS Management: Explains complex Linux commands, evaluates script safety, and provides setup guidance for Ubuntu servers.

VPN Configuration Validator: Expertly parses VPN protocols (VLESS, Trojan, Reality, 3-XUI, Marzban) and diagnoses connectivity issues.

📋 Commands
/start - Get a welcome message from SaYarGyi.

/learn <info> - Admin Only. Saves specific info to the bot's permanent memory.

🛠 Technical Stack
Language: Python 3.10+

Framework: aiogram 3.x

AI Engine: Groq Cloud API (Llama-3.3-70b)

Database: SQLite3

API Integration: GitHub REST API

🚀 How to Set Up
1. Requirements
Install the necessary dependencies:

Bash
pip install aiogram groq aiohttp
2. Configuration
Open main.py and replace the following keys:

TELEGRAM_TOKEN: Your BotFather token.

GROQ_API_KEY: Your Groq API Key.

3. Database
The bot will automatically create bot_memory.db upon the first launch. Ensure your server has write permissions in the script directory.

4. Running the Bot
Bash
python main.py
⚠️ Admin Guidelines
To teach the bot new information, use the /learn command inside the group (must be an Admin):

/learn VPN Plan: 1 Month is 5000 MMK

The bot will store this in its SQLite database and reference it whenever a user asks about that topic.

🛡 Disclaimer
Security: This bot contains advanced technical logic. Ensure you are using the latest version of aiogram.

API Safety: Keep your Groq and Telegram keys secret. Do not push your main.py to a public GitHub repository without hiding your API keys using an .env file!

Pro-Tips for your Repo:
Environment Variables: Since you are using an AI key and a Telegram token, I strongly suggest using a .env file with the python-dotenv library to keep your keys safe.

Code Structure: As your bot grows, consider moving the system_instruction and handlers into separate files for better maintainability.
