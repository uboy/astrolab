from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from utils.config import settings
from utils.prices import get_prices_sync
from utils.constants import (
    BTN_HOROSCOPE, BTN_COMPATIBILITY, BTN_NUMEROLOGY, BTN_PHOTO_DESTINY,
    BTN_ZODIAC_QUIZ, BTN_LUCK_RESET, BTN_PAYMENT, BTN_ABOUT, BTN_CANCEL,
    BTN_PAYMENT_AMOUNT_5, BTN_PAYMENT_AMOUNT_10, BTN_PAYMENT_AMOUNT_15, BTN_PAYMENT_AMOUNT_20,
    BTN_PAYMENT_METHOD_PIGEONS, BTN_PAYMENT_METHOD_FINGER, BTN_PAYMENT_METHOD_COINS,
    BTN_ADMIN, BTN_SUBSCRIBE, BTN_DONE, BTN_PREMIUM
)

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=BTN_HOROSCOPE), KeyboardButton(text=BTN_COMPATIBILITY)],
        [KeyboardButton(text=BTN_NUMEROLOGY), KeyboardButton(text=BTN_PHOTO_DESTINY)],
        [KeyboardButton(text=BTN_ZODIAC_QUIZ), KeyboardButton(text=BTN_LUCK_RESET)],
        [KeyboardButton(text=BTN_PAYMENT), KeyboardButton(text=BTN_SUBSCRIBE)],
        [KeyboardButton(text=BTN_ABOUT)]
    ],
    resize_keyboard=True
)

def menu_for(user_id: int) -> ReplyKeyboardMarkup:
    """Вернуть главное меню с отображением цен и прав администратора."""
    prices = get_prices_sync()
    is_admin = user_id in getattr(settings, "ADMINS", [])
    keyboard = [
        [
            KeyboardButton(text=f"{BTN_HOROSCOPE} ({prices.get('horoscope', 1)} у.е)"),
            KeyboardButton(text=f"{BTN_COMPATIBILITY} ({prices.get('compatibility', 1)} у.е)")
        ],
        [
            KeyboardButton(text=f"{BTN_NUMEROLOGY} ({prices.get('numerology', 1)} у.е)"),
            KeyboardButton(text=f"{BTN_PHOTO_DESTINY} ({prices.get('photo_destiny', 1)} у.е)")
        ],
        [
            KeyboardButton(text=f"{BTN_ZODIAC_QUIZ} ({prices.get('zodiac_quiz', 1)} у.е)"),
            KeyboardButton(text=f"{BTN_LUCK_RESET} ({prices.get('luck_reset', 1)} у.е)")
        ],
        [KeyboardButton(text=BTN_PREMIUM), KeyboardButton(text=f"{BTN_SUBSCRIBE} ({prices.get('subscription', 1)} у.е/день)")],
        [KeyboardButton(text=BTN_PAYMENT), KeyboardButton(text=BTN_ABOUT)],
    ]
    if is_admin:
        keyboard.append([KeyboardButton(text=BTN_ADMIN)])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

payment_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=BTN_PAYMENT_AMOUNT_5), KeyboardButton(text=BTN_PAYMENT_AMOUNT_10)],
        [KeyboardButton(text=BTN_PAYMENT_AMOUNT_15), KeyboardButton(text=BTN_PAYMENT_AMOUNT_20)],
        [KeyboardButton(text=BTN_CANCEL)]
    ],
    resize_keyboard=True
)

payment_type_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=BTN_PAYMENT_METHOD_PIGEONS), KeyboardButton(text=BTN_PAYMENT_METHOD_FINGER)],
        [KeyboardButton(text=BTN_PAYMENT_METHOD_COINS)],
        [KeyboardButton(text=BTN_CANCEL)]
    ],
    resize_keyboard=True
)

cancel_menu = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text=BTN_CANCEL)]],
    resize_keyboard=True
)

cancel_or_done_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=BTN_DONE)],
        [KeyboardButton(text=BTN_CANCEL)]
    ],
    resize_keyboard=True
)
