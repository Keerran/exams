function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

function updateAvgs(data) {
    $("#avg_score").text(Math.round(data["avg_score"]) + " / " + data["max_score"]);
    $("#avg_time").text(Math.round(data["avg_time"]));
}

function sub(pk) {
    $.ajax({
        type: "POST",
        url: "/tests/delete",
        data: {
            "pk": pk
        },
        dataType: "json",
        success: function(data) {
            $("#" + pk).parents("tr").remove();
            updateAvgs(data);
        }
    })
}

$("#add").submit(function (event) {
    $.ajax({
        type: "POST",
        url: window.location.pathname,
        data: {
            "score": $("#score").val(),
            "minutes_left": $("#minutes_left").val()
        },
        dataType: "json",
        success: function(data) {
            var el = $("<tr>" +
                "<td>" + data["score"] + "</td>" +
                "<td>" + data["percentage"] + "</td>" +
                "<td>" + data["minutes_left"] + "</td>" +
                "<td><form class=\"del\" id=\"" + data["pk"] + "\" action=\"javascript:;\">" +
                "<button name=\"pk\" type=\"submit\"><i class=\"material-icons\">delete</i></button>" +
                "</form></td>" +
                "</tr>");
            el.find("form").submit(function() {
                sub(data["pk"])
            });
            $("tbody").append(el);
            $("#error").text();
            $("#score").focus()
            updateAvgs(data);
        }
    });
    $(this)[0].reset()
});

$(".del").submit(function() {
    sub($(this).attr("id"));
});