from django.urls import path,include
from . import views

app_name = 'doc'

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('doc-download/',views.DocDownload.as_view(),name='doc_download'),

]
