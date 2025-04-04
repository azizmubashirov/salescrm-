from django.urls import path
from settings import views


urlpatterns = [
    path('', views.SettingsUpdateApiView.as_view()),
    path('info', views.SettingsInfoApiView.as_view())
]