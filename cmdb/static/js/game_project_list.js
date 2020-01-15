var table;
var editFlag;
var tpl = $("#tpl").html();
//预编译模板
var template = Handlebars.compile(tpl);

// 修改之前的数据
var origin_data;

var str = "确定删除选中的游戏项目?";
var count = 0;

var $select2Leader;
var $select2_status;
var $select2_auto_version_update;
var select2Group;
var select2related_organization;

function checkBeforeAdd(project_name, project_name_en) {
    if (project_name == '') {
        $('#lb-msg').text('请输入项目中文名称!');
        $('#modal-notify').show();
        return false;
    }

    if (project_name_en == '') {
        $('#lb-msg').text('请输入项目英文名称!');
        $('#modal-notify').show();
        return false;
    }

    return true;
}

function edit(id) {
    editFlag = true;
    var data = {
        'id': id,
    };
    var encoded = $.toJSON(data);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/assets/get_cmdb_game_project_list/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function (data) {
            origin_data = data;
            $("#myModalLabel").text("修改游戏项目");
            $("#modal-notify").hide();
            $("#id").val(data.id);
            $("#show_id").hide();
            $("#project_name").val(data.project_name);
            $("#project_name_en").val(data.project_name_en);
            $("#svn_repo").val(data.svn_repo);
            initSelect2('leader', data.leader_id, data.leader);
            //initSelect2('group', data.group_id, data.group);

            // 重新填充select2
            $("#related_user").val('').trigger('change');
            $("#related_user").html('');
            var values = new Array();
            data.related_user.forEach(function (e, i) {
                $("#related_user").append('<option value="' + e.id + '">' + e.username + '</option>');
                values.push(e.id);
            });
            $("#related_user").select2('val', values);
            // 重新填充select2
            $("#relate_role").val('').trigger('change');
            $("#relate_role").html('');
            var values = new Array();
            data.relate_role.forEach(function (e, i) {
                $("#relate_role").append('<option value="' + e.id + '">' + e.name + '</option>');
                values.push(e.id);
            });
            $("#relate_role").select2('val', values);
            // 重新填充select2
            $("#related_organization").val('').trigger('change');
            $("#related_organization").html('');
            var values = new Array();
            data.related_organization.forEach(function (e, i) {
                $("#related_organization").append('<option value="' + e.id + '">' + e.name + '</option>');
                values.push(e.id);
            });
            $("#related_organization").select2('val', values);

            $('#id_game_project_type').css('display', 'none');
            $('input:radio[name=game_project_type]').filter('[value=0]').removeAttr('checked');
            $('input:radio[name=game_project_type]').filter('[value=1]').removeAttr('checked');
            if (data.is_game_project) {
                $('input:radio[name="is_game_project"]').filter('[value="1"]').prop('checked', true);
                $('input:radio[name="game_project_type"]').filter('[value="' + data.game_project_type + '"]').prop('checked', true);
                $('#id_game_project_type').css('display', 'block');
            } else {
                $('input:radio[name="is_game_project"]').filter('[value="0"]').prop('checked', true);
            }

            $("#status").val(data.status).trigger('change');
            $("#auto_version_update").val(data.auto_version_update).trigger('change');
            $("#web_game_id").val(data.web_game_id);
            $("#cloud_account").val(data.cloud_account_id).trigger('change');
            $('#web_ip').val(data.web_ip);
            $('#manager_wan_ip').val(data.manager_wan_ip);
            $('#manager_lan_ip').val(data.manager_lan_ip);
            $('#zabbix_proxy_ip').val(data.zabbix_proxy_ip);
            $('#area').val(data.area).trigger('change');
            $('.soft').val('0').trigger('change');
            for (let key in data.softlist) {
                $('#' + key).val(data.softlist[key]).trigger('change');
            }
            $('#wx_robot').val(data.wx_robot);
            $("#myModal").modal("show");
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


function project_group(id) {
    var url = "/assets/project_group_list/?id=" + id;
    window.location.href = url;
};


function initModalSelect2() {
    $select2_status = $("#status").select2({
        minimumResultsForSearch: Infinity,
    });

    $select2_auto_version_update = $("#auto_version_update").select2({
        minimumResultsForSearch: Infinity,
    });

    $select2Leader = $("#leader").select2({
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
    });

    // $select2Group = $("#group").select2({
    //     ajax: {
    //         url: '/assets/list_group/',
    //         dataType: 'json',
    //         type: 'POST',
    //         delay: 250,
    //         processResults: function (data, params) {
    //             params.page = params.page || 1;
    //             return {
    //                 results: $.map(data, function(item){
    //                     return {
    //                         id: item.id,
    //                         text: item.text,
    //                     }
    //                 })
    //                 // pagination: {
    //                 //     more: (params.page * 30) < data.total_count
    //                 // };
    //             }
    //         },
    //         cache: true,
    //     },
    //     // minimumResultsForSearch: Infinity,
    // });

    $select2related_organization = $("#related_organization").select2({
        ajax: {
            url: '/users/list_new_organization/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
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
            cache: true,
        },
    });

    $select2RelatedUsers = $("#related_user").select2({
        ajax: {
            url: '/assets/list_ops_user/',
            dataType: 'json',
            type: 'POST',
            /*data: function(term, page){
                return {
                    'ip_type': 'VIP',
                }    
            },*/
            delay: 250,
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
            cache: true,
        },
        placeholder: '对接运维',
        multiple: true,
    });

    $select2RelateRoles = $("#relate_role").select2({
        ajax: {
            url: '/users/list_role_group/',
            dataType: 'json',
            type: 'POST',
            delay: 30,
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
            cache: true,
        },
        placeholder: '对接人员分组',
        multiple: true,
    });

    var $select2_role = $("#filter_role").select2({});
    $select2_role.on("select2:select", function (e) {
        table.ajax.reload();
    });
    var $select2_status = $("#filter_status").select2({});
    $select2_status.on("select2:select", function (e) {
        table.ajax.reload();
    });
    var $select2_is_game_project = $("#filter_is_game_project").select2({});
    $select2_is_game_project.on("select2:select", function (e) {
        table.ajax.reload();
    });
    var $select2_project_type = $("#filter_project_type").select2({});
    $select2_project_type.on("select2:select", function (e) {
        table.ajax.reload();
    });

    $('#cloud_account').select2();
    $('#area').select2();

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

function pre_filter_project() {
    var pre_project_name = $.urlParam('project_name');
    if (pre_project_name != null) {
        table.search(pre_project_name).draw()
    }
}

function role_group() {
    window.open('/users/role_group/')
}

$(document).ready(function () {
    $.fn.select2.defaults.set("theme", "bootstrap");

    var rows_selected = [];
    table = $('#mytable').DataTable({
        "processing": true,
        //"serverSide": true,
        "ordering": false,
        "ajax": {
            "url": "/assets/data_game_project_list/",
            "data": function (d) {
                d.filter_role = $('#filter_role').select2('data')[0].id;
                d.filter_status = $('#filter_status').select2('data')[0].id;
                d.filter_is_game_project = $('#filter_is_game_project').select2('data')[0].id;
                d.filter_project_type = $('#filter_project_type').select2('data')[0].id;
            }
        },
        "columns": [
            {"data": null},  // 0
            {"data": "id"},    // 1
            {"data": "project_name"},  // 2
            {"data": "project_name_en"},  // 3
            {"data": "svn_repo"},  // 4
            {"data": "leader"},  // 5
            {"data": "related_organization"},  // 6
            {"data": "related_user"},  // 7
            {"data": "relate_role"},  // 8
            {"data": "status"},  // 9
            {"data": "is_game_project"},  // 10
            {"data": "web_game_id"},  // 11
            {"data": "game_project_type"},  // 12
            {"data": "cloud_account"},  // 13
            {"data": "web_ip"},   // 14
            {"data": "manager_ip"},   // 15
            {"data": "zabbix_proxy_ip"},   // 16
            {"data": "area"},   // 17
            {"data": "softlist"},   // 18
            {"data": "hotupdate_template"},   // 19
            {"data": "auto_version_update"},   // 20
            {"data": "wx_robot"},   // 21
            {
                "data": null,     // 22
                "orderable": false,
            }
        ],
        "order": [[2, 'asc']],
        columnDefs: [
            {
                'targets': 0,
                'searchable': false,
                'orderable': false,
                'className': 'dt-body-center',
                'render': function (data, type, full, meta) {
                    return '<input type="checkbox">';
                },
            },
            {
                'targets': [1, 7, 13, 14, 15, 16, 17, 18, 21],
                'visible': false,
                'searchable': false
            },
            {
                'targets': 5,
                "render": function (data, type, row) {
                    //return '<a href="/users/user_list/?username=' + data + '">' + data + '</a>'
                    return data;
                },
            },
            {
                'targets': 6,
                'width': '15%',
                'searchable': true,
                'orderable': false,
                'className': 'dt-body-left',
                'render': function (data, type, full, meta) {
                    //return '<a href="/users/group_list/?name=' + data + '">' + data + '</a>';
                    return data.split(',').join('<br>');
                },
            },
            {
                'targets': 7,
                "render": function (data, type, row) {
                    return data.split(",").join("<br/>");
                    //return data;
                },
            },
            {
                'targets': 8,
                "render": function (data, type, row) {
                    return data.split(",").join("<br/>");
                    //return data;
                },
            },
            {
                'targets': [15, 18],
                "width": "13%",
                "render": function (data, type, row) {
                    return data.split(",").join("<br/>");
                },
            },
            {
                targets: 19,
                render: function (a, b, c, d) {
                    return c.hotupdate_template.split(',').join('<br/>')
                }
            },
            {
                targets: 22,
                width: '10%',
                render: function (a, b, c, d) {
                    if (c.is_game_project == '是') {
                        var context =
                            {
                                func: [
                                    {"name": "修改", "fn": "edit(\'" + c.id + "\')", "type": "primary"},
                                    //{"name": "项目分组", "fn": "project_group(\'" + c.id + "\')", "type": "info"},
                                    {"name": "热更新模板", "fn": "hotupdate_template(\'" + c.id + "\')", "type": "info"},
                                ]
                            };
                        var html = template(context);
                    }
                    else {
                        var context =
                            {
                                func: [
                                    {"name": "修改", "fn": "edit(\'" + c.id + "\')", "type": "primary"},
                                    //{"name": "项目分组", "fn": "project_group(\'" + c.id + "\')", "type": "info"},
                                ]
                            };
                        var html = template(context);
                    }
                    return html;
                }
            }
        ],
        "language": {
            "url": "/static/js/i18n/Chinese.json"
        },
    });

    pre_filter_project();

    initModalSelect2();

    $(':checkbox.toggle-visiable').on('click', function (e) {
        //e.preventDefault();

        // Get the column API object
        var is_checked = $(this).is(':checked');
        var column = table.column($(this).attr('value'));
        // table.ajax.reload();
        column.visible(is_checked);
    });

    // Handle click on checkbox
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
            makeTitle(str, ++count);
        } else {
            $row.removeClass('selected');
            makeTitle(str, --count);
        }

        // Prevent click event from propagating to parent
        e.stopPropagation();
    });

    // Handle click on table cells
    // $('#mytable tbody').on('click', 'td', function(e){
    //     $(this).parent().find('input[type="checkbox"]').trigger('click');
    // });

    $('#chb-all').on('click', function (e) {
        var checkbox = document.getElementById('chb-all');
        $('#mytable tbody td').parent().find('input[type="checkbox"]').map(function (i, n) {
            var $row = $(this).closest('tr');
            n.checked = checkbox.checked;
            if (checkbox.checked) {
                $row.addClass('selected');
                count = getSelectedTable().length;
                makeTitle(str, count);
            } else {
                $row.removeClass('selected');
                count = 0;
                makeTitle(str, count);
            }
        });

    });


    //删除
    $("#bt-del").confirm({
        //text:"确定删除所选的机房?",
        confirm: function (button) {
            var selected = getSelectedTable();

            if (selected.length == 0) {
                alert('请选择');
            } else {
                var encoded = $.toJSON(selected);
                var pdata = encoded;
                $.ajax({
                    type: "POST",
                    url: "/assets/del_data_cmdb_game_project_list/",
                    contentType: "application/json; charset=utf-8",
                    data: pdata,
                    success: function (data) {

                        if (data['data']) {
                            table.ajax.reload(null, false);
                            makeTitle(str, 0);
                            count = 0;
                        } else {
                            alert(data['msg'])
                            table.ajax.reload();
                            makeTitle(str, 0);
                            count = 0;
                        }
                        ;
                    }
                });
            }
        },

        cancel: function (button) {

        },
        confirmButton: "确定",
        cancelButton: "取消",

    });


    // 监听是否游戏项目的选择
    $("input[name='is_game_project']").on("click", function () {
        var value = $(this).val();
        if (value == 1) {
            $('#id_game_project_type').css('display', 'block');
        } else {
            $('#id_game_project_type').css('display', 'none');
        }
    });


    // 添加
    $('#bt-add').click(function () {
        $("#myModalLabel").text("新增游戏项目参数");
        $("#modal-notify").hide();
        $("#show_id").hide();
        $("#project_name").val('');
        $("#project_name_en").val('');
        $("#svn_repo").val('');
        $('#web_game_id').val('');
        initSelect2('leader', '0', '选择负责人');
        $("#related_user").val('').trigger('change');
        $("#relate_role").val('').trigger('change');
        $("#related_organization").val('').trigger('change');
        $('#id_game_project_type').css('display', 'none');
        $('input:radio[name=game_project_type]').filter('[value=0]').removeAttr('checked');
        $('input:radio[name=game_project_type]').filter('[value=1]').removeAttr('checked');
        $('input:radio[name=is_game_project]').filter('[value=0]').prop('checked', true);
        $("#status").val('1').trigger('change');
        $("#cloud_account").val('0').trigger('change');
        $('#web_ip').val('');
        $('#manager_wan_ip').val('');
        $('#manager_lan_ip').val('');
        $('#zabbix_proxy_ip').val('');
        $("#area").val('0').trigger('change');
        $(".soft").val('0').trigger('change');
        $("#auto_version_update").val('0').trigger('change');
        $('#wx_robot').val('');
        editFlag = false;
        $("#myModal").modal("show");
    });

    $("#del_gorup").click(function () {
        initSelect2('group', '0', '选择部门');
    });

    $("#del_related_roganization").click(function () {
        initSelect2('related_organization', '0', '选择部门');
    });

    $('#bt-save').click(function () {

        var id = $("#id").val();
        var project_name = $("#project_name").val();
        var project_name_en = $("#project_name_en").val();
        var svn_repo = $("#svn_repo").val();
        //var group = $("#group").val();
        var related_organization = $("#related_organization").val();
        var leader = $("#leader").select2('data')[0].id;
        var related_user = $("#related_user").val() == null ? new Array() : $("#related_user").val();
        var relate_role = $("#relate_role").val() == null ? new Array() : $("#relate_role").val();
        var is_game_project = $('input[name=is_game_project]:checked').val();
        var status = $("#status").select2('data')[0].id;
        var auto_version_update = $("#auto_version_update").select2('data')[0].id;
        var web_game_id = $('#web_game_id').val();
        var project_type = $('input[name=game_project_type]:checked').val();
        var cloud_account = $('#cloud_account').val();
        var web_ip = $('#web_ip').val();
        var manager_wan_ip = $('#manager_wan_ip').val();
        var manager_lan_ip = $('#manager_lan_ip').val();
        var zabbix_proxy_ip = $('#zabbix_proxy_ip').val();
        var area = $('#area').val();
        var wx_robot = $('#wx_robot').val();
        var softlist = {};
        $('.soft').each(function (i, e) {
            if ($(e).val()) {
                softlist[$(e).attr('id')] = $(e).val()
            }
        });

        if (is_game_project == 1) {
            if (project_type == null) {
                $('#lb-msg').text('请选择游戏项目类型');
                $('#modal-notify').show();
                return false;
            }
        }

        var inputIds = {
            "id": id,
            "project_name": project_name,
            "project_name_en": project_name_en,
            "svn_repo": svn_repo,
            "leader": leader,
            //"group": group,
            "related_user": related_user,
            "relate_role": relate_role,
            "is_game_project": is_game_project,
            "status": status,
            'related_organization': related_organization,
            'web_game_id': web_game_id,
            'project_type': project_type,
            'cloud_account': cloud_account,
            "editFlag": editFlag,
            'web_ip': web_ip,
            'manager_wan_ip': manager_wan_ip,
            'manager_lan_ip': manager_lan_ip,
            'zabbix_proxy_ip': zabbix_proxy_ip,
            'area': area,
            'softlist': softlist,
            'auto_version_update': auto_version_update,
            'wx_robot': wx_robot,
        };

        var encoded = $.toJSON(inputIds);
        var pdata = encoded;

        urls = '/assets/add_or_edit_game_project/';

        if (!checkBeforeAdd(project_name, project_name_en)) {
            return false;
        }

        $.ajax({
            type: "POST",
            url: urls,
            contentType: "application/json; charset=utf-8",
            data: pdata,
            success: function (data) {

                if (data['data']) {
                    let msg = data['msg'];
                    if (msg != 'ok') {
                        let text = msg.split('http')[0];
                        let link = 'http' + msg.split('http')[1];
                        let html = text + '<a href="' + link + '" class="alert-link" target="_blank">' + link + '</a>';
                        $('#span_page_notice').html(html);
                        $('#div_page_notice').css('display', 'block');
                    }
                    table.ajax.reload(null, false);
                    $("#myModal").modal("hide");
                } else {
                    $('#lb-msg').text(data['msg']);
                    $('#modal-notify').show();
                }
            }
        });
    });

    // 重置筛选条件
    $('#bt-reset').click(function () {
        $(".filter_select2").val("100").select2();
        table.ajax.reload();
    })


});


function hotupdate_template(id) {
    window.location.href = "/myworkflows/hotupdate_templates_bind/" + id + "/"
}
