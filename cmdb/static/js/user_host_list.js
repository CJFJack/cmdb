// 修改之前的数据
var origin_data;

var table;
var editFlag;
var deviceFlag;
var tpl = $("#tpl").html();
//预编译模板
var template = Handlebars.compile(tpl);

var str = "确定删除选中的资产?";
var count=0;

var $select2Status;
var $select2Pos;

function filterColumn ( i ) {
    $('#mytable').DataTable().column( i ).search(
        $('#col'+i+'_filter').val(),
        $('#col'+i+'_regex').prop('checked'),
        $('#col'+i+'_smart').prop('checked')
    ).draw();
}


$.urlParam = function(name){
    var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
    if (results==null){
       return null;
    }
    else{
       return decodeURIComponent(results[1]) || 0;
    }
}

function preFilter(){
    var filter_r_status = $.urlParam('filter_r_status');
    var filter_t_status = $.urlParam('filter_t_status');
    var filter_room = $.urlParam('filter_room');
    var filter_game_project = $.urlParam('filter_game_project');
    var filter_group = $.urlParam('filter_group');

   if ( filter_r_status !== null ) {
        $("#filter_r_status").val(filter_r_status).trigger('change');
   }

   if ( filter_t_status !== null ) {
        $("#filter_t_status").val(filter_t_status).trigger('change');
   }

   if ( filter_room !== null ) {
        $("#filter_room").val(filter_room).trigger('change');
   }

   if ( filter_game_project !== null ) {
        $("#filter_game_project").val(filter_game_project).trigger('change');
   }

   if ( filter_group !== null ) {
        $("#filter_group").val(filter_group).trigger('change');
   }
}


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

function initModalSelect2(){

    $(".filter_select2").select2({
        // minimumResultsForSearch: Infinity,
    }).on("select2:select", function (e) { table.ajax.reload(); });

}

$(document).ready(function() {

    initModalSelect2();

    var rows_selected = [];
    table = $('#mytable').DataTable( {
        "processing": true,
        "ordering": false,
        "serverSide": true,
        "ajax": {
            "url": "/assets/data_user_host_list/",
            "type": "POST",
            "data": function(d){
                d.filter_username = $("#filter_username").select2('data')[0].id;
                d.filter_host = $("#filter_host").select2('data')[0].id;
                d.filter_internal_ip = $("#filter_internal_ip").val();
                d.filter_telecom_ip = $("#filter_telecom_ip").val();
                d.filter_unicom_ip = $("#filter_unicom_ip").val();
                d.filter_start_time = $("#filter_start_time").val();
                d.filter_end_time = $("#filter_end_time").val();
                d.filter_t_status = $("#filter_t_status").select2('data')[0].id;
                d.filter_r_status = $("#filter_r_status").select2('data')[0].id;
                d.filter_v_status = $("#filter_v_status").select2('data')[0].id;
                d.filter_game_project = $("#filter_game_project").select2('data')[0].id;
                d.filter_room = $("#filter_room").select2('data')[0].id;
                d.filter_group = $("#filter_group").select2('data')[0].id;
            }
        },
        "columns": [
            {"data": "id"},  // 0
            {"data": 'user'},  //1
            {"data": 'host'},  //1
            {"data": 'host_status'},  //1
            {"data": 'ip_info'},
            {"data": "start_time"},  // 5
            {"data": "end_time"}, // 6
            {"data": "temporary"},  // 7
            {"data": "is_root"},  // 8
            {"data": "is_valid"},  // 8
        ],
        "order": [[1, 'asc']],
        columnDefs: [
                {
                    'targets': 0,
                    'visible': false,
                    'searchable': false
                },
                {    
                    'targets': 1,
                    "render": function(data, type, row){
                        return '<a href="/users/user_list/?username=' + data + '">' + data + '</a>'
                    },
                },
                {    
                    'targets': 2,
                    "render": function(data, type, row){
                        return '<a href="/assets/host/?host_identifier=' + data + '">' + data + '</a>'
                    },
                },
                {
                    'targets': 3,
                    'searchable':false,
                    'orderable':false,
                    'className': 'dt-body-left',
                    'render': function (data, type, full, meta){
                        if (data == '已归还'){
                            return '<span class="label label-default">' + data + '</span>';
                        }
                        else {
                            return '<span class="label label-success">' + data + '</span>';
                        }
                    },
                },
                {
                    'targets': 7,
                    'searchable':false,
                    'orderable':false,
                    'className': 'dt-body-left',
                    'render': function (data, type, full, meta){
                        if (data == '永久'){
                            return '<span class="label label-primary">' + data + '</span>';
                        }
                        else {
                            return '<span class="label label-danger">' + data + '</span>';
                        }
                    },
                },
                {    
                    'targets': 4,
                    "render": function(data, type, row){
                        return data.split(",").join("<br/>");
                    },
                },
                {
                    'targets': 9,
                    'searchable':false,
                    'orderable':false,
                    'className': 'dt-body-left',
                    'render': function (data, type, full, meta){
                        if (data == '有效'){
                            return '<span class="label label-success">' + data + '</span>';
                        }
                        else {
                            return '<span class="label label-default">' + data + '</span>';
                        }
                    },
                },
                /*{    
                    'targets': [5,6,7,8,9,10],
                    "render": function(data, type, row){
                        return data.split(",").join("<br/>");
                    },
                },*/
        ],
        "language": {
                "url": "/static/js/i18n/Chinese.json"
        },
    });

    preFilter();


    $(':checkbox.toggle-visiable').on( 'click', function (e) {
        //e.preventDefault();
 
        // Get the column API object
        var is_checked = $(this).is(':checked');
        var column = table.column( $(this).attr('value') );
        // table.ajax.reload();
        column.visible( is_checked );
    } );

    $('#bt-modal-notify').click( function () {
        $("#modal-notify").hide();
    } );

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

    $('#bt-search').click(function(){
        $('#div-search').toggleClass('hide');
    });

    $('input.column_filter').on( 'keyup click', function () {
        // filterColumn( $(this).parents('tr').attr('data-column') );
        table.ajax.reload();
    } );

    $("#bt-reset").click( function(){
        // 重置高级搜索
        $("#filter_username").val('0').trigger('change');
        $("#filter_host").val('0').trigger('change');
        $(".column_filter").val('');
        $("#filter_t_status").val('100').trigger('change');
        $("#filter_r_status").val('100').trigger('change');
        $("#filter_v_status").val('100').trigger('change');
        $("#filter_game_project").val('0').trigger('change');
        $("#filter_room").val('0').trigger('change');
        $("#filter_group").val('0').trigger('change');

        table.ajax.reload();

    } );

    $("#bt-download").click( function(){
        $.ajax({
            type: "GET",
            url: "/it_assets/download/",
            contentType: "application/json; charset=utf-8",
            beforeSend: function(){
                $("#myModal").modal("show");
                $("#modal-footer").hide();
                $("#show-msg").hide();
                $("#load").show();
            },
            success: function (data) {
                $("#load").hide();
                $("#modal-footer").show();
                $("#load-msg").text(data.data);
                $("#show-msg").show();
                $("#myModal").modal("hide");
                var file_name = data.data;
                var download_url = '/downloads/' + file_name;
                window.location = download_url;
                
            },
            error: function(){
                $("#load").hide();
                $("#modal-footer").show();
                $("#load-msg").text('下载失败');
                $("#show-msg").show();
            }
        });
    } )


} );
