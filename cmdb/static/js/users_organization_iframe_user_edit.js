var first_name = $('#id_first_name').val();

$(function () {
    //初始所属部门
    $select2Parent = $('#ancestors-user-edit').select2({
        theme: "bootstrap",
        ajax: {
            url: '/users/list_new_organization/',
            dataType: 'json',
            type: 'POST',
            delay: 30,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page
                };
            },

            processResults: function (data, params) {
                params.page = params.page || 1;
                return {
                    results: $.map(data, function (item) {
                        return {
                            id: item.id,
                            text: item.text,
                        }
                    })
                }
            },
            cache: false,
        },
    });


    //清空节点负责人
    $('#reset_leader').on('click', function () {
        $('#leader-option').text('');
        $('#leader-option').val(0);
        $('#select2-leader-container').text('');
    });

});


//弹出修改企业qq信息
$('#edit-ent-qq').click(function () {
    $("#myModalLabel-ent-qq").text("修改企业QQ信息");
    $("#modal-notify-ent-qq").hide();
    $('#name-ent-qq').val('');
    $('#title-ent-qq').val('');
    $('#password-ent-qq').val('');
    $('input[name=sex-ent-qq]:checked').val('');
    $("#myModal-ent-qq").modal("show");
});


//提交修改企业QQ请求
$('#save-ent-qq').click(function () {
    let name = $('#name-ent-qq').val();
    let title = $('#title-ent-qq').val();
    let password = $('#password-ent-qq').val();
    let sex = $('input[name=sex-ent-qq]:checked').val();
    let account = $('#account-ent-qq').val();
    let inputIds = {
        'name': name,
        'title': title,
        'password': password,
        'sex': sex,
        'account': account
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
                $('#modal-notify-ent-qq').attr('class', 'alert alert-success alert-dismissable');
                $('#lb-msg-ent-qq').text(data['msg']);
                $('#modal-notify-ent-qq').show();
            }
            else {
                $('#modal-notify-ent-qq').attr('class', 'alert alert-danger alert-dismissable');
                $('#lb-msg-ent-qq').text(data['msg']);
                $('#modal-notify-ent-qq').show();
            }
        }
    });

});


//弹出修改企业邮箱信息
$('#edit-ent-email').click(function () {
    $("#myModalLabel-ent-email").text("修改企业邮箱信息");
    $("#modal-notify-ent-email").hide();
    $('#name-ent-email').val('');
    $('#position-ent-email').val('');
    $('#password-ent-email').val('');
    $('#enable-ent-email').val('');
    initSelect2('department-ent-email', '0', '（选填）请选择所属部门')
    $("#myModal-ent-email").modal("show");
});

function initModalSelect2() {
    //初始化所属部门
    $select2Department = $('#department-ent-email').select2({
        theme: "bootstrap",
        ajax: {
            url: '/users/list_new_organization/',
            dataType: 'json',
            type: 'POST',
            delay: 30,
            data: function (params) {
                return {
                    q: params.term,
                    page: params.page
                };
            },

            processResults: function (data, params) {
                params.page = params.page || 1;
                return {
                    results: $.map(data, function (item) {
                        return {
                            id: item.id,
                            text: item.text,
                        }
                    })
                }
            },
            cache: false,
        },
    });

    $('#suffix-open-ent-email').select2();

}

initModalSelect2();

// function test() {
//     var text = document.getElementById("test1").value;
//     var re = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[^]{8,16}$/;
//     var result = re.test(text);
//     if (result) {
//
//     } else {
//         alert("密码要求同时包含大写字母、小写字母和数字，长度为8-16个字符，不包含账号信息与空格，不是常见密码");
//     }
// }


//提交修改企业邮箱请求
$('#save-ent-email').click(function () {
    let name = $('#name-ent-email').val();
    let position = $('#position-ent-email').val();
    let password = $('#password-ent-email').val();
    let gender = $('input[name=sex-ent-email]:checked').val();
    let enable = $('input[name=enable-ent-email]:checked').val();
    let userid = $('#edit_email_account').val();
    let department = $('#department-ent-email').select2('data')[0].id;
    let re = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[^]{6,32}$/;
    let result = re.test(password);
    if (!userid) {
        $('#modal-notify-ent-email').attr('class', 'alert alert-danger alert-dismissable');
        $('#lb-msg-ent-email').text('请选择需要修改的邮箱！');
        $('#modal-notify-ent-email').show();
        return false;
    }
    if (password != '' && !result) {
        $('#modal-notify-ent-email').attr('class', 'alert alert-danger alert-dismissable');
        $('#lb-msg-ent-email').text('密码要求同时包含大写字母、小写字母和数字，长度为6-32个字符，不包含账号信息与空格，不是常见密码');
        $('#modal-notify-ent-email').show();
        return false;
    }
    let inputIds = {
        'name': name,
        'position': position,
        'password': password,
        'gender': gender,
        'userid': userid,
        'enable': enable,
        'department': department,
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
                $('#modal-notify-ent-email').attr('class', 'alert alert-success alert-dismissable');
                $('#lb-msg-ent-email').text(data['msg']);
                $('#modal-notify-ent-email').show();
            }
            else {
                $('#modal-notify-ent-email').attr('class', 'alert alert-danger alert-dismissable');
                $('#lb-msg-ent-email').text(data['msg']);
                $('#modal-notify-ent-email').show();
            }
        }
    });

});


// 复制用户分享信息函数
function copyShareText() {
    var share_info_text = document.getElementById("share_info_text");
    share_info_text.select();
    document.execCommand("Copy");
    alert("复制成功，请粘贴");
}


// 弹出用户信息分享文本模太框
$('#bt_share_user_info').click(function () {
    $('#share_first_name').text($('#id_first_name').val());
    $('#share_username').text($('#edit_username').val());
    $('#share_email').text($('#ent_email').val());
    $('#share_ent_qq').text($('#ent_qq').val());
    $('#modal_share_user_info').modal("show");
});


//开通openvpn帐号
$("#create_openvpn").confirm({
    confirm: function () {
        let url = "/users/add_vpn_user/";
        let inputIds = {
            'first_name': first_name,
        };
        let encoded = $.toJSON(inputIds);
        let p_data = encoded;
        $.ajax({
            type: "POST",
            url: url,
            contentType: "application/json; charset=utf-8",
            data: p_data,
            beforeSend: function () {
                jQuery('#org_edit_body').showLoading();
            },
            success: function (data) {
                jQuery('#loading').hideLoading();
                if (data.success) {
                    window.location.reload();
                    alert('开通成功');
                }
                else {
                    alert('开通失败!' + data.msg);
                }
            },
            error: function (data) {
                jQuery('#loading').hideLoading();
                if (xhr.status == '403') {
                    alert('权限拒绝');
                } else {
                    alert('内部错误');
                }
            }
        });
    },
    cancel: function (button) {
    },
    text: '确定要开通openVPN帐号' + first_name + '吗?',
    confirmButton: "确定",
    cancelButton: "取消",
});


//弹出修改openvpn帐号密码模太框
$("#modify_openvpn").click(function () {
    $('#id_vpn_passwd').val('');
    $('#id_vpn_passwd_twice').val('');
    $('#modal_modify_vpn').modal('show');
});


//修改openvpn帐号密码
$("#modify_passwd").click(function () {
    let url = "/users/modify_vpn_user/";
    let passwd = $('#id_vpn_passwd').val();
    let passwd_twice = $('#id_vpn_passwd_twice').val();
    if (!passwd) {
        alert('密码不能为空');
        return false
    }
    if (passwd != passwd_twice) {
        alert('两次密码不一致');
        return false;
    }
    let re = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[^]{8,32}$/;
    let result = re.test(passwd);
    if (passwd != '' && !result) {
        alert('密码要求同时包含大写字母、小写字母和数字，长度为8-32个字符，不包含账号信息与空格，不是常见密码');
        return false;
    }
    let inputIds = {
        'first_name': first_name,
        'passwd': passwd,
    };
    let encoded = $.toJSON(inputIds);
    let p_data = encoded;

    $.ajax({
        type: "POST",
        url: url,
        contentType: "application/json; charset=utf-8",
        data: p_data,
        beforeSend: function () {
            jQuery('#org_edit_body').showLoading();
        },
        success: function (data) {
            jQuery('#loading').hideLoading();
            if (data.success) {
                window.location.reload();
                alert('修改成功');
            }
            else {
                alert('修改失败!' + data.msg);
            }
        },
        error: function (data) {
            jQuery('#loading').hideLoading();
            if (xhr.status == '403') {
                alert('权限拒绝');
            } else {
                alert('内部错误');
            }
        }
    });
});

//触发整个父业面跳转到资产回收页面
$('#org-desire').click(function () {
    var user_id = $('#user_id').val();
    window.parent.location.href = '/users/user_desert/' + user_id + '/';
});

//触发整个父业面跳转到清除用户页面
$('#org-clean').click(function () {
    var user_id = $('#user_id').val();
    window.parent.location.href = '/users/clean/?id=' + user_id;
});

// 开通企业qq模太框
$('#bt-open-ent-qq').click(function () {
    $('#myModalLabel-open-ent-qq').text('核对开通企业QQ信息');
    $('#modal-notify-open-ent-qq').hide();
    $('#myModal-open-ent-qq').modal('show')
});


//提交开通企业QQ请求
$('#save-open-ent-qq').click(function () {
    let account = $('#account-open-ent-qq').val();
    let name = $('#name-open-ent-qq').val();
    let title = $('#title-open-ent-qq').val();
    let department = $('#department-open-ent-qq').val();
    let gender = $('#gender-open-ent-qq').attr('data-gender');
    let inputIds = {
        'name': name,
        'title': title,
        'department': department,
        'gender': gender,
        'account': account
    };
    let url = "/users/open_ent_qq/";
    let encoded = $.toJSON(inputIds);
    let p_data = encoded;

    $.ajax({
        type: "POST",
        url: url,
        contentType: "application/json; charset=utf-8",
        data: p_data,
        beforeSend: function () {
            jQuery('#org_edit_body').showLoading();
        },
        success: function (data) {
            jQuery('#org_edit_body').hideLoading();
            if (data['success']) {
                alert('开通成功');
                parent.location.reload();
            }
            else {
                alert(data['msg'])
            }
        },
        error: function (data) {
            jQuery('#org_edit_body').hideLoading();
            if (xhr.status == '403') {
                alert('权限拒绝');
            } else {
                alert('内部错误');
            }
        }
    });

});


//开通企业邮箱模太框
$('#bt-open-ent-email').click(function () {
    $('#myModalLabel-open-ent-email').text('开通企业邮箱信息');
    $('#modal-notify-open-ent-email').hide();
    $('#myModal-open-ent-email').modal('show')
});


//提交开通企业QQ请求
$('#save-open-ent-email').click(function () {
    let account = $('#account-open-ent-email').val();
    let name = $('#name-open-ent-email').val();
    let title = $('#title-open-ent-email').val();
    let department = $('#department-open-ent-email').val();
    let gender = $('#gender-open-ent-email').attr('data-gender');
    let suffix = $('#suffix-open-ent-email').val();
    if (!suffix) {
        $('#lb-msg-open-ent-email').text('请选择需要开通的邮箱后缀');
        $('#modal-notify-open-ent-email').show();
        return false;
    }
    let inputIds = {
        'name': name,
        'title': title,
        'department': department,
        'gender': gender,
        'account': account,
        'suffix': suffix
    };
    let url = "/users/open_ent_email/";
    let encoded = $.toJSON(inputIds);
    let p_data = encoded;

    $.ajax({
        type: "POST",
        url: url,
        contentType: "application/json; charset=utf-8",
        data: p_data,
        beforeSend: function () {
            jQuery('#org_edit_body').showLoading();
        },
        success: function (data) {
            jQuery('#org_edit_body').hideLoading();
            if (data['success']) {
                alert(data['msg']);
                parent.location.reload();
            }
            else {
                alert(data['msg'])
            }
        },
        error: function (data) {
            jQuery('#org_edit_body').hideLoading();
            if (xhr.status == '403') {
                alert('权限拒绝');
            } else {
                alert('内部错误');
            }
        }
    });

});
