from django.urls import path
from . import views

app_name = 'news'
urlpatterns = [
    # path('admin/', admin.site.urls),
    path('',views.IndexView.as_view(),name='index'),
    path('detail/<int:news_id>/',views.NewsDetailView.as_view(),name='news_detail'),
    path('banner/',views.NewsBannerView.as_view(),name='news_banner'),
    path('search/',views.SearchView(),name='search'),
    path('news/',views.NewsList.as_view(),name='news_list'),


]