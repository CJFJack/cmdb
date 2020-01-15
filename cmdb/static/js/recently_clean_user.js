$(document).ready(function () {

    $('#query').click(function () {
        var inputIds = {
            "start": $('#start').val(),
            "end": $('#end').val(),
        };
        var urls = "/users/recently_clean_user/";
        var encoded = $.toJSON(inputIds);
        var pdata = encoded;
        $.ajax({
            type: "POST",
            url: urls,
            contentType: "application/json; charset=utf-8",
            data: pdata,
            beforeSend: function() {
              $('#query').text('查询中，请稍等...')
                $('#query').prop('disabled', true)
            },
            success: function (data) {
                if (data['data']) {
                    $('#results').html(data.msg)
                } else {
                    alert(data['msg'])
                }
                $('#query').text('查询');
                $('#query').prop('disabled', false)
            }
        });
    })

});
