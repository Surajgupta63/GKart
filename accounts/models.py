from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# Create your models here.

class MyAccountManager(BaseUserManager):
    def create_user(self, email, username, first_name, last_name, password=None):
        if not email:
            raise ValueError("User must have an email address")
        
        if not username:
            raise ValueError("User must have an username")
        
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, username, first_name, last_name, password):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )

        user.is_admin = True
        user.is_staff = True
        user.is_active = True
        user.is_superadmin = True
        user.save(using=self._db)
        return user

class Account(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    username = models.CharField(max_length=100, unique=True)
    email = models.CharField(max_length=100, unique=True)
    mobile_number = models.CharField(max_length=13)

    ## required
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']


    objects = MyAccountManager()

    def full_name(self):
        return f'{self.first_name} {self.last_name}'
    
    def __str__(self):
        return self.email
    
    @property
    def is_superuser(self):
        return self.is_superadmin


    # def has_perm(self, perm, obj=None):
    #     return super().has_perm(perm, obj) or self.is_admin
    
    # def has_module_perms(self, add_label):
    #     if self.is_admin:
    #         return True
        
    #     # Use Django's PermissionsMixin to check group permissions
    #     return self.is_staff and self.user_permissions.exists() or self.groups.exists()
    

class UserProfile(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='userprofile', blank=True)
    address_line_1 = models.CharField(max_length=100, blank=True)
    address_line_2 = models.CharField(max_length=100, blank=True)
    pin_code = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=50, blank=True)
    state = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50, blank=True)

    def full_address(self):
        return f"{self.address_line_1} {self.address_line_2}"

    def __str__(self):
        return self.user.first_name
