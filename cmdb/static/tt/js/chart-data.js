// 路径配置
require.config({
    paths: {
        echarts: '/static/js/'
    }
});

// 使用
require(
    [
        'echarts',
        'echarts/chart/pie', // 使用柱状图就加载bar模块，按需加载
        'echarts/chart/funnel'
    ],
    function (ec) {
        // 基于准备好的dom，初始化echarts图表
        myChartLeft = ec.init(document.getElementById('echart-pie-left'));
        myChartMiddle = ec.init(document.getElementById('echart-pie-middle')); 
        myChartRight = ec.init(document.getElementById('echart-pie-right')); 
        $.get("/dashboard/pie", function(ret){
            if (ret['status']){
                data = ret['data']
                $('#span-left').text('总量：'+data[0].total)
                $('#span-middle').text('总量：'+data[1].total)
                $('#span-right').text('总量：'+data[2].total)
                var options = data.map(function (i,n) {
                    return {
                        title : {
                            text: i.text,
                            // subtext: '纯属虚构',
                            x:'center'
                        },
                        tooltip : {
                            trigger: 'item',
                            formatter: "{a} <br/>{b} : {c} ({d}%)"
                        },
                        legend: {
                            orient : 'vertical',
                            x : 'left',
                            data:['空闲','使用中','故障']
                        },
                        toolbox: {
                            show : true,
                            feature : {
                                mark : {show: false},
                                dataView : {show: false, readOnly: false},
                                magicType : {
                                    show: true, 
                                    type: ['pie', 'funnel'],
                                    option: {
                                        funnel: {
                                            x: '25%',
                                            width: '50%',
                                            funnelAlign: 'left',
                                            max: 1548
                                        }
                                    }
                                },
                                restore : {show: true},
                                saveAsImage : {show: true}
                            }
                        },
                        calculable : true,
                        series : [
                            {
                                name:data.text,
                                type:'pie',
                                radius : '55%',
                                center: ['50%', '60%'],
                                data:[
                                    {value:i.free, name:'空闲'},
                                    {value:i.used, name:'使用中'},
                                    {value:i.errors, name:'故障'},
                                ]
                            }
                        ]
                    };
                });
                
                // 为echarts对象加载数据 
                myChartLeft.setOption(options[0]);
                myChartMiddle.setOption(options[1]);
                myChartRight.setOption(options[2]);
            }
        });
    }
);