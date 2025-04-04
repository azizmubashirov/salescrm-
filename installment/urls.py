from django.urls import path
from .views import *

urlpatterns = [
    path('month-list', MonthListApiView.as_view()),
    path('month-create', MonthCreateApiView.as_view()),
    path('month-edit/<int:id>', MonthUpdateApiView.as_view()),
    path('month-info/<int:id>', MonthDetailApiView.as_view()),
    path('month-delete', MonthDeleteApiView.as_view()),
  
    path('list', InstallmentPlanApiView.as_view()),
    path('leads', InstallmentPlanLeadApiView.as_view()),
    path('list-for-bot', InstallmentPlanBotApiView.as_view()),
    path('import-exel-order', ExportPlanToExcel.as_view()),
    
    path('create', InstallmentCreateApiView.as_view()),
    path('info/<int:id>', InstallmentInfoApiView.as_view()),
    path('info-id/<int:id>', InstallmentIdApiView.as_view()),
    path('update/<int:id>', InstallmentUpdateApiView.as_view()),
    path('return/<int:id>', InstallmentReturnApiView.as_view()),
    path('update-status/<int:id>', InstallmentUpdateStatusApiView.as_view()),
    path('delete', InstallmentDeleteApiView.as_view()),
    path('update-comment/<int:id>', InstallmentUpdateCommentApiView.as_view()),
    
    path('payment-create', PaymentCreateApiView.as_view()),
    path('debt-list', DebtListApiView.as_view()),
    path('debt-update/<int:id>', DebtUpdateApiView.as_view()),
    path('debt-export-exel', DebtExportApiView.as_view()),
]