var table;

function initModalSelect2() {
    // 初始化项目列表
    $select2Project = $("#project").select2({
        ajax: {
            url: '/assets/list_cdn_game_project_by_group/',
            dataType: 'json',
            type: 'POST',
            delay: 30,
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
        // minimumResultsForSearch: Infinity,
        placeholder: '请选择游戏项目',
    });
}


function manual_refresh(record_id) {
    jQuery('#loading').showLoading();
    var inputs = {
        'record_id': record_id,
    };
    var encoded = $.toJSON(inputs);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/assets/manual_query_cdn/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function (data) {
            setTimeout(function () {
                location.reload();
            }, 800);
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

// 查看刷新详情
function view_refresh_detail(record_id) {
    $('#Modal-detail').modal("show");
    var inputs = {
        'record_id': record_id,
    };
    var encoded = $.toJSON(inputs);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/assets/view_fresh_detail/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function (data) {
            var refresh_obj = data.data;
            $('#refresh_obj_detail').val(refresh_obj);
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

$(document).ready(function () {
    $.fn.select2.defaults.set( "theme", "bootstrap" );

    initModalSelect2();

    table = $('#mytable').DataTable({
        responsive: true,
        language: {
            "url": "/static/js/i18n/Chinese.json"
        },
        ordering: false,
        bFilter: false,
        pageLength: 5,
    });

    // 按url提交
    $('#commit_url').click(function () {
        var refresh_obj = $('#cdn_url').val().split("\n");
        var raw_refresh_obj = $('#cdn_url').val();
        var refresh_type = 'url';
        var game_project = $('#project').select2('data')[0].id;

        if (game_project == 0) {
            alert("请选择游戏项目！");
            return
        }
        if (refresh_obj == '') {
            alert("请填写url");
            return
        }

        var inputs = {
            'refresh_obj': refresh_obj,
            'refresh_type': refresh_type,
            'game_project': game_project,
            'raw_refresh_obj': raw_refresh_obj,
        };
        var encoded = $.toJSON(inputs);
        var pdata = encoded;
        jQuery('#loading').showLoading();

        $.ajax({
            type: "POST",
            url: "/assets/cdn_refresh/",
            data: pdata,
            contentType: "application/json; charset=utf-8",
            success: function (data) {
                if (data.success == true) {
                    location.reload();
                }
                else {
                    $('#refresh_notice_text').text(data.msg);
                    $('#refresh_notice').css('display', 'block');
                    jQuery('#loading').hideLoading();
                }
            },
            error: function (xhr, status, error) {
                jQuery('#loading').hideLoading();
                if (xhr.status == '403') {
                    alert('权限拒绝');
                } else {
                    alert('内部错误');
                }
            }
        });
    });

    // 按dir提交
    $('#commit_dir').click(function () {
        var refresh_obj = $('#cdn_dir').val().split("\n");
        var raw_refresh_obj = $('#cdn_dir').val();
        var refresh_type = 'dir';
        var game_project = $('#project').select2('data')[0].id;

        if (game_project == 0) {
            alert("请选择游戏项目！");
            return
        }
        if (refresh_obj == '') {
            alert("请填写目录");
            return
        }

        var inputs = {
            'refresh_obj': refresh_obj,
            'refresh_type': refresh_type,
            'game_project': game_project,
            'raw_refresh_obj': raw_refresh_obj,
        };
        var encoded = $.toJSON(inputs);
        var pdata = encoded;
        jQuery('#loading').showLoading();

        $.ajax({
            type: "POST",
            url: "/assets/cdn_refresh/",
            data: pdata,
            contentType: "application/json; charset=utf-8",
            success: function (data) {
                if (data.success == true) {
                    location.reload();
                }
                else {
                    $('#refresh_notice_text').text(data.msg);
                    $('#refresh_notice').css('display', 'block');
                    jQuery('#loading').hideLoading();
                }
            },
            error: function (xhr, status, error) {
                jQuery('#loading').hideLoading();
                if (xhr.status == '403') {
                    alert('权限拒绝');
                } else {
                    alert('内部错误');
                }
            }
        });
    });

});