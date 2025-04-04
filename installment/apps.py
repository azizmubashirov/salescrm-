from django.apps import AppConfig

class InstallmentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'installment'
    
    def ready(self):
        from . import task  
