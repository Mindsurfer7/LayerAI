import os
import json
import uuid
import requests
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from memory.models import UserMemory
from .services import send_to_ai_provider
from .models import ChatSession, Message
from .serializers import ChatMessageSerializer
from rest_framework.exceptions import NotFound
from django.http import StreamingHttpResponse


# user_facts = user.get_user_facts()
# Или user.get_user_facts(category="interests") для фильтрации
# f"Ранее известные факты: {json.dumps(user_facts, ensure_ascii=False)}\n"

# THIS_SERVER_URL = os.getenv("THIS_SERVER_URL")


class ChatProxyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        provider = request.data.get("provider")
        messages = request.data.get("messages")
        model = request.data.get("model")
        stream = request.data.get("stream", False)
        session_id = request.data.get("session_id")

        if not provider or not messages or not model or not session_id:
            print("checking the error")
            print(provider)
            print(session_id)
            print(messages)
            print(model)

            return Response(
                {"detail": "Missing fields"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            session = ChatSession.objects.get(id=session_id, user=request.user)
        except ChatSession.DoesNotExist:
            print("no sesssion error")
            return Response(
                {"detail": "Chat session not found"}, status=status.HTTP_404_NOT_FOUND
            )

        last_user_msg = messages[-1] if messages else None
        if last_user_msg and last_user_msg.get("role") == "user":
            Message.objects.create(
                session=session,
                role="user",
                content=last_user_msg["content"],
            )

        try:
            ai_response = send_to_ai_provider(
                provider, model, messages, request.user, stream
            )
            self._trigger_memory_analysis(
                request, session, messages, last_user_msg["content"]
            )

            if stream:
                full_response = ""

                def event_stream():
                    nonlocal full_response
                    for line in ai_response.iter_lines():
                        if line:
                            decoded_line = line.decode("utf-8")
                            if decoded_line.startswith("data: "):
                                data = decoded_line[6:]
                                if data == "[DONE]":
                                    yield f"data: {data}\n\n"
                                    break
                                try:
                                    chunk_json = json.loads(data)
                                    content = chunk_json["choices"][0]["delta"].get(
                                        "content"
                                    )
                                    if content:
                                        full_response += content
                                        chunk_response = {
                                            "choices": [{"delta": {"content": content}}]
                                        }
                                        yield f"data: {json.dumps(chunk_response)}\n\n"
                                except (json.JSONDecodeError, KeyError) as e:
                                    print(f"Error parsing chunk: {e}, chunk: {data}")

                    if full_response:

                        Message.objects.create(
                            session=session,
                            role="assistant",
                            content=full_response,
                        )

                return StreamingHttpResponse(
                    event_stream(), content_type="text/event-stream"
                )

            Message.objects.create(
                session=session,
                role="assistant",
                content=ai_response,
            )
            print(ai_response)

            return Response({"choices": [{"message": {"content": ai_response}}]})

        except ValueError as e:
            print(
                ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> something gone wrong <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
            )
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"detail": "AI provider error", "error": str(e)}, status=500
            )

    # а не надо ли вынести это в сервисы?
    def _trigger_memory_analysis(self, request, session, messages, new_message):
        # Собираем данные для анализа
        user = request.user
        # Последние 5 сообщений пользователя (кроме последнего)
        last_messages = [
            msg.content
            for msg in session.messages.filter(role=Message.Role.USER).order_by(
                "-timestamp"
            )[:5]
        ]
        # Ранее известные факты (последние 5)
        known_facts = list(
            UserMemory.objects.filter(user=user).values("title", "fact")[:5]
        )
        # ID сообщений для source_messages (берём ID последних сообщений)
        source_message_ids = list(
            session.messages.filter(role=Message.Role.USER)
            .order_by("-timestamp")
            .values_list("id", flat=True)[:5]
        )

        # Формируем данные для запроса к /api/memory/analyze/
        analyze_data = {
            "user_id": user.id,
            "last_messages": last_messages,
            "new_message": new_message,
            "known_facts": known_facts,
            "source_messages": source_message_ids,
        }

        analyze_url = f"{os.getenv('THIS_SERVER_URL')}/api/v1/memory/analyze/"

        try:
            response = requests.post(
                analyze_url,
                json=analyze_data,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error during memory analysis: {e}")


class ChatSessionCreateAPIView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        session = ChatSession.objects.create(user=request.user)
        return Response({"id": session.id})


class ChatSessionListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        sessions = ChatSession.objects.filter(user=request.user)
        data = [
            {"id": session.id, "title": session.title or f"Чат {session.id}"}
            for session in sessions
        ]
        return Response(data, status=status.HTTP_200_OK)


class ChatMessageListAPIView(generics.ListAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        session_id = self.kwargs.get("session_id")
        try:
            session = ChatSession.objects.get(id=session_id, user=self.request.user)
        except ChatSession.DoesNotExist:
            raise NotFound("Chat session not found.")
        sessionMessages = session.messages.order_by("timestamp")
        print(sessionMessages)
        return sessionMessages


class TranscribeVoiceAPIView(APIView):
    def post(self, request):

        # Проверка API-ключа c расширения(пока нету)
        # api_key = request.headers.get('X-API-Key')
        # if api_key != os.getenv('EXTENSION_API_KEY'):
        #     return Response({'error': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        # Проверка наличия аудиофайла
        audio_file = request.FILES.get("file")
        if not audio_file:
            return Response(
                {"error": "Audio file required"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Проверка MIME-типа (MP3, WebM, OGG, WAV)
        valid_mime_types = [
            "audio/mpeg",
            "audio/webm",
            "audio/ogg",
            "audio/wav",
            "audio/m4a",
        ]
        if audio_file.content_type not in valid_mime_types:
            return Response(
                {"error": f"Unsupported file format: {audio_file.content_type}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Проверка размера файла (максимум 25 МБ для OpenAI Whisper)
        if audio_file.size > 25 * 1024 * 1024:
            return Response(
                {"error": "File size exceeds 25 MB limit"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Сохранение файла временно
        file_name = f"{uuid.uuid4()}.m4a"  # Используем .ogg как расширение (поддерживает MP3 содержимое)
        file_path = os.path.join(settings.MEDIA_ROOT, "voices", file_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        print(file_path)
        try:
            with open(file_path, "wb") as f:
                for chunk in audio_file.chunks():
                    f.write(chunk)

            # Отправка в OpenAI Whisper
            with open(file_path, "rb") as f:
                files = {"file": (file_name, f, audio_file.content_type)}
                data = {"model": request.POST.get("model", "whisper-1")}
                headers = {"Authorization": f'Bearer {os.getenv("OPENAI_API_KEY")}'}
                response = requests.post(
                    "https://api.openai.com/v1/audio/transcriptions",
                    headers=headers,
                    files=files,
                    data=data,
                )

            # Удаление временного файла
            os.remove(file_path)

            # Обработка ответа OpenAI
            if response.status_code == 200:
                result = response.json()
                print(result["text"])
                return Response({"result": result["text"]})
            else:
                error = response.json().get("error", "Unknown error")
                return Response(
                    {"error": error}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except Exception as e:
            # Удаление файла в случае ошибки
            if os.path.exists(file_path):
                os.remove(file_path)
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
