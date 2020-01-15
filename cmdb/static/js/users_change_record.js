var asInitVals = new Array();

$(document).ready(function () {
    var mytable = $('#mytable').dataTable({
        "processing": true,
        "serverSide": true,
        "ordering": false,
        "ajax": {
            "url": "/users/data_user_change_record/",
            "type": "POST",
            "data": function (d) {
                d.filter_create_user = $('#search_create_user').val().trim();
                d.filter_change_obj = $('#search_change_obj').val().trim();
            }
        },
        "columns": [
            {"data": "create_time"}, //0
            {"data": "create_user"},  // 1
            {"data": "change_obj"},  // 2
            {"data": "type"},  // 3
            {"data": "remark"},  // 4
        ],
        responsive: true,
        language: {
            "url": "/static/js/i18n/Chinese.json"
        },
        columnDefs: [
            {
                'targets': 4,
                "render": function (data, type, row) {
                    return data.split(",").join("<br/>");
                },
            },
        ]
    });

    // 筛选操作人
    $("#search_create_user").keyup(function () {
        /* Filter on the column (the index) of this element */
        mytable.fnFilter(this.value, 1);
    });

    // 筛选操作对象
    $("#search_change_obj").keyup(function () {
        /* Filter on the column (the index) of this element */
        mytable.fnFilter(this.value, 2);
    });

});