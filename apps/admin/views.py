from django.shortcuts import render

# Create your views here.
from django.views import View


class AdminIndex(View):
    def get(self,request):
        return render(request,'admin/index.html')