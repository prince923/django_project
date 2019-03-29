from django.urls import path,include
from . import views

app_name = 'admin'

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', views.AdminIndex.as_view(),name='index'),

]
