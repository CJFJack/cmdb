var table;
var editFlag;
var tpl = $("#tpl").html();
//预编译模板
var template = Handlebars.compile(tpl);

// 修改之前的数据
var origin_data;

var $select2Project;
var $select2Room;

var str = "确定删除选中的运维管理机?";
var count = 0;


function formatRepo(repo) {

    var markup = '<div class="clearfix"><div clas="col-sm-7">' + repo.text + '</div></div>';

    return markup;
};

function formatRepoSelection(repo) {
    return repo.text || repo.id;
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
        url: "/assets/get_cmdb_ops_manager_list/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function (data) {
            origin_data = data;
            $("#myModalLabel").text("修改运维管理机");
            $("#modal-notify").hide();
            $("#id").val(data.id);
            $("#show_id").hide();
            initSelect2('project', data.project_id, data.project_name);
            $("#area").val(data.area);
            initSelect2('room', data.room_id, data.room_name);
            $("#url").val(data.url);
            $("#token").val(data.token);
            $("#rsync_module").val(data.rsync_module);
            $("#rsync_user").val(data.rsync_user);
            $("#rsync_pass_file").val(data.rsync_pass_file);
            $("#rsync_port").val(data.rsync_port);
            $("#rsync_ip").val(data.rsync_ip);
            $("#proxy_url").val(data.proxy_url);
            if (data.is_proxy) {
                $('input:radio[name="is_proxy"]').filter('[value="1"]').prop('checked', true);
            } else {
                $('input:radio[name="is_proxy"]').filter('[value="0"]').prop('checked', true);
            }
            if (data.enable) {
                $('input:radio[name="enable"]').filter('[value="1"]').prop('checked', true);
            } else {
                $('input:radio[name="enable"]').filter('[value="0"]').prop('checked', true);
            }
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
};

function initModalSelect2() {
    // 初始化select2
    $select2Project = $('#project').select2({
        ajax: {
            url: '/assets/list_game_project/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page
                };
            },

            processResults: function (data, params) {
                // parse the results into the format expected by Select2
                // since we are using custom formatting functions we do not need to
                // alter the remote JSON data, except to indicate that infinite
                // scrolling can be used
                params.page = params.page || 1;
                return {
                    results: $.map(data, function (item) {
                        return {
                            id: item.id,
                            text: item.text,
                        }
                    })
                    // pagination: {
                    //     more: (params.page * 30) < data.total_count
                    // };
                }
            },
            cache: false,
        },
        //minimumResultsForSearch: Infinity,
        escapeMarkup: function (markup) {
            return markup;
        }, // let our custom formatter work
        // minimumInputLength: 1,
        templateResult: formatRepo, // omitted for brevity, see the source of this page
        templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });

    $select2Room = $('#room').select2({
        ajax: {
            url: '/assets/list_room/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page
                };
            },

            processResults: function (data, params) {
                // parse the results into the format expected by Select2
                // since we are using custom formatting functions we do not need to
                // alter the remote JSON data, except to indicate that infinite
                // scrolling can be used
                params.page = params.page || 1;
                return {
                    results: $.map(data, function (item) {
                        return {
                            id: item.id,
                            text: item.text,
                        }
                    })
                    // pagination: {
                    //     more: (params.page * 30) < data.total_count
                    // };
                }
            },
            cache: false,
        },
        //minimumResultsForSearch: Infinity,
        escapeMarkup: function (markup) {
            return markup;
        }, // let our custom formatter work
        // minimumInputLength: 1,
        templateResult: formatRepo, // omitted for brevity, see the source of this page
        templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });

    $.fn.modal.Constructor.prototype.enforceFocus = function () {
    };

};

$(document).ready(function () {
    $.fn.select2.defaults.set("theme", "bootstrap");

    initModalSelect2();

    var rows_selected = [];
    table = $('#mytable').DataTable({
        "processing": true,
        //"serverSide": true,
        "ordering": false,
        "autoWidth": true,
        "ajax": "/assets/data_ops_manager_list/",
        "columns": [
            {"data": null},
            {"data": "id"},
            {"data": "project"},
            {"data": "area"},
            {"data": "room"},
            {"data": "url"},
            {"data": "is_proxy"},
            {"data": "proxy_url"},
            {"data": "token"},
            {"data": "status"},
            {"data": "rsync_module"},
            {"data": "rsync_user"},
            {"data": "rsync_pass_file"},
            {"data": "rsync_ip"},
            {"data": "rsync_port"},
            {"data": "enable"},
            {
                "data": null,
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
                'visible': false,
                'searchable': false
            },
            {
                'targets': [7, 8],
                'visible': false,
            },
            {
                'targets': 6,
                render: function (a, b, c, d) {
                    if (c.is_proxy == '是') {
                        return '<label class="label label-info">是</label>'
                    }
                    else {
                        return '<label class="label label-default">否</label>'
                    }
                }
            },
            {
                'targets': 15,
                render: function (a, b, c, d) {
                    if (c.enable) {
                        return '<label class="label label-success">启用</label>'
                    }
                    else {
                        return '<label class="label label-danger">禁用</label>'
                    }
                }
            },
            {
                targets: 16,
                render: function (a, b, c, d) {
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
        ],
        "language": {
            "url": "/static/js/i18n/Chinese.json"
        },

    });

    $(':checkbox.toggle-visiable').on('click', function (e) {
        //e.preventDefault();

        // Get the column API object
        var is_checked = $(this).is(':checked');
        var column = table.column($(this).attr('value'));
        // table.ajax.reload();
        column.visible(is_checked);
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
                    url: "/assets/del_data_cmdb_ops_manager_list/",
                    contentType: "application/json; charset=utf-8",
                    data: pdata,
                    success: function (data) {

                        if (data['data']) {
                            table.ajax.reload(null, false);
                            makeTitle(str, 0);
                            count = 0;
                        } else {
                            alert(data['msg'])
                            table.ajax.reload(null, false);
                            makeTitle(str, 0);
                            count = 0;
                        }
                        ;
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
        $("#myModalLabel").text("新增运维管理机");
        $("#modal-notify").hide();
        $("#show_id").hide();
        $("#id").val('');
        initSelect2('project', '0', '选择项目');
        $("#area").val('');
        initSelect2('room', '0', '选择机房');
        $("#url").val('');
        $("#token").val('');
        $("#rsync_module").val('');
        $("#rsync_pass_file").val('');
        $("#rsync_port").val('');
        $("#rsync_user").val('');
        $("#rsync_ip").val('');
        $("#proxy_url").val('');
        $('input[name=is_proxy]:first').prop('checked', false);
        $('input[name=enable]:first').prop('checked', true);
        editFlag = false;
        $("#myModal").modal("show");
    });

    $('#bt-save').click(function () {

        var id = $("#id").val();
        var project = $("#project").select2('data')[0].id;
        var area = $("#area").val();
        var room = $("#room").select2('data')[0].id;
        var _url = $('#url').val();
        var token = $("#token").val();
        var rsync_module = $("#rsync_module").val();
        var rsync_user = $("#rsync_user").val();
        var rsync_pass_file = $("#rsync_pass_file").val();
        var rsync_port = $("#rsync_port").val();
        var rsync_ip = $("#rsync_ip").val();
        var proxy_url = $("#proxy_url").val();
        var is_proxy = $('input[name=is_proxy]:checked').val();
        var enable = $('input[name=enable]:checked').val();

        if (!/\/$/.test(_url)) {
            $('#lb-msg').text('url要/结尾');
            $('#modal-notify').show();
            return false;
        }

        if (project == '0') {
            $('#lb-msg').text('请选择项目!');
            $('#modal-notify').show();
            return false;
        }

        if (area == '') {
            $('#lb-msg').text('请输入区域!');
            $('#modal-notify').show();
            return false;
        }

        if (room == '0') {
            $('#lb-msg').text('请选择机房!');
            $('#modal-notify').show();
            return false;
        }

        if (_url == '') {
            $('#lb-msg').text('请输入url!');
            $('#modal-notify').show();
            return false;
        }

        if (token == '') {
            $('#lb-msg').text('请输入token!');
            $('#modal-notify').show();
            return false;
        }

        if (rsync_ip == '') {
            $('#lb-msg').text('请输入rsync ip!');
            $('#modal-notify').show();
            return false;
        }

        if (proxy_url != '') {
            if (!/\/$/.test(proxy_url)) {
                $('#lb-msg').text('代理url要/结尾');
                $('#modal-notify').show();
                return false;
            }
        }

        var inputIds = {
            "id": id,
            "project": project,
            'area': area,
            "room": room,
            "url": _url,
            "token": token,
            "editFlag": editFlag,
            'rsync_module': rsync_module,
            'rsync_user': rsync_user,
            'rsync_pass_file': rsync_pass_file,
            'rsync_port': rsync_port,
            'rsync_ip': rsync_ip,
            'proxy_url': proxy_url,
            'is_proxy': is_proxy,
            'enable': enable,
        };

        var encoded = $.toJSON(inputIds);
        var pdata = encoded;

        var urls = '/assets/add_or_edit_ops_manager/'

        $.ajax({
            type: "POST",
            url: urls,
            contentType: "application/json; charset=utf-8",
            data: pdata,
            success: function (data) {

                if (data['data']) {
                    table.ajax.reload(null, false);
                    $("#myModal").modal("hide");
                } else {
                    $('#lb-msg').text(data['msg']);
                    $('#modal-notify').show();
                }
                ;
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
