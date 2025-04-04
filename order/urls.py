from django.urls import path
from order.views import *

urlpatterns = [
    path('list', OrderListApiView.as_view()),
    path('leads', OrderLeadApiView.as_view()),
    path('generate-image/<int:order_id>', GenerateOrderImageView.as_view()),
    path('import-exel-order', ExportOrderToExcel.as_view()),
    path('info/<int:id>', OrderDetailApiView.as_view()),
    path('create', OrderCreateApiView.as_view()),
    path('list-for-bot', OrdersForBotListApiView.as_view()),
    path('update/<int:id>', OrderUpdateApiView.as_view()),
    path('update-status/<int:id>', OrderStatusEditApiView.as_view()),
    path('update-return/<int:id>', OrderReturnApiView.as_view()),
    path('delete', OrderDeleteApiView.as_view()),
    path('update-comment/<int:id>', OrderCommentApiView.as_view()),
    
    
    #amo-crm-post
    path('amocrm-order', AmoCrmOrder.as_view()),
    
    path('daily-sales/', DailySalesView.as_view()),
]