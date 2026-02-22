"""
Константы для текстов кнопок и сообщений бота
"""

# Названия кнопок главного меню
BTN_HOROSCOPE = "Гороскоп"
BTN_COMPATIBILITY = "Совместимость"
BTN_NUMEROLOGY = "Нумерология"
BTN_PHOTO_DESTINY = "Судьба по фото"
BTN_CURSE_REMOVAL = "Снятие порчи"
BTN_CURSE_DETECTION = "Определение проклятия"
BTN_PAYMENT = "Оплата"
BTN_ABOUT = "О компании"

# Кнопки действий
BTN_BACK = "Назад"
BTN_CANCEL = "Отмена"
BTN_YES = "Да"
BTN_NO = "Нет"

# Админские кнопки
BTN_ADMIN = "Админка"
BTN_USER_STATS = "Статистика пользователей"
BTN_RESET_LIMITS = "Сброс лимитов"

# Кнопки оплаты
BTN_PAYMENT_AMOUNT_5 = "5"
BTN_PAYMENT_AMOUNT_10 = "10"
BTN_PAYMENT_AMOUNT_15 = "15"
BTN_PAYMENT_AMOUNT_20 = "20"
BTN_PAYMENT_METHOD_PIGEONS = "Голубиной почтой 🕊️"
BTN_PAYMENT_METHOD_FINGER = "Палец к камере ✋📸"
BTN_PAYMENT_METHOD_COINS = "Монетки в портал 🪙✨"

# Цена услуги
PRICE_HOROSCOPE = 1
PRICE_COMPATIBILITY = 1
PRICE_NUMEROLOGY = 1
PRICE_PHOTO_DESTINY = 1
PRICE_CURSE_REMOVAL = 1

# Списки для проверки
MAIN_MENU_BUTTONS = {
    BTN_HOROSCOPE,
    BTN_COMPATIBILITY,
    BTN_NUMEROLOGY,
    BTN_PHOTO_DESTINY,
    BTN_CURSE_REMOVAL,
    BTN_CURSE_DETECTION,
    BTN_PAYMENT,
    BTN_ABOUT,
}

PAYMENT_AMOUNTS = {BTN_PAYMENT_AMOUNT_5, BTN_PAYMENT_AMOUNT_10, BTN_PAYMENT_AMOUNT_15, BTN_PAYMENT_AMOUNT_20}

PAYMENT_METHODS = {
    BTN_PAYMENT_METHOD_PIGEONS,
    BTN_PAYMENT_METHOD_FINGER,
    BTN_PAYMENT_METHOD_COINS,
}

ADMIN_BUTTONS = {
    BTN_ADMIN,
    BTN_USER_STATS,
    BTN_RESET_LIMITS,
    BTN_CANCEL,
}

ALL_MENU_BUTTONS = MAIN_MENU_BUTTONS | ADMIN_BUTTONS

# Сообщения
MSG_NO_FREE_PAID = "💰 У вас закончились бесплатные и оплаченные обращения! Пополните баланс."
MSG_RETURNED_TO_MENU = "🔮 Вы вернулись в главное меню."
MSG_RETURNING_TO_MENU = "🔮 Возвращаю в главное меню:"
MSG_PAYMENT_CANCELLED = "❌ Оплата отменена."
MSG_ACTION_CANCELLED = "❌ Действие отменено."
MSG_NO_ACCESS = "❌ У вас нет доступа к админке."
MSG_NO_COMMAND_ACCESS = "❌ У вас нет доступа к этой команде."

# Форматы сообщений
MSG_BALANCE_FORMAT = "📊 Бесплатные: {free_count}, 💎 Оплаченные: {paid_count}"
MSG_RESPONSE_WITH_BALANCE = "✨ {response}\n\n{balance}"

# Сообщения о запросе во вселенную
MSG_QUERYING_UNIVERSE = "🔮 Запрос во вселенную отправлен... Это может занять некоторое время. Бот вернется с ответом! ✨"

# Ошибки Ollama
MSG_OLLAMA_HOROSCOPE_ERROR = "🤷‍♂️ Бот не смог сгенерировать гороскоп. Попробуйте ещё раз!"
MSG_OLLAMA_COMPATIBILITY_ERROR = "🤷‍♂️ Бот не смог сгенерировать совместимость. Попробуйте ещё раз!"
MSG_OLLAMA_CURSE_ERROR = "🤷‍♂️ Бот не смог провести ритуал снятия порчи. Попробуйте ещё раз!"
MSG_OLLAMA_NUMEROLOGY_ERROR = "🤷‍♂️ Бот не смог провести нумерологический анализ. Попробуйте ещё раз!"
MSG_OLLAMA_PHOTO_ERROR = "🤷‍♂️ Бот не смог проанализировать фото. Попробуйте ещё раз!"

# Имена пользователей по умолчанию
DEFAULT_USER_NAME = "Друг"
DEFAULT_USER_NAME_LOWER = "друг"

# Сообщения об оплате
MSG_PAYMENT_SUCCESS = "✅ Оплата прошла успешно! Добавлено {amount} платных сообщений.\n{balance}"
MSG_PAYMENT_PROCESSING = "💰 Пытаемся оплатить {amount} услуг с помощью: {method}… Подождите 5 секунд ⏳"

PAYMENT_FAIL_MESSAGES = {
    BTN_PAYMENT_METHOD_PIGEONS: "😱 Голубей съели по дороге! Попробуйте снова.",
    BTN_PAYMENT_METHOD_FINGER: "🧙‍♂️ На палец наложили порчу! Оплата не прошла.",
    BTN_PAYMENT_METHOD_COINS: "💨 Портал отказался принимать монетки! Попробуйте другой способ.",
}

# Ошибки валидации
MSG_INVALID_DATE_FORMAT = "❌ Неверный формат. Введите дату в формате ДД.MM.ГГГГ."
MSG_INVALID_NAMES_FORMAT = "❌ Пожалуйста, введите ровно два имени через запятую."
MSG_INVALID_NAME = "❌ Имя не может быть пустым. Пожалуйста, введите ваше имя."
MSG_INVALID_AMOUNT = "⚠️ Пожалуйста, выберите 5, 10, 15 или 20."
MSG_INVALID_PAYMENT_METHOD = "⚠️ Пожалуйста, выберите доступный способ оплаты."
MSG_INVALID_DECISION = "⚠️ Пожалуйста, выберите один из вариантов: Да, Нет или Назад."

# Возрастные ограничения
MSG_UNDERAGE = "🔞 Сервис только для совершеннолетних. Вернёшься, когда станешь старше (шутка)."
MSG_OVERAGE = "🎉 Ого! Вы вечно молоды душой — вы знаете всё лучше меня 😉"

# Приветствия и запросы
MSG_HOROSCOPE_GREETING = "🧙‍♀️ Привет, {name}! Введите дату рождения в формате ДД.MM.ГГГГ, и я приоткрою тайны вашей судьбы… ✨"
MSG_COMPATIBILITY_GREETING = "💞 Привет, {name}! Введите два имени через запятую для анализа совместимости:\nНапример: Анна, Денис"
MSG_NUMEROLOGY_GREETING = "🔢 Привет, {name}! Для нумерологического анализа мне нужна дата рождения в формате ДД.MM.ГГГГ.\n\nИспользовать имя из профиля ({profile_name}) иначе можешь ввести своё?"
MSG_NUMEROLOGY_ASK_NAME = "📝 Введите ваше имя для нумерологического анализа:"
MSG_NUMEROLOGY_ASK_BIRTHDATE = "📅 Введите дату рождения в формате ДД.MM.ГГГГ:"
MSG_PHOTO_DESTINY_GREETING = "📸 Привет, {name}! Загрузите фотографию, и я расскажу о вашей судьбе по фото! ✨"
MSG_PHOTO_INVALID = "❌ Пожалуйста, загрузите фотографию (изображение)."
MSG_PAYMENT_GREETING = "💳 Привет, {name}! Сколько услуг хотите купить?"
MSG_FALLBACK_GREETING = "🔮 Привет, {name}! Я магический бот-гадалка ✨\n\nВыберите услугу из меню или напишите команду:\n- {services}"

# Админские сообщения
MSG_ADMIN_MENU = "🛠️ Админка: выберите действие"
MSG_NO_USERS = "⚠️ Пользователей ещё нет."
MSG_LIMITS_RESET = "✅ Лимиты всех пользователей сброшены."
MSG_USER_STATS_HEADER = "📊 Статистика пользователей:\n{stats}"

# Сообщения о проклятиях
MSG_CURSE_REMOVAL_START = "🧹 Выберите тип порчи из списка или введите свой текст:"
MSG_CURSE_DETECTION_RESULT = "🔮 Результат диагностики:\n\n{curse}\n\nХотите снять это проклятие?"
MSG_CURSE_RITUAL = "✨ Отлично! Вот обряд для снятия проклятия:\n\n{ritual}\n\n🔮 Проклятие будет снято после выполнения обряда!"
MSG_CURSE_REMAINS = "😔 Проклятие останется на вас до снятия.\n\nЕсли передумаете, всегда можете вернуться и снять его!"

# О компании
MSG_ABOUT_COMPANY = (
    "🔮 <b>Telegram-бот «Великий Шар»</b>\n\n"
    "🏢 <b>НИИ НПО «Шар Консалт Инкорпорейтед»</b>\n"
    "Мы занимаемся самыми загадочными и паранормальными услугами с 2025 года.\n\n"
    "💫 <b>Наш девиз:</b> \"Ваше будущее всегда под рукой, особенно если открыть Telegram.\"\n\n"
    "🤖 <b>О боте</b>\n"
    "Я — магический помощник для:\n"
    "✨ Гороскопов любого уровня мистики\n"
    "💑 Совместимости людей и даже любимых кактусов\n"
    "🛡️ Диагностики и снятия порчи\n"
    "🕊️ Оплаты магией, голубями, пальцем и добрым словом\n\n"
    "📜 Делю слишком длинные пророчества, чтобы не утомлять колдунов и пользователей.\n\n"
    "🎭 Магия и ритуалы для всех, кто верит в чудеса 🕊️\n\n"
    "🔮 <b>Ваше будущее зависит только от одной кнопки и немного — от судьбы.</b>\n\n"
    "© 2025 НИИ НПО «Шар Консалт Инкорпорейтед». Все магические права защищены."
)
