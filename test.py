from telethon import TelegramClient, events

api_id = 38433332
api_hash = "96e2e580a0ff590253237b27b089c728"

client = TelegramClient("my_session", api_id, api_hash)


@client.on(events.NewMessage(pattern=r"^\.test$"))
async def test(event):
    # Проверка: реагируем только на сообщения от владельца аккаунта
    me = await client.get_me()
    if event.sender_id != me.id:
        return
    
    await event.edit("Done! Вы являетесь девственником уже 67 лет.")


print("Скрипт запущен...")
client.start()
client.run_until_disconnected()
