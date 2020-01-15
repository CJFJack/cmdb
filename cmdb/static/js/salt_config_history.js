$(document).ready(function () {

    $('#mytable').DataTable({
        responsive: true,
        language: {
            "url": "/static/js/i18n/Chinese.json"
        },
        ordering: false
    });

});

function view_detail(history_id) {
    $.ajax({
        type: "POST",
        url: "/assets/history_detail/"+history_id+"/",
        data: '',
        contentType: "application/json; charset=utf-8",
        success: function (data) {
            var org_data = data.data;
            //alert
            $('#history_id').attr("value", org_data['history_id']);
            $('#task_name').attr("value", org_data['task_name']);
            $('#filename').attr("value", org_data['filename']);
            $('#content').attr("value", org_data['content']);
            $('#task_name').text(org_data['task_name']);
            $('#filename').text(org_data['filename']);
            $('#content').val(org_data['content']);
            $('#remark').val(org_data['remark']);
        },
        error: function (xhr, status, error) {
            if (xhr.status == '403') {
                alert('权限拒绝');
            } else {
                alert('内部错误');
            }
        }
    });
    $('#Modal-edit').modal("show");
}

