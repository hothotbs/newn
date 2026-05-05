from django.shortcuts import render, redirect
from .models import *
from .form import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone


def create_account(request):

    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':

        first_name = request.POST.get('first-name')
        last_name = request.POST.get('last-name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')

        field = [first_name, last_name, email,
                 username, password, confirm_password]

        password_has_error = False
        if not all(field):
            password_has_error = True
            messages.error(request, 'All field are required')
        else:
            if User.objects.filter(username=username).exists():
                password_has_error = True
                messages.error(request, 'username already exist')

            if User.objects.filter(email=email).exists():
                password_has_error = True
                messages.error(request, 'Email already exist')

            if password == "" or confirm_password == "":
                password_has_error = True
                messages.error(request, "Password can't be empty")

            else:
                if password != confirm_password:
                    password_has_error = True
                    messages.error(request, "Password doesn't match")
                else:
                    if len(password) <= 5:
                        password_has_error = True
                        messages.error(request, 'Password must be greater 5 ')

            if not password_has_error:
                user = User.objects.create_user(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    username=username,
                    password=password,
                )

                Dashboard.objects.create(user=user)
                messages.success(request, 'Account has been created, Login!')
                return redirect('login')

    return render(request, 'users/create-account.html')


def loginview(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'invalid inputs')
    context = {'form': form}
    return render(request, 'users/login.html', context)


def logoutview(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard(request):
    dashbord = Dashboard.objects.get(user=request.user)
    context = {'dashbord': dashbord}
    return render(request, 'users/dashboard.html', context)


@login_required
def withdraw(request):
    form = WithdrawalForm()
    withdrawal_history = Withdraw.objects.filter(
        user=request.user).order_by('-created_on')
    dashboard = Dashboard.objects.get(user=request.user)

    if request.method == 'POST':
        form = WithdrawalForm(request.POST)

        if form.is_valid():
            amount = form.cleaned_data['amount']
            wallet_address = form.cleaned_data['wallet_address']

            try:
                dashboard.withdraw(amount)
                dashboard.save()
                Withdraw.objects.create(
                    amount=amount, wallet_address=wallet_address, user=request.user)

            except ValueError as e:
                form.add_error('amount', str(e))

    context = {'form': form,
               "withdrawal_history": withdrawal_history,
               }
    return render(request, 'users/withdraw.html', context)


@login_required
def deposit_process1(request):
    form = DepositForm()
    payment_details = PaymentMethod.objects.all()
    Paymentmethod = request.POST.get('mode_of_payment')
    if request.method == 'POST':

        for payment_detail in payment_details:
            if str(payment_detail.id) == Paymentmethod:
                request.session['Paymentmethod'] = Paymentmethod
                return redirect('deposit')
            else:

                messages.error(request, 'select a valid mode of payment')

    context = {'form': form}
    return render(request, 'users/deposit-process1.html', context)


@login_required
def deposit(request):
    deposit_history = Deposit.objects.filter(
        user=request.user).order_by('-created_on')
    payment_detail = request.session.get('Paymentmethod')
    deposit_details = PaymentMethod.objects.get(
        pk=payment_detail)

    if request.method == 'POST':
        form = DepositForm(request.POST, request.FILES)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            image = form.cleaned_data['image']

            try:
                if amount <= 19:
                    messages.error(request, 'Deposit Mininum of $20')
                else:
                    Deposit.objects.create(
                        amount=amount, image=image, user=request.user)
                    messages.success(
                        request, f' Your ${amount} is processing and will appear on your dashboard when completed')
                    return redirect('deposit')
            except ValueError as e:
                form.add_error('amount', str(e))
    else:
        form = DepositForm()
    context = {'form': form,
               "deposit_history": deposit_history,
               'deposit_details': deposit_details
               }
    return render(request, 'users/deposit.html', context)


@login_required
def edit_profile(request):
    form = EditProfileForm(instance=request.user)
    if request.method == "POST":
        form = EditProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    context = {'form': form}
    return render(request, 'users/edit-profile.html', context)


def reset_password_link(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)

            password_id = PasswordID.objects.create(user=user)

            pwd_id = password_id.reset_id
            reset_pwd_url = f'{request.scheme}://{request.get_host()}/users/password-reset/{pwd_id}'
            a = f'{request.build_absolute_uri(pwd_id)}'

            email_body = f'use the link below to reset your password; \n\n {reset_pwd_url} \n {a}  ',

            email_message = EmailMessage(
                'Reset your password',
                email_body,
                settings.EMAIL_HOST_USER,
                [email]
            )
            email_message.fail_silently = True
            email_message.send()

            return redirect('password-link-sent', pk=pwd_id)

        except User.DoesNotExist:

            messages.error(
                request, 'enter the eamil you use to create account')
            return redirect('reset-password-link')

    return render(request, 'users/forget_password.html')


def password_link_sent(request, pk):

    if PasswordID.objects.filter(reset_id=pk).exists():
        pass
    else:
        messages.error(request, 'please try again')
        return redirect('reset-password-link')

    return render(request, 'users/password-link-sent.html')


def password_reset(request, pk):

    try:
        reset_id = PasswordID.objects.get(reset_id=pk)
        user = reset_id.user

        if request.method == 'POST':
            password = request.POST.get('password')
            password_confirm = request.POST.get('confirm-password')

            error_password = False

            created_time = reset_id.created_on
            minute = timezone.timedelta(minutes=10)

            expiration_time = created_time + minute

            if expiration_time <= timezone.now():
                error_password = True
                messages.error(request, 'Reset link has expired')
                reset_id.delete()
                return redirect('reset-password-link')
            else:

                if password != password_confirm:
                    error_password = True
                    messages.error(request, "password doesn't match")

                else:

                    if len(password) <= 5:
                        error_password = True
                        messages.error(
                            request, 'password must be greater than 5')
                    else:

                        if password == '123456':
                            error_password = True
                            messages.error(
                                request, 'password is too weak')

                        if user.check_password(password):
                            error_password = True
                            messages.error(
                                request, 'old password can not be new password')

                        if not error_password:
                            user.set_password(password)
                            user.save()

                            reset_id.delete()

                            messages.success(
                                request, 'new password has been created')
                            return redirect('login')

    except PasswordID.DoesNotExist:
        messages.error(
            request, "Invalid Link")
        return redirect('reset-password-link')

    return render(request, 'users/password-reset.html')
