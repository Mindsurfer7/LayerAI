# ai_chat/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import send_to_ai_provider


class ChatProxyView(APIView):
    def post(self, request):
        provider = request.data.get("provider")
        messages = request.data.get("messages")
        model = request.data.get("model")
        stream = request.data.get("stream", False)

        if not provider or not messages or not model:
            return Response(
                {"detail": "Missing fields"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            response = send_to_ai_provider(provider, model, messages, stream)
            return response if stream else Response(response)
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"detail": "AI provider error", "error": str(e)}, status=500
            )
