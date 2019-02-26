/*=== bannerStart ===*/
$(()=>{
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
