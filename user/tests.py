from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from user.models import User


# Create your tests here.
class UserTestCase(APITestCase):
    # Тесты для API
    def setUp(self) -> None:
        # Создание пользователей для тестирования
        self.user = User.objects.create(
            phone='11111111111', user_invite_code="AABBCC")
        self.user.referral_code = self.user.generate_referral_code()
        self.user.save()
        self.user2 = User.objects.create(
            phone='77777777777')
        self.user2.referral_code = self.user.generate_referral_code()
        self.user2.save()

    def test_login(self):
        """Тесты на логин пользователя по телефону"""
        response = self.client.post(
            reverse('user:user_login'),
            data={"phone": {self.user.phone}}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(
            reverse('user:user_login'),
            data={"phone": "22222222222", "user_invite_code": self.user2.referral_code}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # вызываем ошибку отсутствия пользователя с реферальным кодом
        response = self.client.post(
            reverse('user:user_login'),
            data={"phone": "33333333333", "user_invite_code": "QQ"}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json(), {'error': 'Пользователя с таким реферальным кодом нет'})

        # вызываем ошибку корректности номера телефона
        response = self.client.post(
            reverse('user:user_login'),
            data={"phone": "11"}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json(), {'error': 'Введите корректный номер телеона'})

        # вызываем ошибку уже введенного кода приглашения
        response = self.client.post(
            reverse('user:user_login'),
            data={"phone": {self.user.phone}, "user_invite_code": self.user2.referral_code}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json(), {'error': 'Вы уже вводили код приглашение'})

        #Тестируем профиль пользователя и добавление номеров телефона по реферальному коду
        response = self.client.get(
            reverse('user:user', kwargs={'phone': self.user2.phone})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['codes'], ['22222222222'])
        print(response.json())


    def test_validation_otp(self):
        '''Тестируем валидацию по коду подтверждения, добавляем пользователю 4-х значный код'''
        self.user.otp = "3412"
        self.user.save()

        #Тестируем на корректность кода
        response = self.client.post(
            reverse('user:user_validate'),
            data={"phone": {self.user.phone}, "otp": {self.user.otp}}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        #Тестируем на корректность телефона
        response = self.client.post(
            reverse('user:user_validate'),
            data={"phone": "55", "otp": {self.user.otp}}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json(), {'error': 'Пользователя с таким телефоном нет'})

        #Тестируем на корректность кода подтверждения
        response = self.client.post(
            reverse('user:user_validate'),
            data={"phone": {self.user.phone}, "otp": "5555"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {'error': 'Неверный код подтверждения'})


