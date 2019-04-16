from datetime import datetime
from urllib.parse import urlencode
import json
import logging

from django.views import View
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Count
from django.http import Http404
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.models import Group, Permission

from admin.forms import NewsPubForm, DocPubForm, CoursePubForm
from django_project import settings
from news.models import TagModel, NewsHots, NewsModel, NewsBanner
from doc.models import DocModel
from course.models import CourseModel, TeachModel, CourseCategory

# Create your views here.
from fdfs_client.client import Fdfs_client

from user.models import UserModel
from utils.json_fun import to_json_data
from utils.res_code import Code, error_map
from scripts import paginator_script
import qiniu
from utils.qiniu import qiniu_info
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin

logger = logging.getLogger('django')


class AdminIndex(LoginRequiredMixin, View):
    def get(self, request: object) -> object:
        return render(request, 'admin/index.html')


class TagManageView(PermissionRequiredMixin, View):
    """
    create tag manage View
    route: '/admin/tags/'
    """
    permission_required = ('news.view_tagmodel', 'news.add_tagmodel')
    raise_exception = True  # 如果为 False直接跳转到登录页,如果为True则抛出异常

    def handle_no_permission(self):  # 如果上面抛出异常，就会用此方法来处理
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg='没有操作权限')
        else:
            return super().handle_no_permission()

    def get(self, request: object) -> object:
        # values 作用类似于 only  返回queryset 里嵌套字典,   annotate  分组 ,别名
        tags = TagModel.objects.values('id', 'tag_name').annotate(num_news=Count('newsmodel')). \
            filter(is_delete=False).order_by('-num_news', '-update_time')
        return render(request, 'admin/tags.html', locals())

    def post(self, request):
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.NODATA, errmsg=error_map[Code.NODATA])
        else:
            data_dict = json.loads(json_data.decode('utf8'))
        tag_name = data_dict.get('name')
        if tag_name:
            # 去空格
            tag_name = tag_name.strip()
            tag = TagModel.objects.filter(tag_name=tag_name, is_delete=False).exists()
            if tag:
                return to_json_data(errno=Code.DATAEXIST, errmsg=error_map[Code.DATAEXIST])
            else:
                TagModel.objects.create(tag_name=tag_name)
                return to_json_data(errmsg="标签创建成功")


class TagEdit(PermissionRequiredMixin, View):
    permission_required = ('news.change_tagmodel', 'news.view_tagmodel', 'news.delete_tagmodel')
    raise_exception = True  # 如果为 False直接跳转到登录页,如果为True则抛出异常

    def handle_no_permission(self):  # 如果上面抛出异常，就会用此方法来处理
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg='没有操作权限')
        else:
            return super().handle_no_permission()

    def put(self, request, tag_id):
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.NODATA, errmsg=error_map[Code.NODATA])
        else:
            data_dict = json.loads(json_data.decode('utf8'))
        tag_name = data_dict.get('name')
        tag = TagModel.objects.only('id', 'tag_name').filter(id=tag_id, is_delete=False).first()
        if not tag:
            return to_json_data(errno=Code.NODATA, errmsg="该标签未找到")
        else:
            tag_name = tag_name.strip()
            if tag.tag_name == tag_name:
                return to_json_data(errno=Code.PARAMERR, errmsg="数据未更改")
            else:
                tag.tag_name = tag_name
                # update_fields 优化措施，如果不加 则会先查找所有字段再进行更新，加了就会只更新规定字段
                tag.save(update_fields=['tag_name'])
        return to_json_data(errmsg="标签更新成功")

    def delete(self, request, tag_id):
        tag = TagModel.objects.filter(is_delete=False, id=tag_id).first()
        if not tag:
            return to_json_data(errno=Code.NODATA, errmsg="该标签不存在")
        else:
            tag.is_delete = True
            tag.save(update_fields=['is_delete'])
            return to_json_data(errmsg="标签删除成功")


class HotNewsManageView(PermissionRequiredMixin, View):
    permission_required = 'news.view_newshots'
    raise_exception = True  # 如果为 False直接跳转到登录页,如果为True则抛出异常

    def handle_no_permission(self):  # 如果上面抛出异常，就会用此方法来处理
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg='没有操作权限')
        else:
            return super().handle_no_permission()

    def get(self, request: object) -> object:
        hot_news = NewsHots.objects.select_related('news'). \
                       only('id', 'priority', 'news_id', 'news__title', 'news__tag__tag_name'). \
                       filter(is_delete=False).order_by('priority', '-news__clicks')[:3]
        return render(request, 'admin/hotnews.html', locals())


class HotNewsEditView(PermissionRequiredMixin, View):
    permission_required = ('news.change_newshots', 'news.delete_newshots')
    raise_exception = True  # 如果为 False直接跳转到登录页,如果为True则抛出异常

    def handle_no_permission(self):  # 如果上面抛出异常，就会用此方法来处理
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg='没有操作权限')
        else:
            return super().handle_no_permission()

    def put(self, request, hotnews_id):
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.NODATA, errmsg=error_map[Code.NODATA])
        else:
            dict_data = json.loads(json_data.decode('utf8'))
        hot_new = NewsHots.objects.only('id').filter(is_delete=False, id=hotnews_id).first()
        if hot_new:
            try:
                priority = int(dict_data.get('priority'))
                priority_list = [i for i, _ in NewsHots.PRI_CHOICES]  # 元组解包, a,b = (1,2) a=1 b=2
                if priority in priority_list:
                    origin_priority = hot_new.priority
                    if origin_priority == priority:
                        return to_json_data(errno=Code.DATAEXIST, errmsg="优先级未更改")
                    else:
                        hot_new.priority = priority
                        hot_new.save(update_fields=['priority'])
                        return to_json_data(errmsg="优先级修改成功")
                else:
                    return to_json_data(errno=Code.DATAERR, errmsg="优先级为1-3")
            except Exception as e:
                logger.error('优先级类型错误{}'.format(e))
                return to_json_data(errno=Code.DATAERR, errmsg="优先级类型错误")
        else:
            return to_json_data(errno=Code.NODATA, errmsg="该热门新闻未找到")

    def delete(self, request, hotnews_id):
        hot_new = NewsHots.objects.only('id').filter(is_delete=False, id=hotnews_id).first()
        if hot_new:
            hot_new.is_delete = True
            hot_new.save(update_fields=['is_delete'])
            return to_json_data(errmsg="热门新闻删除成功")
        else:
            return to_json_data(errno=Code.NODATA, errmsg="该热门新闻不存在")


class AddHotNewsView(PermissionRequiredMixin, View):
    permission_required = ('news.add_newshots', 'news.change_newshots', 'news.view_newshots')
    raise_exception = True  # 如果为 False直接跳转到登录页,如果为True则抛出异常

    def handle_no_permission(self):  # 如果上面抛出异常，就会用此方法来处理
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg='没有操作权限')
        else:
            return super().handle_no_permission()

    def get(self, request: object) -> object:
        tags = TagModel.objects.values('id', 'tag_name').annotate(num_news=Count('newsmodel')). \
            filter(is_delete=False).order_by('-num_news', '-update_time')
        priority_dict = {k: v for k, v in NewsHots.PRI_CHOICES}
        return render(request, 'admin/addhotnews.html', locals())

    def post(self, request):
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.NODATA, errmsg=error_map[Code.NODATA])
        else:
            data_dict = json.loads(json_data.decode('utf8'))
            news_id = data_dict.get('news_id')
            priority = data_dict.get('priority')
            if not news_id or not priority:
                return to_json_data(errno=Code.NODATA, errmsg='新闻id和优先级为必填字段')
            try:
                news_id = int(news_id)
            except Exception as e:
                logger.error('新闻id类型错误{}'.format(e))
                return to_json_data(errno=Code.DATAERR, errmsg='新闻id类型错误')
            try:
                priority = int(priority)
            except Exception as e:
                logger.error('优先级类型错误{}'.format(e))
                return to_json_data(errno=Code.DATAERR, errmsg='优先级类型错误')
            priority_list = [i for i, _ in NewsHots.PRI_CHOICES]
            if priority in priority_list:
                news = NewsModel.objects.only('id').filter(is_delete=False, id=news_id).exists()
                if not news:
                    return to_json_data(errno=Code.NODATA, errmsg='新闻不存在')
                # get_or_create 有则查无则加, 返回一个元组 (obj,created)  如果对象存在created 为 True 不存在为False
                news_tuple = NewsHots.objects.get_or_create(news_id=news_id)
                hot_news, is_created = news_tuple
                hot_news.priority = priority
                hot_news.save(update_fields=['priority'])
                return to_json_data(errmsg='热门新闻创建成功')
            else:
                return to_json_data(errno=Code.DATAERR, errmsg='优先级范围错误')


class NewsBYTag(View):
    def get(self, request: object, tag_id: object) -> object:
        news = list(NewsModel.objects.values('id', 'title').filter(tag_id=tag_id, is_delete=False))
        data = {'news': news}
        return to_json_data(data=data)


class NewsManageView(PermissionRequiredMixin, View):
    permission_required = (
        'news.view_newsmodel', 'news.add_newsmodel')
    raise_exception = True  # 如果为 False直接跳转到登录页,如果为True则抛出异常

    def handle_no_permission(self):  # 如果上面抛出异常，就会用此方法来处理
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg='没有操作权限')
        else:
            return super().handle_no_permission()

    def get(self, request):
        # 获取搜索参数
        tags = TagModel.objects.only('id', 'tag_name').filter(is_delete=False)
        start_time = request.GET.get('start_time', '')
        end_time = request.GET.get('end_time', '')
        title = request.GET.get('title', '')
        author_name = request.GET.get('author_name', '')
        tag_id = request.GET.get('tag_id', 0)
        page = request.GET.get('page', 1)
        try:
            start_time = datetime.strptime(start_time, '%Y%m%d') if start_time else ''
            end_time = datetime.strptime(end_time, '%Y%m%d') if end_time else ''
        except Exception as e:
            logger.error('时间格式有误{}'.format(e))
            start_time = end_time = ''
        try:
            tag_id = int(tag_id)
        except Exception as e:
            logger.error('tag_id 错误 {}'.format(e))
            tag_id = 0
        try:
            page = int(page)
        except Exception as e:
            logger.error('page 类型错误{}'.format(e))
            page = 1
        news = NewsModel.objects.select_related('author', 'tag'). \
            only('id', 'title', 'digest', 'author__username', 'tag__tag_name', 'update_time').filter(is_delete=False)
        # 判断时间
        if start_time and not end_time:
            news = news.filter(update_time__lte=start_time)
        if end_time and not start_time:
            news = news.filter(update_time__gte=end_time)
        if start_time and end_time:
            news = news.filter(update_time__range=(start_time, end_time))
        if title:
            news = news.filter(title__icontains=title)
        if author_name:
            news = news.filter(author__username__icontains=author_name)
        news = news.filter(tag_id=tag_id) or news
        paginator = Paginator(news, 8)
        try:
            news_info = paginator.page(page)
        except EmptyPage:
            logger.error('page大于总页数')
            news_info = paginator.page(paginator.num_pages)
        paginator_data = paginator_script.get_paginator_data(paginator, news_info)
        start_time = start_time.strftime('%Y/%m/%d') if start_time else ''
        end_time = end_time.strftime('%Y/%m/%d') if end_time else ''
        context = {
            'news_info': news_info,
            'tags': tags,
            'paginator': paginator,
            'start_time': start_time,
            "end_time": end_time,
            "title": title,
            "author_name": author_name,
            "tag_id": tag_id,
            "other_param": urlencode({
                "start_time": start_time,
                "end_time": end_time,
                "title": title,
                "author_name": author_name,
                "tag_id": tag_id,
            })
        }
        context.update(paginator_data)
        return render(request, 'admin/news_manage.html', context=context)


class NewsEditView(PermissionRequiredMixin, View):
    permission_required = (
        'news.view_newsmodel', 'news.change_newsmodel', 'news.delete_newsmodel', 'news.add_newsmodel')
    raise_exception = True  # 如果为 False直接跳转到登录页,如果为True则抛出异常

    def handle_no_permission(self):  # 如果上面抛出异常，就会用此方法来处理
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg='没有操作权限')
        else:
            return super().handle_no_permission()

    def get(self, request: object, news_id: object) -> object:
        news = NewsModel.objects.filter(is_delete=False, id=news_id).first()
        if not news:
            return Http404('新闻不存在')
        else:
            tags = TagModel.objects.only('id', 'tag_name').filter(is_delete=False)
        context = {
            'news': news,
            'tags': tags
        }
        return render(request, 'admin/news_pub.html', context=context)

    def put(self, request, news_id):
        news = NewsModel.objects.only('id').filter(is_delete=False, id=news_id).first()
        if not news:
            return Http404('新闻不存在')
        else:
            json_data = request.body
            if not json_data:
                return to_json_data(errno=Code.NODATA, errmsg=error_map[Code.NODATA])
            else:
                dict_data = json.loads(json_data.decode('utf8'))
            forms = NewsPubForm(data=dict_data)
            if forms.is_valid():
                news.title = forms.cleaned_data.get('title')
                news.digest = forms.cleaned_data.get('digest')
                news.image_url = forms.cleaned_data.get('image_url')
                news.content = forms.cleaned_data.get('content')
                news.tag_id = forms.cleaned_data.get('tag')
                news.save()
                return to_json_data(errmsg="文章更新成功")
            else:
                err_msg_list = []
                for item in forms.errors.get_json_data().values():
                    err_msg_list.append(item[0].get('message'))
                    # print(item[0].get('message'))   # for test
                err_msg_str = '/'.join(err_msg_list)  # 拼接错误信息为一个字符串
                return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_str)

    def delete(self, request, news_id):
        news = NewsModel.objects.filter(is_delete=False, id=news_id).first()
        if not news:
            return Http404('新闻不存在')
        else:
            news.is_delete = True
            news.save(update_fields=['is_delete'])
            return to_json_data(errmsg='文章删除成功')


class NewsPubView(PermissionRequiredMixin, View):
    permission_required = (
        'news.view_newsmodel', 'news.change_newsmodel', 'news.delete_newsmodel', 'news.add_newsmodel')
    raise_exception = True  # 如果为 False直接跳转到登录页,如果为True则抛出异常

    def handle_no_permission(self):  # 如果上面抛出异常，就会用此方法来处理
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg='没有操作权限')
        else:
            return super().handle_no_permission()

    def get(self, request):
        tags = TagModel.objects.only('id', 'tag_name').filter(is_delete=False)
        return render(request, 'admin/news_pub.html', locals())

    def post(self, request):
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.NODATA, errmsg=error_map[Code.NODATA])
        else:
            dict_data = json.loads(json_data.decode('utf8'))
        forms = NewsPubForm(data=dict_data)
        if forms.is_valid():
            news_instance = forms.save(commit=False)
            news_instance.author = request.user
            news_instance.save()
            return to_json_data(errmsg="文章发布成功")
        else:
            err_msg_list = []
            for item in forms.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
                # print(item[0].get('message'))   # for test
            err_msg_str = '/'.join(err_msg_list)  # 拼接错误信息为一个字符串
            return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_str)


class UploadImage(LoginRequiredMixin, View):
    """
    upload image to FastDfs
    1. 获取图片并判断图片是否存在
    2. 判断图片格式
    3. 判断是否有拓展名
    4. 判断是否上传异常
    """

    def post(self, request):
        image_file = request.FILES.get('image_file')
        if not image_file:
            return to_json_data(errno=Code.NODATA, errmsg="没有图片文件")
        else:
            if image_file.content_type not in ('image/jpeg', 'image/png', 'image/gif'):
                return to_json_data(errno=Code.DATAERR, errmsg="不能上传非图片文件")
            else:
                image_name = image_file.name
                try:
                    ex_name = image_name.split('.')[-1]
                except Exception as e:
                    logger.error('文件拓展名异常 {}'.format(e))
                    ex_name = 'jpg'
                try:
                    FDFS_Client = Fdfs_client(settings.FDFS_CLIENT_CONF_FILE)
                    upload_res = FDFS_Client.upload_by_buffer(image_file.read(), ex_name)
                except Exception as e:
                    logger.error('文件上传异常{}'.format(e))
                    return to_json_data(errno=Code.DATAERR, errmsg="文件上传异常")
                else:
                    res = upload_res.get('Status')
                    if res != 'Upload successed.':
                        return to_json_data(errno=Code.DATAERR, errmsg="文件上传失败")
                    else:
                        image_name = upload_res.get('Remote file_id')
                        image_url = settings.FAST_DFS_TRACKER_DOMAIN + image_name
                        return to_json_data(errmsg="图片上传成功", data={'image_url': image_url})


class UploadToken(LoginRequiredMixin, View):
    """
    upload image to qi_niu
    :return token
    """

    def get(self, request: object) -> object:
        access_key = qiniu_info.QI_NIU_ACCESS_KEY
        secret_key = qiniu_info.QI_NIU_SECRET_KEY
        bucket_name = qiniu_info.QI_NIU_BUCKET_NAME
        q = qiniu.Auth(access_key, secret_key)
        token = q.upload_token(bucket_name)
        return JsonResponse({'uptoken': token})


class BannerManagerView(PermissionRequiredMixin, View):
    permission_required = 'news.view_newsbanner'
    raise_exception = True  # 如果为 False直接跳转到登录页,如果为True则抛出异常

    def handle_no_permission(self):  # 如果上面抛出异常，就会用此方法来处理
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg='没有操作权限')
        else:
            return super().handle_no_permission()

    def get(self, request):
        priority_dict = dict(NewsBanner.PRI_CHOICES)
        banners = NewsBanner.objects.only('id', 'priority', 'image_url').filter(is_delete=False)
        return render(request, 'admin/news_banner.html', locals())


class BannerEditView(PermissionRequiredMixin, View):
    permission_required = (
        'news.view_newsbanner', 'news.change_newsbanner', 'news.add_newsbanner', 'news.delete_newsbanner')
    raise_exception = True  # 如果为 False直接跳转到登录页,如果为True则抛出异常

    def handle_no_permission(self):  # 如果上面抛出异常，就会用此方法来处理
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg='没有操作权限')
        else:
            return super().handle_no_permission()

    def put(self, request, banner_id):
        banner = NewsBanner.objects.only('id').filter(is_delete=False, id=banner_id).first()
        if not banner:
            return to_json_data(errno=Code.NODATA, errmsg="轮播图未找到")
        else:
            json_data = request.body
            if not json_data:
                return to_json_data(errno=Code.NODATA, errmsg="没有数据")
            else:
                dict_data = json.loads(json_data.decode('utf8'))
            try:
                priority = int(dict_data.get('priority'))
            except Exception as e:
                logger.error('优先级错误 {}'.format(e))
                return to_json_data(errno=Code.DATAERR, errmsg="优先级错误")
            if priority not in [i for i, _ in NewsBanner.PRI_CHOICES]:
                return to_json_data(errno=Code.DATAERR, errmsg="优先级范围错误")
            image_url = dict_data.get('image_url')
            if not image_url:
                return to_json_data(errno=Code.NODATA, errmsg="轮播图url不能为空")
            if image_url == banner.image_url and priority == banner.priority:
                return to_json_data(errno=Code.DATAEXIST, errmsg="数据未改变")
            banner.image_url = image_url
            banner.priority = priority
            banner.save(update_fields=['image_url', 'priority'])
            return to_json_data(errmsg="轮播图更新成功")

    def delete(self, request, banner_id):
        banner = NewsBanner.objects.only('id').filter(is_delete=False, id=banner_id).first()
        if not banner:
            return to_json_data(errno=Code.NODATA, errmsg="轮播图未找到")
        else:
            banner.is_delete = True
            banner.save(update_fields=['is_delete'])
            return to_json_data(errmsg="轮播图删除成功")


class BannerAddView(PermissionRequiredMixin, View):
    permission_required = (
        'news.view_newsbanner', 'news.change_newsbanner', 'news.add_newsbanner', 'news.delete_newsbanner')
    raise_exception = True  # 如果为 False直接跳转到登录页,如果为True则抛出异常

    def handle_no_permission(self):  # 如果上面抛出异常，就会用此方法来处理
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg='没有操作权限')
        else:
            return super().handle_no_permission()

    def get(self, request):
        tags = TagModel.objects.values('id', 'tag_name').annotate(news_count=Count('newsmodel')) \
            .filter(is_delete=False).order_by('-news_count', '-update_time')
        priority_dict = dict(NewsBanner.PRI_CHOICES)
        return render(request, 'admin/news_banner_add.html', locals())

    def post(self, request):
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.NODATA, errmsg="没有数据")
        else:
            dict_data = json.loads(json_data.decode('utf8'))
        try:
            news_id = int(dict_data.get('news_id'))
        except Exception as e:
            logger.error('news_id 错误 {}'.format(e))
            return to_json_data(errno=Code.DATAERR, errmsg="参数错误")
        else:
            news = NewsModel.objects.only('id').filter(id=news_id, is_delete=False).exists()
            if not news:
                return to_json_data(errno=Code.DATAERR, errmsg="新闻不存在")
        try:
            priority = int(dict_data.get('priority'))
        except Exception as e:
            logger.error('priority  错误 {}'.format(e))
            return to_json_data(errno=Code.DATAERR, errmsg="参数错误")
        else:
            if priority not in [i for i, _ in NewsBanner.PRI_CHOICES]:
                return to_json_data(errno=Code.DATAERR, errmsg="优先级范围错误")
        image_url = dict_data.get('image_url')
        if not image_url:
            return to_json_data(errno=Code.NODATA, errmsg="图片url不能为空")
        banner_tuple = NewsBanner.objects.get_or_create(priority=priority, image_url=image_url, news_id=news_id)
        # is_created 如果有 False   如果没有就为True
        banner, is_created = banner_tuple
        if not is_created:
            return to_json_data(errno=Code.DATAEXIST, errmsg="轮播图已存在")
        else:
            banner.priority = priority
            banner.image_url = image_url
            banner.news_id = news_id
            banner.save(update_fields=['priority', 'image_url', 'news_id'])
            return to_json_data(errmsg="轮播图创建成功")


class DocManagerView(PermissionRequiredMixin, View):
    permission_required = 'doc.view_docmode'
    raise_exception = True  # 如果为 False直接跳转到登录页,如果为True则抛出异常

    def handle_no_permission(self):  # 如果上面抛出异常，就会用此方法来处理
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg='没有操作权限')
        else:
            return super().handle_no_permission()

    def get(self, request):
        docs = DocModel.objects.only('id', 'title', 'update_time').filter(is_delete=False)
        return render(request, 'admin/doc_manage.html', locals())


class DocEditView(PermissionRequiredMixin, View):
    permission_required = (
        'doc.view_docmodel', 'doc.delete_docmodel', 'doc.add_newsbanner', 'doc.change_docmodel')
    raise_exception = True  # 如果为 False直接跳转到登录页,如果为True则抛出异常

    def handle_no_permission(self):  # 如果上面抛出异常，就会用此方法来处理
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg='没有操作权限')
        else:
            return super().handle_no_permission()

    def get(self, request, doc_id):
        doc = DocModel.objects.defer('update_time', 'create_time', 'is_delete'). \
            filter(id=doc_id, is_delete=False).first()
        if not doc:
            return to_json_data(errno=Code.NODATA, errmsg="文档不存在")
        return render(request, 'admin/docs_pub.html', locals())

    def delete(self, request, doc_id):
        doc = DocModel.objects.only('id').filter(is_delete=False, id=doc_id).first()
        if not doc:
            return to_json_data(errno=Code.NODATA, errmsg="文档不存在")
        else:
            doc.is_delete = True
            doc.save(update_fields=['is_delete'])
            return to_json_data(errmsg="文档删除成功")

    def put(self, request, doc_id):
        doc = DocModel.objects.only('id').filter(is_delete=False, id=doc_id).first()
        if not doc:
            return to_json_data(errno=Code.NODATA, errmsg="文档不存在")
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.NODATA, errmsg="没有数据")
        else:
            dict_data = json.loads(json_data.decode('utf8'))
        forms = DocPubForm(data=dict_data)
        if forms.is_valid():
            doc.file_url = forms.cleaned_data.get('file_url')
            doc.image_url = forms.cleaned_data.get('image_url')
            doc.title = forms.cleaned_data.get('title')
            doc.desc = forms.cleaned_data.get('desc')
            doc.save(update_fields=['file_url', 'image_url', 'title', 'desc'])
            return to_json_data(errmsg="文档更新成功")
        else:
            err_msg_list = []
            for item in forms.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
                # print(item[0].get('message'))   # for test
            err_msg_str = '/'.join(err_msg_list)  # 拼接错误信息为一个字符串
            return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_str)


class DocUploadView(LoginRequiredMixin, View):

    def post(self, request):
        text_file = request.FILES.get('text_file')
        if not text_file:
            return to_json_data(errno=Code.NODATA, errmsg="没有数据")
        if text_file.content_type not in ('application/octet-stream', 'application/pdf',
                                          'application/zip', 'text/plain', 'application/x-rar'):
            return to_json_data(errno=Code.DATAERR, errmsg='不能上传非文本文件')
        try:
            ex_name = text_file.name.split('.')[-1]
        except Exception as e:
            logger.error('文档后缀名错误: {}'.format(e))
            ex_name = 'pdf'
        try:
            FDFS_Client = Fdfs_client(settings.FDFS_CLIENT_CONF_FILE)
            upload_res = FDFS_Client.upload_by_buffer(text_file.read(), ex_name)
        except Exception as e:
            logger.error('文件上传异常{}'.format(e))
            return to_json_data(errno=Code.DATAERR, errmsg="文件上传异常")
        else:
            res = upload_res.get('Status')
            if res != 'Upload successed.':
                return to_json_data(errno=Code.DATAERR, errmsg="文件上传失败")
            else:
                text_name = upload_res.get('Remote file_id')
                text_url = settings.FAST_DFS_TRACKER_DOMAIN + text_name
                return to_json_data(errmsg="文档上传成功", data={'text_url': text_url})


class DocPubView(PermissionRequiredMixin, View):
    permission_required = (
        'doc.view_docmodel', 'doc.delete_docmodel', 'doc.add_newsbanner', 'doc.change_docmodel')
    raise_exception = True  # 如果为 False直接跳转到登录页,如果为True则抛出异常

    def handle_no_permission(self):  # 如果上面抛出异常，就会用此方法来处理
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg='没有操作权限')
        else:
            return super().handle_no_permission()

    def get(self, request):
        return render(request, 'admin/docs_pub.html')

    def post(self, request):
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.NODATA, errmsg="没有数据")
        else:
            dict_data = json.loads(json_data.decode('utf8'))
        forms = DocPubForm(data=dict_data)
        if forms.is_valid():
            doc = forms.save(commit=False)
            doc.author = request.user
            doc.save()
            return to_json_data(errmsg="文档发布成功")
        else:
            err_msg_list = []
            for item in forms.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
                # print(item[0].get('message'))   # for test
            err_msg_str = '/'.join(err_msg_list)  # 拼接错误信息为一个字符串
            return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_str)


class CourseManageView(PermissionRequiredMixin, View):
    permission_required = ('course.add_course', 'course.view_course')
    raise_exception = True

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg='没有操作权限')
        else:
            return super().handle_no_permission()

    def get(self, request):
        courses = CourseModel.objects.select_related('teacher', 'category'). \
            only('id', 'title', 'teacher__name', 'category__name').filter(is_delete=False)
        return render(
            request, 'admin/courses_manage.html', locals()
        )


class CourseEditView(PermissionRequiredMixin, View):
    permission_required = ('course.change_course', 'course.delete_course')
    raise_exception = True

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg='没有操作权限')
        else:
            return super().handle_no_permission()

    def get(self, request, course_id):
        course = CourseModel.objects.filter(is_delete=False, id=course_id).first()
        if not course:
            return Http404('此课程未找到')
        else:
            teachers = TeachModel.objects.only('id', 'name').filter(is_delete=False)
            categories = CourseCategory.objects.only('id', 'name').filter(is_delete=False)
            return render(request, 'admin/course_pub.html', locals())

    def put(self, request, course_id):
        course = CourseModel.objects.only('id').filter(is_delete=False, id=course_id).first()
        if not course:
            return to_json_data(errno=Code.NODATA, errmsg="课程未找到")
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.NODATA, errmsg="数据不存在")
        else:
            dict_data = json.loads(json_data.decode('utf8'))
        forms = CoursePubForm(data=dict_data)
        if forms.is_valid():
            course.title = forms.cleaned_data.get('title')
            course.video_url = forms.cleaned_data.get('video_url')
            course.cover_url = forms.cleaned_data.get('cover_url')
            course.profile = forms.cleaned_data.get('profile')
            course.duration = forms.cleaned_data.get('duration')
            course.outline = forms.cleaned_data.get('outline')
            course.teacher_id = forms.cleaned_data.get('teacher')
            course.category_id = forms.cleaned_data.get('category')
            course.save()
            return to_json_data(errmsg="课程更新成功")
        else:
            err_msg_list = []
            for item in forms.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
                # print(item[0].get('message'))   # for test
            err_msg_str = '/'.join(err_msg_list)  # 拼接错误信息为一个字符串
            return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_str)

    def delete(self, request, course_id):
        course = CourseModel.objects.only('id').filter(id=course_id, is_delete=False).first()
        if not course:
            return to_json_data(errno=Code.NODATA, errmsg="课程未找到")
        else:
            course.is_delete = True
            course.save(update_fields=['is_delete'])
            return to_json_data(errmsg="课程删除成功")


class CoursePubView(PermissionRequiredMixin, View):
    permission_required = ('course.add_course', 'course.view_course')
    raise_exception = True

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg='没有操作权限')
        else:
            return super().handle_no_permission()

    def get(self, request):
        teachers = TeachModel.objects.only('id', 'name').filter(is_delete=False)
        categories = CourseCategory.objects.only('id', 'name').filter(is_delete=False)
        return render(request, 'admin/course_pub.html', locals())

    def post(self, request):
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.NODATA, errmsg="数据不存在")
        else:
            dict_data = json.loads(json_data.decode('utf8'))
        forms = CoursePubForm(data=dict_data)
        if forms.is_valid():
            forms.save()
            return to_json_data(errmsg="课程发布成功")
        else:
            err_msg_list = []
            for item in forms.errors.get_json_data().values():
                err_msg_list.append(item[0].get('message'))
                # print(item[0].get('message'))   # for test
            err_msg_str = '/'.join(err_msg_list)  # 拼接错误信息为一个字符串
            return to_json_data(errno=Code.PARAMERR, errmsg=err_msg_str)


# 权限相关
class GroupAddView(PermissionRequiredMixin, View):
    permission_required = ('auth.add_group', 'auth.view_group')
    raise_exception = True

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg='没有操作权限')
        else:
            return super().handle_no_permission()

    def get(self, request):
        permissions = Permission.objects.only('id').all()
        return render(request, 'admin/groups_add.html', locals())

    def post(self, request):
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.NODATA, errmsg="没有数据")
        else:
            dict_data = json.loads(json_data.decode('utf8'))
        group_name = dict_data.get('name', '')
        if not group_name:
            return to_json_data(errno=Code.NODATA, errmsg="组名不能为空")
        else:
            group_name = group_name.strip()
            # is_created 如果有 False   如果没有就为True
        group, is_created = Group.objects.get_or_create(name=group_name)
        if not is_created:
            return to_json_data(errno=Code.DATAEXIST, errmsg='该用户组已经存在')
        else:
            group_permissions = dict_data.get('group_permissions')
            if not group_permissions:
                return to_json_data(errno=Code.NODATA, errmsg="权限不能为空")
            try:
                permission_set = set(int(i) for i in group_permissions)
            except Exception as e:
                logger.error('权限错误 : e'.format(e))
                return to_json_data(errno=Code.DATAERR, errmsg="权限错误")
            all_permission_set = set(i.id for i in Permission.objects.only('id').all())
            # 判断  permission_set 所有元素是否都在 all_permission_set 中
            if not permission_set.issubset(all_permission_set):
                return to_json_data(errno=Code.DBERR, errmsg="权限错误")
            for p_id in permission_set:
                p = Permission.objects.filter(id=p_id).first()
                group.permissions.add(p)
            group.save()
            return to_json_data(errmsg="组创建成功")


class GroupManageView(PermissionRequiredMixin, View):
    permission_required = ('auth.add_group', 'auth.view_group')
    raise_exception = True

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg='没有操作权限')
        else:
            return super().handle_no_permission()

    def get(self, request):
        groups = Group.objects.values('id', 'name').annotate(user_num=Count('user')). \
            order_by('-user_num', 'id')
        return render(request, 'admin/groups_manage.html', locals())


class GroupEditView(PermissionRequiredMixin, View):
    permission_required = ('auth.change_group', 'auth.delete_group')
    raise_exception = True

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg='没有操作权限')
        else:
            return super().handle_no_permission()

    def get(self, request, group_id):
        group = Group.objects.only('id', 'name', 'permissions').filter(id=group_id).first()
        if not group:
            return to_json_data(errno=Code.NODATA, errmsg='此组不存在')
        else:
            permissions = Permission.objects.only('id').all()
            return render(request, 'admin/groups_add.html', locals())

    def delete(self, request, group_id):
        group = Group.objects.only('id').filter(id=group_id).first()
        if not group:
            return to_json_data(errno=Code.NODATA, errmsg='此组不存在')
        else:
            group.permissions.clear()
            group.delete()
            return to_json_data(errmsg="组删除成功")

    def put(self, request, group_id):
        group = Group.objects.filter(id=group_id).first()
        if not group:
            return to_json_data(errno=Code.NODATA, errmsg='此组不存在')
        else:
            json_data = request.body
            if not json_data:
                return to_json_data(errno=Code.NODATA, errmsg="数据不存在")
            else:
                dict_data = json.loads(json_data.decode('utf8'))
            group_name = dict_data.get('name', '')
            if not group_name:
                return to_json_data(errno=Code.NODATA, errmsg="组名不能为空")
            else:
                group_name = group_name.strip()
            group_permissions = dict_data.get('group_permissions')
            if not group_permissions:
                return to_json_data(errno=Code.NODATA, errmsg="权限不能为空")
            try:
                permission_set = set(int(i) for i in group_permissions)
            except Exception as e:
                logger.error('权限错误 : e'.format(e))
                return to_json_data(errno=Code.DATAERR, errmsg="权限错误")
            all_permission_set = set(i.id for i in Permission.objects.only('id').all())
            # 判断  permission_set 所有元素是否都在 all_permission_set 中
            if not permission_set.issubset(all_permission_set):
                return to_json_data(errno=Code.DBERR, errmsg="权限错误")
            existed_set = set(i.id for i in group.permissions.all())
            if group.name == group_name and permission_set == existed_set:
                return to_json_data(errno=Code.DATAEXIST, errmsg="数据未修改")
            else:
                for p_id in permission_set:
                    p = Permission.objects.filter(id=p_id).first()
                    group.permissions.add(p)
                group.name = group_name
                group.save()
            return to_json_data(errmsg="组更新成功")


class UserManageView(PermissionRequiredMixin, View):
    permission_required = ('user.view_usermodel', 'user.add_newsmodel')
    raise_exception = True

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg='没有操作权限')
        else:
            return super().handle_no_permission()

    def get(self, request):
        users = UserModel.objects. \
            only('id', 'username', 'is_staff', 'is_superuser').filter(is_active=True)
        return render(request, 'admin/user_manage.html', locals())


class UserEditView(PermissionRequiredMixin, View):
    permission_required = ('user.change_usermodel', 'user.delete_newsmodel')
    raise_exception = True

    def handle_no_permission(self):
        if self.request.method.lower() != 'get':
            return to_json_data(errno=Code.ROLEERR, errmsg='没有操作权限')
        else:
            return super().handle_no_permission()

    def get(self, request, user_id):
        user_instance = UserModel.objects.filter(id=user_id).first()
        groups = Group.objects.only('id', 'name').all()
        if not user_instance:
            return to_json_data(errno=Code.NODATA, errmsg="用户未找到")
        return render(request, 'admin/users_edit.html', locals())

    def delete(self, request, user_id):
        user_instance = UserModel.objects.filter(id=user_id).first()
        if not user_instance:
            return to_json_data(errno=Code.NODATA, errmsg="用户未找到")
        else:
            user_instance.groups.clear()  # 清除用户组
            user_instance.user_permissions.clear()  # 清除用户权限
            user_instance.is_active = False
            user_instance.save()
        return to_json_data(errmsg="用户删除成功")

    def put(self, request, user_id):
        user_instance = UserModel.objects.filter(id=user_id).first()
        if not user_instance:
            return to_json_data(errno=Code.NODATA, errmsg="用户未找到")
        json_data = request.body
        if not json_data:
            return to_json_data(errno=Code.NODATA, errmsg="数据不存在")
        else:
            dict_data = json.loads(json_data.decode('utf8'))
        try:
            is_staff = int(dict_data.get('is_staff'))
            is_active = int(dict_data.get('is_active'))
            is_superuser = int(dict_data.get('is_superuser'))
        except Exception as e:
            logger.error('参数错误 {}'.format(e))
            return to_json_data(errno=Code.DATAERR, errmsg='参数错误')
        parameter_list = [is_staff, is_active, is_superuser]
        standard_list = [0, 1]
        flag = 0
        for p in parameter_list:
            if p not in standard_list:
                flag += 1
        if flag != 0:
            return to_json_data(errno=Code.DATAERR, errmsg="参数错误")
        try:
            groups_set = set(int(i) for i in dict_data.get('groups'))
        except Exception as e:
            logger.error('用户组错误 {}'.format(e))
            return to_json_data(errno=Code.DATAERR, errmsg='用户组错误')
        groups_all = set(i.id for i in Group.objects.only('id').all())
        if not groups_set.issubset(groups_all):
            return to_json_data(errno=Code.DATAERR, errmsg='有不存在的组,请确认')
        # 更新user
        # 先清除组
        gs = Group.objects.filter(id__in=groups_set)
        user_instance.groups.clear()
        user_instance.groups.set(gs)
        user_instance.is_staff = bool(is_staff)
        user_instance.is_superuser = bool(is_superuser)
        user_instance.is_active = bool(is_active)
        user_instance.save()
        return to_json_data(errmsg="用户更新成功")
