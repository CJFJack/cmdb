$(document).ready(function () {

    $("#msg").hide();

    $("#bt-commit").click(function () {
        var new_passwd1 = $("#new_passwd1").val();
        var new_passwd2 = $("#new_passwd2").val();

        if (new_passwd1 == '') {
            $("#msg").text('请输入密码!');
            $("#msg").show();
            return false;
        }

        if (new_passwd2 == '') {
            $("#msg").text('请确认密码!');
            $("#msg").show();
            return false;
        }

        if (new_passwd1 != new_passwd2) {
            $("#msg").text('两次输入密码不同!');
            $("#msg").show();
            return false;
        }

        var data = {
            'new_passwd1': new_passwd1,
            'new_passwd2': new_passwd2,
        };

        var encoded = $.toJSON(data);
        var pdata = encoded;

        $.ajax({
            type: "POST",
            url: "/users/new_passwd/",
            contentType: "application/json; charset=utf-8",
            data: pdata,
            success: function (data) {
                if (data.success) {
                    var redirect_url = '/';
                    window.location.href = redirect_url;
                } else {
                    $("#msg").text(data.data);
                    $("#msg").show();
                    return false;
                }
            }
        });

    });


});
