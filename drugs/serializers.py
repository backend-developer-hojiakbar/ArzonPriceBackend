# serializers.py
from rest_framework import serializers
from .models import ExcelFile, Drug, Token


class ExcelFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExcelFile
        fields = ['file']


class DrugSerializer(serializers.ModelSerializer):
    class Meta:
        model = Drug
        fields = ['name', 'company', 'price']


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields = ['key', 'user', 'created', 'expires', 'period']


