import json
import random
import time
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
from agora_token_builder import RtcTokenBuilder
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt



def getToken(request):
    print('whyyyyyyyyyyyyyyyyyy')

    appId = "ce47399fde4b46bfad2c007471491aa9"
    appCertificate = "b3d8904d8f644f88af87328699ea7504"

    channelName = request.GET.get('channel')

    if not channelName:
      return JsonResponse({'error': 'Channel name is required'}, status=400)

    uid = random.randint(1, 230)

    expirationTimeInSeconds = 3600 * 24
    currentTimeStamp = int(time.time())
    privilegeExpiredTs = currentTimeStamp + expirationTimeInSeconds
    role = 1

    token = RtcTokenBuilder.buildTokenWithUid(appId, appCertificate, channelName, uid, role, privilegeExpiredTs)
    
    print('sending token')
    return JsonResponse({'token': token, 'uid': uid}, safe=False)

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

@login_required
def room(request):
    return render(request,'app/room.html')


@login_required
def lobby(request):
    username=request.user.username
    print(username)
    return render(request,'app/lobby.html',{'username':username})


@csrf_exempt
def createMember(request):
    data = json.loads(request.body)
    username = User.objects.get(username=data['username'])
    member, created = RoomMember.objects.get_or_create(
        user=username,
        uid=data['UID'],
        room_name=data['room_name']
    )

    return JsonResponse({'username':data['username']}, safe=False)


def getMember(request):
    uid = request.GET.get('UID')
    room_name = request.GET.get('room_name')
    
    member = RoomMember.objects.get(
        uid=uid,
        room_name=room_name,
    )
    username = member.user.username
    print(username)
    return JsonResponse({'username':username}, safe=False)

@csrf_exempt
def deleteMember(request):
    data = json.loads(request.body)
    user=User.objects.get(username=data['username'])
    print(f"user is{user}")
    member = RoomMember.objects.get(
        uid = data['UID'],
        user=user,
        room_name=data['room_name']
    )
    print(f"member is{member}")


    member.delete()
    return JsonResponse('Member deleted', safe=False)
