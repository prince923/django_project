from django.shortcuts import render
from django.views import View
# Create your views here.

class LoginView(View):
    def get (self,request):
        return render(request,'user/login.html')

    def post(self,request):
        pass


class RegisterView(View):
    def get(self, request):
        return render(request, 'user/register.html')

    def post(self, request):
        pass
