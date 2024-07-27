from django.utils import timezone
from django.http import JsonResponse
from rest_framework.decorators import api_view
from .models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from datetime import timedelta
from rest_framework import status, viewsets
from rest_framework.decorators import action
from .serializers import ExcelFileSerializer, DrugSerializer
from .models import Drug, ExcelFile, Token
from django.db import transaction
import pandas as pd
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .models import Token
import json


@csrf_exempt  # Exempt from CSRF validation for API requests
def verify_token(request):
    if request.method == 'POST':
        try:
            # Read the raw JSON data
            body = json.loads(request.body)
            token_key = body.get('token')

            # Check if the token exists in the database
            token = Token.objects.filter(key=token_key).first()
            if token and token.expires > timezone.now():
                return JsonResponse({'message': 'Token is valid'})
            else:
                return JsonResponse({'message': 'Invalid token or expired'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON'}, status=400)
    return JsonResponse({'message': 'Method not allowed'}, status=405)


class ExcelUploadViewSet(viewsets.ViewSet):

    @action(detail=False, methods=['post'], url_path='upload')
    def upload_excel(self, request, *args, **kwargs):
        serializer = ExcelFileSerializer(data=request.data)
        if serializer.is_valid():
            file = serializer.save()
            try:
                self.import_drugs_from_excel(file.file.path)
                return Response({"message": "File uploaded and data imported successfully!"}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def import_drugs_from_excel(self, file_path):
        data = pd.read_excel(file_path)
        required_columns = ['Name', 'Company', 'Price']
        with transaction.atomic():
            for _, row in data.iterrows():
                if all(column in row for column in required_columns):
                    name = row['Name']
                    price = row['Price']
                    company = row['Company']
                    if pd.isna(price) or not isinstance(price, (int, float)):
                        continue
                    unique_name = f"{name} - {company}"
                    Drug.objects.create(
                        name=unique_name,
                        price=price,
                        company=company
                    )


class DrugSearchView(ListAPIView):
    serializer_class = DrugSerializer

    def get_queryset(self):
        query = self.request.query_params.get('q', None)
        if query:
            return Drug.objects.filter(name__icontains=query)
        return Drug.objects.none()