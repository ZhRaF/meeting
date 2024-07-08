from django.urls import path
from . import views

urlpatterns=[
    # path('main',views.main_view,name='main'),
    path('signup',views.signup,name='signup'),
    path('',views.signin,name='signin'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),  
    path('signout',views.signout,name='signout'),
]