var table;
var editFlag;
var tpl = $("#tpl").html();
//预编译模板
var template = Handlebars.compile(tpl);

// 修改之前的数据
var origin_data;

var str = "确定删除选中的游戏项目?";
var count = 0;
var is_superuser = $("#is_superuser").val();

var $select2_status;

function checkBeforeAdd(project_name, project_name_en) {
    if (project_name == '') {
        $('#lb-msg').text('请输入项目中文名称!');
        $('#modal-notify').show();
        return false;
    }

    if (project_name_en == '') {
        $('#lb-msg').text('请输入项目英文名称!');
        $('#modal-notify').show();
        return false;
    }

    return true;
};

function apply(id) {
    var redirect_url = '/myworkflows/workflow_template?workflow=' + id;
    window.location.href = redirect_url;
};


function doc(id) {
    var redirect_url = '/myworkflows/help_doc?workflow=' + id;
    window.location.href = redirect_url;
}


function initModalSelect2() {
    $select2_status = $("#status").select2({
        minimumResultsForSearch: Infinity,
    });
};

$(document).ready(function () {

    var rows_selected = [];
    table = $('#mytable').DataTable({
        "processing": true,
        "ordering": false,
        //"serverSide": true,
        "ajax": "/myworkflows/data_workflow_list/",
        "pageLength": 50,
        "columns": [
            {"data": "id"},
            {"data": "name"},
            {"data": "describtion"},
            {
                "data": null,
                "orderable": false,
            }
        ],
        "order": [[2, 'desc']],
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
                'targets': 0,
                'visible': false,
                'searchable': false
            },
            {
                'targets': 1,
                'searchable': false
            },
            {
                'targets': 2,
                "render": function (data, type, row) {
                    return data.split(",").join("<br/>");
                },
            },
            {
                targets: 3,
                render: function (a, b, c, d) {
                    if (is_superuser == 1) {
                        var context =
                            {
                                func: [
                                    {"name": "申请", "fn": "apply(\'" + c.id + "\')", "type": "success"},
                                    {"name": "使用帮助", "fn": "doc(\'" + c.id + "\')", "type": "primary"},
                                    {"name": "流程配置", "fn": "workflow_node_config(\'" + c.id + "\')", "type": "danger"},
                                ]
                            };
                        var html = template(context);
                        return html;
                    }
                    else {
                        var context =
                            {
                                func: [
                                    {"name": "申请", "fn": "apply(\'" + c.id + "\')", "type": "success"},
                                    {"name": "使用帮助", "fn": "doc(\'" + c.id + "\')", "type": "primary"},
                                ]
                            };
                        var html = template(context);
                        return html;
                    }
                }
            }
        ],
        "language": {
            "url": "/static/js/i18n/Chinese.json"
        },
    });


    $('#mytable tbody').on('click', 'tr', function () {
        if ($(this).hasClass('selected')) {
            $(this).removeClass('selected');
        }
        else {
            table.$('tr.selected').removeClass('selected');
            $(this).addClass('selected');
        }
    });


});


// 流程节点配置页
function workflow_node_config(workflow_id) {
    location.href = "/myworkflows/workflow_node_config/" + workflow_id + "/";
}