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
    path('news/images/', views.UploadImage.as_view(), name='upload_image'),
    path('token/', views.UploadToken.as_view(), name='upload_token'),  # 七牛云上传图片需要调用token
    path('banners/',views.BannerManagerView.as_view(), name='banner_manager'),
    path('banners/<int:banner_id>/',views.BannerEditView.as_view(), name='banner_edit'),
    path('banners/add/',views.BannerAddView.as_view(), name='banner_add'),
    path('docs/',views.DocManagerView.as_view(), name='doc_manager'),
    path('docs/<int:doc_id>/',views.DocEditView.as_view(), name='doc_edit'),
    path('docs/files/',views.DocUploadView.as_view(), name='doc_file_upload'),
    path('docs/pub/',views.DocPubView.as_view(), name='doc_pub'),
    path('courses/',views.CourseManageView.as_view(), name='courses_manage'),
    path('courses/<int:course_id>/',views.CourseEditView.as_view(), name='courses_edit'),
    path('courses/pub/',views.CoursePubView.as_view(), name='courses_pub'),
    path('groups/add/',views.GroupAddView.as_view(), name='groups_add'),
    path('groups/',views.GroupManageView.as_view(), name='groups_manage'),
    path('groups/<int:group_id>/',views.GroupEditView.as_view(), name='groups_edit'),
    path('users/',views.UserManageView.as_view(),name='user_manage'),
    path('users/<int:user_id>/',views.UserEditView.as_view(),name='user_edit'),
]
