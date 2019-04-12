$(function () {
  let $closeBtn = $('.close-btn');  // 删除轮播图按钮
  let $bannerList = $(".banner-list");
  let $updateBtn = $(".update-btn");  // 保存按钮
  let $bannerAddBtn = $("#banner-add-btn");  // 添加轮播图按钮

  let $bannerImage = $(".banner-image");  // 获取图片元素
  let $bannerImageSelect = $('input[name=banner-image-select]');  // image input元素

  // 删除轮播图
  $closeBtn.click(function () {
    let _this = this;
    let sBannerId = $(this).parents('li').data("banner-id");
    fAlert.alertConfirm({
      "title": "删除轮播图",
      "type": "error",
      "confirmText": "确认",
      "confirmCallback": function () {

        $.ajax({
          // 请求地址
          url: "/admin/banners/" + sBannerId + "/",  // url尾部需要添加/
          // 请求方式
          type: "DELETE",
          dataType: "json",
        })
          .done(function (res) {
            if (res.errno === "0") {
              message.showSuccess("标签删除成功");
              $(_this).parents('li').remove();
            } else {
              message.showError(res.errmsg);
            }
          })
          .fail(function () {
            message.showError('服务器超时，请重试！');
          });

      }

    })
  });


  // 更新轮播图
  $updateBtn.click(function () {
    // let _this = this;
    let imageUrl = $(this).parents('li').find('.banner-image').attr("src");
    let priority = $(this).parents('li').find('#priority').val();
    let bannerId = $(this).parents('li').data("banner-id");

    // 未更新之前的原始值
    let sSrcPriority = $(this).data('priority');  // 未更新之前的优先级
    let sImageUrl = $(this).data('image-url');    // 未更新之前的图片url
    if (!imageUrl) {
      message.showError('轮播图url为空');
      return
    }

    if (priority == sSrcPriority && imageUrl === sImageUrl) {
      message.showError('未修改任何值');
      return
    }

    let sDataParams = {
      "image_url": imageUrl,
      "priority": priority,
      "banner_id": bannerId
    };


    $.ajax({
      // 请求地址
      url: "/admin/banners/" + bannerId + "/",  // url尾部需要添加/
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
          message.showSuccess("更新成功");
          // fAlert.alertSuccessToast("更新成功");

          setTimeout(function () {
            window.location.href = '/admin/banners/';
          }, 900)
        } else {
          swal.showInputError(res.errmsg);
        }
      })

      .fail(function () {
        message.showError('服务器超时，请重试！');
      });

  });


  // 上传轮播图片
  $bannerImage.click(function () {
    $(this).prev().click();
  });
  $bannerImageSelect.change(function () {
    let _this = this;
    // 获取文件对象
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
          let sImageUrl = res["data"]["image_url"];
          $(_this).next().attr('src', sImageUrl);
        } else {
          message.showError(res.errmsg)
        }
      })
      .fail(function () {
        message.showError('服务器超时，请重试！');
      });

  });


  // 添加轮播图
  $bannerAddBtn.click(function () {
    if ($bannerList.find('li').length < 6) {
      window.location.href = '/admin/banners/add/';
    } else {
      message.showError("最多只能添加6个轮播图")
    }
  });

});