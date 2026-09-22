from django.urls import path
from .views import *

urlpatterns = [
    path('users/create-account', create_account, name='create-account'),
    path('users/login', loginview, name='login'),
    path('users/logout', logoutview, name='logout'),
    path('users/reset-password-link',
         reset_password_link, name='reset-password-link'),
    path('users/password-link-sent',
         password_link_sent, name='password-link-sent'),
    path('users/password-reset/<str:pk>',
         password_reset, name='password-reset'),
    path('users/reset-password/',
         reset_password, name='reset-password'),
    path('users/dashboard', dashboard, name='dashboard'),
    path('users/withdrawal-history', withdrawal_history, name='withdrawal-history'),
    path('users/withdraw', withdraw, name='withdraw'),
    path('users/withdrawal-password',
         withdrawal_password, name='withdrawal_password'),
    path('users/deposit-history', deposit_history, name='deposit-history'),
    path('users/deposit', deposit, name='deposit'),
    path('users/deposit-process1', deposit_process1, name='deposit-process1'),
    path('users/edit-profile', edit_profile, name='edit-profile'),
    path('users/upgrade-plans', upgrade_plans, name='upgrade-plans'),
    path('users/bind-wallet', bind_wallet, name='bind_wallet'),

]
