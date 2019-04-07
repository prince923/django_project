from django import forms
from news.models import NewsModel, TagModel


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
