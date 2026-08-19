from telethon import TelegramClient, events
from datetime import datetime
import pytz
import asyncio
from handlers import register_handlers

api_id = 38433332
api_hash = "96e2e580a0ff590253237b27b089c728"

client = TelegramClient("my_session", api_id, api_hash)

# ID пользователя для уведомлений
OWNER_ID = 7545068007

# Таймзона Киева
KYIV_TZ = pytz.timezone('Europe/Kyiv')


def get_kyiv_time():
    """Получить текущее время в Киеве"""
    return datetime.now(KYIV_TZ).strftime("%Y-%m-%d %H:%M:%S")


async def startup():
    """Функция, выполняемая при запуске бота"""
    # Отправляем сообщение о запуске
    startup_time = get_kyiv_time()
    try:
        await client.send_message(
            OWNER_ID,
            f"The bot has been successfully launched and is running in the background. Date: {startup_time}"
        )
        print(f"✅ Bot started at {startup_time}")
    except Exception as e:
        print(f"⚠️ Не удалось отправить сообщение о запуске: {e}")


async def shutdown():
    """Функция, выполняемая при остановке бота"""
    shutdown_time = get_kyiv_time()
    
    try:
        # Отправляем сообщение об остановке
        await client.send_message(
            OWNER_ID,
            f"The bot is finishing its work. Data: {shutdown_time}"
        )
        print(f"⏹️ Bot stopped at {shutdown_time}")
    except Exception as e:
        print(f"⚠️ Не удалось отправить сообщение об остановке: {e}")
    
    await client.disconnect()


async def main():
    """Главная функция"""
    try:
        await client.start()
        
        # Регистрируем обработчики команд
        register_handlers(client)
        
        await startup()
        
        # Запускаем бота в режиме ожидания входящих сообщений
        print("🤖 Бот запущен и ожидает команд...")
        await client.run_until_disconnected()
    
    except KeyboardInterrupt:
        print("\n🛑 Скрипт прерван пользователем")
        await shutdown()
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        await shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n✋ Выход...")
