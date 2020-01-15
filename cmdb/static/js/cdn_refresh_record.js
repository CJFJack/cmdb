var table;

function initModalSelect2() {
    // 初始化项目列表
    $select2Project = $("#project").select2({
        ajax: {
            url: '/assets/list_cdn_game_project_by_group/',
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
        minimumResultsForSearch: Infinity,
        placeholder: '',
    });
}

// 根据日期查询cdn刷新记录
function initQueryTable() {
    jQuery('#loading').showLoading();
    var project_id = $("#project").select2('data')[0].id;
    var startDate = $('#startDate').val();
    var endDate = $('#endDate').val();
    var curTime = new Date();
    var start_time = new Date(Date.parse(startDate));
    var end_time = new Date(Date.parse(endDate));
    if (project_id == 0) {
        alert('请先选择游戏项目!');
        jQuery('#loading').hideLoading();
        return false
    }
    if (start_time > curTime) {
        alert('开始日期不能大于今天!');
        jQuery('#loading').hideLoading();
        return false
    }
    if (end_time > curTime) {
        alert('结束日期不能大于今天!');
        jQuery('#loading').hideLoading();
        return false
    }
    if (start_time > end_time) {
        alert('开始日期不能大于结束日期!');
        jQuery('#loading').hideLoading();
        return false
    }
    if (table) {
        table.ajax.reload(function (json) {
            setTimeout("jQuery('#loading').hideLoading()", 500);
            if (json['success'] == false) {
                alert(json['msg'])
            }
        });
    }
    else {
        table = $('#mytable').DataTable({
            "processing": true,
            "ordering": false,
            "retrieve": true,
            "paging": true,
            "ajax": {
                "url": "/assets/query_cdn_refresh_record/",
                "type": "POST",
                "data": function (d) {
                    d.project_id = $("#project").select2('data')[0].id;
                    d.startDate = $('#startDate').val();
                    d.endDate = $('#endDate').val();
                },
            },
            "columns": [
                {"data": 'url'},  //0
                {"data": 'status'},  //1
                {"data": 'commit_time'},  // 2
            ],
            "language": {
                "url": "/static/js/i18n/Chinese.json"
            },
            "fnInitComplete": function (nRow, aData, iDisplayIndex, iDisplayIndexFull) {
                setTimeout("jQuery('#loading').hideLoading()", 500);
                if (aData['success'] == false) {
                    alert(aData['msg']);
                }
            },
        });
    }

}

// 获取当前日期
function get_current_date(date = null) {
    if (date) {
        var date = new Date(date);
    }
    else {
        // 获取当前日期
        var date = new Date();
    }
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


$(document).ready(function () {
    $.fn.select2.defaults.set( "theme", "bootstrap" );

    var nowDate = get_current_date();
    var nDate = new Date();
    // 减30天，即60*60*24*30*1000毫秒
    var minDate = get_current_date(nDate.getTime() - 2592000000)
    $("#startDate").val(nowDate);
    $("#endDate").val(nowDate);

    $(".flatpickr").flatpickr({
        locale: "zh",
        minDate: minDate,
        maxDate: "today",
    });


    initModalSelect2();


});