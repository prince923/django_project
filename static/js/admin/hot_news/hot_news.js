// 创建static/js/admin/news/news_hot.js文件

$(function () {
    // 添加热门文章
    let $tagAdd = $("#btn-add-tag");  // 1. 获取添加按钮
    $tagAdd.click(function () {   	// 2. 点击事件
        fAlert.alertOneInput({
            title: "请输入文章标签",
            text: "长度限制在20字以内",
            placeholder: "请输入文章标签",
            confirmCallback: function confirmCallback(inputVal) {
                console.log(inputVal);

                if (inputVal === "") {
                    swal.showInputError('标签不能为空');
                    return false;
                }

                let sDataParams = {
                    "name": inputVal
                };

                $.ajax({
                    // 请求地址
                    url: "/admin/tags/",  // url尾部需要添加/
                    // 请求方式
                    type: "POST",
                    data: JSON.stringify(sDataParams),
                    // 请求内容的数据类型（前端发给后端的格式）
                    contentType: "application/json; charset=utf-8",
                    // 响应数据的格式（后端返回给前端的格式）
                    dataType: "json",
                })
                    .done(function (res) {
                        if (res.errno === "0") {

                            fAlert.alertSuccessToast(inputVal + " 标签添加成功");
                            setTimeout(function () {
                                window.location.reload();
                            }, 1000)
                        } else {
                            swal.showInputError(res.errmsg);
                        }
                    })
                    .fail(function () {
                        message.showError('服务器超时，请重试！');
                    });

            }
        });
    });


    // 编辑热门文章
    let $HotNewsEdit = $(".btn-edit");  // 1. 获取编辑按钮
    $HotNewsEdit.click(function () {    // 2. 点击触发事件
        let _this = this;
        let sHotNewsId = $(this).parents('tr').data('id');
        // let sHotNewsTitle = $(this).parents('tr').data('name');
        let sPriority = $(this).data('priority');

        fAlert.alertOneInput({
            title: "编辑热门文章优先级",
            text: "你正在编辑热门文章的优先级",
            placeholder: "请输入文章优先级",
            value: sPriority,
            confirmCallback: function confirmCallback(inputVal) {
                if (!inputVal.trim()) {
                    swal.showInputError('输入框不能为空！');
                    return false;
                } else if (inputVal == sPriority) {
                    swal.showInputError('优先级未修改');
                    return false;
                } else if (!jQuery.inArray(inputVal, ['1', '2', '3'])) {
                    swal.showInputError('优先级只能取1，2，3中的一个');
                    return false;
                }

                let sDataParams = {
                    "priority": inputVal
                };

                $.ajax({
                    // 请求地址
                    url: "/admin/hotnews/" + sHotNewsId + "/",  // url尾部需要添加/
                    // 请求方式
                    type: "PUT",
                    data: JSON.stringify(sDataParams),
                    // 请求内容的数据类型（前端发给后端的格式）
                    contentType: "application/json; charset=utf-8",
                    // 响应数据的格式（后端返回给前端的格式）
                    dataType: "json",
                })
                    .done(function (res) {
                        if (res.errno === "0") {
                            swal.close();
                            message.showSuccess("标签修改成功");
                            // $(_this).parents('tr').find('td:nth-child(3)').text(inputVal);

                            setTimeout(function () {
                                window.location.href = '/admin/hotnews/';
                            }, 800)
                        } else {
                            swal.showInputError(res.errmsg);
                        }
                    })

                    .fail(function () {
                        message.showError('服务器超时，请重试！');
                    });

            }
        });

    });


    // 删除热门文章
    let $HotNewsDel = $(".btn-del");  // 1. 获取删除按钮
    $HotNewsDel.click(function () {   // 2. 点击触发事件
        let _this = this;
        let sHotNewsId = $(this).parents('tr').data('id');
        fAlert.alertConfirm({
            title: "确定删除热门文章吗？",
            type: "error",
            confirmText: "确认删除",
            cancelText: "取消删除",
            confirmCallback: function confirmCallback() {

                $.ajax({
                    url: "/admin/hotnews/" + sHotNewsId + "/",  // url尾部需要添加/
                    type: "DELETE",
                    dataType: "json",
                })
                    .done(function (res) {
                        if (res.errno === "0") {
                            message.showSuccess("删除热门文章成功");
                            $(_this).parents('tr').remove();
                             setTimeout(function () {
                                window.location.href = '/admin/hotnews/';
                            }, 800)
                        } else {
                            swal.showInputError(res.errmsg);
                        }
                    })
                    .fail(function () {
                        message.showError('服务器超时，请重试！');
                    });
            }
        });
    });

});