var table;

function initModalSelect2() {

    $select2Project = $("#id_project").select2({
        ajax: {
            url: '/myworkflows/list_game_project/',
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
        placeholder: '游戏项目',
    });

    $select2Room = $("#id_room").select2({
        ajax: {
            url: '/myworkflows/list_room_name_by_project_from_host/',
            dataType: 'json',
            type: 'POST',
            delay: 30,
            data: function (params) {
                var project = $("#id_project").val();
                if (project == null) {
                    alert('请先选择游戏项目')
                }
                else {
                    return {
                        q: params.term,
                        page: params.page,
                        project: $("#id_project").select2('data')[0].id,
                    };
                }
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
        placeholder: '机房',
    });
}

// 根据项目和机房展示主机使用率
function search() {

    var id_project = $("#id_project").val();
    var id_room = $("#id_room").val();

    if (id_project == null) {
        alert('请先选择游戏项目!');
        return false
    }
    if (id_room == null) {
        alert('请先选择机房!');
        return false
    }

    table = $('#mytable').DataTable({
        "processing": true,
        "ordering": true,
        "bDestroy": true,
        "ajax": {
            "url": "/assets/data_host_usage/",
            "type": "POST",
            "data": function (d) {
                d.id_project = id_project;
                d.id_room = id_room;
            }
        },
        "columns": [
            {"data": "id"},  // 0
            {"data": "project"}, //1
            {"data": 'room'},  //2
            {"data": 'business'},  //3
            {"data": 'extranet_ip'},  // 4
            {"data": 'cpu_num'},  // 5
            {"data": 'ram'},  // 6
            {"data": 'disk'},  // 7
            {"data": "game_server"},  // 8
            {"data": "game_server_count"},  // 9
            {"data": "usage"},  // 10
        ],
        "order": [[10, 'asc']],
        columnDefs: [
            {
                'targets': [0],
                'visible': false,
                'searchable': false
            },
            {
                'targets': [8],
                "render": function (data, type, row) {
                    return data.split(",").join("<br/>");
                },
            },
            {
                'targets': [10],
                "render": function (data, type, row) {
                    if (data == 0) {
                        return '<span class="text-success"><strong>' + data + '%' + '</strong></span>';
                    }
                    else if (data == 100) {
                        return '<span class="text-danger"><strong>' + data + '%' + '</strong></span>';
                    }
                    else {
                        return data + '%';
                    }

                },
            },
        ],
        "language": {
            "url": "/static/js/i18n/Chinese.json"
        },
    });
}

//导出主机使用率
function download() {
    var id_project = $("#id_project").val();
    var id_room = $("#id_room").val();

    if (id_project == null) {
        alert('请先选择游戏项目!');
        return false
    }
    if (id_room == null) {
        alert('请先选择机房!');
        return false
    }

    var inputIds = {
        'id_project': id_project,
        'id_room': id_room,
    };

    var encoded = $.toJSON(inputIds);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/assets/host_usage_downloads/",
        contentType: "application/json; charset=utf-8",
        data: pdata,
        beforeSend: function () {
            jQuery('#loading').showLoading();
        },
        success: function (data) {
            jQuery('#loading').hideLoading();
            if (data.success) {
                var file_name = data.data;
                var download_url = '/assets/hostusagedownloads/' + file_name;
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


$(document).ready(function () {

    initModalSelect2();

    $("#id_project").change(function () {
        initSelect2('id_room', null, null);
    });

    $('#business').on('keyup change', function () {
        table
            .columns(3)
            .search($('#business').val())
            .draw();
    });

    $('#cpu').on('keyup change', function () {
        table
            .columns(5)
            .search($('#cpu').val())
            .draw();
    });

    $('#ram').on('keyup change', function () {
        table
            .columns(6)
            .search($('#ram').val())
            .draw();
    });

});
