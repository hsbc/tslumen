$("a[href^='#'].anchor").on('click', function (e) {
    e.preventDefault();
    var hash = this.hash;
    $('html, body').animate({
        scrollTop: $(hash).offset().top
    }, 300, function () {
        window.location.hash = hash;
    });
});
$("img.img-plot").on('click', function (e) {
	$("#img-modal-img").attr("src", this.src);
	$("#img-modal").modal('show');
});

function copyClipboard(input_id) {
  var copyText = document.querySelector(input_id);
  copyText.select();
  document.execCommand("copy");
}