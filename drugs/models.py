import os
from django.db.models.signals import post_save
from django.dispatch import receiver
import pandas as pd
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class Token(models.Model):
    PERIOD_CHOICES = (
        ('1D', '1 Day'),
        ('1M', '1 Month'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    key = models.CharField(max_length=40, primary_key=True)
    created = models.DateTimeField(auto_now_add=True)
    expires = models.DateTimeField()
    period = models.CharField(max_length=2, choices=PERIOD_CHOICES, default='1D')

    def save(self, *args, **kwargs):
        self.key = self.generate_key()
        self.expires = timezone.now() + timedelta(days=1 if self.period == '1D' else 30)
        return super().save(*args, **kwargs)

    def generate_key(self):
        import binascii
        import os
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.key

    @staticmethod
    def get_or_create(user, period='1D'):
        token, created = Token.objects.get_or_create(user=user, defaults={'period': period})
        if not created:
            token.expires = timezone.now() + timedelta(days=1 if period == '1D' else 30)
            token.period = period
            token.save()
        return token


class Drug(models.Model):
    name = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} - {self.company} - {self.price}"


class ExcelFile(models.Model):
    file = models.FileField(upload_to='excel_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return os.path.basename(self.file.name)


@receiver(post_save, sender=ExcelFile)
def import_drugs_from_excel(sender, instance, **kwargs):
    excel_file_path = instance.file.path
    try:
        data = pd.read_excel(excel_file_path)

        required_columns = ['Name', 'Company', 'Price']
        for _, row in data.iterrows():
            if all(column in row for column in required_columns):
                name = row['Name']
                price = row['Price']
                company = row['Company']
                if pd.isna(price) or not isinstance(price, (int, float)):
                    continue
                Drug.objects.update_or_create(
                    name=name,
                    defaults={
                        'price': price,
                        'company': company
                    }
                )
    except Exception as e:
        print(f"An error occurred: {str(e)}")
