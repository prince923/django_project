/*=== bannerStart ===*/

$(()=>{
    load_banner();
    let $banner = $('.banner');
    let $picLi = $(".banner .pic li");
    let $prev = $('.banner .prev');
    let $next = $('.banner .next');
    let $tabLi = $('.banner .tab li');
    let index = 0;
    // 小原点
    $tabLi.click(function(){
        index = $(this).index();
        $(this).addClass('active').siblings('li').removeClass('active');
        $picLi.eq(index).fadeIn(1500).siblings('li').fadeOut(1500);
    });
    // 点击切换上一张
    $prev.click(()=>{
        index--;
        if(index<0){index = $tabLi.length-1}
        $tabLi.eq(index).addClass('active').siblings('li').removeClass('active');
        $picLi.eq(index).fadeIn(1500).siblings('li').fadeOut(1500);
    }).mousedown(()=> false);
    // 点击切换下一张
    $next.click(()=>{
        auto();
    }).mousedown(()=> false);
    //  图片向前滑动
    function auto(){
        index++;
        index %= $tabLi.length;
        $tabLi.eq(index).addClass('active').siblings('li').removeClass('active');
        $picLi.eq(index).fadeIn(1500).siblings('li').fadeOut(1500);
    }
    // 定时器
    let timer = setInterval(auto, 2500);
    $banner.hover(()=>{clearInterval(timer)}, ()=>{auto()})
});
/*=== bannerEnd ===*/
/*=== newsNavStart ===*/
$(()=>{
    let $newsLi = $('.news-nav ul li');
    $newsLi.click(function(event) {
        $(this).addClass('active').siblings('li').removeClass('active');
    });
});
/*=== newsNavEnd ===*/

function load_banner () {
       $.ajax({
        url:'/banner/',
        type:'GET',
        dataType:'json',
        async: false
    })
         .done(function (res) {
        if (res.errno === "0") {
          let content = ``;
          let tab_content = ``;
          res.data.banners.forEach(function (one_banner, index) {
            if (index === 0){
              content = `
                <li style="display:block;"><a href="/detail/${one_banner.news_id}/">
                 <img src="${one_banner.image_url}" alt="${one_banner.news_title}"></a></li>
              `;
              tab_content = `<li class="active"></li>`;
            } else {
              content = `
              <li><a href="/detail/${one_banner.news_id}/"><img src="${one_banner.image_url}" alt="${one_banner.news_title}"></a></li>
              `;
              tab_content = `<li></li>`;
            }

            $(".pic").append(content);
            $(".tab").append(tab_content)
          });

        } else {
          // 登录失败，打印错误信息
          message.showError(res.errmsg);
        }
      })
     .fail(function (res) {
        window.showError('服务器连接超时请重试')
    });
}