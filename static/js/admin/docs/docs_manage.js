$(function () {

    // 删除标签
    let $docDel = $(".btn-del");  // 1. 获取删除按钮
    $docDel.click(function () {   // 2. 点击触发事件
        let _this = this;
        let sDocId = $(this).parents('tr').data('id');
        let sDocTile = $(this).parents('tr').data('name');
        fAlert.alertConfirm({
            title: "确定删除文档吗？",
            type: "error",
            confirmText: "确认删除",
            cancelText: "取消删除",
            confirmCallback: function confirmCallback() {

                $.ajax({
                    url: "/admin/docs/" + sDocId + "/",  // url尾部需要添加/
                    // 请求方式
                    type: "DELETE",
                    dataType: "json",
                })
                    .done(function (res) {
                        if (res.errno === "0") {
                            message.showSuccess("文档删除成功");
                            $(_this).parents('tr').remove();
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