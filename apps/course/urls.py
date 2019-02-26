from django.urls import path,include
from . import views

app_name = 'course'

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('index/',views.Course.as_view(),name='course'),
    path('course-detail/',views.CourseDetail.as_view(),name='course_detail'),

]
