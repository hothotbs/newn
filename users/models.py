from django.db import models
from django.contrib.auth.models import User
import uuid


class PasswordID(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reset_id = models.CharField(
        default=uuid.uuid4, unique=True)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} reset password link "


class Dashboard(models.Model):
    level = models.CharField(max_length=20, default="Stater")
    profit = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    invest = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    user = models.OneToOneField(User, on_delete=models.CASCADE, editable=False)
    created_on = models.DateTimeField(auto_now_add=True)
    modify_on = models.DateTimeField(auto_now=True)

    @property
    def total_bal(self):
        total = self.profit + self.invest
        return total

    def deposit(self, amount):
        if amount <= 19:
            raise ValueError('You can deposit $20 Minimum')
        else:
            self.invest += amount

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError(f'enter an amount greater than {amount}')
        elif self.total_bal == 0:
            raise ValueError('your account balance is 0')
        else:
            if amount > self.total_bal:
                raise ValueError(
                    f'{amount} is greater than your avaialble balance')
            elif amount <= self.total_bal:
                if amount <= self.profit:
                    self.profit -= amount
                elif amount > self.profit:
                    remainder = amount - self.profit
                    self.profit = 0
                    self.invest -= remainder

    def __str__(self):
        return self.user.username


class Withdraw(models.Model):

    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('reject', 'Reject'),
    )
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    wallet_address = models.CharField(max_length=100)
    status = models.CharField(choices=STATUS_CHOICES, default='pending')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        dashboard = Dashboard.objects.get(user=self.user)

        if self.pk:
            existing = Withdraw.objects.get(pk=self.pk)

            if existing.status == 'pending' and self.status == 'reject':
                dashboard.profit += existing.amount
                dashboard.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} withdraw ${self.amount} currently {self.status}"


class PaymentMethod(models.Model):
    name_of_coin = models.CharField(max_length=50)
    wallet_address = models.CharField(max_length=100)
    network = models.CharField(max_length=50)
    email = models.EmailField(null=True)

    def __str__(self):
        return self.name_of_coin


class Deposit(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('reject', 'Reject'),
    )
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    mode_of_payment = models.ForeignKey(
        PaymentMethod, on_delete=models.CASCADE, blank=True, null=True)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    status = models.CharField(choices=STATUS_CHOICES, default='pending')
    user = models.ForeignKey(User, on_delete=models.CASCADE, )
    created_on = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        dashboard = Dashboard.objects.get(user=self.user)

        if self.pk:
            existing = Deposit.objects.get(pk=self.pk)
            if existing.status == 'pending' and self.status == 'approved':
                dashboard.deposit(existing.amount)
                dashboard.save()

        elif self.status == "approved":

            dashboard.deposit(self.amount)
            dashboard.save()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} deposit ${self.amount} currently {self.status} via {self.mode_of_payment}"
