
$(function () {
  let $tagSelect = $("#category-select");   // 获取选择分类标签元素
  let $newsSelect = $("#news-select");      // 获取选择文章标签元素
  let $saveBtn = $('#save-btn');            // 获取保存按钮元素

  // 选择文章不同类别，获取相应的文章
  $tagSelect.change(function () {
    // 获取当前选中的下拉框的value
    let sTagId = $(this).val();
    if (sTagId === '0') {
      $newsSelect.children('option').remove();
      $newsSelect.append(`<option value="0">--请选择文章--</option>`);
      return
    }
    // 根据文章分类id向后端发起get请求
    $.ajax({
      url: "/admin/tags/" + sTagId + "/news/",  // url尾部需要添加/
      type: "GET",
      dataType: "json",
    })
      .done(function (res) {
        if (res.errno === "0") {

          $newsSelect.children('option').remove();
          $newsSelect.append(`<option value="0">--请选择文章--</option>`);
          res.data.news.forEach(function (one_news) {
            let content = `<option value="${one_news.id}">${one_news.title}</option>`;
            $newsSelect.append(content)
          });

        } else {
          // swal.showInputError(res.errmsg);
          fAlert.alertErrorToast(res.errmsg);
        }
      })
      .fail(function () {
        message.showError('服务器超时，请重试！');
      });

  });

  // 点击保存按钮执行的事件
  $saveBtn.click(function () {
    // 获取优先级
    let priority = $("#priority").val();
    // 获取下拉框中选中的文章标签id 和 文章id
    let sTagId = $tagSelect.val();
    let sNewsId = $newsSelect.val();
    // 打印值
    console.log(`
          priority(优先级): ${priority}
          tagId(文章标签id): ${sTagId}
          newsId(文章id): ${sNewsId}
    `);
    // 判断是否为 0, 表示在第一个 未选择
    if (sTagId !== '0' && sNewsId !== '0' && priority !== '0') {

      let sDataParams = {
        "priority": priority,
        "news_id": sNewsId
      };

      $.ajax({
        // 请求地址
        url: "/admin/addhotnews/",  // url尾部需要添加/
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
            message.showSuccess("热门文章创建成功");

            setTimeout(function () {
              window.location.href = '/admin/hotnews/';
            }, 800)
          } else {
            // swal.showInputError(res.errmsg);
            message.showError(res.errmsg);
          }
        })

        .fail(function () {
          message.showError('服务器超时，请重试！');
        });

    } else {
      message.showError("文章分类、文章以及优先级都要选！");
    }
  });

});