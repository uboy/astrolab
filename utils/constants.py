"""
Константы для текстов кнопок и сообщений бота
"""

# Названия кнопок главного меню
BTN_HOROSCOPE = "Гороскоп на неделю"
BTN_COMPATIBILITY = "Совместимость"
BTN_CANDIDATE_COMPATIBILITY = "Совместимость с компанией"
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
BTN_ADMIN_BROADCAST = "📣 Бродкаст подписчикам"
BTN_ADMIN_USERS = "Пользователи"
BTN_ADMIN_NEXT_PAGE = "▶️ Следующая страница"
BTN_ADMIN_PREV_PAGE = "◀️ Предыдущая страница"
BTN_ADMIN_BACK_USERS = "↩️ Назад к пользователям"
BTN_ADMIN_USER_INFO = "ℹ️ Профиль/баланс"
BTN_ADMIN_USER_HISTORY = "📜 История действий"
BTN_ADMIN_USER_RESET = "🔄 Сброс лимитов"
BTN_ADMIN_USER_SET_BALANCE = "💳 Установить баланс"
BTN_ADMIN_USER_SUBSCRIBE = "✅ Подписать"
BTN_ADMIN_USER_UNSUBSCRIBE = "🚫 Отписать"
BTN_ADMIN_USER_SET_TIME = "⏰ Время подписки"
BTN_ADMIN_USER_DELETE = "🗑️ Удалить пользователя"
BTN_ADMIN_SETTINGS = "⚙️ Настройки"
BTN_ADMIN_LOGS = "📝 Логи"
BTN_ADMIN_USER_SEND = "📨 Отправить сообщение"
BTN_ADMIN_SUBSCRIBED = "Подписчики"
BTN_ADMIN_SEND_SUBS = "🚀 Отправить подписчикам"
BTN_ADMIN_PRICES = "💲 Цены"
BTN_ADMIN_COMPANY_PARAMS = "🏢 Параметры компании"
BTN_ADMIN_ABOUT_BOT = "🤖 О боте"
BTN_ADMIN_COMPANY_PARAMS_TEMPLATE = "📄 Шаблон параметров"

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
BTN_PREMIUM = "Премиум"
BTN_PREMIUM_1D = "Премиум 1 день"
BTN_PREMIUM_2D = "Премиум 2 дня"
BTN_PREMIUM_3D = "Премиум 3 дня"

# Цена услуги
PRICE_HOROSCOPE = 1
PRICE_COMPATIBILITY = 1
PRICE_CANDIDATE_COMPATIBILITY = 1
PRICE_NUMEROLOGY = 1
PRICE_PHOTO_DESTINY = 1
PRICE_CURSE_REMOVAL = 1
PRICE_ZODIAC_QUIZ = 1
PRICE_LUCK_RESET = 1
PRICE_PREMIUM_1D = 5
PRICE_PREMIUM_2D = 8
PRICE_PREMIUM_3D = 10
PRICE_SUBSCRIPTION = 1
DEFAULT_PRICES = {
    "horoscope": PRICE_HOROSCOPE,
    "compatibility": PRICE_COMPATIBILITY,
    "candidate_compatibility": PRICE_CANDIDATE_COMPATIBILITY,
    "numerology": PRICE_NUMEROLOGY,
    "photo_destiny": PRICE_PHOTO_DESTINY,
    "zodiac_quiz": PRICE_ZODIAC_QUIZ,
    "luck_reset": PRICE_LUCK_RESET,
    "premium_1d": PRICE_PREMIUM_1D,
    "premium_2d": PRICE_PREMIUM_2D,
    "premium_3d": PRICE_PREMIUM_3D,
    "subscription": PRICE_SUBSCRIPTION,
}
PREMIUM_PLANS = {
    "premium_1d": PRICE_PREMIUM_1D,
    "premium_2d": PRICE_PREMIUM_2D,
    "premium_3d": PRICE_PREMIUM_3D,
}

# Списки для проверки
MAIN_MENU_BUTTONS = {
    BTN_HOROSCOPE,
    BTN_COMPATIBILITY,
    BTN_CANDIDATE_COMPATIBILITY,
    BTN_NUMEROLOGY,
    BTN_PHOTO_DESTINY,
    BTN_ZODIAC_QUIZ,
    BTN_LUCK_RESET,
    BTN_PAYMENT,
    BTN_ABOUT,
    BTN_SUBSCRIBE,
    BTN_PREMIUM,
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
    BTN_ADMIN_USER_SET_BALANCE,
    BTN_ADMIN_USER_SUBSCRIBE,
    BTN_ADMIN_USER_UNSUBSCRIBE,
    BTN_ADMIN_USER_SET_TIME,
    BTN_ADMIN_USER_DELETE,
    BTN_ADMIN_USER_SEND,
    BTN_ADMIN_SETTINGS,
    BTN_ADMIN_LOGS,
    BTN_ADMIN_PRICES,
    BTN_ADMIN_COMPANY_PARAMS,
    BTN_ADMIN_ABOUT_BOT,
    BTN_ADMIN_COMPANY_PARAMS_TEMPLATE,
}

ALL_MENU_BUTTONS = MAIN_MENU_BUTTONS | ADMIN_BUTTONS

# Сообщения
MSG_NO_FREE_PAID = "💰 У вас закончились бесплатные и оплаченные обращения! Пополните баланс."
MSG_NOT_ENOUGH_FUNDS = "💰 Недостаточно средств для {feature}. Нужно: {price} у.е, доступно: {free}+{paid}."
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
MSG_OLLAMA_CANDIDATE_ERROR = "🤷‍♂️ Бот не смог качественно разобрать резюме. Попробуйте другой файл или вставьте текстом."

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

# Лимиты
MSG_RATE_LIMIT = "✨ Вселенная устала от ваших запросов. Подождите {wait}s и попробуйте снова."
OLLAMA_FEATURES = {"horoscope", "compatibility", "numerology", "photo_destiny", "zodiac_quiz"}
OLLAMA_PER_MIN = 1
OLLAMA_PER_HOUR = 50
OTHER_PER_MIN = 10
OTHER_PER_HOUR = 500
PREMIUM_MULTIPLIER = 3

# Подписки
MSG_SUBSCRIBE_ASK_BIRTHDATE = "📅 Введите дату рождения для ежедневного гороскопа на сегодня и завтра (ДД.MM.ГГГГ). Стоимость {price} у.е в день."
MSG_SUBSCRIBE_OK = "✅ Подписка оформлена! Гороскоп на сегодня и завтра придёт в окне 11:00–19:00 (ваше время по умолчанию: {time}). Списываю {price} у.е при каждой отправке."
MSG_UNSUB_OK = "❌ Вы отписаны от рассылки ежедневных гороскопов."
MSG_ALREADY_SUBSCRIBED = "🌞 Вы уже в списке на ежедневные гороскопы. Хотите отписаться?"
MSG_NOT_SUBSCRIBED = "ℹ️ Вы ещё не подписаны. Хотите подписаться?"
MSG_SUB_TIME_SET = "⏰ Время рассылки обновлено: {time}. Сообщения приходят в окне 11:00–19:00 или по указанному времени."
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
MSG_HOROSCOPE_GREETING = "🧙‍♀️ Привет, {name}! Введите дату рождения в формате ДД.MM.ГГГГ — составлю гороскоп на эту и следующую недели… ✨"
MSG_COMPATIBILITY_GREETING = "💞 Привет, {name}! Введите два имени через запятую для анализа совместимости:\nНапример: Анна, Денис"
MSG_CANDIDATE_COMPATIBILITY_GREETING = "🏢 Привет, {name}! Проверим совместимость кандидата с компанией."
MSG_CANDIDATE_RESUME_PROMPT = "Пришлите резюме файлом (docx/pdf/md) или текстом одним сообщением."
MSG_CANDIDATE_TEXT_RESUME_PROMPT = "Если отправляете текстом: вставьте резюме одним сообщением."
MSG_CANDIDATE_TEXT_RESUME_GUIDE = (
    "Текстовое резюме должно содержать минимум:\n"
    "1) Имя и фамилию\n"
    "2) Пол\n"
    "3) Возраст\n"
    "4) Опыт работы (в годах или по датам)\n"
    "5) Навыки\n\n"
    "Желательно добавить: email, телефон, локацию, формат работы, образование, языки."
)
MSG_CANDIDATE_RESULT_PREFIX = "Итог по совместимости кандидата:"
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
MSG_CANDIDATE_COLLECTED = "🧪 Данные получены! Запускаю проверку совместимости кандидата..."
MSG_CANDIDATE_FILE_ERROR = "❌ Не удалось прочитать файл резюме. Попробуйте другой файл."
MSG_CANDIDATE_EXPECT_FILE = "Пришлите файл резюме (docx/pdf/md) или текст резюме одним сообщением."
MSG_CANDIDATE_PARSE_EMPTY = "❌ Не смог разобрать резюме: не вижу ФИО, опыта или навыков. Пришлите более структурированный файл/текст."

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
MSG_ADMIN_USER_BALANCE_PROMPT = "Введите два числа: free paid (например: 5 20)."
MSG_ADMIN_USER_BALANCE_SET = "✅ Баланс пользователя {user_id} обновлен: Free={free}, Paid={paid}."
MSG_ADMIN_BROADCAST_ASK = "Введите текст уведомления для всех подписчиков:"
MSG_ADMIN_BROADCAST_DONE = "✅ Уведомление отправлено подписчикам: {count} чел."
MSG_ADMIN_COMPANY_PARAMS_PROMPT = "Текущие параметры компании:\n{text}\n\nВведите новый текст или «Отмена»."
MSG_ADMIN_COMPANY_PARAMS_SAVED = "✅ Параметры компании обновлены."
MSG_ADMIN_COMPANY_PARAMS_TEMPLATE = "Вот шаблон параметров компании (можно редактировать и отправить как новый текст):"
MSG_SUB_FUND_FAIL = "⚠️ Не удалось списать {price} у.е за гороскоп. Подписка остановлена."

# Параметры компании по умолчанию
DEFAULT_COMPANY_PARAMS_TEXT = (
    "Любим митинги на 9:59, юмор — максимум мемов, темп разработки — ракета.\n"
    "Опыт: 2 года. Формат: гибрид. Ритуалы: кофе в 11:11, стендап в 9:59.\n"
    "Отношение к дедлайнам: святы. Методология: scrum. Дресс-код: кэжуал.\n"
    "Толерантность к ананасам в холодильнике: высокая. Проактивность: всегда бодр.\n"
    "Космопрофиль: стихия огонь, число судьбы: 7, карта таро: Колесо Фортуны.\n"
    "Локации: Москва, Санкт-Петербург, remote."
)

# Сообщения о проклятиях
MSG_LUCK_RESET_RESULT = "🍀 Ваша полоса невезения выглядит так:\n\n{curse}\n\nПерезапустим удачу?"
MSG_LUCK_RESET_RITUAL = "✨ Ритуал перезапуска удачи:\n\n{ritual}\n\n🧲 Притягивайте хорошее — и возвращайтесь, если потребуется ещё заряд."
MSG_LUCK_RESET_SKIP = "🙂 Хорошо, оставляем всё как есть. Если захочется больше удачи — жмите «Перезапуск удачи»!"

# О компании
MSG_ABOUT_COMPANY = (
    "\U0001f52e <b>Telegram-\u0431\u043e\u0442 \u00ab\u0412\u0435\u043b\u0438\u043a\u0438\u0439 \u0428\u0430\u0440\u00bb</b>\n\n"
    "\U0001f3e2 <b>\u041d\u0418\u0418 \u041d\u041f\u041e \u00ab\u0428\u0430\u0440 \u041a\u043e\u043d\u0441\u0430\u043b\u0442 \u0418\u043d\u043a\u043e\u0440\u043f\u043e\u0440\u0435\u0439\u0442\u0435\u0434\u00bb</b>\n"
    "\u041c\u044b \u0437\u0430\u043d\u0438\u043c\u0430\u0435\u043c\u0441\u044f \u0441\u0430\u043c\u044b\u043c\u0438 \u0437\u0430\u0433\u0430\u0434\u043e\u0447\u043d\u044b\u043c\u0438 \u0438 \u043f\u0430\u0440\u0430\u043d\u043e\u0440\u043c\u0430\u043b\u044c\u043d\u044b\u043c\u0438 \u0443\u0441\u043b\u0443\u0433\u0430\u043c\u0438 \u0441 2025 \u0433\u043e\u0434\u0430.\n\n"
    "\U0001f4ab <b>\u041d\u0430\u0448 \u0434\u0435\u0432\u0438\u0437:</b> \"\u0412\u0430\u0448\u0435 \u0431\u0443\u0434\u0443\u0449\u0435\u0435 \u0432\u0441\u0435\u0433\u0434\u0430 \u043f\u043e\u0434 \u0440\u0443\u043a\u043e\u0439, \u043e\u0441\u043e\u0431\u0435\u043d\u043d\u043e \u0435\u0441\u043b\u0438 \u043e\u0442\u043a\u0440\u044b\u0442\u044c Telegram.\"\n\n"
    "\U0001f916 <b>\u041e \u0431\u043e\u0442\u0435</b>\n"
    "\u042f \u2014 \u043c\u0430\u0433\u0438\u0447\u0435\u0441\u043a\u0438\u0439 \u043f\u043e\u043c\u043e\u0449\u043d\u0438\u043a \u0434\u043b\u044f:\n"
    "\u2728 \u0413\u043e\u0440\u043e\u0441\u043a\u043e\u043f\u043e\u0432 \u043b\u044e\u0431\u043e\u0433\u043e \u0443\u0440\u043e\u0432\u043d\u044f \u043c\u0438\u0441\u0442\u0438\u043a\u0438\n"
    "\U0001f491 \u0421\u043e\u0432\u043c\u0435\u0441\u0442\u0438\u043c\u043e\u0441\u0442\u0438 \u043b\u044e\u0434\u0435\u0439 \u0438 \u0434\u0430\u0436\u0435 \u043b\u044e\u0431\u0438\u043c\u044b\u0445 \u043a\u0430\u043a\u0442\u0443\u0441\u043e\u0432\n"
    "\U0001f6e1\ufe0f \u0414\u0438\u0430\u0433\u043d\u043e\u0441\u0442\u0438\u043a\u0438 \u0438 \u0441\u043d\u044f\u0442\u0438\u044f \u043f\u043e\u0440\u0447\u0438\n"
    "\U0001f54a\ufe0f \u041e\u043f\u043b\u0430\u0442\u044b \u043c\u0430\u0433\u0438\u0435\u0439, \u0433\u043e\u043b\u0443\u0431\u044f\u043c\u0438, \u043f\u0430\u043b\u044c\u0446\u0435\u043c \u0438 \u0434\u043e\u0431\u0440\u044b\u043c \u0441\u043b\u043e\u0432\u043e\u043c\n\n"
    "\U0001f4dc \u0414\u0435\u043b\u044e \u0441\u043b\u0438\u0448\u043a\u043e\u043c \u0434\u043b\u0438\u043d\u043d\u044b\u0435 \u043f\u0440\u043e\u0440\u043e\u0447\u0435\u0441\u0442\u0432\u0430, \u0447\u0442\u043e\u0431\u044b \u043d\u0435 \u0443\u0442\u043e\u043c\u043b\u044f\u0442\u044c \u043a\u043e\u043b\u0434\u0443\u043d\u043e\u0432 \u0438 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0435\u0439.\n\n"
    "\U0001f3ad \u041c\u0430\u0433\u0438\u044f \u0438 \u0440\u0438\u0442\u0443\u0430\u043b\u044b \u0434\u043b\u044f \u0432\u0441\u0435\u0445, \u043a\u0442\u043e \u0432\u0435\u0440\u0438\u0442 \u0432 \u0447\u0443\u0434\u0435\u0441\u0430 \U0001f54a\ufe0f\n\n"
    "\U0001f4bb <b>\u0421\u0430\u0439\u0442 \u043a\u043e\u043c\u043f\u0430\u043d\u0438\u0438:</b> <a href=\"http://magic-ball.duckdns.org:8080/\">magic-ball.duckdns.org:8080</a> \u2014 \u0442\u0430\u043c \u043c\u043e\u0436\u043d\u043e \u043d\u0430\u0439\u0442\u0438 \u0434\u043e\u043f. \u0438\u043d\u0444\u0443.\n\n"
    "\U0001f52e <b>\u0412\u0430\u0448\u0435 \u0431\u0443\u0434\u0443\u0449\u0435\u0435 \u0437\u0430\u0432\u0438\u0441\u0438\u0442 \u0442\u043e\u043b\u044c\u043a\u043e \u043e\u0442 \u043e\u0434\u043d\u043e\u0439 \u043a\u043d\u043e\u043f\u043a\u0438 \u0438 \u043d\u0435\u043c\u043d\u043e\u0433\u043e \u2014 \u043e\u0442 \u0441\u0443\u0434\u044c\u0431\u044b.</b>\n\n"
    "\u2139\ufe0f \u042d\u0442\u043e \u0440\u0430\u0437\u0432\u043b\u0435\u043a\u0430\u0442\u0435\u043b\u044c\u043d\u044b\u0439 \u043a\u043e\u043d\u0442\u0435\u043d\u0442 \u2014 \u0440\u0435\u0448\u0435\u043d\u0438\u044f \u0437\u0430 \u0432\u0430\u043c\u0438.\n\n"
    "\u00a9 2025 \u041d\u0418\u0418 \u041d\u041f\u041e \u00ab\u0428\u0430\u0440 \u041a\u043e\u043d\u0441\u0430\u043b\u0442 \u0418\u043d\u043a\u043e\u0440\u043f\u043e\u0440\u0435\u0439\u0442\u0435\u0434\u00bb. \u0412\u0441\u0435 \u043c\u0430\u0433\u0438\u0447\u0435\u0441\u043a\u0438\u0435 \u043f\u0440\u0430\u0432\u0430 \u0437\u0430\u0449\u0438\u0449\u0435\u043d\u044b."
)
