import uuid
from django.contrib import auth
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser


auth.signals.user_logged_in.disconnect(auth.models.update_last_login)


class UserManager(BaseUserManager):

    def create_user(self, email):
        user = self.model(email=self.normalize_email(email))
        user.set_password(None)
        user.full_clean()
        user.save()
        return user
        
    def create_superuser(self, email, password):
        user = self.model(email=self.normalize_email(email))
        user.is_admin = True
        user.set_password(password)
        user.full_clean()
        user.save()
        return user


class User(AbstractBaseUser):
    email = models.EmailField(primary_key=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    is_anonymous = False
    is_authenticated = True
    is_admin = models.BooleanField(default=False)

    objects = UserManager()
    
    @property
    def is_active(self):
        return True
        
    def __str__(self):
        return self.email
        
    def get_short_name(self):
        pass
        
    @property
    def is_staff(self):
        return self.is_admin
        
    def has_perm(self, perm, obj=None):
        return self.is_admin
        
    def has_module_perms(self, app_label):
        return self.is_admin


class Token(models.Model):
    email = models.EmailField()
    uid = models.CharField(default=uuid.uuid4, max_length=40)
