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
SAVE_PATH = "/sdcard/Documents/KMBP"


def register_handlers(client_instance):
    """Регистрация всех обработчиков команд"""
    
    @client_instance.on(events.NewMessage(pattern=r"^\.test$"))
    async def test_handler(event):
        """Команда .test"""
        me = await client_instance.get_me()
        if event.sender_id != me.id:
            return
        
        await event.edit("Done! Вы являетесь девственником уже 67 лет.")
    
    
    @client_instance.on(events.NewMessage(pattern=r"^\.savelog(?:\s+(\d+))?$"))
    async def savelog_handler(event):
        """Команда для сохранения информации о профиле"""
        
        # Проверка: команда работает только от владельца
        me = await client_instance.get_me()
        if event.sender_id != me.id:
            return
        
        try:
            user_id = None
            
            # Проверяем, есть ли реплай
            if event.reply_to_msg_id:
                reply_msg = await event.get_reply_message()
                user_id = reply_msg.sender_id
            else:
                # Ищем ID в самой команде
                match = re.search(r"^\.savelog\s+(\d+)", event.text)
                if match:
                    user_id = int(match.group(1))
            
            if not user_id:
                await event.reply("❌ Укажите ID или сделайте реплай на сообщение пользователя")
                return
            
            # Получаем полную информацию о пользователе
            user_full = await client_instance(GetFullUserRequest(user_id))
            user = user_full.user
            
            # Извлекаем информацию
            user_id_profile = user.id
            nick_username = user.first_name or ""
            if user.last_name:
                nick_username += f" {user.last_name}"
            nick_username = nick_username.strip()
            
            username = user.username or "Не указан"
            number_user = user.phone or "Не отображен"
            
            # Создаём директорию
            folder_name = username if username != "Не указан" else f"user_{user_id_profile}"
            folder_path = os.path.join(SAVE_PATH, folder_name)
            os.makedirs(folder_path, exist_ok=True)
            
            # Скачиваем аватарки
            photos_dir = os.path.join(folder_path, "avatars")
            os.makedirs(photos_dir, exist_ok=True)
            
            photo_count = 0
            try:
                async for photo in client_instance.iter_profile_photos(user_id):
                    photo_path = os.path.join(photos_dir, f"avatar_{photo_count}.jpg")
                    await client_instance.download_media(photo, photo_path)
                    photo_count += 1
            except:
                pass  # Если аватарок нет или они закрыты
            
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
            
            # Отправляем подтверждение
            await event.reply(f"Done! Данные сохранены в Documents/KMBP/{folder_name}")
            
            print(f"✅ Профиль {username} сохранён в {folder_path}")
            print(f"📸 Скачано аватарок: {photo_count}")
        
        except Exception as e:
            await event.reply(f"❌ Ошибка: {str(e)}")
            print(f"Ошибка при сохранении профиля: {e}")
