import random
import string
import time

from rest_framework import generics, status
from rest_framework.response import Response
from sms import send_sms

from config.settings import SMS_NUMBER
from user.models import User
from user.serializers import UserSerializer


# Create your views here.
class LoginView(generics.GenericAPIView):
    '''Контроллер на логин пользоватея по номеру телефона, если телефон не зарегистрирован, то добавляется в базу и в конце отправляет четырехзначный код активации в консоль'''
    serializer_class = UserSerializer

    def post(self, request):
        phone = request.data.get('phone')
        user_invite_code = request.data.get('user_invite_code')
        user_code = User.objects.filter(referral_code=user_invite_code).exists()
        if len(phone) != 11:
            return Response({'error': 'Введите корректный номер телеона'}, status=status.HTTP_404_NOT_FOUND)
        if user_code is False and user_invite_code is not None:
            return Response({'error': 'Пользователя с таким реферальным кодом нет'}, status=status.HTTP_404_NOT_FOUND)

        user, created = User.objects.get_or_create(phone=phone)
        if user.user_invite_code is not None and user_invite_code is not None:
            return Response({'error': 'Вы уже вводили код приглашение'}, status=status.HTTP_404_NOT_FOUND)
        if created is True:
            code = user.generate_referral_code()
            user.referral_code = code
            user.user_invite_code = user_invite_code
            user.save()

        characters = string.digits
        otp = ''.join(random.choice(characters) for _ in range(4))
        time.sleep(2)
        send_sms(
            f'4-х значный код активации {otp}',
            SMS_NUMBER,
            [phone],
            fail_silently=False
        )
        user.otp = otp
        user.save()

        return Response({'message': 'На ваш телефон выслан 4-х значный код'}, status=status.HTTP_200_OK)


class ValidateOTP(generics.GenericAPIView):
    '''Контроллер для проверки четырехзначного кода'''
    serializer_class = UserSerializer

    def post(self, request):
        phone = request.data.get('phone')
        otp = request.data.get('otp')

        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return Response({'error': 'Пользователя с таким телефоном нет'}, status=status.HTTP_404_NOT_FOUND)

        if user.otp == otp:
            user.otp = None
            user.save()

            return Response({'message': 'успешно авторизовались'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Неверный код подтверждения'}, status=status.HTTP_400_BAD_REQUEST)


class UserRetrieveAPIView(generics.RetrieveAPIView):
    # Контроллер для просмотра профиля пользователя
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = 'phone'
