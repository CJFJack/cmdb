$(document).ready(function () {
    $("[name='my-checkbox']").bootstrapSwitch({
        'size': 'mini',
        'onColor': 'success',
        'onText': '已开启',
        'offText': '已关闭',
    });
    $("[name='my-wechat-checkbox']").bootstrapSwitch({
        'size': 'mini',
        'onColor': 'success',
        'onText': '已开启',
        'offText': '已关闭',
    });
    $('#bt-save').click(function () {
        var hot_update_email_approve = $('input[name="my-checkbox"]').bootstrapSwitch('state');

        var inputIds = {
            'hot_update_email_approve': hot_update_email_approve,
        };

        var urls = "/users/set_email_approve/";

        var encoded = $.toJSON(inputIds);
        var pdata = encoded;

        $.ajax({
            type: "POST",
            url: urls,
            contentType: "application/json; charset=utf-8",
            data: pdata,
            success: function (data) {
                if (data['data']) {
                    $.toast({
                        text: "保存成功", // Text that is to be shown in the toast
                        heading: 'Success', // Optional heading to be shown on the toast
                        icon: 'success', // Type of toast icon
                        showHideTransition: 'slide', // fade, slide or plain
                        allowToastClose: true, // Boolean value true or false
                        hideAfter: 1000, // false to make it sticky or number representing the miliseconds as time after which toast needs to be hidden
                        stack: 5, // false if there should be only one toast at a time or a number representing the maximum number of toasts to be shown at a time
                        position: 'top-center', // bottom-left or bottom-right or bottom-center or top-left or top-right or top-center or mid-center or an object representing the left, right, top, bottom values
                        textAlign: 'left',  // Text alignment i.e. left, right or center
                        loader: true,  // Whether to show loader or not. True by default
                        loaderBg: '#9EC600',  // Background color of the toast loader
                        beforeShow: function () {
                            $("#bt-save").removeClass('btn-primary').addClass('btn-secondary');
                            $("#bt-save").prop('disabled', true);
                            $('input[name="my-checkbox"]').bootstrapSwitch('toggleDisabled', true, true)
                        }, // will be triggered before the toast is shown
                        afterShown: function () {
                        }, // will be triggered after the toat has been shown
                        beforeHide: function () {

                        }, // will be triggered before the toast gets hidden
                        afterHidden: function () {
                            $("#bt-save").removeClass('btn-secondary').addClass('btn-primary');
                            $("#bt-save").prop('disabled', false);
                            $('input[name="my-checkbox"]').bootstrapSwitch('toggleDisabled', true, true)
                        }  // will be triggered after the toast has been hidden
                    });
                }
                else {
                    alert(data.msg);
                }
            }
        });
    });

    $('#bt-wechat-save').click(function () {
        var wechat_approve = $('input[name="my-wechat-checkbox"]').bootstrapSwitch('state');

        var inputIds = {
            'wechat_approve': wechat_approve,
        };

        var urls = "/users/set_wechat_approve/";

        var encoded = $.toJSON(inputIds);
        var pdata = encoded;

        $.ajax({
            type: "POST",
            url: urls,
            contentType: "application/json; charset=utf-8",
            data: pdata,
            success: function (data) {
                if (data['data']) {
                    $.toast({
                        text: "保存成功", // Text that is to be shown in the toast
                        heading: 'Success', // Optional heading to be shown on the toast
                        icon: 'success', // Type of toast icon
                        showHideTransition: 'slide', // fade, slide or plain
                        allowToastClose: true, // Boolean value true or false
                        hideAfter: 1000, // false to make it sticky or number representing the miliseconds as time after which toast needs to be hidden
                        stack: 5, // false if there should be only one toast at a time or a number representing the maximum number of toasts to be shown at a time
                        position: 'top-center', // bottom-left or bottom-right or bottom-center or top-left or top-right or top-center or mid-center or an object representing the left, right, top, bottom values
                        textAlign: 'left',  // Text alignment i.e. left, right or center
                        loader: true,  // Whether to show loader or not. True by default
                        loaderBg: '#9EC600',  // Background color of the toast loader
                        beforeShow: function () {
                            $("#bt-wechat-save").removeClass('btn-primary').addClass('btn-secondary');
                            $("#bt-wechat-save").prop('disabled', true);
                            $('input[name="my-wechat-checkbox"]').bootstrapSwitch('toggleDisabled', true, true)
                        }, // will be triggered before the toast is shown
                        afterShown: function () {
                        }, // will be triggered after the toat has been shown
                        beforeHide: function () {

                        }, // will be triggered before the toast gets hidden
                        afterHidden: function () {
                            $("#bt-wechat-save").removeClass('btn-secondary').addClass('btn-primary');
                            $("#bt-wechat-save").prop('disabled', false);
                            $('input[name="my-wechat-checkbox"]').bootstrapSwitch('toggleDisabled', true, true)
                        }  // will be triggered after the toast has been hidden
                    });
                }
                else {
                    alert(data.msg);
                }
            }
        });
    });


});


//提交修改企业QQ请求
$('#bt-qq-commit').click(function () {
    let password = $('#password-ent-qq').val();
    let account = $('#account').val();
    let inputIds = {
        'account': account,
        'password': password,
    };
    let url = "/users/edit_ent_qq/";
    let encoded = $.toJSON(inputIds);
    let p_data = encoded;

    $.ajax({
        type: "POST",
        url: url,
        contentType: "application/json; charset=utf-8",
        data: p_data,
        success: function (data) {
            if (data['data']) {
                $.toast({
                    text: "保存成功", // Text that is to be shown in the toast
                    heading: 'Success', // Optional heading to be shown on the toast
                    icon: 'success', // Type of toast icon
                    showHideTransition: 'slide', // fade, slide or plain
                    allowToastClose: true, // Boolean value true or false
                    hideAfter: 1000, // false to make it sticky or number representing the miliseconds as time after which toast needs to be hidden
                    stack: 5, // false if there should be only one toast at a time or a number representing the maximum number of toasts to be shown at a time
                    position: 'top-center', // bottom-left or bottom-right or bottom-center or top-left or top-right or top-center or mid-center or an object representing the left, right, top, bottom values
                    textAlign: 'left',  // Text alignment i.e. left, right or center
                    loader: true,  // Whether to show loader or not. True by default
                    loaderBg: '#9EC600',  // Background color of the toast loader
                    beforeShow: function () {
                        $("#bt-qq-commit").removeClass('btn-primary').addClass('btn-secondary');
                        $("#bt-qq-commit").prop('disabled', true);
                        $('input[name="my-checkbox"]').bootstrapSwitch('toggleDisabled', true, true)
                    }, // will be triggered before the toast is shown
                    afterShown: function () {
                    }, // will be triggered after the toat has been shown
                    beforeHide: function () {

                    }, // will be triggered before the toast gets hidden
                    afterHidden: function () {
                        $("#bt-qq-commit").removeClass('btn-secondary').addClass('btn-primary');
                        $("#bt-qq-commit").prop('disabled', false);
                        $('input[name="my-checkbox"]').bootstrapSwitch('toggleDisabled', true, true)
                    }  // will be triggered after the toast has been hidden
                });
                $('#modal-notify-ent-qq').attr('class', 'alert alert-success alert-dismissable');
                $('#lb-msg-ent-qq').text(data['msg']);
                $('#modal-notify-ent-qq').show();
                $('#password-ent-qq').val('');
            }
            else {
                $('#modal-notify-ent-qq').attr('class', 'alert alert-danger alert-dismissable');
                $('#lb-msg-ent-qq').text(data['msg']);
                $('#modal-notify-ent-qq').show();
                $('#password-ent-qq').val('');
            }
        }
    });

});


//提交修改企业邮箱请求
$('#bt-email-commit').click(function () {
    var userid = $('input:radio:checked').val();
    let password = $('#password-ent-email').val();
    let re = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[^]{6,32}$/;
    let result = re.test(password);
    if (!userid) {
        $('#modal-notify-ent-email').attr('class', 'alert alert-danger alert-dismissable');
        $('#lb-msg-ent-email').text('请选择重置密码的邮箱');
        $('#modal-notify-ent-email').show();
        $('#password-ent-email').val('');
        return false;
    }
    if (!result) {
        $('#modal-notify-ent-email').attr('class', 'alert alert-danger alert-dismissable');
        $('#lb-msg-ent-email').text('密码要求同时包含大写字母、小写字母和数字，长度为6-32个字符，不包含账号信息与空格，不是常见密码');
        $('#modal-notify-ent-email').show();
        $('#password-ent-email').val('');
        return false;
    }
    let inputIds = {
        'password': password,
        'userid': userid,
    };
    let url = "/users/edit_ent_email/";
    let encoded = $.toJSON(inputIds);
    let p_data = encoded;

    $.ajax({
        type: "POST",
        url: url,
        contentType: "application/json; charset=utf-8",
        data: p_data,
        success: function (data) {
            if (data['data']) {
                $.toast({
                    text: "保存成功", // Text that is to be shown in the toast
                    heading: 'Success', // Optional heading to be shown on the toast
                    icon: 'success', // Type of toast icon
                    showHideTransition: 'slide', // fade, slide or plain
                    allowToastClose: true, // Boolean value true or false
                    hideAfter: 1000, // false to make it sticky or number representing the miliseconds as time after which toast needs to be hidden
                    stack: 5, // false if there should be only one toast at a time or a number representing the maximum number of toasts to be shown at a time
                    position: 'top-center', // bottom-left or bottom-right or bottom-center or top-left or top-right or top-center or mid-center or an object representing the left, right, top, bottom values
                    textAlign: 'left',  // Text alignment i.e. left, right or center
                    loader: true,  // Whether to show loader or not. True by default
                    loaderBg: '#9EC600',  // Background color of the toast loader
                    beforeShow: function () {
                        $("#bt-email-commit").removeClass('btn-primary').addClass('btn-secondary');
                        $("#bt-email-commit").prop('disabled', true);
                        $('input[name="my-checkbox"]').bootstrapSwitch('toggleDisabled', true, true)
                    }, // will be triggered before the toast is shown
                    afterShown: function () {
                    }, // will be triggered after the toat has been shown
                    beforeHide: function () {

                    }, // will be triggered before the toast gets hidden
                    afterHidden: function () {
                        $("#bt-email-commit").removeClass('btn-secondary').addClass('btn-primary');
                        $("#bt-email-commit").prop('disabled', false);
                        $('input[name="my-checkbox"]').bootstrapSwitch('toggleDisabled', true, true)
                    }  // will be triggered after the toast has been hidden
                });
                $('#modal-notify-ent-email').attr('class', 'alert alert-success alert-dismissable');
                $('#lb-msg-ent-email').text(data['msg']);
                $('#modal-notify-ent-email').show();
                $('#password-ent-email').val('');
            }
            else {
                $('#modal-notify-ent-email').attr('class', 'alert alert-danger alert-dismissable');
                $('#lb-msg-ent-email').text(data['msg']);
                $('#modal-notify-ent-email').show();
                $('#password-ent-email').val('');
            }
        }
    });

});


//提交修改SVN密码请求
$('#bt-svn-commit').click(function () {
    let username = $('#account').val();
    let passwd = $('#password-svn').val();
    let re = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[^]{8,32}$/;
    let result = re.test(passwd);
    if (!result) {
        $('#modal-notify-svn').attr('class', 'alert alert-danger alert-dismissable');
        $('#lb-msg-svn').text('密码要求同时包含大写字母、小写字母和数字，长度为8-32个字符，不包含账号信息与空格，不是常见密码');
        $('#modal-notify-svn').show();
        $('#password-svn').val('');
        return false;
    }
    let inputIds = {
        'passwd': passwd,
        'username': username,
    };
    let url = "/users/change_svn_passwd/";
    let encoded = $.toJSON(inputIds);
    let p_data = encoded;

    $.ajax({
        type: "POST",
        url: url,
        contentType: "application/json; charset=utf-8",
        data: p_data,
        success: function (data) {
            if (data['data']) {
                $.toast({
                    text: "保存成功", // Text that is to be shown in the toast
                    heading: 'Success', // Optional heading to be shown on the toast
                    icon: 'success', // Type of toast icon
                    showHideTransition: 'slide', // fade, slide or plain
                    allowToastClose: true, // Boolean value true or false
                    hideAfter: 1000, // false to make it sticky or number representing the miliseconds as time after which toast needs to be hidden
                    stack: 5, // false if there should be only one toast at a time or a number representing the maximum number of toasts to be shown at a time
                    position: 'top-center', // bottom-left or bottom-right or bottom-center or top-left or top-right or top-center or mid-center or an object representing the left, right, top, bottom values
                    textAlign: 'left',  // Text alignment i.e. left, right or center
                    loader: true,  // Whether to show loader or not. True by default
                    loaderBg: '#9EC600',  // Background color of the toast loader
                    beforeShow: function () {
                        $("#bt-svn-commit").removeClass('btn-primary').addClass('btn-secondary');
                        $("#bt-svn-commit").prop('disabled', true);
                        $('input[name="my-checkbox"]').bootstrapSwitch('toggleDisabled', true, true)
                    }, // will be triggered before the toast is shown
                    afterShown: function () {
                    }, // will be triggered after the toat has been shown
                    beforeHide: function () {

                    }, // will be triggered before the toast gets hidden
                    afterHidden: function () {
                        $("#bt-svn-commit").removeClass('btn-secondary').addClass('btn-primary');
                        $("#bt-svn-commit").prop('disabled', false);
                        $('input[name="my-checkbox"]').bootstrapSwitch('toggleDisabled', true, true)
                    }  // will be triggered after the toast has been hidden
                });
                $('#modal-notify-svn').attr('class', 'alert alert-success alert-dismissable');
                $('#lb-msg-svn').text(data['msg']);
                $('#modal-notify-svn').show();
                $('#password-svn').val('');
            }
            else {
                $('#modal-notify-svn').attr('class', 'alert alert-danger alert-dismissable');
                $('#lb-msg-svn').text(data['msg']);
                $('#modal-notify-svn').show();
                $('#password-svn').val('');
            }
        }
    });

});


//提交修改LDAP密码请求
$('#bt-ldap-commit').click(function () {
    let username = $('#account').val();
    let passwd = $('#password-ldap').val();
    let re = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[^]{8,32}$/;
    let result = re.test(passwd);
    if (!result) {
        $('#modal-notify-ldap').attr('class', 'alert alert-danger alert-dismissable');
        $('#lb-msg-ldap').text('密码要求同时包含大写字母、小写字母和数字，长度为8-32个字符，不包含账号信息与空格，不是常见密码');
        $('#modal-notify-ldap').show();
        $('#password-ldap').val('');
        return false;
    }
    let inputIds = {
        'passwd': passwd,
        'username': username,
    };
    let url = "/users/change_ldap_passwd/";
    let encoded = $.toJSON(inputIds);
    let p_data = encoded;

    $.ajax({
        type: "POST",
        url: url,
        contentType: "application/json; charset=utf-8",
        data: p_data,
        success: function (data) {
            if (data['data']) {
                $.toast({
                    text: "保存成功", // Text that is to be shown in the toast
                    heading: 'Success', // Optional heading to be shown on the toast
                    icon: 'success', // Type of toast icon
                    showHideTransition: 'slide', // fade, slide or plain
                    allowToastClose: true, // Boolean value true or false
                    hideAfter: 1000, // false to make it sticky or number representing the miliseconds as time after which toast needs to be hidden
                    stack: 5, // false if there should be only one toast at a time or a number representing the maximum number of toasts to be shown at a time
                    position: 'top-center', // bottom-left or bottom-right or bottom-center or top-left or top-right or top-center or mid-center or an object representing the left, right, top, bottom values
                    textAlign: 'left',  // Text alignment i.e. left, right or center
                    loader: true,  // Whether to show loader or not. True by default
                    loaderBg: '#9EC600',  // Background color of the toast loader
                    beforeShow: function () {
                        $("#bt-ldap-commit").removeClass('btn-primary').addClass('btn-secondary');
                        $("#bt-ldap-commit").prop('disabled', true);
                        $('input[name="my-checkbox"]').bootstrapSwitch('toggleDisabled', true, true)
                    }, // will be triggered before the toast is shown
                    afterShown: function () {
                    }, // will be triggered after the toat has been shown
                    beforeHide: function () {

                    }, // will be triggered before the toast gets hidden
                    afterHidden: function () {
                        $("#bt-ldap-commit").removeClass('btn-secondary').addClass('btn-primary');
                        $("#bt-ldap-commit").prop('disabled', false);
                        $('input[name="my-checkbox"]').bootstrapSwitch('toggleDisabled', true, true)
                    }  // will be triggered after the toast has been hidden
                });
                $('#modal-notify-ldap').attr('class', 'alert alert-success alert-dismissable');
                $('#lb-msg-ldap').text(data['msg']);
                $('#modal-notify-ldap').show();
                $('#password-ldap').val('');
            }
            else {
                $('#modal-notify-ldap').attr('class', 'alert alert-danger alert-dismissable');
                $('#lb-msg-ldap').text(data['msg']);
                $('#modal-notify-ldap').show();
                $('#password-ldap').val('');
            }
        }
    });

});


// 重置cmdb登录密码
$("#bt-cmdb-pwd-commit").click(function () {
    var new_passwd1 = $("#new_passwd1").val();
    var new_passwd2 = $("#new_passwd2").val();

    if (new_passwd1 == '') {
        $("#cmdb-pwd-msg").text('请输入密码!');
        $("#cmdb-pwd-msg").show();
        $('#div-cmdb-pwd-msg').show();
        return false;
    }

    let re = /^(?=.*[a-zA-Z])(?=.*\d)[^]{6,16}$/;
    let result = re.test(new_passwd1);
    if (!result) {
        $("#cmdb-pwd-msg").text('长度必须为6-16位，且同时包含字母、数字!');
        $("#cmdb-pwd-msg").show();
        $('#div-cmdb-pwd-msg').show();
        return false;
    }

    if (new_passwd2 == '') {
        $("#cmdb-pwd-msg").text('请确认密码!');
        $("#cmdb-pwd-msg").show();
        $('#div-cmdb-pwd-msg').show();
        return false;
    }

    if (new_passwd1 != new_passwd2) {
        $("#cmdb-pwd-msg").text('两次输入密码不同!');
        $("#cmdb-pwd-msg").show();
        $('#div-cmdb-pwd-msg').show();
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
                $("#cmdb-pwd-msg").text(data.data);
                $("#cmdb-pwd-msg").show();
                return false;
            }
        }
    });

});
