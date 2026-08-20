from telethon import TelegramClient, events
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.errors import ChatAdminRequiredError, ChannelPrivateError
import os
import re
import random
import string
import json
from pathlib import Path

api_id = 38433332
api_hash = "96e2e580a0ff590253237b27b089c728"

client = TelegramClient("my_session", api_id, api_hash)

# ID владельца аккаунта
OWNER_ID = 7545068007

# Пути
SAVE_PATH = "/storage/emulated/0/Documents/KMBP"
PRIKOLI_PATH = "/storage/emulated/0/Documents/prikoli"


def generate_random_folder_name(length=10):
    """Генерирует случайное название папки"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def get_random_prikol():
    """Получает случайный прикол из папки"""
    try:
        if not os.path.exists(PRIKOLI_PATH):
            return None
        
        folders = [f for f in os.listdir(PRIKOLI_PATH) if os.path.isdir(os.path.join(PRIKOLI_PATH, f))]
        
        if not folders:
            return None
        
        random_folder = random.choice(folders)
        folder_path = os.path.join(PRIKOLI_PATH, random_folder)
        
        # Ищем файл nigers.txt
        text_file = os.path.join(folder_path, "nigers.txt")
        if not os.path.exists(text_file):
            return None
        
        with open(text_file, "r", encoding="utf-8") as f:
            text_content = f.read()
        
        # Ищем изображения
        images = []
        for ext in ["jpg", "jpeg", "png", "gif", "webp"]:
            for file in os.listdir(folder_path):
                if file.lower().endswith(ext):
                    images.append(os.path.join(folder_path, file))
        
        return {
            "text": text_content,
            "images": images,
            "folder": random_folder
        }
    except Exception as e:
        print(f"❌ Ошибка при получении приколов: {e}")
        return None


def save_prikol_from_message(message_text, media_files):
    """Сохраняет прикол из сообщения в базу"""
    try:
        folder_name = generate_random_folder_name()
        folder_path = os.path.join(PRIKOLI_PATH, folder_name)
        os.makedirs(folder_path, exist_ok=True)
        
        # Сохраняем текст
        text_file = os.path.join(folder_path, "nigers.txt")
        with open(text_file, "w", encoding="utf-8") as f:
            f.write(message_text)
        
        # Сохраняем медиа
        for i, media in enumerate(media_files):
            os.rename(media, os.path.join(folder_path, f"image_{i}{os.path.splitext(media)[1]}"))
        
        return folder_name
    except Exception as e:
        print(f"❌ Ошибка при сохранении приколов: {e}")
        return None


def register_handlers(client_instance):
    """Регистрация всех обработчиков команд"""
    
    @client_instance.on(events.NewMessage(pattern=r"^\.test$"))
    async def test_handler(event):
        """Команда .test"""
        if event.sender_id != OWNER_ID:
            return
        
        await event.edit("Done! Вы являетесь девственником уже 67 лет.")
    
    
    @client_instance.on(events.NewMessage(pattern=r"^\.savelog"))
    async def savelog_handler(event):
        """Команда для сохранения информации о профиле"""
        
        print(f"🔍 DEBUG: Получена команда: {event.text}")
        print(f"🔍 DEBUG: ID отправителя: {event.sender_id}, Ожидаемый ID: {OWNER_ID}")
        
        if event.sender_id != OWNER_ID:
            print(f"🔍 DEBUG: Отправитель не совпадает с владельцем")
            return
        
        try:
            user_id = None
            
            if event.reply_to_msg_id:
                print(f"🔍 DEBUG: Обнаружен реплай")
                reply_msg = await event.get_reply_message()
                user_id = reply_msg.sender_id
                print(f"🔍 DEBUG: ID из реплая: {user_id}")
            else:
                print(f"🔍 DEBUG: Ищем ID в команде")
                match = re.search(r"\.savelog\s+(\d+)", event.text)
                if match:
                    user_id = int(match.group(1))
                    print(f"🔍 DEBUG: ID из команды: {user_id}")
            
            if not user_id:
                print(f"🔍 DEBUG: ID не найден")
                await event.reply("❌ Укажите ID или сделайте реплай на сообщение пользователя")
                return
            
            print(f"🔍 DEBUG: Начинаем сохранение для ID: {user_id}")
            
            user_full = await client_instance(GetFullUserRequest(user_id))
            user = user_full.users[0]
            
            print(f"🔍 DEBUG: Получена информация о пользователе")
            
            user_id_profile = user.id
            nick_username = user.first_name or ""
            if user.last_name:
                nick_username += f" {user.last_name}"
            nick_username = nick_username.strip()
            
            username = user.username or "Не указан"
            number_user = user.phone or "Не отображен"
            
            print(f"🔍 DEBUG: username={username}, nick={nick_username}, phone={number_user}")
            
            folder_name = username if username != "Не указан" else f"user_{user_id_profile}"
            folder_path = os.path.join(SAVE_PATH, folder_name)
            
            print(f"🔍 DEBUG: Создаю папку: {folder_path}")
            os.makedirs(folder_path, exist_ok=True)
            
            photos_dir = os.path.join(folder_path, "avatars")
            os.makedirs(photos_dir, exist_ok=True)
            
            photo_count = 0
            try:
                print(f"🔍 DEBUG: Начинаю скачивать аватарки")
                async for photo in client_instance.iter_profile_photos(user_id):
                    photo_path = os.path.join(photos_dir, f"avatar_{photo_count}.jpg")
                    await client_instance.download_media(photo, photo_path)
                    photo_count += 1
                    print(f"🔍 DEBUG: Скачана аватарка #{photo_count}")
            except Exception as photo_error:
                print(f"🔍 DEBUG: Ошибка при скачивании аватарок: {photo_error}")
            
            log_content = f"""╔═══《 РАЗНОС КМБП 》═══╗
Данные телеграм профиля {username}

Аватарки находятся в этой папке (если нету, значит их не было или она закрыты в настройках пользователя от чужих глаз)
Актуальный никнейм: {nick_username}
Юзернейм: {username}
Номер телефона: {number_user}
ID: {user_id_profile}
╚═══════════════════════════╝

⟦ ⚡ РАЗНОС КМБП ⚡ ⟧
╰┈➤ 𝙍𝙖𝙯𝙣𝙤𝙨 • 𝙆𝙈𝘽𝙋"""
            
            log_file_path = os.path.join(folder_path, "log.txt")
            with open(log_file_path, "w", encoding="utf-8") as f:
                f.write(log_content)
            
            print(f"🔍 DEBUG: Создан файл log.txt")
            
            await event.reply(f"Done! Данные сохранены в Documents/KMBP/{folder_name}")
            
            print(f"✅ Профиль {username} сохранён в {folder_path}")
            print(f"📸 Скачано аватарок: {photo_count}")
        
        except Exception as e:
            print(f"❌ ОШИБКА: {str(e)}")
            import traceback
            traceback.print_exc()
            await event.reply(f"❌ Ошибка: {str(e)}")
    
    
    @client_instance.on(events.NewMessage(pattern=r"^\.prikol(?:\s+(.+))?$"))
    async def prikol_handler(event):
        """Команда .prikol - отправить прикол"""
        
        if event.sender_id != OWNER_ID:
            return
        
        try:
            args = event.pattern_match.group(1) if event.pattern_match.group(1) else None
            
            # Если есть параметры (ID/URL)
            if args:
                print(f"🔍 DEBUG .prikol: Параметры: {args}")
                
                # Парсим ID или URL
                user_id = None
                message_id = None
                chat_id = None
                
                if args.isdigit():
                    user_id = int(args)
                else:
                    # Пытаемся парсить URL (t.me/...)
                    url_match = re.search(r"t\.me/(\w+)/(\d+)", args)
                    if url_match:
                        username = url_match.group(1)
                        message_id = int(url_match.group(2))
                        
                        # Получаем chat_id по username
                        try:
                            entity = await client_instance.get_entity(username)
                            chat_id = entity.id
                        except:
                            await client_instance.send_message(
                                OWNER_ID,
                                f"❌ Не найден чат с username: {username}"
                            )
                            return
                
                prikol = get_random_prikol()
                
                if not prikol:
                    await client_instance.send_message(
                        OWNER_ID,
                        "❌ Приколов не найдено в базе данных"
                    )
                    return
                
                try:
                    # Отправляем прикол в ЛС пользователю
                    if user_id:
                        await client_instance.send_message(
                            user_id,
                            prikol["text"]
                        )
                        
                        # Отправляем изображения если есть
                        for img in prikol["images"]:
                            await client_instance.send_file(user_id, img)
                    
                    # Или реплаим на сообщение
                    elif message_id and chat_id:
                        await client_instance.send_message(
                            chat_id,
                            prikol["text"],
                            reply_to=message_id
                        )
                        
                        for img in prikol["images"]:
                            await client_instance.send_file(
                                chat_id,
                                img,
                                reply_to=message_id
                            )
                    
                    print(f"✅ Прикол отправлен")
                
                except (ChatAdminRequiredError, ChannelPrivateError) as e:
                    await client_instance.send_message(
                        OWNER_ID,
                        f"❌ Нет доступа к чату/каналу: {str(e)}"
                    )
            
            # Если реплай на сообщение
            elif event.reply_to_msg_id:
                reply_msg = await event.get_reply_message()
                
                prikol = get_random_prikol()
                
                if not prikol:
                    await event.reply("❌ Приколов не найдено")
                    return
                
                try:
                    await event.reply(prikol["text"])
                    
                    for img in prikol["images"]:
                        await client_instance.send_file(
                            event.chat_id,
                            img,
                            reply_to=reply_msg.id
                        )
                    
                    print(f"✅ Прикол отправлен реплаем")
                
                except Exception as e:
                    await event.reply(f"❌ Ошибка: {str(e)}")
            
            else:
                await event.reply("❌ Сделайте реплай или укажите ID/URL")
        
        except Exception as e:
            print(f"❌ ОШИБКА .prikol: {str(e)}")
            import traceback
            traceback.print_exc()
            await client_instance.send_message(OWNER_ID, f"❌ Ошибка .prikol: {str(e)}")
    
    
    @client_instance.on(events.NewMessage(pattern=r"^\.addprikol$", incoming=True, func=lambda e: e.is_private))
    async def addprikol_handler(event):
        """Команда .addprikol - добавить прикол (только в ЛС)"""
        
        if event.sender_id != OWNER_ID:
            return
        
        try:
            # Получаем предыдущее сообщение
            messages = await client_instance.get_messages(event.chat_id, limit=2)
            
            if len(messages) < 2:
                await event.reply("❌ Нет сообщения для сохранения")
                return
            
            source_msg = messages[1]  # Предыдущее сообщение
            
            print(f"🔍 DEBUG .addprikol: Сохраняю сообщение")
            
            # Копируем медиа
            media_files = []
            if source_msg.media:
                media_path = await client_instance.download_media(source_msg.media)
                if media_path:
                    media_files.append(media_path)
            
            # Сохраняем прикол
            prikol_folder = save_prikol_from_message(
                source_msg.text or source_msg.caption or "Прикол без текста",
                media_files
            )
            
            if prikol_folder:
                await event.reply(f"✅ Прикол сохранён в папку: {prikol_folder}")
                print(f"✅ Прикол добавлен: {prikol_folder}")
            else:
                await event.reply("❌ Ошибка при сохранении приколов")
        
        except Exception as e:
            print(f"❌ ОШИБКА .addprikol: {str(e)}")
            import traceback
            traceback.print_exc()
            await event.reply(f"❌ Ошибка: {str(e)}")
