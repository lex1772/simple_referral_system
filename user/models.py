import random
import string

from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
# переменная для полей с нулевым значением
NULLABLE = {'blank': True, 'null': True}


class User(AbstractUser):
    """Создаем пользователя через класс абстрактного пользователя с авторизаией по телефону"""
    username = None

    phone = models.CharField(max_length=35, verbose_name='телефон', unique=True)
    referral_code = models.CharField(max_length=6, verbose_name='реферальный код пользователя', unique=True, **NULLABLE)
    user_invite_code = models.CharField(max_length=6, verbose_name='код приглашение другого пользователя', unique=True,
                                        **NULLABLE)
    otp = models.CharField(max_length=6, **NULLABLE)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.phone

    def generate_referral_code(self):
        '''Функция для генерации реерального кода'''
        referral_code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        return referral_code
