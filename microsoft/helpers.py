import random
import string

import msal
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

from cryptography import x509
from cryptography.hazmat.backends import default_backend
import jwt

User = get_user_model()
graph_url = "https://graph.microsoft.com/v1.0"

def validate_email(email):
    return "@" in email and email.split("@")[1] in settings.VALID_EMAIL_DOMAIN

def get_user(token):
    # Send GET to /me
    user = requests.get('{0}/me'.format(graph_url),
    headers={'Authorization': 'Bearer {0}'.format(token)})
    print(user.json())
    return user.json()
    # with open('static/certificate.crt', 'rb') as cert_file:
    #     cert_data = cert_file.read()
    #     cert = x509.load_der_x509_certificate(cert_data, default_backend())
    #     public_key = cert.public_key()
    #     # public_key_pem = public_key.public_bytes(encoding=serialization.Encoding.PEM,
    #     #                                          format=serialization.PublicFormat.SubjectPublicKeyInfo)
    #     # public_key_pem.decode('utf-8')
    #     decoded_token = jwt.decode(token, public_key, algorithms=['RS256'])
    #     return decoded_token


def get_django_user(email, create_new=True):
    # if not validate_email(email=email):
    #     return
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        if not create_new:
            return
        random_password = "".join(random.choice(string.ascii_letters) for i in range(32))
        user = User(username=email, email=email, password=make_password(random_password))
        user.is_staff = True
        user.save()
    return user

def get_msal_app(cache=None):
    # Initialize the MSAL confidential client
    auth_app = msal.ConfidentialClientApplication(
        settings.MICROSOFT_AUTH_CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{settings.MICROSOFT_AUTH_TENANT_ID}",
        client_credential=settings.MICROSOFT_AUTH_CLIENT_SECRET,
        token_cache=cache,
    )
    return auth_app

def get_sign_in_flow():
    auth_app = get_msal_app()
    return auth_app.initiate_auth_code_flow(settings.MICROSOFT_AUTH_SCOPES, redirect_uri=settings.MICROSOFT_AUTH_REDIRECT_URI)


def get_logout_url():
    return f"https://login.microsoftonline.com/{settings.MICROSOFT_AUTH_TENANT_ID}" + "/oauth2/v2.0/logout" + "?post_logout_redirect_uri=" + settings.LOGOUT_URI


def load_cache(request):
    cache = msal.SerializableTokenCache()
    if request.session.get("token_cache"):
        cache.deserialize(request.session["token_cache"])
    return cache

def save_cache(request, cache):
    if cache.has_state_changed:
        request.session["token_cache"] = cache.serialize()

def get_token_from_code(request):
    cache = load_cache(request)
    auth_app = get_msal_app(cache)
    flow = request.session.pop("auth_flow", {})
    print(cache)
    result = auth_app.acquire_token_by_auth_code_flow(flow, request.GET)
    save_cache(request, cache)
    return result
