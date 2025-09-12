from django.shortcuts import render, redirect
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

## Email Verification libraries
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

# Create your views here.

def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            mobile_number = form.cleaned_data['mobile_number']
            password = form.cleaned_data['password']

            username = email.split("@")[0]
            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                password=password
            )
            user.mobile_number = mobile_number
            user.save()

            ## Sending Verification Link To Email
            currnet_site = get_current_site(request)
            mail_subject = "Please Activate Your Account"
            message = render_to_string('accounts/email_verification.html', {
                "user": user,
                "domain": currnet_site,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": default_token_generator.make_token(user) 
            })

            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            # messages.success(request, f"Thank you for registering with us. We have sent you a verification email to your {to_email} email address. Please verify it.")
            return redirect('/accounts/login/?command=verification&email='+to_email)
    else:
        form = RegistrationForm()

    context = {
        "form": form,
    }
    return render(request, 'accounts/register.html', context)

def login(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)
        if user is not None:
            auth.login(request, user)
            messages.success(request, "You are logged in successfuly.")
            return redirect('dashboard')
        else:
            messages.error(request, "invalid email or password.")
            return redirect('login')

    return render(request, 'accounts/login.html')


@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, "You are logged out.")
    return redirect('login')


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulations! Your account is activated successfully.')
        return redirect('login')

    messages.error(request, 'Invalid activation link or expired. Please try again!')
    return redirect('register')


@login_required(login_url='login')
def dashboard(request):
    return render(request, "accounts/dashboard.html")


def forgotPassword(request):
    if request.method == "POST":
        email = request.POST["email"]
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email=email)

            ##Sending reset password link to email
            currnet_site = get_current_site(request)
            mail_subject = "Reset Password"
            message = render_to_string('accounts/reset_email_password.html', {
                "user": user,
                "domain": currnet_site,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": default_token_generator.make_token(user) 
            })

            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            # messages.success(request, f"Thank you for registering with us. We have sent you a verification email to your {to_email} email address. Please verify it.")
            # return redirect('/accounts/login/?command=reset_password&email='+to_email)
            messages.success(request, f"password reset email has been sent to your {to_email} email address.")
            return redirect('login')

        else:
            messages.error(request, "email does not exist.")
            return redirect('forgotPassword')

    return render(request, "accounts/forgotPassword.html")


def reset_password_validate(request, uidb64, token):
    return HttpResponse('okk')