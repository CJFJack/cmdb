var workflow;
var table;
var project;

var $select2Project;
var $select2Area;
var $select2UpdateVersion;
var $select2HotServerType;
var $select2ClientType;

var $select2TestHead;
var $select2BackupDev;
var $select2OperationHead;
var $select2PairCode;
var $select2Order;
var $select2Extra;

// 全局唯一的uuid
var myuuid;

var file_table;

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

// 需要更新的区服列表
var update_server_list = new Array();

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


// 给展示框展示文件和MD5
function show_file_and_md5() {
    var add_str = '';

    list_update_file.forEach(function (el, index) {
        var file_name = el.file_name;
        var fmd5 = el.fmd5;
        var new_line = file_name + '    ' + fmd5 + '\n';
        add_str += new_line;
    });

    $("#update_files").val('');
    $("#update_files").val(add_str);
}

// 给展示框展示热更的erl命令
function overview_erlcmd_list() {
    var add_str = '';
    var erlang_cmd = $("#erlang_cmd_list").val().trim();

    $("#overview_erlang_cmd_list").val('');
    $("#overview_erlang_cmd_list").val(erlang_cmd);
}


// 判断erl命令是否包含中文字符
function erl_cmd_has_chinese() {
    var erlang_cmd_list = $("#erlang_cmd_list").val().trim();
    var has_chinese = false;
    for (var i = 0; i < erlang_cmd_list.length; i++) {
        if (erlang_cmd_list.charCodeAt(i) > 255) {
            has_chinese = true;
            return has_chinese
        }
    }

    return has_chinese;
}


// 在确认提交处展示选择的热更新文件
function display_overview_file_list() {
    get_selected_file_list();
    var table_structrue = `
            <div class="form-group row" id="show_overview_file_list">
                <label class="col-sm-12" for="TextArea">热更新文件列表</label>
                <div class="col-sm-12">
                  <table id="mytable3" class="cell-border" width="100%" cellspacing="0">
                    <thead>
                      <tr>
                          <th>文件名</th>
                          <th>MD5</th>
                          <th>最后修改时间</th>
                      </tr>
                    </thead>
                  </table>
                </div>
            </div>
        `
    $("#show_overview_file_list").remove();
    $("#overview_file_after").after(table_structrue);

    overview_file_table = $("#mytable3").DataTable({
        "data": list_update_file,
        'ordering': false,
        "paging": true,
        "info": false,
        "searching": true,
        "columns": [
            {"data": "file_name"},
            {"data": "file_md5"},
            {"data": "file_mtime"},
        ],
        "language": {
            "url": "/static/js/i18n/Chinese.json"
        },
    });
}

// 确认提交处展示区服列表
function overview_server_list() {

    var add_str = '';
    update_server_list.forEach(function (el, index) {
        var srv_name = el.srv_name;
        var gtype = el.gtype;
        var pf_name = el.pf_name;
        var srv_id = el.srv_id;
        var ip = el.ip;

        var new_line = gtype + '    ' + pf_name + '    ' + srv_name + '    ' + srv_id + '    ' + ip + '\n';

        add_str += new_line;

    });

    $("#overview_server_list").val('');
    $("#overview_server_list").val(add_str);
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
        // minimumInputLength: 1,
        // templateResult: formatRepo, // omitted for brevity, see the source of this page
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
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
                    project: project,
                    update_type: 'hot_server',  // 修改这里的热更新类型 --------!
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
                    update_type: 'hot_server',
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
                            order: item.order,
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

    $select2PairCode.on("select2:select", function (e) {
        reset_pair_code("select2:select", e, $(this));
    });

    $select2Order = $("#order").select2({
        minimumResultsForSearch: Infinity,
    });

    /*$select2ClientType = $("#client_type").select2({
        minimumResultsForSearch: Infinity,
    });*/

    $select2HotServerType = $("#hot_server_type").select2({
        minimumResultsForSearch: Infinity,
    });

    $select2HotServerType.on("select2:select", function (e) {
        show_file_or_cmd("select2:select", e, $(this));
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
            delay: 250,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page,
                    project: project,
                    project_group: '后端组',
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
        // escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
        // minimumInputLength: 1,
        // templateResult: formatRepo, // omitted for brevity, see the source of this page
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
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
        multiple: true,
        placeholder: '',
        // escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
        // minimumInputLength: 1,
        // templateResult: formatRepo, // omitted for brevity, see the source of this page
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
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
        multiple: true,
        placeholder: '',
        // escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
        // minimumInputLength: 1,
        // templateResult: formatRepo, // omitted for brevity, see the source of this page
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
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
        multiple: true,
        placeholder: '',
        // escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
        // minimumInputLength: 1,
        // templateResult: formatRepo, // omitted for brevity, see the source of this page
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });


    // 更新版本
    $select2UpdateVersion = $('#update_version').select2({
        ajax: {
            url: '/myworkflows/list_game_server_version/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
            cache: true,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page,
                    project: project,
                    area: $("#area").val(),
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
        escapeMarkup: function (markup) {
            return markup;
        }, // let our custom formatter work
        // minimumInputLength: 1,
        // templateResult: formatRepo, // omitted for brevity, see the source of this page
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });

    $select2UpdateVersion.on("select2:select", function (e) {
        display_server_list("select2:select", e, $(this));
    });
};


/*function initFileInput(selector){
    $("#files").fileinput({
        maxFileCount: 10,
        // showUpload: false,
        showPreview: false,
        showRemove: false,
        showClose: false,
        allowedFileExtensions: ["beam", "txt"],
        // uploadAsync: false,
        uploadUrl: "/myworkflows/upload_hot_server/",
        uploadExtraData: function() {
            return {
                uuid: myuuid,
            };
        }
    });

    // 上传完成后显示文件名和MD5
    $('#files').on('fileuploaded', function(event, data, previewId, index) {
        var response = data.response;
        if ( response.success ) {
            var add_str = response.file_name + '    ' + response.fmd5 + '\n';
            // 给全局的数据添加
            add_update_file(response.file_name, response.fmd5, previewId);

            // 添加展示的文件和MD5
            show_file_and_md5();
        }
    });

    // 删除单个文件
    $('#files').on('filesuccessremove', function(event, id) {
        remove_update_file(id);
        show_file_and_md5();
    });
};*/


function initMultiTree(selector) {
    $("#demo1").treeMultiselect();
}

// 获取选择的区服列表
function get_server_list() {
    // 返回 json list的格式
    var data = new Array();
    $($('.option:checkbox:checked')).each(function (i, e) {
        var server_info = {};
        var parent_element = $(e).parent();
        server_info.srv_id = parent_element.attr('data-srv');
        server_info.srv_name = parent_element.attr('data-value').split(";")[0];
        server_info.ip = parent_element.attr('data-ip');
        server_info.gtype = parent_element.attr('data-gtype');
        server_info.pf_name = parent_element.attr('data-platform');
        server_info.gameserverid = parent_element.attr('data-gameserverid');
        data.push(server_info);
    });

    update_server_list = data;
}

function get_all_server_list() {
    var data = new Array();
    $($('.option:checkbox')).each(function (i, e) {
        var server_info = {};
        var parent_element = $(e).parent();
        server_info.srv_id = parent_element.attr('data-srv');
        server_info.srv_name = parent_element.attr('data-value').split(";")[0];
        server_info.ip = parent_element.attr('data-ip');
        server_info.gtype = parent_element.attr('data-gtype');
        server_info.pf_name = parent_element.attr('data-platform');
        server_info.gameserverid = parent_element.attr('data-gameserverid');
        data.push(server_info);
    });

    return data
}


// 选择了版本号以后展示cdn和前端版本号的组合
function display_server_list(name, evt, className) {
    if (name == "select2:select" || name == "select2:select2") {
        var area_name = $("#area").val();
        var server_version = $("#update_version").select2('data')[0].text;

        // 清空热更新文件table
        $("#show_file_list").remove();

        var inputIds = {
            'project': project,
            'area_name': area_name,
            'server_version': server_version,
            'update_type': '后端',
        };

        var encoded = $.toJSON(inputIds);
        var pdata = encoded;

        $.ajax({
            type: "POST",
            url: "/myworkflows/get_server_tree/",
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

                    $("#clean_server").remove();
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
                                var gameserverid = el.gameserverid;

                                var section = game_type + '/' + pf_name;

                                var option = "<option" + " " +
                                    "vlaue=" + srv_id + " " +
                                    "data-gameserverid=" + gameserverid + " " +
                                    "data-section=" + section + " " +
                                    "data-srv=" + srv_id + " " +
                                    "data-ip=" + ip + " " +
                                    "data-gtype=" + game_type + " " +
                                    "data-platform=" + pf_name + " " +
                                    ">" + srv_name + ';' + srv_id + ';' + ip +
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


// 当变更了项目以后全部重置
function reset_all(name, evt, el) {
    if (name == "select2:select" || name == "select2:select2") {
        // 如果是更改了项目，则地区，版本号，cdn和版本号都要重置
        if ($(el).attr('id') == 'area') {
            // 重置后端版本号
            $("#update_version").val('0').trigger('change');

            // 清空区服列表
            update_server_list = new Array();
            $("#clean_server").remove();

            // 清空热更新文件table
            $("#show_file_list").remove();
        }
    }
}


// 当变更了热更类型以后，展示或者隐藏热更文件和erlang命令
function show_file_or_cmd(name, evt, el) {
    if (name == "select2:select" || name == "select2:select2") {
        var hot_server_type = $("#hot_server_type").select2('data')[0].id;

        if (hot_server_type == '0') {
            // 只热更
            $(".show_update_file").show();
            $(".show_erlang_cmd").hide();

            // 清空erl命令
            $("#erlang_cmd_list").val('');
            // 清空文件列表
            $("#show_file_list").remove();
        } else if (hot_server_type == '1') {
            // 先热更,再执行erl命令
            $(".show_update_file").show();
            $(".show_erlang_cmd").show();

            // 清空erl命令
            $("#erlang_cmd_list").val('');
            // 清空文件列表
            $("#show_file_list").remove();
        } else if (hot_server_type == '2') {
            // 只执行erl命令
            $(".show_update_file").hide();
            $(".show_erlang_cmd").show();

            // 清空erl命令
            $("#erlang_cmd_list").val('');
            // 清空文件列表
            $("#show_file_list").remove();
        } else if (hot_server_type == '3') {
            // 先执行erl命令,再热更
            $(".show_update_file").show();
            $(".show_erlang_cmd").show();

            // 清空erl命令
            $("#erlang_cmd_list").val('');
            // 清空文件列表
            $("#show_file_list").remove();
        }
    }
}

// 展示热更新文件列表
function display_file_list(data) {
    var table_structrue = `
            <div class="form-group row show_update_file" id="show_file_list">
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
                          <th>最后修改时间</th>
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
            {"data": "file_mtime"},
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
                'searchable': false
            },
        ],
        "language": {
            "url": "/static/js/i18n/Chinese.json"
        },
    });

    $('#chb2-all').on('click', function (e) {
        var rows = file_table.rows({'search': 'applied'}).nodes();
        $('input[type="checkbox"]', rows).prop('checked', this.checked);

        $('input[type="checkbox"]', rows).each(function (index, el) {
            var $row = $(this).parent().parent();
            if (this.checked) {
                $row.addClass('selected');
            } else {
                $row.removeClass('selected');
            }
        });
    });

    $('#mytable2 tbody').on('click', 'input[type="checkbox"]', function (e) {
        var $row = $(this).closest('tr');

        var data = file_table.row($row).data();
        var index = $.inArray(data[0], rows_selected2);

        if (this.checked && index === -1) {
            rows_selected2.push(data[0]);
        } else if (!this.checked && index !== -1) {
            rows_selected2.splice(index, 1);
        }

        if (this.checked) {
            $row.addClass('selected');
            // makeTitle(str, ++count);
        } else {
            $row.removeClass('selected');
            // makeTitle(str, --count);
        }

        // Prevent click event from propagating to parent
        e.stopPropagation();
    });
}

// 选择热更新文件列表
function get_selected_file_list() {
    var current_file_list = new Array();
    var rows = file_table.rows({'search': 'applied'}).nodes();
    $('input[type="checkbox"]', rows).each(function (index, el) {
        var $row = $(this).parent().parent();
        if (this.checked) {
            var file_info = file_table.rows($($row)).data()[0];
            current_file_list.push(file_info);
        }
    });
    list_update_file = current_file_list;
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
    var _url = '/myworkflows/get_pair_code_order_available?project=' + project + '&area_name=' + area_name + '&pair_code=' + pair_code + '&order=' + order + '&update_type=hot_server';

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

function initToolTip() {
    var title = '如果勾选了这个按钮,下单后装的所有同版本新服也会同步更新'
    $("[data-toggle='tooltip']").attr('title', title)
    $("[data-toggle='tooltip']").tooltip({html: true});
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
            // initFileInput();
            initMultiTree();
            initToolTip();
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
                } else {
                    $("#show_reason_msg").hide();
                }*/

                return true;
            } else if (currentIndex < newIndex & currentIndex == 1) {
                // var project = $("#project").select2('data')[0].id;
                var area = $("#area").select2('data')[0].text;
                var backup_dev = $("#backup_dev").val();
                var test_head = $("#test_head").val() == null ? 0 : $("#test_head").val().length;
                var operation_head = $("#operation_head").val() == null ? 0 : $("#operation_head").val().length;

                if (area == '选择区域') {
                    $("#show_area_msg").html('请选择后端热更新地区!');
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
            } else if (currentIndex < newIndex & currentIndex == 3) {
                var hot_server_type = $("#hot_server_type").select2('data')[0].id;
                if (hot_server_type == '0') {
                    // 只热更
                    get_selected_file_list();
                    if (list_update_file.length == 0) {
                        $("#show_hot_server_type").html('请选择热更新文件');
                        $("#show_hot_server_type").show();
                        return false;
                    } else {
                        $("#show_hot_server_type").hide();
                    }
                } else if (hot_server_type == '1') {
                    // 先热更,再执行erl命令
                    get_selected_file_list();
                    if (list_update_file.length == 0) {
                        $("#show_hot_server_type").html('请选择热更新文件');
                        $("#show_hot_server_type").show();
                        return false;
                    } else {
                        $("#show_hot_server_type").hide();
                    }
                    var erlang_cmd = $("#erlang_cmd_list").val().trim();
                    if (erlang_cmd == '') {
                        $("#show_hot_server_type").html('请输入erl命令');
                        $("#show_hot_server_type").show();
                        return false;
                    } else {
                        $("#show_hot_server_type").hide();
                    }
                    // 检测erl命令是否包含中文字符
                    if (erl_cmd_has_chinese()) {
                        $("#show_hot_server_type").html('erlang命令包含中文字符!');
                        $("#show_hot_server_type").show();
                        return false;
                    } else {
                        $("#show_hot_server_type").hide();
                    }
                } else if (hot_server_type == '2') {
                    // 只执行erl命令
                    var erlang_cmd = $("#erlang_cmd_list").val().trim();
                    if (erlang_cmd == '') {
                        $("#show_hot_server_type").html('请输入erl命令');
                        $("#show_hot_server_type").show();
                        return false;
                    } else {
                        $("#show_hot_server_type").hide();
                    }
                    // 检测erl命令是否包含中文字符
                    if (erl_cmd_has_chinese()) {
                        $("#show_hot_server_type").html('erlang命令包含中文字符!');
                        $("#show_hot_server_type").show();
                        return false;
                    } else {
                        $("#show_hot_server_type").hide();
                    }
                } else if (hot_server_type == '3') {
                    // 先执行erl命令,再热更
                    get_selected_file_list();
                    var erlang_cmd = $("#erlang_cmd_list").val().trim();
                    if (erlang_cmd == '') {
                        $("#show_hot_server_type").html('请输入erl命令');
                        $("#show_hot_server_type").show();
                        return false;
                    } else {
                        $("#show_hot_server_type").hide();
                    }
                    // 检测erl命令是否包含中文字符
                    if (erl_cmd_has_chinese()) {
                        $("#show_hot_server_type").html('erlang命令包含中文字符!');
                        $("#show_hot_server_type").show();
                        return false;
                    } else {
                        $("#show_hot_server_type").hide();
                    }
                    if (list_update_file.length == 0) {
                        $("#show_hot_server_type").html('请选择热更新文件');
                        $("#show_hot_server_type").show();
                        return false;
                    } else {
                        $("#show_hot_server_type").hide();
                    }
                }
                return true;
            } else if (currentIndex < newIndex & currentIndex == 2) {
                var server_version = $("#update_version").select2('data')[0].id;

                if (server_version == '0') {
                    $("#show_update_version_msg").show();
                    $("#show_update_version_msg").html('请选择要更新的后端版本号!');
                    return false;
                } else {
                    $("#show_update_version_msg").hide();
                }

                // 判断是否选了区服
                get_server_list();
                if (update_server_list.length == 0) {
                    $("#show_update_version_msg").show();
                    $("#show_update_version_msg").html('请选择要更新的区服!');
                    return false;
                } else {
                    $("#show_update_version_msg").hide();
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

            if (currentIndex == 5) {
                var title = $("#title").val();
                var reason = $("#reason").val();
                var attention = $("#attention").val();
                // var project = $("#project").select2('data')[0].text;
                var area = $("#area").select2('data')[0].text;
                // var test_head = $("#test_head").select2('data')[0].text;
                // var operation_head = $("#operation_head").select2('data')[0].text;
                var server_version = $("#update_version").select2('data')[0].text;
                var pair_code = get_select_or_gen_pair_code();
                var order = $("#order").val();

                $("#overview_title").val(title);
                $("#overview_reason").val(reason);
                $("#overview_attention").val(attention);
                // $("#overview_project").val(project);
                $("#overview_area").val(area);
                // $("#overview_test_head").val(test_head);
                // $("#overview_operation_head").val(operation_head);
                $("#overview_update_version").val(server_version);
                $("#overview_pair_code").val(pair_code);
                $("#overview_order").val(order);

                if ($("#on_new_server").prop('checked')) {
                    $("#overview_on_new_server").val('是');
                } else {
                    $("#overview_on_new_server").val('否');
                }

                // 展示热更的方式
                $("#overview_hot_server_type").val($("#hot_server_type").select2('data')[0].text);

                if ($("#hot_server_type").select2('data')[0].id == '0') {
                    // 只热更

                    // 展示热更的文件和MD5
                    display_overview_file_list();
                    $("#show_overview_update_files").show();

                    $("#show_overview_erlang_cmd_list").hide();
                } else if ($("#hot_server_type").select2('data')[0].id == '1') {
                    // 先热更,再执行erl命令

                    // 展示热更的文件和MD5
                    display_overview_file_list();
                    $("#show_overview_update_files").show();

                    // 展示热更的erl命令
                    overview_erlcmd_list();
                    $("#show_overview_erlang_cmd_list").show();
                } else if ($("#hot_server_type").select2('data')[0].id == '2') {
                    // 只执行erl命令

                    // 展示热更的erl命令
                    overview_erlcmd_list();
                    $("#show_overview_erlang_cmd_list").show();

                    $("#show_overview_update_files").hide();
                } else if ($("#hot_server_type").select2('data')[0].id == '3') {
                    // 先执行erl命令,再热更

                    // 展示热更的文件和MD5
                    display_overview_file_list();
                    $("#show_overview_update_files").show();

                    // 展示热更的erl命令
                    overview_erlcmd_list();
                    $("#show_overview_erlang_cmd_list").show();
                } else {
                    // 展示热更的文件和MD5
                    display_overview_file_list();
                    $("#show_overview_update_files").show();

                    // 展示热更的erl命令
                    overview_erlcmd_list();
                    $("#show_overview_erlang_cmd_list").show();
                }

                // 展示更新区服列表
                overview_server_list();

            }
        },

        onFinished: function (event, currentIndex) {
            var title = $("#title").val();
            var reason = $("#reason").val()
            var attention = $("#attention").val()
            var area_name = $("#area").select2('data')[0].text;
            var backup_dev = $("#backup_dev").val();
            var test_head = $("#test_head").val();
            var operation_head = $("#operation_head").val();
            var extra = $("#extra").val();
            var hot_server_type = $("#hot_server_type").select2('data')['0'].id;
            var erlang_cmd_list = $("#erlang_cmd_list").val().trim();
            var server_version = $("#update_version").select2('data')[0].text;
            var pair_code = get_select_or_gen_pair_code();
            var order = $("#order").val();
            var on_new_server = $("#on_new_server").prop('checked');

            var replication_server_list = get_all_server_list()

            // 这里重新获取区服列表
            get_server_list();

            // 文件列表数据
            if (hot_server_type != '2') {
                get_selected_file_list();
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
                'hot_server_type': hot_server_type,
                'list_update_file': list_update_file,
                'erlang_cmd_list': erlang_cmd_list,
                'server_version': server_version,
                'update_server_list': update_server_list,
                'replication_server_list': replication_server_list,
                'on_new_server': on_new_server,
                'pair_code': pair_code,
                'order': order,
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

    $("#on_new_server").click(function (event) {
        /* Act on the event */
        if ($("#on_new_server").prop('checked')) {
            var add_str = '<div class="form-group col-sm-6" id="show_on_new_server">' +
                '<div class="alert alert-danger">' +
                '下单后如果有同版本新服<strong>所有同版本新服</strong>也会同步更新!' +
                '</div>' +
                '</div>'

            $("#on_new_server_div").after(add_str)
        } else {
            $("#show_on_new_server").remove()
        }
    });

    // 清空要热更新的文件
    $("#bt-reset").click(function (event) {
        /* Act on the event */
        $("#files").fileinput('clear');

        list_update_file = new Array();

        show_file_and_md5();

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

    // 获取后端热更新文件
    $("#bt-require-file").click(function () {
        // var project = $("#project").val();
        var area_name = $("#area").val();
        var area_name_detail = $("#area").select2('data')[0].text;
        var version = $("#update_version").select2('data')[0].text;

        // 清除之前的文件列表
        $("#show_file_list").remove();

        var inputs = {
            "update_type": 'hot_server',
            'project': project,
            'area_name': area_name,
            'area_name_detail': area_name_detail,
            'version': version,
            'uuid': myuuid,
            'update_server_list': update_server_list,
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
