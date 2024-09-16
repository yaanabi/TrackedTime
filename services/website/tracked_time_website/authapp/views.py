from django.shortcuts import render
from django.views.generic import CreateView
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

from .serializers import RegisterSerializer
from .forms import RegisterForm
# Create your views here.


class RegisterViewAPI(CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class LoginUserView(LoginView):
    template_name = 'registration/login.html'
    success_url = reverse_lazy('index')
    prefix = 'login'

class RegisterUserView(CreateView):
    template_name = 'registration/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('login')
    prefix = 'register'
    
