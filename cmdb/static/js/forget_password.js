

$(document).ready(function() {

    $("#upload-notify").hide();
    $("#upload-notify2").hide();

    $('#email').keypress(function (e) {
        var key = e.which;
        if(key == 13)  // the enter key code
        {
            $('#send_mail').click();
            return false;  
        }
    });   

    $("#send_mail").click( function(){
        var email = $.trim( $("#email").val() );
        if ( ! /^[a-z]+[1-9]?$/.test(email) ){
            $("#upload-notify").show();
            $("#lb-msg-upload").text('格式错误: 请填写你的企业邮箱前缀，例如yanwenchi');
            return false;
        }

        var inputIds = {
            'email': email,
        };

        var urls = "/forget_password/";

        var encoded=$.toJSON( inputIds );
        var pdata = encoded;

        $("#send_mail").text("发送中...");
        $("#send_mail").removeClass('btn-success').addClass('btn-secondary');
        $("#send_mail").prop('disabled', true);

        $.ajax({
            type: "POST",
            url: urls,
            contentType: "application/json; charset=utf-8",
            data: pdata,
            success: function (data) {
                
                if (data.success) {
                    $("#upload-notify2").show();
                    $("#upload-notify").hide();
                    $("#send_mail").text("发送成功");
                }
                else{
                    $("#upload-notify").show();
                    $("#lb-msg-upload").text(data.msg);
                    $("#send_mail").text("发送失败");
                }
            }
        });
    } );


} );
