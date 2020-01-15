var table;
var str = "确定删除选中的web接口?";
var count = 0;
var EditFlag;
var tpl = $("#tpl").html();
//预编译模板
var template = Handlebars.compile(tpl);

$(document).ready(function () {
    $.fn.select2.defaults.set("theme", "bootstrap");

    var rows_selected = [];
    table = $('#mytable').DataTable({
        "processing": true,
        "ordering": false,
        "paging": true,
        "ajax": {
            "url": "/webapi/data_web_get_cdn_list_api/",
            "type": "POST",
        },
        columns: [
            {"data": null},
            {"data": "id"},
            {"data": "project"},
            {"data": "area"},
            {"data": "web_url"},
            {"data": "root"},
            {"data": "dev_flag"},
            {"data": "version"},
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
                targets: 8,
                render: function (a, b, c, d) {
                    var context =
                        {
                            func: [
                                {"name": "修改", "fn": "edit_api(\'" + c.id + "\')", "type": "primary"},
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
                alert('请先勾选需要删除的接口');
            } else {
                var encoded = $.toJSON(selected);
                var pdata = encoded;
                $.ajax({
                    type: "POST",
                    url: "/webapi/delete_get_cdn_list_api/",
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

    // 保存api配置信息
    $('#bt-save').click(function () {
        var api_id = $('#id_api_id').val();
        var project_id = $('#id_project').select2('data')[0].id;
        var area_id = $('#id_area').select2('data')[0].id;
        var web_url = $('#id_api_url').val();
        var root = $('#id_root').val();
        var dev_flag = $('#id_dev_flag').val();
        var version = $('input[name=version]:checked').val();
        if (!project_id) {
            $('#lb-msg').text('请选择项目');
            $('#modal-notify').show();
            return false;
        }
        if (!area_id) {
            $('#lb-msg').text('请选择地区');
            $('#modal-notify').show();
            return false;
        }
        if (/\/$/.test(web_url)) {
            $('#lb-msg').text('api地址不要以 / 结尾');
            $('#modal-notify').show();
            return false;
        }
        if (!version) {
            $('#lb-msg').text('请选择接口版本');
            $('#modal-notify').show();
            return false;
        }
        var inputIds = {
            'api_id': api_id,
            'project_id': project_id,
            'area_id': area_id,
            'web_url': web_url,
            'root': root,
            'dev_flag': dev_flag,
            'EditFlag': EditFlag,
            'version': version,
        };
        var urls = '/webapi/add_or_edit_get_cdn_list_api/';
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
    $('#myModalLabel').text('新增api信息');
    initSelect2('id_project', '', '');
    initSelect2('id_area', '', '');
    $('#id_root').val('');
    $('#id_api_url').val('');
    $('#id_dev_flag').val('');
    $('.radio-info').prop('checked', false);
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

    // 初始化项目列表
    $select2Area = $("#id_area").select2({
        ajax: {
            url: '/assets/list_area/',
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
        placeholder: '请选择地区',
    });
}

function edit_api(id) {
    EditFlag = true;
    inputs = {
        'id': id,
    };
    var encoded = $.toJSON(inputs);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/webapi/get_get_cdn_list_api/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function (data) {
            if (data.success) {
                data = data.data;
                initSelect2('id_project', data.project_id, data.project);
                initSelect2('id_area', data.area_id, data.area);
                $('#id_api_url').val(data.web_url);
                $('#id_root').val(data.root);
                $('#id_dev_flag').val(data.dev_flag);
                $('#id_api_id').val(data.id);
                $('#modal-notify').hide();
                $('#id_version_' + data.version_id).prop('checked', true);
                $('#Modal').modal('show')
            }
            else {
                alert(data.msg)
            }
        },
    });

}