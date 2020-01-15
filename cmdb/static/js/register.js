
var $select2AddGroup;
var $select2AddGameProject;
var $select2ProjectGroup;


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
            url: '/assets/list_register_group/',
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
                            is_public: item.is_public,
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

    $select2AddGroup;
    $select2AddGroup.on("select2:select", function (e){ hide_project("select2:select", e); });

    $.fn.modal.Constructor.prototype.enforceFocus = function() {};

};


function log(name, evt, className){
    if (name == "select2:select" || name == "select2:select2"){
        initSelect2("project_group", '0', '选择项目分组');
        initProjectGroup();
    }
};


function hide_project(name, evt, className){
    if (name == "select2:select" || name == "select2:select2"){
        var is_public = $("#add_group").select2('data')[0].is_public;

        // 公共部门的，可以不选项目和项目分组
        if (is_public){
            $(".show_project_group").hide();
        } else {
            $(".show_project_group").show();
        }
    }
}



$(document).ready(function() {
   
    initModalSelect2();

    $("#upload-notify").hide();

    $("#register").click( function(){
        var username = $("#username").val();
        if ( $.trim(username) == "" ){
            $("#upload-notify").show();
            $("#lb-msg-upload").text('用户中文名不能为空');
            return false;
        }

        var first_name = $("#first_name").val();
        if ( $.trim(first_name) == "" ){
            $("#upload-notify").show();
            $("#lb-msg-upload").text('用户英文名不能为空');
            return false;
        }

        var is_public = $("#add_group").select2('data')[0].is_public;

        var group = $("#add_group").select2('data')[0].id;
        if (group == '0'){
            $("#upload-notify").show();
            $("#lb-msg-upload").text('请选择部门');
            return false;
        }

        var password = $("#password").val();
        if ( $.trim(password) == "" ){
            $("#upload-notify").show();
            $("#lb-msg-upload").text('密码不能为空');
            return false;
        }

        if (is_public){
            var inputIds = {
                'username': username,
                'first_name': first_name,
                'group': group,
                'password': password,
            };

        } else {
            $(".show_project_group").show();

            var game_project = $("#add_game_project").select2('data')[0].id;
            if (game_project == '0'){
                $("#upload-notify").show();
                $("#lb-msg-upload").text('请选择游戏项目');
                return false;
            }

            var project_group = $("#project_group").select2('data')[0].id;
            if (project_group == '0'){
                $("#upload-notify").show();
                $("#lb-msg-upload").text('请选择项目分组');
                return false;
            }

            var inputIds = {
                'username': username,
                'first_name': first_name,
                'group': group,
                'password': password,
                'game_project': game_project,
                'project_group': project_group,
            };
        }

        var urls = "/user_register/";

        var encoded=$.toJSON( inputIds );
        var pdata = encoded;

        $.ajax({
            type: "POST",
            url: urls,
            contentType: "application/json; charset=utf-8",
            data: pdata,
            success: function (data) {
                
                if (data['data']) {
                    window.location.replace('/user_login/')
                }
                else{
                    $("#upload-notify").show();
                    $("#lb-msg-upload").text(data.msg);
                }
            }
        });
    } );


} );
