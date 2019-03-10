$(function () {
    // 登陆
    // 获取表单
    let loginform = $(".form-contain");
    loginform.submit(function (e) {
        e.preventDefault();
        // 获取用户信息
        let $useraccount = $("input[name=telephone]").val();
        // 获取密码
        let $password = $("input[name=password]").val();

        if ($useraccount === "") {
            message.showError("用户信息不能为空")
            return
        }

        if (!(/^1[3-9]\d{9}$/).test($useraccount) && !(/^\w{5,20}/).test($useraccount)) {
            message.showError("手机号或用户名填写有误");
            return
        }
        if ($password === "") {
            message.showError("密码不能为空");
            return
        }

        if ($password.length < 6 || $password.length > 16) {
            message.showError("密码长度为5-20位");
            return
        }

        // 判断是否勾选了记住我，如果勾选了为True 否则为False
        let bstatus = $("input[type=checkbox]").is(":checked");

        // 发起请求
        let data = {
            "user_account":$useraccount,
            "password":$password,
            "remember_me":bstatus,
        };
        $.ajax({
            url : "/user/login/",
            type: "POST",
            data: JSON.stringify(data),
      // 请求内容的数据类型（前端发给后端的格式）
            contentType: "application/json; charset=utf-8",
      // 响应数据的格式（后端返回给前端的格式）
            dataType: "json",
        })
            .done(function (res) {
                if (res.errno === "0"){
                    message.showSuccess(res.errmsg)
                    setTimeout(function () {
                        // 登陆成功后跳转到前一个页面
                        window.location.href = document.referrer;
                    })
                }else {message.showError(res.errmsg)}
            })

            .fail(function (res) {
                message.showError("服务器超时请重试!")
            })


    })
});