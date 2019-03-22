from django.shortcuts import render
from django.views import View
from django.core.paginator import Paginator
import logging
from utils.json_fun import to_json_data
from utils.res_code import Code, error_map
from .models import TagModel, NewsModel, NewsHots, NewsBanner, CommentModel
from user.models import UserModel
from . import constant
import json

logger = logging.getLogger('django')


# Create your views here.


class IndexView(View):
    def get(self, request):
        tags = TagModel.objects.only('tag_name').filter(is_delete=False)  # only 会改变查询语句，只会查询  id  tag_name 字段
        news_hots = NewsHots.objects.select_related('news').only('news__title', 'news__image_url', 'news_id').filter(
            is_delete=False).order_by('priority', '-id')[0:constant.NEWS_HOTS_SHOW_COUNT]
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
            only('id', 'title', 'digest', 'image_url', 'update_time', 'author__username', 'tag__tag_name')
        news = news_query.filter(tag_id=tag_id) or news_query.filter(is_delete=False)
        p = Paginator(news, constant.ONE_PAGE_COUNT)
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
                'id': n.id,
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


class NewsDetailView(View):
    def get(self, request, news_id):
        news = NewsModel.objects.select_related('tag', 'author'). \
            only('id', 'title', 'content', 'author__username', 'tag__tag_name', 'update_time'). \
            filter(is_delete=False, id=news_id).first()
        comments = CommentModel.objects.select_related('author', 'parents'). \
            only('content', 'author__username', 'update_time',
                 'parents__author__username', 'parents__content', 'parents__update_time'). \
            filter(news_id=news_id, is_delete=False)
        return render(request, 'news/news_detail.html', locals())

    def post(self, request, news_id):
        json_data = request.body
        if json_data:
            dict_data = json.loads(json_data.decode('utf8'))
        else:
            return to_json_data(errno=Code.NODATA, errmsg=error_map[Code.NODATA])
        if not request.user:
            return to_json_data(errno=Code.SESSIONERR, errmsg=[Code.SESSIONERR])
        news = NewsModel.objects.filter(id=news_id)
        if news:
            parent_id = dict_data.get('parent_id')
            if parent_id:
                try:
                    int(parent_id)
                except Exception as e:
                    logger.error('父评论错误 {}'.format(e))
                    return to_json_data(errno=Code.DATAERR, errmsg='父评论错误')
            content = dict_data.get('content')
            if content:
                # comment=CommentModel()
                # comment.news_id=news_id
                # comment.content=content
                # comment.parents_id=parent_id
                # comment.author_id=request.user.id
                # comment.save()
                user = UserModel.objects.filter(username=request.user).first()
                comment = CommentModel.objects.create(news_id=news_id, content=content, parents_id=parent_id,
                                                      author_id=user.id)
                comment_info = {'comment_id': comment.id,
                                'comment_news_id': comment.news_id,
                                'content': comment.content,
                                'author_username': comment.author.username,
                                'update_time': comment.update_time.strftime('%Y年%m月%d日 %H:%M')}
                if not comment.parents:
                    return to_json_data(data=comment_info)
                else:
                    parent_comment_data = {
                        'parent_author_username': comment.parents.author.username,
                        'parent_content': comment.parents.content,
                    }
                    comment_info.update(parent_comment_data)
                return to_json_data(data=comment_info)
            else:
                logger.error('评论信息不能为空')
                return to_json_data(errno=Code.NODATA, errmsg="评论信息不能为空")
        else:
            return to_json_data(errno=Code.NODATA, errmsg='新闻不存在')


class NewsSearch(View):
    def get(self, request):
        return render(request, 'news/search.html')

    def post(self, request):
        pass


class NewsBannerView(View):
    def get(self, request):
        banners = NewsBanner.objects.select_related('news').only('image_url', 'news_id', 'news__title').filter(
            is_delete=False)[0:6]
        banner_list = []
        for banner in banners:
            banner_list.append({
                'news_id': banner.news_id,
                'image_url': banner.image_url,
                'news_title': banner.news.title,
            })
        data = {
            'banners': banner_list
        }
        return to_json_data(data=data)
