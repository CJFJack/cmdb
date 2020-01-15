$(document).ready(function () {

    // 下载模板
    $('#download_template').click(function () {
        let alter_type = $('#alter_type option:selected').text();
        console.log(alter_type);
        if (alter_type == '修改公司主体') {
            let download_url = '/it_assets/assets_templates_download/assets_batch_alter_company_template.xlsx';
            window.location = download_url;
        }
        if (alter_type == '修改资产状态') {
            let download_url = '/it_assets/assets_templates_download/assets_batch_alter_status_template.xlsx';
            window.location = download_url;
        }
        if (alter_type == '修改所在仓库区域') {
            let download_url = '/it_assets/assets_templates_download/assets_batch_alter_warehousing_region_template.xlsx';
            window.location = download_url;
        }
        else {
            alert('请先选择修改类型！')
        }
    });

    // 上传excel
    $('#import_excel').click(function () {
        $('#modal-notify').hide();
        $('#myModal').modal('show')
    });

    // 提交修改
    $('#bt-commit').click(function () {
        var table_data = [];
        var tb = document.getElementById("mytable");
        var rows = tb.rows;
        for (var i = 0; i < rows.length; i++) {
            var cells = rows[i].cells;
            var row_data = [];
            for (var j = 0; j < cells.length; j++) {
                row_data.push(cells[j].innerHTML);
            }
            table_data.push(row_data)
        }
        var inputs = {
            'table_data': table_data,
        };
        var encoded = $.toJSON(inputs);
        var pdata = encoded;
        $.ajax({
            type: "POST",
            url: "/it_assets/assets_batch_alter/",
            contentType: "application/json; charset=utf-8",
            data: pdata,
            async: true,
            beforeSend: function () {
                jQuery('#page-wrapper').showLoading();
            },
            success: function (result) {
                if (result.success) {
                    alert('提交成功！');
                    window.location.href = '/it_assets/assets_batch_alter_record/'
                }
                else {
                    alert('提交失败！' + result.msg)
                }
            },
            error: function (errorMsg) {
                alert('内部错误，提交失败！')
            },
            complete: function () {
                jQuery('#page-wrapper').hideLoading();
            },
        });
    })

});
