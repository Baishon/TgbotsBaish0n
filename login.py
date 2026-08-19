from telethon import TelegramClient

api_id = 38433332
api_hash ="96e2e580a0ff590253237b27b089c728"

client = TelegramClient("my_session", api_id, api_hash)

async def main():
    await client.start()
    print("Аккаунт успешно подключён!")
    print("Сессия сохранена в my_session.session")

with client:
    client.loop.run_until_complete(main())
