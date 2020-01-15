var workflow;
var table;
var project;

var $select2Area;
var $select2ClientType;

var $select2TestHead;
var $select2BackupDev;
var $select2OperationHead;
var $select2PairCode;
var $select2Order;
var $select2Extra;
var $select2ExtraProjectGroup;

// 判断更新的游戏项目是0:手游还是1:页游
// 默认是页游
var game_type = 0;

var myuuid;

// 这个变量用来判断是否可以正常离开页面
var _finished = false;


// 在确认提交处展示选择的热更新文件
function display_overview_file_list() {
    // get_selected_file_list();
    var table_structrue = `
            <div class="alert alert-danger col-sm-12" id="show_update_version_msg">
            <div class="form-group row" id="show_overview_file_list">
                <label class="col-sm-12" for="TextArea">热更新文件列表</label>
                <div class="col-sm-12">
                  <table id="mytable3" class="cell-border" width="100%" cellspacing="0">
                    <thead>
                      <tr>
                          <th>版本号</th>
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
            {"data": "version"},
            {"data": "file_name"},
            {"data": "file_md5"},
        ],
        "language": {
            "url": "/static/js/i18n/Chinese.json"
        },
    });
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
                          <th>设备类型</th>
                          <th>版本号</th>
                          <th>目录</th>
                          <th>文件名</th>
                          <th>MD5</th>
                          <th>时间</th>
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
            {"data": "client_type"},
            {"data": "version"},
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
                'targets': 3,
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

    /*$select2ClientType = $("#client_type").select2({
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

    // $select2Project.on("select2:select", function (e) { reset_all("select2:select", e, $( this )); });
    // $select2Area.on("select2:select", function (e) { reset_all("select2:select", e, $( this )); });
    // $select2ClientType.on("select2:select", function (e) { reset_all("select2:select", e, $( this )); });


    // 初始化备用主程审批人
    $select2BackupDev = $("#backup_dev").select2({
        ajax: {
            url: '/assets/list_backup_dev/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page,
                    project: project,
                    project_group: '前端组',
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

    $select2ExtraProjectGroup = $("#extra_project_group").select2({
        ajax: {
            url: '/assets/list_project_group/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page,
                    project: project,
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
}


// 当变更了项目以后全部重置
function reset_all(name, evt, el) {
    if (name == "select2:select" || name == "select2:select2") {
        // 如果是更改了项目，则地区，版本号，cdn和版本号和文件列表都要重置
        if ($(el).attr('id') == 'client_type') {
            // $("#update_version").val('0').trigger('change');
            $("#show_table").remove();
            $(".cdn_version").remove();
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


function get_version_char() {
    var version_char = '';
    $(".update_content").each(function (i, e) {
        var update_version = $($(e).children().get(3)).find('input');
        version_char += update_version.val() + ',';
    });
    return version_char
}


function get_version_list() {
    var version_list = new Array();
    $(".update_content").each(function (i, e) {
        var update_version = $($(e).children().get(3)).find('input');
        version_list.push(update_version.val().trim())
    });
    return version_list
}


function get_client_type_list() {
    var client_type_list = new Array();
    $(".update_content").each(function (i, e) {
        var update_client_type = $($(e).children().get(2)).find('select');
        var update_version = $($(e).children().get(3)).find('input');
        var client_type_dict = {};
        client_type_dict[update_version.val().trim()] = update_client_type.val().split('/')[1];
        client_type_list.push(client_type_dict)
    });
    return client_type_list
}


// 选择的cdn和版本号以及类型
/*      [
            {'cdn_root_url': 'res.ssss.chuangyunet.com', 'cdn_dir': 't1', 'version': 'axxx_13342', 'client_type': 'cn_ios'},
            {'cdn_root_url': 'res.ssss.chuangyunet.com', 'cdn_dir': 't1', 'version': 'axxx_13342', 'client_type': 'cn_ios'},
            {'cdn_root_url': 'res.ssss.chuangyunet.com', 'cdn_dir': 't1', 'version': 'axxx_13342', 'client_type': 'cn_ios'},
        ],
*/
function get_cdn_version_type() {
    var client_type_cdn_root_dir_version = new Array();
    $(".update_content").each(function (i, e) {
        var item_info = {};
        var client_type = $($(e).children().get(0)).find('.client_type');
        var cdn_root_url = $($(e).children().get(1)).find('.cdn_root_url');
        var cdn_dir = $($(e).children().get(2)).find('.cdn_dir');
        var update_version = $($(e).children().get(3)).find('input');

        item_info.client_type = cdn_dir.val().split('/')[1];
        item_info.cdn_root_url = cdn_root_url.val();
        item_info.cdn_dir = cdn_dir.val().split('/')[0];
        item_info.version = $.trim(update_version.val());

        client_type_cdn_root_dir_version.push(item_info)
    });

    return client_type_cdn_root_dir_version
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
                    project: project,
                    area_name: $("#area").select2('data')[0].text,
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
                    project: project,
                    area_name: $("#area").select2('data')[0].text,
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
    })

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
                    project: project,
                    client_type: $(selector).parent().prev().prev().find('.client_type').val(),
                    cdn_root_url: $(selector).parent().prev().find('.cdn_root_url').val(),
                    area_name: $("#area").select2('data')[0].text
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
            var cdn_root_url = $(el).parent().next().find('.cdn_root_url')
            $(cdn_root_url).html('')
            $(cdn_root_url).append('<option value="0">选择cdn根路径</option>')
            $(cdn_root_url).select2('val', 0, true)

            var cdn_dir = $(el).parent().next().next().find('.cdn_dir')
            $(cdn_dir).html('')
            $(cdn_dir).append('<option value="0">选择cdn目录</option>')
            $(cdn_dir).select2('val', 0, true)
        } else if ($(el).hasClass('cdn_root_url')) {
            var cdn_dir = $(el).parent().next().find('.cdn_dir')
            $(cdn_dir).html('')
            $(cdn_dir).append('<option value="0">选择cdn目录</option>')
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
    if ($(".update_content").length == 0) {
        alert('请添加更新条目')
        result = false
    } else {
        $(".update_content").each(function (i, e) {
            var client_type = $($(e).children().get(0)).find('.client_type')
            var show_update_content_msg = $($(e).children().get(4))
            var cdn_root_url = $($(e).children().get(1)).find('.cdn_root_url')
            var cdn_dir = $($(e).children().get(2)).find('.cdn_dir')
            var update_version = $($(e).children().get(3)).find('input')
            // if (client_type.val() == '0') {
            //     show_update_content_msg.html('请选择类型')
            //     show_update_content_msg.show()
            //     result = false
            //     return false
            // } else {
            //     show_update_content_msg.hide()
            // }
            if (cdn_root_url.val() == '0') {
                show_update_content_msg.html('请选择cdn root url')
                show_update_content_msg.show()
                result = false
                return false
            } else {
                show_update_content_msg.hide()
            }
            if (cdn_dir.val() == '0') {
                show_update_content_msg.html('请选择cdn dir')
                show_update_content_msg.show()
                result = false
                return false
            } else {
                show_update_content_msg.hide()
            }
            if (client_type.val() == 'cn_ios') {
                if (update_version.val()[0] != 'I') {
                    show_update_content_msg.html('版本号格式不对!')
                    show_update_content_msg.show()
                    result = false
                    return false
                } else {
                    show_update_content_msg.hide()
                }
            }

            if (client_type.val() == 'cn_android') {
                if (update_version.val()[0] != 'A') {
                    show_update_content_msg.html('版本号格式不对!')
                    show_update_content_msg.show()
                    result = false
                    return false
                } else {
                    show_update_content_msg.hide()
                }
            }

            // var cdn_dir_resource_name = cdn_dir.val().split('_')[0]
            // var update_version_resource_name = update_version.val().split('_')[0].slice(1)
            //
            // if ( cdn_dir_resource_name != update_version_resource_name ) {
            //     show_update_content_msg.html('版本号格式和cdn目录不匹配!')
            //     show_update_content_msg.show()
            //     result = false
            //     return false
            // } else {
            //     show_update_content_msg.hide()
            // }

        })
    }
    return result
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
                return get_project_area_lock(project, area.split('-')[0]);
            } else if (currentIndex < newIndex & currentIndex == 2) {
                var result = checkUpdateContent()
                if (result) {
                    return true;
                }
                else {
                    return false;
                }
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
                var version = get_version_char();

                $("#file_area_name").val(area_name);
                $("#file_version").val(version);
            }
            if (currentIndex == 5) {
                var title = $("#title").val();
                var reason = $("#reason").val();
                var attention = $("#attention").val();
                var area = $("#area").select2('data')[0].text;
                var client_version = get_version_char();
                var pair_code = get_select_or_gen_pair_code();
                var order = $("#order").val();

                $("#overview_title").val(title);
                $("#overview_reason").val(reason);
                $("#overview_attention").val(attention);
                $("#overview_area").val(area);
                $("#overview_update_version").val(client_version);
                $("#overview_pair_code").val(pair_code);
                $("#overview_order").val(order);

                $(".cdn_version").remove();
                $(".client_type_cdn_root_dir_version").remove();

                //热更新文件数据
                display_overview_file_list();

                var client_type_cdn_root_dir_version = get_cdn_version_type();
                client_type_cdn_root_dir_version.forEach(function (el, index) {
                    if (index == 0) {
                        var add_str = '<div class="form-group client_type_cdn_root_dir_version">' +
                            '<label class="col-sm-12">' +
                            '更新的条目' +
                            '</label>' +
                            '<div class="col-sm-3" style="display: none;">' +
                            '<input class="form-control" readonly="readonly" value=' + el.client_type + '>' +
                            '</div>' +
                            '<div class="col-sm-3">' +
                            '<input class="form-control" readonly="readonly" value=' + el.cdn_root_url + '>' +
                            '</div>' +
                            '<div class="col-sm-3">' +
                            '<input class="form-control" readonly="readonly" value=' + el.cdn_dir + '>' +
                            '</div>' +
                            '<div class="col-sm-3">' +
                            '<input class="form-control" readonly="readonly" value=' + el.version + '>' +
                            '</div>' +
                            '</div>'
                    } else {
                        var add_str = '<div class="form-group cdn_version">' +
                            '<div class="col-sm-3" style="display: none;">' +
                            '<input class="form-control" readonly="readonly" value=' + el.client_type + '>' +
                            '</div>' +
                            '<div class="col-sm-3">' +
                            '<input class="form-control" readonly="readonly" value=' + el.cdn_root_url + '>' +
                            '</div>' +
                            '<div class="col-sm-3">' +
                            '<input class="form-control" readonly="readonly" value=' + el.cdn_dir + '>' +
                            '</div>' +
                            '<div class="col-sm-3">' +
                            '<input class="form-control" readonly="readonly" value=' + el.version + '>' +
                            '</div>' +
                            '</div>'
                    }
                    $("#add_overview_cdn_version_before").before(add_str);
                })
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
            var extra_project_group = $("#extra_project_group").val();
            var client_version = 'xxxxxxx';
            var client_type = $(".client_type").select2('data')[0].id;

            var pair_code = get_select_or_gen_pair_code();
            var order = $("#order").val();

            // cdn根和dir
            var client_type_cdn_root_dir_version = get_cdn_version_type();

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
                'extra_project_group': extra_project_group,
                'client_version': client_version,
                'client_type': client_type,
                'content': client_type_cdn_root_dir_version,
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


    $("#bt-gen").click(function (event) {
        /* Act on the event */
        var uuid = new Date().getTime();
        var hash_uuid = md5(uuid);
        $("#gen_pair_code").val(hash_uuid);

        $("#select_pair_code").val('0').trigger('change');
        $("#order").val('无').trigger('change');
        $("#order").attr('disabled', false);
    });

    $("#bt-cdn").click(function (event) {
        // 根据地区和客户端类型来获取
        // cdn 目录

        // 删除原来的cdn信息
        $("#show_table").remove();
        var client_type = $(".client_type").val();
        var area_name_en = $("#area").select2('data')[0].text.split('-')[1];
        var inputs = {
            'client_type': client_type,
            'project': project,
            'area_name_en': area_name_en,
        }

        var encoded = $.toJSON(inputs);
        var pdata = encoded;
        $.ajax({
            type: "POST",
            url: '/myworkflows/get_remote_cdn/',
            async: false,
            data: pdata,
            contentType: "application/json; charset=utf-8",
            success: function (data) {
                if (data.success) {
                    // console.log('ok');
                    var table_data = data.data;
                    var table_structrue = `
                        <div class="form-group" id="show_table">
                            <label class="col-sm-12" for="TextArea">CDN目录</label>
                            <div class="col-sm-6">
                              <table id="mytable" class="cell-border" width="100%" cellspacing="0">
                                <thead>
                                  <tr>
                                      <th class="center sorting_disabled">
                                        <label class="pos-rel">
                                          <input id='chb-all' type="checkbox"/>
                                        </label>
                                      </th>
                                      <th>cdn_root_url</th>
                                      <th>cdn_dir</th>
                                  </tr>
                                </thead>
                              </table>
                            </div>
                        </div>
                    `
                    $("#create_update_version").after(table_structrue);
                    var rows_selected = [];
                    table = $("#mytable").DataTable({
                        "data": table_data,
                        'ordering': false,
                        "paging": false,
                        "info": false,
                        "searching": false,
                        "columns": [
                            {"data": null},
                            {"data": "cdn_root_url"},
                            {"data": "cdn_dir"},
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
                            } else {
                                $row.removeClass('selected');
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
                        } else {
                            $row.removeClass('selected');
                        }
                        // Prevent click event from propagating to parent
                        e.stopPropagation();
                    });


                } else {
                    alert('获取cdn失败');
                    return false;
                }
            },
            error: function () {
                alert('获取cdn失败');
                return false;
            }
        });
    });

    $("#bt-add").click(function (event) {
        /* Act on the event */
        var add_str = '<div class="form-group update_content">' +
            '<div class="col-sm-2" style="display: none;">' +
                '<select style="width: 70%" class="client_type">' +
                    '<option value="0" selected="selected">选择类型</option>' +
                '</select>' +
            '</div>' +
            '<div class="col-sm-2">' +
            '<select style="width: 100%" class="cdn_root_url">' +
            '<option value="0" selected="selected">选择cdn根路径</option>' +
            '</select>' +
            '</div>' +
            '<div class="col-sm-2">' +
            '<select style="width: 70%" class="cdn_dir">' +
            '<option value="0" selected="selected">选择cdn目录</option>' +
            '</select>' +
            '</div>' +
            '<div class="col-sm-2">' +
            '<input type="text" class="form-control" style="width: 100%" placeholder="更新版本">' +
            '</div>' +
            '<div class="alert alert-danger col-sm-2 show_update_content_msg" style="display: none;">' +
            '请选择更新cdn root url!' +
            '</div>' +
            '<div class="col-sm-1">' +
            '<button class="btn btn-danger btn-sm myRemove" type="button">x</button>' +
            '</div>' +
            '</div>'
        $("#create_update_version").after(add_str);

        var selector_client_type = $($("#create_update_version").next().children().get(0)).find('.client_type')
        var selector_cdn_root_url = $($("#create_update_version").next().children().get(1)).find('.cdn_root_url');
        var selector_cdn_dir = $($("#create_update_version").next().children().get(2)).find('.cdn_dir');

        var myRemove_bt = $($("#create_update_version").next().children().get(3))

        // console.log(selector_client_type)

        initClientType(selector_client_type);
        initCDNRootUlr(selector_cdn_root_url);
        initCDNDir(selector_cdn_dir);
        addMyRemove()

    });

    $("#bt-require-file").click(function () {
        var area_name = $("#area").val();
        var area_name_detail = $("#area").select2('data')[0].text;
        var version = get_version_list();
        var client_type = get_client_type_list();

        // 清除之前的文件列表
        $("#show_file_list").remove();

        var inputs = {
            "update_type": 'hot_client',
            'project': project,
            'area_name': area_name,
            'area_name_detail': area_name_detail,
            'version': version,
            'uuid': myuuid,
            'client_type': client_type,
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
