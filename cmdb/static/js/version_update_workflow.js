var workflow;
var $select2project;
var $select2server_charge;
var $select2client_charge;
var $select2plan_charge;
var $select2test_charge;

// 需要的区服列表
var update_server_list = new Array();


function initDateTime() {
    var dt = new Date();
    var current_month = dt.getMonth() + 1
    var from = dt.getFullYear() + '-' + current_month + '-' + dt.getDate();
    var next_month = dt.getMonth() + 2
    var to = dt.getFullYear() + '-' + next_month + '-' + dt.getDate();
    $(".flatpickr").flatpickr({
        enableTime: true,
        time_24hr: true,
        locale: "zh",
        /*disable: [
            function(date) {
                var dt = new Date();
                return (date < new Date(dt.getFullYear(), dt.getMonth(), dt.getDate()));
            }
        ],*/
        enable: [
            {
                from: from,
                to: to,
            },
        ],
    });
}

function initModalSelect2() {
    $select2project = $('#project').select2({
        ajax: {
            url: '/myworkflows/list_game_project/',
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
        // minimumInputLength: 1,
        // templateResult: formatRepo, // omitted for brevity, see the source of this page
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });

    // $select2project.on("select2:select", function (e){ show_game_server("select2:select", e); });

    $select2server_charge = $("#server_charge").select2({
        ajax: {
            url: '/myworkflows/list_project_group_user/',
            dataType: 'json',
            type: 'POST',
            delay: 0,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page,
                    project: $("#project").select2('data')[0].id,
                    project_group: '服务端技术组',
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
        //minimumResultsForSearch: Infinity,
        // escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
        // minimumInputLength: 1,
        // templateResult: formatRepo, // omitted for brevity, see the source of this page
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });

    $select2client_charge = $("#client_charge").select2({
        ajax: {
            url: '/myworkflows/list_project_group_user/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page,
                    project: $("#project").select2('data')[0].id,
                    project_group: '客户端技术组',
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
        //minimumResultsForSearch: Infinity,
        // escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
        // minimumInputLength: 1,
        // templateResult: formatRepo, // omitted for brevity, see the source of this page
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });

    $select2plan_charge = $("#plan_charge").select2({
        ajax: {
            url: '/myworkflows/list_project_group_user/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page,
                    project: $("#project").select2('data')[0].id,
                    project_group: '策划组',
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
        //minimumResultsForSearch: Infinity,
        // escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
        // minimumInputLength: 1,
        // templateResult: formatRepo, // omitted for brevity, see the source of this page
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });

    $select2test_charge = $("#test_charge").select2({
        ajax: {
            url: '/myworkflows/list_project_group_user/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page,
                    project: $("#project").select2('data')[0].id,
                    project_group: '测试组',
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
        //minimumResultsForSearch: Infinity,
        // escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
        // minimumInputLength: 1,
        // templateResult: formatRepo, // omitted for brevity, see the source of this page
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });
}


// 选择了项目以后展示区服列表
function show_game_server(name, evt, className) {
    if (name == "select2:select" || name == "select2:select2") {

        // 项目改变以后各个审批人都需要变
        $("#server_charge").val('0').trigger('change');
        $("#client_charge").val('0').trigger('change');
        $("#plan_charge").val('0').trigger('change');
        $("#test_charge").val('0').trigger('change');

        // 重新加载区服列表
        $("#clean_server").remove();
        var project = $("#project").select2('data')[0].id;
        var inputIds = {
            'project': project,
        };

        var encoded = $.toJSON(inputIds);
        var pdata = encoded;

        $.ajax({
            type: "POST",
            url: "/myworkflows/get_project_server_tree/",
            contentType: "application/json; charset=utf-8",
            data: pdata,
            success: function (data) {
                if (data.success) {
                    var server_list_str = `
                                    <div class="form-group" id="clean_server">
                                      <label class="col-sm-12">区服列表</label>
                                      <div class="col-sm-6">
                                        <select id="server_list" multiple="multiple">
                                        </select>
                                      </div>
                                    </div>
                                `

                    $("#add_server_list_after").after(server_list_str);
                    data.all_server_list.forEach(function (e, index) {
                        var game_type = e.game_type;
                        var server_list = e.server_list;
                        $.each(server_list, function (key, value) {
                            var pf_name = key;
                            var pf_server_list = server_list[key];

                            pf_server_list.forEach(function (el, index2) {
                                var srv_name = el.srv_name;
                                var ip = el.ip;
                                var srv_id = el.srv_id;

                                var section = game_type + '/' + pf_name;

                                var option = "<option" + " " +
                                    "vlaue=" + srv_id + " " +
                                    "data-section=" + section + " " +
                                    "data-srv=" + srv_id + " " +
                                    "data-ip=" + ip + " " +
                                    "data-gtype=" + game_type + " " +
                                    "data-platform=" + pf_name + " " +
                                    ">" + srv_name +
                                    "</option>";

                                $("#server_list").append(option);

                            });

                        });

                    });

                    // 初始化区服列表
                    $("#server_list").treeMultiselect(
                        {
                            searchable: true, searchParams: ['section', 'text'],
                            freeze: false, hideSidePanel: true, startCollapsed: true
                        }
                    );

                } else {
                    alert('获取区服列表失败');
                    return false;
                }


            },
            error: function () {
                /* Act on the event */
                alert('获取区服列表失败');
                return false;
            },
        });
    }
}

// 获取选择的区服列表
function get_server_list() {
    // 返回 json list的格式
    var data = new Array();
    $($('.option:checkbox:checked')).each(function (i, e) {
        var server_info = {}
        var parent_element = $(e).parent()
        server_info.srv_id = parent_element.attr('data-srv');
        server_info.srv_name = parent_element.attr('data-value');
        server_info.ip = parent_element.attr('data-ip');
        server_info.gtype = parent_element.attr('data-gtype');
        server_info.pf_name = parent_element.attr('data-platform');
        data.push(server_info);
    });

    update_server_list = data;

}


function checkBefore(applicant, title, content) {

    if (applicant == '0') {
        alert('请选择申请人');
        return false;
    }

    if (title == '') {
        alert('请输入标题');
        return false;
    }

    if (content == '') {
        alert('请输入内容');
        return false;
    }

    return true;

}


$(document).ready(function () {

    workflow = $("#workflow_id").text();
    initDateTime();
    initModalSelect2();

    // 提交
    $("#bt-commit").confirm({
        text: "确定提交到下一步?",
        confirm: function (button) {

            get_server_list();

            var title = $("#title").val();
            if (title == '') {
                alert('请填写title');
                return false;
            }
            ;

            var content = $("#content").val();
            if (content == '') {
                alert('请更新内容');
                return false;
            }
            ;

            var project = $("#project").val();
            if (project == '0') {
                alert('请选择项目');
                return false;
            }
            ;

            var server_list = $("#server_list").val();
            if (server_list == '') {
                alert('请填写区服列表');
                return false;
            }
            ;

            var start_time = $("#start_time").val();
            if (start_time == '') {
                alert('请选择开始时间');
                return false;
            }
            ;
            var end_time = $("#end_time").val();
            if (end_time == '') {
                alert('请选择结束时间');
                return false;
            }
            ;

            var server_charge = $("#server_charge").select2('data')[0].id;
            var client_charge = $("#client_charge").select2('data')[0].id;
            var plan_charge = $("#plan_charge").select2('data')[0].id;
            var test_charge = $("#test_charge").select2('data')[0].id;

            if (server_charge == '0' || client_charge == '0' || plan_charge == '0' || 'test_charge' == '0') {
                alert('请选择相应的审批人');
                return false;
            }
            ;

            var new_edition = $('#new_edition').val();

            // var result = checkBefore(applicant, title, content);
            var result = true;

            var inputs = {
                'title': title,
                'content': content,
                'project': project,
                'server_list': server_list,
                'start_time': start_time,
                'end_time': end_time,
                'server_charge': server_charge,
                'client_charge': client_charge,
                'plan_charge': plan_charge,
                'test_charge': test_charge,
                'workflow': workflow,
                'new_edition': new_edition,
            };

            var encoded = $.toJSON(inputs);
            var pdata = encoded;

            if (result) {
                $.ajax({
                    type: "POST",
                    url: "/myworkflows/start_workflow/",
                    contentType: "application/json; charset=utf-8",
                    data: pdata,
                    success: function (data) {
                        if (data.success) {
                            var redirect_url = '/myworkflows/apply_history/';
                            window.location.href = redirect_url;
                        } else {
                            alert(data.data);
                        }
                    }
                });
            }
        },

        cancel: function (button) {

        },
        confirmButton: "确定",
        cancelButton: "取消",

    });

});
