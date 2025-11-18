from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import base, horoscope, compatibility, numerology, photo_destiny, curse, curse_detection, admin
from utils.config import settings
import asyncio

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    # Регистрируем роутеры
    dp.include_router(horoscope.router)
    dp.include_router(compatibility.router)
    dp.include_router(numerology.router)
    dp.include_router(photo_destiny.router)
    dp.include_router(curse.router)
    dp.include_router(curse_detection.router)
    dp.include_router(admin.router)
    dp.include_router(base.router)
    print("🚀 Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError as e:
        if "asyncio.run() cannot be called from a running event loop" in str(e):
            loop = asyncio.get_event_loop()
            loop.run_until_complete(main())
        else:
            raise
