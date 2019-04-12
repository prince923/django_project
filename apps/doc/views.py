from django.http import FileResponse, Http404
from django.shortcuts import render
from django.utils.encoding import escape_uri_path
from django.views import View
from .models import DocModel
from django.conf import settings
import requests
import logging

# Create your views here
logger = logging.getLogger('django')  # 导入日志器


class DocIndex(View):
    def get(self, request: object) -> object:
        docs = DocModel.objects.defer('author', 'is_delete', 'create_time', 'update_time').filter(is_delete=False)
        return render(request, 'doc/docDownload.html', locals())


def down_doc(request, doc_id):
    """

    :param doc_id
    :return:  file
    """
    doc = DocModel.objects.only('id').filter(id=doc_id, is_delete=False).first()
    if doc:
        doc_url = doc.file_url
        # full_url = settings.SITE_NAME + doc_url
        try:
            res = FileResponse(requests.get(doc_url, stream=True))
        except Exception as e:
            logger.error('获取文件异常{}'.format(e))
            raise Http404('<h1>文件未找到<h1>')
        ex_name = doc_url.split('.')[-1]   # 取文件扩展名
        if not ex_name:
            return Http404('文件异常')
        else:
            ex_name = ex_name.lower()
            if ex_name == "pdf":
                res["Content-type"] = "application/pdf"
            elif ex_name == "zip":
                res["Content-type"] = "application/zip"
            elif ex_name == "doc":
                res["Content-type"] = "application/msword"
            elif ex_name == "xls":
                res["Content-type"] = "application/vnd.ms-excel"
            elif ex_name == "docx":
                res["Content-type"] = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            elif ex_name == "ppt":
                res["Content-type"] = "application/vnd.ms-powerpoint"
            elif ex_name == "pptx":
                res["Content-type"] = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
            else:
                raise Http404("文档格式不正确！")
            # escape_uri_path : 从（URI）的路径部分中转义不安全的字符。
            doc_filename = escape_uri_path(doc_url.split('/')[-1])
            # 设置为inline，会直接打开
            res["Content-Disposition"] = "attachment; filename*=UTF-8''{}".format(doc_filename)
            return res
    else:
        return Http404('<h1>文档不存在<h1>')
