import httpx
import json
from typing import Optional, List, Union
from pathlib import Path
import base64
from utils.config import settings
import re
from utils.logging_config import get_logger

logger = get_logger(__name__)
MAX_TELEGRAM_LENGTH = 4000


async def ask_ollama(
        prompt: str,
        images: Optional[List[str]] = None,
        files: Optional[List[Union[str, Path]]] = None,
        model: Optional[str] = None,
        apply_formatting: bool = True,
        stream: bool = False,
        timeout: Optional[int] = None
) -> str:
    """
    Универсальная функция для отправки запросов к Ollama.
    Поддерживает текст, изображения и файлы.

    Args:
        prompt: Текстовый промпт
        images: Список изображений в формате base64 (опционально)
        files: Список путей к файлам для загрузки (опционально)
        model: Модель Ollama (если None, используется из настроек)
        apply_formatting: Применять ли HTML форматирование (по умолчанию True)
        stream: Использовать ли потоковую передачу (по умолчанию False)
        timeout: Таймаут в секундах (если None, используется автоматически)

    Returns:
        Ответ от Ollama

    Examples:
        # Простой текстовый запрос
        response = await ask_ollama("Привет!")

        # Запрос с изображением
        response = await ask_ollama("Что на картинке?", images=[base64_image])

        # Запрос с файлом
        response = await ask_ollama("Проанализируй документ", files=["document.pdf"])

        # Запрос с несколькими изображениями и файлами
        response = await ask_ollama(
            "Сравни эти изображения и документы",
            images=[img1_base64, img2_base64],
            files=["doc1.pdf", "doc2.txt"]
        )
    """
    # Определяем модель
    if model is None:
        # Если есть изображения или файлы, используем vision модель
        if (images and len(images) > 0) or (files and len(files) > 0):
            model = "qwen3-vl:32b"
        else:
            model = settings.OLLAMA_MODEL

    # Определяем endpoint и формат запроса
    has_multimodal = bool((images and len(images) > 0) or (files and len(files) > 0))

    if has_multimodal:
        # Для multimodal используем /api/chat
        url = _get_chat_url(settings.OLLAMA_URL)
        payload = await _build_chat_payload(prompt, images, files, model, stream)
        # Увеличенный таймаут для vision моделей (могут работать медленно)
        default_timeout = 300 if timeout is None else timeout
    else:
        # Для обычного текста используем /api/generate
        url = settings.OLLAMA_URL
        payload = {"model": model, "prompt": prompt, "stream": stream}
        default_timeout = 420 if timeout is None else timeout

    logger.debug(f"Отправка запроса к Ollama. URL: {url}, Модель: {model}, Промпт: {len(prompt)} символов, "
                 f"Изображений: {len(images) if images else 0}, Файлов: {len(files) if files else 0}, "
                 f"Таймаут: {default_timeout}с")

    try:
        async with httpx.AsyncClient(timeout=default_timeout) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()

            # Парсим ответ
            if has_multimodal:
                content = _parse_chat_response(resp.json())
            else:
                content = _parse_generate_response(resp.text)

            if not content:
                content = "Бот не смог сгенерировать ответ. Попробуйте ещё раз."

            # Применяем форматирование
            if apply_formatting:
                content = format_for_telegram(content)

            # Ограничение длины для Telegram
            if len(content) > MAX_TELEGRAM_LENGTH:
                content = content[:MAX_TELEGRAM_LENGTH - 3] + "..."

            return content

    except httpx.HTTPStatusError as e:
        error_detail = ""
        try:
            error_json = e.response.json()
            error_detail = f" - {error_json.get('error', error_json)}"
        except:
            error_detail = f" - {e.response.text[:200]}"

        logger.error(f"HTTP ошибка при запросе ко Вселенной: {e.response.status_code}{error_detail}", exc_info=True)
        return "✨ Вселенная недоступна. Попробуйте позже."
    except httpx.TimeoutException:
        logger.error("Таймаут при запросе ко Вселенной", exc_info=True)
        return "✨ Вселенная задумалась. Попробуйте ещё раз позже."
    except Exception as e:
        logger.error(f"Ошибка при запросе ко Вселенной: {e}", exc_info=True)
        return "✨ Вселенная недоступна. Попробуйте позже."


def _get_chat_url(base_url: str) -> str:
    """Получить URL для /api/chat endpoint"""
    if "/api/chat" in base_url:
        return base_url
    elif "/api/generate" in base_url:
        return base_url.replace("/api/generate", "/api/chat")
    else:
        return base_url.rstrip("/") + "/api/chat"


async def _build_chat_payload(
        prompt: str,
        images: Optional[List[str]],
        files: Optional[List[Union[str, Path]]],
        model: str,
        stream: bool
) -> dict:
    """Построить payload для /api/chat endpoint"""
    # Собираем все изображения (из параметра и из файлов)
    all_images: List[str] = []

    if images:
        # Проверяем, не передали ли одну строку вместо списка
        # Если в списке слишком много элементов по 1 символу - это ошибка
        if len(images) > 100 and all(len(img) == 1 for img in images[:100]):
            logger.error("Обнаружена ошибка: передана строка base64 вместо списка строк!")
            logger.error("Используйте: images=[base64_str] вместо images=base64_str")
            # Собираем строку обратно
            combined = ''.join(images)
            logger.info(f"Попытка восстановить строку, длина: {len(combined)}")
            images = [combined]

        # Очищаем base64 от возможных префиксов
        for idx, img in enumerate(images):
            logger.debug(f"Обработка изображения {idx + 1}: длина={len(img) if img else 0}")
            cleaned_img = _clean_base64(img)
            if cleaned_img:
                all_images.append(cleaned_img)
                logger.info(f"✓ Изображение {idx + 1} успешно обработано")
            else:
                logger.warning(f"✗ Изображение {idx + 1} не прошло валидацию base64")

    # Загружаем файлы и конвертируем изображения в base64
    if files:
        for file_path in files:
            file_content = await _load_file_as_base64(file_path)
            if file_content:
                all_images.append(file_content)

    # Формируем сообщение
    message: dict = {
        "role": "user",
        "content": prompt
    }

    # Добавляем изображения только если они есть
    if all_images and len(all_images) > 0:
        message["images"] = all_images

    payload = {
        "model": model,
        "messages": [message],
        "stream": stream
    }

    logger.debug(f"Построен chat payload: model={model}, images_count={len(all_images)}, stream={stream}")

    return payload


def _clean_base64(data: str) -> str:
    """
    Очистить base64 строку от возможных префиксов и лишних символов.
    Автоматически добавляет padding если необходимо.
    """
    if not data:
        logger.warning("Получена пустая строка base64")
        return ""

    # Убираем пробелы и переносы строк
    data = data.strip().replace('\n', '').replace('\r', '').replace(' ', '')

    # Проверяем минимальную длину (изображение в base64 должно быть длинным)
    if len(data) < 100:
        logger.warning(f"Слишком короткая строка для base64 изображения: {len(data)} символов")
        return ""

    # Проверяем наличие data URI префикса
    if data.startswith('data:'):
        # Ищем base64 после запятой
        if ',' in data:
            data = data.split(',', 1)[1]

    # Добавляем padding если необходимо
    # Base64 строка должна быть кратна 4
    missing_padding = len(data) % 4
    if missing_padding:
        data += '=' * (4 - missing_padding)

    # Проверяем корректность base64
    try:
        # Пробуем декодировать для проверки
        decoded = base64.b64decode(data, validate=True)
        logger.debug(f"Base64 успешно декодирован, размер: {len(decoded)} байт")
        return data
    except Exception as e:
        logger.error(f"Некорректный base64 формат: {str(e)[:100]}")
        return ""


async def _load_file_as_base64(file_path: Union[str, Path]) -> Optional[str]:
    """
    Загрузить файл и конвертировать в base64.
    Поддерживает изображения и документы.
    """
    try:
        path = Path(file_path)
        if not path.exists():
            logger.error(f"Файл не найден: {file_path}")
            return None

        with open(path, "rb") as f:
            content = f.read()

        # Конвертируем в base64
        base64_content = base64.b64encode(content).decode('utf-8')
        logger.debug(f"Файл {path.name} загружен ({len(base64_content)} символов)")
        return base64_content

    except Exception as e:
        logger.error(f"Ошибка при загрузке файла {file_path}: {e}", exc_info=True)
        return None


def _parse_chat_response(response: dict) -> str:
    """Парсинг ответа от /api/chat endpoint"""
    if not isinstance(response, dict):
        return ""

    # Извлекаем контент из message
    message = response.get("message", {})
    if isinstance(message, dict):
        content = message.get("content", "")
    else:
        content = str(message)

    # Пробуем альтернативные поля
    if not content:
        content = (
                response.get("response") or
                response.get("text") or
                response.get("content") or
                ""
        )

    return content


def _parse_generate_response(text: str) -> str:
    """Парсинг ответа от /api/generate endpoint (streaming JSON lines)"""
    if not text:
        return ""

    text = text.strip()
    output = ""

    # Обрабатываем streaming JSON lines
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        try:
            obj = json.loads(line)
            if isinstance(obj, dict):
                output += (
                        obj.get("response") or
                        obj.get("text") or
                        obj.get("content") or
                        obj.get("message") or
                        ""
                )
            else:
                output += str(obj)
        except json.JSONDecodeError:
            # Если не JSON, добавляем как есть
            output += line

    return output or text


def format_for_telegram(text: str) -> str:
    """
    Универсальная функция для конвертации различных форматов в HTML для Telegram.
    Поддерживает: Markdown, CommonMark.
    """
    if not text:
        return text

    # Шаг 1: Конвертируем заголовки Markdown
    text = re.sub(r'^### (.+)$', r'🔮 <b>\1</b>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'✨ <b>\1</b>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.+)$', r'🌟 <b>\1</b>', text, flags=re.MULTILINE)

    # Шаг 2: Конвертируем жирный текст (сначала двойные символы)
    text = re.sub(r'\*\*([^*]+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'__([^_]+?)__', r'<b>\1</b>', text)

    # Шаг 3: Конвертируем курсив (одинарные символы)
    # Используем negative lookahead/lookbehind чтобы избежать конфликтов
    text = re.sub(r'(?<![*_])\*([^*\n]+?)\*(?![*_])', r'<i>\1</i>', text)
    text = re.sub(r'(?<![*_])_([^_\n]+?)_(?![*_])', r'<i>\1</i>', text)

    # Шаг 4: Конвертируем код
    text = re.sub(r'`([^`]+?)`', r'<code>\1</code>', text)

    # Шаг 5: Конвертируем зачеркнутый текст
    text = re.sub(r'~~([^~]+?)~~', r'<s>\1</s>', text)

    # Шаг 6: Конвертируем ссылки
    text = re.sub(r'\[([^]]+?)]\(([^)]+?)\)', r'<a href="\2">\1</a>', text)

    # Шаг 8: Валидация парности тегов
    text = _validate_and_fix_tags(text)

    # Шаг 7: Экранируем опасные символы
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

    # Шаг 8: Валидация парности тегов
    #text = _validate_and_fix_tags(text)

    return text


# def _validate_and_fix_tags(text: str) -> str:
#     """
#     Проверяет и исправляет незакрытые HTML теги.
#     """
#     tags_to_check = ['b', 'i', 'u', 's', 'code', 'pre', 'a', 'strong', 'em', 'strike', 'del']
#
#     for tag in tags_to_check:
#         # Подсчитываем открывающие и закрывающие теги
#         open_pattern = f'<{tag}(?:\\s[^>]*)?>'
#         close_pattern = f'</{tag}>'
#
#         open_count = len(re.findall(open_pattern, text))
#         close_count = len(re.findall(close_pattern, text))
#
#         # Если несоответствие - удаляем все такие теги для безопасности
#         if open_count != close_count:
#             logger.warning(f"Обнаружены незакрытые теги <{tag}>: открыто={open_count}, закрыто={close_count}")
#             # Удаляем все теги этого типа
#             text = re.sub(open_pattern, '', text)
#             text = re.sub(close_pattern, '', text)
#             logger.info(f"Удалены все теги <{tag}> для безопасности")
#
#     return text


def _validate_and_fix_tags(text: str) -> str:
    # Убрали 'pre' и 'a' из общего списка
    tags_to_check = ['b', 'i', 'u', 's', 'code', 'strong', 'em', 'strike', 'del']

    for tag in tags_to_check:
        # Простой паттерн БЕЗ атрибутов
        open_pattern = rf'<{tag}>'
        close_pattern = rf'</{tag}>'

        # Используем finditer вместо findall для большей точности
        open_tags = list(re.finditer(open_pattern, text))
        close_tags = list(re.finditer(close_pattern, text))

        open_count = len(open_tags)
        close_count = len(close_tags)

        if open_count != close_count:
            logger.warning(f"Несбалансированные теги...")
            text = re.sub(open_pattern, '', text)
            text = re.sub(close_pattern, '', text)
            logger.info(f"Удалены все теги <{tag}>...")

    # Отдельная обработка для <a> (имеет атрибуты)
    a_open = len(re.findall(r'<a\s+href="[^"]*">', text))
    a_close = len(re.findall(r'</a>', text))

    if a_open != a_close:
        logger.warning(f"Несбалансированные теги <a>...")
        text = re.sub(r'<a\s+href="[^"]*">', '', text)
        text = re.sub(r'</a>', '', text)
        logger.info("Удалены все теги <a>...")

    return text
