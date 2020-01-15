$(document).ready(function () {

    $.fn.select2.defaults.set("theme", "bootstrap");

    // 初始化select2
    $('#project').select2({placeholder: '请选择项目'});
    $('#area').select2({placeholder: '请选择地区'});
    $('#memory').select2({placeholder: '请选择实例规格'});
    $('#ProjectId').select2({placeholder: '请选择腾讯云项目'});
    $('#SecurityGroupId').select2({placeholder: '请选择安全组'});


    $("#project").on("select2:select", function () {
        // project改变时删除border警告样式
        $('#project').parent().removeClass('has-error');
        // 获取腾讯云帐号项目
        get_txcloud_project();
        // 获取腾讯云安全组
        get_security_group()
    });

    $("#area").on("select2:select", function () {
        // area改变时删除border警告样式
        $('#area').parent().removeClass('has-error');
    });

    $("#ProjectId").on("select2:select", function () {
        // ProjectId改变时删除border警告样式
        $('#ProjectId').parent().removeClass('has-error');
    });

    $("#SecurityGroupId").on("select2:select", function () {
        // SecurityGroupId改变时删除border警告样式
        $('#SecurityGroupId').parent().removeClass('has-error');
    });

    // 修改实例内存时，重新查询价格
    $("#memory").on("select2:select", function () {
        describe_db_price();
    });

    // 修改硬盘大小时，重新查询价格
    $('#volume').on("change", function () {
        describe_db_price()
    });

    // 修改购买数量时，重新查询价格
    $('#goods_num').on("change", function () {
        describe_db_price()
    });

    // purpose改变时删除border警告样式
    $('#purpose').on("change", function () {
        // purpose改变时删除border警告样式
        $('#purpose').parent().removeClass('has-error');
    });

    // 输入框获得焦点则删除border警告样式
    $("#volume").focus(function () {
        $('#volume').parent().removeClass('has-error');
    });


    // 重新获取云数据库可售的配置信息
    $.ajax({
        type: "POST",
        url: "/txcloud/get_mysql_config/",
        async: true,
        data: $.toJSON({}),
        beforeSend: function () {
            jQuery('#page-wrapper').showLoading();
        },
        success: function (data) {
            if (data.success) {
                get_mysql_region_from_db();
                get_mysql_zone_from_db();
                get_mysql_framework();
                get_mysql_engine();
                describe_db_price();
                $('.is_init').css('display', 'block');
                get_mysql_default_params();
                $('input:radio[name=is_init]').eq(0).prop('checked', true);
            }
            else {
                alert('获取云数据库配置信息失败' + data.data)
            }
        },
        error: function (xhr, status, error) {
            console.log('内部错误');
        },
        complete: function () {
            jQuery('#page-wrapper').hideLoading();
        }
    });


    // 监听是否初始化选项，展示初始化参数表单
    // $('input:radio[name=is_init]').change(function () {
    //     var is_init = $('input:radio[name=is_init]:checked').val();
    //     if (is_init == '1') {
    //         $('.is_init').css('display', 'block');
    //         get_mysql_default_params();
    //     }
    //     if (is_init == '0') {
    //         $('.is_init').css('display', 'none')
    //     }
    // });


    // 核对信息
    $('#purchase_info_check').click(function () {
        var cmdb_project = $('#project').select2('data')[0].text;
        var project_cloud_account = $('#project').select2('data')[0].title;
        var area = $('#area').select2('data')[0].text;
        var purpose = $('#purpose').val();
        var pay_type = $('input[name=pay_type]:checked').closest('li').find('.label_pay_type').text();
        var region = $('input[name=region]:checked').closest('li').find('.label_region').text();
        var zone = $('input[name=zone]:checked').closest('li').find('.label_zone').text();
        var engine_version = $('input[name=engine_version]:checked').closest('li').find('.label_engine_version').text();
        var memory = $('#memory').select2('data')[0].text;
        var volume = $('#volume').val();
        var protect_mode = $('input[name=protect_mode]:checked').closest('li').find('.label_protect_mode').text();
        var ProjectId = $('#ProjectId option:selected').text();
        var SecurityGroupId = $('#SecurityGroupId option:selected').text();
        var instance_name = $('#instance_name').val();
        var goods_num = $('#goods_num').val();
        var period = $('input[name=period]:checked').closest('li').find('.label_period').text();
        var auto_renew = $('#AutoRenewFlag:checked').val();
        if (auto_renew === '1') {
            auto_renew = '是'
        }
        else {
            auto_renew = '否'
        }
        var is_init = $('input[name=is_init]:checked').parent().text();
        var character = $('input[name=character_set_server]:checked').val();
        var lower_case_table_names = $('input[name=lower_case_table_names]:checked').parent().text();
        var port = $('#port').val();

        if (cmdb_project == '请选择项目') {
            $('#project').parent().addClass('has-error');
            $('.alert_text').text('请选择cmdb项目');
            $('.alert-danger').css('display', 'block');
            return false;
        }
        if (project_cloud_account == 0) {
            $('#project').parent().addClass('has-error');
            $('.alert_text').html('cmdb项目没有关联云帐号，请先到“<a class="alert-link" href="/assets/game_project_list/" target="_blank">游戏项目管理-项目列表</a>”中进行关联');
            $('.alert-danger').css('display', 'block');
            return false;
        }
        if (area == '请选择地区') {
            $('#area').parent().addClass('has-error');
            $('.alert_text').text('请选择地区');
            $('.alert-danger').css('display', 'block');
            return false;
        }
        if (!purpose) {
            $('#purpose').parent().addClass('has-error');
            $('.alert_text').text('请填写用途');
            $('.alert-danger').css('display', 'block');
            return false;
        }
        if (volume > 6000 || volume < 5) {
            $('#volume').parent().addClass('has-error');
            $('.alert_text').text('硬盘大小必须在5～6000之间');
            $('.alert-danger').css('display', 'block');
            return false;
        }
        if (!ProjectId) {
            $('#ProjectId').parent().addClass('has-error');
            $('.alert_text').text('请选择腾讯云项目');
            $('.alert-danger').css('display', 'block');
            return false;
        }
        if (!SecurityGroupId) {
            $('#SecurityGroupId').parent().addClass('has-error');
            $('.alert_text').text('请选择安全组');
            $('.alert-danger').css('display', 'block');
            return false;
        }
        if (!is_init) {
            $('.alert_text').text('请选择是否初始化');
            $('.alert-danger').css('display', 'block');
            return false;
        }
        if (is_init.indexOf('是') != -1) {
            if (!character) {
                $('.alert_text').text('请选择支持字符集');
                $('.alert-danger').css('display', 'block');
                return false;
            }
            if (!lower_case_table_names) {
                $('.alert_text').text('请选择是否大小写敏感');
                $('.alert-danger').css('display', 'block');
                return false;
            }
            if (!port) {
                $('.alert_text').text('请填写自定义端口');
                $('.alert-danger').css('display', 'block');
                return false;
            }
            if (port > 65535 || port < 1024) {
                $('.alert_text').text('自定义端口必须在1024～65535之间');
                $('.alert-danger').css('display', 'block');
                return false;
            }
        }

        $('#info_cmdb_project').text(cmdb_project);
        $('#info_area').text(area);
        $('#info_purpose').text(purpose);
        $('#info_pay_type').text(pay_type);
        $('#info_region').text(region);
        $('#info_zone').text(zone);
        $('#info_engine_version').text(engine_version);
        $('#info_configs').text(memory + '内存，' + volume + 'GB存储空间');
        $('#info_protect_mode').text(protect_mode);
        $('#info_ProjectId').text(ProjectId);
        $('#info_SecurityGroupId').text(SecurityGroupId);
        $('#info_instance_name').text(instance_name);
        $('#info_goods_num').text(goods_num);
        $('#info_period').text(period);
        $('#info_is_init').text(is_init);
        $('#info_character').text(character);
        $('#info_lower_case_table_names').text(lower_case_table_names);
        $('#info_port').text(port);
        $('#info_auto_renew').text(auto_renew);

        $('#myModal').modal('show');
    });


    // 确认购买
    $('#purchase_action').click(function () {
        var cmdb_project = $('#project').select2('data')[0].id;
        var area = $('#area').select2('data')[0].id;
        var purpose = $('#purpose').val();
        var pay_type = $('input[name=pay_type]:checked').val();
        var region = $('input[name=region]:checked').val();
        var zone = $('input[name=zone]:checked').val();
        var engine_version = $('input[name=engine_version]:checked').val();
        var memory = $('#memory').select2('data')[0].id;
        var volume = $('#volume').val();
        var protect_mode = $('input[name=protect_mode]:checked').val();
        var ProjectId = $('#ProjectId option:selected').val();
        var SecurityGroupId = $('#SecurityGroupId option:selected').val();
        var instance_name = $('#instance_name').val();
        var goods_num = $('#goods_num').val();
        var period = $('input[name=period]:checked').val();
        var is_init = $('input[name=is_init]:checked').val();
        var character = $('input[name=character_set_server]:checked').val();
        var lower_case_table_names = $('input[name=lower_case_table_names]:checked').val();
        var port = $('#port').val();
        var AutoRenewFlag = $('#AutoRenewFlag:checked').val();
        if (AutoRenewFlag === '1') {
            AutoRenewFlag = 1
        }
        else {
            AutoRenewFlag = 0
        }

        var inputIds = {
            'cmdb_project': cmdb_project,
            'area': area,
            'purpose': purpose,
            'pay_type': pay_type,
            'region': region,
            'Zone': zone,
            'EngineVersion': engine_version,
            'Memory': parseInt(memory),
            'Volume': parseInt(volume),
            'ProtectMode': parseInt(protect_mode),
            'ProjectId': parseInt(ProjectId),
            'SecurityGroup': [SecurityGroupId],
            'InstanceName': instance_name,
            'GoodsNum': parseInt(goods_num),
            'Period': parseInt(period),
            'is_init': is_init,
            'character_set_server': character,
            'lower_case_table_names': parseInt(lower_case_table_names),
            'Port': parseInt(port),
            'AutoRenewFlag': AutoRenewFlag,
        };
        var encoded = $.toJSON(inputIds);
        var pdata = encoded;
        $.ajax({
            type: "POST",
            url: "/txcloud/create_txcloud_mysql/",
            async: true,
            data: pdata,
            beforeSend: function () {
                jQuery('#page-wrapper').showLoading();
            },
            success: function (data) {
                if (data.success) {
                    alert('提交成功');
                    window.location.href = '/mysql/instance/';
                }
                else {
                    alert('提交失败： ' + data.data)
                }
            },
            error: function (xhr, status, error) {
                if (xhr.status == '403') {
                    alert('权限拒绝');
                } else {
                    alert('内部错误');
                }
            },
            complete: function () {
                jQuery('#page-wrapper').hideLoading();
            },
        });
    })

});


function get_mysql_region_from_db() {
    // 获取地域
    $.ajax({
        type: "POST",
        url: "/txcloud/get_mysql_region/",
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

}

function get_mysql_zone_from_db() {
    //  获取可用区
    var region_code = $('input[name=region]:checked').val();
    var inputIds = {
        'region_code': region_code,
    };
    var encoded = $.toJSON(inputIds);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/txcloud/get_mysql_zone/",
        async: false,
        data: pdata,
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


function get_mysql_framework() {
    // 获取数据库架构
    var region = $('input[name=region]:checked').val();
    var zone = $('input[name=zone]:checked').val();
    var inputIds = {
        'region': region,
        'zone': zone,
    };
    var encoded = $.toJSON(inputIds);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/txcloud/get_mysql_framework/",
        async: false,
        data: pdata,
        success: function (data) {
            if (data.success) {
                var framework = data.data;
                $('#framework').html('');
                for (let i of framework) {
                    if (i == '高可用版') {
                        var html = '<li>' +
                            '<input checked type="radio" name="framework" id="' + i + '" value="' + i + '"/>' +
                            '<label class="label_framework" for="' + i + '">' + i + '</label>' +
                            '</li>';
                    }
                    // API不支持购买基础版数据库
                    // else {
                    //     var html = '<li>' +
                    //         '<input type="radio" name="framework" id="' + i + '" value="' + i + '"/>' +
                    //         '<label class="label_framework" for="' + i + '">' + i + '</label>' +
                    //         '</li>';
                    // }
                    $('#framework').append(html)
                }
            }
            else {
                alert(data.data);
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
}


function get_mysql_engine() {
    // 获取数据库版本
    var region = $('input[name=region]:checked').val();
    var zone = $('input[name=zone]:checked').val();
    var framework = $('input[name=framework]:checked').val();
    var inputIds = {
        'region': region,
        'zone': zone,
        'framework': framework,
    };
    var encoded = $.toJSON(inputIds);
    var pdata = encoded;
    $.ajax({
        type: "POST",
        url: "/txcloud/get_mysql_engine/",
        async: false,
        data: pdata,
        success: function (data) {
            if (data.success) {
                // 数据库版本
                var engine_version = data.data.engine_version;
                $('#engine_version').html('');
                for (let i of engine_version) {
                    if (i == '5.7') {
                        var html = '<li>' +
                            '<input checked type="radio" name="engine_version" id="' + i + '" value="' + i + '"/>' +
                            '<label class="label_engine_version" for="' + i + '">MySQL' + i + '</label>' +
                            '</li>';
                    }
                    else {
                        var html = '<li>' +
                            '<input type="radio" name="engine_version" id="' + i + '" value="' + i + '"/>' +
                            '<label class="label_engine_version" for="' + i + '">MySQL' + i + '</label>' +
                            '</li>';
                    }
                    $('#engine_version').append(html)
                }
                // 数据复制方式
                var protect_mode = data.data.protect_mode;
                $('#protect_mode').html('');
                for (let i of protect_mode) {
                    if (i == '0') {
                        var protect = '异步复制'
                    }
                    else if (i == '1') {
                        var protect = '半同步复制'
                    }
                    else if (i == '2') {
                        var protect = '强同步复制'
                    }
                    if (i == '0') {
                        var html = '<li>' +
                            '<input checked type="radio" name="protect_mode" id="' + i + '" value="' + i + '"/>' +
                            '<label class="label_protect_mode" for="' + i + '">' + protect + '</label>' +
                            '</li>';
                    }
                    else {
                        var html = '<li>' +
                            '<input type="radio" name="protect_mode" id="' + i + '" value="' + i + '"/>' +
                            '<label class="label_protect_mode" for="' + i + '">' + protect + '</label>' +
                            '</li>';
                    }
                    $('#protect_mode').append(html)
                }
                // 数据库cpu内存配置
                $("#memory").html("");
                var configs = data.data.configs;
                for (let i in configs) {
                    if ($('#memory').find("option[value='" + configs[i].memory + "']").length) {
                        $('#memory').val(data.id)
                    } else {
                        // Create a DOM Option and pre-select by default
                        var newOption = new Option(configs[i].cpu + '核' + configs[i].memory + 'MB', configs[i].memory, false, false);
                        // Append it to the select
                        $('#memory').append(newOption);
                        if (i == 0) {
                            $('#memory').val(configs[i].memory).trigger('change');
                        }
                    }
                }
            }
            else {
                alert(data.data);
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
}


// 当选择地域时，根据地域获取可用区
$(document).on("click", ".label_region", function () {
    $(this).closest('li').find("input[name=region]").prop('checked', true);
    var region_code = $(this).closest('li').find("input[name=region]").val();
    var inputIds = {
        'region_code': region_code,
    };
    var encoded = $.toJSON(inputIds);
    var pdata = encoded;
    $('#div_protect_mode').css('display', 'block');
    $.ajax({
        type: "POST",
        url: "/txcloud/get_mysql_zone/",
        async: false,
        data: pdata,
        success: function (data) {
            var origin_data = data.data;
            if (data.success) {
                $('#zone').html('');
                for (let i in origin_data) {
                    if (i == '0') {
                        let zone_data = origin_data[i];
                        var html = '<li>' +
                            '<input checked type="radio" name="zone" id="' + zone_data.zone + '" value="' + zone_data.zone + '"/>' +
                            '<label class="label_zone" for="' + zone_data.zone + '">' + zone_data.zone_name + '</label>' +
                            '</li>';
                    }
                    else {
                        let zone_data = origin_data[i];
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
        },
        error: function (xhr, status, error) {
            if (xhr.status == '403') {
                alert('权限拒绝');
            } else {
                alert('内部错误');
            }
        }
    });

    // 更新价格
    describe_db_price();

});


// 当选择可用区时，获取架构
$(document).on("click", ".label_zone", function () {
    $(this).closest('li').find("input[name=zone]").prop('checked', true);
    var zone = $(this).closest('li').find("input[name=zone]").val();
    var region = $('input[name=region]:checked').val();
    var inputIds = {
        'region': region,
        'zone': zone,
    };
    var encoded = $.toJSON(inputIds);
    var pdata = encoded;
    $('#div_protect_mode').css('display', 'block');
    $.ajax({
        type: "POST",
        url: "/txcloud/get_mysql_framework/",
        async: false,
        data: pdata,
        success: function (data) {
            if (data.success) {
                var framework = data.data;
                $('#framework').html('');
                for (let i of framework) {
                    if (i == '高可用版') {
                        var html = '<li>' +
                            '<input checked type="radio" name="framework" id="' + i + '" value="' + i + '"/>' +
                            '<label class="label_framework" for="' + i + '">' + i + '</label>' +
                            '</li>';
                    }
                    // API不支持购买基础版数据库
                    // else {
                    //     var html = '<li>' +
                    //         '<input type="radio" name="framework" id="' + i + '" value="' + i + '"/>' +
                    //         '<label class="label_framework" for="' + i + '">' + i + '</label>' +
                    //         '</li>';
                    // }
                    $('#framework').append(html)
                }
                // 重新获取数据库版本
                get_mysql_engine();
            }
            else {
                alert(data.data);
                console.log(data.data)
            }
        },
        error: function (xhr, status, error) {
            if (xhr.status == '403') {
                alert('权限拒绝');
            } else {
                alert('内部错误');
            }
        },
    });

    // 更新价格
    describe_db_price();

});


// 当选择架构时，获取其他配置信息
$(document).on("click", ".label_framework", function () {
    $(this).closest('li').find("input[name=framework]").prop('checked', true);
    var framework = $(this).closest('li').find("input[name=framework]").val();
    var region = $('input[name=region]:checked').val();
    var zone = $('input[name=zone]:checked').val();
    var inputIds = {
        'region': region,
        'zone': zone,
        'framework': framework,
    };
    var encoded = $.toJSON(inputIds);
    var pdata = encoded;
    // 默认选择异步复制方式
    if (framework == '基础版') {
        $('input[name=protect_mode][value="0"]').prop('checked', true);
        $('#div_protect_mode').css('display', 'none');
    }
    else {
        $('#div_protect_mode').css('display', 'block');
    }

    $.ajax({
        type: "POST",
        url: "/txcloud/get_mysql_engine/",
        async: false,
        data: pdata,
        success: function (data) {
            if (data.success) {
                // 数据库版本
                var engine_version = data.data.engine_version;
                $('#engine_version').html('');
                for (let i of engine_version) {
                    if (i == '5.7') {
                        var html = '<li>' +
                            '<input checked type="radio" name="engine_version" id="' + i + '" value="' + i + '"/>' +
                            '<label class="label_engine_version" for="' + i + '">MySQL' + i + '</label>' +
                            '</li>';
                    }
                    else {
                        var html = '<li>' +
                            '<input type="radio" name="engine_version" id="' + i + '" value="' + i + '"/>' +
                            '<label class="label_engine_version" for="' + i + '">MySQL' + i + '</label>' +
                            '</li>';
                    }
                    $('#engine_version').append(html)
                }
                // 数据库cpu内存配置
                $("#memory").html("");
                var configs = data.data.configs;
                for (let i in configs) {
                    if ($('#memory').find("option[value='" + configs[i].memory + "']").length) {
                        $('#memory').val(data.id)
                    } else {
                        // Create a DOM Option and pre-select by default
                        var newOption = new Option(configs[i].cpu + '核' + configs[i].memory + 'MB', configs[i].memory, false, false);
                        // Append it to the select
                        $('#memory').append(newOption);
                        if (i == 0) {
                            $('#memory').val(configs[i].memory).trigger('change');
                        }
                    }
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

    // 更新价格
    describe_db_price();

});


// 当选择数据复制方式时，重新查询价格
$(document).on("click", ".label_protect_mode", function () {
    $(this).closest('li').find("input[name=protect_mode]").prop('checked', true);
    describe_db_price();
});


// 当选择购买时长时，重新查询价格
$(document).on("click", ".label_period", function () {
    $(this).closest('li').find("input[name=period]").prop('checked', true);
    describe_db_price();
});


// 当选择计费模式时，重新查询价格
$(document).on("click", ".label_pay_type", function () {
    $(this).closest('li').find("input[name=pay_type]").prop('checked', true);
    describe_db_price();
});


// 获取购买数据库实例价格
function describe_db_price() {
    var project = $('#project').val();
    var region = $('input[name="region"]:checked').val();
    var zone = $('input[name="zone"]:checked').val();
    var goods_num = $('#goods_num').val();
    var memory = $('#memory').val();
    var volume = $('#volume').val();
    var pay_type = $('input[name="pay_type"]:checked').val();
    var period = $('input[name="period"]:checked').val();
    var protect_mode = $('input[name="protect_mode"]:checked').val();
    var inputIds = {
        'project': project,
        'region': region,
        'Zone': zone,
        'GoodsNum': parseInt(goods_num),
        'Memory': parseInt(memory),
        'Volume': parseInt(volume),
        'PayType': pay_type,
        'Period': parseInt(period),
        'ProtectMode': parseInt(protect_mode),
    };
    var encoded = $.toJSON(inputIds);
    var pdata = encoded;

    $.ajax({
        type: "POST",
        url: "/txcloud/get_mysql_price/",
        async: true,
        data: pdata,
        success: function (data) {
            if (pay_type == 'PRE_PAID') {
                $('#config_price').text(data.data.Price + ' 元')
            }
            else if (pay_type == 'HOUR_PAID') {
                $('#config_price').text(data.data.Price + ' 元/小时')
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


// 获取腾讯云帐号中项目列表数据
function get_txcloud_project() {
    var project = $('#project').select2('data')[0].id;
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
            $('#ProjectId').html('');
            var newOption = new Option('', '0', false, false);
            $('#ProjectId').append(newOption);
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


// 异步获取安全组数据
function get_security_group() {
    var project = $('#project').select2('data')[0].id;
    var region_code = $('input[name=region]:checked').val();
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
            $('#SecurityGroupId').html('');
            var newOption = new Option('', '0', false, false);
            $('#SecurityGroupId').append(newOption);
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

// 获取腾讯云mysql初始化参数
function get_mysql_default_params() {
    // 获取地域
    $.ajax({
        type: "POST",
        url: "/txcloud/get_mysql_default_params/",
        async: true,
        data: $.toJSON({
            'project': $('#project').select2('data')[0].id,
            'Region': $('input[name=region]:checked').val(),
            'EngineVersion': $('input[name=engine_version]:checked').val()
        }),
        beforeSend: function () {
            jQuery('#page-wrapper').showLoading();
        },
        success: function (data) {
            if (data.success) {
                var char_data = data.data.value;
                var html = '';
                for (let i of char_data) {
                    html += '<label>' +
                        '<input type="radio" value="' + i + '" name="character_set_server">' + i +
                        '</label>&nbsp;&nbsp;&nbsp;'
                }
                $('#character').append(html)
            }
            else {
                console.log(data.data)
            }
        },
        error: function (xhr, status, error) {
            console.log('内部错误');
        },
        complete: function () {
            jQuery('#page-wrapper').hideLoading();
        },
    })

}
