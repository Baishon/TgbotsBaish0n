from telethon import TelegramClient, events
from telethon.tl.functions.users import GetFullUserRequest
import os
import re

api_id = 38433332
api_hash = "96e2e580a0ff590253237b27b089c728"

client = TelegramClient("my_session", api_id, api_hash)

# ID владельца аккаунта
OWNER_ID = 7545068007

# Путь для сохранения
SAVE_PATH = "/storage/emulated/0/Documents/KMBP"


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
        
        # Проверка: команда работает только от владельца
        if event.sender_id != OWNER_ID:
            print(f"🔍 DEBUG: Отправитель не совпадает с владельцем")
            return
        
        try:
            user_id = None
            
            # Проверяем, есть ли реплай
            if event.reply_to_msg_id:
                print(f"🔍 DEBUG: Обнаружен реплай")
                reply_msg = await event.get_reply_message()
                user_id = reply_msg.sender_id
                print(f"🔍 DEBUG: ID из реплая: {user_id}")
            else:
                # Ищем ID в самой команде
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
            
            # Получаем полную информацию о пользователе
            user_full = await client_instance(GetFullUserRequest(user_id))
            user = user_full.user
            
            print(f"🔍 DEBUG: Получена информация о пользователе")
            
            # Извлекаем информацию
            user_id_profile = user.id
            nick_username = user.first_name or ""
            if user.last_name:
                nick_username += f" {user.last_name}"
            nick_username = nick_username.strip()
            
            username = user.username or "Не указан"
            number_user = user.phone or "Не отображен"
            
            print(f"🔍 DEBUG: username={username}, nick={nick_username}, phone={number_user}")
            
            # Создаём директорию
            folder_name = username if username != "Не указан" else f"user_{user_id_profile}"
            folder_path = os.path.join(SAVE_PATH, folder_name)
            
            print(f"🔍 DEBUG: Создаю папку: {folder_path}")
            os.makedirs(folder_path, exist_ok=True)
            
            # Скачиваем аватарки
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
            
            # Создаём файл log.txt
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
            
            # Отправляем подтверждение
            await event.reply(f"Done! Данные сохранены в Documents/KMBP/{folder_name}")
            
            print(f"✅ Профиль {username} сохранён в {folder_path}")
            print(f"📸 Скачано аватарок: {photo_count}")
        
        except Exception as e:
            print(f"❌ ОШИБКА: {str(e)}")
            import traceback
            traceback.print_exc()
            await event.reply(f"❌ Ошибка: {str(e)}")
