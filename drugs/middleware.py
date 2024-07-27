# yourapp/middleware.py
from django.utils import timezone
from .models import Token


class ExpireTokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.delete_expired_tokens()
        response = self.get_response(request)
        return response

    def delete_expired_tokens(self):
        Token.objects.filter(expires__lt=timezone.now()).delete()
