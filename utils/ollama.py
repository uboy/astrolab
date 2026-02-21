import httpx
import json
from utils.config import settings
import re
from utils.logging_config import get_logger


logger = get_logger(__name__)
MAX_TELEGRAM_LENGTH = 4000

async def ask_ollama(prompt: str, apply_formatting: bool = True) -> str:
    """
    Отправить текстовый запрос к Ollama
    
    Args:
        prompt: Текстовый промпт
        apply_formatting: Применять ли HTML форматирование (по умолчанию True)
        
    Returns:
        Ответ от Ollama
    """
    url = f"{settings.OLLAMA_URL}"
    model = settings.OLLAMA_MODEL
    payload = {"model": model, "prompt": prompt}
    logger.debug(f"Отправка запроса к Ollama. Длина промпта: {len(prompt)}")

    try:
        async with httpx.AsyncClient(timeout=45) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            txt = resp.text or ""
            txt = txt.strip()

            # Streaming-style JSON lines
            out = ""
            for line in txt.splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    if isinstance(obj, dict):
                        out += obj.get("response") or obj.get("text") or obj.get("content") or obj.get("message") or ""
                    else:
                        out += str(obj)
                except Exception:
                    out += line

            if not out:
                out = txt or "Бот не смог сгенерировать ответ. Попробуйте ещё раз."

            # Применяем форматирование перед ограничением длины
            if apply_formatting:
                out = format_for_telegram(out)

            # Ограничение длины для Telegram
            if len(out) > MAX_TELEGRAM_LENGTH:
                out = out[:MAX_TELEGRAM_LENGTH-3] + "..."

            return out

    except Exception as e:
        logger.error(f"Ошибка при запросе к Ollama: {e}", exc_info=True)
        return f"✨ Ошибка при запросе к Ollama: {e}"


async def ask_ollama_with_image(prompt: str, image_base64: str, apply_formatting: bool = True) -> str:
    """
    Отправить запрос к Ollama с изображением
    
    Args:
        prompt: Текстовый промпт
        image_base64: Изображение в формате base64
        apply_formatting: Применять ли HTML форматирование (по умолчанию True)
        
    Returns:
        Ответ от Ollama
    """
    # Определяем URL - для vision models используем /api/chat
    base_url = settings.OLLAMA_URL
    if "/api/generate" in base_url:
        url = base_url.replace("/api/generate", "/api/chat")
    elif "/api/chat" in base_url:
        url = base_url
    else:
        # Если URL не содержит endpoint, добавляем /api/chat
        url = base_url.rstrip("/") + "/api/chat"
    
    model = "qwen3-vl:32b" #settings.OLLAMA_MODEL
    
    # Формируем сообщения для vision model (формат /api/chat)
    messages = [
        {
            "role": "user",
            "content": prompt,
            "images": [image_base64]
        }
    ]
    
    payload = {
        "model": model,
        "messages": messages,
        "stream": False
    }

    try:
        async with httpx.AsyncClient(timeout=90) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            result = resp.json()
            
            # Извлекаем ответ из JSON
            if isinstance(result, dict):
                message = result.get("message", {})
                if isinstance(message, dict):
                    content = message.get("content", "")
                else:
                    content = str(message)
                
                if not content:
                    # Пробуем другие варианты
                    content = result.get("response") or result.get("text") or result.get("content") or ""
                
                if not content:
                    return "Бот не смог проанализировать изображение. Попробуйте ещё раз."
                
                # Применяем форматирование перед ограничением длины
                if apply_formatting:
                    content = format_for_telegram(content)
                
                # Ограничение длины для Telegram
                if len(content) > MAX_TELEGRAM_LENGTH:
                    content = content[:MAX_TELEGRAM_LENGTH-3] + "..."
                
                return content
            else:
                return "Бот не смог проанализировать изображение. Попробуйте ещё раз."

    except Exception as e:
        return f"✨ Ошибка при запросе к Ollama с изображением: {e}"


def format_for_telegram(text: str) -> str:
    """
    Универсальная функция для конвертации различных форматов в HTML для Telegram.
    Поддерживает: Markdown, CommonMark.
    Если текст уже содержит HTML-теги, они останутся без изменений.

    Конвертирует:
    - ### Заголовок → 🔮 Заголовок (жирный)
    - ## Заголовок → ✨ Заголовок (жирный)
    - # Заголовок → 🌟 Заголовок (жирный)
    - **текст** → жирный
    - *текст* → курсив
    - `код` → моноширинный
    - ~~текст~~ → зачеркнутый
    - [ссылка](url) → кликабельная ссылка

    Args:
        text: Текст с форматированием (Markdown, HTML или обычный)

    Returns:
        Отформатированный текст в HTML для Telegram
    """
    if not text:
        return text

    # Шаг 1: Конвертируем заголовки Markdown в жирный текст с магическими эмодзи
    text = re.sub(r'^### (.+)$', r'🔮 <b>\1</b>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'✨ <b>\1</b>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.+)$', r'🌟 <b>\1</b>', text, flags=re.MULTILINE)

    # Шаг 2: Конвертируем жирный текст (сначала двойные символы)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'__(.+?)__', r'<b>\1</b>', text)

    # Шаг 3: Конвертируем курсив (одинарные символы)
    text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
    text = re.sub(r'_(.+?)_', r'<i>\1</i>', text)

    # Шаг 4: Конвертируем код
    text = re.sub(r'`([^`]+?)`', r'<code>\1</code>', text)

    # Шаг 5: Конвертируем зачеркнутый текст
    text = re.sub(r'~~(.+?)~~', r'<s>\1</s>', text)

    # Шаг 6: Конвертируем ссылки
    text = re.sub(r'\[([^\]]+?)\]\(([^\)]+?)\)', r'<a href="\2">\1</a>', text)

    # Шаг 7: Экранируем опасные символы, НО не трогаем HTML-теги
    # Заменяем & на &amp; только если это не часть HTML-entity
    text = re.sub(r'&(?![a-zA-Z]+;|#[0-9]+;)', r'&amp;', text)

    # Разрешённые HTML-теги для Telegram
    allowed_tags = r'</?(?:b|i|u|s|code|pre|a(?:\s+href="[^"]*")?|strong|em|strike|del)>'

    # Временно заменяем разрешённые теги на плейсхолдеры
    placeholders = {}
    counter = 0
    for match in re.finditer(allowed_tags, text):
        placeholder = f"___HTML_TAG_{counter}___"
        placeholders[placeholder] = match.group(0)
        text = text.replace(match.group(0), placeholder, 1)
        counter += 1

    # Экранируем оставшиеся < и >
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')

    # Восстанавливаем HTML-теги
    for placeholder, tag in placeholders.items():
        text = text.replace(placeholder, tag)

    return text