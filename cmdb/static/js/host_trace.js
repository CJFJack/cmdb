// 修改之前的数据
var origin_data;

var table;
var tpl = $("#tpl").html();
//预编译模板
var template = Handlebars.compile(tpl);


function initModalSelect2() {
    var select2type = $('#filter_type').select2();
    var select2operationuser = $('#filter_operation_user').select2();
    select2type.on("select2:select", function (e) {
        table.ajax.reload();
    });
    select2operationuser.on("select2:select", function (e) {
        table.ajax.reload();
    });
}




$(document).ready(function () {

    $.fn.select2.defaults.set("theme", "bootstrap");

    table = $('#mytable').DataTable({
        "processing": true,
        "ordering": false,
        "serverSide": true,
        "searching":false,
        "ajax": {
            "url": "/assets/data_host_trace/",
            "type": "POST",
            "data": function (d) {
                d.filter_type = $('#filter_type').select2('data')[0].id;
                d.filter_operation_user = $('#filter_operation_user').select2('data')[0].id;
                d.filter_host_ip = $('#filter_host_ip').val();
                d.filter_source_ip = $('#filter_source_ip').val();
            }
        },
        "columns": [
            {"data": "id"},  // 0
            {"data": 'project'},  //1
            {"data": 'room'},  //2
            {"data": 'business'},  //3
            {"data": 'telecom_ip'},  //4
            {"data": 'create_time'},  //5
            {"data": 'operation_user'},  //6
            {"data": 'type'},  // 7
            {"data": "alter_field"},  // 8
            {"data": "old_content"},  // 9
            {"data": "new_content"},  // 10
            {"data": "remark"},  // 11
            {"data": "source_ip"},  // 12
        ],
        "order": [[1, 'asc']],
        columnDefs: [
            {
                'targets': 0,
                'visible': false,
                'searchable': false
            },
            {
                'targets': 7,
                render: function (data) {
                    if (data == '新增') {
                        return '<label class="label label-success">' + data + '</label>'
                    }
                    else if (data == '修改') {
                        return '<label class="label label-info">' + data + '</label>'
                    }
                    else if (data == '删除') {
                        return '<label class="label label-danger">' + data + '</label>'
                    }
                    else {
                        return '<label class="label label-default">' + data + '</label>'
                    }
                }
            }
        ],
        "language": {
            "url": "/static/js/i18n/Chinese.json"
        },
    });


    initModalSelect2();

    $('input.column_filter').on('keyup click', function () {
        // filterColumn( $(this).parents('tr').attr('data-column') );
        table.ajax.reload();
    });

    $('#bt-reset').click(function () {
        $('input.column_filter').val('');
        $('#filter_type').val('0').trigger('change');
        $('#filter_operation_user').val('0').trigger('change');
        table.ajax.reload();
    })

});
