import requests
import json
import telebot
import time
import base64
from telebot import types

TOKEN = "7702772691:0000"  # TG BOT TOKEN
GEMINI_API_KEY = "AIzaSyDZdeZDYQ2cAEhuSCru-jD8CfgIWaHa9I8"  # Google Gemini API Key
bot = telebot.TeleBot(TOKEN)

def ask_gemini(question):
    """
    Google Gemini API üzerinden soruya cevap alır.
    """
    url = "https://generativelanguage.googleapis.com/v1beta2/models/text-bison-001:generateText"
    headers = {"Authorization": f"Bearer {GEMINI_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "prompt": {"text": question},
        "temperature": 0.7,  # Yanıtın çeşitliliğini kontrol eder
        "maxOutputTokens": 256  # Yanıtın maksimum uzunluğu
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            return result.get("candidates", [{}])[0].get("output", "Bir hata oluştu.")
        else:
            return f"Google Gemini Hatası: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Hata: {str(e)}"

def generate(prompt, width, height, model):
    url = "https://create.thena.workers.dev/create_image_thena_v5"
    payload = {
        "prompt": prompt,
        "model": model,
        "creative": False,
        "width": width,
        "height": height,
        "fastMode": False
    }
    headers = {
        'User-Agent': 'thena-free-7-84-994-55664-49485653-MTAwMQ==',
        'Content-Type': 'application/json'
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": str(e)}

def save_image(base64_data, file_name):
    try:
        with open(file_name, "wb") as img_file:
            img_file.write(base64.b64decode(base64_data))
    except Exception as e:
        return f"Error saving image: {str(e)}"
    return None

@bot.message_handler(commands=['start'])
def start_message(message):
    keyboard = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text="♂️ SAHİP", url="https://t.me/ViosCeo")
    button2 = types.InlineKeyboardButton(text="🗨️ KANAL", url="https://t.me/ViosTeam")
    button3 = types.InlineKeyboardButton(text="📕 Komutlar", callback_data="help")
    keyboard.add(button1, button2, button3)

    bot.reply_to(
        message,
        "Merhaba! Ben bir görsel ve sohbet botuyum.\n"
        "Aşağıdaki butonları kullanarak daha fazla bilgi alabilirsin:",
        reply_markup=keyboard
    )

@bot.message_handler(commands=['ask'])
def ask_question(message):
    question = message.text.replace("/ask", "").strip()
    if not question:
        bot.reply_to(message, "Lütfen bir soru sorun! Örneğin: /ask Yapay zeka nedir?")
        return
    bot.reply_to(message, "Soru işleniyor, lütfen bekleyin...")
    try:
        answer = ask_gemini(question)
        bot.reply_to(message, f"🤖 Yanıt:\n\n{answer}")
    except Exception as e:
        bot.reply_to(message, f"Bir hata oluştu: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data == "help")
def help_message(call):
    help_text = (
        "Komutlar:\n"
        "/dream - Rüyanı düşle ❤️\n"
        "/ask - Sorularını sor 🤖\n\n"
        "Hayalindeki sahneyi tarif et veya aklına takılan bir soruyu bana sor!"
    )
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, help_text)

print("Bot çalışıyor...")
bot.polling(none_stop=True, interval=0, timeout=60)
