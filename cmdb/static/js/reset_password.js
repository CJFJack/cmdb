
$.urlParam = function(name){
    var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
    if (results==null){
       return null;
    }
    else{
       return decodeURIComponent(results[1]) || 0;
    }
}

$(document).ready(function() {

    $("#msg").hide();

    $("#reset_password").click( function(){
        var new_passwd1 = $("#new_passwd1").val();
        var new_passwd2 = $("#new_passwd2").val();

        if (new_passwd1 == ''){
            $("#msg").text('请输入密码!');
            $("#msg").show();
            return false;
        }

        if (new_passwd2 == ''){
            $("#msg").text('请确认密码!');
            $("#msg").show();
            return false;
        }

        if (new_passwd1 != new_passwd2){
            $("#msg").text('两次输入密码不同!');
            $("#msg").show();
            return false;
        }

        var token = $.urlParam('token');

        var data = {
            'token': token,
            'new_passwd1': new_passwd1,
            'new_passwd2': new_passwd2,
        };

        var encoded = $.toJSON(data);
        var pdata = encoded;

        $.ajax({
            type: "POST",
            url: "/users/reset_password/",
            contentType: "application/json; charset=utf-8",
            data: pdata,
            success: function (data) {
                console.log(data);
                if (data.success) {
                    var redirect_url = '/user_login/';
                    window.location.href = redirect_url;
                } else {
                    $("#msg").text(data.data);
                    $("#msg").show();
                    return false;
                }
            }
        });

    } );


} );
