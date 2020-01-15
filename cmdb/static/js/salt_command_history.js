var tpl = $("#tpl").html();
var template = Handlebars.compile(tpl);


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
        url: "/assets/salt_command_history_result/" + history_id + "/",
        data: '',
        contentType: "application/json; charset=utf-8",
        success: function (data) {
            var org_data = data.data;
            $('#execute_result').html(org_data['text']);
        },
        error: function (xhr, status, error) {
            if (xhr.status == '403') {
                alert('权限拒绝');
            } else {
                alert('内部错误');
            }
        }
    });
    $('#Modal-execute').modal("show");
}


