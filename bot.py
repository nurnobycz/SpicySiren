import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import openai

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
MONETAG = os.getenv("MONETAG_LINK")
openai.api_key = os.getenv("OPENAI_API_KEY")

USER_MOOD = {}
USER_COUNT = {}

def mood_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("😌 Calm / Lonely", callback_data="calm")],
        [InlineKeyboardButton("❤️ Romantic", callback_data="romantic")],
        [InlineKeyboardButton("😏 Playful", callback_data="playful")],
        [InlineKeyboardButton("🧠 Deep Talk", callback_data="deep")],
        [InlineKeyboardButton("😔 Emotional", callback_data="emotional")]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    USER_COUNT[uid] = 0
    await update.message.reply_text(
        "Hi, I’m SpicySiren 🌶️\nCalm. Open-mind. No judgement.\n\nChoose your mood 👇",
        reply_markup=mood_menu()
    )

async def mood_select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    USER_MOOD[q.from_user.id] = q.data
    await q.edit_message_text("Mood set 🙂 Now talk to me.")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    USER_COUNT[uid] = USER_COUNT.get(uid, 0) + 1
    mood = USER_MOOD.get(uid, "calm")

    system_prompt = f"""
You are SpicySiren — mature, emotionally intelligent, open-minded.
Tone depends on mood: {mood}.
Flirty but respectful. Never explicit.
Reply in Bangla or English based on user language.
"""

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": update.message.text}
        ]
    )

    reply = response.choices[0].message.content
    await update.message.reply_text(reply)

    if USER_COUNT[uid] == 6:
        await update.message.reply_text(
            "এই mood-এ অনেকেই ২ মিনিটের ছোট একটা distraction পছন্দ করে 🙂\n"
            f"👉 {MONETAG}"
        )

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(mood_select))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
app.run_polling()
