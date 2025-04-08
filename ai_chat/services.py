import os
import requests
from django.http import StreamingHttpResponse

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
        "url": "https://api.deepseek.com/v1/chat/completions",
        "key": os.getenv("DEEPSEEK_API_KEY"),
    },
}


def send_to_ai_provider(provider, model, messages, stream=False):
    print(provider, model, stream, "ASYNC ")
    if provider not in AI_PROVIDERS:
        raise ValueError(f"Unknown provider: {provider}")

    config = AI_PROVIDERS[provider]
    headers = {
        "Authorization": f"Bearer {config['key']}",
        "Content-Type": "application/json",
    }
    body = {"model": model, "messages": messages, "stream": stream}

    response = requests.post(config["url"], json=body, headers=headers, stream=stream)

    if stream:

        def event_stream():
            for line in response.iter_lines():
                if line:
                    yield f"data: {line.decode('utf-8')}\n\n"

        return StreamingHttpResponse(event_stream(), content_type="text/event-stream")

    if response.status_code != 200:
        raise Exception(f"{provider} error: {response.status_code} {response.text}")

    return response.json()["choices"][0]["message"]["content"]
