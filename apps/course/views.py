from django.http import Http404
from django.shortcuts import render
from django.views import View
from .models import CourseModel
from django.contrib.auth.mixins import LoginRequiredMixin


# Create your views here.

class Course(LoginRequiredMixin, View):
    def get(self, request: object) -> object:
        courses = CourseModel.objects.select_related('teacher', 'category'). \
            only('teacher__name', 'category__name', 'title', 'cover_url', 'teacher__positional_title'). \
            filter(is_delete=False)
        return render(request, 'course/course.html', locals())


class CourseDetail(LoginRequiredMixin, View):
    def get(self, request: object, course_id: object) -> object:
        course = CourseModel.objects.filter(id=course_id).first()
        if not course:
            return Http404('<h1>课程未找到<h1>')
        else:
            return render(request, 'course/course_detail.html', locals())

    def post(self, request):
        pass
