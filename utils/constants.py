"""
Константы для текстов кнопок и сообщений бота
"""

# Названия кнопок главного меню
BTN_HOROSCOPE = "Гороскоп"
BTN_COMPATIBILITY = "Совместимость"
BTN_NUMEROLOGY = "Нумерология"
BTN_PHOTO_DESTINY = "Судьба по фото"
BTN_ZODIAC_QUIZ = "Угадай мой знак"
BTN_LUCK_RESET = "Перезапуск удачи"
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
BTN_ADMIN_UNSUB = "Админ: отписать пользователя"
BTN_ADMIN_SET_TIME = "Админ: время рассылки"
BTN_ADMIN_BROADCAST = "Админ: отправить подписчикам"
BTN_ADMIN_USERS = "Пользователи"
BTN_ADMIN_NEXT_PAGE = "▶️ Следующая страница"
BTN_ADMIN_PREV_PAGE = "◀️ Предыдущая страница"
BTN_ADMIN_BACK_USERS = "↩️ Назад к пользователям"
BTN_ADMIN_USER_INFO = "ℹ️ Профиль/баланс"
BTN_ADMIN_USER_HISTORY = "📜 История действий"
BTN_ADMIN_USER_RESET = "🔄 Сброс лимитов"
BTN_ADMIN_USER_SUBSCRIBE = "✅ Подписать"
BTN_ADMIN_USER_UNSUBSCRIBE = "🚫 Отписать"
BTN_ADMIN_USER_SET_TIME = "⏰ Время подписки"
BTN_ADMIN_USER_DELETE = "🗑️ Удалить пользователя"

# Кнопки оплаты
BTN_PAYMENT_AMOUNT_5 = "5"
BTN_PAYMENT_AMOUNT_10 = "10"
BTN_PAYMENT_AMOUNT_15 = "15"
BTN_PAYMENT_AMOUNT_20 = "20"
BTN_PAYMENT_METHOD_PIGEONS = "Голубиной почтой 🕊️"
BTN_PAYMENT_METHOD_FINGER = "Палец к камере ✋📸"
BTN_PAYMENT_METHOD_COINS = "Монетки в портал 🪙✨"
BTN_SUBSCRIBE = "Подписка на гороскоп"
BTN_UNSUBSCRIBE = "Отписаться от рассылки"
BTN_DONE = "Готово"

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
    BTN_ZODIAC_QUIZ,
    BTN_LUCK_RESET,
    BTN_PAYMENT,
    BTN_ABOUT,
    BTN_SUBSCRIBE,
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
    BTN_ADMIN_UNSUB,
    BTN_ADMIN_SET_TIME,
    BTN_ADMIN_BROADCAST,
    BTN_ADMIN_USERS,
    BTN_ADMIN_NEXT_PAGE,
    BTN_ADMIN_PREV_PAGE,
    BTN_ADMIN_BACK_USERS,
    BTN_ADMIN_USER_INFO,
    BTN_ADMIN_USER_HISTORY,
    BTN_ADMIN_USER_RESET,
    BTN_ADMIN_USER_SUBSCRIBE,
    BTN_ADMIN_USER_UNSUBSCRIBE,
    BTN_ADMIN_USER_SET_TIME,
    BTN_ADMIN_USER_DELETE,
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

# Подписки
MSG_SUBSCRIBE_ASK_BIRTHDATE = "📅 Введите дату рождения для ежедневного гороскопа (ДД.MM.ГГГГ):"
MSG_SUBSCRIBE_OK = "✅ Подписка оформлена! Гороскоп придёт между 12:00 и 15:00 (ваше время по умолчанию: {time})."
MSG_UNSUB_OK = "❌ Вы отписаны от рассылки ежедневных гороскопов."
MSG_ALREADY_SUBSCRIBED = "🌞 Вы уже в списке на ежедневные гороскопы. Хотите отписаться?"
MSG_NOT_SUBSCRIBED = "ℹ️ Вы ещё не подписаны. Хотите подписаться?"
MSG_SUB_TIME_SET = "⏰ Время рассылки обновлено: {time}. Сообщения приходят только с 12:00 до 15:00."
MSG_SUB_INVALID_DATE = "❌ Неверный формат даты. Введите в формате ДД.MM.ГГГГ."

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
MSG_ZODIAC_QUIZ_GREETING = "🧩 Давай угадаем твой знак зодиака! Честно ответь на несколько вопросов."
MSG_ZODIAC_QUIZ_DONE = "🔮 Спасибо за ответы! Сейчас попробую угадать твой знак..."
MSG_ZODIAC_QUIZ_ERROR = "🤔 Не смог угадать знак. Попробуй снова позже."
MSG_LUCK_RESET_GREETING = "🍀 Проверим, где застряла удача, и перезапустим её."
MSG_COMPATIBILITY_PHOTO_PROMPT = "📸 Отправьте 1–2 фото или введите имена и даты рождения пары. Можно сделать и то, и другое."
MSG_COMPATIBILITY_COLLECTED = "🧪 Данные получены! Запускаю магический анализ совместимости..."

# Админские сообщения
MSG_ADMIN_MENU = "🛠️ Админка: выберите действие"
MSG_NO_USERS = "⚠️ Пользователей ещё нет."
MSG_LIMITS_RESET = "✅ Лимиты всех пользователей сброшены."
MSG_USER_STATS_HEADER = "📊 Статистика пользователей:\n{stats}"
MSG_ADMIN_ASK_USER_ID = "Введите ID пользователя:"
MSG_ADMIN_UNSUB_OK = "✅ Пользователь {user_id} отписан от рассылки."
MSG_ADMIN_TIME_OK = "⏰ Время рассылки для {user_id} установлено: {time}."
MSG_ADMIN_INVALID_TIME = "⚠️ Введите время в формате ЧЧ:ММ (12:00–15:00)."
MSG_ADMIN_NO_USER = "Пользователь с ID {user_id} не найден."
MSG_ADMIN_BROADCAST_ASK = "Введите текст уведомления для всех подписчиков:"
MSG_ADMIN_BROADCAST_DONE = "✅ Уведомление отправлено подписчикам: {count} чел."

# Сообщения о проклятиях
MSG_LUCK_RESET_RESULT = "🍀 Ваша полоса невезения выглядит так:\n\n{curse}\n\nПерезапустим удачу?"
MSG_LUCK_RESET_RITUAL = "✨ Ритуал перезапуска удачи:\n\n{ritual}\n\n🧲 Притягивайте хорошее — и возвращайтесь, если потребуется ещё заряд."
MSG_LUCK_RESET_SKIP = "🙂 Хорошо, оставляем всё как есть. Если захочется больше удачи — жмите «Перезапуск удачи»!"

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
