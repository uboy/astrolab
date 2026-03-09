# Инструкция по запуску

## Требования
- **Python**: Версия 3.11 или выше.
- **Ollama**: Установленная и запущенная локально (или на доступном сервере).
- **Docker & Docker Compose**: (Опционально) для запуска в контейнерах.

## Локальный запуск (без Docker)

1.  **Клонирование репозитория**:
    ```bash
    git clone <url_репозитория>
    cd astrolab-bot
    ```

2.  **Настройка окружения**:
    ```bash
    python -m venv .venv
    # Windows:
    .venv\Scripts\activate
    # Linux/Mac:
    source .venv/bin/activate
    ```

3.  **Установка зависимостей**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Конфигурация**:
    Создайте файл `.env` на основе `.env.example` и заполните его:
    - `BOT_TOKEN`: Токен вашего бота от @BotFather.
    - `ADMINS`: Список ID администраторов через запятую.
    - `OLLAMA_URL`: URL API Ollama (обычно http://localhost:11434/api/generate).

5.  **Запуск**:
    ```bash
    python main.py
    ```

## Запуск через Docker

1.  **Сборка и запуск**:
    ```bash
    docker-compose up -d --build
    ```
    *Примечание: Если Ollama запущена на хост-машине (не в Docker), используйте `http://host.docker.internal:11434` в качестве URL.*

## Тестирование
Для запуска тестов используйте:
```bash
pytest
```
