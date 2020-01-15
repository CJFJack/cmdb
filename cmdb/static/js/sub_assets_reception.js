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

var $select2Ctype;
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
    var name = $.urlParam('name');
    var status_code = $.urlParam('status_code');
    var company_id = $.urlParam('company_id');
    var user = $.urlParam('user');

    if ( name !== null & status_code !== null & company_id !==null) {
        var ctype = name.split('-')[0]
        var smodel = name.split('-')[1]

        if ( ctype == '显卡' ){
            $("#filter_graphics").val(smodel).trigger('change');
        } else if ( ctype == 'CPU' ) {
            $("#filter_CPU").val(smodel).trigger('change');
        } else if ( ctype == '主板' ) {
            $("#filter_board").val(smodel).trigger('change');
        } else if ( ctype == '固态硬盘' ) {
            $("#filter_ssd").val(smodel).trigger('change');
        } else if ( ctype == '机械硬盘' ) {
            $("#filter_disk").val(smodel).trigger('change');
        } else if ( ctype == '内存' ) {
            $("#filter_mem").val(smodel).trigger('change');
        }

        $("#filter_status").val(status_code).trigger('change');
        $("#filter_company").val(company_id).trigger('change');
        $("#filter_user").val(user).trigger('change');
        // table.ajax.reload();
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

    $select2Status = $("#filter_status").select2({
        minimumResultsForSearch: Infinity,
    });
    $select2Status.on("select2:select", function (e) { log("select2:select", e); });

    $select2Pos = $("#filter_pos").select2({
        ajax: {
            url: '/it_assets/list_pos/',
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
        // templateResult: formatRepo, // omitted for brevity, see the source of this page
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });
    $select2Pos.on("select2:select", function (e) { log("select2:select", e); });
}


function log(name, evt, className){
    if (name == "select2:select" || name == "select2:select2"){
        table.ajax.reload();

    }
}


$(document).ready(function() {

    initModalSelect2();

    var rows_selected = [];
    table = $('#mytable').DataTable( {
        "processing": true,
        "ordering": false,
        "serverSide": true,
        "ajax": {
            "url": "/it_assets/data_sub_assets_reception/",
            "type": "POST",
            "data": function(d){
                d.filter_CPU = $("#filter_CPU").select2('data')[0].text;
                d.filter_board = $("#filter_board").select2('data')[0].text;
                d.filter_ssd = $("#filter_ssd").select2('data')[0].text;
                d.filter_disk = $("#filter_disk").select2('data')[0].text;
                d.filter_mem = $("#filter_mem").select2('data')[0].text;
                d.filter_graphics = $("#filter_graphics").select2('data')[0].text;
                d.filter_number = $("#filter_number").val();
                d.filter_pos = $("#filter_pos").val();
                d.filter_status = $("#filter_status").val();
                d.filter_user = $("#filter_user").select2('data')[0].text;
                d.filter_company = $("#filter_company").val();
            }
        },
        "columns": [
            {"data": "id"},  // 0
            {"data": "company"},  // 1
            {"data": "ctype"},  // 2
            {"data": 'brand'},  //3
            {"data": 'smodel'},  //4
            {"data": 'status'},  // 5
            {"data": "number"},  // 6
            {"data": "pos"},  // 7
            {"data": "supplier"},  // 8
            {"data": "user"},  // 9
        ],
        "order": [[1, 'asc']],
        columnDefs: [
                {
                    'targets': 0,
                    'visible': false,
                    'searchable': false
                },
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

    $("#bt-reset").click(function(){
        $("#filter_status").val('0').trigger('change');
        $("#filter_number").val('');
        $("#filter_pos").val('0').trigger('change');
        //$("#filter_user").val('');
        $(".filter_select2").val('0').trigger('change');
        table.ajax.reload();
    });



} );
