$(function () {
    // 获取修改之前的值
    let noModifyIsStaff = $("input[name='login_admin']:checked").val();
    let noModifyIsSuperuser = $("input[name='is_superuser']:checked").val();
    let noModifyIsActive = $("input[name='is_active']:checked").val();
    let noModifyGroups = $("#add_group").val();

    // ================== 删除用户 ================
    let $userDel = $(".btn-del");  // 1. 获取删除按钮
    $userDel.click(function () {   // 2. 点击触发事件
        let _this = this;
        let sUserId = $(this).parents('tr').data('id');
        let sUserName = $(this).parents('tr').data('name');

        fAlert.alertConfirm({
            title: `确定删除 ${sUserName} 这个用户吗？`,
            type: "error",
            confirmText: "确认删除",
            cancelText: "取消删除",
            confirmCallback: function confirmCallback() {

                $.ajax({
                    url: "/admin/users/" + sUserId + "/",  // url尾部需要添加/
                    // 请求方式
                    type: "DELETE",
                    dataType: "json",
                })
                    .done(function (res) {
                        if (res.errno === "0") {
                            message.showSuccess("用户删除成功");
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


    // ================== 修改用户 ================
    let $usersBtn = $("#btn-edit-user");
    $usersBtn.click(function () {
        // 判断用户信息是否修改
        // 获取修改之后的值
        let modifiedIsStaff = $("input[name='login_admin']:checked").val();
        let modifiedIsSuperuser = $("input[name='is_superuser']:checked").val();
        let modifiedIsActive = $("input[name='is_active']:checked").val();
        let modifiedGroups = $("#add_group").val();

        if (noModifyIsStaff === modifiedIsStaff && noModifyIsSuperuser === modifiedIsSuperuser
            && noModifyIsActive === modifiedIsActive &&
            (JSON.stringify(noModifyGroups) === JSON.stringify(modifiedGroups))) {
            message.showError('用户信息未修改！');
            return
        }

        // 获取userId
        let userId = $(this).data("user-id");
        let url = '/admin/users/' + userId + '/';
        let data = {
            "is_staff": modifiedIsStaff,
            "is_superuser": modifiedIsSuperuser,
            "is_active": modifiedIsActive,
            "groups": modifiedGroups

        };

        $.ajax({
            // 请求地址
            url: url,
            // 请求方式
            type: 'PUT',
            data: JSON.stringify(data),
            // 请求内容的数据类型（前端发给后端的格式）
            contentType: "application/json; charset=utf-8",
            // 响应数据的格式（后端返回给前端的格式）
            dataType: "json",
        })
            .done(function (res) {
                if (res.errno === "0") {
                    fAlert.alertNewsSuccessCallback("用户信息更新成功", '跳到用户管理页', function () {
                        window.location.href = '/admin/users/'
                    })
                } else {
                    fAlert.alertErrorToast(res.errmsg);
                }
            })
            .fail(function () {
                message.showError('服务器超时，请重试！');
            });

    });

});