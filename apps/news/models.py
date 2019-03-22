from django.db import models


# Create your models here.


class BaseModel(models.Model):
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_delete = models.BooleanField(default=False, verbose_name='逻辑删除')

    class Meta:
        #  定义为抽象类，在迁移的时候不会迁移到数据库
        abstract = True


class TagModel(BaseModel):
    """
    新闻标签
    """
    tag_name = models.CharField(max_length=64, help_text='新闻标签名', verbose_name='新闻标签名')

    class Meta:
        ordering = ['-update_time', '-id']
        db_table = 'tb_tag'  # 指明数据库表名
        verbose_name = '新闻标签'  # 在admin站点中显示的名称
        verbose_name_plural = verbose_name  # 显示的复数名称

    def __str__(self):
        return '新闻标签{}'.format(self.tag_name)


class NewsModel(BaseModel):
    title = models.CharField(max_length=150, verbose_name='新闻标题', help_text='新闻标题')
    digest = models.CharField(max_length=200, verbose_name='新闻摘要', help_text='新闻摘要')
    content = models.TextField(verbose_name='新闻内容', help_text='新闻内容')
    clicks = models.IntegerField(default=0, verbose_name='新闻点击量', help_text='新闻点击量')
    image_url = models.URLField(default="", verbose_name='图片url', help_text='图片url')
    author = models.ForeignKey('user.UserModel', verbose_name='新闻作者', help_text='新闻作者',
                               on_delete=models.SET_NULL, null=True)
    tag = models.ForeignKey('TagModel', verbose_name='新闻标签', help_text='新闻标签', on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-update_time', '-id']
        db_table = 'tb_news'
        verbose_name = '新闻'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '新闻{}'.format(self.title)


class CommentModel(BaseModel):
    content = models.TextField(verbose_name='评论内容', help_text='评论内容')
    news = models.ForeignKey('NewsModel', on_delete=models.CASCADE, verbose_name='评论新闻', help_text='评论新闻')
    author = models.ForeignKey('user.UserModel', on_delete=models.CASCADE, verbose_name='评论作者', help_text='评论作者')
    parents = models.ForeignKey('self', on_delete=models.CASCADE,blank=True,null=True)  # 自关联，用于创建自评论

    class Meta:
        ordering = ['-update_time', '-id']
        db_table = 'tb_comments'
        verbose_name = '新闻评论'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '新闻评论{}'.format(self.content)


class NewsHots(BaseModel):

    PRI_CHOICES = [
        (1,'第一级'),
        (2,'第二级'),
        (3,'第三级'),
    ]

    news = models.OneToOneField('NewsModel', on_delete=models.CASCADE)
    priority = models.IntegerField(verbose_name='新闻优先级', help_text='新闻优先级',default=3,choices=PRI_CHOICES)

    class Meta:
        ordering = ['-update_time', '-id']
        db_table = 'tb_news_hots'
        verbose_name = '新闻优先级'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '新闻优先级{}'.format(self.priority)


class NewsBanner(BaseModel):

    PRI_CHOICES = [
        (1, '第一级'),
        (2, '第二级'),
        (3, '第三级'),
        (4, '第四级'),
        (5, '第五级'),
        (6, '第六级'),
    ]

    image_url = models.URLField(verbose_name='轮播图图片链接', help_text='轮播图图片链接')
    priority = models.IntegerField(verbose_name='轮播图片优先级', help_text='轮播图片优先级',default=6,choices=PRI_CHOICES) # 优先级默认为第六级
    news = models.ForeignKey('NewsModel', on_delete=models.CASCADE)

    class Meta:
        ordering = ['priority','-update_time','-id']
        db_table = 'news_banner'
        verbose_name = '新闻轮播图'
        verbose_name_plural = verbose_name

