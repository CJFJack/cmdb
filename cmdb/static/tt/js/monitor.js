var calendar;

var select2_belongs_to_game_project;

var select2_game_project_person;

var editFlag;

function init_game_project_person(){
    // 根据选择的游戏项目来选择相应的负责人
    var game_project_id = $('#belongs_to_game_project').select2('data')[0].id;

    if (game_project_id == '0') {
        game_project_id = '';
    }
    
    $('.game_project_person').select2( {
        ajax: {
            url: '/cmdb/list_user/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page,
                    game_project_id: game_project_id,
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
        // minimumResultsForSearch: Infinity,
        // escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
        // minimumInputLength: 1,
        // templateResult: formatRepo, // omitted for brevity, see the source of this page
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });

};

function game_project_get_related_person(name, evt, className){
    // 当选择的游戏项目改变了以后根据游戏项目
    // 重新初始化相关的值班人员
    if (name == "select2:select" || name == "select2:select2"){
        init_game_project_person();
        $(".game_project_person").val('0').trigger("change");
    }
};


function initModalSelect2(){
    // 初始化select2
    
    $select2_belongs_to_game_project = $('#belongs_to_game_project').select2( {
        ajax: {
            url: '/cmdb/list_game_project/',
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
        //minimumResultsForSearch: Infinity,
        // escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
        // minimumInputLength: 1,
        // templateResult: formatRepo, // omitted for brevity, see the source of this page
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });
    $select2_belongs_to_game_project;
    $select2_belongs_to_game_project.on("select2:select", function (e){ game_project_get_related_person("select2:select", e); });

    init_game_project_person();

    $.fn.modal.Constructor.prototype.enforceFocus = function() {};


};


$(document).ready(function() {

    calendar = $('#calendar').fullCalendar({
        // put your options and callbacks here
        firstDay: 1,

        dayClick: function(date, allDay, jsEvent, view) {
            
            $("#myModalLabel").text("新建事件");
            $("#modal-notify").hide();
            $("#show_id").hide();
            initSelect2('belongs_to_game_project', '0', '选择项目');
            $(".game_project_person").val('0').trigger('change');
            $("#start").val('');
            $("#end").val('');
            $("#myModal").modal("show");
            editFlag = false;
        },

        events: {
            url: '/cmdb/data_cmdb_fullcalendar/',
            type: 'POST',
            cache: false,
            /*data: {
                custom_param1: 'something',
                custom_param2: 'somethingelse'
            },*/
            error: function() {
                alert('there was an error while fetching events!');
            },
        },


        eventClick: function(calEvent, jsEvent, view) {

            editFlag = true;

            var data = {
                'id': calEvent.id,
            };
            
            var encoded = $.toJSON(data);
            var pdata = encoded;

            $.ajax({
                type: "POST",
                url: "/cmdb/get_cmdb_fullcalendar/",
                data: pdata,
                contentType: "application/json; charset=utf-8",
                success: function(data){
                    $("#myModalLabel").text("修改值班安排表");
                    $("#modal-notify").hide();
                    $("#id").val(data.id);
                    $("#show_id").hide();

                    // Fill data

                    initSelect2('belongs_to_game_project', data.game_project_id, data.game_project);
                    $("#start").val(data.start);
                    $("#end").val(data.end);
                    initSelect2('related_user', data.related_user_id, data.related_user);

                    // 重新初始化下拉用户选择select2
                    init_game_project_person();

                    $("#myModal").modal("show");
                },
            });

        },

    });

    initModalSelect2();

    $('#start').Zebra_DatePicker({
    });
    $('#end').Zebra_DatePicker({
    });

    $("#bt-save").click( function(){
        var id = $("#id").val();

        // 没有选择游戏项目
        var belongs_to_game_project = $("#belongs_to_game_project").select2('data')[0].id;
        if (belongs_to_game_project == '0'){
            $('#lb-msg').text('请选择游戏项目!');
            $('#modal-notify').show();
            return false;
        }

        // 没有选择负责人
        var related_user = $("#related_user").select2('data')[0].id;
        if (related_user == '0'){
            $('#lb-msg').text('请选择负责人!');
            $('#modal-notify').show();
            return false;
        }
        
        var start = $("#start").val();
        var end = $("#end").val();

        if (start > end) {
            $('#lb-msg').text('开始时间不能大于结束时间!');
            $('#modal-notify').show();
            return false;
        }

        if (editFlag){
            var urls = "/cmdb/edit_data_fullcalendar/";
        } else {
            var urls = "/cmdb/add_data_fullcalendar/";
        }
        
        
        var inputIds = {
                'id': id,
                'belongs_to_game_project': belongs_to_game_project,
                'related_user': related_user,
                'start': start,
                'end': end,
            };
        var encoded=$.toJSON( inputIds );
        var pdata = encoded;

        $.ajax({
            type: "POST",
            url: urls,
            contentType: "application/json; charset=utf-8",
            data: pdata,
            success: function (data) {
                
                if (data['data']) {
                    calendar.fullCalendar('refetchEvents');
                    $("#myModal").modal("hide");
                }else{
                    $('#lb-msg').text(data['msg']);
                    $('#modal-notify').show();
                };
            },
        });
    } );

    $("#bt-del").click( function(){
        var data = [$("#id").val()];
        
        var encoded = $.toJSON(data);
        var pdata = encoded;

        $.ajax({
            type: "POST",
            url: "/cmdb/del_data_cmdb_fullcalendar/",
            data: pdata,
            contentType: "application/json; charset=utf-8",
            success: function(data){
                if (data['data']) {
                    calendar.fullCalendar('refetchEvents');
                    $("#myModal").modal("hide");
                }
            },
        });
    } );

});