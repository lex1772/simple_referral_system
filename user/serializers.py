from rest_framework import serializers

from user.models import User


class UserSerializer(serializers.ModelSerializer):
    # Сериализатор для пользователя
    codes = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['phone', 'referral_code', 'codes',]

    def get_codes(self, instance):
        '''функция для полчения списка номеров телеонов, которые зарегистрировались по коду пользователя'''
        user_list = []
        users = User.objects.filter(user_invite_code=instance.referral_code)
        for user in users:
            user_list.append(user.phone)
        return user_list
