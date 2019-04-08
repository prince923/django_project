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

from admin.forms import NewsPubForm
from django_project import settings
from news.models import TagModel, NewsHots, NewsModel

# Create your views here.
from fdfs_client.client import Fdfs_client
from utils.json_fun import to_json_data
from utils.res_code import Code, error_map
from scripts import paginator_script
import qiniu
from utils.qiniu import qiniu_info

logger = logging.getLogger('django')


class AdminIndex(View):
    def get(self, request: object) -> object:
        return render(request, 'admin/index.html')


class TagManageView(View):
    """
    create tag manage View
    route: '/admin/tags/'
    """

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


class TagEdit(View):
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


class HotNewsManageView(View):
    def get(self, request: object) -> object:
        hot_news = NewsHots.objects.select_related('news'). \
                       only('id', 'priority', 'news_id', 'news__title', 'news__tag__tag_name'). \
                       filter(is_delete=False).order_by('priority', '-news__clicks')[:3]
        return render(request, 'admin/hotnews.html', locals())


class HotNewsEditView(View):
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


class AddHotNewsView(View):
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


class NewsManageView(View):
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


class NewsEditView(View):
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
                news.tag_id = forms.cleaned_data.get('tag_id')
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


class NewsPubView(View):
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


class UploadImage(View):
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
                    upload_res =FDFS_Client.upload_by_buffer(image_file.read(),ex_name)
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


class UploadToken(View):
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
