from django.urls import path

from user.apps import UserConfig
from user.views import UserRetrieveAPIView, LoginView, ValidateOTP

app_name = UserConfig.name

# Урлы для приложения пользователя
urlpatterns = [
    path('login/', LoginView.as_view(), name='user_login'),
    path('validate/', ValidateOTP.as_view(), name='user_validate'),
    path('<str:phone>/', UserRetrieveAPIView.as_view(), name='user'),
]
