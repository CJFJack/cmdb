// 修改之前的数据
var origin_data;

var table;
var editFlag;
var deviceFlag;
var tpl = $("#tpl").html();
//预编译模板
var template = Handlebars.compile(tpl);

var str = "确定删除选中的资产?";
var count = 0;

var $select2Event;
var $select2Ctype;
var $select2Pos;

function filterColumn(i) {
    $('#mytable').DataTable().column(i).search(
        $('#col' + i + '_filter').val(),
        $('#col' + i + '_regex').prop('checked'),
        $('#col' + i + '_smart').prop('checked'),
    ).draw();
}

function initModalSelect2() {
    // 初始化select2
    $select2Event = $("#filter_event").select2({
        minimumResultsForSearch: Infinity,
    });

    $select2Event.on("select2:select", function (e) {
        log("select2:select", e);
    });

    $(".filter_select2").select2({
        // minimumResultsForSearch: Infinity,
    }).on("select2:select", function (e) {
        table.ajax.reload();
    });

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
            cache: false,
        },
        //minimumResultsForSearch: Infinity,
        escapeMarkup: function (markup) {
            return markup;
        }, // let our custom formatter work
        // minimumInputLength: 1,
        // templateResult: formatRepo, // omitted for brevity, see the source of this page
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });
    $select2Pos.on("select2:select", function (e) {
        log("select2:select", e);
    });

    $.fn.modal.Constructor.prototype.enforceFocus = function () {
    };

};


function log(name, evt, className) {
    if (name == "select2:select" || name == "select2:select2") {
        table.ajax.reload();

    }
}


function formatRepo(repo) {

    var markup = '<div class="clearfix"><div clas="col-sm-7">' + repo.text + '</div></div>';

    return markup;
};

function formatRepoSelection(repo) {
    return repo.text || repo.id;
};


// $(document).on('hidden.bs.modal', function (e) {
//     clearModalSelect2();
//     initModalSelect2();
// });


$(document).ready(function () {
    var rows_selected = [];
    table = $('#mytable').DataTable({
        "processing": true,
        "ordering": false,
        "serverSide": true,
        "ajax": {
            "url": "/it_assets/data_assets_trace/",
            "type": "POST",
            "data": function (d) {
                d.filter_event = $("#filter_event").select2('data')[0].id;
                d.filter_assets_number = $("#filter_assets_number").val();
                d.filter_name = $("#filter_name").val();
                d.filter_CPU = $("#filter_CPU").select2('data')[0].text;
                d.filter_board = $("#filter_board").select2('data')[0].text;
                d.filter_ssd = $("#filter_ssd").select2('data')[0].text;
                d.filter_disk = $("#filter_disk").select2('data')[0].text;
                d.filter_mem = $("#filter_mem").select2('data')[0].text;
                d.filter_graphics = $("#filter_graphics").select2('data')[0].text;
                d.filter_number = $("#filter_number").val();
                d.filter_etime = $("#filter_etime").val();
                d.filter_log_user = $("#filter_log_user").select2('data')[0].text;
                d.filter_pos = $("#filter_pos").select2('data')[0].id;
                d.filter_user = $("#filter_user").select2('data')[0].text;
                d.filter_purchase = $("#filter_purchase").select2('data')[0].id;
                d.filter_price = $("#filter_price").val();
            }
        },
        "columns": [
            {"data": "id"},  // 0
            {"data": 'event'},  //1
            {"data": 'assets'},  //2
            {"data": 'name'},  //3
            {"data": 'smodel'},  //4
            {"data": 'number'},  //5
            {"data": 'etime'},  // 6
            {"data": "log_user"},  // 7
            {"data": "pos"},  // 8
            {"data": "user"},  // 9
            {"data": "purchase"},  // 10
            {"data": "price"},  // 11
            {"data": "pre_user"},  // 12
            {"data": "change_remark"} //13
        ],
        "order": [[1, 'asc']],
        columnDefs: [
            /*{
                'targets': 0,
                'visible': false,
                'searchable': false
            },*/
            {
                'targets': [13],
                'width': "20%",
                'searchable': true
            },
        ],
        "language": {
            "url": "/static/js/i18n/Chinese.json"
        },
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

    initModalSelect2();

    $('#bt-search').click(function () {
        $('#div-search').toggleClass('hide');
    });

    $('input.column_filter').on('keyup click', function () {
        // filterColumn( $(this).parents('tr').attr('data-column') );
        table.ajax.reload();
    });

    $("#bt-reset").click(function () {
        $("#filter_event").val('100').trigger('change');
        $("#filter_assets_number").val('');
        $(".filter_select2").val('0').trigger('change');
        $("#filter_number").val('');
        $("#filter_etime").val('');
        //$("#filter_log_user").text('');
        $("#filter_pos").val('0').trigger('change');
        //$("#filter_user").text('');
        $("#filter_purchase").val('100').trigger('change');
        $("#filter_price").val('');
        table.ajax.reload();

    })


});
