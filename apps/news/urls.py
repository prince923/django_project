from django.urls import path,include
from . import views

app_name = 'news'
urlpatterns = [
    # path('admin/', admin.site.urls),
    path('',views.IndexView.as_view(),name='index'),
    path('detail/',views.NewsDetail.as_view(),name='news_detail'),
    path('search/',views.NewsSearch.as_view(),name='news_search'),
    path('news/',views.NewsList.as_view(),name='news_list'),


]