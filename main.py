from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import base, horoscope, compatibility, numerology, photo_destiny, curse, curse_detection, admin
from utils.config import settings
import asyncio

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Регистрируем роутеры
dp.include_router(horoscope.router)
dp.include_router(compatibility.router)
dp.include_router(numerology.router)
dp.include_router(photo_destiny.router)
dp.include_router(curse.router)
dp.include_router(curse_detection.router)
dp.include_router(admin.router)
dp.include_router(base.router)

if __name__ == "__main__":
    print("🚀 Бот запущен!")
    asyncio.run(dp.start_polling(bot))
