from django.urls import path,include
from . import views

app_name = 'admin'

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', views.AdminIndex.as_view(),name='index'),
    path('tags/',views.TagManageView.as_view(),name='tags'),
    path('tags/<int:tag_id>/',views.TagEdit.as_view(),name='tags_edit'),
    path('hotnews/',views.HotNewsManageView.as_view(),name='hot_news'),
    path('hotnews/<int:hotnews_id>/',views.HotNewsEditView.as_view(),name='hot_news_edit'),
    path('addhotnews/',views.AddHotNewsView.as_view(),name='add_hot_news'),
    path('tags/<int:tag_id>/news/',views.NewsBYTag.as_view(),name='news_by_tag'),
    path('news/',views.NewsManageView.as_view(),name='news_manage'),
    path('news/<int:news_id>/',views.NewsEditView.as_view(),name='news_edit'),
    path('news/pub/',views.NewsPubView.as_view(),name='news_pub'),

]
