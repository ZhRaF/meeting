from django.urls import path
from . import views

urlpatterns=[
    path('room',views.room,name='room'),
    path('signup',views.signup,name='signup'),
    path('',views.signin,name='signin'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),  
    path('signout',views.signout,name='signout'),
]