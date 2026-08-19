from telethon import TelegramClient, events
from datetime import datetime
import pytz
import asyncio

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


@client.on(events.NewMessage(incoming=True))
async def startup_handler(event):
    """Обработчик для различных команд"""
    pass


async def startup():
    """Функция, выполняемая при запуске бота"""
    await client.start()
    
    # Отправляем сообщение о запуске
    startup_time = get_kyiv_time()
    await client.send_message(
        OWNER_ID,
        f"The bot has been successfully launched and is running in the background. Date: {startup_time}"
    )
    print(f"✅ Bot started at {startup_time}")


async def shutdown():
    """Функция, выполняемая при остановке бота"""
    shutdown_time = get_kyiv_time()
    
    # Отправляем сообщение об остановке
    await client.send_message(
        OWNER_ID,
        f"The bot is finishing its work. Data: {shutdown_time}"
    )
    print(f"⏹️ Bot stopped at {shutdown_time}")
    
    await client.disconnect()


async def main():
    """Главная функция"""
    try:
        await startup()
        
        # Запускаем бота в режиме ожидания входящих сообщений
        async with client:
            await client.run_until_disconnected()
    
    except KeyboardInterrupt:
        print("\n🛑 Скрипт прерван пользователем")
        await shutdown()
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        await shutdown()


if __name__ == "__main__":
    asyncio.run(main())
