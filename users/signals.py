from django.db.models.signals import post_save, pre_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import *
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile


@receiver(post_save, sender=User)
def withdraw_password(sender, instance, created, **kwargs):
    if created:

        Withdraw_password.objects.create(user=instance)


@receiver(post_save, sender=User)
def create_dashboard(sender, instance, created, **kwargs):
    if created:
        Dashboard.objects.create(user=instance)


@receiver(pre_save, sender=Deposit)
def dashboard_deposit(sender, instance, **kwargs):
    dashboard = Dashboard.objects.get(user=instance.user)

    if instance.pk:
        existing_deposit = Deposit.objects.get(pk=instance.pk)
        existing_deposit_status = existing_deposit.status

        if (existing_deposit_status == 'pending' or existing_deposit_status == 'rejected') and instance.status == 'approved':

            dashboard.invest += instance.amount
            dashboard.save()
        elif existing_deposit_status == 'approved' and (instance.status == 'rejected' or instance.status == 'pending'):
            dashboard.invest -= instance.amount
            dashboard.save()

    elif not instance.pk:

        if instance.status == 'approved':
            dashboard.invest += instance.amount
            dashboard.save()


@receiver(pre_save, sender=Withdraw)
def dashboard_withdrawal(sender, instance, **kwargs):

    dashboard = Dashboard.objects.get(user=instance.user)
    if not instance.pk:

        if instance.amount <= dashboard.profit:
            dashboard.profit -= instance.amount
            dashboard.save()

        elif instance.amount > dashboard.profit:
            remainder = instance.amount - dashboard.profit
            dashboard.profit = 0
            dashboard.invest -= remainder
            dashboard.save()

    elif instance.pk:
        print('existing')
        existing_withdraw = Withdraw.objects.get(pk=instance.pk)

        if (existing_withdraw.status == 'pending' or existing_withdraw.status == 'approved') and instance.status == 'rejected':
            dashboard.profit += existing_withdraw.amount
            dashboard.save()
            print('pending to reject')

        if existing_withdraw.status == 'rejected' and (instance.status == 'pending' or instance.status == 'approved'):
            dashboard.profit -= existing_withdraw.amount
            dashboard.save()
            print('reject to pend')


@receiver(pre_save, sender=PaymentMethod)
def create_qrcode(sender, instance, **kwargs):
    if instance.pk:
        old_address = PaymentMethod.objects.get(pk=instance.pk).wallet_address

    if not instance.pk or (instance.pk and (old_address != instance.wallet_address)):
        name = '-'.join(instance.name_of_coin.split())
        wallet_address = instance.wallet_address

        img = qrcode.make(wallet_address)
        buffer = BytesIO()
        img.save(buffer, format='PNG')

        instance.qr_code.save(f'{name}.png', ContentFile(buffer.getvalue()),
                              save=False
                              )
