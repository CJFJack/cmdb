var tpl = $("#tpl").html();
//预编译模板
var template = Handlebars.compile(tpl);

var select2_belongs_to_game_project;
var select2_data_tables_game_project;
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
    // var game_project_id = $('#belongs_to_game_project').select2('data')[0].id;

    // if (game_project_id == '0') {
    //     game_project_id = '';
    // }
    
    $('.game_project_person').select2( {
        ajax: {
            url: '/assets/list_ops_user/',
            dataType: 'json',
            type: 'POST',
            delay: 250,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page,
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
        multiple: true,
        placeholder: '选择值班人员',
    });

};


function initModalSelect2(){
    // 初始化select2
    
    $select2_belongs_to_game_project = $('#belongs_to_game_project').select2( {
        ajax: {
            url: '/assets/list_game_project/',
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
        multiple: true,
        placeholder: '选择游戏项目',
    });
    // $select2_belongs_to_game_project;
    // $select2_belongs_to_game_project.on("select2:select", function (e){ game_project_get_related_person("select2:select", e); });

    $select2_data_tables_game_project = $('#data_tables_game_project').select2( {
        ajax: {
            url: '/assets/list_game_project/',
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
    $select2_data_tables_game_project;
    $select2_data_tables_game_project.on("select2:select", function (e){ reload_data_tables("select2:select", e); });

    init_game_project_person();

    $select2WeekdaysPerson =  $("#filter_weekdays_person").select2();
    $select2WeekdaysPerson.on("select2:select", function (e) { log("select2:select", e); });

    $select2WeekendPerson =  $("#filter_weekend_person").select2();
    $select2WeekendPerson.on("select2:select", function (e) { log("select2:select", e); });

    $select2BelongsToGameProject =  $("#filter_belongs_to_game_project").select2();
    $select2BelongsToGameProject.on("select2:select", function (e) { log("select2:select", e); });

    $.fn.modal.Constructor.prototype.enforceFocus = function() {};
};

function log(name, evt, className){
    if (name == "select2:select" || name == "select2:select2"){
        table.ajax.reload();

    }
}

function reload_data_tables(name, evt, className){
    // 根据选择的项目重新加载值班表
    if (name == "select2:select" || name == "select2:select2"){
        // var data_tables_game_project = $('#data_tables_game_project').select2('data')[0].id;
        table.ajax.reload(null, false);
        // initDataTables();
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
        url: "/assets/get_cmdb_duty_schedule/",
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
            
            var weekdays_value = new Array();
            $("#weekdays_person").html('');
            data.weekdays_person.forEach( function(e, i) {
                $("#weekdays_person").append('<option value="' + e.id + '">' + e.username + '</option>');
                weekdays_value.push(e.id)
            } )
            $("#weekdays_person").select2('val', weekdays_value)

            var weekend_value = new Array();
            $("#weekend_person").html('');
            data.weekend_person.forEach( function(e, i) {
                $("#weekend_person").append('<option value="' + e.id + '">' + e.username + '</option>');
                weekend_value.push(e.id)
            } )
            $("#weekend_person").select2('val', weekend_value)


            // 重新初始化下拉用户select2
            init_game_project_person();

            $("#belongs_to_game_project").attr('disabled', true)

            $("#myModal").modal("show");
        },
        error: function (data) {
            alert('权限拒绝!')
        }
    });

};

function checkBeforeAdd(belongs_to_game_project,start_date,end_date,weekdays_person,weekend_person){
    if (belongs_to_game_project == null){
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
    if (weekdays_person == null){
        $('#lb-msg').text('请选择周一到周五跟进负责人!');
        $('#modal-notify').show();
        return false;
    }
    if (weekend_person == null){
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

function initDataTables(){
    // 初始化datatables

    // var data_tables_game_project = typeof data_tables_game_project !== 'undefined' ? data_tables_game_project : '';
    // var data_tables_game_project = $('#data_tables_game_project').select2('data')[0].id;
    // console.log(data_tables_game_project);

    var mytable = $('#mytable').DataTable( {
        "processing": true,
        "serverSide": true,
        "ordering": false,
        "ajax": {
            "url": "/assets/data_cmdb_duty_schedule/",
            "type": "POST",
            "data": function(d){
                d.filter_belongs_to_game_project = $('#filter_belongs_to_game_project').val();
                d.filter_weekdays_person = $("#filter_weekdays_person").val();
                d.filter_weekend_person = $("#filter_weekend_person").val();
                d.filter_start_date = $("#filter_start_date").val();
                d.filter_end_date = $("#filter_end_date").val();
            },
        },
        "columns": [
            {"data": null},
            {"data": "id"},
            {"data": 'game_project'},
            {"data": 'schedul_date'},
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
                    'targets': [4,5],
                    "render": function(data, type, row){
                        return data.split(",").join("<br/>");
                    },
                },
                {
                    targets: 6,
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
    });

    return mytable;
};


function get_current_date() {
    // 获取当前日期
    var date = new Date();

    // 获取当前月份
    var nowMonth = date.getMonth() + 1;

    // 获取当前是几号
    var strDate = date.getDate();

    // 添加分隔符“-”
    var seperator = "-";

    // 对月份进行处理，1-9月在前面添加一个“0”
    if (nowMonth >= 1 && nowMonth <= 9) {
       nowMonth = "0" + nowMonth;
    }

    // 对月份进行处理，1-9号在前面添加一个“0”
    if (strDate >= 0 && strDate <= 9) {
       strDate = "0" + strDate;
    }

    // 最后拼接字符串，得到一个格式为(yyyy-MM-dd)的日期
    var nowDate = date.getFullYear() + seperator + nowMonth + seperator + strDate;

    return nowDate
}


$(document).ready(function() {

    initModalSelect2();

    var nowDate = get_current_date();

    $("#filter_start_date").val(nowDate)

    var rows_selected = [];

    table = initDataTables();


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

    $(".flatpickr").flatpickr({
        locale: "zh",
        onClose: function(selectedDates, dateStr, instance){
            table.ajax.reload();
        }
    });   


    $('#bt-add').click( function () {
        $("#belongs_to_game_project").attr('disabled', false)
        $("#myModalLabel").text("新增值班安排");
        $("#modal-notify").hide();
        $("#show_id").hide();
        // initSelect2('belongs_to_game_project', '0', '选择项目');

        $("#belongs_to_game_project").val('0').trigger('change');
        $(".game_project_person").val('0').trigger('change');
        
        $("#start_date").val('');
        $("#end_date").val('');
        
        editFlag=false;
        $("#myModal").modal("show");

    } );
    

    $('#bt-save').click( function(){
        var id = $("#id").val();
        var belongs_to_game_project = $("#belongs_to_game_project").val()
        var start_date = $("#start_date").val();
        var end_date = $("#end_date").val();
        var weekdays_person = $("#weekdays_person").val()
        var weekend_person = $("#weekend_person").val()

        if (editFlag){
            var urls = "/assets/edit_data_cmdb_duty_schedule/";
        }else{
            var urls = "/assets/add_data_cmdb_duty_schedule/";
        }

        var inputIds = {
                'id': id,
                'belongs_to_game_project': belongs_to_game_project,
                'start_date': start_date,
                'end_date': end_date,
                'weekdays_person': weekdays_person,
                'weekend_person': weekend_person,
            };
        
        if ( !checkBeforeAdd(belongs_to_game_project,start_date,end_date,weekdays_person,weekend_person) ){
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
                    table.ajax.reload(null, false);
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
                    url: "/assets/del_data_cmdb_duty_schedule/",
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

    $('#bt-reset').click(function(){
        $(".filter_select2").val('全部').trigger('change')
        $(".flatpickr-input").val('');
        table.ajax.reload()
    });

} );
