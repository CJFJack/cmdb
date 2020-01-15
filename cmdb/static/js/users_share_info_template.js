$(document).ready(function () {

    $('#bt-save').click(function () {
        var template_content = $('#text_template_content').val();
        var data = {
            'template_content': template_content,
        };
        var encoded = $.toJSON(data);
        var pdata = encoded;
        $.ajax({
            type: "POST",
            url: "/users/users_share_info_template/",
            data: pdata,
            contentType: "application/json; charset=utf-8",
            success: function (data) {
                if (data.success) {
                    alert('修改成功');
                    window.location.href = '/users/users_share_info_template/'
                }
                else {
                    alert(data.msg)
                }
            },
            error: function (xhr, status, error) {
                if (xhr.status == '403') {
                    alert('权限拒绝');
                } else {
                    alert('内部错误');
                }
            }
        });
    });

    $('#bt-preview').click(function () {
        var template_content = $('#text_template_content').val();
        var data = {
            'template_content': template_content,
            'preview': true,
        };
        var encoded = $.toJSON(data);
        var pdata = encoded;
        $.ajax({
            type: "POST",
            url: "/users/users_share_info_template/",
            data: pdata,
            contentType: "application/json; charset=utf-8",
            success: function (data) {
                if (data.success) {
                    alert('修改成功');
                    window.location.href = '/users/users_share_info_template/'
                }
                else {
                    alert(data.msg)
                }
            },
            error: function (xhr, status, error) {
                if (xhr.status == '403') {
                    alert('权限拒绝');
                } else {
                    alert('内部错误');
                }
            }
        });
    })

});
