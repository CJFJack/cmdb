var tpl = $("#tpl").html();
//预编译模板
var template = Handlebars.compile(tpl);

var select2_belongs_to_game_project;
var select2_tuesday_person;
var select2_thursday_person;
var select2_weekdays_person;
var select2_weekend_person;

var select2_game_project_person;

var editFlag;

// 删除提示
var str = "确定删除选中的值班列表?";
var count=0;

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
        escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
        // minimumInputLength: 1,
        templateResult: formatRepo, // omitted for brevity, see the source of this page
        templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });

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
        escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
        // minimumInputLength: 1,
        templateResult: formatRepo, // omitted for brevity, see the source of this page
        templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });
    $select2_belongs_to_game_project;
    $select2_belongs_to_game_project.on("select2:select", function (e){ game_project_get_related_person("select2:select", e); });


    /*$select2_game_project_person = $('.game_project_person').select2( {
        ajax: {
            url: '/cmdb/list_user/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page,
                    game_project_id: $('#belongs_to_game_project').select2('data')[0].id,
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
        escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
        // minimumInputLength: 1,
        templateResult: formatRepo, // omitted for brevity, see the source of this page
        templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });*/

    init_game_project_person();

    $.fn.modal.Constructor.prototype.enforceFocus = function() {};


};

function game_project_get_related_person(name, evt, className){
    // 当选择的游戏项目改变了以后根据游戏项目
    // 重新初始化相关的值班人员
    if (name == "select2:select" || name == "select2:select2"){
        var game_project_id = $('#belongs_to_game_project').select2('data')[0].id;
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
                cache: true,
            },
            escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
            // minimumInputLength: 1,
            templateResult: formatRepo, // omitted for brevity, see the source of this page
            templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
        });
        $(".game_project_person").val('0').trigger("change");
    }
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
        url: "/cmdb/get_cmdb_duty_schedule/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function(data){
            $("#myModalLabel").text("修改值班安排表");
            $("#modal-notify").hide();
            $("#id").val(id);
            $("#show_id").hide();

            // Fill data

            initSelect2('belongs_to_game_project', data.game_project_id, data.game_project);
            $("#start_date").val(data.start_date);
            $("#end_date").val(data.end_date);
            initSelect2('tuesday_person', data.tuesday_person_id, data.tuesday_person);
            initSelect2('thursday_person', data.thursday_person_id, data.thursday_person);
            initSelect2('weekdays_person', data.weekdays_person_id, data.weekdays_person);
            initSelect2('weekend_person', data.weekend_person_id, data.weekend_person);

            // 重新初始化下拉用户select2
            init_game_project_person();

            $("#myModal").modal("show");
        },
    });

};

function checkBeforeAdd(belongs_to_game_project,start_date,start_date,tuesday_person,thursday_person,weekdays_person,weekend_person){
    if (belongs_to_game_project == '0'){
        $('#lb-msg').text('请选择游戏项目!');
        $('#modal-notify').show();
        return false;
    }

    if (start_date == ''){
        $('#lb-msg').text('选择开始值班时间!');
        $('#modal-notify').show();
        return false;
    }
    if (end_date == '') {
        $('#lb-msg').text('结束值班时间!');
        $('#modal-notify').show();
        return false;
    }
    if (start_date > end_date){
        $('#lb-msg').text('开始时间不能大于结束时间!');
        $('#modal-notify').show();
        return false;
    }
    if (tuesday_person == '0'){
        $('#lb-msg').text('请选择周二更新负责人!');
        $('#modal-notify').show();
        return false;
    }
    if (thursday_person == '0'){
        $('#lb-msg').text('请选择周四更新负责人!');
        $('#modal-notify').show();
        return false;
    }
    if (weekdays_person == '0'){
        $('#lb-msg').text('请选择周一到周五跟进负责人!');
        $('#modal-notify').show();
        return false;
    }
    if (weekend_person == '0'){
        $('#lb-msg').text('请选择周六日值班负责人!');
        $('#modal-notify').show();
        return false;  
    }
    return true;
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


$(document).ready(function() {
    var rows_selected = [];
    table = $('#mytable').DataTable( {
        "processing": true,
        "ordering": false,
        "ajax": "/cmdb/data_cmdb_duty_schedule",
        "columns": [
            {"data": null},
            {"data": "id"},
            {"data": 'game_project'},
            {"data": 'schedul_date'},
            {"data": "tuesday_person"},
            {"data": "thursday_person"},
            {"data": "weekdays_person"},
            {"data": "weekend_person"},
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
                {
                    targets: 8,
                    render: function (a, b, c, d) {
                        var context =
                        {
                            func: [
                                {"name": "修改", "fn": "edit(\'" + c.id + "\')", "type": "primary"},
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
        // 'rowCallback': function(row, data, dataIndex){
        //     // If row ID is in list of selected row IDs
        //     if($.inArray(data[0], rows_selected) !== -1){
        //     $(row).find('input[type="checkbox"]').prop('checked', true);
        //     $(row).addClass('selected');
        //     }
        // },
    });

    // Handle click on table cells
    // $('#mytable tbody').on('click', 'td', function(e){
    //     $(this).parent().find('input[type="checkbox"]').trigger('click');
    // });

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

    $('#start_date').Zebra_DatePicker({
    });
    $('#end_date').Zebra_DatePicker({
    });

    initModalSelect2();
    


    $('#bt-add').click( function () {
        $("#myModalLabel").text("新增值班安排");
        $("#modal-notify").hide();
        $("#show_id").hide();
        initSelect2('belongs_to_game_project', '0', '选择项目');

        $(".game_project_person").val('0').trigger('change');
        
        $("#start_date").val('');
        $("#end_date").val('');
        
        editFlag=false;
        $("#myModal").modal("show");

    } );
    

    $('#bt-save').click( function(){
        var id = $("#id").val();
        var belongs_to_game_project = $("#belongs_to_game_project").select2('data')[0].id;
        var start_date = $("#start_date").val();
        var end_date = $("#end_date").val();
        var tuesday_person = $("#tuesday_person").select2('data')[0].id;
        var thursday_person = $("#thursday_person").select2('data')[0].id;
        var weekdays_person = $("#weekdays_person").select2('data')[0].id;
        var weekend_person = $("#weekend_person").select2('data')[0].id;

        if (editFlag){
            var urls = "/cmdb/edit_data_cmdb_duty_schedule/";
        }else{
            var urls = "/cmdb/add_data_cmdb_duty_schedule/";
        }

        var inputIds = {
                'id': id,
                'belongs_to_game_project': belongs_to_game_project,
                'start_date': start_date,
                'end_date': end_date,
                'tuesday_person': tuesday_person,
                'thursday_person':thursday_person,
                'weekdays_person': weekdays_person,
                'weekend_person': weekend_person,
            };
        
        if ( !checkBeforeAdd(belongs_to_game_project,start_date,start_date,tuesday_person,thursday_person,weekdays_person,weekend_person) ){
            return false;
        }

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
                }else{
                    $('#lb-msg').text(data['msg']);
                    $('#modal-notify').show();
                };
            },
        });
    });

    $("#bt-del").confirm({
        //text:"确定删除所选的主机?",
        confirm: function(button){
            var selected = getSelectedTable();

            if (selected.length == 0){
                alert('请选择');
            }else{
                var encoded=$.toJSON( selected );
                var pdata = encoded;
                $.ajax({
                    type: "POST",
                    url: "/cmdb/del_data_cmdb_duty_schedule/",
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

    $('#bt-search').click(function(){
        $('#div-search').toggleClass('hide');
    });

} );
