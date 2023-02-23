from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponseForbidden
from rest_framework import generics
from .helpers import get_sign_in_flow, get_logout_url, get_token_from_code, get_user, get_django_user
from django.contrib.auth import login, logout
from django.conf import settings
from .serializers import RegisterSerializer

# Create your views here.


class ToAuthRedirect(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    def get(self, request, *args,  **kwargs):
        flow = get_sign_in_flow()
        try:
            request.session['auth_flow'] = flow
        except Exception as e:
            print(e)
        return HttpResponseRedirect(flow['auth_uri'])
    

class Logout(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    def post(self, request, *args,  **kwargs):
        logout(request)
        return HttpResponseRedirect(get_logout_url())



class Callback(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    def get(self, request, *args,  **kwargs):
        result = get_token_from_code(request)
        print(f"Result {result}")
        ms_user = get_user(result['access_token'])
        user = get_django_user(email=ms_user['mail'])
        print(ms_user["mail"])
        print(user)
        if user:
            login(request, user)
        else:
            return HttpResponseForbidden("Invalid email for this app.")
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL or "/admin")