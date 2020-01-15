var table;
var editFlag;
var tpl = $("#tpl").html();
//预编译模板
var template = Handlebars.compile(tpl);

// 修改之前的数据
var origin_data;

var str = "确定删除选中的机房?";
var count = 0;


function edit(id) {
    editFlag = true;
    var data = {
        'id': id,
    };
    var encoded = $.toJSON(data);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/assets/get_cmdb_room/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function (data) {
            origin_data = data;
            $("#myModalLabel").text("修改机房信息");
            $("#modal-notify").hide();
            $("#id").val(data.id);
            $("#show_id").hide();
            //console.log(roomid);
            $("#room_name").val(data.room_name);
            $("#room_name_en").val(data.room_name_en);
            initSelect2('area', data.area_id, data.area_text);
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

    // 初始化地区选择
    $select2Area = $("#area").select2({
        ajax: {
            url: '/assets/list_area/',
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
    });
}


$(document).ready(function () {

    initModalSelect2();

    var rows_selected = [];
    table = $('#mytable').DataTable({
        "processing": true,
        // "serverSide": true,
        "ordering": false,
        "ajax": "/assets/data_room",
        "columns": [
            {"data": null},
            {"data": "id"},
            {"data": "area"},
            {"data": "room_name"},
            {
                "data": null,
                "orderable": false,
            }
        ],
        "order": [[3, 'asc']],
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
                targets: 4,
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
                    url: "/assets/del_data_cmdb_room/",
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
        $("#myModalLabel").text("新增机房信息");
        $("#modal-notify").hide();
        $("#show_id").hide();
        $("#id").val('');
        initSelect2('area', '', '');
        $("#room_name").val('');
        $("#room_name_en").val('');
        editFlag = false;
        $("#myModal").modal("show");
    });

    $('#bt-save').click(function () {

        var id = $("#id").val();
        var room_name = $('#room_name').val();
        var room_name_en = $('#room_name_en').val();
        var area = $('#area').val();

        if (room_name == '') {
            $('#lb-msg').text('请输入机房名!');
            $('#modal-notify').show();
            return false;
        }
        if (room_name_en == '') {
            $('#lb-msg').text('请输入机房名缩写!');
            $('#modal-notify').show();
            return false;
        }
        if (area == '') {
            $('#lb-msg').text('请选择所属地区!');
            $('#modal-notify').show();
            return false;
        }

        var inputIds = {
            "id": id,
            "room_name": room_name,
            "room_name_en": room_name_en,
            "area": area,
            "editFlag": editFlag,
        };

        var encoded = $.toJSON(inputIds)
        var pdata = encoded

        var urls = '/assets/add_or_edit_room/'

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
