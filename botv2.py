import requests
import json
import telebot
import time
import yt_dlp
from youtube_search import YoutubeSearch
import base64
from telebot import types

TOKEN = "7702772691:0000"  # TG BOT TOKEN
bot = telebot.TeleBot(TOKEN)

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
        response = requests.post(url, headers=headers, json=payload, timeout=60)  # Timeout artırıldı.
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": str(e)}

def control(id):
    url = f"https://create.thena.workers.dev/status?id={id}"
    headers = {'User-Agent': 'thena-free-7-84-994-55664-49485653-MTAwMQ=='}
    try:
        response = requests.get(url, headers=headers, timeout=60)  # Timeout artırıldı.
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
    # Butonlar için inline keyboard oluşturuluyor
    keyboard = types.InlineKeyboardMarkup()

    # Butonlar
    button1 = types.InlineKeyboardButton(text="♂️ SAHİP", url="https://t.me/ViosCeo")
    button2 = types.InlineKeyboardButton(text="🗨️ KANAL", url="https://t.me/ViosTsam")
    button3 = types.InlineKeyboardButton(text="📕 Komutlar", callback_data="help")

    keyboard.add(button1, button2, button3)

    bot.reply_to(
        message,
        "Merhaba! Ben bir görsel işleme botuyum. Bana hayalindeki bir sahneyi tarif et ve sana özel bir görsel göndereyim.\n\n"
        "Aşağıdaki butonları kullanarak daha fazla bilgi alabilirsin:",
        reply_markup=keyboard  # Butonları mesajın altına ekliyoruz
    )

@bot.message_handler(commands=['dream'])
def prompt_request(message):
    bot.reply_to(message, "GÜZEL, ŞİMDİ RÜYANI\n\n[ İNGİLİZCE DİLİ OLARAK DÜŞLE ]")

@bot.message_handler(func=lambda message: True)
def process_prompt(message):
    prompt = message.text.replace("/dream", "").strip()
    if not prompt:
        bot.reply_to(message, "Lütfen bir sahne tarif edin!")
        return
    
    bot.reply_to(message, f"Görsel işleniyor...\nPrompt: {prompt}")
    
    try:
        model_ID = "5g72h1 y661hp k771ns 33bb21 77bagl 6b 3090" if "anime" in prompt else "754019 b5df2e e606f1 a7600b 96b0c8 94"
        model_Name = "Anime Core" if "anime" in prompt else "Photoreal"
        result = generate(prompt, 768, 1024, model_ID)

        if result.get("status") != 200:
            bot.reply_to(message, f"Görsel oluşturulamadı: {result.get('message', 'Bilinmeyen hata')}")
            return
        
        generated = False
        while not generated:
            check = control(result.get("image"))
            if check.get("status") == 200:
                generated = True
                base64_image = check.get("image")
                if base64_image:
                    save_error = save_image(base64_image, "output.jpg")
                    if save_error:
                        bot.reply_to(message, f"Görsel kaydedilemedi: {save_error}")
                        return
                    with open("output.jpg", "rb") as img:
                        bot.send_photo(message.chat.id, img, caption=f"✨ Resim Oluşturuldu\nModel :: {model_Name}")
                else:
                    bot.reply_to(message, "Görsel verisi alınamadı. Lütfen tekrar deneyin.")
            elif check.get("status") == 202:
                time.sleep(10)  # Görsel oluşturulmadıysa 10 saniye bekle
            else:
                bot.reply_to(message, f"Görsel oluşturulamadı. Durum: {check.get('status')}")
                generated = True
    except Exception as e:
        bot.reply_to(message, f"Hata oluştu: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data == "help")
def help_message(call):
    # Yardım mesajı
    help_text = (
        "Komutlar:\n"
        "/song : Sevdiğin Sanatçıları Keşfet\n\n"
        "/dream - Rüyanı düşle ❤️\n\n"
        "Hayalindeki sahneyi bana tarif et ve sana özel bir görsel göndereyim."
    )
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, help_text)

@Mukesh.on_message(filters.command(["song", "bul"]))
def song(client, message):

    message.delete()
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    chutiya = "[" + user_name + "](tg://user?id=" + str(user_id) + ")"

    query = ""
    for i in message.command[1:]:
        query += " " + str(i)
    print(query)
    m = message.reply("**» Bekleyiniz...**")
    ydl_opts = {"format": "bestaudio[ext=m4a]"}
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        link = f"https://youtube.com{results[0]['url_suffix']}"
        # print(results)
        title = results[0]["title"][:40]
        thumbnail = results[0]["thumbnails"][0]
        thumb_name = f"thumb{title}.jpg"
        thumb = requests.get(thumbnail, allow_redirects=True)
        open(thumb_name, "wb").write(thumb.content)

        duration = results[0]["duration"]
        results[0]["url_suffix"]
        views = results[0]["views"]

    except Exception as e:
        m.edit(
            "**Youtube İçerik Bulunamadı,"
        )
        print(str(e))
        return
    m.edit("» İndiriliyor...")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            audio_file = ydl.prepare_filename(info_dict)
            ydl.process_info(info_dict)
        rep = f"**Başlık :** {title[:25]}\n**İzlenme :** `{duration}`\n**Süre :** `{views}`\n**Talep »** {chutiya}"
        secmul, dur, dur_arr = 1, 0, duration.split(":")
        for i in range(len(dur_arr) - 1, -1, -1):
            dur += int(dur_arr[i]) * secmul
            secmul *= 60
        message.reply_audio(
            audio_file,
            caption=rep,
            thumb=thumb_name,
            title=title,
            duration=dur,
        )
        m.delete()
    except Exception as e:
        m.edit(
            f"**» Başarısız,"
        )
        print(e)

    try:
        os.remove(audio_file)
        os.remove(thumb_name)
    except Exception as e:
        print(e)


s = bytearray.fromhex("68 74 74 70 73 3A 2F 2F 67 69 74 68 75 62 2E 63 6F 6D 2F 4E 6F 6F 62 2D 6D 75 6B 65 73 68 2F 43 68 61 74 67 70 74 2D 62 6F 74").decode()

if SOURCE != s:
    print("So sad, you have changed source, change it back to ` https://github.com/zeedslowy `  else I won't work")
    sys.exit(1) 


print("Bot çalışıyor...")
bot.polling(none_stop=True, interval=0, timeout=60)  # Timeout artırıldı, polling ayarlandı
