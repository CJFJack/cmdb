$(function () {
    $('#tree').treeview({
        data: getTree(),
        //showCheckbox: true,
        onNodeChecked: nodeChecked,
        onNodeUnchecked: nodeUnchecked,
    });


    //选中节点后更新右边修改页面数据
    $('#tree').on('nodeSelected', function (event, data) {
        var org_id = data.dataId;
        if (org_id != 1) {
            $("#section-head").text(data.text);
        }
        pdata = {
            'org_id': org_id
        };
        var encoded = $.toJSON(pdata);
        var pdata = encoded;
        $.ajax({
            type: "POST",
            url: "/users/get_org_section_permission/",
            contentType: "application/json; charset=utf-8",
            data: pdata,
            success: function (data) {
                $('input[type=checkbox]').map(function () {
                    $(this).prop('checked', false);
                });
                data.forEach(function (info, i) {
                    $("#" + info).prop('checked', true);
                });
                if (org_id == 1) {
                    $('#permission-edit').css('display', 'none');
                }
                else {
                    $('#org-id').text(org_id);
                    $('#permission-edit').css('display', 'block');
                }
            }
        });
    });
});


$("#bt-save").click(function (e) {
    var checked = $('#tree').treeview('getChecked');
    checked = JSON.stringify(checked);
    var org_id = $('#org-id').text();
    var checked_list = getChecked();
    pdata = {
        'org_id': org_id,
        'checked_list': checked_list
    };
    var encoded = $.toJSON(pdata);
    var pdata = encoded;
    jQuery('#loading').showLoading();
    $.ajax({
        type: "POST",
        url: "/users/new_department_permission/",
        contentType: "application/json; charset=utf-8",
        data: pdata,
        success: function (data) {
            jQuery('#loading').hideLoading();
        }
    });
});


function getChecked() {
    var listChecked = new Array();
    $('input[type=checkbox]:checked').map(function () {
        listChecked.push($(this).attr('id'));
    });
    return listChecked;
}


var nodeCheckedSilent = false;


function nodeChecked(event, node) {
    if (nodeCheckedSilent) {
        return;
    }
    nodeCheckedSilent = true;
    checkAllParent(node);
    checkAllSon(node);
    nodeCheckedSilent = false;
}

var nodeUncheckedSilent = false;

function nodeUnchecked(event, node) {
    if (nodeUncheckedSilent)
        return;
    nodeUncheckedSilent = true;
    uncheckAllParent(node);
    uncheckAllSon(node);
    nodeUncheckedSilent = false;
}

//全选所有父级节点
function checkAllParent(node) {
    $('#tree').treeview('checkNode', node.nodeId, {silent: true});
    var parentNode = $('#searchTree').treeview('getParent', node.nodeId);
    if (!("nodeId" in parentNode)) {
        return;
    } else {
        checkAllParent(parentNode);
    }
}

//取消全选所有父级节点
function uncheckAllParent(node) {
    $('#tree').treeview('uncheckNode', node.nodeId, {silent: true});
    var siblings = $('#searchTree').treeview('getSiblings', node.nodeId);
    var parentNode = $('#searchTree').treeview('getParent', node.nodeId);
    if (!("nodeId" in parentNode)) {
        return;
    }
    var isAllUnchecked = true;  //ÊÇ·ñÈ«²¿Ã»Ñ¡ÖÐ
    for (var i in siblings) {
        if (siblings[i].state.checked) {
            isAllUnchecked = false;
            break;
        }
    }
    if (isAllUnchecked) {
        uncheckAllParent(parentNode);
    }

}

//全选所有子节点
function checkAllSon(node) {
    $('#tree').treeview('checkNode', node.nodeId, {silent: true});
    if (node.nodes != null && node.nodes.length > 0) {
        for (var i in node.nodes) {
            checkAllSon(node.nodes[i]);
        }
    }
}

//取消全选所有子节点
function uncheckAllSon(node) {
    $('#tree').treeview('uncheckNode', node.nodeId, {silent: true});
    if (node.nodes != null && node.nodes.length > 0) {
        for (var i in node.nodes) {
            uncheckAllSon(node.nodes[i]);
        }
    }
}

//全选所有节点
$('#check-all').click(function () {
    $('#tree').treeview('checkAll', {silent: true});
});


//取消全选所有节点
$('#uncheck-all').click(function () {
    $('#tree').treeview('uncheckAll', {silent: true});
});








