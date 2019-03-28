from django.db import models
from utils.base_models import BaseModel


# Create your models here.

class TeachModel(BaseModel):
    name = models.CharField(max_length=150, verbose_name='讲师姓名', help_text='讲师姓名')
    positional_title = models.CharField(max_length=150, verbose_name='讲师职称', help_text='讲师职称')
    profile = models.TextField(verbose_name='讲师简介', help_text='讲师简介')
    avatar_url = models.URLField(verbose_name='头像url', help_text='头像url')

    class Meta:
        db_table = "tb_teachers"  # 指明数据库表名
        verbose_name = "讲师"  # 在admin站点中显示的名称

    def __str__(self):
        return self.name


class CourseCategory(BaseModel):
    name = models.CharField(max_length=100, verbose_name="课程分类名", help_text='课程分类名')

    class Meta:
        db_table = "tb_course_category"  # 指明数据库表名
        verbose_name = "课程分类"  # 在admin站点中显示的名称
        verbose_name_plural = verbose_name  # 显示的复数名称

    def __str__(self):
        return self.name


class CourseModel(BaseModel):
    title = models.CharField(max_length=150, verbose_name="课程名", help_text='课程名')
    cover_url = models.URLField(verbose_name="课程封面图URL", help_text='课程封面图URL')
    video_url = models.URLField(verbose_name="课程视频URL", help_text='课程视频URL')
    duration = models.FloatField(default=0.0, verbose_name="课程时长", help_text='课程时长')
    profile = models.TextField(null=True, blank=True, verbose_name="课程简介", help_text='课程简介')
    outline = models.TextField(null=True, blank=True, verbose_name="课程大纲", help_text='课程大纲')

    teacher = models.ForeignKey(TeachModel, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.ForeignKey(CourseCategory, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = "tb_course"  # 指明数据库表名
        verbose_name = "课程"  # 在admin站点中显示的名称
        verbose_name_plural = verbose_name  # 显示的复数名称

    def __str__(self):
        return self.title

