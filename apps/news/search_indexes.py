from haystack import indexes
from .models import NewsModel


class NewsModelIndex(indexes.SearchIndex, indexes.Indexable):
    """
    创建 News索引表
    """
    text = indexes.CharField(document=True, use_template=True)
    id = indexes.IntegerField(model_attr='id')
    title = indexes.CharField(model_attr='title')
    digest = indexes.CharField(model_attr='digest')
    content = indexes.CharField(model_attr='content')
    image_url = indexes.CharField(model_attr='image_url')

    def get_model(self):
        """返回建立索引的模型类
        """
        return NewsModel

    def index_queryset(self, using=None):
        """返回要建立索引的数据查询集
        """

        # return self.get_model().objects.filter(is_delete=False, tag_id=1)
        return self.get_model().objects.filter(is_delete=False, tag_id__in=[1, 2, 3, 4, 5, 6])
