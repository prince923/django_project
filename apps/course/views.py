from django.shortcuts import render
from django.views import View
# Create your views here.

class Course(View):
    def get(self,request):
        return render(request,'course/course.html')

    def post(self,request):
        pass


class CourseDetail (View):
    def get(self,request):
        return render(request,'course/course_detail.html')

    def post(self,request):
        pass

