from django.db.models import Count
from django.shortcuts import render
from news.models import TagModel, NewsHots, NewsModel
import json
import logging
# Create your views here.
from django.views import View

from utils.json_fun import to_json_data
from utils.res_code import Code, error_map

logger = logging.getLogger('django')


class AdminIndex(View):
    def get(self, request):
        return render(request, 'admin/index.html')


class TagManageView(View):
    """
    create tag manage View
    route: '/admin/tags/'
    """

    def get(self, request):
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
    def get(self, request):
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
    def get(self, request):
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
    def get(self, request, tag_id):
        news = list(NewsModel.objects.values('id', 'title').filter(tag_id=tag_id, is_delete=False))
        data = {'news': news}
        return to_json_data(data=data)
