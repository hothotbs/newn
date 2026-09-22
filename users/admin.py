from django.contrib import admin
from .models import *

# Register your models here.


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    exclude = ['is_active', 'is_staff',
               'is_supersuer', 'groups', 'Superuser_status', 'user_permissions']
    list_display = ['email', 'full_name', 'last_login', 'country']


@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ['user', 'invest', 'profit', 'level']
    list_editable = ['invest', 'profit', 'level']
    search_fields = ['user__email']


@admin.register(Withdraw)
class WithdrawAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'wallet_address', 'status', 'created_on']
    list_editable = ['amount', 'wallet_address', 'status']
    search_fields = ['user__email']


@admin.register(Deposit)
class DepositAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'mode_of_payment',
                    'image', 'status', 'created_on']
    list_editable = ['amount', 'status']
    search_fields = ['user__email']


@admin.register(Config)
class ConfigAdmin(admin.ModelAdmin):
    list_display = ['app_name']


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['name_of_coin', 'wallet_address', 'network']
    list_editable = ['wallet_address', 'network']
    search_fields = ['name_of_coin', 'wallet_address', 'network']


@admin.register(Withdraw_password)
class Withdraw_passwordAdmin(admin.ModelAdmin):
    list_display = ['user', 'password']
    search_fields = ['user__email']


@admin.register(Bind_wallet)
class Bind_walletAdmin(admin.ModelAdmin):
    list_display = ['user', 'private_key']
