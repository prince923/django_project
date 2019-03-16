from django.shortcuts import render
from django.views import View
from django.core.paginator import Paginator
import logging
from utils.json_fun import to_json_data
from .models import TagModel, NewsModel

logger = logging.getLogger('django')


# Create your views here.


class IndexView(View):
    def get(self, request):
        tags = TagModel.objects.only('tag_name').filter(is_delete=False)  # only 会改变查询语句，只会查询  id  tag_name 字段
        return render(request, 'news/index.html', locals())  # 当需要返回数据较多的时候，可以用locals() 代替context

    def post(self, request):
        pass


class NewsList(View):
    """
    新闻列表
    :param :  1. page   2. tag_id
    1.  取数据
    2. 后台校验
    3. 数据库获取数据
    4. 分页
    5. 返回数据
    """

    def get(self, request):
        try:
            page = int(request.GET.get('page', 1))
        except Exception as e:
            logger.error('page error : {}'.format(e))
            page = 1  # 如果获取不到，或者类型错误  page 都为 第一页
        try:
            tag_id = int(request.GET.get('tag_id', 0))
        except Exception as e:
            logger.error('tag_id error : {}'.format(e))
            tag_id = 0  # 如果获取不到，或者类型错误 tag_id  都为  0 为最新资讯
        news_query = NewsModel.objects.select_related('tag', 'author'). \
            only('title', 'digest', 'image_url', 'update_time', 'author__username', 'tag__tag_name')
        news = news_query.filter(tag_id=tag_id) or news_query.filter(is_delete=False)
        p = Paginator(news, 5)
        try:
            # 表示取第几页的数据,超出范围就会抛出异常
            news_info = p.page(page)
        except Exception as e:
            logger.error('总页数超出范围 {}'.format(e))
            #  num_pages 表示页数，如果超出范围显示最后一页
            news_info = p.page(p.num_pages)
        # 序列化数据
        news_list = []
        for n in news_info:
            news_list.append({
                'digest': n.digest,
                'title': n.title,
                'author': n.author.username,
                'tag_name': n.tag.tag_name,
                'image_url': n.image_url,
                'update_time': n.update_time.strftime('%Y年%m月%d日 %H:%M')
            })
        data = {
            'total_page': p.num_pages,
            'news': news_list,
        }
        return to_json_data(data=data)


class NewsDetail(View):
    def get(self, request):
        return render(request, 'news/news_detail.html')

    def post(self, request):
        pass


class NewsSearch(View):
    def get(self, request):
        return render(request, 'news/search.html')

    def post(self, request):
        pass
