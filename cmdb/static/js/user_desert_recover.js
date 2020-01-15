function submit_sure() {
    var warehousing_region = $('.warehousing_region');
    var warehousing_error = false;
    warehousing_region.each(function () {
        if ($(this).val() == null) {
            alert('请选择仓库位置');
            warehousing_error = true;
            return false;
        }
    });
    if (warehousing_error) {
        return false;
    }
    var gnl = confirm("确定勾选的资产正确吗？ 提交进入下一步，用户状态将改为离职，请确认！");
    if (gnl == true) {
        return true;
    } else {
        return false;
    }
}

function get_user_clean_page(user_id) {
    var gnl = confirm("进入权限清理页面，用户状态将改为离职，请确认！");
    if (gnl == true) {
        window.location.href = "/users/get_user_clean_page/" + user_id + "/";
    } else {
        return false;
    }
}


$(function () {
    function initTableCheckbox() {
        var $thr = $('table thead tr');
        var $checkAllTh = $('<th style="display: none"><input type="checkbox" id="checkAll" name="checkAll" /></th>');
        /*将全选/反选复选框添加到表头最前，即增加一列*/
        $thr.prepend($checkAllTh);
        /*“全选/反选”复选框*/
        var $checkAll = $thr.find('input');
        $checkAll.click(function (event) {
            /*将所有行的选中状态设成全选框的选中状态*/
            $tbr.find('input').prop('checked', $(this).prop('checked'));
            /*并调整所有选中行的CSS样式*/
            if ($(this).prop('checked')) {
                $tbr.find('input').parent().parent().addClass('info');
            } else {
                $tbr.find('input').parent().parent().removeClass('info');
            }
            /*阻止向上冒泡，以防再次触发点击操作*/
            event.stopPropagation();
        });
        /*将所有行的选中状态设成全选框的选中状态*/
        /*点击全选框所在单元格时也触发全选框的点击操作*/
        $checkAllTh.click(function () {
            $(this).find('input').click();
        });
        var $tbr = $('table tbody tr');
        var $checkItemTd = $('<td style="display: none"><input class="item" type="checkbox" name="Item" /></td>');
        /*每一行都在最前面插入一个选中复选框的单元格*/
        $tbr.prepend($checkItemTd);
        /*点击每一行的选中复选框时*/
        $tbr.find('input').click(function (event) {
            /*调整选中行的CSS样式*/
            $(this).parent().parent().toggleClass('info');
            /*如果已经被选中行的行数等于表格的数据行数，将全选框设为选中状态，否则设为未选中状态*/
            $checkAll.prop('checked', $tbr.find('input:checked').length == $tbr.length ? true : false);
            /*阻止向上冒泡，以防再次触发点击操作*/
            event.stopPropagation();
        });
        /*点击每一行时也触发该行的选中操作*/
        $tbr.click(function () {
            $(this).find('input').click();
        });

        $checkAllTh.click()
    }

    initTableCheckbox();

});




