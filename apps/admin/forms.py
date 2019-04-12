from django import forms
from news.models import NewsModel, TagModel
from doc.models import DocModel
from course.models import CourseModel, TeachModel, CourseCategory


class NewsPubForm(forms.ModelForm):
    """
    create news pub form

    """
    image_url = forms.URLField(error_messages={'required': '图片url不能为空'})
    tag = forms.ModelChoiceField(queryset=TagModel.objects.only('id').filter(is_delete=False),
                                 error_messages={
                                     'required': '文章标签不能为空',
                                     'invalid_choice': '文章标签id不存在',
                                 })

    class Meta:
        model = NewsModel
        fields = ['title', 'digest', 'content', 'image_url', 'tag']
        error_messages = {
            'title': {
                'max_length': '文章标题长度为1-150位',
                'min_length': '文章标题长度为1-150位',
                'required': '文章标题不能为空',
            },
            'digest': {
                'max_length': "文章摘要长度不能超过200",
                'min_length': "文章标题长度大于1",
                'required': '文章摘要不能为空',
            },
            'content': {
                'required': '文章内容不能为空',
            },
        }


class DocPubForm(forms.ModelForm):
    file_url = forms.URLField(label='文件URL', error_messages={'required': '文件URL不能为空'})
    image_url = forms.URLField(label='文档图片URL', error_messages={'required': '图片URL不能为空'})

    class Meta:
        model = DocModel
        fields = ['file_url', 'title', 'desc', 'image_url']
        error_messages = {
            'title': {
                'max_length': '标题最大长度为150位',
                'min_length': '标题最小长度为1位',
                'required': '文档标题不能为空',
            },
            'desc': {
                'min_length': '文档描述最小长度为1位',
                'max_length': '文档描述最大长度为200位',
                'required': '文档描述不能为空',
            }
        }


class CoursePubForm(forms.ModelForm):
    video_url = forms.URLField(label='课程地址', error_messages={'required': '课程地址不能为空'})
    cover_url = forms.URLField(label='课程封面图', error_messages={'required': '课程封面图不能为空'})
    teacher = forms.ModelChoiceField(
        queryset=TeachModel.objects.only('id').filter(is_delete=False),
        error_messages={'required': '课程讲师不能为空', 'invalid_choice': '讲师ID不存在'})
    category = forms.ModelChoiceField(
        queryset=CourseCategory.objects.only('id').filter(is_delete=False),
        error_messages={
            'required': '课程分类不能为空',
            'invalid_choice': '课程分类ID不存在'
        })

    class Meta:
        model = CourseModel
        fields = ['title', 'cover_url', 'video_url', 'profile', 'duration', 'outline', 'teacher', 'category']
        error_messages = {
            'title': {
                'min_length': '课程标题最小长度为1',
                'max_length': '课程标题最大长度不能超过150',
                'required': '课程标题不能为空'
            },
            'duration': {
                'required': '课程时长不能为空'
            },
            'profile': {
                'required': '课程简介不能为空'
            },
            'outline': {
                'required':'课程大纲不能为空'
            }
        }
