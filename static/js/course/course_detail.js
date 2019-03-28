$(function () {
  let $course_data = $(".course-data");
  let sVideoUrl = $course_data.data('video-url');
  let sCoverUrl = $course_data.data('cover-url');

  let player = cyberplayer("course-video").setup({
    width: '100%',
    height: 650,
    file: sVideoUrl,
    image: sCoverUrl,
    autostart: false,
    stretching: "uniform",
    repeat: false,
    volume: 100,
    controls: true,
    ak: '7d30644f2e04436d8e5608d3f9a37477'
  });

});