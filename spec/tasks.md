# Tasks

1) Resolve the merge conflict in `utils/constants.py` for `MSG_ABOUT_COMPANY`.
- How to verify: `python -m py_compile utils/constants.py` completes without syntax errors, and the bot starts normally.

2) Fix missing asset reference in `utils/message_helpers.py` (either add `data/magic_ball.png` or remove the unused path).
- How to verify: trigger any Ollama-backed feature and confirm the progress animation works without asset-related errors.

3) Add tests for balance/rate limiting and pricing flows.
- How to verify: run `pytest` and ensure tests cover `utils/user_helpers.py:decrement_user_limit`, `utils/rate_limit.py:check_rate_limit`, and `utils/pricing_helpers.py:ensure_balance_and_charge`.

4) Add a lightweight persistence test to ensure JSON corruption is handled as expected.
- How to verify: a test writes invalid JSON to a temp file and confirms `utils/json_db.py:read_json` returns `{}` and rewrites the file.

5) Add a regression test for subscription scheduling logic with a fixed timezone.
- How to verify: test `utils/subscription_scheduler.py:_process_once` with controlled time and confirm it sends exactly once per day per user and charges balance.

---

# Feature Design: Проверка кандидата на совместимость с компанией

## 1) Как я понял задачу

Нужно добавить новую функцию бота: он принимает данные кандидата (часть обязательна, часть опциональна), умеет извлекать данные из резюме в форматах `docx`, `pdf`, `md`, сравнивает кандидата с параметрами компании и выдает текстовый результат: совместим/не совместим + краткое резюме кандидата. Параметры компании должны быть в шуточном стиле, храниться и редактироваться через админку в виде одного текста: бот показывает текущие параметры, ждет новый текст или команду отмены.

## 2) Требования и модель данных

### 2.1 Параметры кандидата

**Обязательные:**
- `first_name` — имя
- `last_name` — фамилия
- `gender` — пол (enum: `male|female|other|prefer_not_to_say`)
- `age` — возраст (int, >= 14)
- `experience_years` — общий стаж в годах (float, >= 0)

**Опциональные:**
- `middle_name` — отчество
- `phone` — телефон
- `email` — email
- `location` — город/страна
- `desired_role` — целевая роль/вакансия
- `skills` — список ключевых навыков
- `education_level` — уровень образования
- `last_employer` — последний работодатель
- `salary_expectation` — ожидания по зарплате
- `work_format` — удаленка/офис/гибрид
- `languages` — языки и уровень
- `portfolio_links` — ссылки
- `certifications` — сертификаты
- `hobbies` — хобби (для «культурной совместимости»)

### 2.2 Источник данных

1) Если прикреплен файл резюме (`docx|pdf|md`) — извлекаем текст и парсим.
2) Если файл не приложен — используем данные из формы/сообщения пользователя.
3) Если данные частично есть и в тексте, и в форме — приоритет у формы (явный ввод пользователя).

### 2.3 Параметры компании (шуточные)

Компания задает «культурные» и «процессные» параметры в виде одного текста. Пример набора параметров, которые бот пытается распознать:
- Любимые ритуалы: «стендап в 9:59», «кофе-ритуал на 11:11»
- Уровень любви к митингам: `0..10`
- Отношение к дедлайнам: «святы», «примерные», «фантики»
- Темп разработки: «ракета», «велосипед», «черепаха»
- Уровень юмора в чатах: `сухой|умеренный|максимум мемов`
- Предпочтения по формату работы: `удаленка|офис|гибрид|всё сразу`
- Толерантность к «холодильнику с ананасами»: `низкая|средняя|высокая`
- Дресс-код: `пижама|кэжуал|торжественный шлем`
- Любимая методология: `scrum|kanban|chaos`
- Уровень «проактивности»: `не буди дракона|можно проснуться|всегда бодр`

Формат хранения — **произвольный текст**. Бот делает парсинг «по максимуму», а если не нашел поле — использует дефолтные значения.

## 3) Поток работы

1) Пользователь инициирует команду «Проверка кандидата».
2) Бот запрашивает:
   - Имя, фамилия, пол, возраст, стаж (обязательные).
   - Опциональные параметры (можно пропустить).
   - Файл резюме (если есть).
3) Если приложен файл — извлекается текст, делается попытка автозаполнения опциональных полей.
4) Бот строит краткий профиль кандидата.
5) Бот сопоставляет профиль с параметрами компании.
6) Отдает ответ:
   - `Совместим / Не совместим` (с юмором)
   - краткое резюме кандидата (1–3 предложения)
   - краткое объяснение причин (2–4 буллета)

## 4) Парсинг резюме

### 4.1 Поддерживаемые форматы
- `docx` — чтение текста с сохранением порядка абзацев.
- `pdf` — извлечение текста с попыткой сохранить блоки.
- `md` — прямое чтение текста.

### 4.2 Извлекаемые поля
- Имя/Фамилия (первая строка, или заголовок)
- Email/Телефон (регекс)
- Опыт (число лет или даты в тексте)
- Навыки (по ключевым словам/маркированным спискам)
- Образование (по ключевым словам «университет», «бакалавр»)

### 4.3 Конфликты
- Если данные из резюме противоречат явному вводу — берем ввод пользователя и добавляем «заметку» в лог.

## 5) Логика совместимости (мягкая, шуточная)

1) Считаем «скор» по нескольким осям:
   - опыт vs минимальный опыт (если указан компанией)
   - совпадение навыков (процент пересечения)
   - соответствие формату работы
   - «культурный матч» (юмор, митинги, ритуалы)
2) Итог:
   - `>= 70` — совместим
   - `50..69` — «скорее совместим, но сомнения есть»
   - `< 50` — не совместим
3) Текст ответа содержит итог и 2–4 причины; формулировки — в шуточном стиле, но без оскорблений.

## 6) Админский сценарий изменения параметров компании

1) Админ вводит команду «Параметры компании».
2) Бот показывает текущий текст параметров.
3) Бот просит ввести новый текст или «отмена».
4) Если «отмена» — параметры не меняются.
5) Иначе бот сохраняет новый текст как есть.

## 7) Хранение данных

- `company_params_text` — один текстовый блок.
- `candidate_profile` — JSON-объект, хранится в контексте диалога (или временно в памяти).

## 8) Ответ бота (пример)

«Вердикт: совместим ✅ (мы уже греем кружку под кофе).
Кандидат: Анна Петрова, 27 лет, 4.5 года опыта, Python/SQL, любит удаленку.
Почему: опыт >= минимального, навыки совпали на 80%, готова к мемным чатам, не боится стендапов в 9:59.»

## 9) Возможные улучшения требований и дополнительные функции

- Настраиваемые пороги совместимости (например, «строгость» компании).
- Режим «что улучшить кандидату» (подсказки).
- Пояснение оценки по шкале (график/эмодзи).
- Сравнение нескольких кандидатов.
- Авто-заполнение из LinkedIn/HH (при наличии).
- История проверок кандидатов.
- Многоязычный режим вывода.
- Режим «анонимного кандидата» (без имени/фамилии).

---

# Architect Design: Проверка кандидата на совместимость с компанией

## Цели и границы

- Цель: дать шуточный, но объяснимый вердикт совместимости на основе данных кандидата и текстовых параметров компании.
- Вне рамок: хранение долгосрочной истории кандидатов, интеграции с внешними HR‑системами, ML‑скоринг.

## Компоненты

1) `candidate_input` — сбор обязательных и опциональных полей.
2) `resume_ingest` — загрузка файла, валидация форматов, извлечение текста.
3) `resume_parser` — извлечение полей и нормализация.
4) `company_params_provider` — чтение/запись текстовых параметров.
5) `compatibility_engine` — вычисление скора и причин.
6) `response_builder` — юмористический текст результата.

## Поток данных

1) Пользователь → `candidate_input` (форма/сообщения).
2) Пользователь → `resume_ingest` (файл).
3) `resume_ingest` → `resume_parser` → `candidate_profile`.
4) `candidate_input` + `candidate_profile` → `profile_merge`.
5) `company_params_provider` → `company_params_text` → `company_params_struct`.
6) `compatibility_engine` → `score`, `reasons`.
7) `response_builder` → ответ пользователю.

## Модель данных (ключевые структуры)

`candidate_profile`:
- `first_name*`, `last_name*`, `gender*`, `age*`, `experience_years*`
- `skills[]`, `education_level`, `work_format`, `languages[]`, `hobbies[]`, `email`, `phone`, `location`

`company_params_struct` (извлечено из текста, дефолты допустимы):
- `min_experience_years`
- `preferred_work_format`
- `humor_level`
- `meeting_love_level`
- `rituals[]`
- `deadline_attitude`
- `dev_speed`

## Правила слияния данных

- Явный ввод пользователя приоритетнее извлеченного из резюме.
- Конфликты фиксируются в логе (без PII в логах).
- Если обязательные поля отсутствуют — бот запрашивает их.

## Алгоритм совместимости

- Базовый скор 0..100 из 4 осей:
  - опыт (0–30)
  - навыки (0–30)
  - формат работы (0–20)
  - культурный матч (0–20)
- Пороги:
  - `>= 70` — совместим
  - `50..69` — скорее совместим
  - `< 50` — не совместим

## Юмористический стиль ответа

- Тон: дружелюбный, без оскорблений.
- Содержит: вердикт, короткий профиль, 2–4 причины.
- Примеры фраз держать в шаблонах, чтобы контролировать стиль.

## Админ‑редактор параметров

- Команда «Параметры компании».
- Бот показывает текущий текст.
- Ввод нового текста или «отмена».
- Валидация: пустой текст — просим повторить.

## Хранение и безопасность

- `company_params_text` хранится как строка.
- `candidate_profile` хранится временно (контекст диалога).
- Логи без персональных данных.
- Ограничения размера файла, проверка расширения и MIME.

## Ошибки и деградация

- Невалидный файл → дружественная ошибка + предложение загрузить другой файл.
- Нераспознанные поля → fallback на дефолты и запрос недостающего.
- Низкий скор → объяснение без «жестких» формулировок.

---

# Codebase Mapping (куда ложится реализация)

## Новые/изменяемые файлы

- `handlers/candidate_compatibility.py` — новый роутер и FSM для фичи.
- `main.py` — подключить новый роутер.
- `utils/constants.py` — кнопки/сообщения/дефолты для фичи и админки.
- `keyboards/menus.py` — кнопка фичи в главном меню, цена в `menu_for`.
- `utils/prices.py` + `data/prices.json` — добавить цену `candidate_compatibility`.
- `utils/company_params.py` — чтение/запись параметров компании (текст).
- `data/company_params.json` (или `.txt`) — хранение текста параметров.
- `utils/resume_ingest.py` — валидация файла, извлечение текста.
- `utils/resume_parser.py` — парсинг текста резюме в partial‑профиль.
- `utils/candidate_compatibility.py` — скоринг + генерация юмористического ответа.
- `utils/message_helpers.py` — при необходимости прогресс‑индикация для тяжелого парсинга.
- `handlers/admin.py` — пункт «Параметры компании», сценарий редактирования.
- `requirements.txt` — библиотеки для `docx|pdf` (например `python-docx`, `pdfplumber`).

## Реюз текущих модулей

- `utils/user_helpers.py` — лимиты/профиль.
- `utils/rate_limit.py` — анти‑спам.
- `utils/pricing_helpers.py` — списание и проверка баланса.
- `utils/json_db.py` — хранение параметров компании.

---

# API/Handler Signatures (черновик)

## FSM и команды

```python
# handlers/candidate_compatibility.py
router = Router()

class CandidateCompatibilityStates(StatesGroup):
    waiting_required = State()
    waiting_optional = State()
    waiting_resume = State()
    waiting_result = State()

@router.message(F.text.func(lambda t: t and t.startswith(BTN_CANDIDATE_COMPATIBILITY)), StateFilter(None))
async def start_candidate_compatibility(message: Message, state: FSMContext):
    ...

@router.message(CandidateCompatibilityStates.waiting_required)
async def collect_required_fields(message: Message, state: FSMContext):
    ...

@router.message(CandidateCompatibilityStates.waiting_optional)
async def collect_optional_fields(message: Message, state: FSMContext):
    ...

@router.message(CandidateCompatibilityStates.waiting_resume)
async def collect_resume_file(message: Message, state: FSMContext, bot: Bot):
    ...

async def run_candidate_compatibility(message: Message, state: FSMContext):
    ...
```

## Админ‑сценарий

```python
# handlers/admin.py
class AdminStates(StatesGroup):
    ...
    waiting_company_params = State()

@router.message(AdminStates.home)
async def admin_home(message: Message, state: FSMContext):
    # новый пункт "Параметры компании"
    ...

@router.message(AdminStates.waiting_company_params)
async def admin_set_company_params(message: Message, state: FSMContext):
    ...
```

## Сервисы/утилиты

```python
# utils/company_params.py
async def get_company_params_text() -> str: ...
async def set_company_params_text(text: str) -> None: ...
def parse_company_params(text: str) -> dict: ...

# utils/resume_ingest.py
async def extract_resume_text(file_bytes: bytes, filename: str, content_type: str) -> str: ...
def validate_resume_file(filename: str, content_type: str, size_bytes: int) -> None: ...

# utils/resume_parser.py
def parse_resume_text(text: str) -> dict: ...

# utils/candidate_compatibility.py
def merge_candidate_profile(user_input: dict, resume_data: dict) -> dict: ...
def score_compatibility(profile: dict, company_params: dict) -> tuple[int, list[str]]: ...
def build_humorous_response(profile: dict, score: int, reasons: list[str]) -> str: ...
```

---

# Payload Schemas (черновик)

## candidate_profile

```json
{
  "first_name": "string",
  "last_name": "string",
  "gender": "male|female|other|prefer_not_to_say",
  "age": 27,
  "experience_years": 4.5,
  "skills": ["Python", "SQL"],
  "education_level": "bachelor|master|phd|other",
  "work_format": "remote|office|hybrid|any",
  "languages": ["ru-B2", "en-B1"],
  "hobbies": ["настолки", "котики"],
  "email": "user@example.com",
  "phone": "+79990001122",
  "location": "Moscow, RU"
}
```

## company_params_text (raw)

```json
{
  "text": "Любим митинги на 9:59, темп разработки — ракета, юмор — мемы, формат — гибрид..."
}
```

## company_params_struct (parsed)

```json
{
  "min_experience_years": 2,
  "preferred_work_format": "hybrid",
  "humor_level": "max_memes",
  "meeting_love_level": 8,
  "rituals": ["standup_09_59", "coffee_11_11"],
  "deadline_attitude": "sacred",
  "dev_speed": "rocket"
}
```

## compatibility_result

```json
{
  "score": 78,
  "verdict": "compatible",
  "reasons": [
    "Опыт закрывает минимальный порог",
    "Навыки совпали на 75%",
    "Формат работы совпадает",
    "Юмор — мемы на уровне компании"
  ],
  "summary": "Анна Петрова, 27 лет, 4.5 года опыта, Python/SQL, любит удаленку."
}
```

---

# Team Lead: Разбивка и хенд‑офф разработчику

## Handoff → Agent Developer

**Цель:** реализовать новую фичу «Проверка кандидата на совместимость с компанией» согласно архитектурному дизайну.

### Задачи
1) Создать `handlers/candidate_compatibility.py` с FSM и бизнес‑флоу.
2) Добавить кнопки/сообщения в `utils/constants.py`.
3) Добавить пункт в главное меню `keyboards/menus.py`.
4) Подключить роутер в `main.py`.
5) Реализовать `utils/company_params.py` + хранение в `data/company_params.json`.
6) Реализовать `utils/resume_ingest.py` и `utils/resume_parser.py`.
7) Реализовать `utils/candidate_compatibility.py` (скоринг + юмор).
8) Добавить админ‑сценарий редактирования параметров в `handlers/admin.py`.
9) Обновить `requirements.txt` для парсеров `docx|pdf`.
10) Добавить тесты на парсинг, скоринг, админ‑сценарий.

### Критерии приемки
- Обязательные поля кандидата валидируются, недостающие запрашиваются.
- При наличии резюме данные подтягиваются и корректно мержатся.
- Выдается шуточный вердикт + краткая сводка + причины.
- Админ может просмотреть и заменить текст параметров компании, либо отменить.
- Ошибки файлов обрабатываются дружественно.

### Оценка (dev)
- Реализация флоу и FSM — 6ч
- Парсинг резюме + маппинг — 8ч
- Скоринг + юмористические тексты — 3ч
- Админ‑сценарий — 2ч
- Тесты + регрессия — 6ч
Итого: ~25ч

---

# PR‑Sized Chunks (Developer Handoff)

## PR1: Каркас фичи и UI‑точки входа
- Создать `handlers/candidate_compatibility.py` со скелетом FSM (без логики).
- Добавить кнопки/тексты в `utils/constants.py`.
- Добавить кнопку в `keyboards/menus.py`.
- Подключить роутер в `main.py`.
- Добавить цену `candidate_compatibility` в `utils/prices.py` (DEFAULT).

## PR2: Хранение и админ‑редактор параметров компании
- Добавить `utils/company_params.py`.
- Добавить хранение `data/company_params.json` (первичная инициализация).
- Обновить `handlers/admin.py` с новым пунктом меню и FSM для редактирования.

## PR3: Resume ingest + parser (без скоринга)
- Добавить `utils/resume_ingest.py` (валидация, извлечение текста).
- Добавить `utils/resume_parser.py` (извлечение полей).
- Обновить `requirements.txt` под `docx|pdf`.

## PR4: Скоринг + юмористический ответ
- Добавить `utils/candidate_compatibility.py`.
- Реализовать `merge_candidate_profile`, `score_compatibility`, `build_humorous_response`.

## PR5: Интеграция флоу + тесты
- В `handlers/candidate_compatibility.py` связать все этапы.
- Добавить тесты парсинга/скоринга/админ‑сценария.
- Мелкие полировки (ошибки, UX, тексты).

### Suggested order
PR1 → PR2 → PR3 → PR4 → PR5

---

# Test Plan: Resume Parsing

## Цели
- Убедиться, что извлечение текста корректно работает для `docx|pdf|md`.
- Проверить, что парсер извлекает ключевые поля и мержит данные по правилам.
- Проверить устойчивость к битым/пустым файлам.

## Покрытие

### Unit tests (`utils/resume_ingest.py`)
- `validate_resume_file`:
  - принимает `docx|pdf|md`, отклоняет остальные.
  - отклоняет файл выше лимита (например 5–10MB).
- `extract_resume_text`:
  - возвращает непустой текст для корректных файлов.
  - возвращает `""` или бросает контролируемую ошибку на битом файле.

### Unit tests (`utils/resume_parser.py`)
- `parse_resume_text`:
  - корректно находит имя/фамилию (первой строкой).
  - находит email и телефон по регексу.
  - извлекает опыт (число лет или диапазон дат).
  - извлекает навыки из маркированных списков.

### Integration tests (handler)
- загрузка `docx|pdf|md` + частичный ввод → приоритет у явного ввода.
- отсутствие файла → только ручной ввод.
- конфликт данных → приоритет ручного ввода, лог‑заметка (mock).

## Fixtures (пример структуры)

```
tests/fixtures/resumes/
├─ resume_basic.md
├─ resume_basic.docx
├─ resume_basic.pdf
├─ resume_missing_fields.md
├─ resume_conflict.md
├─ resume_multilang.md
├─ resume_bad.pdf
└─ resume_empty.md
```

### Fixture content (черновики)

`resume_basic.md`
```
Иван Петров
Email: ivan.petrov@example.com
Телефон: +7 999 111-22-33
Опыт: 4.5 года
Навыки: Python, SQL, Docker
Формат работы: удаленка
```

`resume_missing_fields.md`
```
Анна Смирнова
Навыки: React, TypeScript
```

`resume_conflict.md`
```
Петр Иванов
Email: old@example.com
Опыт: 2 года
Навыки: Java
```

`resume_multilang.md`
```
Maria Johnson
Email: maria@example.com
Experience: 5 years
Skills: Python, ML, AWS
```

`resume_empty.md`
```
(пусто)
```

## Пример ожидаемых результатов (парсер)

- `resume_basic.*` → name=Иван, last_name=Петров, email, phone, experience_years≈4.5, skills=[Python, SQL, Docker], work_format=remote
- `resume_missing_fields.*` → name=Анна, last_name=Смирнова, skills=[React, TypeScript], остальное пустое
- `resume_conflict.*` + ручной ввод `email=new@example.com`, `experience_years=5` → итог email=new..., experience=5


# Проектные агенты для выполнения флоу задач

## Роли и ответственность

### Архитектор
- Формирует целевую архитектуру, выбирает подходы к хранению и обработке данных.
- Определяет интерфейсы между модулями (парсер резюме, оценка совместимости, админ-редактор параметров).
- Определяет нефункциональные требования (безопасность, масштабируемость, логирование).

### Тим лид
- Декомпозирует работу в задачи и план спринта.
- Следит за код-стайлом и качеством PR.
- Координирует интеграцию и риски.

### Разработчик
- Реализует обработчики, парсинг файлов, бизнес-логику совместимости.
- Добавляет сообщения и тексты ответа в шуточном стиле.
- Пишет unit/integration тесты на парсинг и оценку.

### QA
- Проверяет happy-path и edge-cases (битые файлы, пустые поля, конфликтные данные).
- Автоматизирует тесты загрузки `docx|pdf|md`.
- Проверяет регрессии по текущим функциям.

### Legal expert
- Проверяет соблюдение лицензий библиотек (особенно pdf/docx парсеров).
- Оценивает риск утечки персональных данных и соответствие локальным законам.
- Проверяет формулировки ответа на предмет дискриминации/предвзятости.
- Даёт рекомендации по хранению/удалению резюме и срокам ретенции.

## Пример флоу

1) Архитектор: утверждает дизайн и точки интеграции.
2) Тим лид: ставит задачи и критерии готовности.
3) Разработчик: реализует функциональность + тесты.
4) QA: проверяет и валидирует сценарии.
5) Legal expert: проводит правовую проверку до релиза.

---

# Acceptance Criteria по ролям

## Архитектор
- Есть целевая схема модулей и потока данных (резюме -> парсер -> профиль -> совместимость -> ответ).
- Определены интерфейсы модулей и формат `candidate_profile`.
- Описаны риски и нефункциональные требования (безопасность, логирование, хранение).
- Указаны точки расширения (новые форматы резюме, новые параметры компании).

## Тим лид
- Есть декомпозиция задач с оценкой и владельцами.
- Зафиксированы критерии готовности (DoD) на фичу.
- Определены ветка, правила PR и порядок ревью.
- Есть план тестирования и время на регрессию.

## Разработчик
- Реализованы обработчики кандидата и админ-редактор параметров.
- Реализован парсинг `docx|pdf|md` и маппинг в `candidate_profile`.
- Реализована логика совместимости и шуточные тексты ответа.
- Покрыты тестами критические пути (парсинг, совместимость, админ-изменения).

## QA
- Пройдены happy-path сценарии с ручным вводом и с файлами.
- Пройдены edge-cases: пустые поля, некорректные файлы, конфликт данных.
- Есть автотесты загрузки разных форматов.
- Оформлен отчет по регрессии.

## Legal expert
- Проверены лицензии всех библиотек для парсинга `docx|pdf`.
- Оценены риски работы с персональными данными и даны рекомендации.
- Проверены формулировки на отсутствие дискриминации и токсичности.
- Подготовлены требования по ретенции/удалению резюме.

---

# Execution Checklist

## Архитектор
- Дизайн-док утвержден
- Интерфейсы модулей согласованы
- Риски и NFR описаны
- План интеграции с текущими модулями есть

## Тим лид
- Бэклог и приоритеты согласованы
- DoD утвержден
- План релиза и регрессии согласован
- Схема ревью и тестов утверждена

## Разработчик
- Парсер резюме работает для `docx|pdf|md`
- `candidate_profile` формируется корректно
- Логика совместимости стабильна
- Юмористический ответ не содержит оскорблений
- Тесты на критические пути есть

## QA
- Пройдены ручные сценарии
- Пройдены негативные сценарии
- Автотесты на форматы резюме есть
- Регрессия пройдена

## Legal expert
- Лицензии проверены
- Риски по персональным данным оценены
- Рекомендации по хранению/удалению есть
- Формулировки ответов проверены
