
var str = "确定删除用户?";
var count=0;

//预编译模板
var tpl = $("#tpl").html();

var template = Handlebars.compile(tpl);

var $select2AddGroup;
var $select2AddGameProject;
var $select2ProjectGroup;
var $select2GroupSection;
var $select2LDAPGroup;


function passwd(id){
    $("#show_passwd_id").hide();
    $("#id-passwd").val(id);
    $("#password").val('');
    $("#modal-passwd-notify2").hide();
    $("#Modal-passwd").modal("show");
};


function edit(id) {
    editFlag = true;
    var data = {
        'id': id,
    };
    var encoded = $.toJSON(data);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/users/get_data_user/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function(data){
            if (data.success){
                $("#myModalLabel").text("修改用户信息");
                $("#modal-notify").hide();
                $("#id").val(data.data.id);
                $("#show_id").hide()
                $("#show_ldap_group").hide()
                $("#username").val(data.data.username);
                // $("#show_first_name").hide()
                $("#first_name").val(data.data.first_name);
                $("#email").val(data.data.email);

                initSelect2('add_group', data.data.group_id, data.data.group_name);
                initSelect2('group_section', data.data.group_section_id, data.data.group_section_name);

                initSelect2('add_game_project', data.data.project_id, data.data.project_name);

                initSelect2('project_group', data.data.project_group_id, data.data.project_group_name);

                if (data.data.is_superuser){
                    $('input:radio[name="is_superuser"]').filter('[value="1"]').prop('checked', true);
                }else{
                    $('input:radio[name="is_superuser"]').filter('[value="0"]').prop('checked', true);
                }

                if (data.data.is_active){
                    $('input:radio[name="is_active"]').filter('[value="1"]').prop('checked', true);
                }else{
                    $('input:radio[name="is_active"]').filter('[value="0"]').prop('checked', true);
                }

                // 屏蔽不能修改的项
                if (data.immutable){
                    $(".immutable").prop('disabled', true);
                } else {
                    $(".immutable").prop('disabled', false);
                }

                if (data.subordinate_user){
                    $(".subordinate_user").prop('disabled', false);
                } else {
                    $(".subordinate_user").prop('disabled', true);
                }

                $("#myModal").modal("show");
            } else {
                alert(data.data);
            }
        },
    });
};

function clean(id) {
    var _url = '/users/clean/?id=' + id;
    window.location.href = _url;
}

function desert(id) {
    var _url = '/users/user_desert/' + id;
    window.location.href = _url;

}

function initProjectGroup(){
    // 初始化项目分组
    // 根据所选的项目来决定分组
    var project = $("#add_game_project").select2('data')[0].id;

    $("#project_group").select2({
        ajax: {
            url: '/assets/list_project_group/',
            dataType: 'json',
            type: 'POST',
            data: {
                'project': project,
            },
            delay: 250,
            processResults: function (data, params) {
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
            cache: true,
        },
        // minimumResultsForSearch: Infinity,
    });
}

function initModalSelect2(){
    // 初始化select2


    $select2AddGameProject = $("#add_game_project").select2({
        ajax: {
            url: '/assets/list_game_project/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
            processResults: function (data, params) {
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
            cache: true,
        },
        // minimumResultsForSearch: Infinity,
    });

    $select2AddGameProject;
    $select2AddGameProject.on("select2:select", function (e){ log("select2:select", e); });

    initProjectGroup();

    $select2AddGroup = $("#add_group").select2({
        ajax: {
            url: '/assets/list_group/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
            processResults: function (data, params) {
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
            cache: true,
        },
        // minimumResultsForSearch: Infinity,
    });
    $select2AddGroup.on("select2:select", function (e){ log2("select2:select", e); });

    $select2GroupSection = $("#group_section").select2({
        ajax: {
            url: '/users/list_group_section/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page,
                    group: $("#add_group").val(),
                };
            },
            processResults: function (data, params) {
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
            cache: true,
        },
        // minimumResultsForSearch: Infinity,
    });
    

    var $select2Project = $("#filter_project").select2({});
    $select2Project.on("select2:select", function (e){ reload_table("select2:select", e); });

    var $select2ProjectGroup = $("#filter_project_group").select2({});
    $select2ProjectGroup.on("select2:select", function (e){ reload_table("select2:select", e); });

    var $select2Group = $("#filter_group").select2({});
    $select2Group.on("select2:select", function (e){ reload_table("select2:select", e); });

    var $select2IsSuperuser = $("#filter_is_superuser").select2({
        minimumResultsForSearch: Infinity,
    });
    $select2IsSuperuser.on("select2:select", function (e){ reload_table("select2:select", e); });

    var $select2IsActive = $("#filter_is_active").select2({
        minimumResultsForSearch: Infinity,
    });
    $select2IsActive.on("select2:select", function (e){ reload_table("select2:select", e); });

    $select2LDAPGroup = $("#ldap_group").select2({
        ajax: {
            url: '/users/list_ldap_groups/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
            processResults: function (data, params) {
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
            cache: true,
        },
        // minimumResultsForSearch: Infinity,
    });

    $.fn.modal.Constructor.prototype.enforceFocus = function() {};

};


function log(name, evt, className){
    if (name == "select2:select" || name == "select2:select2"){
        initSelect2("project_group", '0', '选择项目分组');
        initProjectGroup();
    }
};


function log2(name, evt, className){
    if (name == "select2:select" || name == "select2:select2"){
        initSelect2("group_section", '0', '部门分组');
    }
};

function reload_table(name, evt, className){
    if (name == "select2:select" || name == "select2:select2"){
        table.ajax.reload();
    }
};

function formatRepo (repo) {
    
    var markup = '<div class="clearfix"><div clas="col-sm-7">' + repo.text + '</div></div>';

    return markup;
};

function formatRepoSelection (repo) {
    return repo.text || repo.id;
};


// $(document).on('hidden.bs.modal', function (e) {
//     clearModalSelect2();
//     initModalSelect2();
// });

$.urlParam = function(name){
    var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
    if (results==null){
       return null;
    }
    else{
       return decodeURIComponent(results[1]) || 0;
    }
}

function pre_filter_username() {
    var username = $.urlParam('username');
    if ( username != null ) {
        table.search(username).draw()
    }
}


$(document).ready(function() {
    var rows_selected = [];
    table = $('#mytable').DataTable( {
        "processing": true,
        "ordering": false,
        "serverSide": true,
        "ajax": {
            'type': 'POST',
            'url': '/users/data_user_list/',
            "data": function(d) {
                d.filter_username = $("#filter_username").val();
                d.filter_first_name = $("#filter_first_name").val();
                d.filter_email = $("#filter_email").val();
                d.filter_project = $("#filter_project").val();
                d.filter_project_group = $("#filter_project_group").val();
                d.filter_group = $("#filter_group").val();
                d.filter_is_superuser = $("#filter_is_superuser").val();
                d.filter_is_active = $("#filter_is_active").val();
            }
        },
        "columns": [
            {"data": null},
            {"data": 'id'},
            {"data": 'username'},
            {"data": 'first_name'},
            {"data": 'email'},
            {"data": 'groups'},
            {"data": 'group_section'},
            {"data": 'game_project_group'},
            {"data": 'is_superuser'},
            {"data": 'is_active'},
            {
              "data": null,
              "orderable": false,
            }
        ],
        // "order": [[1, 'asc']],
        columnDefs: [
                {
                  'targets': 0,
                  'searchable':false,
                  'orderable':false,
                  'className': 'dt-body-center',
                  'render': function (data, type, full, meta){
                   return '<input type="checkbox">';
                  },
                },
                {
                    'targets': 1,
                    'visible': false,
                    'searchable': false
                },
                /*{    
                    'targets': [3, 4],
                    "render": function(data, type, row){
                        return data.split(",").join("<br/>");
                    },
                },*/
                {
                    'targets': 7,
                    'searchable':false,
                    'orderable':false,
                    'className': 'dt-body-left',
                    'render': function (data, type, full, meta){
                        // return '<a href="/assets/game_project_list/?project_name=' + data + '">' + data + '</a>';
                        return data.split(",").join("<br/>");
                    },
                },
                {
                    'targets': 5,
                    'searchable':false,
                    'orderable':false,
                    'className': 'dt-body-left',
                    'render': function (data, type, full, meta){
                        return '<a href="/users/group_list/?name=' + data + '">' + data + '</a>';
                    },
                },
                {
                    targets: 10,
                    render: function (a, b, c, d) {
                        var context =
                        {
                            func: [
                                {"name": "修改", "fn": "edit(\'" + c.id + "\')", "type": "primary"},
                                {"name": "密码", "fn": "passwd(\'" + c.id + "\')", "type": "warning"},
                                {"name": "清除权限", "fn": "clean(\'" + c.id + "\')", "type": "danger"},
                                {"name": "离职", "fn": "desert(\'" + c.id + "\')", "type": "info"},
                            ]
                        };
                        var html = template(context);
                        return html;
                    }
                }
        ],
        "language": {
                "url": "/static/js/i18n/Chinese.json"
        },
    });

    if ( ! $("#is_superuser_object").data('my-object') ) {
        table.column( 10 ).visible(false);
    }

    pre_filter_username();

    $('#chb-all').on('click', function(e){
        var checkbox = document.getElementById('chb-all');
        $('#mytable tbody td').parent().find('input[type="checkbox"]').map(function(i,n){
            var $row = $(this).closest('tr');
            n.checked = checkbox.checked;
            if (checkbox.checked){
              $row.addClass('selected');
              count = getSelectedTable().length;
              makeTitle(str, count);
            }else{
              $row.removeClass('selected');
              count = 0;
              makeTitle(str, count);
            }
        });
    });

    $('#bt-modal-notify').click( function () {
        $("#modal-notify").hide();
    } );

    $('#bt-modal-passwd-notify').click( function () {
        $("#modal-passwd-notify2").hide();
    } );

    $("#reset_project").click(function(event) {
        /* Act on the event */
        initSelect2("add_game_project", '0', '选择项目');
        initSelect2("project_group", '0', '选择项目分组');
    });

    $('#bt-search').click(function(){
        $('#div-search').toggleClass('hide');
    });

    // Handle click on checkbox
    $('#mytable tbody').on('click', 'input[type="checkbox"]', function(e){
        var $row = $(this).closest('tr');

        var data = table.row($row).data();
        var index = $.inArray(data[0], rows_selected);

        if(this.checked && index === -1){
            rows_selected.push(data[0]);
        } else if (!this.checked && index !== -1){
            rows_selected.splice(index, 1);
        }

        if(this.checked){
            $row.addClass('selected');
            makeTitle(str, ++count);
        } else {
            $row.removeClass('selected');
            makeTitle(str, --count);
        }

        // Prevent click event from propagating to parent
        e.stopPropagation();
    });

    initModalSelect2();

    $('#bt-add').click( function () {
        $("#myModalLabel").text("选择用户");
        $("#modal-notify").hide();
        $("#show_id").hide()
        $("#show_ldap_group").show();
        $("#username").val('');
        $("#show_first_name").show();
        $("#first_name").val('');
        $("#email").val('');
        $('input:radio[name=is_superuser]').filter('[value=0]').prop('checked',true);
        $('input:radio[name=is_active]').filter('[value=1]').prop('checked',true);
        initSelect2('add_game_project', '0', '选择项目');
        initSelect2('add_group', '0', '选择部门');
        initSelect2('group_section', '0', '部门分组');
        initSelect2("ldap_group", "0", "选择LDAP部门(不选则不添加LDAP账号)");
        $(".immutable").prop('disabled', false);
        editFlag=false;
        $("#myModal").modal("show");
    } );
    
    $('#bt-save').click( function(){
        var id = $("#id").val();
        var username = $("#username").val();

        if (username == '') {
            $('#lb-msg').text('请输入用户名!');
            $('#modal-notify').show();
            return false;
        }

        var first_name = $("#first_name").val();
        if (first_name == '') {
            $('#lb-msg').text('请输入用户拼音!');
            $('#modal-notify').show();
            return false;
        }

        var email = $("#email").val();

        if (email == '') {
            $('#lb-msg').text('请输入公司邮箱!');
            $('#modal-notify').show();
            return false;
        }

        var group = $("#add_group").select2('data')[0].id;
        if (group == '0') {
            $('#lb-msg').text('请选择部门!');
            $('#modal-notify').show();
            return false;
        }

        var group_section = $("#group_section").val()

        var project_group = $("#project_group").select2('data')[0].id;


        // var listGameProjectId = new Array();
        // $("#add_game_project").select2('data').forEach(function(info,i){ listGameProjectId.push(info.id) });
        var add_game_project = $("#add_game_project").select2('data')[0].id;

        if ( add_game_project != '0' ){
            if ( project_group == '0' ){
                $('#lb-msg').text('你选择了项目，需要选择一个项目分组');
                $('#modal-notify').show();
                return false;
            }
        }

        var is_superuser = $('input[name=is_superuser]:checked').val();

        var is_active = $('input[name=is_active]:checked').val();

        var ldap_group = $("#ldap_group").val();

        var inputIds = {
                'id': id,
                'username': username,
                'first_name': first_name,
                'email': email,
                'group': group,
                'group_section': group_section,
                'project_group': project_group,
                'is_superuser': is_superuser,
                'is_active': is_active,
                'ldap_group': ldap_group,
                'editFlag': editFlag,
            };

        var urls = "/users/add_or_edit_user/";

        var encoded=$.toJSON( inputIds );
        var pdata = encoded;

        $.ajax({
            type: "POST",
            url: urls,
            contentType: "application/json; charset=utf-8",
            data: pdata,
            success: function (data) {
                
                if (data['data']) {
                    table.ajax.reload();
                    $("#myModal").modal("hide");
                }
                else{
                    $('#lb-msg').text(data['msg']);
                    $('#modal-notify').show();
                }
            }
        });
    });

    $("#bt-passwd-save").click( function(){

        var id = $("#id-passwd").val();

        var password = $("#password").val();
        if (password == ''){
            $('#modal-passwd-notify2').show();
            $('#lb-msg-passwd').text('请输入密码!');
            return false;
        }

        var data = {
        'id': id,
        'password': password,
        };

        var encoded = $.toJSON(data);
        var pdata = encoded;

        $.ajax({
            type: "POST",
            url: "/users/passwd_data_user/",
            data: pdata,
            contentType: "application/json; charset=utf-8",
            success: function(data){
                if (data.data){
                    $.toast({
                        text: "修改密码成功", // Text that is to be shown in the toast
                        heading: 'Success', // Optional heading to be shown on the toast
                        icon: 'success', // Type of toast icon
                        showHideTransition: 'slide', // fade, slide or plain
                        allowToastClose: true, // Boolean value true or false
                        hideAfter: 1000, // false to make it sticky or number representing the miliseconds as time after which toast needs to be hidden
                        stack: 5, // false if there should be only one toast at a time or a number representing the maximum number of toasts to be shown at a time
                        position: 'top-center', // bottom-left or bottom-right or bottom-center or top-left or top-right or top-center or mid-center or an object representing the left, right, top, bottom values



                        textAlign: 'left',  // Text alignment i.e. left, right or center
                        loader: true,  // Whether to show loader or not. True by default
                        loaderBg: '#9EC600',  // Background color of the toast loader
                        beforeShow: function () {}, // will be triggered before the toast is shown
                        afterShown: function () {}, // will be triggered after the toat has been shown
                        beforeHide: function () {}, // will be triggered before the toast gets hidden
                        afterHidden: function () {
                            if (data.logout_required){
                                window.location.replace("/user_out");
                            }
                        }  // will be triggered after the toast has been hidden
                    });
                    $("#Modal-passwd").modal("hide");
                    // window.location.replace("/user_login");
                } else {
                    $('#modal-passwd-notify2').show();
                    $('#lb-msg-passwd').text(data.msg);
                    return false;
                }
            },
        });

    });

    $('input.column_filter').on( 'keyup click', function () {
        // filterColumn( $(this).parents('tr').attr('data-column') );
        table.ajax.reload();
    } );

    //删除
    $("#bt-del").confirm({
        //text:"确定删除所选的vip?",
        confirm: function(button){
            var selected = getSelectedTable();

            if (selected.length == 0){
                alert('请选择');
            }else{
                var encoded=$.toJSON( selected );
                var pdata = encoded;
                $.ajax({
                    type: "POST",
                    url: "/users/del_user/",
                    contentType: "application/json; charset=utf-8",
                    data: pdata,
                    success: function (data) {
                        
                        if (data['data']) {
                            table.ajax.reload();
                            makeTitle(str, 0);
                            count = 0;
                        }else{
                            alert(data['msg'])
                            table.ajax.reload();
                            makeTitle(str, 0);
                            count = 0;
                        };
                    }
                });
            }
        },

        cancel: function(button){

        },
        confirmButton: "确定",
        cancelButton: "取消",

    });

    $("#bt-reset").click( function(){
        $(".column_filter").val('')
        $(".filter_select2").val('全部').trigger('change');
        table.ajax.reload();

    } );

    $("#reset_ldap_group").click(function(event) {
        /* Act on the event */
        initSelect2("ldap_group", "0", "选择LDAP部门(不选则不添加LDAP账号)")
    });



} );
