var table;
var tpl = $("#tpl").html();
//预编译模板
var template = Handlebars.compile(tpl);


$.urlParam = function (name) {
    var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
    if (results == null) {
        return null;
    }
    else {
        return decodeURIComponent(results[1]) || 0;
    }
};

function preFilter() {
    var migrate_status = $.urlParam('migrate_status');
    var recover_status = $.urlParam('recover_status');

    if (migrate_status !== null) {
        $("#filter_action_status").append("<option value='1'>未迁服</option>");
        $("#filter_action_status").append("<option value='2'>迁服中</option>");
        $("#filter_action_status").append("<option value='3'>迁服成功</option>");
        $("#filter_action_status").append("<option value='4'>迁服失败</option>");
        $("#filter_action_status").append("<option value='5'>取消</option>");
        $("#filter_action_status").val(migrate_status).trigger('change');
    }

    if (recover_status !== null) {
        $("#filter_recover_status").append("<option value='1'>未回收</option>");
        $("#filter_recover_status").append("<option value='2'>回收中</option>");
        $("#filter_recover_status").append("<option value='3'>回收成功</option>");
        $("#filter_recover_status").append("<option value='4'>回收失败</option>");
        $("#filter_recover_status").append("<option value='5'>取消</option>");
        $("#filter_recover_status").val(recover_status).trigger('change');
    }
}


$(document).ready(function () {
    $.fn.select2.defaults.set("theme", "bootstrap");

    table = $('#mytable').DataTable({
        "processing": true,
        "ordering": false,
        "serverSide": true,
        autoWidth: true,
        "ajax": {
            "url": "/myworkflows/data_host_compression_apply_list/",
            "type": "POST",
            "data": function (d) {
                d.filter_title = $('#filter_title').val();
                d.filter_ops = $('#filter_ops').select2('data')[0].id;
                d.filter_type = $('#filter_type').select2('data')[0].id;
                d.filter_project = $('#filter_project').select2('data')[0].id;
                d.filter_apply_user = $('#filter_apply_user').select2('data')[0].id;
                d.filter_room = $('#filter_room').select2('data')[0].id;
                d.filter_action_status = $('#filter_action_status').select2('data')[0].id;
                d.filter_recover_status = $('#filter_recover_status').select2('data')[0].id;
                d.filter_start_action_time = $('#filter_start_action_time').val();
                d.filter_end_action_time = $('#filter_end_action_time').val();
                d.filter_start_recover_time = $('#filter_start_recover_time').val();
                d.filter_end_recover_time = $('#filter_end_recover_time').val();
                d.filter_start_apply_time = $('#filter_start_apply_time').val();
                d.filter_end_apply_time = $('#filter_end_apply_time').val();
            }
        },
        "columns": [
            {"data": "id"},  // 0
            {"data": 'title'},  //1
            {"data": 'project'},  //2
            {"data": 'room'},  //3
            {"data": 'apply_user'},  //4
            {"data": 'apply_time'},  //5
            {"data": 'uuid'},  //6
            {"data": 'ops'},  //7
            {"data": 'type'},  // 8
            {"data": 'hosts'},  // 9
            {"data": "action_time"},  // 10
            {"data": "action_deadline"},  // 11
            {"data": "action_status"},  // 12
            {"data": "recover_time"},  // 13
            {"data": "recover_deadline"},  // 14
            {"data": "recover_status"},  // 15
            {
                "data": null,        //16
                "orderable": false,
            },
            // {
            //     "data": null,        //17
            //     "orderable": false,
            // },
            {
                "data": null,        //17
                "orderable": false,
            },
        ],
        columnDefs: [
            {
                'targets': 0,
                'visible': false,
                'searchable': false
            },
            {
                'targets': [4, 5, 6, 7],
                'visible': false,
            },
            {
                'targets': [9],
                "render": function (data, type, row) {
                    return data.split(",").join("<br/>");
                },
            },
            {
                'targets': 10,
                'width': '11%',
                render: function (a, b, c, d) {
                    if (c.type == '迁服回收') {
                        return '<span class="tooltip-demo"><span>' + c.action_time + '&nbsp;</span><label class="label label-danger" data-toggle="tooltip" data-placement="top" title="' + c.action_deadline + '">截</label></span>'
                    }
                    else {
                        return ''
                    }
                }
            },
            {
                'targets': [11, 14],
                'visible': false,
                'searchable': false
            },
            {
                'targets': 12,
                render: function (a, b, c, d) {
                    if (c.type == '迁服回收') {
                        if (c.action_status == '迁服中') {
                            return '<label class="label label-info" disabled>' + c.action_status + '</label>'
                        }
                        else if (c.action_status == '取消') {
                            return '<label class="label label-default" disabled>' + c.action_status + '</label>'
                        }
                        else if (c.action_status == '迁服成功') {
                            return '<label class="label label-success" disabled>' + c.action_status + '</label>'
                        }
                        else {
                            let attr = '';
                            for (let i of c.action_status_detail.split(',')) {
                                let Iresult = i.split('-')[0];
                                let Iremark = i.split('-')[1];
                                if (Iresult == '未迁服') {
                                    attr += '<label class="label label-warning">' + Iresult + '</label><br/>'
                                }
                                if (Iresult == '迁服成功') {
                                    attr += '<label class="label label-success">' + Iresult + '</label></span><br/>'
                                }
                                if (Iresult == '迁服失败') {
                                    attr += '<span class="tooltip-demo text-danger"><label class="label label-danger" data-toggle="popover" data-placement="right" disabled title="' + Iremark + '">' + Iresult + '</label></span><br/>'
                                }
                            }
                            console.log(attr)
                            return attr;
                        }
                    }
                    else {
                        return ''
                    }
                }
            },
            {
                'targets': 13,
                'width': '11%',
                render: function (a, b, c, d) {
                    return '<span class="tooltip-demo"><span>' + c.recover_time + '&nbsp;</span><label type="button" class="label label-danger" data-toggle="tooltip" data-placement="top" title="' + c.recover_deadline + '">截</label></span>'
                }
            },
            {
                'targets': 15,
                render: function (a, b, c, d) {
                    if (c.recover_status == '回收中') {
                        return '<label class="label label-info" disabled>' + c.recover_status + '</label>'
                    }
                    else if (c.recover_status == '取消') {
                        return '<label class="label label-default" disabled>' + c.recover_status + '</label>'
                    }
                    else if (c.recover_status == '回收成功') {
                        return '<label class="label label-success" disabled>' + c.recover_status + '</label>'
                    }
                    else {
                        let attr = '';
                        for (let i of c.recover_status_detail.split(',')) {
                            let Iresult = i.split('-')[0];
                            let Iremark = i.split('-')[1];
                            if (Iresult == '未回收') {
                                attr += '<label class="label label-warning">' + Iresult + '</label><br/>'
                            }
                            if (Iresult == '回收成功') {
                                attr += '<label class="label label-success">' + Iresult + '</label><br/>'
                            }
                            if (Iresult == '回收失败') {
                                attr += '<span class="tooltip-demo text-danger"><label class="label label-danger" data-toggle="popover" data-placement="right" disabled title="' + Iremark + '">' + Iresult + '</label><br/>'
                            }
                        }
                        return attr;
                    }
                }
            },
            {
                targets: 16,
                render: function (a, b, c, d) {
                    if (c.type == '迁服回收') {
                        if (c.action_status == '未迁服') {
                            var context =
                                {
                                    func: [
                                        {
                                            "name": "修改",
                                            "fn": "edit(\'" + c.id + "\')",
                                            "type": "primary",
                                            "class": "but_xq"
                                        },
                                        {
                                            "name": "迁服",
                                            "fn": "execute_confirm(\'" + c.id + "\')",
                                            "type": "danger"
                                        },
                                    ]
                                };
                            var html = template(context);
                            return html;
                        }
                        if (c.action_status == '迁服成功' && c.recover_status == '未回收') {
                            var context =
                                {
                                    func: [
                                        {"name": "修改", "fn": "edit(\'" + c.id + "\')", "type": "primary"},
                                        {
                                            "name": "回收",
                                            "fn": "execute_confirm(\'" + c.id + "\')",
                                            "type": "danger"
                                        },
                                    ]
                                };
                            var html = template(context);
                            return html;
                        }
                        else {
                            var context =
                                {
                                    func: [
                                        {"name": "修改", "fn": "edit(\'" + c.id + "\')", "type": "primary"},
                                    ]
                                };
                            var html = template(context);
                            return html;
                        }
                    }
                    else {
                        if (c.recover_status == '未回收') {
                            var context =
                                {
                                    func: [
                                        {"name": "修改", "fn": "edit(\'" + c.id + "\')", "type": "primary"},
                                        {
                                            "name": "回收",
                                            "fn": "execute_confirm(\'" + c.id + "\')",
                                            "type": "danger"
                                        },
                                    ]
                                };
                            var html = template(context);
                            return html;
                        }
                        else {
                            var context =
                                {
                                    func: [
                                        {"name": "修改", "fn": "edit(\'" + c.id + "\')", "type": "primary"},
                                    ]
                                };
                            var html = template(context);
                            return html;
                        }
                    }
                }
            },
            // {
            //     targets: 17,
            //     render: function (a, b, c, d) {
            //         var context =
            //             {
            //                 func: [
            //                     {"name": "查看", "fn": "detail(\'" + c.id + "\')", "type": "info"},
            //                 ]
            //             };
            //         var html = template(context);
            //         return html;
            //     }
            // },
            {
                targets: 17,
                render: function (a, b, c, d) {
                    var context =
                        {
                            func: [
                                {"name": "cmdb", "fn": "log(\'" + c.id + "\')", "type": "link"},
                            ]
                        };
                    var html = template(context);
                    return html;
                }
            }
        ],
        "language":
            {
                "url":
                    "/static/js/i18n/Chinese.json"
            },
        "initComplete": function (settings, json) {
            // tooltip demo
            $('.tooltip-demo').tooltip({
                selector: "[data-toggle=tooltip]",
                container: "body"
            });
            // popover demo
            $("[data-toggle=popover]")
                .popover()
        }
    });


    // 翻页后也要重新初始化提示插件
    $('#mytable').on('draw.dt', function () {
        // tooltip demo
        $('.tooltip-demo').tooltip({
            selector: "[data-toggle=tooltip]",
            container: "body"
        });
        // popover demo
        $("[data-toggle=popover]")
            .popover()
    });

    // 设置权限
    is_superuser = $("#is_superuser").data('is-superuser');
    if (is_superuser == "true") {
        table.column(16).visible(false);
        table.column(7).visible(false);
        table.column(11).visible(false);
        table.column(17).visible(false);
    }
    if (is_superuser == "False") {
        table.column(6).visible(false);
        table.column(11).visible(false);
        table.column(16).visible(false);
        table.column(17).visible(false);
    }

    $(':checkbox.toggle-visiable').on('click', function (e) {
        var is_checked = $(this).is(':checked');
        var column = table.column($(this).attr('value'));
        column.visible(is_checked);
    });

    $('#bt-search').click(function () {
        $('#div-search').toggleClass('hide');
    });

    $('input.column_filter').on('keyup click', function () {
        table.ajax.reload();
    });

    $(".filter_select2").select2({}).on("select2:select", function (e) {
        table.ajax.reload();
    });

    $("#bt-reset").click(function () {
        // 重置高级搜索
        $("#filter_title").val('');
        $(".filter_select2").val('0').trigger('change');
        $("#filter_start_action_time").val('');
        $("#filter_end_action_time").val('');
        $("#filter_start_recover_time").val('');
        $("#filter_end_recover_time").val('');
        $("#filter_start_apply_time").val('');
        $("#filter_end_apply_time").val('');
        table.ajax.reload();
    });

    initModalSelect2();

    preFilter();

    // 时间插件初始化
    $(".flatpickr").flatpickr({
        locale: "zh",
        enableTime: true,
        time_24hr: true,
        onChange: function () {
            table.ajax.reload();
        }
    });


    //提示工具
    $("[data-toggle=popover]")
        .popover();

    $('.tooltip-demo').tooltip({
        selector: "[data-toggle=tooltip]",
        container: "body"
    });

    init_ws()

});


function initModalSelect2() {
    $select2Project = $("#filter_project").select2({
        ajax: {
            url: '/myworkflows/list_game_project/',
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
                var dict = {
                    results: $.map(data, function (item) {
                        return {
                            id: item.id,
                            text: item.text,
                        }
                    })
                };
                var list = dict['results'];
                list.unshift({'id': 0, 'text': '全部'});
                dict['results'] = list;
                return dict
            },
            cache: false,
        },
        escapeMarkup: function (markup) {
            return markup;
        },
        placeholder: '游戏项目',
    });

    $select2Room = $("#filter_room").select2({
        ajax: {
            url: '/myworkflows/list_room_name_by_project/',
            dataType: 'json',
            type: 'POST',
            delay: 30,
            data: function (params) {
                var project = $("#filter_project").val();
                if (project == 0) {
                    alert('请先选择游戏项目')
                }
                else {
                    return {
                        q: params.term,
                        page: params.page,
                        project: $("#filter_project").select2('data')[0].id,
                    };
                }
            },

            processResults: function (data, params) {
                params.page = params.page || 1;
                var dict = {
                    results: $.map(data, function (item) {
                        return {
                            id: item.id,
                            text: item.text,
                        }
                    })
                };
                var list = dict['results'];
                list.unshift({'id': 0, 'text': '全部'});
                dict['results'] = list;
                return dict
            },
            cache: false,
        },
        escapeMarkup: function (markup) {
            return markup;
        },
        placeholder: '机房',
    });

    // 初始化运维负责人
    $select2Ops = $("#filter_ops").select2({
        ajax: {
            url: '/assets/list_ops_user/',
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
                var dict = {
                    results: $.map(data, function (item) {
                        return {
                            id: item.id,
                            text: item.text,
                        }
                    })
                };
                var list = dict['results'];
                list.unshift({'id': 0, 'text': '全部'});
                dict['results'] = list;
                return dict
            },
            cache: false,
        },
        escapeMarkup: function (markup) {
            return markup;
        },
        placeholder: '请选择运维负责人',
    });

    // 定义操作类型为select2
    $select2Type = $("#filter_type").select2({
        ajax: {
            url: '/myworkflows/list_host_compression_type/',
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
                var dict = {
                    results: $.map(data, function (item) {
                        return {
                            id: item.id,
                            text: item.text,
                        }
                    })
                };
                var list = dict['results'];
                list.unshift({'id': 0, 'text': '全部'});
                dict['results'] = list;
                return dict
            },
            cache: false,
        },
        escapeMarkup: function (markup) {
            return markup;
        },
        placeholder: '请选择操作类型',
    });

    // 定义状态为select2
    $select2ActionStatus = $("#filter_action_status").select2({
        ajax: {
            url: '/myworkflows/list_host_compression_action_status/',
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
                var dict = {
                    results: $.map(data, function (item) {
                        return {
                            id: item.id,
                            text: item.text,
                        }
                    })
                };
                var list = dict['results'];
                list.unshift({'id': 0, 'text': '全部'});
                dict['results'] = list;
                return dict
            },
            cache: false,
        },
        escapeMarkup: function (markup) {
            return markup;
        },
        placeholder: '请选择状态',
    });

    // 定义状态为select2
    $select2RecoverStatus = $("#filter_recover_status").select2({
        ajax: {
            url: '/myworkflows/list_host_compression_recover_status/',
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
                var dict = {
                    results: $.map(data, function (item) {
                        return {
                            id: item.id,
                            text: item.text,
                        }
                    })
                };
                var list = dict['results'];
                list.unshift({'id': 0, 'text': '全部'});
                dict['results'] = list;
                return dict
            },
            cache: false,
        },
        escapeMarkup: function (markup) {
            return markup;
        },
        placeholder: '请选择状态',
    });

    // 定义修改任务状态下拉框类型为select2
    $("#edit_action_status").select2({
        ajax: {
            url: '/myworkflows/list_host_compression_action_status/',
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
        escapeMarkup: function (markup) {
            return markup;
        },
        placeholder: '请选择状态',
    });


    // 定义修改任务状态下拉框类型为select2
    $("#edit_recover_status").select2({
        ajax: {
            url: '/myworkflows/list_host_compression_recover_status/',
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
        escapeMarkup: function (markup) {
            return markup;
        },
        placeholder: '请选择状态',
    });


    //定义修改任务运维负责人下拉框为select2
    $("#edit_ops").select2({
        ajax: {
            url: '/assets/list_ops_user/',
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
        escapeMarkup: function (markup) {
            return markup;
        },
        placeholder: '请选择运维负责人',
    });


}


// 查看主机回收/迁服申请详细页面
function detail(id) {
    window.location.href = '/myworkflows/host_compression_apply_detail/' + id + '/';
}

//修改任务状态函数
function edit(id) {
    $('#modal-notify').hide();
    var inputIds = {
        'apply_id': id,
    };
    var encoded = $.toJSON(inputIds);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/myworkflows/get_data_host_compression_apply/",
        contentType: "application/json; charset=utf-8",
        data: pdata,
        success: function (data) {
            if (data.success) {
                $('#myModalLabel').text('修改-' + data.title);
                $('#id_edit').attr('value', id);
                initSelect2('edit_action_status', data.action_status_id, data.action_status_text);
                initSelect2('edit_recover_status', data.recover_status_id, data.recover_status_text);
                initSelect2('edit_ops', data.ops_id, data.ops_text);
                $('#edit_action_time').val(data.action_time);
                $('#edit_action_deadline').val(data.action_deadline);
                $('#div_action_time').css('display', 'none');
                $('#div_action_status').css('display', 'none');
                $('#div_action_deadline').css('display', 'none');
                $('#edit_recover_time').val(data.recover_time);
                $('#edit_recover_deadline').val(data.recover_deadline);
                if (data.type_id == 2) {
                    $('#div_action_time').css('display', 'block');
                    $('#div_action_deadline').css('display', 'block');
                    $('#div_action_status').css('display', 'block');
                }
                $('#myModal').modal('show');
            }
            else {
                alert(data.msg)
            }
        },
        error: function (data) {
            if (xhr.status == '403') {
                alert('权限拒绝');
            } else {
                alert('内部错误');
            }
        }
    });
}


//保存修改任务状态
function save() {
    var apply_id = $('#id_edit').val();
    var action_status = $('#edit_action_status').val();
    var recover_status = $('#edit_recover_status').val();
    var ops = $('#edit_ops').val();
    var action_time = $('#edit_action_time').val();
    var action_deadline = $('#edit_action_deadline').val();
    var recover_time = $('#edit_recover_time').val();
    var recover_deadline = $('#edit_recover_deadline').val();
    if (!action_status) {
        $('#lb-msg').text('请选择迁服状态');
        $('#modal-notify').show();
        return false;
    }
    if (!recover_status) {
        $('#lb-msg').text('请选择回收状态');
        $('#modal-notify').show();
        return false;
    }
    var inputIds = {
        'apply_id': apply_id,
        'action_status': action_status,
        'recover_status': recover_status,
        'ops': ops,
        'action_time': action_time,
        'action_deadline': action_deadline,
        'recover_time': recover_time,
        'recover_deadline': recover_deadline,
    };
    var encoded = $.toJSON(inputIds);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/myworkflows/edit_host_compression_apply/",
        contentType: "application/json; charset=utf-8",
        data: pdata,
        success: function (data) {
            if (data.success) {
                location.reload();
            }
            else {
                alert(data.msg)
            }
        },
        error: function (data) {
            if (xhr.status == '403') {
                alert('权限拒绝');
            } else {
                alert('内部错误');
            }
        }
    });

}


//执行任务确认弹窗
function execute_confirm(id) {
    $('#id_execute').attr('value', id);
    $('#id_confirm').text('确认要手动执行操作吗？');
    $('#myModal2').modal('show');
}


//执行任务
function execute() {
    var apply_id = $('#id_execute').val();
    var inputIds = {
        'apply_id': apply_id,
    };
    var encoded = $.toJSON(inputIds);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/myworkflows/execute_host_compression/",
        contentType: "application/json; charset=utf-8",
        data: pdata,
        beforeSend: function () {
            $('#myModal2').modal('hide');
        },
        success: function (data) {
            table.ajax.reload();
            if (data.success) {
                $('#id_notice').text(data.msg);
                $('#myModal3').modal('show');
            }
            else {
                $('#id_notice').text(data.msg);
                $('#myModal3').modal('show');
            }
        },
        error: function (data) {
            if (xhr.status == '403') {
                alert('权限拒绝');
            } else {
                alert('内部错误');
            }
        }
    });
}


//初始化websocket
function init_ws() {
    var protocol = window.location.protocol;
    if (protocol == 'http:') {
        wsp = 'ws:'
    } else {
        wsp = 'wss:'
    }
    socket = new ReconnectingWebSocket(wsp + "//" + window.location.host + "/ws/host_compression_list/", null, {debug: true});

    socket.onmessage = function (e) {
        var data = $.parseJSON(e.data);
        if (data.message == "update_table") {
            table.ajax.reload();
        }
    };

    socket.onopen = function () {
        socket.send("start ws connection");
    };

    if (socket.readyState == WebSocket.OPEN) socket.onopen();

}


//跳转到日志页面
function log(id) {
    window.open("/myworkflows/host_compression_cmdb_log/" + id + "/");
}