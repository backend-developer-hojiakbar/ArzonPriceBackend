from django.contrib import admin
from .models import Drug, ExcelFile, Token
# Register your models here.

admin.site.register(Drug)


@admin.register(ExcelFile)
class ExcelFileAdmin(admin.ModelAdmin):
    list_display = ('file', 'uploaded_at')


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'period', 'key')