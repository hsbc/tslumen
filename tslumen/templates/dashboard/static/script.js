$( document ).ready(function() {
  $("a[href^='#'].anchor").on('click', function (e) {
    alert(e);
    e.preventDefault();
    var hash = this.hash;
    $('html, body').animate({
      scrollTop: $(hash).offset().top
    }, 300, function () {
      window.location.hash = hash;
    });
  });
});
function copyClipboard(input_id) {
  var copyText = document.querySelector(input_id);
  copyText.select();
  document.execCommand("copy");
}