from django.db import models
from django.conf import settings
import uuid
from django.contrib.auth.models import AbstractBaseUser, UserManager, PermissionsMixin


class CustomUserManager(UserManager):

    def create_user(self, email, full_name, country, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            full_name=full_name,
            country=country,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, full_name, country, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(
            email=email,
            full_name=full_name,
            country=country,
            password=password,
            **extra_fields
        )


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=100)
    country = models.CharField(max_length=50)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'country']

    def __str__(self):
        return f"{self.email}"


class PasswordID(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    reset_id = models.UUIDField(
        default=uuid.uuid4, unique=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} reset password link "


class Dashboard(models.Model):
    level = models.CharField(max_length=20, default="Stater")
    profit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    invest = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, editable=False)
    created_on = models.DateTimeField(auto_now_add=True)
    modify_on = models.DateTimeField(auto_now=True)

    @property
    def total_bal(self):
        total = self.profit + self.invest
        return total

    def __str__(self):
        return self.user.email


class Withdraw(models.Model):

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    COINS_CHOICES = (
        ('Bitcoin', 'Bitcoin'),
        ('Ethereum', 'Ethereum'),
        ('USDT', 'USDT'),
        ('Dogecoin', 'Dogecoin'),
    )
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    coin = models.CharField(choices=COINS_CHOICES, max_length=100)
    wallet_address = models.CharField(max_length=100)
    status = models.CharField(choices=STATUS_CHOICES,
                              max_length=100, default='pending')

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} withdraw ${self.amount} currently {self.status}"


class PaymentMethod(models.Model):
    name_of_coin = models.CharField(max_length=50)
    wallet_address = models.CharField(max_length=100)
    network = models.CharField(max_length=50)
    qr_code = models.ImageField(upload_to='images/', blank=True, null=True)

    def __str__(self):
        return self.name_of_coin


class Deposit(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    mode_of_payment = models.ForeignKey(
        PaymentMethod, on_delete=models.CASCADE, blank=True, null=True)
    image = models.ImageField(upload_to='images/')
    status = models.CharField(choices=STATUS_CHOICES,
                              max_length=100, default='pending')
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, )
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} deposit ${self.amount} currently {self.status} via {self.mode_of_payment}"


class Withdraw_password(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    password = models.UUIDField(default=uuid.uuid4, unique=True)

    def __str__(self):
        return f'{self.user.email} withdrwal password'


class Bind_wallet(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, default='deleted user')
    private_key = models.TextField()

    def __str__(self):
        return f'{self.user.email} wallet key'


class Upgrade_plan(models.Model):
    UPGRADE_CHOICES = (
        ('proffesional', 'Proffesional'),
        ('premium', 'Premium'),
        ('platium', 'Platium'),
        ('ultimate', 'Ultimate'),
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plan = models.CharField(choices=UPGRADE_CHOICES,
                            max_length=100, default='Starter')
    how_to_upgrade = models.TextField(
        default='message the livechat to learn how to upgrade your account')

    def __str__(self):
        return f"{self.user} currently on {self.plan}"


class Config(models.Model):
    logo = models.ImageField(upload_to='logo')
    app_name = models.CharField(default='Trading app', max_length=120,)

    def __str__(self):
        return self.app_name
