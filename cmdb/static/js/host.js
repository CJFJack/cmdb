// 修改之前的数据
var origin_data;

var table;
var editFlag;
var deviceFlag;
var tpl = $("#tpl").html();
//预编译模板
var template = Handlebars.compile(tpl);

var str = "确定删除选中的主机?";
var count = 0;

var $select2_belongs_to_game_project;
var $select2_belongs_to_room;
var $select2_belongs_to_business;
var $select2_host_class;
var $select2_status;
var $select2_machine_type;
var $select2_system;
var $select2_is_internet;


function url_preFilter() {
    var filter_room = $.urlParam('room');
    var filter_status = $.urlParam('status');
    var filter_project = $.urlParam('project');

    if (filter_room !== null) {
        let filter_room_val = $("#filter_belongs_to_room option:contains('" + filter_room + "')").val();
        $("#filter_belongs_to_room").val(filter_room_val).trigger('change');
    }

    if (filter_status !== null) {
        let filter_status_val = $("#filter_status option:contains('" + filter_status + "')").val();
        $("#filter_status").val(filter_status_val).trigger('change');
    }

    if (filter_project !== null) {
        let filter_project_val = $("#filter_belongs_to_game_project option:contains('" + filter_project + "')").val();
        $("#filter_belongs_to_game_project").val(filter_project_val).trigger('change');
    }
}


function filterColumn(i) {
    $('#mytable').DataTable().column(i).search(
        $('#col' + i + '_filter').val(),
        $('#col' + i + '_regex').prop('checked'),
        $('#col' + i + '_smart').prop('checked')
    ).draw();
}

function initModalSelect2() {
    // 初始化select2
    $select2_host_class = $("#host_class").select2({
        minimumResultsForSearch: Infinity,
    });

    $select2_status = $("#status").select2({
        minimumResultsForSearch: Infinity,
    });

    $select2_belongs_to_game_project = $('#belongs_to_game_project').select2({
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

    $select2_belongs_to_room = $('#belongs_to_room').select2({
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

    $select2_machine_type = $("#machine_type").select2({
        minimumResultsForSearch: Infinity,
    });

    $select2_belongs_to_business = $('#belongs_to_business').select2({
        ajax: {
            url: '/assets/list_business/',
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


    $select2_opsmanager = $('#opsmanager').select2({
        ajax: {
            url: '/assets/list_opsmanager/',
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
        //minimumResultsForSearch: Infinity,
        escapeMarkup: function (markup) {
            return markup;
        }, // let our custom formatter work
        // minimumInputLength: 1,
        templateResult: formatRepo, // omitted for brevity, see the source of this page
        templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });


    $select2_system = $("#system").select2({
        minimumResultsForSearch: Infinity,
    });

    $select2_is_internet = $("#is_internet").select2({
        minimumResultsForSearch: Infinity,
    });


    $.fn.modal.Constructor.prototype.enforceFocus = function () {
    };

}

function initFilterTable() {
    $select2_filter_stauts = $("#filter_status").select2({
        minimumResultsForSearch: Infinity,
    })
    $select2_filter_stauts.on("change", function (e) {
        reload_datatables("select2:select", e);
    });

    $select2_filter_host_class = $("#filter_host_class").select2({
        minimumResultsForSearch: Infinity,
    })
    $select2_filter_host_class.on("select2:select", function (e) {
        reload_datatables("select2:select", e);
    });

    $select2_filter_belongs_to_game_project = $("#filter_belongs_to_game_project").select2({
        // minimumResultsForSearch: Infinity,
    })
    $select2_filter_belongs_to_game_project.on("select2:select", function (e) {
        reload_datatables("select2:select", e);
    });

    $select2_filter_belongs_to_room = $("#filter_belongs_to_room").select2({
        // minimumResultsForSearch: Infinity,
    })
    $select2_filter_belongs_to_room.on("select2:select", function (e) {
        reload_datatables("select2:select", e);
    });

    $select2_filter_machine_type = $("#filter_machine_type").select2({
        minimumResultsForSearch: Infinity,
    })
    $select2_filter_machine_type.on("select2:select", function (e) {
        reload_datatables("select2:select", e);
    });

    $select2_filter_belongs_to_business = $("#filter_belongs_to_business").select2({
        // minimumResultsForSearch: Infinity,
    })
    $select2_filter_belongs_to_business.on("select2:select", function (e) {
        reload_datatables("select2:select", e);
    });

    $select2_filter_opsmanager = $("#filter_opsmanager").select2({
        // minimumResultsForSearch: Infinity,
    })
    $select2_filter_opsmanager.on("select2:select", function (e) {
        reload_datatables("select2:select", e);
    });

    $select2_filter_system = $("#filter_system").select2({
        minimumResultsForSearch: Infinity,
    })
    $select2_filter_system.on("select2:select", function (e) {
        reload_datatables("select2:select", e);
    });

    $select2_filter_is_internet = $("#filter_is_internet").select2({
        minimumResultsForSearch: Infinity,
    })
    $select2_filter_is_internet.on("select2:select", function (e) {
        reload_datatables("select2:select", e);
    });

    var $select2_project = $("#filter_project").select2({});
    var $select2_room = $("#filter_room").select2({});
    var $select2_status2 = $("#filter_status2").select2({});
    $select2_project.on("select2:select", function (e) {
        reload_datatables("select2:select", e);
    });
    $select2_room.on("select2:select", function (e) {
        reload_datatables("select2:select", e);
    });
    $select2_status2.on("change", function (e) {
        reload_datatables("select2:select", e);
    });

}

function reload_datatables(name, evt, className) {
    if (name == "select2:select" || name == "select2:select2") {
        table.ajax.reload();
    }
}


function edit(id) {
    editFlag = true;
    var data = {
        'id': id,
    };

    var encoded = $.toJSON(data);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/assets/get_cmdb_host/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function (data) {
            origin_data = data;
            $("#myModalLabel").text("修改设备信息");
            $("#modal-notify").hide();
            $("#id").val(id);
            $("#show_id").hide();

            // Fill data

            $("#status").val(data.status).trigger('change');
            initSelect2('belongs_to_game_project', data.belongs_to_game_project.id, data.belongs_to_game_project.text);
            initSelect2('belongs_to_room', data.belongs_to_room.id, data.belongs_to_room.text);
            $("#machine_type").val(data.machine_type).trigger('change');
            initSelect2('belongs_to_business', data.belongs_to_business.id, data.belongs_to_business.text);
            initSelect2('opsmanager', data.opsmanager.id, data.opsmanager.text);
            $("#host_class").val(data.host_class).trigger('change');
            $("#platform").val(data.platform);
            $("#internal_ip").val(data.internal_ip);
            $("#telecom_ip").val(data.telecom_ip);
            $("#unicom_ip").val(data.unicom_ip);
            $("#system").val(data.system).trigger('change');
            $("#is_internet").val(data.is_internet).trigger('change');
            $("#sshuser").val(data.sshuser);
            $("#sshport").val(data.sshport);
            $("#machine_model").val(data.machine_model);
            $("#cpu_num").val(data.cpu_num);
            $("#cpu").val(data.cpu);
            $("#ram").val(data.ram);
            $("#disk").val(data.disk);
            $("#host_comment").val(data.host_comment);
            $("#belongs_to_host").val(data.belongs_to_host);
            $("#host_identifier").val(data.host_identifier);
            $("#password").val(data.password);
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

function checkBeforeAdd(hostname, belongs_to_device, belongs_to_PlatForm, belongs_to_ostype, host_cpu, host_mem, host_disk, iptypes, host_status) {
    if (hostname == '') {
        $('#lb-msg').text('主机名不能为空!');
        $('#modal-notify').show();
        return false;
    }
    if (!editFlag) {
        if (deviceFlag) {
            if (belongs_to_device == '0') {
                $('#lb-msg').text('请输入物理编号!');
                $('#modal-notify').show();
                return false;
            }
        }
    }

    if (belongs_to_PlatForm == '0') {
        $('#lb-msg').text('所属平台名不能为空!');
        $('#modal-notify').show();
        return false;
    }
    if (iptypes == '0') {
        $('#lb-msg').text('请选择网络区域!');
        $('#modal-notify').show();
        return false;
    }
    if (belongs_to_ostype == '0') {
        $('#lb-msg').text('请选择操作系统模版!');
        $('#modal-notify').show();
        return false;
    }
    if (host_cpu == '') {
        $('#lb-msg').text('请输入cpu型号!');
        $('#modal-notify').show();
        return false;
    }
    if (host_mem == '') {
        $('#lb-msg').text('请输入内存型号!');
        $('#modal-notify').show();
        return false;
    }
    if (host_disk == '') {
        $('#lb-msg').text('请输入硬盘信息!');
        $('#modal-notify').show();
        return false;
    }
    if (host_status == null) {
        $('#lb-msg').text('请选择主机状态!');
        $('#modal-notify').show();
        return false;
    }
    return true;
};

function formatRepo(repo) {

    var markup = '<div class="clearfix"><div clas="col-sm-7">' + repo.text + '</div></div>';

    return markup;
};

function formatRepoSelection(repo) {
    return repo.text || repo.id;
}


// $(document).on('hidden.bs.modal', function (e) {
//     clearModalSelect2();
//     initModalSelect2();
// });


$.urlParam = function (name) {
    var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
    if (results == null) {
        return null;
    }
    else {
        return decodeURIComponent(results[1]) || 0;
    }
};

function pre_filter_host_idenfier() {
    var host_identifier = $.urlParam('host_identifier');
    if (host_identifier != null) {
        table.search(host_identifier).draw()
    }
}


$(document).ready(function () {
    $.fn.select2.defaults.set( "theme", "bootstrap" );

    initFilterTable();

    var rows_selected = [];
    table = $('#mytable').DataTable({
        "processing": true,
        "ordering": false,
        "serverSide": true,
        "ajax": {
            "url": "/assets/data_host/",
            "type": "POST",
            "data": function (d) {
                d.filter_status = $("#filter_status").val();
                d.filter_host_class = $("#filter_host_class").val();
                d.filter_belongs_to_game_project = $("#filter_belongs_to_game_project").val();
                d.filter_belongs_to_room = $("#filter_belongs_to_room").val();
                d.filter_machine_type = $("#filter_machine_type").val();
                d.filter_belongs_to_business = $("#filter_belongs_to_business").val();
                d.filter_platform = $("#filter_platform").val();
                d.filter_internal_ip = $("#filter_internal_ip").val();
                d.filter_telecom_ip = $("#filter_telecom_ip").val();
                d.filter_unicom_ip = $("#filter_unicom_ip").val();
                d.filter_system = $("#filter_system").val();
                d.filter_is_internet = $("#filter_is_internet").val();
                d.filter_sshuser = $("#filter_sshuser").val();
                d.filter_sshport = $("#filter_sshport").val();
                d.filter_machine_model = $("#filter_machine_model").val();
                d.filter_cpu_num = $("#filter_cpu_num").val();
                d.filter_cpu = $("#filter_cpu").val();
                d.filter_ram = $("#filter_ram").val();
                d.filter_disk = $("#filter_disk").val();
                d.filter_belongs_to_host = $("#filter_belongs_to_host").val();
                d.filter_host_identifier = $("#filter_host_identifier").val();
                d.filter_host_comment = $("#filter_host_comment").val();
                d.filter_opsmanager = $("#filter_opsmanager").val();
                d.filter_project = $("#filter_project").val();
                d.filter_room = $("#filter_room").val();
                d.filter_status2 = $("#filter_status2").val();
            }
        },
        "columns": [
            {"data": null},  // 0
            {"data": "id"},  // 1
            {"data": 'status'},  //2
            {"data": 'host_class'},  // 3
            {"data": "belongs_to_game_project"},  // 4
            {"data": "belongs_to_room"},  // 5
            {"data": "machine_type"},  // 6
            {"data": "belongs_to_business"}, // 7
            {"data": "platform"},  // 8
            {"data": "internal_ip"},  // 9
            {"data": "telecom_ip"},  // 10
            {"data": "unicom_ip"},  // 11
            {"data": "system"},  // 12
            {"data": "is_internet"},  // 13
            {"data": "sshuser"},  // 14
            {"data": "sshport"},  // 15
            {"data": "machine_model"},  // 16
            {"data": "cpu_num"},  // 17
            {"data": "cpu"},  // 18
            {"data": "ram"},  // 19
            {"data": "disk"},  // 20
            {"data": "host_comment"},  // 21
            {"data": "belongs_to_host"},  // 22
            {"data": "host_identifier"},  // 23
            {"data": "opsmanager"},  // 24
            {"data": "password"},  // 25
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
                'targets': [3, 6, 12, 13, 14, 15, 16, 17, 18, 19, 20, 22, 23, 24, 25],
                'visible': false,
            },
            {
                targets: 26,
                render: function (a, b, c, d) {
                    var context =
                        {
                            func: [
                                {"name": "修改", "fn": "edit(\'" + c.id + "\')", "type": "primary"},
                                {"name": "变更记录", "fn": "host_history_record(\'" + c.id + "\')", "type": "success"},
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

    pre_filter_host_idenfier();

    url_preFilter();

    // 设置权限
    is_superuser = $("#is_superuser").data('is-superuser');
    if (is_superuser == "False") {
        table.column(25).visible(false);
        table.column(26).visible(false);
        table.column(12).visible(false);
    }


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
                makeTitle(str, count);
            } else {
                $row.removeClass('selected');
                count = 0;
                makeTitle(str, count);
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
            makeTitle(str, ++count);
        } else {
            $row.removeClass('selected');
            makeTitle(str, --count);
        }

        // Prevent click event from propagating to parent
        e.stopPropagation();
    });

    initModalSelect2();


    $('#bt-add').click(function () {
        $("#myModalLabel").text("新增主机信息");
        $("#modal-notify").hide();
        $("#show_id").hide();
        $("#host_class").val('0').trigger('change');
        $("#status").val('0').trigger('change');
        initSelect2('belongs_to_game_project', '0', '选择项目');
        initSelect2('belongs_to_room', '0', '选择机房');
        $("machine_type").val('0').trigger('change');
        initSelect2('belongs_to_business', '0', '选择业务类型');
        $("#platform").val('');
        $("#internal_ip").val('');
        $("#telecom_ip").val('');
        $("#unicom_ip").val('');
        $("#system").val('0').trigger('change');
        $("#is_internet").val('0').trigger('change');
        $("#sshuser").val('');
        $("#sshport").val('');
        $("#machine_model").val('');
        $("#cpu_num").val('');
        $("#cpu").val('');
        $("#ram").val('');
        $("#disk").val('');
        $("#host_comment").val('');
        $("#host_identifier").val('');
        initSelect2('opsmanager', '0', '选择所属运维管理机');
        $("#password").val('');

        editFlag = false;
        $("#myModal").modal("show");
    });
    $('#file-save').click(function () {
        $("#Modal-file").modal("hide");
    });

    $('#bt-upload').click(function () {
        $("#Modal-file").modal("show");
        $("#upload-notify").hide();
    });

    $('#bt-upload-notify').click(function () {
        $("#upload-notify").hide();
    });

    $('#bt-modal-notify').click(function () {
        $("#modal-notify").hide();
    });

    $('#bt-save').click(function () {
        var id = $("#id").val();
        var status = $("#status").select2('data')[0].id;
        var host_class = $("#host_class").select2('data')[0].id;

        var belongs_to_game_project = $("#belongs_to_game_project").select2('data')[0].id;
        if ($('#belongs_to_game_project') == '0') {
            $('#lb-msg').text('请选择项目!');
            $('#modal-notify').show();
            return false;
        }

        var belongs_to_room = $("#belongs_to_room").select2('data')[0].id;
        if ($('#belongs_to_room') == '0') {
            $('#lb-msg').text('请选择机房!');
            $('#modal-notify').show();
            return false;
        }

        var machine_type = $("#machine_type").select2('data')[0].id;


        var belongs_to_business = $("#belongs_to_business").select2('data')[0].id;
        if ($('#belongs_to_business') == '0') {
            $('#lb-msg').text('请选择机房!');
            $('#modal-notify').show();
            return false;
        }

        var opsmanager = $("#opsmanager").select2('data')[0].id;

        var platform = $("#platform").val();
        if (platform == '') {
            $('#lb-msg').text('请输入平台!');
            $('#modal-notify').show();
            return false;
        }

        var internal_ip = $("#internal_ip").val();

        var telecom_ip = $("#telecom_ip").val();

        var unicom_ip = $("#unicom_ip").val();

        var system = $("#system").select2('data')[0].id;

        var is_internet = $("#is_internet").select2('data')[0].id;

        var sshuser = $("#sshuser").val();

        var sshport = $("#sshport").val();

        var machine_model = $("#machine_model").val();
        if (machine_model == '') {
            $('#lb-msg').text('请输入机器型号!');
            $('#modal-notify').show();
            return false;
        }

        var cpu_num = $("#cpu_num").val();
        if (cpu_num == '') {
            $('#lb-msg').text('请输入cpu核心数!');
            $('#modal-notify').show();
            return false;
        }

        var cpu = $("#cpu").val();
        if (cpu == '') {
            $('#lb-msg').text('请输入cpu!');
            $('#modal-notify').show();
            return false;
        }
        var ram = $("#ram").val();
        if (ram == '') {
            $('#lb-msg').text('请输入ram!');
            $('#modal-notify').show();
            return false;
        }
        var disk = $("#disk").val();
        if (disk == '') {
            $('#lb-msg').text('请输入disk!');
            $('#modal-notify').show();
            return false;
        }

        var host_comment = $("#host_comment").val();
        if (host_comment == '') {
            $('#lb-msg').text('请输入用途!');
            $('#modal-notify').show();
            return false;
        }

        var belongs_to_host = $("#belongs_to_host").val();

        var host_identifier = $("#host_identifier").val();
        if (host_identifier == '') {
            $('#lb-msg').text('请输入标识符!');
            $('#modal-notify').show();
            return false;
        }
        var password = $("#password").val();

        var urls = "/assets/add_or_edit_host/";

        var inputIds = {
            'id': id,
            'status': status,
            'host_class': host_class,
            'belongs_to_game_project': belongs_to_game_project,
            'belongs_to_room': belongs_to_room,
            'machine_type': machine_type,
            'belongs_to_business': belongs_to_business,
            'platform': platform,
            'internal_ip': internal_ip,
            'telecom_ip': telecom_ip,
            'unicom_ip': unicom_ip,
            'system': system,
            'is_internet': is_internet,
            'sshuser': sshuser,
            'sshport': sshport,
            'machine_model': machine_model,
            'cpu_num': cpu_num,
            'cpu': cpu,
            'ram': ram,
            'disk': disk,
            'host_comment': host_comment,
            'belongs_to_host': belongs_to_host,
            'host_identifier': host_identifier,
            'opsmanager': opsmanager,
            'password': password,
            'editFlag': editFlag,
        };

        var encoded = $.toJSON(inputIds);
        var pdata = encoded;
        $.ajax({
            type: "POST",
            url: urls,
            contentType: "application/json; charset=utf-8",
            data: pdata,
            success: function (data) {

                if (data['data']) {
                    table.ajax.reload(null, false);
                    // table.ajax.reload();
                    $("#myModal").modal("hide");
                } else {
                    $('#lb-msg').text(data['msg']);
                    $('#modal-notify').show();
                }
            }
        });
    });


    $("#bt-del").confirm({
        //text:"确定删除所选的主机?",
        confirm: function (button) {
            var selected = getSelectedTable();

            if (selected.length == 0) {
                alert('请选择');
            } else {
                var encoded = $.toJSON(selected);
                var pdata = encoded;
                $.ajax({
                    type: "POST",
                    url: "/assets/del_data_cmdb_host/",
                    contentType: "application/json; charset=utf-8",
                    data: pdata,
                    success: function (data) {

                        if (data['data']) {
                            table.ajax.reload();
                            makeTitle(str, 0);
                            count = 0;
                        } else {
                            alert(data['msg'])
                            table.ajax.reload();
                            makeTitle(str, 0);
                            count = 0;
                        }
                        ;
                    }
                });
            }
        },

        cancel: function (button) {

        },
        confirmButton: "确定",
        cancelButton: "取消",

    });

    $('#bt-search').click(function () {
        $('#div-search').toggleClass('hide');
    });

    $('input.column_filter').on('keyup click', function () {
        // filterColumn( $(this).parents('tr').attr('data-column') );
        table.ajax.reload();
    });

    $("#bt-reset").click(function () {
        $(".column_filter").val('');
        $(".filter_select2").val('全部').trigger('change');
        table.ajax.reload();
    })

    $("#bt-download").click(function () {
        var filter_status = $("#filter_status").val();
        var filter_host_class = $("#filter_host_class").val();
        var filter_belongs_to_game_project = $("#filter_belongs_to_game_project").val();
        var filter_belongs_to_room = $("#filter_belongs_to_room").val();
        var filter_machine_type = $("#filter_machine_type").val();
        var filter_belongs_to_business = $("#filter_belongs_to_business").val();
        var filter_platform = $("#filter_platform").val();
        var filter_internal_ip = $("#filter_internal_ip").val();
        var filter_telecom_ip = $("#filter_telecom_ip").val();
        var filter_unicom_ip = $("#filter_unicom_ip").val();
        var filter_system = $("#filter_system").val();
        var filter_is_internet = $("#filter_is_internet").val();
        var filter_sshuser = $("#filter_sshuser").val();
        var filter_sshport = $("#filter_sshport").val();
        var filter_machine_model = $("#filter_machine_model").val();
        var filter_cpu_num = $("#filter_cpu_num").val();
        var filter_cpu = $("#filter_cpu").val();
        var filter_ram = $("#filter_ram").val();
        var filter_disk = $("#filter_disk").val();
        var filter_belongs_to_host = $("#filter_belongs_to_host").val();
        var filter_host_identifier = $("#filter_host_identifier").val();
        var filter_host_comment = $("#filter_host_comment").val();
        var filter_opsmanager = $("#filter_opsmanager").val();
        var filter_status2 = $("#filter_status2").val();

        var inputIds = {
            'filter_status': filter_status,
            'filter_host_class': filter_host_class,
            'filter_belongs_to_game_project': filter_belongs_to_game_project,
            'filter_belongs_to_room': filter_belongs_to_room,
            'filter_machine_type': filter_machine_type,
            'filter_belongs_to_business': filter_belongs_to_business,
            'filter_platform': filter_platform,
            'filter_internal_ip': filter_internal_ip,
            'filter_telecom_ip': filter_telecom_ip,
            'filter_unicom_ip': filter_unicom_ip,
            'filter_system': filter_system,
            'filter_is_internet': filter_is_internet,
            'filter_sshuser': filter_sshuser,
            'filter_sshport': filter_sshport,
            'filter_machine_model': filter_machine_model,
            'filter_cpu_num': filter_cpu_num,
            'filter_cpu': filter_cpu,
            'filter_ram': filter_ram,
            'filter_disk': filter_disk,
            'filter_belongs_to_host': filter_belongs_to_host,
            'filter_host_identifier': filter_host_identifier,
            'filter_host_comment': filter_host_comment,
            'filter_opsmanager': filter_opsmanager,
            'filter_status2': filter_status2,
        };

        var encoded = $.toJSON(inputIds);
        var pdata = encoded;

        $.ajax({
            type: "POST",
            url: "/assets/host_download/",
            contentType: "application/json; charset=utf-8",
            data: pdata,
            beforeSend: function () {
                $("#myModal-download").modal("show");
                $("modal-download-footer").hide();
                $("#show-msg").hide();
                $("#load").show();
            },
            success: function (data) {
                if (data.success) {
                    $("#load").hide();
                    $("#modal-download-footer").show();
                    $("#load-msg").text(data.data);
                    $("#show-msg").show();
                    $("#myModal-download").modal("hide");
                    var file_name = data.data;
                    var download_url = '/host_download/' + file_name;
                    window.location = download_url;
                } else {
                    $("#load").hide();
                    $("#modal-download-footer").show();
                    $("#load-msg").text(data.data);
                    $("#show-msg").show();
                }
            },
            error: function () {
                $("#load").hide();
                $("#modal-download-footer").show();
                $("#load-msg").text('下载失败');
                $("#show-msg").show();
            }
        });
    })


});


function host_history_record(id) {
    editFlag = true;
    var data = {
        'host_id': id,
    };

    var encoded = $.toJSON(data);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/assets/get_host_history_record/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function (data) {
            origin_data = data.data;
            let record = '';
            $("#myModalLabelHistory").text("查看主机变更记录");
            for (let i = 0; i < origin_data.length; i++) {
                let log = origin_data[i];
                if (log['type'] == '新增') {
                    let create_time = '<p class="text-danger"><strong>' + log['create_time'] + '</strong></p>';
                    let operation_user = '<span>' + '<span class="text-info">操作人：</span>' + log['operation_user'] + '</span>&nbsp;&nbsp;&nbsp;&nbsp;';
                    let type = '<span class="text-success">' + log['type'] + '</span><br/>';
                    let source_ip = '<span>' + '<span class="text-info">源IP：</span>' + log['source_ip'] + '</span><br/><br/>';
                    record = record + create_time + operation_user + type + source_ip;
                }
                if (log['type'] == '修改') {
                    let create_time = '<p class="text-danger"><strong>' + log['create_time'] + '</strong></p>';
                    let operation_user = '<span>' + '<span class="text-info">操作人：</span>' + log['operation_user'] + '</span><br/>';
                    let alter_detail = log['alter_detail'];
                    let detail = '<span class="text-info">操作明细：</span></br>';
                    for (let i = 0; i < alter_detail.length; i++) {
                        let r = alter_detail[i];
                        detail = detail + '<span>' + r + '</span><br/>'
                    }
                    let source_ip = '<span>' + '<span class="text-info">源IP：</span>' + log['source_ip'] + '</span><br/><br/>';
                    record = record + create_time + operation_user + detail + source_ip;
                }
            }

            $("#myModalHistoryContent").html(record);
            $("#myModalHistory").modal("show");
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

// 后退不刷新页面
function back() {
    history.go(-1);
}