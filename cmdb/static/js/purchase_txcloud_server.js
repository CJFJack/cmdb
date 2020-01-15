$(document).ready(function () {

    $.fn.select2.defaults.set("theme", "bootstrap");

    // 初始化select2
    $('#project').select2();
    $('#room').select2();
    $('#business').select2();
    $('#instance_type').select2();
    $('#instance_cpu').select2();
    $('#instance_memory').select2();
    $('#image_version').select2();
    $('#ProjectId').select2({placeholder: '请选择腾讯云项目'});
    $('#SecurityGroupId').select2({placeholder: '请选择安全组'});

    // select元素改变时删除border警告样式
    $("#project").on("select2:select", function () {
        $('#project').parent().removeClass('has-error');
    });

    // 改变购买数量时，发起询价请求
    $('#InstanceCount').on("change", function () {
        inquiry_price()
    });

    // 获取地域
    $.ajax({
        type: "POST",
        url: "/txcloud/get_server_region/",
        async: false,
        data: $.toJSON({}),
        success: function (data) {
            var origin_data = data.data;
            if (data.success) {
                $('#region').html('');
                for (let i in origin_data) {
                    let region_data = origin_data[i];
                    if (region_data.city == '广州') {
                        var html = '<li>' +
                            '<input checked type="radio" name="region" id="' + region_data.code + '" value="' + region_data.code + '"/>' +
                            '<label class="label_region" for="' + region_data.code + '">' + region_data.city + '</label>' +
                            '</li>';
                    }
                    else {
                        var html = '<li>' +
                            '<input type="radio" name="region" id="' + region_data.code + '" value="' + region_data.code + '"/>' +
                            '<label class="label_region" for="' + region_data.code + '">' + region_data.city + '</label>' +
                            '</li>';
                    }
                    $('#region').append(html)
                }
            }
            else {
                console.log(data.data)
            }
        },
        error: function (xhr, status, error) {
            console.log('内部错误');
        }
    });


    // 获取可用机型
    $.ajax({
        type: "POST",
        url: "/txcloud/get_server_zone_number/",
        async: true,
        success: function (data) {
            if (!data.success) {
                console.log(data.data)
            }
        },
        error: function (xhr, status, error) {
            console.log('内部错误');
        }
    });

});


// 当选择地域时，根据地域获取可用区
$(document).on("click", ".label_region", function () {
    var region_code = $(this).closest('li').find("input[name=region]").val();
    var project = $('#project').select2('data')[0].id;

    var inputIds = {
        'region_code': region_code,
        'project': project,
    };
    var encoded = $.toJSON(inputIds);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/txcloud/get_server_zone/",
        async: true,
        data: pdata,
        success: function (data) {
            var origin_data = data.data;
            if (data.success) {
                $('#zone').html('');
                for (let i in origin_data) {
                    let zone_data = origin_data[i];
                    let html = '<li>' +
                        '<input type="radio" name="zone" id="' + zone_data.zone + '" value="' + zone_data.zone + '"/>' +
                        '<label class="label_zone" for="' + zone_data.zone + '">' + zone_data.zone_name + '</label>' +
                        '</li>';
                    $('#zone').append(html)
                }
            }
            else {
                console.log(data.data)
            }
        },
        error: function (xhr, status, error) {
            if (xhr.status == '403') {
                alert('权限拒绝');
            } else {
                alert('内部错误');
            }
        }
    });

});


function getnext(prev, next) {

    // 跳转到第1个步骤
    if (next == 'step1' && prev == 'step0') {

        var project = $('#project').select2('data')[0].id;
        var room = $('#room').select2('data')[0].id;
        var business = $('#business').select2('data')[0].id;
        var project_cloud_account = $('#project').select2('data')[0].title;
        if (project == '0') {
            $('#project').parent().addClass('has-error');
            return false;
        }
        if (room == '0') {
            $('#room').parent().addClass('has-error');
            return false;
        }
        if (business == '0') {
            $('#business').parent().addClass('has-error');
            return false;
        }
        if (project_cloud_account == 0) {
            $('.alert_text').text('项目没有关联云帐号，请先到“游戏项目管理-项目列表”中进行关联');
            $('.alert-danger').css('display', 'block');
            return false;
        }

        //  获取地域
        var inputIds = {
            'project': project,
        };
        var encoded = $.toJSON(inputIds);
        var pdata = encoded;
        // $.ajax({
        //     type: "POST",
        //     url: "/txcloud/get_server_region/",
        //     async: false,
        //     data: pdata,
        //     beforeSend: function () {
        //         jQuery('#page-wrapper').showLoading();
        //     },
        //     success: function (data) {
        //         var origin_data = data.data;
        //         if (data.success) {
        //             $('#region').html('');
        //             for (let i in origin_data) {
        //                 let region_data = origin_data[i];
        //                 if (region_data.city == '广州') {
        //                     var html = '<li>' +
        //                         '<input checked type="radio" name="region" id="' + region_data.code + '" value="' + region_data.code + '"/>' +
        //                         '<label class="label_region" for="' + region_data.code + '">' + region_data.city + '</label>' +
        //                         '</li>';
        //                 }
        //                 else {
        //                     var html = '<li>' +
        //                         '<input type="radio" name="region" id="' + region_data.code + '" value="' + region_data.code + '"/>' +
        //                         '<label class="label_region" for="' + region_data.code + '">' + region_data.city + '</label>' +
        //                         '</li>';
        //                 }
        //                 $('#region').append(html)
        //             }
        //         }
        //         else {
        //             console.log(data.data)
        //         }
        //         jQuery('#page-wrapper').hideLoading();
        //     },
        //     error: function (xhr, status, error) {
        //         if (xhr.status == '403') {
        //             alert('权限拒绝');
        //         } else {
        //             alert('内部错误');
        //         }
        //         jQuery('#page-wrapper').hideLoading();
        //     }
        // });


        //  获取可用区
        var region_code = $('input[name=region]:checked').val();
        var inputIds = {
            'region_code': region_code,
            'project': project,
        };
        var encoded = $.toJSON(inputIds);
        var pdata = encoded;
        $.ajax({
            type: "POST",
            url: "/txcloud/get_server_zone/",
            async: true,
            data: pdata,
            beforeSend: function () {
                jQuery('#page-wrapper').showLoading();
            },
            success: function (data) {
                var origin_data = data.data;
                if (data.success) {
                    $('#zone').html('');
                    for (let i in origin_data) {
                        var zone_data = origin_data[i];
                        if (zone_data.zone_name == '广州四区') {
                            var html = '<li>' +
                                '<input checked type="radio" name="zone" id="' + zone_data.zone + '" value="' + zone_data.zone + '"/>' +
                                '<label class="label_zone" for="' + zone_data.zone + '">' + zone_data.zone_name + '</label>' +
                                '</li>';
                        }
                        else {
                            var html = '<li>' +
                                '<input type="radio" name="zone" id="' + zone_data.zone + '" value="' + zone_data.zone + '"/>' +
                                '<label class="label_zone" for="' + zone_data.zone + '">' + zone_data.zone_name + '</label>' +
                                '</li>';
                        }
                        $('#zone').append(html)
                    }
                }
                else {
                    console.log(data.data)
                }
                jQuery('#page-wrapper').hideLoading();
            },
            error: function (xhr, status, error) {
                if (xhr.status == '403') {
                    alert('权限拒绝');
                } else {
                    alert('内部错误');
                }
                jQuery('#page-wrapper').hideLoading();
            }
        });

        // 初始化实例机型选择框
        $('#instance_type').select2({
            ajax: {
                url: '/txcloud/get_instance_config_info/',
                dataType: 'json',
                type: 'POST',
                delay: 0,
                data: function (params) {
                    return {
                        q: params.term, // search term
                        page: params.page,
                        region_code: $('input[name=region]:checked').val(),
                        project: project,
                        zone: $('input[name=zone]:checked').val(),
                        charge_mode: $('input[name=charge_mode]:checked').val(),
                        instance_cpu: $('#instance_cpu').select2('data')[0].id,
                        instance_memory: $('#instance_memory').select2('data')[0].id,
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
                cache: true,
            },
            escapeMarkup: function (markup) {
                return markup;
            },
        });

        // 获取腾讯云帐号中项目列表数据
        var inputIds = {
            'project': project,
        };
        var encoded = $.toJSON(inputIds);
        var pdata = encoded;
        $.ajax({
            type: "POST",
            url: "/txcloud/get_server_project/",
            async: true,
            data: pdata,
            success: function (data) {
                var origin_data = data;
                for (let i in origin_data) {
                    data = origin_data[i];
                    if ($('#ProjectId').find("option[value='" + data.id + "']").length) {

                    } else {
                        var newOption = new Option(data.text, data.id, false, false);
                        $('#ProjectId').append(newOption);
                    }
                }
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

    // 跳转到第2个步骤
    if (next == 'step2' && prev == 'step1') {
        //跳转前检查前一步所填信息是否完整
        let charge_mode = $('input[name=charge_mode]:checked').val();
        let region = $('input[name=region]:checked').val();
        let zone = $('input[name=zone]:checked').val();
        let instance = $('#instance_type').val();
        if (!charge_mode) {
            $('.alert_text').text('请选择计费模式');
            $('.alert-danger').css('display', 'block');
            return false;
        }
        if (!region) {
            $('.alert_text').text('请选择地域');
            $('.alert-danger').css('display', 'block');
            return false;
        }
        if (!zone) {
            $('.alert_text').text('请选择可用区');
            $('.alert-danger').css('display', 'block');
            return false;
        }
        if (!instance) {
            $('.alert_text').text('请选择实例');
            $('.alert-danger').css('display', 'block');
            return false;
        }

        // 异步获取镜像版本数据
        var project = $('#project').select2('data')[0].id;
        var region_code = $('input[name=region]:checked').val();
        $('#image_version').select2({
            ajax: {
                url: '/txcloud/get_image_version/',
                dataType: 'json',
                type: 'POST',
                delay: 0,
                data: function (params) {
                    return {
                        q: params.term, // search term
                        page: params.page,
                        region_code: region_code,
                        project: project,
                        image_type: $('input[name=image_type]:checked').val(),
                        operation_system: $('input[name=operation_system]:checked').val(),
                        system_framework: $('input[name=system_framework]:checked').val(),
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
                cache: true,
            },
            escapeMarkup: function (markup) {
                return markup;
            },
        });

        // 异步获取安全组数据
        var inputIds = {
            'project': project,
            'region_code': region_code,
        };
        var encoded = $.toJSON(inputIds);
        var pdata = encoded;
        $.ajax({
            type: "POST",
            url: "/txcloud/get_security_group/",
            async: true,
            data: pdata,
            success: function (data) {
                var origin_data = data;
                for (let i in origin_data) {
                    data = origin_data[i];
                    if ($('#SecurityGroupId').find("option[value='" + data.id + "']").length) {

                    } else {
                        var newOption = new Option(data.text, data.id, false, false);
                        $('#SecurityGroupId').append(newOption);
                    }
                }
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

    // 跳转到setp3
    if (next == 'step3' && prev == 'step2') {
        // 检查上一步所需参数是否完整
        var image_version = $('#image_version').val();
        if (!image_version) {
            $('.alert_text').text('请选择镜像版本');
            $('.alert-danger').css('display', 'block');
            return false;
        }

        // 根据step1选择的计费模式，添加网络计费模式
        var charge_mode = $('input[name=charge_mode]:checked').val();
        $('#network_charge_mode').html('');
        if (charge_mode == 'PREPAID') {
            var html = '<li>' +
                '<input type="radio" name="network_charge_mode" id="BANDWIDTH_PREPAID" value="BANDWIDTH_PREPAID"/>' +
                '<label for="BANDWIDTH_PREPAID">按带宽计费</label>' +
                '</li>' +
                '<li>' +
                '<input type="radio" name="network_charge_mode" id="TRAFFIC_POSTPAID_BY_HOUR" value="TRAFFIC_POSTPAID_BY_HOUR" checked/>' +
                '<label for="TRAFFIC_POSTPAID_BY_HOUR">按使用量计费</label>' +
                '</li>';

        }
        if (charge_mode == 'POSTPAID_BY_HOUR') {
            var html = '<li>' +
                '<input type="radio" name="network_charge_mode" id="BANDWIDTH_POSTPAID_BY_HOUR" value="BANDWIDTH_POSTPAID_BY_HOUR" checked/>' +
                '<label for="BANDWIDTH_POSTPAID_BY_HOUR">按带宽计费</label>' +
                '</li>' +
                '<li>' +
                '<input type="radio" name="network_charge_mode" id="TRAFFIC_POSTPAID_BY_HOUR" value="TRAFFIC_POSTPAID_BY_HOUR"/>' +
                '<label for="TRAFFIC_POSTPAID_BY_HOUR">按使用量计费</label>' +
                '</li>';
        }
        $('#network_charge_mode').append(html)
    }


    // 跳转到setp4
    if (next == 'step4' && prev == 'step3') {
        // 异步获取安全组数据
        // $('#SecurityGroupId').select2({
        //     ajax: {
        //         url: '/txcloud/get_security_group/',
        //         dataType: 'json',
        //         type: 'POST',
        //         delay: 0,
        //         data: function (params) {
        //             return {
        //                 q: params.term, // search term
        //                 page: params.page,
        //                 project: $('#project').select2('data')[0].id,
        //                 region_code: $('input[name=region]:checked').val(),
        //             };
        //         },
        //
        //         processResults: function (data, params) {
        //             params.page = params.page || 1;
        //             return {
        //                 results: $.map(data, function (item) {
        //                     return {
        //                         id: item.id,
        //                         text: item.text,
        //                     }
        //                 })
        //             }
        //         },
        //         cache: true,
        //     },
        //     escapeMarkup: function (markup) {
        //         return markup;
        //     },
        //     placeholder: '请选择安全组',
        // });
    }

    if (next == 'step5' && prev == 'step4') {
        var ProjectId = $('#ProjectId').val();
        var SecurityGroupId = $('#SecurityGroupId').val();
        if (!ProjectId) {
            $('.alert_text').text('请选择所属项目');
            $('.alert-danger').css('display', 'block');
            return false;
        }
        if (!SecurityGroupId) {
            $('.alert_text').text('请选择安全组');
            $('.alert-danger').css('display', 'block');
            return false;
        }

        // 展示确认汇总信息
        // 地域和机型
        $('#confirm_charge_mode').text($('input[name=charge_mode]:checked').closest('li').find('label').text());
        $('#confirm_region').text($('input[name=region]:checked').closest('li').find('label').text());
        $('#confirm_zone').text($('input[name=zone]:checked').closest('li').find('label').text());
        $('#confirm_network_type').text($('input[name=network_type]:checked').closest('li').find('label').text());
        $('#confirm_instance_type').text($('#instance_type').select2('data')[0].text);
        // 镜像
        $('#confirm_image_type').text($('input[name=image_type]:checked').closest('li').find('label').text());
        $('#confirm_image_version').text($('#image_version').select2('data')[0].text);
        // 存储和带宽
        $('#confirm_system_disk').text($('#SystemDiskSize').val() + 'GB , ' + $('input[name=system_disk]:checked').closest('li').find('label').text())
        let data_disk_text_list = get_data_disk_text_list();
        let confirm_data_disk = '';
        for (let i in data_disk_text_list) {
            confirm_data_disk = confirm_data_disk + data_disk_text_list[i].size + 'GB , ' + data_disk_text_list[i].type + '      '
        }
        $('#confirm_data_disk').text(confirm_data_disk);
        let PublicIpAssigned = $('#PublicIpAssigned').prop('checked');
        if (PublicIpAssigned) {
            $('#confirm_PublicIpAssigned').text('分配')
        }
        else {
            $('#confirm_PublicIpAssigned').text('未分配')
        }
        $('#confirm_InternetChargeType').text($('input[name=network_charge_mode]:checked').closest('li').find('label').text() + ': ' + $('#InternetMaxBandwidthOut').val() + 'Mbps');
        // 安全组
        $('#confirm_security_group').text($('#SecurityGroupId').select2('data')[0].text);
        // 设置信息
        $('#confirm_ProjectId').text($('#ProjectId').select2('data')[0].text)
        let instance_name = $('#InstanceName').val();
        if (instance_name) {
            $('#confirm_InstanceName').text(instance_name)
        }
        else {
            $('#confirm_InstanceName').text('(未命名)')
        }
        $('#confirm_login_mode').text('cmdb随机生成初始密码，并发送邮件');
        let security_enhance = $('#security_enhance').prop('checked');
        if (security_enhance) {
            $('#confirm_security_enhance').text('免费开通')
        }
        else {
            $('#confirm_security_enhance').text('不开通')
        }
        let cloud_monitor = $('#cloud_monitor').prop('checked');
        if (cloud_monitor) {
            $('#confirm_cloud_monitor').text('免费开通')
        }
        else {
            $('#confirm_cloud_monitor').text('不开通')
        }

        // 发起询价请求
        inquiry_price();

    }

    // 切换tab
    $('.alert-danger').css('display', 'none');
    let next_step = $('a[href=#' + next + ']');
    next_step.removeClass('disabled');
    next_step.click();

}


// 添加数据盘
function add_data_disk() {
    var a_data_disk = $('#a_data_disk');
    var data_disk_option = '<form class="form-inline">' +
        '<div class="data_disk">' +
        '<div class="col-sm-3">' +
        '<select class="form-control">' +
        '<option selected value="CLOUD_PREMIUM">高性能云硬盘</option>' +
        '<option value="CLOUD_SSD">SSD云硬盘</option>' +
        '</select>' +
        '</div>' +
        '<div class="col-sm-3 input-group">' +
        '<input type="number" class="form-control" value="100"/>' +
        '<span class="input-group-addon">GB</span>' +
        '</div>' +
        '&nbsp;&nbsp;&nbsp;<button type="button" onclick="cancel_data_disk(this)" class="btn btn-default btn-circle"><i class="fa fa-times"></i></button>' +
        '</div><br>' +
        '</form>';
    a_data_disk.before(data_disk_option)
}


// 获取数据盘文字数据
function get_data_disk_text_list() {
    var data_disk_list = [];
    $('.data_disk').each(function (i, e) {
        let data_disk_type_text = $($(e).children().get(0)).find('select option:selected').text();
        let data_disk_size = $($(e).children().get(1)).find('input').val();
        data_disk_list.push({'type': data_disk_type_text, 'size': data_disk_size})
    });
    return data_disk_list
}


// 获取数据盘value数据
function get_data_disk_value_list() {
    var data_disk_list = [];
    $('.data_disk').each(function (i, e) {
        let data_disk_type_text = $($(e).children().get(0)).find('select option:selected').val();
        let data_disk_size = $($(e).children().get(1)).find('input').val();
        data_disk_list.push({'DiskType': data_disk_type_text, 'DiskSize': parseInt(data_disk_size)})
    });
    return data_disk_list
}


// 收集所有购买服务器所需要的信息
function get_all_purchase_info() {
    let cmdb_project = $('#project').select2('data')[0].id;
    let InstanceChargeType = $('input[name=charge_mode]:checked').val();
    let Region = $('input[name=region]:checked').val();
    let Placement_Zone = $('input[name=zone]:checked').val();
    let Placement_ProjectId = $('#ProjectId').select2('data')[0].id;
    let InstanceType = $('#instance_type').select2('data')[0].id;
    let ImageId = $('#image_version').select2('data')[0].id;
    let SystemDisk_DiskType = $('input[name=system_disk]:checked').val();
    let SystemDisk_DiskSize = $('#SystemDiskSize').val();
    let DataDisks = get_data_disk_value_list();
    let InternetAccessible_InternetChargeType = $('input[name=network_charge_mode]:checked').val();
    let InternetAccessible_InternetMaxBandwidthOut = $('#InternetMaxBandwidthOut').val();
    let InternetAccessible_PublicIpAssigned = $('#PublicIpAssigned').prop('checked');
    let SecurityGroupIds = $('#SecurityGroupId').select2('data')[0].id;
    let InstanceName = $('#InstanceName').val();
    let LoginSettings_Password = '';
    let EnhancedService_SecurityService = $('#security_enhance').prop('checked');
    let EnhancedService_MonitorService = $('#cloud_monitor').prop('checked');
    let InstanceCount = $('#InstanceCount').val();
    let InstanceChargePrepaid_Period = $('input[name=period]:checked').val();
    let InstanceChargePrepaid_RenewFlag = $('input[id=RenewFlag]:checked').val();
    return {
        'cmdb_project': cmdb_project,
        'InstanceChargeType': InstanceChargeType,
        'Region': Region,
        'Placement': {
            'Zone': Placement_Zone,
            'ProjectId': parseInt(Placement_ProjectId),
        },
        'InstanceType': InstanceType,
        'ImageId': ImageId,
        'SystemDisk': {
            'DiskType': SystemDisk_DiskType,
            'DiskSize': parseInt(SystemDisk_DiskSize),
        },
        'DataDisks': DataDisks,
        'InternetAccessible': {
            'InternetChargeType': InternetAccessible_InternetChargeType,
            'InternetMaxBandwidthOut': parseInt(InternetAccessible_InternetMaxBandwidthOut),
            'PublicIpAssigned': InternetAccessible_PublicIpAssigned,
        },
        'SecurityGroupIds': [SecurityGroupIds],
        'InstanceName': InstanceName,
        'LoginSettings': {
            'Password': LoginSettings_Password,
        },
        'EnhancedService': {
            'SecurityService': {'Enabled': EnhancedService_SecurityService},
            'MonitorService': {'Enabled': EnhancedService_MonitorService},
        },
        'InstanceCount': parseInt(InstanceCount),
        'InstanceChargePrepaid': {
            'Period': parseInt(InstanceChargePrepaid_Period),
            'RenewFlag': InstanceChargePrepaid_RenewFlag,
        }
    }
}


// 发送询价请求
function inquiry_price() {
    var data = get_all_purchase_info();
    var encoded = $.toJSON(data);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/txcloud/inquiry_price/",
        data: pdata,
        async: true,
        contentType: "application/json; charset=utf-8",
        success: function (data) {
            let cost_data = data.data;
            if (cost_data.BandwidthPrice.OriginalPrice) {
                $('#bw_orginprice').text(cost_data.BandwidthPrice.OriginalPrice);
                $('#bw_discount').text(cost_data.BandwidthPrice.Discount);
                $('.bw_discountprice').text(cost_data.BandwidthPrice.DiscountPrice);
                $('#in_orginprice').text(cost_data.InstancePrice.OriginalPrice);
                $('#in_discount').text(cost_data.InstancePrice.Discount);
                $('.in_discountprice').text(cost_data.InstancePrice.DiscountPrice);
                $('#total_cost').text(parseInt(cost_data.BandwidthPrice.DiscountPrice) + parseInt(cost_data.InstancePrice.DiscountPrice));
            }
            if (cost_data.BandwidthPrice.UnitPrice) {
                $('#bw_orginprice').text('每' + cost_data.BandwidthPrice.ChargeUnit + ' ' + cost_data.BandwidthPrice.UnitPrice);
                $('#bw_discount').text(cost_data.BandwidthPrice.Discount);
                $('.bw_discountprice').text('每' + cost_data.BandwidthPrice.ChargeUnit + ' ' + cost_data.BandwidthPrice.UnitPriceDiscount);
                $('#in_orginprice').text(cost_data.InstancePrice.OriginalPrice);
                $('#in_discount').text(cost_data.InstancePrice.Discount);
                $('.in_discountprice').text(cost_data.InstancePrice.DiscountPrice);
                $('#total_cost').text(parseInt(cost_data.InstancePrice.DiscountPrice));
            }
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


// 取消增加的数据盘
function cancel_data_disk(e) {
    $(e).parent().parent().remove()
}


// 购买确认modal
function confirm_modal() {
    $('#modal_text').text('确定要立即购买服务器？');
    $('#purchase_button').show();
    $('#myModal').modal('show');
}


// 购买服务器
function purchase() {
    var data = get_all_purchase_info();
    let room = $('#room').select2('data')[0].id;
    let business = $('#business').select2('data')[0].id;
    data['room'] = room;
    data['business'] = business;
    var encoded = $.toJSON(data);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/txcloud/run_instance/",
        data: pdata,
        async: true,
        contentType: "application/json; charset=utf-8",
        beforeSend: function () {
            jQuery('#page-wrapper').showLoading();
        },
        success: function (data) {
            $('#purchase_button').hide();
            if (data.success) {
                $('#modal_text').text('提交成功');
                window.location.href = "/assets/host_initialize/"
            }
            else {
                $('#modal_text').text(data.data);
            }
            jQuery('#page-wrapper').hideLoading();

        },
        error: function (xhr, status, error) {
            if (xhr.status == '403') {
                alert('权限拒绝');
            } else {
                alert('内部错误');
            }
            jQuery('#page-wrapper').hideLoading();
        }
    });
}
