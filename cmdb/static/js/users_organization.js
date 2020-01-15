var tree;

//初始化ldap下拉框
function initModalSelect2() {
    $select2LDAPGroup = $("#ldap_group").select2({
        ajax: {
            url: '/users/list_ldap_groups/',
            dataType: 'json',
            type: 'POST',
            delay: 0,
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
            cache: true,
        },
        // minimumResultsForSearch: Infinity,
    });

    //初始化节点负责人
    $select2Leader = $('#section-leader').select2({
        ajax: {
            url: '/assets/list_user/',
            dataType: 'json',
            type: 'POST',
            delay: 0,
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
    });

    //初始化父节点
    $select2Parent = $('#section-parent').select2({
        ajax: {
            url: '/users/list_new_organization/',
            dataType: 'json',
            type: 'POST',
            delay: 0,
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
    });

    //初始化所属部门
    $select2Ancestors = $('#ancestors-user-add').select2({
        ajax: {
            url: '/users/list_new_organization/',
            dataType: 'json',
            type: 'POST',
            delay: 0,
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
    });

    $("#ent_email").select2();
}

//搜索函数
function search() {
    let search = document.getElementById("search").value;
    jQuery('#page-wrapper').showLoading();
    result = $('#tree').treeview('search', [search, {
        ignoreCase: true,     // case insensitive
        exactMatch: false,    // like or equals
        revealResults: true,  // reveal matching nodes
    }]);
    if (result.length == 1) {
        // 搜索结果如果只有一条记录，则直接选中节点
        $('#tree').treeview('selectNode', [result]);
    }
    else {
        // 如果搜索结果大于1，则联动数据表格
        var result_list = new Array();
        for (var i = 0; i < result.length; i++) {
            let dataId = result[i].dataId;
            result_list.push({'dataId': dataId})
        }
        var result = JSON.stringify(result_list);
        document.getElementById("iframepage").src = "/users/user_research_result/?result=" + result;
    }
    setTimeout(function () {
        jQuery('#page-wrapper').hideLoading();
    }, 500);
}


//获取树状列表数据
function getTree() {
    //节点上的数据遵循如下的格式：
    $.ajax({
        type: "post",
        async: true,
        url: "/users/organization_tree/",
        dataType: "json",
        beforeSend: function() {
            jQuery('#page-wrapper').showLoading();
        },
        success: function (result) {
            jQuery('#page-wrapper').hideLoading();
            var tree = result.tree;
            $('#tree').treeview({
                data: tree,
                showTags: true,
                highlightSearchResults: true,
            });

            //选中节点后，iframe联动编辑页面，并切换节点展开折叠状态
            $('#tree').on('nodeSelected', function (event, data) {
                document.getElementById("iframepage").src = "/users/organization/" + data.dataId + "/";
            });

            //搜索并高亮
            $('#bt-search').on('click', function () {
                search();
            });
        },
        error: function (errorMsg) {
            jQuery('#page-wrapper').hideLoading();
        }
    });
}


$(document).ready(function () {

    $.fn.select2.defaults.set("theme", "bootstrap");

    getTree();

    //回车键出发搜索函数
    document.onkeyup = function (e) {
        var code = e.charCode || e.keyCode;
        if (code == 13) {
            search();
        }
    };

    //清除搜索
    $('#bt-clear').on('click', function () {
        $('#tree').treeview('clearSearch');
        $('#tree').treeview('expandAll', {levels: 1, silent: true});
        $('#search').val('');
    });

    //折叠所有节点
    $('#bt-collapse').on('click', function () {
        $('#tree').treeview('expandAll', {levels: 1, silent: true});
    });

    //展开所有节点
    $('#bt-expand').on('click', function () {
        $('#tree').treeview('expandAll', {silent: true});
    });


    //弹出增加节点框
    $('#bt-add-section').click(function () {
        initModalSelect2();
        $("#myModalLabel").text("新增节点");
        $("#modal-notify-add-section").hide();
        $('#show_id').hide();
        $("#section_name").val('');
        initSelect2('section-parent', '0', '');
        initSelect2('section-leader', '0', '');
        $("input[type='radio']").removeAttr('checked');
        editFlag = false;
        $("#myModal").modal("show");
    });

    //弹出增加用户框
    $('#bt-add-user').click(function () {
        initModalSelect2();
        $("input[name='is_open_email']").on("click", function () {
            var value = $(this).val();
            if (value == 1) {
                $('#ent_email').attr('disabled', false);
            } else {
                $('#ent_email').attr('disabled', true);
            }
        });
        $("#myModalLabel-add-user").text("新增用户");
        $("#modal-notify-add-user").hide();
        // initSelect2("ldap_group", "0", "选择LDAP部门(不选则不添加LDAP账号)");
        editFlag = false;
        $("#myModal-add-user").modal("show");
    });

});


//保存新增用户js
$('#bt-save-user-add').click(function () {
    let username = $('#name-add-user').val();
    if (username == '') {
        $('#lb-msg-add-user').text('请输入用户名!');
        $('#modal-notify-add-user').show();
        return false;
    }

    let first_name = $('#first_name-add-user').val();
    if (first_name == '') {
        $('#lb-msg-add-user').text('请输入用户拼音!');
        $('#modal-notify-add-user').show();
        return false;
    }

    let title = $('#title').val();
    if (title == '') {
        $('#lb-msg-add-user').text('请输入员工职位!');
        $('#modal-notify-add-user').show();
        return false;
    }
    let sex = $('input:radio[name="sex"]:checked').val();
    if (sex == null) {
        $('#lb-msg-add-user').text('请选择性别!');
        $('#modal-notify-add-user').show();
        return false;
    }

    let is_open_qq = $('input:radio[name="is_open_qq"]:checked').val();
    if (is_open_qq == null) {
        $('#lb-msg-add-user').text('请选择是否开通企业QQ!');
        $('#modal-notify-add-user').show();
        return false;
    }

    let is_open_email = $('input:radio[name="is_open_email"]:checked').val();
    if (is_open_email == null) {
        $('#lb-msg-add-user').text('请选择是否开通企业邮箱!');
        $('#modal-notify-add-user').show();
        return false;
    }

    let ent_email = $('#ent_email').val();
    if (ent_email == null & is_open_email == 1) {
        $('#lb-msg-add-user').text('请选择企业邮箱后缀!');
        $('#modal-notify-add-user').show();
        return false;
    }

    let org = $('#ancestors-user-add').select2('data')[0].id;
    if (org == '0') {
        $('#lb-msg-add-user').text('请选择部门!');
        $('#modal-notify-add-user').show();
        return false;
    }

    let is_superuser = $('input[name=is_superuser]:checked').val();

    let is_open_ldap = $('input:radio[name="is_open_ldap"]:checked').val();
    if (is_open_ldap == null) {
        $('#lb-msg-add-user').text('请选择是否开通ldap!');
        $('#modal-notify-add-user').show();
        return false;
    }

    let inputIds = {
        'username': username,
        'first_name': first_name,
        'email': '',
        'org': org,
        'is_superuser': is_superuser,
        'is_open_ldap': is_open_ldap,
        'sex': sex,
        'title': title,
        'is_open_qq': is_open_qq,
        'is_open_email': is_open_email,
        'ent_email': ent_email,
    };

    let url = "/users/organization_user_add/";

    let encoded = $.toJSON(inputIds);
    let p_data = encoded;

    // initSelect2("ldap_group", "0", "选择LDAP部门(不选则不添加LDAP账号)");

    $.ajax({
        type: "POST",
        url: url,
        contentType: "application/json; charset=utf-8",
        data: p_data,
        success: function (data) {

            if (data['data']) {
                window.location.href = "/users/organization/";
            }
            else {
                $('#lb-msg-add-user').text(data['msg']);
                $('#modal-notify-add-user').show();
            }
        }
    });

});


//保存新增部门或部门分组js
$('#bt-save-section-add').click(function () {
    let parent = $('#section-parent').select2('data')[0].id;
    if (parent == '0') {
        $('#lb-msg-add-section').text('请选择父级节点!');
        $('#modal-notify-add-section').show();
        return false;
    }
    let name = $('#section_name').val();
    if (name == '') {
        $('#lb-msg-add-section').text('请输入节点名称!');
        $('#modal-notify-add-section').show();
        return false;
    }
    let leader = $('#section-leader').select2('data')[0].id;
    if (leader == '0') {
        $('#lb-msg-add-section').text('请选择负责人!');
        $('#modal-notify-add-section').show();
        return false;
    }
    let is_public = $('input:radio[name="is_public"]:checked').val();
    if (is_public == null) {
        $('#lb-msg-add-section').text('请选择是否公共部门!');
        $('#modal-notify-add-section').show();
        return false;
    }
    let is_department_group = $('input:radio[name="is_department_group"]:checked').val();
    if (is_department_group == null) {
        $('#lb-msg-add-section').text('请选择是否部门下分组!');
        $('#modal-notify-add-section').show();
        return false;
    }

    let inputIds = {
        'parent': parent,
        'name': name,
        'leader': leader,
        'is_public': is_public,
        'is_department_group': is_department_group,
    };

    let url = "/users/organization_section_add/";

    let encoded = $.toJSON(inputIds);
    let p_data = encoded;

    // initSelect2("ldap_group", "0", "选择LDAP部门(不选则不添加LDAP账号)");

    $.ajax({
        type: "POST",
        url: url,
        contentType: "application/json; charset=utf-8",
        data: p_data,
        success: function (data) {

            if (data['data']) {
                window.location.href = "/users/organization/";
                $("#myModal-add-user").modal("hide");
            }
            else {
                $('#lb-msg-add-section').text(data['msg']);
                $('#modal-notify-add-section').show();
            }
        }
    });

});


// 导出用户
$('#bt-download').click(function () {
    $.ajax({
        type: "POST",
        url: "/users/downloads/",
        contentType: "application/json; charset=utf-8",
        beforeSend: function () {
            jQuery('#loading').showLoading();
        },
        success: function (data) {
            jQuery('#loading').hideLoading();
            if (data.success) {
                var file_name = data.data;
                var download_url = '/usersdownloads/' + file_name;
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
});
