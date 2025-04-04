from django.urls import path
from currency.views import *

urlpatterns = [
    path('create', CurrencyCreateApiView.as_view()),
    path('update/<int:id>', CurrencyUpdateApiView.as_view()),
    path('info/<int:id>', CurrencyDetailView.as_view()),
    path('delete', CurrencyDeleteApiView.as_view()),
    path('list', CurrencyListApiView.as_view()),
    path('history-list', CurrencyHistoryList.as_view())
]