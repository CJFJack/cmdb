// 修改之前的数据
var origin_data;

var table;
var tpl = $("#tpl").html();
//预编译模板
var template = Handlebars.compile(tpl);


function initModalSelect2() {
    var select2type = $('#filter_type').select2();
    var select2createuser = $('#filter_create_user').select2();
    select2type.on("select2:select", function (e) {
        table.ajax.reload();
    });
    select2createuser.on("select2:select", function (e) {
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
            "url": "/mysql/data_mysql_history/",
            "type": "POST",
            "data": function (d) {
                d.filter_type = $('#filter_type').select2('data')[0].id;
                d.filter_create_user = $('#filter_create_user').select2('data')[0].id;
                d.filter_instance = $('#filter_instance').val();
                d.filter_source_ip = $('#filter_source_ip').val();
            }
        },
        "columns": [
            {"data": "id"},  // 0
            {"data": 'project'},  //1
            {"data": 'cmdb_area'},  //2
            {"data": 'instance'},  //3
            {"data": 'create_time'},  //4
            {"data": 'create_user'},  //5
            {"data": 'type'},  // 6
            {"data": "alter_field"},  // 7
            {"data": "old_content"},  // 8
            {"data": "new_content"},  // 9
            {"data": "remark"},  // 10
            {"data": "source_ip"},  // 11
        ],
        "order": [[1, 'asc']],
        columnDefs: [
            {
                'targets': 0,
                'visible': false,
                'searchable': false
            },
            {
                'targets': 6,
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
        $('#filter_create_user').val('0').trigger('change');
        table.ajax.reload();
    })

});
