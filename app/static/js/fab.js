$(function() {
	$(".fab").hover(function(){
		$(".fab_text",this).css({"display": "block"})
	},function() {
		$(".fab_text",this).css({"display": "none"})
	});
	$(".fab-children").css({"height":(parseInt($("#masterfab").css("bottom")) + parseInt($("#masterfab").outerHeight()) + 55 * 1- $(".fab.child").outerHeight()) + "px"});
	$(".fab.child").each(function() {
	    $(this).css({"bottom": (parseInt($("#masterfab").css("bottom")) + parseInt($("#masterfab").outerHeight()) + 55 * $(this).data("subitem") - $(".fab.child").outerHeight()) + "px"})
    })
	$("#masterfab").click(function(e) {
        if(!$(this).hasClass("open")) {
            $(".fab.child").each(function() {
                $(this).css({
                    "transform": "scale(0.8)",
                    "transition": ".4s cubic-bezier(0.25, 1.15, 0.28, 1.25)"
                });
            });
        } else {
            $(".fab.child").each(function() {
                $(this).css({
                    "transform": "scale(0)",
                    "transition": ".4s cubic-bezier(0.72, -0.25, 0.75, 0.15)"
                });
            });
        }
        $(this).toggleClass("open")
        $(".ripple").remove()
        $(this).prepend("<span class='ripple'></span>");
        var offset = $(this).offset(),
            dim = $(this).height();
        var x = e.pageX - offset.left - dim/2,
            y = e.pageY - offset.top - dim/2;
        $(".ripple").css({
            width: dim,
            height: dim,
            top: y,
            left: x
        }).addClass("rippleEffect")
        e.stopPropagation()
	});
	$(".fab.child").click(function(e) {e.stopPropagation();})
    $(document).click(function() {
        $("#masterfab").toggleClass("open", false);
        $(".fab.child").each(function() {
            $(this).css({
                "transform": "scale(0)",
                "transition": ".4s cubic-bezier(0.72, -0.25, 0.75, 0.15)"
            });
		});
    })
});