import requests
import yt_dlp
from youtube_search import YoutubeSearch
from pyrogram import Client, filters
import telebot
import time
import base64

# Telegram Bot Token
TOKEN = "7702772691:0000"  # TG BOT TOKEN
bot = telebot.TeleBot(TOKEN)

# Pyrogram Client Initialization (Mukesh)
api_id = "your_api_id"  # Pyrogram API ID
api_hash = "your_api_hash"  # Pyrogram API Hash
bot_token = "your_bot_token"  # Bot Token for Pyrogram
Mukesh = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Song search and download functions
def download_song(url, user_id):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{user_id}_%(title)s.%(ext)s',
        'noplaylist': True,
        'quiet': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return info['title'], f"{user_id}_{info['title']}.m4a"

def search_song(query):
    results = YoutubeSearch(query, max_results=1).to_dict()
    if results:
        link = f"https://youtube.com{results[0]['url_suffix']}"
        title = results[0]["title"]
        return link, title
    return None, None

# Dream image generation functions
def generate_image(prompt, width, height, model):
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
    with open(file_name, "wb") as img_file:
        img_file.write(base64.b64decode(base64_data))

# Telegram Bot Start command
@bot.message_handler(commands=['start'])
def start_message(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    button1 = telebot.types.InlineKeyboardButton(text="♂️ SAHİP", url="https://t.me/ViosCeo")
    button2 = telebot.types.InlineKeyboardButton(text="🗨️ KANAL", url="https://t.me/ViosTsam")
    button3 = telebot.types.InlineKeyboardButton(text="📕 Komutlar", callback_data="help")
    keyboard.add(button1, button2, button3)
    bot.reply_to(
        message,
        "Merhaba! Ben bir görsel işleme botuyum. Bana hayalindeki bir sahneyi tarif et ve sana özel bir görsel göndereyim.\n\n"
        "Aşağıdaki butonları kullanarak daha fazla bilgi alabilirsin:",
        reply_markup=keyboard
    )

# Song Command: Search for and download song
@bot.message_handler(commands=['song'])
def song_request(message):
    query = " ".join(message.text.split()[1:])
    if not query:
        bot.reply_to(message, "Lütfen bir şarkı adı girin.")
        return
    
    bot.reply_to(message, f"Aranıyor: {query}...")
    link, title = search_song(query)
    
    if link:
        bot.reply_to(message, f"Şarkı bulundu! İndiriliyor: {title}")
        song_title, audio_file = download_song(link, message.from_user.id)
        with open(audio_file, "rb") as audio:
            bot.send_audio(message.chat.id, audio, title=song_title)
        # Clean up the downloaded file
        os.remove(audio_file)
    else:
        bot.reply_to(message, "Şarkı bulunamadı.")

# Dream Command: Generate image based on the user's prompt
@bot.message_handler(commands=['dream'])
def dream_request(message):
    bot.reply_to(message, "Hayalini tarif et ve ben sana bir görsel oluşturayım.")
    
@bot.message_handler(func=lambda message: True)
def process_prompt(message):
    prompt = message.text.strip()
    if not prompt:
        bot.reply_to(message, "Lütfen bir sahne tarif edin!")
        return
    
    bot.reply_to(message, f"Görsel işleniyor...\nPrompt: {prompt}")
    
    try:
        model_ID = "5g72h1 y661hp k771ns 33bb21 77bagl 6b 3090" if "anime" in prompt else "754019 b5df2e e606f1 a7600b 96b0c8 94"
        model_Name = "Anime Core" if "anime" in prompt else "Photoreal"
        result = generate_image(prompt, 768, 1024, model_ID)

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
                    save_image(base64_image, "output.jpg")
                    with open("output.jpg", "rb") as img:
                        bot.send_photo(message.chat.id, img, caption=f"✨ Resim Oluşturuldu\nModel :: {model_Name}")
                else:
                    bot.reply_to(message, "Görsel verisi alınamadı. Lütfen tekrar deneyin.")
            elif check.get("status") == 202:
                time.sleep(10)
            else:
                bot.reply_to(message, f"Görsel oluşturulamadı. Durum: {check.get('status')}")
                generated = True
    except Exception as e:
        bot.reply_to(message, f"Hata oluştu: {str(e)}")

# Help message for commands
@bot.callback_query_handler(func=lambda call: call.data == "help")
def help_message(call):
    help_text = (
        "Komutlar:\n"
        "/song : Şarkı indir\n\n"
        "/dream - Rüyanı düşle ❤️\n\n"
        "Hayalindeki sahneyi bana tarif et ve sana özel bir görsel göndereyim."
    )
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, help_text)

# Pyrogram client to handle song search
@Mukesh.on_message(filters.command(["song", "bul"]))
def song(client, message):
    message.delete()
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    query = " ".join(message.command[1:])
    
    m = message.reply("**» Bekleyiniz...**")
    ydl_opts = {"format": "bestaudio[ext=m4a]"}
    
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        link = f"https://youtube.com{results[0]['url_suffix']}"
        title = results[0]["title"]
        thumbnail = results[0]["thumbnails"][0]
        thumb_name = f"thumb{title}.jpg"
        thumb = requests.get(thumbnail, allow_redirects=True)
        open(thumb_name, "wb").write(thumb.content)
        
        duration = results[0]["duration"]
        views = results[0]["views"]
    except Exception as e:
        m.edit("**Youtube İçerik Bulunamadı,**")
        print(str(e))
        return

    m.edit("» İndiriliyor...")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            audio_file = ydl.prepare_filename(info_dict)
            ydl.process_info(info_dict)
        
        rep = f"**Başlık :** {title[:25]}\n**İzlenme :** `{duration}`\n**Süre :** `{views}`\n**Talep »** {user_name}"
        
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
        m.edit(f"**» Başarısız,**")
        print(e)

    try:
        os.remove(audio_file)
        os.remove(thumb_name)
    except Exception as e:
        print(e)

# Start bot polling
print("Bot çalışıyor...")
bot.polling(none_stop=True, interval=0, timeout=60)
Mukesh.run()  # Starts the Pyrogram client
