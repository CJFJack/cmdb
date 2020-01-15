$(function() {

    Morris.Area({
        element: 'morris-area-chart',
        data: [{
            period: '2010 Q1',
            iphone: 2666,
            ipad: null,
            itouch: 2647
        }, {
            period: '2010 Q2',
            iphone: 2778,
            ipad: 2294,
            itouch: 2441
        }, {
            period: '2010 Q3',
            iphone: 4912,
            ipad: 1969,
            itouch: 2501
        }, {
            period: '2010 Q4',
            iphone: 3767,
            ipad: 3597,
            itouch: 5689
        }, {
            period: '2011 Q1',
            iphone: 6810,
            ipad: 1914,
            itouch: 2293
        }, {
            period: '2011 Q2',
            iphone: 5670,
            ipad: 4293,
            itouch: 1881
        }, {
            period: '2011 Q3',
            iphone: 4820,
            ipad: 3795,
            itouch: 1588
        }, {
            period: '2011 Q4',
            iphone: 15073,
            ipad: 5967,
            itouch: 5175
        }, {
            period: '2012 Q1',
            iphone: 10687,
            ipad: 4460,
            itouch: 2028
        }, {
            period: '2012 Q2',
            iphone: 8432,
            ipad: 5713,
            itouch: 1791
        }],
        xkey: 'period',
        ykeys: ['iphone', 'ipad', 'itouch'],
        labels: ['已处理', '处理中', '未处理'],
        pointSize: 2,
        hideHover: 'auto',
        resize: true
    });

    Morris.Donut({
        element: 'morris-donut-chart',
        data: [{
            label: "已使用",
            value: 112
        }, {
            label: "空闲",
            value: 30
        }, {
            label: "故障",
            value: 20
        }],
        resize: true
    });
    Morris.Donut({
        element: 'morris-donut-chart2',
        data: [{
            label: "已使用",
            value: 112
        }, {
            label: "空闲",
            value: 30
        }, {
            label: "故障",
            value: 20
        }],
        resize: true
    });
     Morris.Donut({
        element: 'morris-donut-chart3',
        data: [{
            label: "已使用",
            value: 112
        }, {
            label: "空闲",
            value: 30
        }, {
            label: "故障",
            value: 20
        }],
        resize: true
    });

    Morris.Bar({
        element: 'morris-bar-chart',
        data: [{
            y: '2006',
            a: 100,
            b: 90,
            c: 80,
            d: 60
        }, {
            y: '2007',
            a: 75,
            b: 65,
            c: 80,
            d: 9
        }, {
            y: '2008',
            a: 50,
            b: 40,
            c: 30,
            d: 20
        }, {
            y: '2009',
            a: 75,
            b: 65,
            c: 50,
            d: 35
        }, {
            y: '2010',
            a: 50,
            b: 40,
            c: 33,
            d: 10
        }, {
            y: '2011',
            a: 75,
            b: 65,
            c: 37,
            d: 10
        }, {
            y: '2012',
            a: 100,
            b: 90,
            c: 50,
            d: 10
        }],
        xkey: 'y',
        ykeys: ['a', 'b','c','d'],
        labels: ['机房0', '机房1','机房2','机房3'],
        hideHover: 'auto',
        resize: true
    });

});
