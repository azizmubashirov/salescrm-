from django.contrib import admin
from .models import User, Role, Permission


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'firstname', 'lastname', 'surname', 'login', 'phone')
    
@admin.register(Role)
class RolerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    
@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


