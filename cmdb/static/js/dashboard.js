var hot_update_pie = echarts.init(document.getElementById('hot_update_pie'));
var host_migrate_pie = echarts.init(document.getElementById('host_migrate_pie'));
var host_recover_pie = echarts.init(document.getElementById('host_recover_pie'));
var game_server_off_pie = echarts.init(document.getElementById('game_server_off_pie'));
var modsrv_opentime_pie = echarts.init(document.getElementById('modsrv_opentime_pie'));
var system_cron_pie = echarts.init(document.getElementById('system_cron_pie'));
var game_server_action_pie = echarts.init(document.getElementById('game_server_action_pie'));
var host_initialize_pie = echarts.init(document.getElementById('host_initialize_pie'));
var game_server_merge_pie = echarts.init(document.getElementById('game_server_merge_pie'));
var game_server_install_pie = echarts.init(document.getElementById('game_server_install_pie'));
var version_update_pie = echarts.init(document.getElementById('version_update_pie'));


function function_hot_update_pie() {
    $.ajax({
            type: "post",
            async: true,
            url: "/dashboard/hot_update_pie/",
            dataType: "json",
            beforeSend: function () {
                jQuery('#hot_update_pie').showLoading();
            },
            success: function (result) {
                let data_list = result['data_list'];
                let legend = result['legend'];
                let text = result['text'];
                let subtext = result['subtext'];
                let option = {
                    title: {
                        text: text,
                        subtext: subtext,
                        x: 'center'
                    },
                    tooltip: {
                        trigger: 'item',
                        formatter: "{a} <br/>{b} : {c} ({d}%)"
                    },
                    legend: {
                        orient: 'vertical',
                        left: 'left',
                        data: legend,
                    },
                    series: [
                        {
                            name: '比例',
                            type: 'pie',
                            radius: '60%',
                            center: ['50%', '60%'],
                            data: data_list,
                            itemStyle: {
                                emphasis: {
                                    shadowBlur: 10,
                                    shadowOffsetX: 0,
                                    shadowColor: 'rgba(0, 0, 0, 0.5)'
                                }
                            }
                        }
                    ]
                };
                hot_update_pie.setOption(option);
                jQuery('#hot_update_pie').hideLoading();
            },
            error: function (errorMsg) {
                jQuery('#hot_update_pie').hideLoading();
            }
        });
}


function function_version_update_pie() {
    $.ajax({
        type: "post",
        async: true,
        url: "/dashboard/version_update_pie/",
        dataType: "json",
        beforeSend: function () {
            jQuery('#version_update_pie').showLoading();
        },
        success: function (result) {
            let data_list = result['data_list'];
            let legend = result['legend'];
            let text = result['text'];
            let subtext = result['subtext'];
            let option = {
                title: {
                    text: text,
                    subtext: subtext,
                    x: 'center'
                },
                tooltip: {
                    trigger: 'item',
                    formatter: "{a} <br/>{b} : {c} ({d}%)"
                },
                legend: {
                    orient: 'vertical',
                    left: 'left',
                    data: legend,
                },
                series: [
                    {
                        name: '比例',
                        type: 'pie',
                        radius: '60%',
                        center: ['50%', '60%'],
                        data: data_list,
                        itemStyle: {
                            emphasis: {
                                shadowBlur: 10,
                                shadowOffsetX: 0,
                                shadowColor: 'rgba(0, 0, 0, 0.5)'
                            }
                        }
                    }
                ]
            };
            version_update_pie.setOption(option);
            jQuery('#version_update_pie').hideLoading();
        },
        error: function (errorMsg) {
            jQuery('#version_update_pie').hideLoading();
        }
    });
}


function function_host_migration_pie() {
    $.ajax({
        type: "post",
        async: true,
        url: "/dashboard/host_migrate_pie/",
        dataType: "json",
        beforeSend: function () {
            jQuery('#host_migrate_pie').showLoading();
        },
        success: function (result) {
            let data_list = result['data_list'];
            let legend = result['legend'];
            let text = result['text'];
            let subtext = result['subtext'];
            let option = {
                title: {
                    text: text,
                    subtext: subtext,
                    x: 'center'
                },
                tooltip: {
                    trigger: 'item',
                    formatter: "{a} <br/>{b} : {c} ({d}%)"
                },
                legend: {
                    orient: 'vertical',
                    left: 'left',
                    data: legend,
                },
                series: [
                    {
                        name: '比例',
                        type: 'pie',
                        radius: '60%',
                        center: ['50%', '60%'],
                        data: data_list,
                        itemStyle: {
                            emphasis: {
                                shadowBlur: 10,
                                shadowOffsetX: 0,
                                shadowColor: 'rgba(0, 0, 0, 0.5)'
                            }
                        }
                    }
                ]
            };
            host_migrate_pie.setOption(option);
            jQuery('#host_migrate_pie').hideLoading();
        },
        error: function (errorMsg) {
            jQuery('#host_migrate_pie').hideLoading();
        }
    });
}


function function_host_recover_pie() {
    $.ajax({
        type: "post",
        async: true,
        url: "/dashboard/host_recover_pie/",
        dataType: "json",
        beforeSend: function () {
            jQuery('#host_recover_pie').showLoading();
        },
        success: function (result) {
            let data_list = result['data_list'];
            let legend = result['legend'];
            let text = result['text'];
            let subtext = result['subtext'];
            let option = {
                title: {
                    text: text,
                    subtext: subtext,
                    x: 'center'
                },
                tooltip: {
                    trigger: 'item',
                    formatter: "{a} <br/>{b} : {c} ({d}%)"
                },
                legend: {
                    orient: 'vertical',
                    left: 'left',
                    data: legend,
                },
                series: [
                    {
                        name: '比例',
                        type: 'pie',
                        radius: '60%',
                        center: ['50%', '60%'],
                        data: data_list,
                        itemStyle: {
                            emphasis: {
                                shadowBlur: 10,
                                shadowOffsetX: 0,
                                shadowColor: 'rgba(0, 0, 0, 0.5)'
                            }
                        }
                    }
                ]
            };
            host_recover_pie.setOption(option);
            jQuery('#host_recover_pie').hideLoading();
        },
        error: function (errorMsg) {
            jQuery('#host_recover_pie').hideLoading();
        }
    });
}


function function_game_server_off_pie() {
    $.ajax({
        type: "post",
        async: true,
        url: "/dashboard/game_server_off_pie/",
        dataType: "json",
        beforeSend: function () {
            jQuery('#game_server_off_pie').showLoading();
        },
        success: function (result) {
            let data_list = result['data_list'];
            let legend = result['legend'];
            let text = result['text'];
            let subtext = result['subtext'];
            let option = {
                title: {
                    text: text,
                    subtext: subtext,
                    x: 'center'
                },
                tooltip: {
                    trigger: 'item',
                    formatter: "{a} <br/>{b} : {c} ({d}%)"
                },
                legend: {
                    orient: 'vertical',
                    left: 'left',
                    data: legend,
                },
                series: [
                    {
                        name: '比例',
                        type: 'pie',
                        radius: '60%',
                        center: ['50%', '60%'],
                        data: data_list,
                        itemStyle: {
                            emphasis: {
                                shadowBlur: 10,
                                shadowOffsetX: 0,
                                shadowColor: 'rgba(0, 0, 0, 0.5)'
                            }
                        }
                    }
                ]
            };
            game_server_off_pie.setOption(option);
            jQuery('#game_server_off_pie').hideLoading();
        },
        error: function (errorMsg) {
            jQuery('#game_server_off_pie').hideLoading();
        }
    });
}


function function_modsrv_opentime_pie() {
    $.ajax({
        type: "post",
        async: true,
        url: "/dashboard/modsrv_opentime_pie/",
        dataType: "json",
        beforeSend: function () {
            jQuery('#modsrv_opentime_pie').showLoading();
        },
        success: function (result) {
            let data_list = result['data_list'];
            let legend = result['legend'];
            let text = result['text'];
            let subtext = result['subtext'];
            let option = {
                title: {
                    text: text,
                    subtext: subtext,
                    x: 'center'
                },
                tooltip: {
                    trigger: 'item',
                    formatter: "{a} <br/>{b} : {c} ({d}%)"
                },
                legend: {
                    orient: 'vertical',
                    left: 'left',
                    data: legend,
                },
                series: [
                    {
                        name: '比例',
                        type: 'pie',
                        radius: '60%',
                        center: ['50%', '60%'],
                        data: data_list,
                        itemStyle: {
                            emphasis: {
                                shadowBlur: 10,
                                shadowOffsetX: 0,
                                shadowColor: 'rgba(0, 0, 0, 0.5)'
                            }
                        }
                    }
                ]
            };
            modsrv_opentime_pie.setOption(option);
            jQuery('#modsrv_opentime_pie').hideLoading();
        },
        error: function (errorMsg) {
            jQuery('#modsrv_opentime_pie').hideLoading();
        }
    });
}


function function_system_cron_pie() {
    $.ajax({
        type: "post",
        async: true,
        url: "/dashboard/system_cron_pie/",
        dataType: "json",
        beforeSend: function () {
            jQuery('#system_cron_pie').showLoading();
        },
        success: function (result) {
            let data_list = result['data_list'];
            let legend = result['legend'];
            let text = result['text'];
            let subtext = result['subtext'];
            let option = {
                title: {
                    text: text,
                    subtext: subtext,
                    x: 'center'
                },
                tooltip: {
                    trigger: 'item',
                    formatter: "{a} <br/>{b} : {c} ({d}%)"
                },
                legend: {
                    orient: 'vertical',
                    left: 'left',
                    data: legend,
                },
                series: [
                    {
                        name: '比例',
                        type: 'pie',
                        radius: '60%',
                        center: ['50%', '60%'],
                        data: data_list,
                        itemStyle: {
                            emphasis: {
                                shadowBlur: 10,
                                shadowOffsetX: 0,
                                shadowColor: 'rgba(0, 0, 0, 0.5)'
                            }
                        }
                    }
                ]
            };
            system_cron_pie.setOption(option);
            jQuery('#system_cron_pie').hideLoading();
        },
        error: function (errorMsg) {
            jQuery('#system_cron_pie').hideLoading();
        }
    });
}


function function_game_server_action_pie() {
    $.ajax({
        type: "post",
        async: true,
        url: "/dashboard/game_server_action_pie/",
        dataType: "json",
        beforeSend: function () {
            jQuery('#game_server_action_pie').showLoading();
        },
        success: function (result) {
            let data_list = result['data_list'];
            let legend = result['legend'];
            let text = result['text'];
            let subtext = result['subtext'];
            let option = {
                title: {
                    text: text,
                    subtext: subtext,
                    x: 'center'
                },
                tooltip: {
                    trigger: 'item',
                    formatter: "{a} <br/>{b} : {c} ({d}%)"
                },
                legend: {
                    orient: 'vertical',
                    left: 'left',
                    data: legend,
                },
                series: [
                    {
                        name: '比例',
                        type: 'pie',
                        radius: '60%',
                        center: ['50%', '60%'],
                        data: data_list,
                        itemStyle: {
                            emphasis: {
                                shadowBlur: 10,
                                shadowOffsetX: 0,
                                shadowColor: 'rgba(0, 0, 0, 0.5)'
                            }
                        }
                    }
                ]
            };
            game_server_action_pie.setOption(option);
            jQuery('#game_server_action_pie').hideLoading();
        },
        error: function (errorMsg) {
            jQuery('#game_server_action_pie').hideLoading();
        }
    });
}


function function_host_initialize_pie() {
    $.ajax({
        type: "post",
        async: true,
        url: "/dashboard/host_initialize_pie/",
        dataType: "json",
        beforeSend: function () {
            jQuery('#host_initialize_pie').showLoading();
        },
        success: function (result) {
            let data_list = result['data_list'];
            let legend = result['legend'];
            let text = result['text'];
            let subtext = result['subtext'];
            let option = {
                title: {
                    text: text,
                    subtext: subtext,
                    x: 'center'
                },
                tooltip: {
                    trigger: 'item',
                    formatter: "{a} <br/>{b} : {c} ({d}%)"
                },
                legend: {
                    orient: 'vertical',
                    left: 'left',
                    data: legend,
                },
                series: [
                    {
                        name: '比例',
                        type: 'pie',
                        radius: '60%',
                        center: ['50%', '60%'],
                        data: data_list,
                        itemStyle: {
                            emphasis: {
                                shadowBlur: 10,
                                shadowOffsetX: 0,
                                shadowColor: 'rgba(0, 0, 0, 0.5)'
                            }
                        }
                    }
                ]
            };
            host_initialize_pie.setOption(option);
            jQuery('#host_initialize_pie').hideLoading();
        },
        error: function (errorMsg) {
            jQuery('#host_initialize_pie').hideLoading();
        }
    });
}


function function_game_server_merge_pie() {
    $.ajax({
        type: "post",
        async: true,
        url: "/dashboard/game_server_merge_pie/",
        dataType: "json",
        beforeSend: function () {
            jQuery('#game_server_merge_pie').showLoading();
        },
        success: function (result) {
            let data_list = result['data_list'];
            let legend = result['legend'];
            let text = result['text'];
            let subtext = result['subtext'];
            let option = {
                title: {
                    text: text,
                    subtext: subtext,
                    x: 'center'
                },
                tooltip: {
                    trigger: 'item',
                    formatter: "{a} <br/>{b} : {c} ({d}%)"
                },
                legend: {
                    orient: 'vertical',
                    left: 'left',
                    data: legend,
                },
                series: [
                    {
                        name: '比例',
                        type: 'pie',
                        radius: '60%',
                        center: ['50%', '60%'],
                        data: data_list,
                        itemStyle: {
                            emphasis: {
                                shadowBlur: 10,
                                shadowOffsetX: 0,
                                shadowColor: 'rgba(0, 0, 0, 0.5)'
                            }
                        }
                    }
                ]
            };
            game_server_merge_pie.setOption(option);
            jQuery('#game_server_merge_pie').hideLoading();
        },
        error: function (errorMsg) {
            jQuery('#game_server_merge_pie').hideLoading();
        }
    });
}


function function_game_serve_install_pie() {
    $.ajax({
        type: "post",
        async: true,
        url: "/dashboard/game_server_install_pie/",
        dataType: "json",
        beforeSend: function () {
            jQuery('#game_server_install_pie').showLoading();
        },
        success: function (result) {
            let data_list = result['data_list'];
            let legend = result['legend'];
            let text = result['text'];
            let subtext = result['subtext'];
            let option = {
                title: {
                    text: text,
                    subtext: subtext,
                    x: 'center'
                },
                tooltip: {
                    trigger: 'item',
                    formatter: "{a} <br/>{b} : {c} ({d}%)"
                },
                legend: {
                    orient: 'vertical',
                    left: 'left',
                    data: legend,
                },
                series: [
                    {
                        name: '比例',
                        type: 'pie',
                        radius: '60%',
                        center: ['50%', '60%'],
                        data: data_list,
                        itemStyle: {
                            emphasis: {
                                shadowBlur: 10,
                                shadowOffsetX: 0,
                                shadowColor: 'rgba(0, 0, 0, 0.5)'
                            }
                        }
                    }
                ]
            };
            game_server_install_pie.setOption(option);
            jQuery('#game_server_install_pie').hideLoading();
        },
        error: function (errorMsg) {
            jQuery('#game_server_install_pie').hideLoading();
        }
    });
}


$(document).ready(function () {

    //热更新(每隔30秒异步刷新)
    function_hot_update_pie();
    setInterval(function () {
        function_hot_update_pie();
    }, 60000);

    // 给热更新饼图绑定点击事件
    hot_update_pie.on('click', function (param) {
        let url = param.data.url;
        window.location.href = url;
    });

    //版本更新(每隔30秒异步刷新)
    function_version_update_pie();
    setInterval(function () {
        function_version_update_pie();
    }, 60000);

    //主机迁服(每隔30秒异步刷新)
    function_host_migration_pie();
    setInterval(function () {
        function_host_migration_pie();
    }, 60000);

    // 给主机迁服图绑定点击事件
    host_migrate_pie.on('click', function (param) {
        let url = param.data.url;
        window.location.href = url;
    });

    //主机回收(每隔30秒异步刷新)
    function_host_recover_pie();
    setInterval(function () {
        function_host_recover_pie();
    }, 60000);


    // 给主机回收图绑定点击事件
    host_recover_pie.on('click', function (param) {
        let url = param.data.url;
        window.location.href = url;
    });

    //区服下架(每隔30秒异步刷新)
    function_game_server_off_pie();
    setInterval(function () {
        function_game_server_off_pie();
    }, 60000);

    // 给区服下架图绑定点击事件
    game_server_off_pie.on('click', function (param) {
        let url = param.data.url;
        window.location.href = url;
    });

    //修改开服时间(每隔30秒异步刷新)
    function_modsrv_opentime_pie();
    setInterval(function () {
        function_modsrv_opentime_pie();
    }, 60000);

    // 给修改开服时间图绑定点击事件
    modsrv_opentime_pie.on('click', function (param) {
        let url = param.data.url;
        window.location.href = url;
    });

    //系统作业(每隔30秒异步刷新)
    function_system_cron_pie();
    setInterval(function () {
        function_system_cron_pie();
    }, 60000);


    // 给系统作业图绑定点击事件
    system_cron_pie.on('click', function (param) {
        let url = param.data.url;
        window.location.href = url;
    });

    //区服管理操作(每隔30秒异步刷新)
    function_game_server_action_pie();
    setInterval(function () {
        function_game_server_action_pie();
    }, 60000);

    // 给区服管理操作图绑定点击事件
    game_server_action_pie.on('click', function (param) {
        let url = param.data.url;
        window.location.href = url;
    });

    //主机初始化(每隔30秒异步刷新)
    function_host_initialize_pie();
    setInterval(function () {
        function_host_initialize_pie();
    }, 60000);

    //合服计划(每隔30秒异步刷新)
    function_game_server_merge_pie();
    setInterval(function () {
        function_game_server_merge_pie();
    }, 60000);

    //装服计划(每隔30秒异步刷新)
    function_game_serve_install_pie();
    setInterval(function () {
        function_game_serve_install_pie();
    }, 60000);


});
