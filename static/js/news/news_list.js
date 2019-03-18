$(function () {
    let $news_li = $('.news-nav ul li');
    let $ipage = 1;  // 默认为第一页
    let $curren_tagid = 0; // 默认tag_id 为0
    let $total_page = 1;  // 默认总页数为1
    let $bIsLoadData = true;   // 是否正在向后台加载数据

    //  页面一加载调用 load_more  函数
    load_more();

    //  点击切换分类标签
    $news_li.click(function () {
        // 给被点击标签加上active 属性 其他兄弟元素去掉 active 属性
        $(this).addClass('active').siblings('li').removeClass('active');
        //  获取当前元素的 tag_id
        let $itag_id = $(this).children('a').attr('data-id');
        if($itag_id !== $curren_tagid){
            $curren_tagid = $itag_id;
            $ipage = 1;
            $total_page =1;
            // 调用函数
            load_more()
        }

    });

      //页面滚动加载相关
  $(window).scroll(function () {
    // 浏览器窗口高度
    let showHeight = $(window).height();

    // 整个网页的高度
    let pageHeight = $(document).height();

    // 页面可以滚动的距离
    let canScrollHeight = pageHeight - showHeight;

    // 页面滚动了多少,这个是随着页面滚动实时变化的
    let nowScroll = $(document).scrollTop();

    if ((canScrollHeight - nowScroll) < 100) {
      // 判断页数，去更新新闻数据
      if (!$bIsLoadData) {
        $bIsLoadData = true;
        // 如果当前页数据如果小于总页数，那么才去加载数据
        if ($ipage < $total_page) {
          $ipage += 1;
          $(".btn-more").remove();  // 删除标签
          // 去加载数据
          load_more()
        } else {
          message.showInfo('已全部加载，没有更多内容！');
          $(".btn-more").remove();  // 删除标签
          $(".news-list").append($('<a href="javascript:void(0);" class="btn-more">已全部加载，没有更多内容！</a>'))
        }
      }
    }
  });

    //  定义加载更多函数
    function load_more() {
        let $data = {
            'page': $ipage,
            'tag_id': $curren_tagid
        };
        $.ajax({
            url: '/news/',
            dataType: 'json',
            type: 'GET',
            data: $data,
        })

        .done(function (res) {
                if (res.errno === '0') {
                    $total_page = res.data.total_page;
                    if ($ipage === 1) {
                        $('.news-list').html("")
                    }
                    res.data.news.forEach(function (one_news) {
                        let content = `<li class="news-item">
                      <a href="/detail/${one_news.id}/" class="news-thumbnail"
                         target="_blank">
                          <img src="${one_news.image_url}" alt="${one_news.title}"
                               title="${one_news.title}">
                      </a>
                      <div class="news-content">
                          <h4 class="news-title"><a
                                  href="/detail/${one_news.id}/">${one_news.title}</a>
                          </h4>
                          <p class="news-details">${one_news.digest}</p>
                          <div class="news-other">
                              <span class="news-type">${one_news.tag_name}</span>
                              <span class="news-time">${one_news.update_time}</span>
                              <span class="news-author">${one_news.author}</span>
                          </div>
                      </div>
                  </li>`;
                        $('.news-list').append(content);
                    });
                        $(".news-list").append($('<a href="javascript:void(0);" class="btn-more">滚动加载更多</a>'));
                        // 数据加载完毕，设置正在加载数据的变量为false，表示当前没有在加载数据
                        $bIsLoadData = false;
                }else {
                    message.showError(res.errmeg)
                }
            })
            .fail(function (res) {
                message.showError('服务器超时请重试')
            })

    }


});