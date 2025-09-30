from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import resolve_url
from allauth.account.utils import user_email, user_username
from accounts.models import UserProfile

class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=False)

        # Normal signup → inactive until email confirmation
        if not hasattr(user, 'socialaccount_set') or not user.socialaccount_set.exists():
            user.is_active = False

        if commit:
            user.save()
        return user

    def get_login_redirect_url(self, request):
        return resolve_url('dashboard')  # Redirect after login
    

    def send_confirmation_mail(self, request, emailconfirmation, signup):
        user = emailconfirmation.email_address.user
        # Only send confirmation email for normal signup
        if not hasattr(user, "socialaccount_set") or not user.socialaccount_set.exists():
            super().send_confirmation_mail(request, emailconfirmation, signup)
        # Social signup → skip sending mail


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):

    def is_open_for_signup(self, request, sociallogin):
        # Allow social signup only if the email doesn't already exist.
        # If email exists, link to existing user automatically.
        email = user_email(sociallogin.user)
        if email:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                existing_user = User.objects.get(email=email)
                # Link social account to existing user
                sociallogin.connect(request, existing_user)
                return False  # Skip signup form
            except User.DoesNotExist:
                return True  # New email → allow signup
        return True

    def save_user(self, request, sociallogin, form=None):
        # Save the user; mark as active and create user profile if new.
        user = sociallogin.user
        # If user is new, set basic info and active
        if not user.pk:
            user.is_active = True
            user_username(user, sociallogin.account.extra_data.get('name', ''))
            user_email(user, sociallogin.account.extra_data.get('email', ''))
            user.save()

            # Create UserProfile for new user
            user_profile = UserProfile(user_id=user.id, profile_picture="default/default_user.png")
            user_profile.save()

        # Prevent Allauth from sending verification email
        sociallogin.email_addresses = []
        return user
