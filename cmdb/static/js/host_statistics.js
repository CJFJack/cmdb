var app = {};
var host_statistics_by_project_chart = echarts.init(document.getElementById("host_statistics_by_project_chart"), 'dark');
var host_statistics_by_room_chart = echarts.init(document.getElementById("host_statistics_by_room_chart"), 'dark');


$(document).ready(function () {

    // 按项目统计
    $.ajax({
        type: "post",
        async: true,
        url: "/assets/host_statistics_by_project_chart/",
        dataType: "json",
        beforeSend: function () {
            host_statistics_by_project_chart.showLoading();
        },
        success: function (result) {
            if (result.success) {
                let data = result.data;
                let tile = data.title;
                let legend_data = data.legend_data;
                let yAxis_data = data.yAxis_data;
                let series = data.series;
                let option = null;
                app.title = tile;

                option = {
                    tooltip: {
                        trigger: 'axis',
                        axisPointer: {            // 坐标轴指示器，坐标轴触发有效
                            type: 'shadow'        // 默认为直线，可选为：'line' | 'shadow'
                        }
                    },
                    toolbox: {
                        feature: {
                            dataView: {show: true, readOnly: true},
                            restore: {show: true},
                            saveAsImage: {show: true}
                        }
                    },
                    legend: {
                        selected: {
                            '已归还': false
                        },
                        data: legend_data
                    },
                    grid: {
                        left: '3%',
                        right: '4%',
                        bottom: '3%',
                        containLabel: true
                    },
                    xAxis: {
                        type: 'value',
                        axisLabel: {
                            show: true,
                            interval: 'auto',
                            formatter: '100'
                        },
                        show: true
                    },
                    yAxis: {
                        type: 'category',
                        data: yAxis_data,
                    },
                    series: series
                };

                if (option && typeof option === "object") {
                    host_statistics_by_project_chart.setOption(option, true);
                }
            }
            else {
                alert(result.data)
            }
            host_statistics_by_project_chart.hideLoading();
        },
        error: function (errorMsg) {
            host_statistics_by_project_chart.hideLoading();
        }
    });

    // 绑定点击事件
    host_statistics_by_project_chart.on('click', function (param) {
        let room_name = param.name;
        let status = param.seriesName;
        let url = '/assets/host/?project=' + room_name + '&status=' + status;
        window.location.href = url;
    });


    // 按机房统计
    $.ajax({
        type: "post",
        async: true,
        url: "/assets/host_statistics_by_room_chart/",
        dataType: "json",
        beforeSend: function () {
            host_statistics_by_room_chart.showLoading();
        },
        success: function (result) {
            if (result.success) {
                let data = result.data;
                let tile = data.title;
                let legend_data = data.legend_data;
                let yAxis_data = data.yAxis_data;
                let series = data.series;
                let option = null;
                app.title = tile;

                option = {
                    tooltip: {
                        trigger: 'axis',
                        axisPointer: {            // 坐标轴指示器，坐标轴触发有效
                            type: 'shadow'        // 默认为直线，可选为：'line' | 'shadow'
                        }
                    },
                    toolbox: {
                        feature: {
                            dataView: {show: true, readOnly: true},
                            restore: {show: true},
                            saveAsImage: {show: true}
                        }
                    },
                    legend: {
                        selected: {
                            '已归还': false
                        },
                        data: legend_data
                    },
                    grid: {
                        left: '3%',
                        right: '4%',
                        bottom: '3%',
                        containLabel: true
                    },
                    xAxis: {
                        type: 'value',
                        axisLabel: {
                            show: true,
                            interval: 'auto',
                            formatter: '100'
                        },
                        show: true
                    },
                    yAxis: {
                        type: 'category',
                        data: yAxis_data,
                    },
                    series: series
                };

                if (option && typeof option === "object") {
                    host_statistics_by_room_chart.setOption(option, true);
                }
            }
            else {
                alert(result.data)
            }
            host_statistics_by_room_chart.hideLoading();
        },
        error: function (errorMsg) {
            host_statistics_by_room_chart.hideLoading();
        }
    });

    // 绑定点击事件
    host_statistics_by_room_chart.on('click', function (param) {
        let room_name = param.name;
        let status = param.seriesName;
        let url = '/assets/host/?room=' + room_name + '&status=' + status;
        window.location.href = url;
    });

});