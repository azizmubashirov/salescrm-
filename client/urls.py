from django.urls import path
from client.views import *

urlpatterns = [
    path('create', ClientCreateApiView.as_view()),
    path('create-bot', ClientCreateBotApiView.as_view()),
    path('update/<int:id>', ClientUpdateApiView.as_view()),
    path('delete', ClientDeleteApiView.as_view()),
    path('info/<int:id>', ClientDetailApiView.as_view()),
    path('info-bot/<int:chat_id>', ClientInfoForBotDetailApiView.as_view()),
    path('list', ClientListApiView.as_view()),
    
    #Discount
    path('discount-level-list', DiscountLevelListApiView.as_view()),
    path('discount-level-create', DiscountLevelCreateApiView.as_view()),
    path('discount-level-edit/<int:id>', DiscountLevelUpdateApiView.as_view()),
    path('discount-level-delete/', DiscountLevelDeleteApiView.as_view()),
    path('discount-level-info/<int:id>', DiscountLevelDetailApiView.as_view()),
    
    #Clinet Level
    path('client-level', ClientLevelListApiView.as_view()),
    path('client-level-accept/<int:id>', ClientLevelUpdateApiView.as_view()),
    path('client-level-create', ClientLevelCreateApiView.as_view()),
]