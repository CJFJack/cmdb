var table;
var tpl = $("#tpl").html();
//预编译模板
var template = Handlebars.compile(tpl);
var editFlag;
var xhr;
var ot;
var str = "确定要初始化选中的主机?";
var count = 0;

$(document).ready(function () {
    var rows_selected = [];
    table = $('#mytable').DataTable({
        "processing": true,
        "ordering": false,
        "serverSide": true,
        "ajax": {
            "url": "/assets/data_host_initialize/",
            "type": "POST",
            "data": function (d) {
            },
            error: function (jqXHR, textStatus, errorThrown) {
                console.log(jqXHR.responseText);
                alert('数据获取失败')
            }
        },
        "columns": [
            {"data": null},  // 0
            {"data": "id"},  // 1
            {"data": 'instance_state'},  //2
            {"data": 'telecom_ip'},  //3
            {"data": 'syndic_ip'},  //4
            {"data": 'sshport'},  // 5
            {"data": 'sshuser'},  // 6
            {"data": 'business'},  // 7
            {"data": "project"},  // 8
            {"data": "room"},  // 9
            {"data": "add_user"},  // 10
            {"data": "add_time"},  // 11
            {"data": "install_status"}, // 12
            {"data": "initialize_status"},  // 13
            {"data": "reboot_status"},  // 14
            {"data": "import_status"},  // 15
            {
                "data": null,        // 16
                "orderable": false,
            },
        ],
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
                'searchable': false,
            },
            {
                'targets': 2,
                render: function (data) {
                    if (data == '运行中') {
                        return '<label class="label-success label">' + data + '</label>'
                    }
                    if (data == '创建失败') {
                        return '<label class="label-danger label">' + data + '</label>'
                    }
                    if (data == '创建中') {
                        return '<label class="label-info label">' + data + '</label>'
                    }
                    else {
                        return '<label class="label-default label">' + data + '</label>'
                    }
                }
            },
            {
                'targets': 3,
                'searchable': false,
                'render': function (data) {
                    if (!data) {
                        return '<div class="progress progress-striped active">' +
                            '<div class="progress-bar progress-bar-success" role="progressbar" aria-valuenow="100" aria-valuemin="0" aria-valuemax="100" style="width: 100%;">' +
                            '</div>' +
                            '</div>'
                    }
                    else {
                        return data
                    }
                }
            },
            {
                'targets': 12,
                render: function (data) {
                    if (data === '未安装') {
                        return '<label class="label-default label">' + data + '</label>'
                    }
                    if (data === '安装中') {
                        return '<label class="label-info label">' + data + '</label>'
                    }
                    if (data === '安装成功') {
                        return '<label class="label-success label">' + data + '</label>'
                    }
                    if (data === '安装失败') {
                        return '<label class="label-danger label">' + data + '</label>'
                    }
                }
            },
            {
                'targets': 13,
                render: function (data) {
                    if (data === '未初始化') {
                        return '<label class="label-default label">' + data + '</label>'
                    }
                    if (data === '初始化中') {
                        return '<label class="label-info label">' + data + '</label>'
                    }
                    if (data === '初始化成功') {
                        return '<label class="label-success label">' + data + '</label>'
                    }
                    if (data === '初始化失败') {
                        return '<label class="label-danger label">' + data + '</label>'
                    }
                }
            },
            {
                'targets': 14,
                render: function (data) {
                    if (data === '未重启') {
                        return '<label class="label-default label">' + data + '</label>'
                    }
                    if (data === '重启中') {
                        return '<label class="label-info label">' + data + '</label>'
                    }
                    if (data === '重启成功') {
                        return '<label class="label-success label">' + data + '</label>'
                    }
                    if (data === '重启失败') {
                        return '<label class="label-danger label">' + data + '</label>'
                    }
                }
            },
            {
                'targets': 15,
                render: function (data) {
                    if (data === '未入库') {
                        return '<label class="label-default label">' + data + '</label>'
                    }
                    if (data === '入库中') {
                        return '<label class="label-info label">' + data + '</label>'
                    }
                    if (data === '入库成功') {
                        return '<label class="label-success label">' + data + '</label>'
                    }
                    if (data === '入库失败') {
                        return '<label class="label-danger label">' + data + '</label>'
                    }
                }
            },
            {
                targets: 16,
                width: "13%",
                render: function (a, b, c, d) {
                    if (c.initialize_status === '未初始化' && c.install_status !== '安装中') {
                        var context =
                            {
                                func: [
                                    {"name": "修改", "fn": "edit(\'" + c.id + "\')", "type": "primary"},
                                    {"name": "日志", "fn": "log(\'" + c.id + "\')", "type": "success"},
                                    {"name": "初始化", "fn": "initialize(\'" + c.id + "\')", "type": "danger"},
                                ]
                            };
                        var html = template(context);
                    }
                    else if (c.initialize_status === '初始化成功' && c.install_status === '安装成功') {
                        if (c.reboot_status === '未重启') {
                            var context =
                                {
                                    func: [
                                        {"name": "修改", "fn": "edit(\'" + c.id + "\')", "type": "primary"},
                                        {"name": "日志", "fn": "log(\'" + c.id + "\')", "type": "success"},
                                        {"name": "重启", "fn": "reboot(\'" + c.telecom_ip + "\')", "type": "warning"},
                                    ]
                                };
                        }
                        else if (c.reboot_status === '重启成功' && c.import_status === '未入库') {
                            var context =
                                {
                                    func: [
                                        {"name": "修改", "fn": "edit(\'" + c.id + "\')", "type": "primary"},
                                        {"name": "日志", "fn": "log(\'" + c.id + "\')", "type": "success"},
                                        {"name": "入库", "fn": "host_import(\'" + c.telecom_ip + "\')", "type": "info"},
                                    ]
                                };
                        }
                        else {
                            var context =
                                {
                                    func: [
                                        {"name": "修改", "fn": "edit(\'" + c.id + "\')", "type": "primary"},
                                        {"name": "日志", "fn": "log(\'" + c.id + "\')", "type": "success"},
                                    ]
                                };
                        }
                        var html = template(context);
                    }
                    else {
                        var context =
                            {
                                func: [
                                    {"name": "修改", "fn": "edit(\'" + c.id + "\')", "type": "primary"},
                                    {"name": "日志", "fn": "log(\'" + c.id + "\')", "type": "success"},
                                ]
                            };
                        var html = template(context);
                    }
                    return html;
                }
            },
        ],
        "language": {
            "url": "/static/js/i18n/Chinese.json"
        },
        initComplete: function (result) {
            if (!result.json.success) {
                console.log(result.json.msg);
                alert('数据获取失败');
            }
        }
    });

    $(':checkbox.toggle-visiable').on('click', function (e) {
        //e.preventDefault();

        // Get the column API object
        var is_checked = $(this).is(':checked');
        var column = table.column($(this).attr('value'));
        // table.ajax.reload();
        column.visible(is_checked);
    });

    $('#bt-modal-notify').click(function () {
        $("#modal-notify").hide();
    });

    $('#chb-all').on('click', function (e) {
        var checkbox = document.getElementById('chb-all');
        $('#mytable tbody td').parent().find('input[type="checkbox"]').map(function (i, n) {
            var $row = $(this).closest('tr');
            n.checked = checkbox.checked;
            if (checkbox.checked) {
                $row.addClass('selected');
                count = getSelectedTable().length;
                makeInitializeTitle(str, count);
            } else {
                $row.removeClass('selected');
                count = 0;
                makeInitializeTitle(str, count);
            }
        });
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
            makeInitializeTitle(str, ++count);
        } else {
            $row.removeClass('selected');
            makeInitializeTitle(str, --count);
        }

        // Prevent click event from propagating to parent
        e.stopPropagation();
    });

    init_ws();
    initModalSelect2();

    $('#add-initialize-host').click(function () {
        $('#add_or_edit_host_initialize_modal_title').text('添加初始化主机');
        $('#add_or_edit_host_initialize_notify').hide();
        $('#telecom_ip').attr('disabled', false);
        $('#telecom_ip').val('');
        $('#syndic_ip').val('');
        $('#sshuser').val('');
        $('#sshport').val('');
        $('#sshpassword').val('');
        initSelect2('project', '0', '请选择项目');
        initSelect2('room', '0', '请选择机房');
        initSelect2('business', '0', '请选择业务类型');
        $("#div_initialize_at_once").show();
        $("#initialize_at_once").attr("checked", false);
        $('#telecom_ip_notice').hide();
        $('#div_saltstack_install_status').hide();
        $('#div_initialize_status').hide();
        $('#div_reboot_status').hide();
        $('#div_import_status').hide();
        $('#sshpassword').attr('type', 'password');
        $('#dis_pwd').attr("checked", false);
        editFlag = false;
        $('#add_or_edit_host_initialize_modal').modal('show');
    });

    $('#bt-confirm').click(function () {
        let urls = "/assets/add_or_edit_host_initialize_manual/";
        let telecom_ip = $('#telecom_ip').val();
        let syndic_ip = $('#syndic_ip').val();
        let sshport = $('#sshport').val();
        let sshuser = $('#sshuser').val();
        let password = $('#sshpassword').val();
        let project = $('#project').select2('data')[0].id;
        let room = $('#room').select2('data')[0].id;
        let business = $('#business').select2('data')[0].id;
        let at_once = $("#initialize_at_once").prop("checked");
        let install_status = $("#saltstack_install_status").select2('data')[0].id;
        let initialize_status = $("#initialize_status").select2('data')[0].id;
        let reboot_status = $("#reboot_status").select2('data')[0].id;
        let import_status = $("#import_status").select2('data')[0].id;

        if (!telecom_ip) {
            $('#add_or_edit_host_initialize_msg').text('请输入minion_ip');
            $('#add_or_edit_host_initialize_notify').show();
            return false;
        }
        if (!syndic_ip) {
            $('#add_or_edit_host_initialize_msg').text('请输入syndic_ip');
            $('#add_or_edit_host_initialize_notify').show();
            return false;
        }
        if (!sshport) {
            $('#add_or_edit_host_initialize_msg').text('请输入ssh端口');
            $('#add_or_edit_host_initialize_notify').show();
            return false;
        }
        if (!sshuser) {
            $('#add_or_edit_host_initialize_msg').text('请输入ssh帐号');
            $('#add_or_edit_host_initialize_notify').show();
            return false;
        }
        if (!sshpassword) {
            $('#add_or_edit_host_initialize_msg').text('请输入ssh密码');
            $('#add_or_edit_host_initialize_notify').show();
            return false;
        }
        if (project == "0") {
            $('#add_or_edit_host_initialize_msg').text('请选择项目');
            $('#add_or_edit_host_initialize_notify').show();
            return false;
        }
        if (room == "0") {
            $('#add_or_edit_host_initialize_msg').text('请选择机房');
            $('#add_or_edit_host_initialize_notify').show();
            return false;
        }
        if (business == "0") {
            $('#add_or_edit_host_initialize_msg').text('请选择业务类型');
            $('#add_or_edit_host_initialize_notify').show();
            return false;
        }

        let inputIds = {
            'telecom_ip': telecom_ip,
            'syndic_ip': syndic_ip,
            'sshport': sshport,
            'sshuser': sshuser,
            'password': password,
            'project': project,
            'room': room,
            'business': business,
            'at_once': at_once,
            'editFlag': editFlag,
        };
        if (editFlag) {
            inputIds['install_status'] = install_status;
            inputIds['initialize_status'] = initialize_status;
            inputIds['reboot_status'] = reboot_status;
            inputIds['import_status'] = import_status;

        }
        let encoded = $.toJSON(inputIds);
        let pdata = encoded;

        $.ajax({
            type: "POST",
            url: urls,
            contentType: "application/json; charset=utf-8",
            data: pdata,
            success: function (data) {
                if (data['data']) {
                    table.ajax.reload(null, false);
                    $("#add_or_edit_host_initialize_modal").modal("hide");
                } else {
                    $('#add_or_edit_host_initialize_msg').text(data['msg']);
                    $('#add_or_edit_host_initialize_notify').show();
                }
            },
            error: function () {
                $("#add_or_edit_host_initialize_modal").modal("hide");
                alert('内部错误')
            }
        });
    });

    $("#initialize_at_once").change(function () {
        if ($('#initialize_at_once').prop("checked") == true) {
            $('#telecom_ip_notice').show();
        }
        else {
            $('#telecom_ip_notice').hide();
        }
    });

    $("#dis_pwd").change(function () {
        if ($('#dis_pwd').prop("checked") == true) {
            $('#sshpassword').attr('type', 'text')
        }
        else {
            $('#sshpassword').attr('type', 'password')
        }
    });

    $('#bt-start').click(function () {
        let urls = "/assets/start_host_initialize/";
        let telecom_ip = $('#start_initialize_ip').val();

        let inputIds = {
            'telecom_ip': [telecom_ip],
        };
        let encoded = $.toJSON(inputIds);
        let pdata = encoded;

        $.ajax({
            type: "POST",
            url: urls,
            contentType: "application/json; charset=utf-8",
            data: pdata,
            success: function (data) {
                if (data.data) {
                    table.ajax.reload(null, false);
                    $('#start_initialize').modal('hide');
                }
                else {
                    $('#start_initialize').modal('hide');
                    alert(data.msg)
                }
            },
            error: function () {
                $('#start_initialize').modal('hide');
                alert('初始化失败，内部错误')
            }
        });
    });

    $('#bt-reboot').click(function () {
        let urls = "/assets/reboot_initialize_host/";
        let telecom_ip = $('#reboot_ip').text();

        let inputIds = {
            'telecom_ip': [telecom_ip],
        };
        let encoded = $.toJSON(inputIds);
        let pdata = encoded;

        $.ajax({
            type: "POST",
            url: urls,
            contentType: "application/json; charset=utf-8",
            data: pdata,
            success: function (data) {
                if (data.data) {
                    table.ajax.reload(null, false);
                    $('#reboot').modal('hide');
                }
                else {
                    $('#reboot').modal('hide');
                    alert(data.msg)
                }
            },
            error: function () {
                $('#reboot').modal('hide');
                alert('发送重启请求失败，cmdb内部错误')
            }
        });
    });

    $('#bt-host-import').click(function () {
        let urls = "/assets/import_initialize_host/";
        let telecom_ip = $('#host_import_ip').text();

        let inputIds = {
            'telecom_ip': [telecom_ip],
        };
        let encoded = $.toJSON(inputIds);
        let pdata = encoded;

        $.ajax({
            type: "POST",
            url: urls,
            contentType: "application/json; charset=utf-8",
            data: pdata,
            success: function (data) {
                if (data.data) {
                    table.ajax.reload(null, false);
                    $('#host_import').modal('hide');
                }
                else {
                    $('#host_import').modal('hide');
                    alert(data.msg)
                }
            },
            error: function () {
                $('#host_import').modal('hide');
                alert('发送入库请求失败，cmdb内部错误')
            }
        });
    });

    // 下载模板
    $('#download_template').click(function () {
        let download_url = '/assets/host_initialize_templates_download/host_initialize_batch_import_template.xlsx';
        window.location = download_url;
    });

    // 上传excel
    $('#import_excel').click(function () {
        $('#importModal').modal('show')
    });

    // 批量初始化
    $("#batch_initialize").confirm({
        //text:"确定要初始化所选的主机?",
        confirm: function (button) {
            let selected = getInitSelectedTable();
            let inputIds = {
                'telecom_ip': selected,
            };

            if (selected.length == 0) {
                alert('请选择');
            } else {
                var encoded = $.toJSON(inputIds);
                var pdata = encoded;
                $.ajax({
                    type: "POST",
                    url: "/assets/start_host_initialize/",
                    contentType: "application/json; charset=utf-8",
                    data: pdata,
                    success: function (data) {

                        if (data['data']) {
                            table.ajax.reload(null, false);
                            makeInitializeTitle(str, 0);
                            count = 0;
                        } else {
                            alert(data['msg']);
                            table.ajax.reload(null, false);
                            makeInitializeTitle(str, 0);
                            count = 0;
                        }
                    }
                });
            }
        },

        cancel: function (button) {

        },
        confirmButton: "确定",
        cancelButton: "取消",

    });

    // 同步pillar
    $("#sync_pillar").confirm({
        confirm: function (button) {
            $('#sync_pillar').text('刷新中，请勿刷新页面');
            $('#sync_pillar').attr('disabled', true);
            $.ajax({
                type: "POST",
                url: "/assets/sync_pillar/",
                contentType: "application/json; charset=utf-8",
                async: true,
                success: function (data) {
                    if (data['data']) {
                        alert(data['msg']);
                    } else {
                        alert(data['msg']);
                    }
                    $('#sync_pillar').text('刷新pillar配置');
                    $('#sync_pillar').attr('disabled', false);
                }
            });
        },

        cancel: function (button) {

        },
        confirmButton: "确定",
        cancelButton: "取消",

    });

});


function initModalSelect2() {

    $select2Project = $('#project').select2({
        ajax: {
            url: '/assets/list_game_project/',
            dataType: 'json',
            type: 'POST',
            delay: 0,
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
        escapeMarkup: function (markup) {
            return markup;
        },
    });

    $select2Room = $('#room').select2({
        ajax: {
            url: '/assets/list_room/',
            dataType: 'json',
            type: 'POST',
            delay: 0,
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
        escapeMarkup: function (markup) {
            return markup;
        },
    });

    $select2Business = $('#business').select2({
        ajax: {
            url: '/assets/list_business/',
            dataType: 'json',
            type: 'POST',
            delay: 0,
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
        escapeMarkup: function (markup) {
            return markup;
        },
    });

    $select2InstallStatus = $('#saltstack_install_status').select2({});
    $select2InitialStatus = $('#initialize_status').select2({});
    $select2RebootStatus = $('#reboot_status').select2({});
    $select2InstanceState = $('#instance_state').select2({});
    $select2ImportStatus = $('#import_status').select2({});
}


function edit(id) {
    $('#add_or_edit_host_initialize_modal_title').text('修改初始化信息');
    $('#add_or_edit_host_initialize_notify').hide();
    $("#div_initialize_at_once").hide();
    $('#telecom_ip_notice').hide();
    $('#sshpassword').attr('type', 'password');
    $('#dis_pwd').attr("checked", false);
    editFlag = true;

    let data = {
        'id': id,
    };

    let encoded = $.toJSON(data);
    let pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/assets/get_initialize_host_info/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function (data) {
            if (data.success) {
                $('#telecom_ip').val(data.telecom_ip);
                $('#telecom_ip').attr('disabled', true);
                $('#syndic_ip').val(data.syndic_ip);
                $('#sshport').val(data.sshport);
                $('#sshuser').val(data.sshuser);
                $('#sshpassword').val(data.password);
                initSelect2('project', data.project_id, data.project);
                initSelect2('room', data.room_id, data.room);
                initSelect2('business', data.business_id, data.business);
                $("#saltstack_install_status").val(data.install_status).trigger("change");
                $("#initialize_status").val(data.initialize_status).trigger("change");
                $("#reboot_status").val(data.reboot_status).trigger("change");
                $("#instance_state").val(data.instance_state).trigger("change");
                $("#import_status").val(data.import_status).trigger("change");
                $('#div_saltstack_install_status').show();
                $('#div_initialize_status').show();
                $('#div_reboot_status').show();
                $('#div_instance_state').show();
                $('#div_import_status').show();
            }
            else {
                console.log('获取数据失败: ' + data.msg)
            }
            $('#add_or_edit_host_initialize_modal').modal('show');

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


function log(id) {
    window.location.href = "/assets/host_initialize_log/" + id + "/";
}


function init_ws() {
    var protocol = window.location.protocol;
    if (protocol == 'http:') {
        wsp = 'ws:'
    } else {
        wsp = 'wss:'
    }
    socket = new ReconnectingWebSocket(wsp + "//" + window.location.host + "/ws/host_initialize_list/", null, {debug: true});

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


function initialize(id) {
    $('#start_initialize_title').text('确认初始化信息');
    $('#start_initialize_notify').hide();

    let data = {
        'id': id,
    };

    let encoded = $.toJSON(data);
    let pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/assets/get_initialize_host_info/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function (data) {
            if (data.success) {
                $('#start_initialize_ip').val(data.telecom_ip);
                let info = '<h5 class="text-danger"><strong>请务必确认以下信息是否正确： </strong></h5>';
                info += '<strong><p class="text-danger">* minion_ip： ' + data.telecom_ip + '</p></strong>';
                info += '<strong><p class="text-danger">* syndic_ip： ' + data.syndic_ip + '</p></strong>';
                info += '<strong><p class="text-danger">* ssh端口： ' + data.sshport + '</p></strong>';
                info += '<strong><p class="text-danger">* ssh用户： ' + data.sshuser + '</p></strong>';
                info += '<strong><p class="text-danger">* 项目： ' + data.project + '</p></strong>';
                info += '<strong><p class="text-danger">* 机房： ' + data.room + '</p></strong>';
                info += '<strong><p class="text-danger">* 业务类型： ' + data.business + '</p></strong>';
                $('#host_initialize_info').html(info);
                $('#start_initialize').modal('show')
            }
            else {
                console.log('获取数据失败: ' + data.msg)
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


function reboot(telecom_ip) {
    $('#reboot_ip').text(telecom_ip);
    $('#reboot').modal('show')
}


//上传文件方法
$('#bt-import').click(function () {
    var fileobj = $("#file")[0].files[0];
    var form = new FormData();
    form.append('file', fileobj);
    $.ajax({
        type: 'POST',
        url: '/assets/host_initialize_batch_excel_import/',
        data: form,
        async: false,
        processData: false,
        contentType: false,
        success: function (data) {
            if (data.success) {
                $('#importModal').modal('hide');
                alert('上传成功');
            }
            else {
                $('#importModal').modal('hide');
                alert(data.msg)
            }
            window.location.reload()
        }
    })
});


function host_import(telecom_ip) {
    $('#host_import_ip').text(telecom_ip);
    $('#host_import').modal('show')
}
