	$(function() {
	$(".fab").hover(function(){
		$(".fab_text",this).css({"display": "block"})
	},function() {
		$(".fab_text",this).css({"display": "none"})
	});
	$(".fab-children").hover(function() {
			$(".fab-children").css({"height":(parseInt($("#masterfab").css("bottom")) + parseInt($("#masterfab").outerHeight()) + 55 * 1- $(".fab.child").outerHeight()) + "px"});
			$(".fab.child").each(function() {
				$(this)
					.stop()
					.show()
					.animate({
						bottom	: (parseInt($("#masterfab").css("bottom")) + parseInt($("#masterfab").outerHeight()) + 55 * $(this).data("subitem") - $(".fab.child").outerHeight()) + "px",
						opacity	: 1
					},125);
			});
		}, function() {
			$(".fab-children").css({"height":"56px"});
			$(".fab.child")
				.stop()
				.animate({
					bottom	: $("#masterfab").css("bottom"),
					opacity	: 0
				},125,function(){
					$(this).hide();
				});
	});
});