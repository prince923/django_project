$(function () {
    // 用户图片验证码
    let $img = $(".form-item .captcha-graph-img img");  // 获取图像标签
    let sImageCodeId = "";  // 定义图像验证码ID值

    generateImageCode();  // 生成图像验证码图片
    $img.click(generateImageCode);  // 点击图片验证码生成新的图片验证码图片

    // 生成一个图片验证码的编号，并设置页面中图片验证码img标签的src属性
    function generateImageCode() {
        // 1、生成一个图片验证码随机编号
        sImageCodeId = generateUUID();
        // 2、拼接请求url /verification/image_codes/<uuid:image_code_id>/
        let imageCodeUrl = "/verification/image_codes/" + sImageCodeId + "/";
        // 3、修改验证码图片src地址
        $img.attr('src', imageCodeUrl)
    }

    // 生成图片UUID验证码
    function generateUUID() {
        let d = new Date().getTime();
        if (window.performance && typeof window.performance.now === "function") {
            d += performance.now(); //use high-precision timer if available
        }
        let uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
            let r = (d + Math.random() * 16) % 16 | 0;
            d = Math.floor(d / 16);
            return (c == 'x' ? r : (r & 0x3 | 0x8)).toString(16);
        });
        return uuid;
    };

    //   用户名验证
    let $usernameinput = $("#username");
    $usernameinput.blur(function () {
        checkusername()
    });

    // 判断用户名是否存在
    function checkusername() {
        let username = $usernameinput.val();
        let result = "";

        if (username === "") {
            message.showError('用户名不能为空！');
            return
        }
        if (!(/^\w{5,20}$/).test(username)) {
            message.showError('请输入5-20个字符的用户名');
            return
        }

        $.ajax({
            type: "GET",
            url: "/user/username/" + username + "/",
            dataType: "json",
            async: false
        })
            .done(function (res) {
                if (res.data.count == 0) {
                    message.showSuccess("此用户名可以正常使用")
                    result = "success"
                } else {
                    message.showError("此用户名已被注册")
                    result = ""
                }
            })

            .fail(function (res) {
                message.showError("服务器超时请重试!")
                result = ""
            });
        return result

    }

    // 判断手机号是否存在
    let $mobileinput = $("#mobile");
    $mobileinput.blur(
        function () {
            checkmobile()
        }
    )

    function checkmobile() {
        let mobile = $mobileinput.val();
        let result = "";
        if (mobile === "") {
            message.showError("手机号不能为空");
            return
        }
        ;
        if (!(/^1[345789]\d{9}$/).test(mobile)) {
            message.showError("手机号格式不正确请重新输入");
            return
        }
        ;
        $.ajax({
            type: 'GET',
            url: "/user/mobile/" + mobile + "/",
            dataType: "json",
            async: false
        })
            .done(function (res) {
                if (res.data.count === "1") {
                    message.showError("此手机号码已被注册");
                    result = ""
                } else {
                    // message.showSuccess("此手机号可以使用");
                    result = "success"

                }
            })

            .fail(function (res) {
                message.showError("服务器超时请重试");
                result = ""
            });
        return result
    }

    //发送手机短信验证码认证
    let $SmsBtn = $(".sms-captcha");
    let $img_input = $(".form-captcha");
    $SmsBtn.click(function () {
        if (checkmobile() !== "success") {
            message.showError("手机号验证有误");
            return
        }

        if (!sImageCodeId) {
            message.showError("图片uuid不能为空");
            return
        }
        let text = $img_input.val();
        if (!text) {
            message.show("图片验证码不能为空");
            return
        }
        let mobile = $mobileinput.val();
        let data = {
            "mobile": mobile,
            "text": text,
            "image_code_id": sImageCodeId,
        };
        //   发起请求
        console.log(data);
        $.ajax({
            url: "/user/sms_codes/",
            type: "POST",
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            data: JSON.stringify(data),
            async: false,
        })
            .done(function (res) {
                if (res.errno === "0") {
                    message.showSuccess("短信验证码发送成功");
                    // 设置计数器
                    let num = 60;
                    let t = setInterval(function () {
                        if (num === 1) {
                            clearInterval(t);
                            $SmsBtn.html('获取短信验证码')
                        }
                        else {
                            num -= 1;
                            $SmsBtn.html(num + "秒")
                        }
                    }, 1000)
                } else {
                    message.showError(res.errmsg)
                }

            })
            .fail(function (res) {
                message.showError("服务器连接超时,请重试")
            })


    })


    // 最终注册
    // 注意这里获取的不是注册按钮的元素，而是form表单的元素
    let $registerform = $(".form-contain");
    $registerform.submit(function (e) {
        //  关闭form表单默认的提交事件
        e.preventDefault();
        let $username = $("input[name=username]").val();
        let $password = $("input[name=password]").val();
        let $password_repeat = $("input[name=password_repeat]").val();
        let $mobile = $("input[name=telephone]").val();
        let $captcha_graph = $("input[name=captcha_graph]").val();
        let $sms_code = $("input[name=sms_captcha]").val();
        // console.log($username,$password,$password_repeat,$mobile,$captcha_graph,$sms_captcha)

        // 验证用户名是否符合要求
        if (checkusername() !== "success") {
            return
        }

        // 验证手机号是否符合要求
        if (checkmobile() !== "success") {
            return
        }
        // 判断两次密码的长度是否符合要求
        if (($password.length < 6 || $password.length > 20 ||
                $password_repeat.length < 6 || $password_repeat.length > 20)) {
            message.showError("密码长度以及重复密码长度为6-20");
            return
        }
        // 判断两次密码是否相等
        if ($password !== $password_repeat) {
            message.showError("两次密码不相等");
            return
        }

        // 判断用户输入的短信验证码是否为6位数字
        if (!(/^\d{6}$/).test($sms_code)) {
            message.showError('短信验证码格式不正确，必须为6位数字！');
            return
        }

        //   发起注册请求
        let  data = {
            "username":$username,
            "password":$password,
            "password_repeat":$password_repeat,
            "mobile":$mobile,
            "sms_code":$sms_code
        };
        console.log(data);
        $.ajax({
            url: '/user/register/',
            type: "POST",
            data: JSON.stringify(data),
      // 请求内容的数据类型（前端发给后端的格式）
            contentType: "application/json; charset=utf-8",
      // 响应数据的格式（后端返回给前端的格式）
            dataType: "json",
        })

            .done(function (res) {
                if(res.errno == "0"){
                    message.showSuccess(res.errmsg);
                    setTimeout(function () {
                    // 注册成功之后重定向到主页
                window.location.href = document.referrer;
          }, 1000)
                }else {
                    message.showError(res.errmsg)
                }
            })

            .fail(function (res) {
                message.showError("服务器超时请重试!")
            })



    })
});