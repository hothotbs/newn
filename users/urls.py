from django.urls import path
from .views import *

urlpatterns = [
    path('users/create-account', create_account, name='create-account'),
    path('users/login', loginview, name='login'),
    path('users/logout', logoutview, name='logout'),
    path('users/reset-password-link',
         reset_password_link, name='reset-password-link'),
    path('users/password-link-sent/<str:pk>',
         password_link_sent, name='password-link-sent'),
    path('users/password-reset/<str:pk>',
         password_reset, name='password-reset'),
    path('users/dashboard', dashboard, name='dashboard'),
    path('users/withdraw', withdraw, name='withdraw'),
    path('users/deposit', deposit, name='deposit'),
    path('users/deposit-process1', deposit_process1, name='deposit-process1'),
    path('users/edit-profile', edit_profile, name='edit-profile'),


]
