$(document).ready(function () {
    var project_id = $('#project').val();

    init_select_template();

    $('input[name=client_hotupdate_template]').click(function () {
        $('.panel').removeClass('panel-primary').addClass('panel-default');
        let div = $(this).parents('div.panel-default');
        div.removeClass('panel-default').addClass('panel-primary');
    });

    $('input[name=server_hotupdate_template]').click(function () {
        $('.panel').removeClass('panel-primary').addClass('panel-default');
        let div = $(this).parents('div.panel-default');
        div.removeClass('panel-default').addClass('panel-primary');
    });

    $('#bt-save').click(function () {
        var data = {
            'project_id': project_id,
            'client_template_id': $('input[name="client_hotupdate_template"]:checked').val(),
            'server_template_id': $('input[name="server_hotupdate_template"]:checked').val(),
        };
        var encoded = $.toJSON(data);
        var pdata = encoded;
        $.ajax({
            type: "POST",
            url: "/myworkflows/save_project_relate_hotupdate_template/",
            data: pdata,
            async: true,
            contentType: "application/json; charset=utf-8",
            success: function (data) {
                $('#purchase_button').hide();
                if (data.success) {
                    window.location.href = "/assets/game_project_list/"
                }
                else {
                    alert(data.data)
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
    })

});


function init_select_template() {
    let project_client_template_id = $('#project_client_template_id').val();
    let project_server_template_id = $('#project_server_template_id').val();

    let client_input = $('input[value=\"' + project_client_template_id + '\"]:radio');
    console.log(client_input.attr('value'));
    client_input.prop('checked', true);
    let client_div = client_input.parents('div.panel-default');
    client_div.removeClass('panel-default').addClass('panel-primary');

    let server_input = $('input[value=\"' + project_server_template_id + '\"]:radio');
    server_input.prop('checked', true);
    let server_div = server_input.parents('div.panel-default');
    server_div.removeClass('panel-default').addClass('panel-primary');
}
