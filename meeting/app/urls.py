from django.urls import path
from . import views

urlpatterns=[

    path('signup',views.signup,name='signup'),
    path('',views.signin,name='signin'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),  
    path('signout',views.signout,name='signout'),
    path('room',views.room,name='room'),
    path('lobby',views.lobby,name='lobby'),
    path('getToken/', views.getToken,name='getToken'),
    path('createMember/', views.createMember,name='createMember'),
    path('getMember/', views.getMember,name='getMember'),
    path('deleteMember/', views.deleteMember,name='deleteMember'),
]