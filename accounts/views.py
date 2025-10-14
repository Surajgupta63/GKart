from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrationForm, UserForm, UserProfileForm
from .models import Account, UserProfile
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from carts.models import Cart, CartItem
from carts.views import _cart_id
import requests
from orders.models import Order, OrderProduct

from core.utils import log_event

## Email Verification libraries
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

# Create your views here.

def send_verification_email(request, user, to_email):
    ## Sending Verification Link To Email
    current_site = get_current_site(request)
    mail_subject = "Please Activate Your Account"
    message = render_to_string('accounts/email_verification.html', {
        "user": user,
        "domain": current_site,
        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
        "token": default_token_generator.make_token(user) 
    })
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()

def register(request):
    if request.method == "POST":
        email = request.POST.get('email')
        inactive_user = Account.objects.filter(email=email, is_active=False).first()
        if inactive_user:
            to_email = email
            send_verification_email(request, inactive_user, to_email)
            messages.info(request, "You already registered but haven’t verified your email. We’ve sent a new confirmation link.")
            return redirect('/accounts/login/?command=verification&email='+to_email)
        
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

            ## Creating User Profile
            user_profile = UserProfile()
            user_profile.user_id = user.id
            user_profile.profile_picture = "default/default_user.png"
            user_profile.save()

            ## Sending Verification Link To Email
            to_mail = email
            send_verification_email(request, user, to_mail)
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
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)

                    ##Bring all the variations from cart by cart id
                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))
                    
                    ##Get cart item from the user to acces his all product variations
                    cart_item = CartItem.objects.filter(user=user)
                    ex_var_list = []
                    id = []
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation))
                        id.append(item.id)
                    
                    for pv in product_variation:
                        if pv in ex_var_list:
                            # increase the cart item quantity
                            index = ex_var_list.index(pv)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()

            except:
                pass
            
            auth.login(request, user)
            messages.success(request, "You are logged in successfuly.")
            log_event(
                event_type="login",
                request=request,
                user=user
            )
            url = request.META.get("HTTP_REFERER")
            try:
                query = requests.utils.urlparse(url).query
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    return redirect(params['next'])
            except:
                return redirect('dashboard')
        else:
            messages.error(request, "invalid email or password.")
            log_event(
                event_type="invalid_login_creds",
                request=request,
                user=user
            )
            return redirect('login')

    return render(request, 'accounts/login.html')

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request, "You are logged out.")
    log_event(
        event_type="logout",
        request=request,
        user=request.user ## optional
    )
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
        log_event(
            event_type="register_link_activated",
            request=request,
            user=user
        )
        return redirect('login')

    messages.error(request, 'Invalid activation link or expired. Please try again!')
    log_event(
        event_type="register_link_expired_or_invalid",
        request=request,
        user=user
    )
    return redirect('register')

@login_required(login_url='login')
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
    total_orders = orders.count()
    try:
        user_profile = UserProfile.objects.get(user_id=request.user.id)
    except UserProfile.DoesNotExist:
        user_profile = None
    context = {
        "total_orders": total_orders,
        "user_profile": user_profile
    }
    return render(request, "accounts/dashboard.html", context)

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
            log_event(
                event_type="forgot_password",
                request=request,
                user=user
            )
            return redirect('login')

        else:
            messages.error(request, "email does not exist.")
            log_event(
                event_type="forgot_password_email_does_not_exist",
                request=request,
                user=user
            )
            return redirect('forgotPassword')

    return render(request, "accounts/forgotPassword.html")

def reset_password_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid

        messages.success(request, 'Link is verified. Please reset your password')
        log_event(
            event_type="reset_password_link_verified",
            request=request,
            user=user
        )
        return redirect('resetPassword')

    messages.error(request, 'Invalid activation link or expired. Please try again!')
    log_event(
        event_type="Invalid activation link or expired. Please try again!",
        request=request,
        user=user
    )
    return redirect('login')

def resetPassword(request):
    if request.method == "POST":
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successfuly.')
            log_event(
                event_type="reset_password_successfully",
                request=request,
                user=user,
                extra={"match": "Password matched!"}
            )
            return redirect('login')
        else:
            messages.error(request, 'Password does not matched!')
            log_event(
                event_type="reset_password_not_successful",
                request=request,
                user=user,
                extra={"match": "Password does not matched!"}
            )
            return redirect('resetPassword')
    
    return render(request, 'accounts/resetPassword.html')

@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.filter(user_id=request.user.id, is_ordered=True).order_by('-created_at')
    context = {
        "orders": orders
    }
    return render(request, 'accounts/my_orders.html', context)

@login_required(login_url='login')
def edit_profile(request):
    try:
        user_profile = get_object_or_404(UserProfile, user=request.user)
    except:
        user_profile = None
    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        user_profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if user_form.is_valid() and user_profile_form.is_valid():
            user_form.save()
            user_profile_form.save()
            messages.success(request, "Your profile has been updated.")
            log_event(
                event_type="profile_updated",
                request=request,
                user=user_profile,
                extra={"description": "Your profile has been updated."}
            )
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        user_profile_form = UserProfileForm(instance=user_profile)
    
    context = {
        "user_form": user_form,
        "user_profile_form": user_profile_form,
        "user_profile": user_profile
    }
    return render(request, 'accounts/edit_profile.html', context)

@login_required(login_url='login')
def change_password(request):
    if request.method == "POST":
        current_password = request.POST["current_password"]
        new_password = request.POST["new_password"]
        confirm_password = request.POST["confirm_password"]

        user = Account.objects.get(username__exact=request.user.username)

        if new_password == confirm_password:
            if user.check_password(current_password):
                user.set_password(new_password)
                user.save()
                # auth.logout()
                messages.success(request, "Your password has been changed.")
                return redirect('change_password')
            else:
                messages.error(request, "Please provide valid current password")
                return redirect('change_password')
            
        else:
            messages.error(request, "password does not matched.")
            return redirect('change_password')

    return render(request, 'accounts/change_password.html')


@login_required(login_url='login')
def order_detail(request, order_id):
    order = Order.objects.get(order_number=order_id)
    order_detail = OrderProduct.objects.filter(order=order)
    # order_detail = OrderProduct.objects.filter(order__order_number=order_id)

    subtotal = 0
    for i in order_detail:
        subtotal += i.product_price * i.quantity

    context = {
        "order_detail": order_detail,
        "order": order,
        "subtotal": subtotal
    }

    return render(request, 'accounts/order_detail.html', context)
