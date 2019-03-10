from django.urls import path,include,re_path
from  . import views



app_name = 'user'

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('login/',views.LoginView.as_view(),name='login'),
    path('logout/',views.LogoutView.as_view(),name='logout'),
    path('register/',views.RegisterView.as_view(),name='register'),
    re_path('username/(?P<username>\w{5,20})/',views.CheckUsername.as_view(),name='check_username'),
    re_path('mobile/(?P<mobile>1[3-9]\d{9})/',views.CheckMobile.as_view(),name='check_mobile'),
    re_path('sms_codes/',views.SmsCodes.as_view(),name='sms_codes'),

]