from django.urls import path,include
from . import views

app_name = 'doc'

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('doc-index/',views.DocIndex.as_view(),name='doc_index'),
    path('doc-download/<int:doc_id>/',views.down_doc,name='doc_download'),

]
