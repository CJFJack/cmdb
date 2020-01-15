function getSelectedTable(selector) {
    selector = selector || 'id';
    var selected = new Array();

    table.rows('.selected').data().toArray().forEach(function (info, i) {
        //console.log(selector.id);
        // console.log(info);
        selected.push(info[selector]);
    });

    return selected;
};


function getInitSelectedTable(selector) {
    selector = selector || 'telecom_ip';
    var selected = new Array();

    table.rows('.selected').data().toArray().forEach(function (info, i) {
        //console.log(selector.telecom_ip);
        // console.log(info);
        selected.push(info[selector]);
    });

    return selected;
}


function makeTitle(str, count) {
    $("#bt-del").data().text = str + " " + count + "个";
}

function makeMergeSrvTitle(str, count) {
    $("#bt-merge").data().text = str + " " + count + "个";
    $("#bt-mergecallback").data().text = str + " " + count + "个";
}

function makeInitializeTitle(str, count) {
    $("#batch_initialize").data().text = str + " " + count + "个";
}

function makeGameSrvInstallTitle(str, count) {
    $("#bt-install").data().text = str + " " + count + "个";
    $("#bt-uninstall").data().text = str + " " + count + "个";
}


function hidefun() {
    $(".sidebar-nav.navbar-collapse").hide();
    $("#page-wrapper").css("margin", "0");
    $("#navopt").html("显示导航");
}

function showfun() {
    $(".sidebar-nav.navbar-collapse").show();
    $("#page-wrapper").css("margin", "0 0 0 200px");
    $("#navopt").html("隐藏导航");
};

// 这个方法用来生成uuid
function generateUUID() {
    var d = new Date().getTime();
    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        var r = (d + Math.random() * 16) % 16 | 0;
        d = Math.floor(d / 16);
        return (c == 'x' ? r : (r & 0x7 | 0x8)).toString(16);
    });
    return uuid;
};

function initSelect2(id, select_id, select_value) {
    $("#" + id).html('');
    $("#" + id).append('<option value="' + select_id + '">' + select_value + '</option>');
    $("#" + id).select2('val', select_id, true);
}

//给modal监听close事件
/*$('#myModal').on('hidden.bs.modal', function () {
    table.ajax.reload();
})*/

$(document).ready(function () {

    // console.log('------');
    var agent = navigator.userAgent.toLowerCase();

    /*var regStr_ie = /msie [\d.]+;/gi ;
    var regStr_ff = /firefox\/[\d.]+/gi
    var regStr_chrome = /chrome\/[\d.]+/gi ;
    var regStr_saf = /safari\/[\d.]+/gi ;*/

    //firefox
    if (agent.indexOf("firefox") > 0) {
        // return agent.match(regStr_ff);
    } else if (agent.indexOf("chrome") > 0) {
        // return agent.match(regStr_chrome);
    } else if (agent.indexOf("safari") > 0) {
        // return agent.match(regStr_chrome);
    } else if (agent.indexOf("mobile") > 0) {
        // return agent.match(regStr_chrome);
    } else {
        window.location = "/error_version";
    }

    //禁用 BootStrap Modal 点击空白时自动关闭
    $('#myModal').modal({
        backdrop: 'static',
        keyboard: true,
        show: false,
    });
    var status = true;
    $("#navopt").click(function () {
        if (status == true) {
            hidefun();
            status = false;
        } else {
            showfun();
            status = true;
        }
    })
});
