import httpx
import json
from utils.config import settings

MAX_TELEGRAM_LENGTH = 4000

async def ask_ollama(prompt: str) -> str:
    url = f"{settings.OLLAMA_URL}"
    model = settings.OLLAMA_MODEL
    payload = {"model": model, "prompt": prompt}

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

            # Ограничение длины для Telegram
            if len(out) > MAX_TELEGRAM_LENGTH:
                out = out[:MAX_TELEGRAM_LENGTH-3] + "..."

            return out

    except Exception as e:
        return f"✨ Ошибка при запросе к Ollama: {e}"


async def ask_ollama_with_image(prompt: str, image_base64: str) -> str:
    """
    Отправить запрос к Ollama с изображением
    
    Args:
        prompt: Текстовый промпт
        image_base64: Изображение в формате base64
        
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
    
    model = settings.OLLAMA_MODEL
    
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
                
                # Ограничение длины для Telegram
                if len(content) > MAX_TELEGRAM_LENGTH:
                    content = content[:MAX_TELEGRAM_LENGTH-3] + "..."
                
                return content
            else:
                return "Бот не смог проанализировать изображение. Попробуйте ещё раз."

    except Exception as e:
        return f"✨ Ошибка при запросе к Ollama с изображением: {e}"