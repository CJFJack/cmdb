var workflow;
var table;
var project;

var $select2Project;
var $select2Area;
var $select2UpdateVersion;
var $select2ClientType;

var $select2TestHead;
var $select2BackupDev;
var $select2OperationHead;
var $select2PairCode;
var $select2Order;
var $select2Extra;

// 判断更新的游戏项目是手游还是页游
// 默认是页游
var game_type = 1;

var myuuid;

// 这个变量用来判断是否可以正常离开页面
var _finished = false;

// 上传的文件和MD5
/*
格式
[
    {'file_name': 'a.bean', 'fmd5': 'xxxxxx', 'id': 'preview-1504677330847-0'},
    {'file_name': 'a2.bean', 'fmd5': 'xxxxxx', 'id': 'preview-1504677330847-1'},
]
*/
var list_update_file = new Array();

// 生成uuid
function generateUUID() {
    var d = new Date().getTime();
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        var r = (d + Math.random() * 16) % 16 | 0;
        d = Math.floor(d / 16);
        return (c == 'x' ? r : (r & 0x7 | 0x8)).toString(16);
    });

    return uuid;
};

function initModalSelect2() {
    /*
    $select2Project = $('#project').select2( {
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
                    results: $.map(data, function(item){
                        return {
                            id: item.id,
                            text: item.text,
                            type: item.type,
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
        escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
    });*/

    $select2Area = $('#area').select2({
        ajax: {
            url: '/myworkflows/list_area_name_by_project/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page,
                    // project: $("#project").select2('data')[0].id,
                    project: project,
                    update_type: 'hot_client',  // 修改这里的热更新类型 --------!
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
        minimumResultsForSearch: Infinity,
        escapeMarkup: function (markup) {
            return markup;
        }, // let our custom formatter work
    });

    /*
    $select2ClientType = $("#client_type").select2({
        minimumResultsForSearch: Infinity,
    });*/

    $select2PairCode = $("#select_pair_code").select2({
        ajax: {
            url: '/myworkflows/list_pair_code/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page,
                    update_type: 'hot_client',
                };
            },

            processResults: function (data, params) {
                params.page = params.page || 1;
                return {
                    results: $.map(data, function (item) {
                        return {
                            id: item.id,
                            text: item.text,
                            order: item.order,
                        }
                    })
                }
            },
            cache: false,
        },
        minimumResultsForSearch: Infinity,
        escapeMarkup: function (markup) {
            return markup;
        }, // let our custom formatter work
    });

    $select2PairCode.on("select2:select", function (e) {
        reset_pair_code("select2:select", e, $(this));
    });


    $select2Order = $("#order").select2({
        minimumResultsForSearch: Infinity,
    });

    // $select2Project.on("select2:select", function (e) { reset_all("select2:select", e, $( this )); });
    $select2Area.on("select2:select", function (e) {
        reset_all("select2:select", e, $(this));
    });


    // 初始化备用主程审批人
    $select2BackupDev = $("#backup_dev").select2({
        ajax: {
            url: '/assets/list_backup_dev/',
            //url: '/assets/list_user/',
            dataType: 'json',
            type: 'POST',
            delay: 30,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page,
                    project: project,
                    project_group: '前端组',
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
    });

    // 初始化测试负责人，只能是测试部门的人
    $select2TestHead = $("#test_head").select2({
        ajax: {
            url: '/assets/list_test_user/',
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
        minimumResultsForSearch: Infinity,
        multiple: true,
        placeholder: '',
    });

    // 初始化测试负责人，只能是测试部门的人
    $select2OperationHead = $("#operation_head").select2({
        ajax: {
            url: '/assets/list_operation_user/',
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
        minimumResultsForSearch: Infinity,
        multiple: true,
        placeholder: '',
    });

    // 更新完成后需要额外通知的人
    $select2Extra = $("#extra").select2({
        ajax: {
            url: '/assets/list_user/',
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
        minimumResultsForSearch: Infinity,
        multiple: true,
        placeholder: '',
    });

    // 更新版本
    $select2UpdateVersion = $('#update_version').select2({
        ajax: {
            url: '/myworkflows/list_game_client_version/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
            cache: false,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page,
                    project: project,
                    area: $("#area").val(),
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
        },
        escapeMarkup: function (markup) {
            return markup;
        }, // let our custom formatter work
    });

    $select2UpdateVersion.on("select2:select", function (e) {
        display_cdn_version("select2:select", e, $(this));
    });

    // 隐藏客户端类型
    // $("#show_client_type").hide();    
}


// 如果更新的游戏项目是页游，由用户自己选择版本号和cdn目录
function initSelect2UpdateVersion() {
    // 更新版本
    var add_str = '<div class="form-group create_update_version" id="create_update_version">' +
        '<label class="col-sm-12">更新版本号</label>' +
        '<div class="col-sm-6">' +
        '<select id="update_version" style="width: 100%">' +
        '<option value="0" selected="selected">选择更新版本号</option>' +
        '</select>' +
        '</div>' +
        '<div class="alert alert-danger col-sm-4" id="show_update_version_msg" style="display: none;">' +
        '请选择要更新的前端版本号!' +
        '</div>' +
        '</div>'
    $(".create_update_version").remove();
    $("#append_create_update_version").append(add_str);
    $select2UpdateVersion = $('#update_version').select2({
        ajax: {
            url: '/myworkflows/list_game_client_version/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page,
                    project: project,
                    area: $("#area").val(),
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
        }, // let our custom formatter work
    });

    $select2UpdateVersion.on("select2:select", function (e) {
        display_cdn_version("select2:select", e, $(this));
    });
};


// 选择了版本号以后展示cdn和前端版本号的组合
function display_cdn_version(name, evt, className) {
    if (name == "select2:select" || name == "select2:select2") {
        // 清除之前的cdn版本号和文件列表
        $("#show_table").remove();
        $("#show_file_list").remove();
        $(".server-by-cdn").remove();
        var area_name = $("#area").val();
        var client_version = $("#update_version").select2('data')[0].text;
        var table_structrue = `
            <div class="form-group" id="show_table">
                <label class="col-sm-12" for="TextArea">CDN和版本号</label>
                <div class="col-sm-6">
                  <table id="mytable" class="cell-border" width="100%" cellspacing="0">
                    <thead>
                      <tr>
                          <th class="center sorting_disabled">
                            <label class="pos-rel">
                              <input id='chb-all' type="checkbox"/>
                            </label>
                          </th>
                          <th>id</th>
                          <th>项目</th>
                          <th>cdn_root_url</th>
                          <th>cdn_dir</th>
                          <th>client_version</th>
                          <th>地区</th>
                      </tr>
                    </thead>
                  </table>
                </div>
            </div>
        `;
        var inputIds = {
            'project': project,
            'area_name': area_name,
            'client_version': client_version
        };

        var encoded = $.toJSON(inputIds);
        var pdata = encoded;

        $.ajax({
            type: "POST",
            url: "/myworkflows/get_cnd_version_list/",
            contentType: "application/json; charset=utf-8",
            data: pdata,
            success: function (data) {
                $("#create_update_version").after(table_structrue);
                var rows_selected = [];
                table = $("#mytable").DataTable({
                    "data": data,
                    'ordering': false,
                    "paging": false,
                    "info": false,
                    "searching": false,
                    "columns": [
                        {"data": null},
                        {"data": "id"},
                        {"data": "project"},
                        {"data": "cdn_root_url"},
                        {"data": "cdn_dir"},
                        {"data": "client_version"},
                        {"data": "area_name"},
                    ],
                    "columnDefs": [
                        {
                            'targets': 0,
                            'searchable': false,
                            'orderable': false,
                            'className': 'dt-body-left',
                            'render': function (data, type, full, meta) {
                                return '<input type="checkbox">';
                            },
                        },
                        {
                            'targets': [1, 2, 6],
                            'visible': false,
                        },
                    ],
                });

                $('#chb-all').on('click', function (e) {
                    var checkbox = document.getElementById('chb-all');
                    $('#mytable tbody td').parent().find('input[type="checkbox"]').map(function (i, n) {
                        var $row = $(this).closest('tr');
                        var data = table.row($row).data();
                        n.checked = checkbox.checked;
                        if (checkbox.checked) {
                            $row.addClass('selected');
                            // count = getSelectedTable().length;
                            // makeTitle(str, count);
                            $.ajax({
                                url: '/myworkflows/get_server_list_by_cdn/',
                                type: 'POST',
                                async: true,
                                contentType: "application/json; charset=utf-8",
                                data: $.toJSON(data),
                                success: function (result) {
                                    var _id = data.id;
                                    var server_value_id = "server_value" + "_" + _id;
                                    var cdn_root_url = data.cdn_root_url;
                                    var cdn_dir = data.cdn_dir;
                                    var client_version = data.client_version;
                                    var cdn_server_info = cdn_root_url + ':' + cdn_dir + ':' + client_version;
                                    var add_server_by_cdn = '<div class="form-group server-by-cdn" id=' + _id + '>' +
                                        '<label class="col-sm-12">' + cdn_server_info + '</label>' +
                                        '<div class="col-sm-6">' +
                                        '<textarea class="form-control" id=' + server_value_id + ' rows="10"></textarea>' +
                                        '</div>' +
                                        '</div>'
                                    $("#show_table").after(add_server_by_cdn);
                                    // 插入区服列表
                                    $("#" + server_value_id).val(result.data);
                                },
                                error: function () {
                                    alert('根据cdn获取区服列表失败!')
                                    return false
                                }
                            });
                        } else {
                            $row.removeClass('selected');
                            // count = 0;
                            // makeTitle(str, count);
                            var _id = data.id;
                            $("#" + _id).remove();
                        }
                    });

                });

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
                        // makeTitle(str, ++count);
                        // 获取区服列表
                        $.ajax({
                            url: '/myworkflows/get_server_list_by_cdn/',
                            type: 'POST',
                            async: false,
                            contentType: "application/json; charset=utf-8",
                            data: $.toJSON(data),
                            success: function (result) {
                                var _id = data.id;
                                var server_value_id = "server_value" + "_" + _id;
                                var cdn_root_url = data.cdn_root_url;
                                var cdn_dir = data.cdn_dir;
                                var client_version = data.client_version;
                                var cdn_server_info = cdn_root_url + ':' + cdn_dir + ':' + client_version;
                                var add_server_by_cdn = '<div class="form-group server-by-cdn" id=' + _id + '>' +
                                    '<label class="col-sm-12">' + cdn_server_info + '</label>' +
                                    '<div class="col-sm-6">' +
                                    '<textarea class="form-control" id=' + server_value_id + ' rows="10"></textarea>' +
                                    '</div>' +
                                    '</div>'
                                $("#show_table").after(add_server_by_cdn);
                                // 插入区服列表
                                $("#" + server_value_id).val(result.data);
                            },
                            error: function () {
                                alert('根据cdn获取区服列表失败!')
                                return false
                            }
                        });
                    } else {
                        $row.removeClass('selected');
                        var _id = data.id;
                        $("#" + _id).remove();
                        // makeTitle(str, --count);
                    }
                    // Prevent click event from propagating to parent
                    e.stopPropagation();
                });
            },
            error: function () {
                /* Act on the event */
                alert('获取cdn版本号失败');
                return false;
            },
        });
    }
}

// 展示热更新文件列表
function display_file_list(data) {
    var table_structrue = `
            <div class="form-group row" id="show_file_list">
                <label class="col-sm-12" for="TextArea">热更新文件列表</label>
                <div class="col-sm-12">
                  <table id="mytable2" class="cell-border" width="100%" cellspacing="0">
                    <thead>
                      <tr>
                          <th class="center sorting_disabled">
                            <label class="pos-rel">
                              <input id='chb2-all' type="checkbox"/>
                            </label>
                          </th>
                          <th>目录</th>
                          <th>文件名</th>
                          <th>MD5</th>
                      </tr>
                    </thead>
                  </table>
                </div>
            </div>
        `
    $("#add_file_after").after(table_structrue);

    var rows_selected2 = [];
    file_table = $("#mytable2").DataTable({
        "data": data,
        'ordering': false,
        "paging": true,
        "info": false,
        "searching": true,
        "columns": [
            {"data": null},
            {"data": "area_dir"},
            {"data": "file_name"},
            {"data": "file_md5"},
        ],
        "columnDefs": [
            {
                'targets': 0,
                'searchable': false,
                'orderable': false,
                'className': 'dt-body-left',
                'render': function (data, type, full, meta) {
                    return '<input type="checkbox">';
                },
            },
            {
                'targets': 1,
                'visible': false,
            },
        ],
        "language": {
            "url": "/static/js/i18n/Chinese.json"
        },
    });

    $('#chb2-all').on('click', function (e) {
        var rows = file_table.rows({'search': 'applied'}).nodes();
        $('input[type="checkbox"]', rows).prop('checked', this.checked);

        /*$('input[type="checkbox"]', rows).each(function(index, el) {
            var $row = $( this ).parent().parent();
            if ( this.checked ) {
                $row.addClass('selected');
            } else {
                $row.removeClass('selected');
            }
        });*/
    });
}

// 在确认提交处展示选择的热更新文件
function display_overview_file_list() {
    // get_selected_file_list();
    var table_structrue = `
            <div class="form-group row" id="show_overview_file_list">
                <label class="col-sm-12" for="TextArea">热更新文件列表</label>
                <div class="col-sm-12">
                  <table id="mytable3" class="cell-border" width="100%" cellspacing="0">
                    <thead>
                      <tr>
                          <th>文件名</th>
                          <th>MD5</th>
                      </tr>
                    </thead>
                  </table>
                </div>
            </div>
        `
    $("#show_overview_file_list").remove();
    $("#add_overview_cdn_version_before").after(table_structrue);

    overview_file_table = $("#mytable3").DataTable({
        "data": list_update_file,
        'ordering': false,
        "paging": true,
        "info": false,
        "searching": true,
        "columns": [
            {"data": "file_name"},
            {"data": "file_md5"},
        ],
        "language": {
            "url": "/static/js/i18n/Chinese.json"
        },
    });
}

// 选择热更新文件列表
function get_selected_file_list() {
    var current_file_list = new Array();
    var rows = file_table.rows({'search': 'applied'}).nodes();
    $('input[type="checkbox"]', rows).each(function (index, el) {
        var $row = $(this).parent().parent();
        if (this.checked) {
            file_info = file_table.rows($($row)).data()[0];
            current_file_list.push(file_info);
        }
    });
    list_update_file = current_file_list;
}


// 当变更了项目以后全部重置
function reset_all(name, evt, el) {
    if (name == "select2:select" || name == "select2:select2") {
        // 如果是更改了项目，则地区，版本号，cdn和版本号和文件列表都要重置
        if ($(el).attr('id') == 'area') {
            // $("#update_version").val('0').trigger('change');
            $("#show_table").remove();
            $(".cdn_version").remove();
            $("#show_file_list").remove();
            $(".server-by-cdn").remove();

            initSelect2UpdateVersion();
        }
    }
}


// 当选择了创建好的热更新代号后重置
function reset_pair_code(name, evt, el) {
    if (name == "select2:select" || name == "select2:select2") {
        $("#gen_pair_code").val('');

        var order = $("#select_pair_code").select2('data')[0].order;
        if (order == '先') {
            $("#order").val('后').trigger('change');
        } else if (order == '后') {
            $("#order").val('先').trigger('change');
        } else {
            $("#order").val('无').trigger('change');
        }
        $("#order").attr('disabled', true);
    }
}


function get_workflow_state_approve_process() {
    var inputs = {
        'wse': wse,
    }

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

// 获取项目和地区的锁
function get_project_area_lock(project, area) {
    var result = false;
    var _url = "/myworkflows/get_project_area_lock?project=" + project + "&area_name=" + area;
    $.ajax({
        type: "GET",
        url: _url,
        async: false,
        contentType: "application/json; charset=utf-8",
        success: function (data) {
            if (data.success) {
                result = true;
            } else {
                // alert(data.msg);
                $("#show_area_msg").html(data.msg);
                $("#show_area_msg").show();
                result = false;
            }
        },
        error: function () {
            alert('未知的异常');
            result = false;
        }
    });

    return result;
}

// 根据项目地区和绑定代号以及先后顺序判断可用性
function pair_code_order_available(project, area_name, pair_code, order) {
    var result = false;
    if (pair_code == '无' | order == '无') {
        $("#show_pair_code_msg").show();
        $("#show_pair_code_msg").html('如果是和后端绑定热更新，需要绑定代号和顺序!');
        result = false;
        return result;
    }
    var _url = '/myworkflows/get_pair_code_order_available?project=' + project + '&area_name=' + area_name + '&pair_code=' + pair_code + '&order=' + order + '&update_type=hot_client';

    $.ajax({
        type: "GET",
        url: _url,
        async: false,
        contentType: "application/json; charset=utf-8",
        success: function (data) {
            if (data.success) {
                result = true;
            } else {
                // alert(data.msg);
                $("#show_pair_code_msg").html(data.msg);
                $("#show_pair_code_msg").show();
                result = false;
            }
        },
        error: function () {
            alert('未知的异常');
            result = false;
        }
    });

    return result;
}

// 获取热更新代号
function get_select_or_gen_pair_code() {
    var order = $("#order").val();
    if (order == '无') {
        return '无';
    } else {
        var select_pair_code = $("#select_pair_code").val();
        if (select_pair_code != '0') {
            return select_pair_code;
        } else {
            return $("#gen_pair_code").val();
        }
    }
}


// 选择的cdn和版本号
function get_cdn_and_version_by_game_type() {
    if (game_type == 1) {
        return table.rows('.selected').data();
    }

    var cdn_client_version_list = new Array();
    $(".input_cdn_dir").each(function (index, el) {
        cdn_client_version_list.push({"cdn_dir": $(el).val(), "client_version": $("#update_version").val()});
    });

    return cdn_client_version_list;
}

$.urlParam = function (name) {
    var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
    if (results == null) {
        return null;
    }
    else {
        return decodeURIComponent(results[1]) || 0;
    }
}

$(document).ready(function () {

    workflow = $.urlParam('workflow');
    project = $.urlParam('project');

    myuuid = generateUUID();
    // initModalSelect2();

    // initDateTime();

    $("#example-basic").steps({
        headerTag: "h3",
        bodyTag: "section",
        transitionEffect: "slideLeft",
        autoFocus: false,
        showFinishButtonAlways: false,
        enableKeyNavigation: false,
        labels: {
            'next': '下一步',
            'previous': '上一步',
            'finish': '提交'
        },
        // enableCancelButton: true,
        // forceMoveForward: true,
        onInit: function (event, currentIndex, newIndex) {
            // initProject();
            initModalSelect2();
        },
        onStepChanging: function (event, currentIndex, newIndex) {
            if (currentIndex < newIndex & currentIndex == 0) {
                var title = $("#title").val();
                var reason = $("#reason").val();
                var attention = $("#attention").val();

                if (title == '') {
                    $("#show_title_msg").show();
                    return false;
                } else {
                    $("#show_title_msg").hide();
                }

                if (title.length > 255) {
                    $("#show_title_len_msg").show();
                    return false;
                } else {
                    $("#show_title_len_msg").hide();
                }

                /*
                if ( reason == ''){
                    $("#show_reason_msg").show();
                    return false;
                }*/

                return true;

            } else if (currentIndex < newIndex & currentIndex == 1) {
                // var project = $("#project").select2('data')[0].id;
                var area = $("#area").select2('data')[0].text;
                // var test_head = $("#test_head").select2('data')[0].id;
                var backup_dev = $("#backup_dev").val();
                var test_head = $("#test_head").val() == null ? 0 : $("#test_head").val().length;
                // var operation_head = $("#operation_head").select2('data')[0].id;
                var operation_head = $("#operation_head").val() == null ? 0 : $("#operation_head").val().length;


                if (area == '选择区域') {
                    $("#show_area_msg").html('请选择前端热更新地区!');
                    $("#show_area_msg").show();
                    return false;
                } else {
                    $("#show_area_msg").hide();
                }

                if (backup_dev == '0') {
                    $("#show_backup_dev_msg").show();
                    return false;
                } else {
                    $("#show_backup_dev_msg").hide();
                }

                /*
                if ( test_head < 1 ){
                    $("#show_test_head_msg").show();
                    return false;
                } else {
                    $("#show_test_head_msg").hide();
                }*/

                if (operation_head < 1) {
                    $("#show_operation_head_msg").show();
                    return false;
                } else {
                    $("#show_operation_head_msg").hide();
                }

                // var result = get_project_area_lock(project, area);
                // return true;
                // return get_project_area_lock(project, area.split('-')[0]);
                return true;
            } else if (currentIndex < newIndex & currentIndex == 2) {
                /*var client_version = $("#update_version").select2('data')[0].id;

                if ( client_version == '0' ){
                    $("#show_update_version_msg").show();
                    $("#show_update_version_msg").html('请选择要更新的前端版本号!');
                    return false;
                } else {
                    $("#show_update_version_msg").hide();
                }*/

                if (game_type == 1) {
                    var client_version = $("#update_version").val();
                    if (client_version == '0') {
                        $("#show_update_version_msg").show();
                        $("#show_update_version_msg").html('请选择要更新的前端版本号!');
                        return false;
                    } else {
                        $("#show_update_version_msg").hide();
                    }

                    var selected_cdn_client_version = table.rows('.selected').data();
                    if (selected_cdn_client_version.length == 0) {
                        $("#show_update_version_msg").show();
                        $("#show_update_version_msg").html('请选择要更新的cdn和前端版本号!');
                        return false;
                    } else {
                        $("#show_update_version_msg").hide();
                    }
                } else {
                    var client_version = $("#update_version").val();
                    if (client_version == '') {
                        $("#show_update_version_msg").show();
                        $("#show_update_version_msg").html('请填写要更新的前端版本号!');
                        return false;
                    } else {
                        $("#show_update_version_msg").hide();
                    }
                    var input_cdn_dir_array = $(".input_cdn_dir").map(function () {
                        return $(this).val().trim();
                    }).get();
                    var empty_index = $.inArray("", input_cdn_dir_array);
                    // 如果没有添加任何的cdn目录
                    if (input_cdn_dir_array.length == 0) {
                        $("#show_update_version_msg").show();
                        $("#show_update_version_msg").html('请添加cdn目录!');
                        return false;
                    } else {
                        $("#show_update_version_msg").hide();
                    }
                    // 如果添加了cdn目录但是没有填写或者为空
                    if (empty_index != -1) {
                        $("#show_update_version_msg").show();
                        $("#show_update_version_msg").html('请填写cdn目录!');
                        return false;
                    } else {
                        $("#show_update_version_msg").hide();
                    }
                }
                return true;
            } else if (currentIndex < newIndex & currentIndex == 3) {
                // 获取文件列表
                get_selected_file_list();
                if (list_update_file.length == 0) {
                    $("#show_file_list_msg").show();
                    $("#show_file_list_msg").html('你没有选择热更新文件!');
                    return false;
                } else {
                    $("#show_file_list_msg").hide();
                }
                return true;
            } else if (currentIndex < newIndex & currentIndex == 4) {
                var select_pair_code = $("#select_pair_code").val();
                var gen_pair_code = $("#gen_pair_code").val();
                var order = $("#order").val();
                // 从先后顺序入手
                if (order == '无') {
                    if (select_pair_code != '0' | gen_pair_code != '') {
                        $("#show_pair_code_msg").show();
                        $("#show_pair_code_msg").html('你需要同时选择更新代号和先后顺序');
                        return false;
                    } else {
                        $("#show_pair_code_msg").hide();
                    }
                } else {
                    // 如果有了先后顺序，则必须并且只能选一个代号
                    if (select_pair_code != '0' & gen_pair_code != '') {
                        $("#show_pair_code_msg").show();
                        $("#show_pair_code_msg").html('只能选择一个互斥的代号(下拉选择或者生成)');
                        return false;
                    } else if (select_pair_code == '0' & gen_pair_code == '') {
                        $("#show_pair_code_msg").show();
                        $("#show_pair_code_msg").html('请选择一个互斥的代号(下拉选择或者生成)');
                        return false;
                    } else {
                        $("#show_pair_code_msg").hide();
                    }
                }
                return true;
            } else {
                return true;
            }
        },

        onStepChanged: function (event, currentIndex, priorIndex) {
            // the options available on each tab depends on what you have selected in the previous steps.
            $('.steps .current').nextAll().removeClass('done').addClass('disabled');
            if (currentIndex == 3) {
                var area_name = $("#area").val();
                var version = $("#update_version").val();

                $("#file_area_name").val(area_name);
                $("#file_version").val(version);
            }
            if (currentIndex == 5) {
                var title = $("#title").val();
                var reason = $("#reason").val();
                var attention = $("#attention").val();
                var area = $("#area").select2('data')[0].text;
                // var test_head = $("#test_head").select2('data')[0].text;
                // var operation_head = $("#operation_head").select2('data')[0].text;
                var client_version = $("#update_version").val();
                var pair_code = get_select_or_gen_pair_code();
                var order = $("#order").val();

                $("#overview_title").val(title);
                $("#overview_reason").val(reason);
                $("#overview_attention").val(attention);
                $("#overview_area").val(area);
                // $("#overview_test_head").val(test_head);
                // $("#overview_operation_head").val(operation_head);
                $("#overview_update_version").val(client_version);
                $("#overview_pair_code").val(pair_code);
                $("#overview_order").val(order);

                $(".cdn_version").remove();

                //热更新文件数据
                display_overview_file_list();

                var selected_cdn_client_version = get_cdn_and_version_by_game_type();
                selected_cdn_client_version.each(function (el, index) {
                    cdn_root_url = el.cdn_root_url == undefined ? '' : el.cdn_root_url;
                    if (index == 0) {
                        var add_str = '<div class="form-group cdn_version">' +
                            '<label class="col-sm-12" for="TextArea">' +
                            '选择的cdn和版本号' +
                            '</label>' +
                            '<div class="col-sm-3">' +
                            '<input class="form-control" readonly="readonly" value=' + cdn_root_url + '></input>' +
                            '</div>' +
                            '<div class="col-sm-3">' +
                            '<input class="form-control" readonly="readonly" value=' + el.cdn_dir + '></input>' +
                            '</div>' +
                            '<div class="col-sm-3">' +
                            '<input class="form-control" readonly="readonly" value=' + client_version + '></input>' +
                            '</div>' +
                            '</div>'
                    } else {
                        var add_str = '<div class="form-group cdn_version">' +
                            '<div class="col-sm-3">' +
                            '<input class="form-control" readonly="readonly" value=' + cdn_root_url + '></input>' +
                            '</div>' +
                            '<div class="col-sm-3">' +
                            '<input class="form-control" readonly="readonly" value=' + el.cdn_dir + '></input>' +
                            '</div>' +
                            '<div class="col-sm-3">' +
                            '<input class="form-control" readonly="readonly" value=' + client_version + '></input>' +
                            '</div>' +
                            '</div>'
                    }
                    // console.log(add_str);
                    $("#add_overview_cdn_version_before").before(add_str);
                });
            }
        },

        onFinished: function (event, currentIndex) {
            var title = $("#title").val();
            var reason = $("#reason").val();
            var attention = $("#attention").val();
            var area_name = $("#area").select2('data')[0].text;
            var backup_dev = $("#backup_dev").val();
            var test_head = $("#test_head").val();
            var operation_head = $("#operation_head").val();
            var extra = $("#extra").val();
            var client_version = $("#update_version").val();
            // var client_type = $("#client_type").select2('data')[0].id;

            var pair_code = get_select_or_gen_pair_code();
            var order = $("#order").val();

            // 文件列表数据
            // get_selected_file_list();
            if (game_type == 1) {
                var selected_cdn_client_version = table.rows('.selected').data();
                var cdn_client_version_list = new Array();
                selected_cdn_client_version.each(function (el, i) {
                    cdn_client_version_list.push(selected_cdn_client_version[i]);
                });
            } else {
                var cdn_client_version_list = new Array();
                $(".input_cdn_dir").each(function (index, el) {
                    cdn_client_version_list.push({
                        "cdn_dir": $(el).val(),
                        "client_version": $("#update_version").val()
                    });
                });
            }

            var inputs = {
                'workflow': workflow,
                'title': title,
                'reason': reason,
                'attention': attention,
                'project': project,
                'area_name_and_en': area_name,
                'backup_dev': backup_dev,
                'test_head': test_head,
                'operation_head': operation_head,
                'extra': extra,
                'client_version': client_version,
                // 'client_type': client_type,
                'content': cdn_client_version_list,
                'pair_code': pair_code,
                'order': order,
                'list_update_file': list_update_file,
                'uuid': myuuid,
            };

            var encoded = $.toJSON(inputs);
            var pdata = encoded;

            $.ajax({
                type: "POST",
                url: "/myworkflows/start_workflow/",
                contentType: "application/json; charset=utf-8",
                data: pdata,
                success: function (data) {
                    if (data.success) {
                        _finished = true;
                        var redirect_url = '/myworkflows/apply_history/';
                        window.location.href = redirect_url;
                    } else {
                        alert(data.data);
                    }
                },
                error: function () {
                    alert('failed');
                }
            });
        }
    });

    window.onbeforeunload = function () {
        if (!_finished) {
            return '确定放弃本次热更新申请?'
        }
    }

    window.onunload = function () {
        if (!_finished) {
            return '确定放弃本次热更新申请?'
        }
    }

    // 提交
    /*
    $("#bt-commit").confirm({
        text:"确定提交到下一步?",
        confirm: function(button){

            var title = $("#title").val();
            if ( title == "" ){
                alert('请输入标题');
                return false;
            }

            var reason = $("#reason").val();
            if ( reason == "" ){
                alert('请输入更新原因');
                return false;
            }

            var attention = $("#attention").val();

            var project_id = $("#project").select2('data')[0].id;
            var project = $("#project").select2('data')[0].text;
            if ( project_id == "0" ){
                alert('请选择热更项目');
                return false;
            }
            var test_head = $("#test_head").select2('data')[0].id;
            if ( test_head == "0" ){
                alert('请选择测试负责人');
                return false;
            }

            var operation_head = $("#operation_head").select2('data')[0].id;
            if ( operation_head == "0" ){
                alert('请选择运营负责人');
                return false;
            }

            var update_type = $("#update_type").select2('data')[0].text;
            var update_type_id = $("#update_type").select2('data')[0].id;

            var update_version_id = $("#update_version").select2('data')[0].id;
            var update_version = $("#update_version").select2('data')[0].text;
            if ( update_version_id == "0" ){
                alert('请选择更新版本号');
                return false;
            }

            var update_time = $("#update_time").val();
            if ( update_time == "" ){
                alert('请选择更新时间');
                return false;
            }

            var inputs = {
                'title': title,
                'reason': reason,
                'attention': attention,
                'project': project,
                'test_head': test_head,
                'operation_head': operation_head,
                'update_type': update_type,
                'update_type_id': update_type_id,
                'update_version': update_version,
                'update_time': update_time,
                'workflow': workflow,
            }

            // 如果是后端的话添加热更文件列表和erlang命令
            if ( update_type == '后端' ) {
                // 后端文件列表
                var file_list = $("#file_list").val().trim();
                if ( file_list == "" ){
                    alert('你选择了更新后端，需要填写热更文件列表');
                    return false;
                }
                inputs.file_list = file_list;

                // 要执行的erlang命令
                var erlang_cmd = $("#erlang_cmd").val().trim();
                inputs.erlang_cmd = erlang_cmd;
            }


            // 根据选区服的类型来确定content数据
            var choose_server_type = $("#choose_server").select2('data')[0].text;
            if ( choose_server_type == '选服方式' ){
                alert('请选择一个选服方式');
                return false;
            }
            inputs.choose_server_type = choose_server_type;

            if ( update_type == '前端' ){
                if ( choose_server_type == '版本号' ){
                    var content = get_server_list();
                    if ( content.length == 0 ){
                        alert('请选择区服');
                        return false;
                    }
                    inputs.content = content;
                } else if ( choose_server_type == '前端CDN' ){
                    var content = get_cnd_version_list();
                    if ( typeof(content) == "boolean" ){
                        alert('请选择CDN版本号');
                        return false;
                    } else {
                        if ( content.length == 0 ){
                            alert('请选择CDN版本号');
                            return false;
                        }
                    }
                    inputs.content = content;
                }
            } else if ( update_type == '后端' ){
                if ( choose_server_type == '版本号' ){
                    var content = get_server_list();
                    if ( content.length == 0 ){
                        alert('请选择区服');
                        return false;
                    }
                    inputs.content = content;
                }
            }

            var encoded=$.toJSON( inputs );
            var pdata = encoded;

            result = true;
            // console.log(pdata);
            // return false;

            if ( result ){
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

        cancel: function(button){

        },
        confirmButton: "确定",
        cancelButton: "取消",
    });*/

    $("#add_server").click(function () {
        add_server();
    });

    $("#reset_server").click(function () {
        $(".clean_choose_server").remove();
    });

    $("#bt-gen").click(function (event) {
        /* Act on the event */
        var uuid = new Date().getTime();
        var hash_uuid = md5(uuid);
        $("#gen_pair_code").val(hash_uuid);

        $("#select_pair_code").val('0').trigger('change');
        $("#order").val('无').trigger('change');
        $("#order").attr('disabled', false);
    });

    $("#bt-require-file").click(function () {
        var area_name = $("#area").val();
        var area_name_detail = $("#area").select2('data')[0].text;
        var version = $("#update_version").val();

        if (game_type == 1) {
            var selected_cdn_client_version = table.rows('.selected').data();
            var cdn_client_version_list = new Array();
            selected_cdn_client_version.each(function (el, i) {
                cdn_client_version_list.push(selected_cdn_client_version[i]);
            });
        } else {
            var cdn_client_version_list = new Array();
            $(".input_cdn_dir").each(function (index, el) {
                cdn_client_version_list.push({"cdn_dir": $(el).val(), "client_version": $("#update_version").val()});
            });
        }

        // 清除之前的文件列表
        $("#show_file_list").remove();

        var inputs = {
            "update_type": 'hot_client',
            'project': project,
            'area_name': area_name,
            'area_name_detail': area_name_detail,
            'version': version,
            'uuid': myuuid,
            'content': cdn_client_version_list,
        };

        var encoded = $.toJSON(inputs);
        var pdata = encoded;

        $("#bt-require-file").text("获取文件中...");
        $("#bt-require-file").removeClass('btn-success').addClass('btn-secondary');
        $("#bt-require-file").prop('disabled', true);

        $.ajax({
            type: "POST",
            url: "/myworkflows/pull_file_list/",
            contentType: "application/json; charset=utf-8",
            data: pdata,
            success: function (data) {
                if (data.success) {
                    $("#bt-require-file").text("重新获取");
                    $("#bt-require-file").removeClass('btn-secondary').addClass('btn-success');
                    $("#bt-require-file").prop('disabled', false);
                    display_file_list(data.data);
                }
                else {
                    $("#bt-require-file").text(data.data);
                    $("#bt-require-file").removeClass('btn-secondary').addClass('btn-success');
                    $("#bt-require-file").prop('disabled', false);

                }
            }
        });
    });

});
