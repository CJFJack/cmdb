var workflow;
var $select2Applicant;
var $select2Name;


function initModalSelect2() {
    $select2ApplicantWifiApply = $("#applicant-wifi-apply").select2({
        ajax: {
            url: '/assets/list_user/',
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
    });

    $select2ApplicantWifiNetwork = $("#applicant-network").select2({
        ajax: {
            url: '/assets/list_user/',
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
    });


    $select2ApplicantWifiApply.on("select2:select", function (e) {
        get_workflow_approve_user_wifi_apply(workflow, $("#applicant-wifi-apply").val())
    });


    $select2ApplicantWifiNetwork.on("select2:select", function (e) {
        get_workflow_approve_user_network(workflow, $("#applicant-network").val())
    });


    $select2Name = $("#name-wifi-apply").select2({
        minimumResultsForSearch: Infinity,
    });


    $select2Name = $("#name-network").select2({
        minimumResultsForSearch: Infinity,
    });

}

function get_workflow_state_approve_process() {
    var inputs = {
        'wse': wse,
    };

    var encoded = $.toJSON(inputs);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/myworkflows/workflow_state_approve_process/",
        async: true,
        contentType: "application/json; charset=utf-8",
        data: pdata,
        success: function (data) {
            // console.log(data.data, data.current_index);
            $(".ystep1").loadStep({
                size: "large",
                color: "green",
                steps: data.data,
            });

            $(".ystep1").setStep(data.current_index + 1);
        }
    });
}

// 获取流程的各个节点的审批人员
function get_workflow_approve_user_wifi_apply(workflow, applicant_id) {
    if (applicant_id == '0') {
        console.log('none')
    } else {
        var inputs = {
            'workflow': workflow,
            'applicant_id': applicant_id,
        };

        var encoded = $.toJSON(inputs);
        var pdata = encoded;
        $.ajax({
            type: "POST",
            url: "/myworkflows/get_workflow_approve_user/",
            contentType: "application/json; charset=utf-8",
            data: pdata,
            success: function (data) {
                // console.log(data.data, data.current_index);
                if (data.success) {
                    $("#approve_user-wifi-apply").html(data.data)
                    $("#approve_user-wifi-apply").removeClass('alert-danger')
                    $("#approve_user-wifi-apply").addClass('alert-success')
                    // $(".ystep1").setStep(data.current_index + 1);
                } else {
                    $("#approve_user-wifi-apply").removeClass('alert-success')
                    $("#approve_user-wifi-apply").addClass('alert-danger')
                    $("#approve_user-wifi-apply").html(data.data)
                }
            },
            error: function () {
                /* Act on the event */
                $("#approve_user-wifi-apply").removeClass('alert-success')
                $("#approve_user-wifi-apply").addClass('alert-danger')
                $("#approve_user-wifi-apply").html('获取审批人失败!')
            },
        });
    }
}

function get_workflow_approve_user_network(workflow, applicant_id) {
    if (applicant_id == '0') {
        console.log('none')
    } else {
        var inputs = {
            'workflow': workflow,
            'applicant_id': applicant_id,
        };

        var encoded = $.toJSON(inputs);
        var pdata = encoded;
        $.ajax({
            type: "POST",
            url: "/myworkflows/get_workflow_approve_user/",
            contentType: "application/json; charset=utf-8",
            data: pdata,
            success: function (data) {
                // console.log(data.data, data.current_index);
                if (data.success) {
                    $("#approve_user-network").html(data.data)
                    $("#approve_user-network").removeClass('alert-danger')
                    $("#approve_user-network").addClass('alert-success')
                    // $(".ystep1").setStep(data.current_index + 1);
                } else {
                    $("#approve_user-network").removeClass('alert-success')
                    $("#approve_user-network").addClass('alert-danger')
                    $("#approve_user-network").html(data.data)
                }
            },
            error: function () {
                /* Act on the event */
                $("#approve_user-network").removeClass('alert-success')
                $("#approve_user-network").addClass('alert-danger')
                $("#approve_user-network").html('获取审批人失败!')
            },
        });
    }
}

function checkBefore_wifi_apply(applicant, title, reason) {

    if (applicant == '0') {
        alert('请选择申请人');
        return false;
    }

    if (title == '') {
        alert('请填写标题');
        return false;
    }

    if (reason == '') {
        alert('请填写申请理由');
        return false;
    }

    return true;

}

function checkBefore_network(applicant, title, content) {

    if (applicant == '0') {
        alert('请选择申请人');
        return false;
    }

    if (title == '') {
        alert('请填写标题');
        return false;
    }


    if (content == '') {
        alert('请填写问题描述');
        return false;
    }

    return true;

}

function macAddressIsValid(address) {
    var regex = "^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]){2}$";
    var regexp = new RegExp(regex);

    if (!regexp.test(address)) {
        alert('MAC地址无效,请检查');
        return false;
    }
    return true;
}

function ipAddressIsValid(address) {
    var regex = "^((25[0-5]|2[0-4]\\d|((1\\d{2})|([1-9]?\\d)))\\.){3}(25[0-5]|2[0-4]\\d|((1\\d{2})|([1-9]?\\d)))$";
    var regexp = new RegExp(regex);

    if (!regexp.test(address)) {
        alert('IP地址无效,请检查');
        return false;
    }
    return true;
}


$(document).ready(function () {

    workflow = $("#workflow_id").text();
    initModalSelect2();

    get_workflow_approve_user_wifi_apply(workflow, $("#applicant-wifi-apply").val());

    // 提交
    $("#bt-commit-wifi-apply").confirm({
        text: "确定提交到下一步?",
        confirm: function (button) {

            var applicant = $("#applicant-wifi-apply").select2('data')[0].id;
            var title = $("#title-wifi-apply").val();
            var mac = $("#mac").val();
            var name = $("#name-wifi-apply").select2('data')[0].text;
            var reason = $("#reason-wifi-apply").val();

            var result = checkBefore_wifi_apply(applicant, title, reason);

            var macAddressValid = macAddressIsValid(mac);

            var inputs = {
                'applicant': applicant,
                'title': title,
                'name': name,
                'reason': reason,
                'mac': mac,
                'workflow': workflow,
            };

            if (result && macAddressValid) {
                var regexp = new RegExp("-", "g");
                inputs.mac = inputs.mac.toLowerCase().replace(regexp, ':');
                var encoded = $.toJSON(inputs);
                var pdata = encoded;
                $.ajax({
                    type: "POST",
                    url: "/myworkflows/start_workflow/",
                    contentType: "application/json; charset=utf-8",
                    data: pdata,
                    success: function (data) {
                        if (data.success) {
                            var redirect_url = '/myworkflows/apply_history/';
                            window.location.href = redirect_url;
                        } else {
                            alert(data.data);
                        }
                    }
                });
            }
        },

        cancel: function (button) {

        },
        confirmButton: "确定",
        cancelButton: "取消",

    });

});


$(document).ready(function () {

    workflow = $("#workflow_id").text();
    initModalSelect2();

    get_workflow_approve_user_network(workflow, $("#applicant-network").val());

    // 提交
    $("#bt-commit-network").confirm({
        text: "确定提交到下一步?",
        confirm: function (button) {

            var applicant = $("#applicant-network").select2('data')[0].id;
            var title = $("#title-network").val();
            var ip = $("#ip").val();
            var name = "Null";
            var reason = $("#reason-network").val();

            var result = checkBefore_network(applicant, title, reason);

            var ipAddressValid = ipAddressIsValid(ip);

            var inputs = {
                'applicant': applicant,
                'title': title,
                'name': name,
                'reason': reason,
                'ip': ip,
                'workflow': workflow,
            };

            if (result && ipAddressValid) {
                var encoded = $.toJSON(inputs);
                var pdata = encoded;
                $.ajax({
                    type: "POST",
                    url: "/myworkflows/start_workflow/",
                    contentType: "application/json; charset=utf-8",
                    data: pdata,
                    success: function (data) {
                        if (data.success) {
                            var redirect_url = '/myworkflows/apply_history/';
                            window.location.href = redirect_url;
                        } else {
                            alert(data.data);
                        }
                    }
                });
            }
        },

        cancel: function (button) {

        },
        confirmButton: "确定",
        cancelButton: "取消",

    });

});
