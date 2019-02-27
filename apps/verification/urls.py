from django.urls import path
from  . import views


app_name = 'verification'
urlpatterns = [
    # path('admin/', admin.site.urls),
    path('image_codes/<uuid:image_code_id>/',views.ImageVerification.as_view(),name='image_verification'),
]