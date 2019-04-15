$(function () {

    // 删除组
    let $groupDel = $(".btn-del");  // 1. 获取删除按钮
    $groupDel.click(function () {   // 2. 点击触发事件
        let _this = this;
        let sGroupId = $(this).parents('tr').data('id');
        let sGroupName = $(this).parents('tr').data('name');
        // 获取用户个数
        let num_users = $(this).parents('tr').find('td:nth-child(2)').html();
        // 判断组成员是否为空
        if (num_users > '0') {
            message.showError('组成员不为空，无法删除！');
            return
        }

        fAlert.alertConfirm({
            title: `确定删除 ${sGroupName} 吗？`,
            type: "error",
            confirmText: "确认删除",
            cancelText: "取消删除",
            confirmCallback: function confirmCallback() {

                $.ajax({
                    url: "/admin/groups/" + sGroupId + "/",  // url尾部需要添加/
                    // 请求方式
                    type: "DELETE",
                    dataType: "json",
                })
                    .done(function (res) {
                        if (res.errno === "0") {
                            message.showSuccess("用户组删除成功");
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