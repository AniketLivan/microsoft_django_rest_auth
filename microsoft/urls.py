from django.urls import path 
from .views import Logout, Callback, ToAuthRedirect
urlpatterns = [
        path('to-auth-redirect', ToAuthRedirect.as_view()),
        path('signout', Logout.as_view()),
        path('auth-callback/', Callback.as_view()),
]