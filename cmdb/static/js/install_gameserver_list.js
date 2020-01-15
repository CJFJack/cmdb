var table;

//预编译模板
var tpl = $("#tpl").html();
var str = "确定执行选中的区服?";
var count = 0;

var template = Handlebars.compile(tpl);

function initModalSelect2() {
    $(".filter_select2").select2().on("select2:select", function (e) {
        table.ajax.reload();
    });
    $("#status").select2();
};

function edit(id) {
    editFlag = true;
    var data = {
        'id': id,
    };
    var encoded = $.toJSON(data);
    var pdata = encoded;

    $.ajax({
        type: "POST",
        url: "/ops/get_install_game/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function (data) {
            origin_data = data;
            $("#myModalLabel").text("修改开服计划");
            $("#modal-notify").hide();
            $("#id").val(data.id);
            $("#show_id").hide();
            $("#srv_name").val(data.srv_name);
            $("#status").val(data.status).trigger('change');
            $("#myModal").modal("show");
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

function init_ws() {
    var protocol = window.location.protocol;
    if (protocol == 'http:') {
        wsp = 'ws:'
    } else {
        wsp = 'wss:'
    }
    socket = new ReconnectingWebSocket(wsp + "//" + window.location.host + "/ws/game_install/", null, {debug: true});

    socket.onmessage = function (e) {
        console.log(e)
        if (e.data == 'update_table') {
            // console.log('reload');
            table.ajax.reload();
        }
    }

    socket.onopen = function () {
        socket.send("start ws connection");
    }

    if (socket.readyState == WebSocket.OPEN) socket.onopen();

}

$(document).ready(function () {

    init_ws();

    var rows_selected = [];
    table = $('#mytable').DataTable({
        "processing": true,
        "serverSide": true,
        "ordering": false,
        "ajax": {
            "url": "/ops/data_install_gameserver_list/",
            "type": "POST",
            "data": function (d) {
                d.filter_project_type = $("#filter_project_type").select2('data')[0].id;
                d.filter_project = $("#filter_project").select2('data')[0].id;
                d.filter_srv_status = $("#filter_srv_status").select2('data')[0].id;
                d.filter_game_type = $("#filter_game_type").select2('data')[0].id;
                d.filter_pf_name = $("#filter_pf_name").val();
                d.filter_internal_ip = $("#filter_internal_ip").val();
                d.filter_telecom_ip = $("#filter_telecom_ip").val();
                d.filter_unicom_ip = $("#filter_unicom_ip").val();
                d.filter_srv_name = $("#filter_srv_name").val();
                d.filter_room = $("#filter_room").select2('data')[0].id;
                d.filter_ip = $("#filter_ip").val();
                d.filter_merge_id = $("#filter_merge_id").val();
                d.filter_merge_time = $("#filter_merge_time").val();
                d.filter_client_version = $("#filter_client_version").val();
                d.filter_server_version = $("#filter_server_version").val();
                d.filter_cdn_root_url = $("#filter_cdn_root_url").val();
                d.filter_cdn_dir = $("#filter_cdn_dir").val();
                d.filter_open_time = $("#filter_open_time").val();
                d.filter_area_name = $("#filter_area_name").val();
                d.filter_master_server = $("#master_server").is(':checked');
            }
        },
        "columns": [
            {"data": null},  // 0
            {"data": "id"},  // 1
            {"data": "open_time"},  // 2
            {"data": "project"},  // 3
            {"data": "area"},  // 4
            {"data": "pf_id"},  // 5
            {"data": "pf_name"},  // 6
            {"data": "srv_num"},  // 7
            {"data": "srv_name"},  // 8
            {"data": "server_version"},  // 9
            {"data": "client_version"},  // 10
            {"data": "client_dir"},  // 11
            {"data": "qq_srv_id"},  // 12
            {"data": "srv_type"},  // 13
            {"data": "srv_farm_id"},  // 14
            {"data": "srv_farm_name"},  // 15
            {"data": "unique_srv_id"},  // 16
            {"data": "status"},  // 17
            {
                "data": null,     //18
                "orderable": false,
            }
        ],
        "order": [[2, 'asc']],
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
                'searchable': false,
                'orderable': false,
                'visible': false,
            },
            /*{
                'targets': 9,
                "width": "20%",
                "render": function(data, type, row){
                    return data.split(",").join("<br/>");
                },
            },*/
            {
                'targets': 17,
                'searchable': false,
                'orderable': false,
                'className': 'dt-body-left',
                'render': function (a, b, c, d) {
                    if (c.status == '安装成功' || c.status == '卸载成功') {
                        return '<span class="label label-success">' + c.status + '</span>';
                    } else if (c.status == '安装中' || c.status == '卸载中') {
                        return '<span class="label label-info">' + c.status + '</span>';
                    } else if (c.status == '安装失败') {
                        return '<span class="tooltip-demo"><span data-toggle="tooltip" data-placement="left" class="label label-danger" title="' + c.install_remark + '">' + c.status + '</span></span>'
                    } else if (c.status == '卸载失败') {
                        return '<span class="tooltip-demo"><span data-toggle="tooltip" data-placement="left" class="label label-danger" title="' + c.uninstall_remark + '">' + c.status + '</span></span>'
                    } else {
                        return '<span class="label label-default">' + c.status + '</span>';
                    }
                },
            },
            {
                targets: 18,
                render: function (a, b, c, d) {
                    var context =
                        {
                            func: [
                                {"name": "修改", "fn": "edit(\'" + c.id + "\')", "type": "info"},
                            ]
                        };
                    var html = template(context);
                    return html;
                }
            }
        ],
        "language": {
            "url": "/static/js/i18n/Chinese.json"
        },
        initComplete: function () {
            // tooltip demo
            $('.tooltip-demo').tooltip({
                selector: "[data-toggle=tooltip]",
                container: "body"
            })
        }
    });

    initModalSelect2();

    // 翻页后也要重新初始化提示插件
    $('#mytable').on('draw.dt', function () {
        // tooltip demo
        $('.tooltip-demo').tooltip({
            selector: "[data-toggle=tooltip]",
            container: "body"
        })
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
            makeGameSrvInstallTitle(str, ++count);
        } else {
            $row.removeClass('selected');
            makeGameSrvInstallTitle(str, --count);
        }

        // Prevent click event from propagating to parent
        e.stopPropagation();
    });

    // Handle click on table cells
    // $('#mytable tbody').on('click', 'td', function(e){
    //     $(this).parent().find('input[type="checkbox"]').trigger('click');
    // });

    $('input.column_filter').on('keyup click', function () {
        // filterColumn( $(this).parents('tr').attr('data-column') );
        table.ajax.reload();
    });

    $("#master_server").click(function () {
        table.ajax.reload();
    });

    $('#chb-all').on('click', function (e) {
        var checkbox = document.getElementById('chb-all');
        $('#mytable tbody td').parent().find('input[type="checkbox"]').map(function (i, n) {
            var $row = $(this).closest('tr');
            n.checked = checkbox.checked;
            if (checkbox.checked) {
                $row.addClass('selected');
                count = getSelectedTable().length;
                makeGameSrvInstallTitle(str, count);
            } else {
                $row.removeClass('selected');
                count = 0;
                makeGameSrvInstallTitle(str, count);
            }
        });

    });

    $('#bt-search').click(function () {
        $('#div-search').toggleClass('hide');
    });

    $("#bt-reset").click(function () {
        // 重置高级搜索
        $("#filter_project").val('0').trigger('change');
        $("#filter_project_type").val('100').trigger('change');
        $("#filter_srv_status").val('100').trigger('change');
        $("#filter_game_type").val('0').trigger('change');
        $(".column_filter").val('');
        table.ajax.reload();

    });


    $('#bt-save').click(function () {

        var id = $("#id").val();
        var status = $("#status").val()

        var inputIds = {
            "id": id,
            "status": status,
        };

        var encoded = $.toJSON(inputIds)
        var pdata = encoded

        var urls = '/ops/edit_install_game/'

        $.ajax({
            type: "POST",
            url: urls,
            contentType: "application/json; charset=utf-8",
            data: pdata,
            success: function (data) {

                if (data['data']) {
                    table.ajax.reload();
                    $("#myModal").modal("hide");
                } else {
                    $('#lb-msg').text(data['msg']);
                    $('#modal-notify').show();
                }
                ;
            },
            error: function (data) {
                if (editFlag) {
                    $('#lb-msg').text('权限拒绝');
                    $('#modal-notify').show();
                } else {
                    $('#lb-msg').text('权限拒绝');
                    $('#modal-notify').show();
                }
            }
        });
    });


    $(':checkbox.toggle-visiable').on('click', function (e) {
        //e.preventDefault();

        // Get the column API object
        var is_checked = $(this).is(':checked');
        var column = table.column($(this).attr('value'));
        // table.ajax.reload();
        column.visible(is_checked);
    });


    $("#bt-install").confirm({
        //text:"确定install?",
        confirm: function (button) {
            var selected = getSelectedTable();

            if (selected.length == 0) {
                alert('请选择');
            } else {
                var encoded = $.toJSON(selected);
                var pdata = encoded;
                $.ajax({
                    type: "POST",
                    url: "/ops/game_install/",
                    contentType: "application/json; charset=utf-8",
                    data: pdata,
                    success: function (data) {

                        if (data['data']) {
                            // table.ajax.reload();
                            makeGameSrvInstallTitle(str, 0);
                            count = 0;
                        } else {
                            alert(data['msg']);
                            // table.ajax.reload();
                            makeGameSrvInstallTitle(str, 0);
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


    $("#bt-uninstall").confirm({
        //text:"确定uninstall?",
        confirm: function (button) {
            var selected = getSelectedTable();

            if (selected.length == 0) {
                alert('请选择');
            } else {
                var encoded = $.toJSON(selected);
                var pdata = encoded;
                $.ajax({
                    type: "POST",
                    url: "/ops/game_uninstall/",
                    contentType: "application/json; charset=utf-8",
                    data: pdata,
                    success: function (data) {

                        if (data['data']) {
                            // table.ajax.reload();
                            makeGameSrvInstallTitle(str, 0);
                            count = 0;
                        } else {
                            alert(data['msg']);
                            // table.ajax.reload();
                            makeGameSrvInstallTitle(str, 0);
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

});


function install(id) {
    var r = confirm("确定安装？");
    if (r == true) {
        var inputs = [id];
        var encoded = $.toJSON(inputs);
        var pdata = encoded;
        $.ajax({
            type: "POST",
            url: "/ops/game_install/",
            contentType: "application/json; charset=utf-8",
            data: pdata,
            success: function (data) {

                if (data['data']) {
                    table.ajax.reload(null, false);
                } else {
                    alert(data['msg']);
                    table.ajax.reload(null, false);
                }
            }
        });
    }
}


function uninstall(id) {
    var r = confirm("确定卸载？");
    if (r == true) {
        var inputs = [id];
        var encoded = $.toJSON(inputs);
        var pdata = encoded;
        $.ajax({
            type: "POST",
            url: "/ops/game_uninstall/",
            contentType: "application/json; charset=utf-8",
            data: pdata,
            success: function (data) {
                if (data['data']) {
                    table.ajax.reload(null, false);
                } else {
                    alert(data['msg']);
                    table.ajax.reload(null, false);
                }
            }
        });
    }
}
