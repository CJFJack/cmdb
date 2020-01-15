var table;
var str = "确定删除选中的web接口?";
var count = 0;
var EditFlag;
var tpl = $("#tpl").html();
//预编译模板
var template = Handlebars.compile(tpl);

$(document).ready(function () {
    $.fn.select2.defaults.set( "theme", "bootstrap" );

    var rows_selected = [];
    table = $('#mytable').DataTable({
        "processing": true,
        "ordering": false,
        // "serverSide": true,
        "paging": true,
        "ajax": {
            "url": "/myworkflows/data_project_celery_queue_map/",
            "type": "POST",
        },
        columns: [
            {'data': null},
            {"data": "id"},
            {"data": "project_name"},
            {"data": "project_name_en"},
            {"data": "worker"},
            {"data": "celery_queue"},
            {"data": "use"},
            {"data": null},
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
                'searchable': false
            },
            {
                targets: 7,
                render: function (a, b, c, d) {
                    var context =
                        {
                            func: [
                                {"name": "修改", "fn": "edit_map(\'" + c.id + "\')", "type": "primary"},
                            ]
                        };
                    var html = template(context);
                    return html;
                }
            }
        ],
        responsive: true,
        language: {
            "url": "/static/js/i18n/Chinese.json"
        },
        ordering: false
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

    // 全选table checkbox
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
        //text:"确定删除所选的cdn接口?",
        confirm: function (button) {
            var selected = getSelectedTable();

            if (selected.length == 0) {
                alert('请先勾选需要删除的celery队列');
            } else {
                var encoded = $.toJSON(selected);
                var pdata = encoded;
                $.ajax({
                    type: "POST",
                    url: "/myworkflows/delete_get_cdn_list_api/",
                    contentType: "application/json; charset=utf-8",
                    data: pdata,
                    success: function (data) {

                        if (data['success']) {
                            location.reload();
                        } else {
                            alert(data['msg']);
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

    // 初始化select2下拉框
    initModalSelect2();

    // 保存配置信息
    $('#bt-save').click(function () {
        var map_id = $('#id_map_id').val();
        var celery_queue = $('#id_celery_queue').select2('data')[0].id;
        var project_id = $('#id_project').select2('data')[0].id;
        var worker_id = $('#id_worker').select2('data')[0].id;
        var use = $("input[name='use']:checked").val();
        if (!project_id) {
            $('#lb-msg').text('请选择项目');
            $('#modal-notify').show();
            return false;
        }
        if (!worker_id) {
            $('#lb-msg').text('请选择worker');
            $('#modal-notify').show();
            return false;
        }
        if (!celery_queue) {
            $('#lb-msg').text('请填写celery队列名');
            $('#modal-notify').show();
            return false;
        }
        if (use == null) {
            $('#lb-msg').text('请选择用途');
            $('#modal-notify').show();
            return false;
        }
        var inputIds = {
            'map_id': map_id,
            'celery_queue': celery_queue,
            'project_id': project_id,
            'worker_id': worker_id,
            'use': use,
            'EditFlag': EditFlag,
        };
        var urls = '/myworkflows/add_or_edit_project_celery_queue_map/';
        var encoded = $.toJSON(inputIds);
        var pdata = encoded;
        $.ajax({
            type: "POST",
            url: urls,
            contentType: "application/json; charset=utf-8",
            data: pdata,
            success: function (data) {
                if (data.success) {
                    table.ajax.reload(null, false);
                    $("#Modal").modal("hide");
                } else {
                    $('#lb-msg').text(data['msg']);
                    $('#modal-notify').show();
                }
            }
        });
    })

});


//新增api信息
function bt_add() {
    EditFlag = false;
    $('#modal-notify').hide();
    $('#myModalLabel').text('新增celery队列信息');
    initSelect2('id_project', '', '');
    initSelect2('id_worker', '', '');
    initSelect2('id_celery_queue', '', '');
    $('.form-check-input').removeAttr("checked");
    $('#Modal').modal('show');
}


function initModalSelect2() {
    // 初始化项目列表
    $select2Project = $("#id_project").select2({
        ajax: {
            url: '/assets/list_game_project/',
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
        placeholder: '请选择项目',
    });

    // 初始化worker列表
    $select2Worker = $("#id_worker").select2({
        ajax: {
            url: '/myworkflows/list_celery_worker/',
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
        placeholder: '请选择项目',
    });


    // 初始化celery队列列表
    $select2Queue = $("#id_celery_queue").select2({
        ajax: {
            url: '/myworkflows/list_celery_queue/',
            dataType: 'json',
            type: 'POST',
            delay: 30,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page,
                    worker: $('#id_worker').select2('data')[0].id
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
        placeholder: '请选择项目',
    });

}

function edit_map(id) {
    EditFlag = true;
    inputs = {
        'id': id,
    };
    var encoded = $.toJSON(inputs);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/myworkflows/get_project_celery_queue_map/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function (data) {
            if (data.success) {
                data = data.data;
                initSelect2('id_project', data.project_id, data.project);
                initSelect2('id_worker', data.worker_id, data.worker);
                initSelect2('id_celery_queue', data.celery_queue, data.celery_queue);
                var use_id = data.use_id;
                if (use_id == 1) {
                    $("input:radio[value=1]").prop('checked', true);
                }
                if (use_id == 2) {
                    $("input:radio[value=2]").prop('checked', true);
                }
                $('#id_map_id').val(id);
                $('#modal-notify').hide();
                $('#Modal').modal('show')
            }
            else {
                alert(data.msg)
            }
        },
    });

}