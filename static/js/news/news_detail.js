// 在static/js/news/news_detail.js中加入如下代码：

$(function () {
    // 未登录提示框
    let $loginComment = $('.please-login-comment input');
    let $send_comment = $('.comment-btn');

    $('.comment-list').delegate('a,input', 'click', function () {

        let sClassValue = $(this).prop('class');

        if (sClassValue.indexOf('reply_a_tag') >= 0) {
            $(this).next().toggle();
        }

        if (sClassValue.indexOf('reply_cancel') >= 0) {
            $(this).parent().toggle();
        }

        if (sClassValue.indexOf('reply_btn') >= 0) {
            // 获取新闻id、评论id、评论内容
            let $this = $(this);
            let news_id = $this.parent().attr('news-id');
            let parent_id = $this.parent().attr('comment-id');
            let content = $this.prev().val();
            ;

            if (!content) {
                message.showError('请输入评论内容！');
                return
            }
            // 定义发给后端的参数
            let sDataParams = {
                "content": content,
                "parent_id": parent_id
            };
            $.ajax({
                url: "/detail/" + news_id + "/",
                type: "POST",
                contentType: "application/json; charset=utf-8",
                data: JSON.stringify(sDataParams),
                dataType: "json",
            })
                .done(function (res) {
                    if (res.errno === "0") {
                        let one_comment = res.data;
                        let html_comment = ``;
                        html_comment += `
          <li class="comment-item">
            <div class="comment-info clearfix">
              <img src="/static/images/avatar.jpeg" alt="avatar" class="comment-avatar">
              <span class="comment-user">${one_comment.author_username}</span>
            </div>
            <div class="comment-content">${one_comment.content}</div>

                <div class="parent_comment_text">
                  <div class="parent_username">${one_comment.parent_author_username}</div>
                  <br/>
                  <div class="parent_content_text">
                    ${one_comment.parent_content}
                  </div>
                </div>

              <div class="comment_time left_float">${one_comment.update_time}</div>
              <a href="javascript:;" class="reply_a_tag right_float">回复</a>
              <form class="reply_form left_float" comment-id="${one_comment.comment_id}" news-id="${one_comment.comment_news_id}">
                <textarea class="reply_input"></textarea>
                <input type="button" value="回复" class="reply_btn right_float">
                <input type="reset" name="" value="取消" class="reply_cancel right_float">
              </form>

          </li>`;

                        $(".comment-list").prepend(html_comment);
                        $this.prev().val('');   // 请空输入框
                        $this.parent().hide();  // 关闭评论框

                    } else if (res.errno === "4101") {
                        // 用户未登录
                        message.showError(res.errmsg);
                        setTimeout(function () {
                            // 重定向到打开登录页面
                            window.location.href = "/user/login/";
                        }, 800)

                    } else {
                        // 失败，打印错误信息
                        message.showError(res.errmsg);
                    }
                })
                .fail(function () {
                    message.showError('服务器超时，请重试！');
                });

        }
    });


    // 点击评论框，重定向到用户登录页面
    $loginComment.click(function () {

        $.ajax({
            url: "/detail/" + $(".please-login-comment").attr('news-id') + "/",
            type: "POST",
            contentType: "application/json; charset=utf-8",
            dataType: "json",
        })
            .done(function (res) {
                if (res.errno === "4101") {
                    message.showError("请登录之后再评论！");
                    setTimeout(function () {
                        // 重定向到打开登录页面
                        window.location.href = "/users/login/";
                    }, 800)

                } else {
                    // 失败，打印错误信息
                    message.showError(res.errmsg);
                }
            })
            .fail(function () {
                message.showError('服务器超时，请重试！');
            });
    });

    // 发表评论
    $send_comment.click(function () {
        // 获取新闻id、评论id、评论内容
        //   console.log('asd');
        let $this = $(this);
        let news_id = $this.parent().attr('news-id');
        // let parent_id = $this.parent().attr('comment-id');
        let content = $(".input_comment").val();
        // console.log(content);

        if (!content) {
            message.showError('请输入评论内容！');
            return
        }
        // 定义发给后端的参数
        let sDataParams = {
            "content": content
        };
        $.ajax({
            url: "/detail/" + news_id + "/",
            type: "POST",
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify(sDataParams),
            dataType: "json",
        })
            .done(function (res) {
                if (res.errno === "0") {
                    let one_comment = res.data;
                    let html_comment = ``;
                    html_comment += `
          <li class="comment-item">
            <div class="comment-info clearfix">
              <img src="/static/images/avatar.jpeg" alt="avatar" class="comment-avatar">
              <span class="comment-user">${one_comment.author_username}</span>
            </div>
            <div class="comment-content">${one_comment.content}</div>

              <div class="comment_time left_float">${one_comment.update_time}</div>
              <a href="javascript:;" class="reply_a_tag right_float">回复</a>
              <form class="reply_form left_float" comment-id="${one_comment.comment_id}" news-id="${one_comment.comment_news_id}">
                <textarea class="reply_input"></textarea>
                <input type="button" value="回复" class="reply_btn right_float">
                <input type="reset" name="" value="取消" class="reply_cancel right_float">
              </form>

          </li>`;

                    $(".comment-list").prepend(html_comment);
                    $this.prev().val('');   // 请空输入框
                    // $this.parent().hide();  // 关闭评论框

                } else if (res.errno === "4101") {
                    // 用户未登录
                    message.showError(res.errmsg);
                    setTimeout(function () {
                        // 重定向到打开登录页面
                        window.location.href = "/user/login/";
                    }, 800)

                } else {
                    // 失败，打印错误信息
                    message.showError(res.errmsg);
                }
            })
            .fail(function () {
                message.showError('服务器超时，请重试！');
            });
         // get cookie using jQuery
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      let cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        let cookie = jQuery.trim(cookies[i]);
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
  }

  // Setting the token on the AJAX request
  $.ajaxSetup({
    beforeSend: function (xhr, settings) {
      if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
      }
    }
  });
});
    });

