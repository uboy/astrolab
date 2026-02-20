from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from utils.constants import (
    BTN_HOROSCOPE, BTN_COMPATIBILITY, BTN_NUMEROLOGY, BTN_PHOTO_DESTINY,
    BTN_CURSE_REMOVAL, BTN_CURSE_DETECTION, BTN_PAYMENT, BTN_ABOUT, BTN_CANCEL,
    BTN_PAYMENT_AMOUNT_5, BTN_PAYMENT_AMOUNT_10, BTN_PAYMENT_AMOUNT_15, BTN_PAYMENT_AMOUNT_20,
    BTN_PAYMENT_METHOD_PIGEONS, BTN_PAYMENT_METHOD_FINGER, BTN_PAYMENT_METHOD_COINS
)

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=BTN_HOROSCOPE), KeyboardButton(text=BTN_COMPATIBILITY)],
        [KeyboardButton(text=BTN_NUMEROLOGY), KeyboardButton(text=BTN_PHOTO_DESTINY)],
        [KeyboardButton(text=BTN_CURSE_REMOVAL), KeyboardButton(text=BTN_CURSE_DETECTION)],
        [KeyboardButton(text=BTN_PAYMENT), KeyboardButton(text=BTN_ABOUT)]
    ],
    resize_keyboard=True
)

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