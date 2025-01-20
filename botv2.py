import requests
import json
import telebot
import base64
from telebot import types

TOKEN = "7702772691:0000"  # Telegram Bot Token
HF_API_KEY = "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"  # Hugging Face API Key
bot = telebot.TeleBot(TOKEN)

# Hugging Face üzerinden soruları yanıtlayan fonksiyon
def ask_hugging_face(question):
    url = "https://api-inference.huggingface.co/models/google/flan-t5-large"  # Hugging Face modeli
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    data = {"inputs": question}
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            return result[0].get("generated_text", "Bir hata oluştu.")
        else:
            return f"Hugging Face Hatası: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Hata: {str(e)}"

# Thena API üzerinden görsel oluşturan fonksiyon
def generate(prompt, width, height, model="stable-diffusion"):
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

# Görseli kaydeden fonksiyon
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
        answer = ask_hugging_face(question)
        bot.reply_to(message, f"🤖 Yanıt:\n\n{answer}")
    except Exception as e:
        bot.reply_to(message, f"Bir hata oluştu: {str(e)}")

@bot.message_handler(commands=['dream'])
def dream_image(message):
    text = message.text.replace("/dream", "").strip()
    if not text:
        bot.reply_to(message, "Lütfen bir hayalinizi yazın! Örneğin: /dream bir orman içinde şato")
        return
    bot.reply_to(message, "Görsel oluşturuluyor, lütfen bekleyin...")
    try:
        result = generate(prompt=text, width=512, height=512, model="stable-diffusion")
        if result.get("status") == "error":
            bot.reply_to(message, f"Görsel oluşturulamadı: {result['message']}")
            return
        base64_image = result.get("image_base64")
        if base64_image:
            file_name = "dream_image.png"
            error = save_image(base64_image, file_name)
            if error:
                bot.reply_to(message, error)
            else:
                with open(file_name, "rb") as img:
                    bot.send_photo(message.chat.id, img, caption="İşte hayalinizden doğan görsel!")
        else:
            bot.reply_to(message, "Görsel oluşturulamadı. Lütfen tekrar deneyin.")
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
