from django.shortcuts import render
from django.views import  View
# Create your views here.


class IndexView (View):
    def get(self,request):
        return render(request,'news/index.html')

    def post(self,request):
        pass


class NewsDetail(View):
    def get(self,request):
        return render(request,'news/news_detail.html')

    def post(self,request):
        pass


class NewsSearch (View):
    def get(self,request):
        return render(request,'news/search.html')

    def post(self,request):
        pass




