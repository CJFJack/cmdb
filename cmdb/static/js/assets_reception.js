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

var $select2Status;
var $select2Pos;
var $select2WarehousingRegion;

function filterColumn(i) {
    $('#mytable').DataTable().column(i).search(
        $('#col' + i + '_filter').val(),
        $('#col' + i + '_regex').prop('checked'),
        $('#col' + i + '_smart').prop('checked')
    ).draw();
}


$.urlParam = function (name) {
    var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
    if (results == null) {
        return null;
    }
    else {
        return decodeURIComponent(results[1]) || 0;
    }
};

function preFilter() {
    var name = $.urlParam('name');
    var status_code = $.urlParam('status_code');
    var company_id = $.urlParam('company_id');

    if (name !== null & status_code !== null & company_id !== null) {
        $("#filter_name").val(name).trigger('change');
        $("#filter_status").val(status_code).trigger('change');
        $("#filter_company").val(company_id).trigger('change');
        // table.ajax.reload();
    }
}


function formatRepo(repo) {

    var markup = '<div class="clearfix"><div clas="col-sm-7">' + repo.text + '</div></div>';

    return markup;
}

function formatRepoSelection(repo) {
    return repo.text || repo.id;
}

function config_add(ctype) {
    memory_add_table = $('#mytable-AddConfig').DataTable({
        "processing": true,
        "ordering": false,
        "serverSide": true,
        "destroy": true,
        "autoWidth": true,
        "ajax": {
            "url": "/it_assets/data_sub_assets_reception/",
            "type": "POST",
            "data": function (d) {
                d.ctype = ctype;
                d.AddConfigFlag = true;
            }
        },
        "columns": [
            {"data": null},// 0
            {"data": "id"},  // 1
            {"data": "company"},  // 2
            {"data": "ctype"},  // 3
            {"data": 'brand'},  //4
            {"data": 'smodel'},  //5
            {"data": 'status'},  // 6
            {"data": "number"},  // 7
            {"data": "pos"},  // 8
            {"data": "supplier"},  // 9
            {"data": "user"},  // 10
        ],
        "order": [[1, 'asc']],
        columnDefs: [
            {
                'targets': 1,
                'visible': false,
                'searchable': false
            },
        ],
        fnRowCallback: function (nRow, data, iDataIndex) {
            let id = data.id;
            let html = '<input type="radio" name="radio" id=' + id + '>';
            $('td:eq(0)', nRow).html(html);
            return nRow;
        },
        "language": {
            "url": "/static/js/i18n/Chinese.json"
        },
    });
    $("#myModalLabelAddConfig").text("增加" + ctype);
    $("#myModalAddConfig").modal("show");
    //$("#myModalEdit").modal("hide");
}


$("#add-confirm").confirm({
    confirm: function () {
        $("#myModalAddConfig").modal("hide");
        let dataId = $('input[name="radio"]:checked').attr("id");
        let assetsId = $('#assets_id').text();
        let input = {
            'assetsId': assetsId,
            'dataId': dataId,
        };

        let encoded = $.toJSON(input)
        let pdata = encoded

        let url = '/it_assets/assets_add_config/';
        $.ajax({
            type: "POST",
            url: url,
            contentType: "application/json; charset=utf-8",
            data: pdata,
            success: function (data) {
                editFlag = true;
                var input = {
                    'id': assetsId,
                };
                var encoded = $.toJSON(input);
                var pdata = encoded;
                $.ajax({
                    type: "POST",
                    url: "/it_assets/get_assets_reception/",
                    data: pdata,
                    contentType: "application/json; charset=utf-8",
                    success: function (data) {
                        $("#cpu").val(data.cpu);
                        $("#mem").val(data.mem);
                        $("#board").val(data.board);
                        $("#hdd").val(data.hdd);
                        $("#ssd").val(data.ssd);
                        $("#graphics").val(data.graphics);
                    },
                    error: function (xhr, status, error) {
                        if (xhr.status == '403') {
                            alert('权限拒绝');
                        } else {
                            alert('内部错误');
                        }
                    }
                });
            },
            error: function (data) {

            }
        });
    },
    cancel: function (button) {
    },
    text: '确定要添加吗? 确定则马上减少库存!',
    confirmButton: "确定",
    cancelButton: "取消",
});


function add_config_cancel() {
    $("#myModalAddConfig").modal("hide");
}


function edit(id) {
    editFlag = true;
    var data = {
        'id': id,
    };

    var encoded = $.toJSON(data);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/it_assets/get_assets_reception/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function (data) {
            origin_data = data;
            $("#myModalLabelEdit").text("修改固定资产");
            $("#modal-notify-edit").hide();
            $("#id").val(id);
            $("#assets_id").text(id);
            $("#show_id").hide();

            // Fill data

            initSelect2('supplier', data.supplier_id, data.supplier);
            initSelect2('company', data.company_id, data.company);
            initSelect2('pos', data.pos_id, data.pos);
            initSelect2('warehousing_region', data.warehousing_region_id, data.warehousing_region);
            initSelect2('user', data.user, data.user);
            //initSelect2('new_organization', data.belongs_to_new_organization, data.belongs_to_new_organization);

            $("#new_organization").val(data.belongs_to_new_organization);
            $("#brand").val(data.brand);
            $("#specification").val(data.specification);
            if (data.is_dz_assets_type) {
                $("#cpu").val(data.cpu);
                $("#mem").val(data.mem);
                $("#board").val(data.board);
                $("#hdd").val(data.hdd);
                $("#ssd").val(data.ssd);
                $("#graphics").val(data.graphics);
                $("#div-cpu").show();
                $("#div-mem").show();
                $("#div-board").show();
                $("#div-hdd").show();
                $("#div-ssd").show();
                $("#div-graphics").show();
            }
            else {
                $("#div-cpu").hide();
                $("#div-mem").hide();
                $("#div-board").hide();
                $("#div-hdd").hide();
                $("#div-ssd").hide();
                $("#div-graphics").hide();
                $("#cpu").val('');
                $("#mem").val('');
                $("#board").val('');
                $("#hdd").val('');
                $("#ssd").val('');
                $("#graphics").val('');
            }
            $("#remark").val(data.remark);

            $("#myModalEdit").modal("show");
        },
        error: function (xhr, status, error) {
            if (xhr.status == '403') {
                alert('权限拒绝');
            } else {
                alert('内部错误');
            }
        }
    });

}


function assets_change_history(id) {
    editFlag = true;
    var data = {
        'id': id,
    };

    var encoded = $.toJSON(data);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/it_assets/get_assets_change_history/",
        data: pdata,
        contentType: "application/json; charset=utf-8",
        success: function (data) {
            origin_data = data.data;
            let record = '';
            $("#myModalLabelHistory").text("查看资产变更记录");
            for (let i = 0; i < origin_data.length; i++) {
                let log = origin_data[i];
                if (log['event'] === '公司主体变更' || log['event'] === '仓库区域变更') {
                    let etime = '<p class="text-danger"><strong>' + log['etime'] + '</strong></p>';
                    let log_user = '<span>' + '<span class="text-info">操作人：</span>' + log['log_user'] + '</span>&nbsp;&nbsp;&nbsp;&nbsp;';
                    let ctype = '<span class="text-success">' + log['event'] + '</span>&nbsp;&nbsp;&nbsp;&nbsp;';
                    let pre_configuration = '<span>' + log['pre_configuration'] + '&nbsp;&nbsp;&nbsp;&nbsp;' + '\>>>>>' + '</span>&nbsp;&nbsp;&nbsp;&nbsp;';
                    let current_configuration = '<span>' + log['current_configuration'] + '</span>&nbsp;&nbsp;&nbsp;&nbsp;<br/><br/>';
                    record = record + etime + log_user + ctype + pre_configuration + current_configuration;
                }
                else if (log['event'] == '主机参数变更') {
                    let etime = '<p class="text-danger"><strong>' + log['etime'] + '</strong></p>';
                    let log_user = '<span>' + '<span class="text-info">操作人：</span>' + log['log_user'] + '</span>&nbsp;&nbsp;&nbsp;&nbsp;';
                    let ctype = '<span class="text-success">' + log['ctype'] + '修改' + '</span>&nbsp;&nbsp;&nbsp;&nbsp;';
                    let pre_configuration = '<span>' + log['pre_configuration'] + '&nbsp;&nbsp;&nbsp;&nbsp;' + '\>>>>>' + '</span>&nbsp;&nbsp;&nbsp;&nbsp;';
                    let current_configuration = '<span>' + log['current_configuration'] + '</span>&nbsp;&nbsp;&nbsp;&nbsp;<br/><br/>';
                    record = record + etime + log_user + ctype + pre_configuration + current_configuration;
                }
                else if (log['event'] == '主机配置升级') {
                    let etime = '<p class="text-danger"><strong>' + log['etime'] + '</strong></p>';
                    let log_user = '<span>' + '<span class="text-info">操作人：</span>' + log['log_user'] + '</span>&nbsp;&nbsp;&nbsp;&nbsp;';
                    let ctype = '<span class="text-success">' + log['ctype'] + '增加' + '</span>&nbsp;&nbsp;&nbsp;&nbsp;';
                    let current_configuration = '<span>' + log['current_configuration'] + '</span>&nbsp;&nbsp;&nbsp;&nbsp;<br/><br/>';
                    record = record + etime + log_user + ctype + current_configuration;
                }
                else {
                    let etime = '<p class="text-danger"><strong>' + log['etime'] + '</strong></p>';
                    let log_user = '<span>' + '<span class="text-info">录入人：</span>' + log['log_user'] + '</span>&nbsp;&nbsp;&nbsp;&nbsp;';
                    let user = '<span>' + '<span class="text-info">保管人：</span>' + log['user'] + '</span>&nbsp;&nbsp;&nbsp;&nbsp;';
                    let action = '<span class="text-success">' + log['event'] + '</span>&nbsp;&nbsp;&nbsp;&nbsp;';
                    let number = '<span>' + '<span class="text-info">数量：</span>' + log['number'] + '个' + '</span>&nbsp;&nbsp;&nbsp;&nbsp;<br/><br/>';
                    record = record + etime + log_user + user + action + number;
                }
            }

            $("#myModalHistoryContent").html(record);
            $("#myModalHistory").modal("show");
        },
        error: function (xhr, status, error) {
            if (xhr.status == '403') {
                alert('权限拒绝');
            } else {
                alert('内部错误');
            }
        }
    });

}


// $(document).on('hidden.bs.modal', function (e) {
//     clearModalSelect2();
//     initModalSelect2();
// });

function initModalSelect2() {

    $select2Ctype = $("#filter_ctype").select2({
        minimumResultsForSearch: Infinity,
    });

    $select2AssetsCtype = $("#filter_assets_type").select2({
        minimumResultsForSearch: Infinity,
    });

    $(".filter_select2").select2({
        // minimumResultsForSearch: Infinity,
    }).on("select2:select", function (e) {
        table.ajax.reload();
    });

    $select2Ctype.on("select2:select", function (e) {
        log("select2:select", e);
    });
    $select2AssetsCtype.on("select2:select", function (e) {
        log("select2:select", e);
    });

    $select2Status = $("#filter_status").select2({
        minimumResultsForSearch: Infinity,
    });
    $select2Status.on("change", function (e) {
        log("select2:select", e);
    });

    $select2Pos = $("#filter_pos").select2({
        minimumResultsForSearch: Infinity,
    });
    $select2Pos.on("change", function (e) {
        log("select2:select", e);
    });

    $select2WarehousingRegion = $("#filter_warehousing_region").select2({
        minimumResultsForSearch: Infinity,
    });
    $select2WarehousingRegion.on("change", function (e) {
        log("select2:select", e);
    });

    $select2Supplier = $("#supplier").select2({
        ajax: {
            url: '/it_assets/list_supplier/',
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

    $select2Company = $("#company").select2({
        ajax: {
            url: '/it_assets/list_company_code/',
            dataType: 'json',
            type: 'POST',
            delay: 30,
            data: function (params) {
                return {
                    q: params.term, // search term
                    page: params.page
                };
            },
            processResults: function (data, params) {
                params.page = params.page || 1;
                return {
                    results: $.map(data, function (item) {
                        return {
                            id: item.id,
                            text: item.text,
                        }
                    })
                }
            },
            cache: false,
        },
        escapeMarkup: function (markup) {
            return markup;
        },
    });

    $select2User = $("#user").select2({
        ajax: {
            url: '/it_assets/list_all_users/',
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

    // $select2NewOrganization = $("#new_organization").select2({
    //     ajax: {
    //         url: '/it_assets/list_new_organization/',
    //         dataType: 'json',
    //         type: 'POST',
    //         delay: 0,
    //         data: function (params) {
    //             return {
    //                 q: params.term, // search term
    //                 page: params.page
    //             };
    //         },
    //
    //         processResults: function (data, params) {
    //             // parse the results into the format expected by Select2
    //             // since we are using custom formatting functions we do not need to
    //             // alter the remote JSON data, except to indicate that infinite
    //             // scrolling can be used
    //             params.page = params.page || 1;
    //             return {
    //                 results: $.map(data, function (item) {
    //                     return {
    //                         id: item.id,
    //                         text: item.text,
    //                     }
    //                 })
    //                 // pagination: {
    //                 //     more: (params.page * 30) < data.total_count
    //                 // };
    //             }
    //         },
    //         cache: false,
    //     },
    //     //minimumResultsForSearch: Infinity,
    //     escapeMarkup: function (markup) {
    //         return markup;
    //     }, // let our custom formatter work
    //     // minimumInputLength: 1,
    //     // templateResult: formatRepo, // omitted for brevity, see the source of this page
    //     // templateSelection: formatRepoSelection, // omitted for brevity, see the source of this page
    // });

    $select2Pos2 = $("#pos").select2({
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

    $select2WarehousingRegion = $("#warehousing_region").select2({
        ajax: {
            url: '/it_assets/list_warehousing_region/',
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
                params.page = params.page || 1;
                return {
                    results: $.map(data, function (item) {
                        return {
                            id: item.id,
                            text: item.text,
                        }
                    })
                }
            },
            cache: false,
        },
        escapeMarkup: function (markup) {
            return markup;
        },
    });
}


function log(name, evt, className) {
    if (name == "select2:select" || name == "select2:select2") {
        table.ajax.reload();

    }
}

$(document).ready(function () {

    initModalSelect2();

    var rows_selected = [];
    table = $('#mytable').DataTable({
        "processing": true,
        "ordering": false,
        "serverSide": true,
        "ajax": {
            "url": "/it_assets/data_assets_reception/",
            "type": "POST",
            "data": function (d) {
                d.filter_ctype = $("#filter_ctype").select2('data')[0].id;
                d.filter_assets_type = $("#filter_assets_type").select2('data')[0].id;
                d.filter_assets_number = $("#filter_assets_number").val();
                d.filter_name = $("#filter_name").select2('data')[0].id;
                d.filter_warehousing_region = $("#filter_warehousing_region").val();
                d.filter_merge_assets_number = $("#filter_merge_assets_number").val();
                d.filter_company = $("#filter_company").select2('data')[0].id;
                d.filter_CPU = $("#filter_CPU").select2('data')[0].text;
                d.filter_board = $("#filter_board").select2('data')[0].text;
                d.filter_ssd = $("#filter_ssd").select2('data')[0].text;
                d.filter_disk = $("#filter_disk").select2('data')[0].text;
                d.filter_mem = $("#filter_mem").select2('data')[0].text;
                d.filter_graphics = $("#filter_graphics").select2('data')[0].text;
                d.filter_brand = $("#filter_brand").select2('data')[0].text;
                d.filter_specification = $("#filter_specification").val();
                d.filter_new_organization = $("#filter_new_organization").select2('data')[0].text;
                d.filter_user = $("#filter_user").select2('data')[0].text;
                d.filter_status = $("#filter_status").val();
                d.filter_pos = $("#filter_pos").val();
                d.filter_supplier = $("#filter_supplier").select2('data')[0].id;
                d.filter_remark = $("#filter_remark").val();
                d.exclude_unvailable_assets = $("input[id=exclude_unvailable_assets]:checked").length;
            }
        },
        "columns": [
            {"data": null}, //0
            {"data": "id"},  // 1
            {"data": 'ctype'},  //2
            {"data": 'company'},  //3
            {"data": 'assets_number'},  // 4
            {"data": "name"},  // 5
            {"data": "warehousing_region"},  // 6
            {"data": "merge_assets"},  // 7
            {"data": "with_cpu"},  // 8
            {"data": "board"},  // 9
            {"data": "with_ssd"}, //10
            {"data": "with_disk"},  // 11
            {"data": "with_mem"},  // 12
            {"data": "with_graphics"},  // 13
            {"data": "brand"},  // 14
            {"data": "specification"},  // 15
            {"data": "new_organization"},  // 16
            {"data": "auth_user"}, //17
            {"data": "status"},  // 18
            {"data": "pos"},  // 19
            {"data": "supplier"},  // 20
            {"data": "remark"},  // 21
            {
                "data": null,   //22
                "orderable": false,
            },
        ],
        "order": [[1, 'asc']],
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
                'targets': [1, 2],
                'visible': false,
                'searchable': false
            },
            {
                'targets': [5, 16, 19],
                'width': "10%",
                'searchable': true
            },
            {
                'targets': 6,
                "render": function (data, type, row) {
                    return '<span class="text-danger"><strong>' + data + '</strong></span>';
                },
            },
            {
                'targets': [7, 8, 9, 10, 11, 12, 13],
                "render": function (data, type, row) {
                    return data.split(",").join("<br/>");
                },
            },
            {
                targets: 21,
                width: "10%",
                render: function (data, type, row, meta) {
                    let num = 8;
                    if (data.length > num) {
                        return '<span class="tooltip-demo"><span data-toggle="tooltip" data-placement="right" title="' + data + '">' + data.substring(1, num) + '......' + '</span></span>'
                    }
                    else {
                        return '<span>' + data + '</span>'
                    }
                }
            },
            {
                targets: 22,
                width: "10%",
                render: function (a, b, c, d) {
                    var context =
                        {
                            func: [
                                {"name": "修改", "fn": "edit(\'" + c.id + "\')", "type": "primary"},
                                {"name": "变更记录", "fn": "assets_change_history(\'" + c.id + "\')", "type": "success"},
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
        initComplete: function () {
            // tooltip demo
            $('.tooltip-demo').tooltip({
                selector: "[data-toggle=tooltip]",
                container: "body"
            })
        }
    });

    // 翻页后也要重新初始化提示插件
    $('#mytable').on('draw.dt', function () {
        // tooltip demo
        $('.tooltip-demo').tooltip({
            selector: "[data-toggle=tooltip]",
            container: "body"
        })
    });

    preFilter();


    $(':checkbox.toggle-visiable').on('click', function (e) {
        //e.preventDefault();

        // Get the column API object
        var is_checked = $(this).is(':checked');
        var column = table.column($(this).attr('value'));
        // table.ajax.reload();
        column.visible(is_checked);
    });

    $('#bt-modal-notify').click(function () {
        $("#modal-notify").hide();
    });

    $('#chb-all').on('click', function (e) {
        var checkbox = document.getElementById('chb-all');
        $('#mytable tbody td').parent().find('input[type="checkbox"]').map(function (i, n) {
            var $row = $(this).closest('tr');
            n.checked = checkbox.checked;
            if (checkbox.checked) {
                $row.addClass('selected');
                count = getSelectedTable().length;
                //makeTitle(str, count);
            } else {
                $row.removeClass('selected');
                count = 0;
                //makeTitle(str, count);
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
            //makeTitle(str, ++count);
        } else {
            $row.removeClass('selected');
            //makeTitle(str, --count);
        }

        // Prevent click event from propagating to parent
        e.stopPropagation();
    });

    $('#bt-search').click(function () {
        $('#div-search').toggleClass('hide');
    });

    $('input.column_filter').on('keyup click', function () {
        // filterColumn( $(this).parents('tr').attr('data-column') );
        table.ajax.reload();
    });

    $("#bt-reset").click(function () {
        // 重置高级搜索
        $("#filter_ctype").val('100').trigger('change');
        $("#filter_assets_type").val('100').trigger('change');
        $("#filter_assets_number").val('');
        $("#filter_brand").val('');
        $("#filter_specification").val('');
        $("#filter_status").val('100').trigger('change');
        $("#filter_pos").val('100').trigger('change');
        $("#filter_warehousing_region").val('100').trigger('change');
        $("#filter_remark").val('');
        $(".filter_select2").val('0').trigger('change');
        table.ajax.reload();

    });

    $("#bt-download").click(function () {
        var filter_ctype = $("#filter_ctype").select2('data')[0].id;
        var filter_assets_type = $("#filter_assets_type").select2('data')[0].id;
        var filter_assets_number = $("#filter_assets_number").val();
        var filter_name = $("#filter_name").select2('data')[0].id;
        var filter_merge_assets_number = $("#filter_merge_assets_number").val();
        var filter_company = $("#filter_company").select2('data')[0].id;
        var filter_CPU = $("#filter_CPU").select2('data')[0].text;
        var filter_board = $("#filter_board").select2('data')[0].text;
        var filter_ssd = $("#filter_ssd").select2('data')[0].text;
        var filter_disk = $("#filter_disk").select2('data')[0].text;
        var filter_mem = $("#filter_mem").select2('data')[0].text;
        var filter_graphics = $("#filter_graphics").select2('data')[0].text;
        var filter_brand = $("#filter_brand").select2('data')[0].text;
        var filter_specification = $("#filter_specification").val();
        var filter_new_organization = $("#filter_new_organization").select2('data')[0].text;
        var filter_user = $("#filter_user").select2('data')[0].text;
        var filter_status = $("#filter_status").val();
        var filter_pos = $("#filter_pos").val();
        var filter_warehousing_region = $("#filter_warehousing_region").val();
        var filter_supplier = $("#filter_supplier").select2('data')[0].id;
        var filter_remark = $("#filter_remark").val();

        var inputIds = {
            'filter_ctype': filter_ctype,
            'filter_assets_type': filter_assets_type,
            'filter_assets_number': filter_assets_number,
            'filter_name': filter_name,
            'filter_merge_assets_number': filter_merge_assets_number,
            'filter_company': filter_company,
            'filter_CPU': filter_CPU,
            'filter_board': filter_board,
            'filter_ssd': filter_ssd,
            'filter_disk': filter_disk,
            'filter_mem': filter_mem,
            'filter_graphics': filter_graphics,
            'filter_brand': filter_brand,
            'filter_specification': filter_specification,
            'filter_new_organization': filter_new_organization,
            'filter_user': filter_user,
            'filter_status': filter_status,
            'filter_pos': filter_pos,
            'filter_supplier': filter_supplier,
            'filter_remark': filter_remark,
            'filter_warehousing_region': filter_warehousing_region,
        };

        var encoded = $.toJSON(inputIds)
        var pdata = encoded

        $.ajax({
            type: "POST",
            url: "/it_assets/download/",
            contentType: "application/json; charset=utf-8",
            data: pdata,
            beforeSend: function () {
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
            error: function () {
                $("#load").hide();
                $("#modal-footer").show();
                $("#load-msg").text('下载失败');
                $("#show-msg").show();
            }
        });
    });

    $("#bt-save").click(function (event) {
        /* Act on the event */

        var id = $("#id").val();
        var supplier = $("#supplier").select2('data')[0].id;
        var company = $("#company").select2('data')[0].id;
        var pos = $("#pos").select2('data')[0].id;
        var warehousing_region = $("#warehousing_region").select2('data')[0].id;
        var user = $("#user").select2('data')[0].text;
        //var new_organization = $("#new_organization").select2('data')[0].text;
        var brand = $("#brand").val();
        var specification = $("#specification").val();
        var cpu = $("#cpu").val();
        var mem = $("#mem").val();
        var hdd = $("#hdd").val();
        var ssd = $("#ssd").val();
        var graphics = $("#graphics").val();
        var board = $("#board").val();
        var remark = $("#remark").val();

        var inputIds = {
            'id': id,
            'supplier': supplier,
            'pos': pos,
            'warehousing_region': warehousing_region,
            'user': user,
            //'new_organization': new_organization,
            'brand': brand,
            'specification': specification,
            'cpu': cpu,
            'mem': mem,
            'hdd': hdd,
            'ssd': ssd,
            'graphics': graphics,
            'board': board,
            'remark': remark,
            'company': company,
        };

        var urls = "/it_assets/edit_assets_reception/";

        var encoded = $.toJSON(inputIds);
        var pdata = encoded;
        $.ajax({
            type: "POST",
            url: urls,
            contentType: "application/json; charset=utf-8",
            data: pdata,
            success: function (data) {

                if (data['data']) {
                    table.ajax.reload(null, false);
                    $("#myModalEdit").modal("hide");
                } else {
                    $('#lb-msg-edit').text(data['msg']);
                    $('#modal-notify-edit').show();
                }

            }
        });
    });

    // 生成打印单
    $("#bt-print").confirm({
        text: "确定生成打印单?",
        confirm: function (button) {

            var selected = getSelectedTable();
            var inputs = {
                'selected': selected,
                'type': 'assets',
            };

            if (selected.length == 0) {
                alert('请勾选需要生成打印单的资产');
            } else {
                var encoded = $.toJSON(inputs);
                var pdata = encoded;
                $.ajax({
                    type: "POST",
                    url: "/it_assets/create_application_form/",
                    contentType: "application/json; charset=utf-8",
                    data: pdata,
                    success: function (result) {
                        var assets_id_list = result['assets_id_list'];
                        $.ajax({
                            type: "POST",
                            url: "/it_assets/assets_application_form/",
                            contentType: "application/json; charset=utf-8",
                            data: JSON.stringify(assets_id_list),
                            success: function (result) {
                                var w = window.open();
                                $(w.document.body).html(result);
                            }
                        });
                    },
                    error: function (errorMsg) {

                    }

                });
            }
        },

        cancel: function (button) {

        }
        ,
        confirmButton: "确定",
        cancelButton:
            "取消",

    });


    $("#exclude_unvailable_assets").change(function () {
        table.ajax.reload();
    });


    // 统计数量
    $.ajax({
        type: "post",
        async: true,
        url: "/it_assets/it_assets_amount_statistics/",
        dataType: "json",
        beforeSend: function () {
            jQuery('.panel-body').showLoading();
        },
        success: function (result) {
            if (result['success']) {
                let computer = result.computer;
                let computer_html = '';
                for (var k in computer) {
                    computer_html += '<p><b>' + k + '</b></p>';
                    let data = '';
                    for (let i of computer[k]) {
                        data += i.specification + '： ' + i.total + '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'
                    }
                    data = '<p>' + data + '</p>';
                    computer_html += data;
                }
                $('#computer_statistics').html(computer_html);
                let display = result.display;
                let display_html = '';
                for (var k in display) {
                    display_html += '<p><b>' + k + '</b></p>';
                    let data = '';
                    for (let i of display[k]) {
                        data += i.brand + '： ' + i.total + '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'
                    }
                    data = '<p>' + data + '</p>';
                    display_html += data;
                }
                $('#display_statistics').html(display_html);
                let draw = result.draw;
                let draw_html = '';
                for (let i of draw) {
                    draw_html += i.company + '： ' + i.total + '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'
                }
                $('#draw_statistics').html(draw_html)
            }
            jQuery('.panel-body').hideLoading();
        },
        error: function (errorMsg) {
            jQuery('.panel-body').hideLoading();
        }
    });

});


// 后退不刷新页面
function back() {
    history.go(-1);
}