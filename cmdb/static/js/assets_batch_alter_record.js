var table;
var table_detail;
var tpl = $("#tpl").html();
//预编译模板
var template = Handlebars.compile(tpl);

$(document).ready(function () {

    table = $('#mytable').DataTable({
        "processing": true,
        "ordering": false,
        "serverSide": true,
        "ajax": {
            "url": "/it_assets/data_assets_batch_alter_record/",
            "type": "POST",
            "data": function (d) {
                d.filter_alter_user = $("#filter_alter_user").select2('data')[0].text;
                d.filter_alter_type = $("#filter_alter_type").select2('data')[0].id;
            }
        },
        "columns": [
            {"data": "id"}, //0
            {"data": "alter_time"},  // 1
            {"data": "alter_user"},  // 2
            {"data": "alter_type"},  // 3
            {
                "data": null,        // 4
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
                targets: 4,
                render: function (a, b, c, d) {
                    var context =
                        {
                            func: [
                                {"name": "查看结果", "fn": "detail(\'" + c.id + "\')", "type": "success"},
                                {"name": "导出明细", "fn": "download(\'" + c.id + "\')", "type": "info"},
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


    $('#bt-search').click(function () {
        $('#div-search').toggleClass('hide');
    });

    $(".filter_select2").select2({}).on("select2:select", function (e) {
        table.ajax.reload(null, false);
    });

    $("#bt-reset").click(function () {
        // 重置高级搜索
        $(".filter_select2").val('0').trigger('change');
        table.ajax.reload();

    });

});


// 查看详情
function detail(id) {
    table_detail = $('#mytable_detail').DataTable({
        "processing": true,
        "ordering": false,
        "serverSide": true,
        "destroy": true,
        "ajax": {
            "url": "/it_assets/data_assets_batch_alter_record_detail/",
            "type": "POST",
            "data": function (d) {
                d.record_id = id
            }
        },
        "columns": [
            {"data": "assets_number"},  // 0
            {"data": "old_value"},  // 1
            {"data": "new_value"},  // 2
            {"data": "result"},  // 3
            {"data": "remark"},  // 4
        ],
        columnDefs: [
            {
                'targets': 3,
                render: function (a, b, c, d) {
                    if (c.result == '修改成功') {
                        return '<label class="label label-success">' + c.result + '</label>'
                    }
                    else if (c.result == '修改失败') {
                        return '<label class="label label-danger">' + c.result + '</label>'
                    }
                    else {
                        return '<label class="label label-default">' + c.result + '</label>'
                    }
                }
            },
        ],
        "language": {
            "url": "/static/js/i18n/Chinese.json"
        },
    });
    $('#myModal').modal('show')
}


function download(id) {
    var inputIds = {
        'id': id,
    };

    var encoded = $.toJSON(inputIds);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/it_assets/create_bthalt_assets_excel_data/",
        contentType: "application/json; charset=utf-8",
        data: pdata,
        beforeSend: function () {
            jQuery('#loading').showLoading();
        },
        success: function (data) {
            jQuery('#loading').hideLoading();
            if (data.success) {
                var file_name = data.data;
                var download_url = '/it_assets/bthalt_assets_result_downloads/' + file_name;
                window.location = download_url;
            }
            else {
                alert(data.msg)
            }
        },
        error: function () {
            jQuery('#loading').hideLoading();
        }
    });
}
