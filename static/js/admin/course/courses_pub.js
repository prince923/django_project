let sdk = baidubce.sdk;
let VodClient = sdk.VodClient;

const CONFIG = {
  endpoint: 'http://vod.bj.baidubce.com',	// 默认区域名
  credentials: {
    ak: '7d30644f2e04436d8e5608d3f9a37477',	 // 填写你的百度云中ak和sk
    sk: '3d2c75424b904db09040e174c4462f9b'
  }
};

let BAIDU_VOD_DOMAIN = 'imuw7w4n9pxhzjamzc3.exp.bcevod.com';	// 百度云VOD域名

const CLIENT = new VodClient(CONFIG);

$(function () {
    let $e = window.wangEditor;
    window.editor = new $e('#course-outline');
    window.editor.create();


    let $thumbnailUrl = $("#news-thumbnail-url");   // 获取缩略图输入框元素
    let $courseFileUrl = $("#docs-file-url");    // 获取课程地址输入框元素

    // ================== 上传图片文件至服务器 ================
    let $upload_image_server = $("#upload-image-server");
    $upload_image_server.change(function () {
        // let _this = this;
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
                    message.showSuccess("图片上传成功");
                    let sImageUrl = res.data.image_url;
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

    // ================== 上传文件至服务器 ================
    let $upload_file_server = $("#upload-file-server");
    $upload_file_server.change(function () {

        // 先判断课程标题是否为空
        let sTitle = $("#news-title").val();  // 获取课程标题
        if (!sTitle) {
            message.showError('请先填写课程标题之后，再上传视频！');
            return
        }

        // 判断课程简介是否为空
        let sDesc = $("#news-desc").val();  // 获取课程简介
        if (!sDesc) {
            message.showError('请先填写课程描述之后，再上传视频！');
            return
        }

        let video_file = this.files[0];   // 获取文件
        let video_file_type = video_file.type;

        // 调用百度云VOD接口
        let blob = new Blob([video_file], {type: video_file_type});

        CLIENT.createMediaResource(sTitle, sDesc, blob)
        // Node.js中<data>可以为一个Stream、<pathToFile>；在浏览器中<data>为一个Blob对象
            .then(function (response) {
                // 上传完成
                message.showSuccess("视频上传成功");
                let sMediaId = response.body.mediaId;
                console.log('媒资ID为：', sMediaId);
                let sVideoUrl = 'http://' + BAIDU_VOD_DOMAIN + '/' + sMediaId + '/' + sMediaId + '.m3u8';
                $courseFileUrl.val('');
                $courseFileUrl.val(sVideoUrl);

            })
            .catch(function (error) {
                console.log(error);   // 上传错误
                message.showError(error)
            });

    });


    // ================== 上传图片至七牛（云存储平台） ================
    let $progressBar = $(".progress-bar");
    QINIU.upload({
        "domain": "http://ppmd5bmae.bkt.clouddn.com/",  // 七牛空间域名
        // 后台返回 token的地址 (后台返回的 url 地址) 不可能成功
        "uptoken_url": "/admin/token/",
        // 按钮
        "browse_btn": "upload-image-btn",
        // 成功
        "success": function (up, file, info) {
            let domain = up.getOption('domain');
            let res = JSON.parse(info);
            let filePath = domain + res.key;
            console.log(filePath);  // 打印文件路径
            $thumbnailUrl.val('');
            $thumbnailUrl.val(filePath);
        },
        // 失败
        "error": function (up, err, errTip) {
            console.log(up);
            console.log(err);
            console.log(errTip);
            message.showError(errTip);
        },
        "progress": function (up, file) {
            let percent = file.percent;
            $progressBar.parent().css("display", 'block');
            $progressBar.css("width", percent + '%');
            $progressBar.text(parseInt(percent) + '%');
        },
        // 完成后 去掉进度条
        "complete": function () {
            $progressBar.parent().css("display", 'none');
            $progressBar.css("width", '0%');
            $progressBar.text('0%');
        }
    });


    // ================== 发布文章 ================
    let $docsBtn = $("#btn-pub-news");
    $docsBtn.click(function () {
        // 判断课程标题是否为空
        let sTitle = $("#news-title").val();  // 获取文件标题
        if (!sTitle) {
            message.showError('请填写课程标题！');
            return
        }

        // 判断课程简介是否为空
        let sDesc = $("#news-desc").val();  // 获取课程简介
        if (!sDesc) {
            message.showError('请填写课程描述！');
            return
        }

        // 判断课程缩略图url是否为空
        let sThumbnailUrl = $thumbnailUrl.val();
        if (!sThumbnailUrl) {
            message.showError('请上传课程缩略图');
            return
        }

        // 判断课程url是否为空
        let sCourseFileUrl = $courseFileUrl.val();
        if (!sCourseFileUrl) {
            message.showError('请上传视频或输入视频地址');
            return
        }

        // 判断视频时长是否为空
        let sCourseTime = $('#course-time').val();  // 获取视频时长
        if (!sCourseTime) {
            message.showError('请填写视频时长！');
            return
        }

        // 判断是否选择讲师
        let sTeacherId = $("#course-teacher").val();
        if (!sTeacherId || sTeacherId === '0') {
            message.showError('请选择讲师');
            return
        }

        // 判断是否选择课程分类
        let sCategoryId = $("#course-category").val();
        if (!sCategoryId || sCategoryId === '0') {
            message.showError('请选择课程分类');
            return
        }

        // 判断课程大纲是否为空
        let sContentHtml = window.editor.txt.html();
        // let sContentText = window.editor.txt.text();
        if (!sContentHtml || sContentHtml === '<p><br></p>') {
            message.showError('请填写课程大纲！');
            return
        }

        // 获取coursesId 存在表示更新 不存在表示发表
        let coursesId = $(this).data("news-id");
        let url = coursesId ? '/admin/courses/' + coursesId + '/' : '/admin/courses/pub/';
        let data = {
            "title": sTitle,
            "profile": sDesc,
            "cover_url": sThumbnailUrl,
            "video_url": sCourseFileUrl,
            "duration": sCourseTime,
            "outline": sContentHtml,
            "teacher": sTeacherId,
            "category": sCategoryId
        };

        $.ajax({
            // 请求地址
            url: url,
            // 请求方式
            type: coursesId ? 'PUT' : 'POST',
            data: JSON.stringify(data),
            // 请求内容的数据类型（前端发给后端的格式）
            contentType: "application/json; charset=utf-8",
            // 响应数据的格式（后端返回给前端的格式）
            dataType: "json",
        })
            .done(function (res) {
                if (res.errno === "0") {
                    if (coursesId) {
                        fAlert.alertNewsSuccessCallback("课程更新成功", '跳到课程管理页', function () {
                            window.location.href = '/admin/courses/'
                        });

                    } else {
                        fAlert.alertNewsSuccessCallback("课程发表成功", '跳到课程管理页', function () {
                            window.location.href = '/admin/courses/'
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