var table;
var str = "确定删除选中的CDN接口?";
var count = 0;

$(document).ready(function () {

    var rows_selected = [];
    table = $('#mytable').DataTable({
        columns: [
            {},
            {"data": "id"},
            {"data": "chinese_name"},
            {"data": "short_name"},
            {},
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
        //text:"确定删除所选的地区信息?",
        confirm: function (button) {
            var selected = getSelectedTable();

            if (selected.length == 0) {
                alert('请先勾选需要删除的地区');
            } else {
                var encoded = $.toJSON(selected);
                var pdata = encoded;
                $.ajax({
                    type: "POST",
                    url: "/assets/delete_area/",
                    contentType: "application/json; charset=utf-8",
                    data: pdata,
                    success: function (data) {

                        if (data['data']) {
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

});


// 新增cdn接口信息modal框
function add_area() {
    $('#chinese_name').val('');
    $('#short_name').val('');
    $('#modal-notify-add-area').hide();
    $('#Modal-Add').modal('show')
}

// 修改cdn接口信息modal框
function edit_area(id) {
    var inputs = {
        'id': id,
    };
    $('#edit_area_id').attr('value', id);
    var encoded = $.toJSON(inputs);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/assets/get_area_detail/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function (data) {
            $('#modal-notify-edit-area').hide();
            $('#edit_chinese_name').val(data.chinese_name)
            $('#edit_short_name').val(data.short_name)
        },
        error: function (xhr, status, error) {
            if (xhr.status == '403') {
                alert('权限拒绝');
            } else {
                alert('内部错误');
            }
        }
    });
    $('#modal-notify-edit-api').hide();
    $('#Modal-edit').modal('show')
}

// 保存新增接口信息
function save_add_area() {
    var chinese_name = $("#chinese_name").val();
    var short_name = $("#short_name").val();
    if (chinese_name == '') {
        $('#lb-msg-add-area').text('请选填写地区中文名!');
        $('#modal-notify-area').show();
        return false;
    }
    inputs = {
        'chinese_name': chinese_name,
        'short_name': short_name,
    };

    var encoded = $.toJSON(inputs);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/assets/add_area/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function (data) {
            if (data['success']) {
                location.reload();
            }
            else {
                alert(data['msg'])
            }
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

// 保存修改接口信息
function save_edit_area() {
    var chinese_name = $('#edit_chinese_name').val();
    var short_name = $("#edit_short_name").val();
    var area_id = $('#edit_area_id').val();
    var inputs = {
        'area_id': area_id,
        'chinese_name': chinese_name,
        'short_name': short_name,
    };
    var encoded = $.toJSON(inputs);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/assets/edit_area/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function (data) {
            if (data['success']) {
                location.reload();
            }
            else {
                alert(data['msg'])
            }
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