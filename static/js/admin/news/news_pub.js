$(function () {
    let $e = window.wangEditor;
    window.editor = new $e('#news-content');
    window.editor.create();

    // 获取缩略图输入框元素
    let $thumbnailUrl = $("#news-thumbnail-url");

    // ================== 上传图片文件至服务器 ================
    let $upload_to_server = $("#upload-news-thumbnail");
    $upload_to_server.change(function () {
        let file = this.files[0];   // 获取文件
        let oFormData = new FormData();  // 创建一个 FormData
        oFormData.append("image_file", file); // 把文件添加进去
        // 发送请求
        $.ajax({
            url: "/admin/news/images/",
            method: "POST",
            data: oFormData,
            processData: false,   // 定义文件的传输
            contentType: false,
        })
            .done(function (res) {
                if (res.errno === "0") {
                    // 更新标签成功
                    message.showSuccess("图片上传成功");
                    let sImageUrl = res["data"]["image_url"];
                    // console.log(thumbnailUrl);
                    $thumbnailUrl.val('');
                    $thumbnailUrl.val(sImageUrl);
                } else {
                    message.showError(res.errmsg)
                }
            })
            .fail(function () {
                message.showError('服务器超时，请重试！');
            });

    });


    // ================== 上传至七牛（云存储平台） ================
    let $progressBar = $(".progress-bar");
    QINIU.upload({
        "domain": "http://ppmd5bmae.bkt.clouddn.com/",  // 七牛空间域名
        "uptoken_url": "/admin/token/",	 // 后台返回 token的地址
        "browse_btn": "upload-btn",		// 按钮
        "success": function (up, file, info) {	 // 成功
            let domain = up.getOption('domain');
            let res = JSON.parse(info);
            let filePath = domain + res.key;
            console.log(filePath);
            $thumbnailUrl.val('');
            $thumbnailUrl.val(filePath);
        },
        "error": function (up, err, errTip) {
            // console.log('error');
            console.log(up);
            console.log(err);
            console.log(errTip);
            // console.log('error');
            message.showError(errTip);
        },
        "progress": function (up, file) {
            let percent = file.percent;
            $progressBar.parent().css("display", 'block');
            $progressBar.css("width", percent + '%');
            $progressBar.text(parseInt(percent) + '%');
        },
        "complete": function () {
            $progressBar.parent().css("display", 'none');
            $progressBar.css("width", '0%');
            $progressBar.text('0%');
        }
    });


    // ================== 发布文章 ================
    let $newsBtn = $("#btn-pub-news");
    $newsBtn.click(function () {
        // 判断文章标题是否为空
        let sTitle = $("#news-title").val();  // 获取文章标题
        if (!sTitle) {
            message.showError('请填写文章标题！');
            return
        }
        // 判断文章摘要是否为空
        let sDesc = $("#news-desc").val();  // 获取文章摘要
        if (!sDesc) {
            message.showError('请填写文章摘要！');
            return
        }

        let sTagId = $("#news-category").val();
        if (!sTagId || sTagId === '0') {
            message.showError('请选择文章标签')
            return
        }

        let sThumbnailUrl = $thumbnailUrl.val();
        if (!sThumbnailUrl) {
            message.showError('请上传文章缩略图')
            return
        }

        let sContentHtml = window.editor.txt.html();
        if (!sContentHtml || sContentHtml === '<p><br></p>') {
            message.showError('请填写文章内容！');
            return
        }

        // 获取news_id 存在表示更新 不存在表示发表
        let newsId = $(this).data("news-id");
        let url = newsId ? '/admin/news/' + newsId + '/' : '/admin/news/pub/';
        let data = {
            "title": sTitle,
            "digest": sDesc,
            "tag": sTagId,
            "image_url": sThumbnailUrl,
            "content": sContentHtml,
        };

        $.ajax({
            // 请求地址
            url: url,
            // 请求方式
            type: newsId ? 'PUT' : 'POST',
            data: JSON.stringify(data),
            // 请求内容的数据类型（前端发给后端的格式）
            contentType: "application/json; charset=utf-8",
            // 响应数据的格式（后端返回给前端的格式）
            dataType: "json",
        })
            .done(function (res) {
                if (res.errno === "0") {
                    if (newsId) {
                        fAlert.alertNewsSuccessCallback("文章更新成功", '跳到后台首页', function () {
                            window.location.href = '/admin/'
                        });

                    } else {
                        fAlert.alertNewsSuccessCallback("文章发表成功", '跳到后台首页', function () {
                            window.location.href = '/admin/'
                        });
                    }
                } else {
                    fAlert.alertErrorToast(res.errmsg);
                }
            })
            .fail(function () {
                message.showError('服务器超时，请重试！');
            });
    });

});
