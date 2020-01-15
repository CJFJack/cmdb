var wse;
var project_id;
var area_id;
project_id = $('#project_id').val();
area_id = $('#area_id').val();


$.urlParam = function (name) {
    var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
    if (results == null) {
        return null;
    }
    else {
        return decodeURIComponent(results[1]) || 0;
    }
};


function get_workflow_state_approve_process() {
    var inputs = {
        'wse': wse,
    };

    var encoded = $.toJSON(inputs);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/myworkflows/workflow_state_approve_process/",
        async: true,
        contentType: "application/json; charset=utf-8",
        data: pdata,
        success: function (data) {
            // console.log(data.data, data.current_index);
            $(".ystep1").loadStep({
                size: "large",
                color: "green",
                steps: data.data,
            });

            $(".ystep1").setStep(data.current_index + 1);
        }
    });
}


function get_cdn_version_type() {
    var client_type_cdn_root_dir_version = new Array();
    $(".update_content").each(function (i, e) {
        var item_info = {};
        var client_type = $($(e).children('div').get(0)).find('.client_type');
        var cdn_root_url = $($(e).children('div').get(1)).find('.cdn_root_url');
        var cdn_dir = $($(e).children('div').get(2)).find('.cdn_dir');
        var update_version = $($(e).children('div').get(3)).find('input');

        item_info.client_type = client_type.val();
        item_info.cdn_root_url = cdn_root_url.val();
        item_info.cdn_dir = cdn_dir.val();
        item_info.version = $.trim(update_version.val());

        client_type_cdn_root_dir_version.push(item_info)
    });

    return client_type_cdn_root_dir_version
}


function get_version_compare_platform_type() {
    var version_compare_platform_type = new Array();
    $(".update_content").each( function(i, e) {
        console.log($(e))
        var item_info = {};
        var input_version = $($(e).children().get(0)).find('.input_version');
        var input_compare = $($(e).children().get(1)).find('.input_compare');
        var input_platform = $($(e).children().get(2)).find('.input_platform');
        var input_type = $($(e).children().get(3)).find('.input_type');

        item_info.input_version = $.trim(input_version.val());
        item_info.input_compare = $.trim(input_compare.val());
        item_info.input_platform = input_platform.val();
        item_info.input_type = input_type.val();

        version_compare_platform_type.push(item_info)
    });

    return version_compare_platform_type
}


function show_div_server_content() {
    let server_range = $('#server_range').select2('data')[0].id;
    let server_range_text = $('#server_range').select2('data')[0].text;
    if (server_range.length === 0 || server_range === 'all') {
        $('#div_server_content').addClass('hidden');
    }
    else {
        $('#div_server_content').find('label').text(server_range_text + 'ID');
        $('#div_server_content').removeClass('hidden');
    }
    if (server_range.length === 0 || server_range === 'include') {
        $('#div_on_new_server').addClass('hidden');
    }
    else {
        $('#div_on_new_server').removeClass('hidden');
    }
}


function initSelect2Range() {
    var $select2Range = $('#server_range').select2();
    // 初始化区服范围的值
    show_div_server_content();
    // 监听区服范围下拉框变化
    $select2Range.on("select2:select", function (e) {
        show_div_server_content();
    });
}


$(document).ready(function () {

    $.fn.select2.defaults.set("theme", "bootstrap");
    initSelect2Range();

    wse = $("#wse_id").text();

    get_workflow_state_approve_process();

    // get_workflow_state();

    // 提交
    $("#bt-commit").confirm({
        text: "确定提交?",
        confirm: function (button) {

            var transition = $('input[name=transitions]:checked').attr('id');
            var opinion = $("#opinion").val();
            var transition_condition = $('input[name=transitions]:checked').attr('condition');

            if (!transition) {
                alert('请选择审批意见!');
                return false;
            }

            var server_range = $('#server_range').select2('data')[0].id;
            var server_content = $('#server_content').val();
            var on_new_server = $('#on_new_server').prop('checked');
            if (!server_range) {
                alert('请选择更新区服范围!');
                return false;
            }

            if (typeof($("#server_version").attr('readonly')) == 'undefined' && transition_condition == '同意') {
                // 如果没有readonly，说明需要填写版本号
                if ($("#server_version").val() == '') {
                    alert('请填写版本号!');
                    return false;
                }
                if ($("#server_attention").val() == '') {
                    alert('请填写后端注意事项!');
                    return false;
                }
                // let result = check_push_dir('server', $("#server_version").val());
                // if (!result.success) {
                //     alert(result.msg);
                //     return false
                // }
            }

            var ask_reset = $('#ask_reset').prop('checked');
            var server_erlang = $('#server_erlang').val();
            if (ask_reset) {
                if (!server_erlang) {
                    alert('请填写erlang命令!');
                    return false;
                }
            }


            if ($("#client_version").length > 0 && typeof($("#client_version").attr('readonly')) == 'undefined') {
                // 如果没有readonly，说明需要填写版本号
                if ($("#client_version").val() == '') {
                    alert('请填写版本号!');
                    return false;
                }

                if ($("#client_attention").val() == '') {
                    alert('请填写前端注意事项!');
                    return false;
                }
            }


            var version_compare_platform_type = get_version_compare_platform_type();

            if ($("#bt-add").length > 0 && transition_condition == '同意') {
                // 如果没有disabled，说明需要填写前端版本号
                if (!checkUpdateContent()) {
                    return false;
                }
            }

            console.log($("#client_attention").val())
            console.log($('#edit_client').val())
            console.log($("#bt-add").length)
            if ($('#edit_client').val() === 'True') {
                if (!checkUpdateContent()) {
                    return false;
                }
                if ($("#client_attention").val() === '') {
                    alert('请填写前端注意事项!');
                    return false;
                }
            }

            var inputs = {
                'wse': wse,
                'transition': transition,
                'opinion': opinion,
                'server_version': $("#server_version").val(),
                'server_attention': $("#server_attention").val(),
                'client_version': $("#client_version").val(),
                'client_attention': $("#client_attention").val(),
                'client_content': version_compare_platform_type,
                'ask_reset': ask_reset,
                'server_range': server_range,
                'server_content': server_content,
                'on_new_server': on_new_server,
                'server_erlang': server_erlang,
            };
            // console.log(inputs);

            var encoded = $.toJSON(inputs);
            var pdata = encoded;
            $.ajax({
                type: "POST",
                url: "/myworkflows/workflow_approve/",
                async: true,
                contentType: "application/json; charset=utf-8",
                data: pdata,
                success: function (data) {
                    if (data.success) {
                        var redirect_url = '/myworkflows/approve_list/';
                        window.location.href = redirect_url;
                    } else {
                        alert(data.data);
                        return false;
                    }
                }
            });
        },

        cancel: function (button) {

        },
        confirmButton: "确定",
        cancelButton: "取消",

    });

    $("#bt-load").click(function () {
        var inputs = {
            'wse': wse,
        };

        var encoded = $.toJSON(inputs);
        var pdata = encoded;

        $.ajax({
            type: "POST",
            url: "/myworkflows/test_load/",
            contentType: "application/json; charset=utf-8",
            async: true,
            data: pdata,
            beforeSend: function () {
                $("#myModal").modal("show");
                $("#modal-footer").hide();
                $("#show-msg").hide();
                $("#load").show();
            },
            success: function (data) {
                $("#load").hide();
                $("#modal-footer").show();
                $("#load-msg").text(data.data);
                $("#show-msg").show();

            },
            error: function () {
                $("#load").hide();
                $("#modal-footer").show();
                $("#load-msg").text(data.data);
                $("#show-msg").show();
            }
        });
    });

    $("#bt-transfer").confirm({
        text: "确定转交另外的人员处理?",
        confirm: function (button) {

            var to_anthoer_admin = $("#to_anthoer_admin").select2('data')[0].id;

            if (to_anthoer_admin == '0') {
                alert('请选择转交网管人员!');
                return false;
            }

            var inputs = {
                'wse': wse,
                'to_anthoer_admin': to_anthoer_admin,
            };

            var encoded = $.toJSON(inputs);
            var pdata = encoded;
            $.ajax({
                type: "POST",
                url: "/myworkflows/transfer_to_other_admin/",
                async: true,
                contentType: "application/json; charset=utf-8",
                data: pdata,
                success: function (data) {
                    if (data.success) {
                        var redirect_url = '/myworkflows/approve_list/';
                        window.location.href = redirect_url;
                    } else {
                        alert(data.data);
                        return false;
                    }
                }
            });
        },

        cancel: function (button) {

        },
        confirmButton: "确定",
        cancelButton: "取消",

    });


    // 初始化区服列表
    $("#server_list_v2").treeMultiselect(
        {
            searchable: true, searchParams: ['section', 'text'],
            freeze: false, hideSidePanel: true, startCollapsed: true
        }
    );


    // 添加前端更新条目
    $("#bt-add").click(function (event) {
        var add_str = '<div class="col-sm-12 form-group update_content">' +
            '<div class="col-sm-2">' +
            '<div class="input-group">' +
            '<span class="input-group-addon">版本</span>' +
            '<input type="text" class="form-control input_version" placeholder="242093020F">' +
            '</div>' +
            '</div>' +
            '<div class="col-sm-2">' +
            '<div class="input-group">' +
            '<span class="input-group-addon">对比</span>' +
            '<input type="text" class="form-control input_compare" placeholder="没有可以不填">' +
            '</div>' +
            '</div>' +
            '<div class="col-sm-2">' +
            '<div class="input-group">' +
            '<span class="input-group-addon">平台</span>' +
            '<select class="input_platform" style="width: 100%">' +
            '<option value="0" selected="selected">选择平台</option>' +
            '</select>' +
            '</div>' +
            '</div>' +
            '<div class="col-sm-2">' +
            '<div class="input-group">' +
            '<span class="input-group-addon">类型</span>' +
            '<select class="input_type" style="width: 100%">' +
            '<option value="0" selected="selected">选择类型</option>' +
            '</select>' +
            '</div>' +
            '</div>' +
            '<div class="alert alert-danger col-sm-2 show_update_content_msg" style="display: none;">' +
            '请填写更新内容!' +
            '</div>' +
            '<div class="col-sm-1">' +
            '<button class="btn btn-danger btn-sm myRemove" type="button">x</button>' +
            '</div>' +
            '</div>'
        $("#create_update_version").after(add_str);

        var input_version = $($("#create_update_version").next().children().get(0)).find('.input_version')
        var input_compare = $($("#create_update_version").next().children().get(1)).find('.input_compare')
        var selector_input_platform = $($("#create_update_version").next().children().get(2)).find('.input_platform')
        var selector_input_type = $($("#create_update_version").next().children().get(3)).find('.input_type')

        var myRemove_bt = $($("#create_update_version").next().children().get(5))


        initPlatForm(selector_input_platform);
        initType(selector_input_type);
        addMyRemove()
    });


    // 监听是否执行跨服重排
    check_is_ask_reset();


});


// 给客户端类型添加select2
function initPlatForm(selector) {
    var $select2PlatForm = selector.select2({
        ajax: {
            url: '/myworkflows/get_csxy_game_server_platform/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page,
                    project: $('#project_id').val(),
                    area_name: $("#area").val(),
                };
            },

            processResults: function (data, params) {
                // parse the results into the format expected by Select2
                // since we are using custom formatting functions we do not need to
                // alter the remote JSON data, except to indicate that infinite
                // scrolling can be used
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
        // minimumResultsForSearch: Infinity,
        escapeMarkup: function (markup) {
            return markup;
        }, // let our custom formatter work
    })
}


// cdn根路径添加select2
function initType(selector) {
    var $select2Type = selector.select2({
        ajax: {
            url: '/myworkflows/get_hotupdate_client_type/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page,
                    area_name: $("#area").val(),
                    project: $('#project_id').val(),
                };
            },

            processResults: function (data, params) {
                // parse the results into the format expected by Select2
                // since we are using custom formatting functions we do not need to
                // alter the remote JSON data, except to indicate that infinite
                // scrolling can be used
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
        // minimumResultsForSearch: Infinity,
        escapeMarkup: function (markup) {
            return markup;
        }, // let our custom formatter work
    })
}


// 监听是否执行跨服重排
function check_is_ask_reset() {
    if ($('#ask_reset').prop('checked')) {
        $('#div_server_erlang').removeClass('hidden')
    }
    else {
        $('#div_server_erlang').addClass('hidden')
    }
    $("#ask_reset").change(function () {
        // console.log($('#ask_reset').prop('checked'))
        if ($('#ask_reset').prop('checked')) {
            $('#div_server_erlang').removeClass('hidden')
        }
        else {
            $('#div_server_erlang').addClass('hidden')
        }
    });
}


// 给客户端类型添加select2
function initClientType(selector) {
    var $select2ClienType = selector.select2({
        ajax: {
            url: '/myworkflows/get_hotupdate_client_type/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page,
                    project: project_id,
                    area_name: $("#area").val(),
                };
            },

            processResults: function (data, params) {
                // parse the results into the format expected by Select2
                // since we are using custom formatting functions we do not need to
                // alter the remote JSON data, except to indicate that infinite
                // scrolling can be used
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
        minimumResultsForSearch: Infinity,
        escapeMarkup: function (markup) {
            return markup;
        }, // let our custom formatter work
    });

    $select2ClienType.on("select2:select", function (e) {
        reset_cdn("select2:select", e, $(this));
    });

}


// cdn根路径添加select2
function initCDNRootUlr(selector) {
    var $select2CDNRootUll = selector.select2({
        ajax: {
            url: '/myworkflows/get_cdn_root_url/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page,
                    project: project_id,
                    area_name: $("#area").val(),
                    client_type: $(".client_type").select2('data')[0].id,
                };
            },

            processResults: function (data, params) {
                // parse the results into the format expected by Select2
                // since we are using custom formatting functions we do not need to
                // alter the remote JSON data, except to indicate that infinite
                // scrolling can be used
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
        minimumResultsForSearch: Infinity,
        escapeMarkup: function (markup) {
            return markup;
        }, // let our custom formatter work
    });

    $select2CDNRootUll.on("select2:select", function (e) {
        reset_cdn("select2:select", e, $(this));
    });
}

// cdn目录添加select2
function initCDNDir(selector) {
    selector.select2({
        ajax: {
            url: '/myworkflows/get_cdn_dir/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page,
                    project: project_id,
                    client_type: $(selector).parent().prev().prev().find('.client_type').val(),
                    cdn_root_url: $(selector).parent().prev().find('.cdn_root_url').val(),
                    area_name: $("#area").val(),
                };
            },

            processResults: function (data, params) {
                // parse the results into the format expected by Select2
                // since we are using custom formatting functions we do not need to
                // alter the remote JSON data, except to indicate that infinite
                // scrolling can be used
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
        minimumResultsForSearch: Infinity,
        escapeMarkup: function (markup) {
            return markup;
        }, // let our custom formatter work
    })
}


// 重置cdn的select2
function reset_cdn(name, evt, el) {
    if (name == "select2:select" || name == "select2:select2") {
        if ($(el).hasClass('client_type')) {
            var cdn_root_url = $(el).parent().next().find('.cdn_root_url');
            $(cdn_root_url).html('')
            $(cdn_root_url).append('<option value="0">选择cdn根路径</option>');
            $(cdn_root_url).select2('val', 0, true);

            var cdn_dir = $(el).parent().next().next().find('.cdn_dir');
            $(cdn_dir).html('')
            $(cdn_dir).append('<option value="0">选择cdn目录</option>');
            $(cdn_dir).select2('val', 0, true)
        } else if ($(el).hasClass('cdn_root_url')) {
            var cdn_dir = $(el).parent().next().find('.cdn_dir');
            $(cdn_dir).html('')
            $(cdn_dir).append('<option value="0">选择cdn目录</option>');
            $(cdn_dir).select2('val', 0, true)
        }
    }
}


// 监听删除按钮
function addMyRemove() {
    $(".myRemove").click(function (event) {
        /* Act on the event */
        $($(this)).parent().parent().remove()
    });
}


// 检查是否添加更新条目
function checkUpdateContent() {
    var result = true
    if ( $(".update_content").length == 0 ) {
        alert('请添加更新条目')
        result = false
    } else {
        $(".update_content").each( function(i, e) {
            var input_version = $($(e).children().get(0)).find('.input_version')
            var show_update_content_msg = $($(e).children().get(4))
            var input_compare = $($(e).children().get(1)).find('.input_compare')
            var input_platform = $($(e).children().get(2)).find('.input_platform')
            var input_type = $($(e).children().get(3)).find('.input_type')
            if ( input_version.val() == '' ) {
                show_update_content_msg.html('请填写版本')
                show_update_content_msg.show()
                result = false
                return false
            } else {
                show_update_content_msg.hide()
            }
            if ( input_platform.val() == '0' ) {
                show_update_content_msg.html('请选择平台')
                show_update_content_msg.show()
                result = false
                return false
            } else {
                show_update_content_msg.hide()
            }
            if ( input_type.val() == '0' ) {
                show_update_content_msg.html('请选择类型')
                show_update_content_msg.show()
                result = false
                return false
            } else {
                show_update_content_msg.hide()
            }
        } )
    }
    return result
}


function check_push_dir(version_update_type, version) {
    var inputs = {
        'version_update_type': version_update_type,
        'version': version,
        'project_id': project_id,
        'area_id': area_id,
    };

    var encoded = $.toJSON(inputs);
    var pdata = encoded;
    var success = true;
    var msg;

    $.ajax({
        type: "POST",
        url: "/myworkflows/version_update_check_push_dir/",
        async: false,
        contentType: "application/json; charset=utf-8",
        data: pdata,
        beforeSend: function () {
            jQuery('#loading').showLoading();
        },
        success: function (data) {
            jQuery('#loading').hideLoading();
            if (!data.success) {
                msg = data.msg;
                success = false
            }
        },
        error: function () {
            jQuery('#loading').hideLoading();
            msg = '内部错误！';
            success = false
        }
    });

    return {'success': success, 'msg': msg}
}
