from django.db import models
from utils.base_models import BaseModel


# Create your models here.

class DocModel(BaseModel):
    """
    create doc model

     """
    file_url = models.URLField(verbose_name="文件url", help_text="文件url")
    title = models.CharField(max_length=150, verbose_name="文档标题", help_text="文档标题")
    desc = models.TextField(verbose_name="文档描述", help_text="文档描述")
    image_url = models.URLField(default="", verbose_name="图片url", help_text="图片url")
    author = models.ForeignKey('user.UserModel', on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = "tb_docs"  # 指明数据库表名
        verbose_name = "用户"  # 在admin站点中显示的名称
        verbose_name_plural = verbose_name  # 显示的复数名称

    def __str__(self):
        return self.title
