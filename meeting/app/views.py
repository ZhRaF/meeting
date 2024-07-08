from django.shortcuts import render
from django.contrib import messages
from django.forms import ValidationError
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.decorators import login_required
from django.utils.encoding import force_bytes , force_str
from django.utils.http import urlsafe_base64_decode ,urlsafe_base64_encode
from django.conf import settings
from .tokens import generate_token 
from django.core.mail import send_mail ,EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from .models import *



def main_view(request):
    context={}
    return render(request,'app/main.html',context=context)



def signup(request):
    """
    Handle user signup, including validation, creation, and email confirmation.

    Parameters:
    request (HttpRequest): The request object.

    Returns:
    HttpResponse: Redirect to the signin page or render the signup template.
    """
    if request.method == "POST":
        username = request.POST.get("username")
        fname = request.POST.get("fname")
        lname = request.POST.get("lname")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        try:
            validate_password(password1)
        except ValidationError as e:
            for error in e.messages:
                messages.error(request, error)
            return redirect('signup')

        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists')
            return redirect('signup')

        user = User.objects.create_user(username, email, password1)
        user.first_name = fname
        user.last_name = lname
        user.is_active = False
        user.save()

        messages.success(request, 'Your account has been successfully created. We have sent you a confirmation email.')

        # Welcome email
        subject = 'Welcome to meeting app'
        message1 = f'Hello {username},\nWelcome to meeting app'
        from_email = settings.EMAIL_HOST_USER
        to_list = [user.email]
        send_mail(subject, message1, from_email, to_list, fail_silently=True)

        # Confirmation email
        current_site = get_current_site(request)
        email_subject = 'Confirm your email'
        message2 = render_to_string('authentication/emailConfirmation.html', {
            'name': user.username,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': generate_token.make_token(user),
        })
        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            to=[user.email]
        )
        email.send()

        return redirect('signin')

    return render(request, 'authentication/signup.html')


def activate(request, uidb64, token):
    """
    Activate a user's account using the activation link.

    Parameters:
    request (HttpRequest): The request object.
    uidb64 (str): Base64 encoded user ID.
    token (str): Activation token.

    Returns:
    HttpResponse: Redirect to the signin page or raise Http404 if invalid.
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
        raise Http404("Invalid activation link")

    if user is not None and generate_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, "Your account has been activated!")
        return redirect('signin')
    else:
        raise ValidationError("Invalid activation link.")

def signin(request):
    """
    Handle user login and redirect based on user type.

    Parameters:
    request (HttpRequest): The request object.

    Returns:
    HttpResponse: Render the signin template or redirect to appropriate page after login.
    """
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            messages.success(request, "You have successfully logged in.")
            return redirect("lobby")
        else:
            if not User.objects.filter(username=username).exists():
                messages.error(request, "Incorrect username")
            else:
                messages.error(request, "Incorrect password")

    return render(request, "authentication/signin.html")

@login_required
def signout(request):
    """
    Handle user logout and redirect to the signin page.

    Parameters:
    request (HttpRequest): The request object.

    Returns:
    HttpResponse: Redirect to the signin page.
    """
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect("signin")

def room(request):
    return render(request,'app/room.html')



def lobby(request):
    return render(request,'app/lobby.html')