$(document).ready(function () {
    $.fn.select2.defaults.set( "theme", "bootstrap" );

    initModalSelect2();

    $(".flatpickr").flatpickr({
        locale: "zh",
        enableTime: true,
        time_24hr: true,
    });

    $("#id_type").change(function () {
        var type = $('#id_type option:selected').val();
        if (type == 2) {
            $('#div_id_migrate_time').css('display', 'block');
        }
        else {
            $('#div_id_migrate_time').css('display', 'none');
        }
    })

});


function initModalSelect2() {
    // 初始化运维负责人
    $select2Ops = $("#id_ops").select2({
        ajax: {
            url: '/assets/list_ops_user/',
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
        placeholder: '请选择运维负责人',
    });

    // 定义操作类型为select2
    $("#id_type").select2({
        data: [{id: 1, text: '空闲回收'}, {id: 2, text: '迁服回收'}, {id: 3, text: '关服回收'}],
        allowClear: true,
        placeholder: '请选择操作类型',
    });

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
                console.log(project)
                if (!project) {
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


// 提交迁服/回收主机申请
function submit_apply() {
    var title = $('#id_title').val();
    var ops_id = $('#id_ops').select2('data')[0].id;
    var type = $('#id_type').select2('data')[0].id;
    var ip = $('#id_ip').val();
    var action_time = $('#id_action_time').val();
    var recover_time = $('#id_recover_time').val();
    var action_deadline = $('#id_action_deadline').val();
    var recover_deadline = $('#id_recover_deadline').val();
    var uuid = generateUUID();
    var project = $('#id_project').select2('data')[0].id;
    var room = $('#id_room').select2('data')[0].id;

    if (!title) {
        alert('请填写标题');
        return false;
    }
    if (!project) {
        alert('请选择项目');
        return false;
    }
    if (!room) {
        alert('请选择机房');
        return false;
    }
    if (!ops_id) {
        alert('请选择运维负责人');
        return false;
    }
    if (!type) {
        alert('请选择操作类型');
        return false;
    }
    if (!ip) {
        alert('请填写IP地址');
        return false;
    }
    if (type == '2') {
        if (!action_time) {
            alert('请选择迁服时间');
            return false;
        }
        if (!action_deadline) {
            alert('请选择迁服截止时间');
            return false;
        }
        if (action_deadline <= action_time) {
        alert('迁服截止时间必须大于迁服时间');
        return false;
    }
    }
    if (!recover_time) {
        alert('请选择回收时间');
        return false;
    }
    if (!recover_deadline) {
        alert('请选择回收截止时间');
        return false;
    }
    if (recover_deadline <= recover_time) {
        alert('回收截止时间必须大于回收时间');
        return false;
    }


    if (type == '2') {
        inputIds = {
            'title': title,
            'ops_id': ops_id,
            'type': type,
            'ip': ip,
            'action_time': action_time,
            'action_deadline': action_deadline,
            'recover_time': recover_time,
            'recover_deadline': recover_deadline,
            'uuid': uuid,
            'project': project,
            'room': room,
        };
    }
    else {
        inputIds = {
            'title': title,
            'ops_id': ops_id,
            'type': type,
            'ip': ip,
            'recover_time': recover_time,
            'recover_deadline': recover_deadline,
            'uuid': uuid,
            'project': project,
            'room': room,
        };
    }
    var encoded = $.toJSON(inputIds);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/myworkflows/host_compression_apply/",
        contentType: "application/json; charset=utf-8",
        data: pdata,
        success: function (data) {
            if (data.success) {
                window.location.href = '/myworkflows/host_compression_apply_list/'
            }
            else {
                alert(data.msg)
            }
        },
        error: function (data) {
            if (xhr.status == '403') {
                alert('权限拒绝');
            } else {
                alert('内部错误');
            }
        }
    });
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
}
