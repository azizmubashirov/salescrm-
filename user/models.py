from django.db import models
from store.models import Store
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import PermissionsMixin, AbstractBaseUser
from django.utils import timezone
from .utils import create_slug

class UserManager(BaseUserManager):
    def create_user(self, login, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        login = self.normalize_email(login)
        user = self.model(login=login, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, login, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(login=login, password=password, **extra_fields)

class DateModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
        
class Permission(DateModel):
    name = models.CharField(max_length=25, blank=False, null=False)
    slug = models.SlugField(max_length=25, blank=True, null=True)
    
    class Meta:
        ordering = ['id'] 
        
    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        self.slug = create_slug(self)
        return super().save(*args, **kwargs)
    
class Role(DateModel):
    name = models.CharField(max_length=50, blank=False, null=False)
    def __str__(self) -> str:
        return self.name
    


class User(AbstractBaseUser, PermissionsMixin):
    login = models.CharField(max_length=100, blank=False, null=False, unique=True)
    firstname = models.CharField(max_length=150, blank=True, null=True)
    lastname = models.CharField(max_length=100, blank=True, null=True)
    surname = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=25, blank=True, null=True)
    role = models.ForeignKey(to=Role, on_delete=models.SET_NULL, blank=True, null=True)
    permission = models.ManyToManyField(to=Permission)
    store = models.ForeignKey(to=Store, on_delete=models.SET_NULL, blank=True, null=True)
    photo = models.URLField(blank=True, null=True, max_length=500)
    passport_seria_number = models.CharField(max_length=150, blank=True, null=True)
    passport_file = models.URLField(blank=True, null=True, max_length=500)
    order_price_change = models.BooleanField(default=False, )
    joined_date = models.DateTimeField(default=timezone.now, editable=False)
    is_staff = models.BooleanField(default=False, )
    is_active = models.BooleanField(default=True, null=False)
    is_verified = models.BooleanField(default=False, null=False)
 
    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = []

    objects = UserManager()
    
    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        return self.firstname or self.lastname or self.surname or "User None"
    