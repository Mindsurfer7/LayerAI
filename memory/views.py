import json
import requests
from django.http import JsonResponse

# from django.conf import settings
from .models import UserMemory
import os
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model

#  ATTENTION!!! Надо сделать чтоб провайдер аи передавалс динамически, а не хардкодом
# и вывести системное сбщ в коснтанты


@csrf_exempt
def analyze_memory(request):
    # Предполагаем, что данные приходят в теле запроса в формате JSON
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    # Извлекаем данные из запроса
    user_id = data.get("user_id")
    last_messages = data.get("last_messages", [])  # Последние сообщения
    new_message = data.get("new_message", "")  # Новое сообщение
    known_facts = data.get("known_facts", [])  # Ранее известные факты

    # Проверяем, что user_id передан
    if not user_id:
        return JsonResponse({"error": "user_id is required"}, status=400)

    # Получаем класс модели пользователя
    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    # Вызываем функцию анализа
    memory_suggestion = analyze_user_memory(
        user, last_messages, new_message, known_facts
    )

    # Если memory_suggestion есть и confidence >= 0.75, сохраняем в базу
    if memory_suggestion and memory_suggestion.get("confidence", 0) >= 0.65:
        UserMemory.objects.create(
            user=user,
            title=memory_suggestion["title"],
            fact=memory_suggestion["fact"],
            reason=memory_suggestion["reason"],
            confidence=memory_suggestion["confidence"],
            fact_category=memory_suggestion["fact_category"],
            source_messages=memory_suggestion["source_messages"],
        )

    return JsonResponse({"status": "success", "memory_suggestion": memory_suggestion})


def analyze_user_memory(user, last_messages, new_message, known_facts):
    # Системный промпт для Grok
    system_prompt = """
    Ты — модуль анализа поведения пользователя. Твоя задача — анализировать частичную переписку и извлекать устойчивые, значимые или повторяющиеся факты о пользователе.

    Ты получишь:
        1. Ранее известные факты о пользователе (если есть).
        2. Несколько последних сообщений переписки.
        3. Новое сообщение от пользователя.

    Проанализируй это и определи, появился ли новый значимый факт о пользователе, который стоит сохранить. Факт может относиться к категориям(fact_category): интересам, привычкам, профессии, стилю общения, цели использования, ценностям, языку, мировоззрению, предпочтениям и т.д.

    Верни результат строго в формате JSON. Если ты не уверен, что факт важен или устойчив — верни null.
    Формат:
    {
      "memory_suggestion": {
        "title": "...",
        "fact": "...",
        "reason": "...",
        "confidence": 0.0-1.0,
        "source_messages": [...]
        "fact_category": [...]
      }
    }
    """

    system_content = (
        f"Ранее известные факты: {json.dumps(known_facts, ensure_ascii=False)}\n"
        f"Последние сообщения: {json.dumps(last_messages, ensure_ascii=False)}\n"
    )
    user_content = f"Новое сообщение: {new_message}"

    # Формируем messages в формате, который ожидает Grok API
    messages = [
        {"role": "system", "content": system_prompt + system_content},
        {"role": "user", "content": user_content},
    ]

    # Формируем данные для отправки в Grok
    payload = {
        "model": "grok-2-latest",  # Укажи правильную модель, если "grok" не работает
        "messages": messages,
        # "temperature": 0.7,  # Опционально
        # "max_tokens": 1000,  # Опционально
        "stream": False,  # Укажи False, если не используешь стриминг
    }

    # Используем конфигурацию Grok из AI_PROVIDERS
    grok_config = {
        "url": "https://api.x.ai/v1/chat/completions",  # URL для Grok
        "key": os.getenv("GROK_API_KEY"),  # API-ключ из переменных окружения
    }

    try:
        response = requests.post(
            grok_config["url"],
            json=payload,
            headers={"Authorization": f"Bearer {grok_config['key']}"},
        )
        response.raise_for_status()  # Проверяем, что запрос успешен
        result = response.json()

        print(result)

        memory_suggestion = (
            result.get("choices", [{}])[0].get("message", {}).get("content", None)
        )
        raw = result.get("choices", [{}])[0].get("message", {}).get("content", None)
        if raw and isinstance(raw, str):
            try:
                parsed = json.loads(raw)
                memory_suggestion = parsed.get("memory_suggestion")  # <- вот тут
            except json.JSONDecodeError as e:
                print("❌ JSON parse error:", e)
                return None

        # # Если Grok вернул строку, пытаемся её распарсить как JSON
        # if memory_suggestion and isinstance(memory_suggestion, str):
        #     try:
        #         memory_suggestion = parsed.get("memory_suggestion")
        #     except json.JSONDecodeError as e:
        #         print(
        #             f"Error parsing Grok response as JSON: {e}, response: {memory_suggestion}"
        #         )
        #         return None

        return memory_suggestion

    except requests.exceptions.RequestException as e:
        # Если что-то пошло не так, возвращаем None и логируем ошибку
        print(f"Error calling Grok API: {e}")
        return None
