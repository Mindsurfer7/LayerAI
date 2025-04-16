import os
import json
import requests

# from django.http import StreamingHttpResponse

AI_PROVIDERS = {
    "openai": {
        "url": "https://api.openai.com/v1/chat/completions",
        "key": os.getenv("OPENAI_API_KEY"),
    },
    "grok": {
        "url": "https://api.x.ai/v1/chat/completions",
        "key": os.getenv("GROK_API_KEY"),
    },
    "deepseek": {
        "url": "https://api.deepseek.com/chat/completions",
        "key": os.getenv("DEEPSEEK_API_KEY"),
    },
}


def send_to_ai_provider(provider, model, messages, user=None, stream=False):

    print(provider, model, user, stream, "send_to_ai_provider data ")

    if provider not in AI_PROVIDERS:
        raise ValueError(f"Unknown provider: {provider}")

    modified_messages = messages.copy()

    if user:
        user_facts = user.get_user_facts()  # Получаем факты пользователя
        facts_json = json.dumps(user_facts, ensure_ascii=False)
        system_message = {
            "role": "system",
            "content": f"Факты о пользователе: {facts_json}. Учитывай эти факты при ответе.",
        }

        modified_messages.insert(0, system_message)

    config = AI_PROVIDERS[provider]
    headers = {
        "Authorization": f"Bearer {config['key']}",
        "Content-Type": "application/json",
    }
    body = {"model": model, "messages": modified_messages, "stream": stream}
    print("--------------------> ")
    print(config["url"])
    response = requests.post(config["url"], json=body, headers=headers, stream=stream)

    print("-----------------------------")
    print(f"Status Code: {response.status_code}")

    if stream:
        return response

    if response.status_code != 200:
        raise Exception(f"{provider} error: {response.status_code} {response.text}")

    return response.json()["choices"][0]["message"]["content"]


#  if stream:

#         def event_stream():
#             for line in response.iter_lines():
#                 if line:
#                     yield f"data: {line.decode('utf-8')}\n\n"

#         return StreamingHttpResponse(event_stream(), content_type="text/event-stream")
