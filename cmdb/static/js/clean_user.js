var socket;
var $select2_server_project;
var $select2_svn_project;

function getChecked() {
    var listChecked = new Array();
    $('input[type=checkbox]:checked').map(function () {
        listChecked.push($(this).attr('id'));
    });
    return listChecked;
}

$.urlParam = function (name) {
    var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
    if (results == null) {
        return null;
    }
    else {
        return decodeURIComponent(results[1]) || 0;
    }
};

function init_ws() {
    var id = $.urlParam('id');
    var protocol = window.location.protocol;
    if (protocol == 'http:') {
        wsp = 'ws:'
    } else {
        wsp = 'wss:'
    }
    socket = new ReconnectingWebSocket(wsp + "//" + window.location.host + "/ws/clean_user/" + id, null, {debug: true});

    socket.onmessage = function (e) {
        var data = $.parseJSON(e.data);
        /*
            data的数据格式:
            {
                "message": "update_msg",
                "user_id": 1,
                process_info": process_info
            }
        */
        if (data.message == "update_msg") {
            $("#results").html(data.process_info)
        }
    };

    socket.onopen = function () {
        socket.send("start ws connection");
    };

    if (socket.readyState == WebSocket.OPEN) socket.onopen();

}


function initModalSelect2() {

    $select2_server_project = $('#select_server_project').select2({
        ajax: {
            url: '/assets/list_game_project/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
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
        //minimumResultsForSearch: Infinity,
        escapeMarkup: function (markup) {
            return markup;
        }, // let our custom formatter work
    });


    $select2_svn_project = $('#select_svn_project').select2({
        ajax: {
            url: '/assets/list_game_project/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
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
                    // pagination: {
                    //     more: (params.page * 30) < data.total_count
                    // };
                }
            },
            cache: false,
        },
        //minimumResultsForSearch: Infinity,
        escapeMarkup: function (markup) {
            return markup;
        }, // let our custom formatter work
    });
}


$(document).ready(function () {

    init_ws();
    initModalSelect2();

    // $('input[type=checkbox]').map(function () {
    //     $(this).prop('checked', false);
    // });

    $("#clean_mysql").click(function (event) {
        /* Act on the event */
        if ($(this).is(':checked')) {
            $("#clean_mysql_force").attr('disabled', true)
            $("#clean_mysql_force").attr('checked', false)
        } else {
            $("#clean_mysql_force").attr('disabled', false)
        }

    });

    $("#clean_user").click(function (event) {
        /* Act on the event */
        var listChecked = getChecked();
        var server_projects = $('#select_server_project').val();
        var server_clean_type = $('input[name=server_project]:checked').val();
        var svn_projects = $('#select_svn_project').val();
        var svn_clean_type = $('input[name=svn_project]:checked').val();
        var data = {
            "listChecked": listChecked,
            "id": $.urlParam('id'),
            "server_projects": server_projects,
            "server_clean_type": server_clean_type,
            "svn_projects": svn_projects,
            "svn_clean_type": svn_clean_type,
        };
        var encoded = $.toJSON(data);
        var pdata = encoded;

        $("#clean_user").text("清除...");
        $("#clean_user").removeClass('btn-danger').addClass('btn-secondary');
        $("#clean_user").prop('disabled', true);

        $("#results").val('');

        $.ajax({
            type: "POST",
            url: "/users/do_clean/",
            data: pdata,
            contentType: "application/json; charset=utf-8",
            success: function (data) {
                if (data.success) {
                    // alert('清除成功');
                    return false;
                }
            },
        });
    });

    $('#check_all').click(function () {
        $(":checkbox").prop("checked", true)
    });


    $("input[name=server_project]").on('change', function () {
        if ($(this).val() === 'section') {
            $('#div_server_project').removeClass('hidden')
        }
        else {
            $('#div_server_project').addClass('hidden')
        }
    });

    $('#clean_server').on('change', function () {
        if ($(this).prop('checked')) {
            $('#server_clean_type').removeClass('hidden')
        }
        else {
            $('#server_clean_type').addClass('hidden');
            $('#div_server_project').addClass('hidden');
            $('#input_server_project[value=all]').prop('checked', true);
        }
    });

    $("input[name=svn_project]").on('change', function () {
        if ($(this).val() === 'section') {
            $('#div_svn_project').removeClass('hidden')
        }
        else {
            $('#div_svn_project').addClass('hidden')
        }
    });

    $('#clean_svn').on('change', function () {
        if ($(this).prop('checked')) {
            $('#svn_clean_type').removeClass('hidden')
        }
        else {
            $('#svn_clean_type').addClass('hidden');
            $('#div_svn_project').addClass('hidden');
            $('#input_svn_project[value=all]').prop('checked', true);
        }
    });

    $('#server_clean_all_select').click(function () {
        var selectedItems = [];
        var allOptions = $("#select_server_project option");
        allOptions.each(function () {
            selectedItems.push($(this).val());
        });
        $("#select_server_project").select2("val", selectedItems);
    });

    $('#server_clean_inverse_select').click(function () {
        var selectedItems = [];
        var allOptions = $("#select_server_project option");
        allOptions.each(function () {
            selectedItems.push($(this).val());
        });
        var currentItems = $('#select_server_project').val();
        if (currentItems === null) {
            currentItems = []
        }
        for (let i of currentItems) {
            if ($.inArray(i, selectedItems) >= 0) {
                selectedItems.splice($.inArray(i, selectedItems), 1);
            }
        }
        $("#select_server_project").select2("val", selectedItems);
    });

    $('#svn_clean_all_select').click(function () {
        var selectedItems = [];
        var allOptions = $("#select_svn_project option");
        allOptions.each(function () {
            selectedItems.push($(this).val());
        });
        $("#select_svn_project").select2("val", selectedItems);
    });

    $('#svn_clean_inverse_select').click(function () {
        var selectedItems = [];
        var allOptions = $("#select_svn_project option");
        allOptions.each(function () {
            selectedItems.push($(this).val());
        });
        var currentItems = $('#select_svn_project').val();
        if (currentItems === null) {
            currentItems = []
        }
        for (let i of currentItems) {
            if ($.inArray(i, selectedItems) >= 0) {
                selectedItems.splice($.inArray(i, selectedItems), 1);
            }
        }
        $("#select_svn_project").select2("val", selectedItems);
    });

});
