var table;
var editFlag;
var tpl = $("#tpl").html();
//预编译模板
var template = Handlebars.compile(tpl);

// 修改之前的数据
var origin_data;

var str = "确定删除选中的数据库实例?";
var count = 0;


function edit(id) {
    editFlag = true;
    var data = {
        'id': id,
    };
    var encoded = $.toJSON(data);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/mysql/get_instance_info/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function (data) {
            if (data.success) {
                origin_data = data.data;
                $("#myModalLabel").text("修改数据库信息");
                $("#modal-notify").hide();
                $("#id").val(origin_data.id);
                $('#project').val(origin_data.project).select2();
                $('#cmdb_area').val(origin_data.cmdb_area).select2();
                $('#purpose').val(origin_data.purpose);
                $('#host').val(origin_data.host);
                $('#port').val(origin_data.port);
                $('#user').val(origin_data.user);
                $('#password').val(origin_data.password);
                $('#white_list').val(origin_data.white_list);
                $("#myModal").modal("show");
            }
            else {
                alert(data.data)
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
}


$(document).ready(function () {

    $.fn.select2.defaults.set("theme", "bootstrap");
    initSelect2();

    // 初始化websocket
    init_ws();

    var rows_selected = [];

    table = $('#mytable').DataTable({
        "processing": true,
        "serverSide": true,
        "ordering": false,
        "ajax": {
            "type": "POST",
            "url": "/mysql/data_instance/",
        },
        "columns": [
            {"data": null},
            {"data": "id"},
            {"data": "project"},
            {"data": "cmdb_area"},
            {"data": "purpose"},
            {"data": "host"},
            {"data": "port"},
            {"data": "account"},
            {"data": "white_list"},
            {"data": "status"},
            {
                "data": null,
                "orderable": false,
            }
        ],
        "order": [[1, 'asc']],
        columnDefs: [
            {
                'targets': 0,
                'searchable': false,
                'orderable': false,
                'className': 'dt-body-center',
                'render': function (data, type, full, meta) {
                    return '<input type="checkbox">';
                },
            },
            {
                'targets': 1,
                'visible': false,
                'searchable': false
            },
            {
                'targets': 7,
                'searchable': false,
                'render': function (data) {
                    data = data.split(',');
                    var password_visible = $("#password_visible").val();
                    if (password_visible == 'True') {
                        var password = data[1];
                        data[1] = '<a href="javascript:void(0);" data-clipboard-text="' + password + '" onclick="copy(this)">' + password + '</a>';
                    }
                    else {
                        var password = '******';
                        data[1] = '<a href="javascript:void(0);" onclick="copy(this)">' + password + '</a>';
                    }

                    return data.join('<br>')
                }
            },
            {
                'targets': 8,
                "render": function (data, type, row) {
                    return data.split(",").join("<br/>");
                },
            },
            {
                targets: 9,
                width: "10%",
                render: function (a, b, c, d) {
                    if (c.status == '创建中') {
                        return '<lable class="label label-info">' + c.status + '</lable>'
                    }
                    else if (c.status == '运行中') {
                        return '<lable class="label label-success">' + c.status + '</lable>'
                    }
                    else if (c.status == '运行中，未初始化') {
                        return '<lable class="label label-default">' + c.status + '</lable>'
                    }
                    else {
                        return '<lable class="label label-warning">' + c.status + '</lable>'
                    }
                }
            },
            {
                targets: 10,
                width: "15%",
                render: function (a, b, c, d) {
                    if (c.open_wan === 0 && c.status === '运行中') {
                        var context =
                            {
                                func: [
                                    {"name": "修改", "fn": "edit(\'" + c.id + "\')", "type": "primary"},
                                    {"name": "变更记录", "fn": "history(\'" + c.id + "\')", "type": "success"},
                                    {"name": "开通外网访问", "fn": "open_wan(\'" + c.id + "\')", "type": "warning"},
                                ]
                            };
                    }
                    else {
                        var context =
                            {
                                func: [
                                    {"name": "修改", "fn": "edit(\'" + c.id + "\')", "type": "primary"},
                                    {"name": "变更记录", "fn": "history(\'" + c.id + "\')", "type": "success"},
                                    // {"name": "开通外网访问", "fn": "open_wan(\'" + c.id + "\')", "type": "warning"},
                                ]
                            };
                    }
                    var html = template(context);
                    return html;
                }
            }
        ],
        "language": {
            "url": "/static/js/i18n/Chinese.json"
        },
    });

    // Handle click on checkbox
    $('#mytable tbody').on('click', 'input[type="checkbox"]', function (e) {
        var $row = $(this).closest('tr');

        var data = table.row($row).data();
        var index = $.inArray(data[0], rows_selected);

        if (this.checked && index === -1) {
            rows_selected.push(data[0]);
        } else if (!this.checked && index !== -1) {
            rows_selected.splice(index, 1);
        }

        if (this.checked) {
            $row.addClass('selected');
            makeTitle(str, ++count);
        } else {
            $row.removeClass('selected');
            makeTitle(str, --count);
        }

        // Prevent click event from propagating to parent
        e.stopPropagation();
    });

    // Handle click on table cells
    // $('#mytable tbody').on('click', 'td', function(e){
    //     $(this).parent().find('input[type="checkbox"]').trigger('click');
    // });

    $('#chb-all').on('click', function (e) {
        var checkbox = document.getElementById('chb-all');
        $('#mytable tbody td').parent().find('input[type="checkbox"]').map(function (i, n) {
            var $row = $(this).closest('tr');
            n.checked = checkbox.checked;
            if (checkbox.checked) {
                $row.addClass('selected');
                count = getSelectedTable().length;
                makeTitle(str, count);
            } else {
                $row.removeClass('selected');
                count = 0;
                makeTitle(str, count);
            }
        });

    });


    //删除
    $("#bt-del").confirm({
        //text:"确定删除所选的机房?",
        confirm: function (button) {
            var selected = getSelectedTable();

            if (selected.length == 0) {
                alert('请选择');
            } else {
                var encoded = $.toJSON(selected);
                var pdata = encoded;
                $.ajax({
                    type: "POST",
                    url: "/mysql/del_mysql_instance/",
                    contentType: "application/json; charset=utf-8",
                    data: pdata,
                    success: function (data) {
                        if (data['success']) {
                            table.ajax.reload();
                            makeTitle(str, 0);
                            count = 0;
                        } else {
                            alert(data['msg']);
                            table.ajax.reload();
                            makeTitle(str, 0);
                            count = 0;
                        }
                    },
                });
            }
        },
        cancel: function (button) {
        },
        confirmButton: "确定",
        cancelButton: "取消",
    });

    // 添加
    $('#bt-add').click(function () {
        $("#myModalLabel").text("新增数据库信息");
        $("#modal-notify").hide();
        $("#id").val('');
        $("#project").val('0').select2();
        $("#cmdb_area").val('0').select2();
        $("#purpose").val('');
        $("#host").val('');
        $("#port").val('');
        $("#user").val('');
        $("#password").val('');
        $("#white_list").val('');
        editFlag = false;
        $("#myModal").modal("show");
    });


    $('#bt-save').click(function () {
        var id = $("#id").val();
        var project = $('#project').select2('data')[0].id;
        var cmdb_area = $('#cmdb_area').select2('data')[0].id;
        var purpose = $('#purpose').val();
        var host = $('#host').val();
        var port = $('#port').val();
        var user = $('#user').val();
        var password = $('#password').val();
        var white_list = $('#white_list').val();

        if (project == '0') {
            $('#lb-msg').text('请选择项目!');
            $('#modal-notify').show();
            return false;
        }
        if (cmdb_area == '0') {
            $('#lb-msg').text('请选择地区!');
            $('#modal-notify').show();
            return false;
        }
        if (!purpose) {
            $('#lb-msg').text('请填写用途!');
            $('#modal-notify').show();
            return false;
        }
        if (!host) {
            $('#lb-msg').text('请填写主机地址!');
            $('#modal-notify').show();
            return false;
        }
        if (!port) {
            $('#lb-msg').text('请填写端口!');
            $('#modal-notify').show();
            return false;
        }
        if (!user) {
            $('#lb-msg').text('请填写用户!');
            $('#modal-notify').show();
            return false;
        }
        if (!password) {
            $('#lb-msg').text('请填写密码!');
            $('#modal-notify').show();
            return false;
        }
        // if (!white_list) {
        //     $('#lb-msg').text('请填写白名单!');
        //     $('#modal-notify').show();
        //     return false;
        // }

        var inputIds = {
            "id": id,
            "project": project,
            "cmdb_area": cmdb_area,
            'purpose': purpose,
            'host': host,
            'port': port,
            'user': user,
            'password': password,
            'white_list': white_list,
            'editFlag': editFlag,
        };

        var encoded = $.toJSON(inputIds);
        var pdata = encoded;

        var urls = '/mysql/add_or_edit_mysql/';

        $.ajax({
            type: "POST",
            url: urls,
            contentType: "application/json; charset=utf-8",
            data: pdata,
            success: function (data) {
                if (data['success']) {
                    table.ajax.reload(null, false);
                    $("#myModal").modal("hide");
                } else {
                    $('#lb-msg').text(data['msg']);
                    $('#modal-notify').show();
                }
            },
            error: function (data) {
                if (editFlag) {
                    $('#lb-msg').text('你没有修改基础资源权限');
                    $('#modal-notify').show();
                } else {
                    $('#lb-msg').text('你没有增加基础资源权限');
                    $('#modal-notify').show();
                }
            }
        });
    });
});


function initSelect2() {
    $('#project').select2();
    $('#cmdb_area').select2();
}


function copy(i) {
    let password_visible = $('#password_visible').val();
    if (password_visible == 'False') {
        alert('没有权限！请联系管理员开通！')
    }
    else {
        window.getSelection().selectAllChildren(i);
        document.execCommand("Copy");
        alert("复制成功¦")
    }
}


function history(id) {
    var inputIds = {
        "id": id,
    };

    var encoded = $.toJSON(inputIds);
    var pdata = encoded;

    var urls = '/mysql/get_mysql_history/';

    $.ajax({
        type: "POST",
        url: urls,
        contentType: "application/json; charset=utf-8",
        data: pdata,
        success: function (data) {
            if (data['success']) {
                var history_list = data['msg'];
                var html = '';
                for (let i of history_list) {
                    console.log(i);
                    let creat_time = '<span class="text-danger"><strong>' + i.create_time + '</strong></span><br/>';
                    let creat_user = '<span><span class="text-info">操作人：</span>' + i.create_user + '</span>&nbsp;<span class="text-success">' + i.type + '</span><br/>';
                    let alter_content = '';
                    if (i.type == '修改') {
                        if (i.alter_field == '密码' || i.alter_field == '帐号密码') {
                            alter_content = '<span>' + i.alter_field + '</span><br/>'
                        }
                        else {
                            alter_content = '<span>' + i.alter_field + '：' + i.old_content + ' --> ' + i.new_content + '</span><br/>'
                        }
                    }
                    html += creat_time + creat_user + alter_content + '<br/>'
                }
                $('#myModalHistoryContent').html(html);
                $("#myModalHistory").modal("show");
            } else {
                alert(data['msg'])
            }
        },
        error: function (data) {
            alert('你没有权限')
        }
    });
}


function init_ws() {
    var protocol = window.location.protocol;
    if (protocol == 'http:') {
        wsp = 'ws:'
    } else {
        wsp = 'wss:'
    }
    socket = new ReconnectingWebSocket(wsp + "//" + window.location.host + "/ws/mysql_list/", null, {debug: true});

    socket.onmessage = function (e) {
        var data = $.parseJSON(e.data);
        if (data.message == "update_table") {
            table.ajax.reload(null, false);
        }
    };

    socket.onopen = function () {
        socket.send("start ws connection");
    };

    if (socket.readyState == WebSocket.OPEN) socket.onopen();

}


// 开通外网访问
function open_wan(id) {
    var confirm_message = confirm('确认要开通外网访问吗？');
    if (confirm_message == true) {
        var inputIds = {
            "id": id,
        };
        var encoded = $.toJSON(inputIds);
        var pdata = encoded;

        var urls = '/txcloud/open_mysql_wan/';

        $.ajax({
            type: "POST",
            url: urls,
            contentType: "application/json; charset=utf-8",
            data: pdata,
            async: true,
            beforeSend: function () {
                jQuery('#loading').showLoading();
            },
            success: function (data) {
                if (data.success) {

                }
                else {
                    alert(data.data)
                }
            },
            error: function () {
                alert('你没有权限')
            },
            complete: function () {
                jQuery('#loading').hideLoading();
            },
        });
    }
    else {

    }
}
