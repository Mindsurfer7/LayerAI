import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions

from memory.models import UserMemory
from .services import send_to_ai_provider
from .models import ChatSession, Message
from .serializers import ChatMessageSerializer
from rest_framework.exceptions import NotFound


class ChatProxyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        provider = request.data.get("provider")
        messages = request.data.get("messages")
        model = request.data.get("model")
        stream = request.data.get("stream", False)
        session_id = request.data.get("session_id")

        if not provider or not messages or not model or not session_id:
            return Response(
                {"detail": "Missing fields"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            session = ChatSession.objects.get(id=session_id, user=request.user)
        except ChatSession.DoesNotExist:
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
            ai_response = send_to_ai_provider(provider, model, messages, stream)
            self._trigger_memory_analysis(
                request, session, messages, last_user_msg["content"]
            )

            if stream:
                return ai_response

            Message.objects.create(
                session=session,
                role="assistant",
                content=ai_response,
            )
            return Response({"choices": [{"message": {"content": ai_response}}]})

        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"detail": "AI provider error", "error": str(e)}, status=500
            )

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

        # Вызываем эндпоинт анализа памяти
        analyze_url = "http://localhost:8000/api/v1/memory/analyze/"  # Замени на реальный URL, если нужно
        try:
            response = requests.post(
                analyze_url,
                json=analyze_data,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            print("Memory analysis result:", response.json())
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
        return session.messages.order_by("timestamp")
