from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Dashboard)
admin.site.register(Withdraw)
admin.site.register(Deposit)

admin.site.register(PaymentMethod)
admin.site.register(PasswordID)
