var tpl = $("#tpl").html();
//预编译模板
var template = Handlebars.compile(tpl);

var select2_project;

var editFlag;

function initModalSelect2() {
    // 初始化select2

    $select2_project = $('#project').select2({
        /*ajax: {
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
        },*/
        // minimumResultsForSearch: Infinity,
        // escapeMarkup: function (markup) { return markup; }, // let our custom formatter work
        // minimumInputLength: 1,
        // templateResult: formatRepo, // omitted for brevity, see the source of this page
        // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    });
    $select2_project;
    $select2_project.on("select2:select", function (e) {
        reload_data_tables("select2:select", e);
    });


    $.fn.modal.Constructor.prototype.enforceFocus = function () {
    };
};


function reload_data_tables(name, evt, className) {
    // 根据选择的项目重新加载值班表
    if (name == "select2:select" || name == "select2:select2") {
        // var data_tables_game_project = $('#data_tables_game_project').select2('data')[0].id;
        table.ajax.reload();
        // initDataTables();
    }
};

function edit(id) {
    var redirect_url = '/myworkflows/myworkflow_history?id=' + id;
    window.location.href = redirect_url;
};


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

function initDataTables() {
    // 初始化datatables

    // var data_tables_game_project = typeof data_tables_game_project !== 'undefined' ? data_tables_game_project : '';
    // var data_tables_game_project = $('#data_tables_game_project').select2('data')[0].id;
    // console.log(data_tables_game_project);

    var mytable = $('#mytable').DataTable({
        "processing": true,
        "serverSide": true,
        "ordering": false,
        "ajax": {
            "url": "/myworkflows/data_version_update_summarize/",
            "type": "POST",
            "data": function (d) {
                d.project = $('#project').select2('data')[0].id;
            },
        },
        "columns": [
            {"data": null},
            {"data": "id"},
            {"data": 'project'},
            {"data": 'create_time'},
            {"data": "creator"},
            {"data": "applicant"},
            {"data": "title"},
            {"data": "current_state"},
            {"data": "state_value"},
            {"data": "handle_status"},
            {"data": "is_valid"},
            {
                "data": null,
                "orderable": false,
            }
        ],
        // "order": [[1, 'asc']],
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
                'targets': 1,
                'visible': false,
                'searchable': false
            },
            {
                targets: 9,
                render: function (a, b, c, d) {
                    if (c.handle_status == '已处理') {
                        return '<label class="label label-success">' + c.handle_status + '</label>'
                    }
                    else if (c.handle_status == '故障中') {
                        return '<label class="label label-danger">' + c.handle_status + '</label>'
                    }
                    else {
                        return '<label class="label label-default">' + c.handle_status + '</label>'
                    }
                }
            },
            {
                targets: 10,
                render: function (a, b, c, d) {
                    if (c.is_valid == '有效') {
                        return '<label class="label label-success">' + c.is_valid + '</label>'
                    }
                    else {
                        return '<label class="label label-danger">' + c.is_valid + '</label>'
                    }
                }
            },
            {
                targets: 11,
                render: function (a, b, c, d) {
                    var context =
                        {
                            func: [
                                {"name": "查看", "fn": "edit(\'" + c.id + "\')", "type": "primary"},
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


$(document).ready(function () {

    initModalSelect2();


    var rows_selected = [];

    table = initDataTables();


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

    $('#bt-search').click(function () {
        $('#div-search').toggleClass('hide');
    });

    $('#bt-reset').click(function () {
        $('#project').val('0').trigger('change');
        table.ajax.reload();
    });

});
