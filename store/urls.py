from django.urls import path
from store.views import *

urlpatterns = [
    path('list', StoreListApiView.as_view()),
    path('create', StoreCreateApiView.as_view()),
    path('update/<int:id>', StoreUpdateApiView.as_view()),
    path('delete', StoreDeleteApiView.as_view()),
    path('info/<int:id>', StoreDetailApiView.as_view()),
    
    #StoreBalance
    path('store-balance-history/<int:store_id>', BalanceListApiView.as_view()),
    path('store-balance/<int:store_id>', BalanceApiView.as_view()),
    path('balance/create', BalanceCreateApiView.as_view()),
    path('import-exel-balance', ExportBalanceToExcel.as_view()),
    path('import-exel-balance-admin', ExportBalanceToExcelAdmin.as_view()),
    path('balance-delete', BalanceDeleteApiView.as_view()),
    
    path('daily-store-balance/', DailyStoreBalanceView.as_view()),
]