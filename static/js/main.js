function highchartsinit(fn, gernes) {
    Highcharts.chart('chart', {
        chart: {
            type: 'column',
        },
        title: {
            text: '音樂風格分析'
        },
        xAxis: {
            categories: [
                "藍調",
                "古典",
                "鄉村",
                "迪斯可",
                "嘻哈",
                "重金屬",
                "流行",
                "雷鬼",
                "搖滾",
            ],
            crosshair: true,
        },
        yAxis: {
            min: 0,
            title: {
                text: "信心度(%)"
            }
        },
        tooltip: {
            headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
            pointFormat: '<tr>' +
                '<td style="padding:0"><b>{point.y:.2f} %</b></td></tr>',
            footerFormat: '</table>',
            shared: true,
            useHTML: true
        },
        plotOptions: {
            column: {
                pointPadding: 0.2,
                borderWidth: 0
            }
        },
        series: [
            {
                name: fn,
                data: gernes,
            }
        ]
    })
}

document.getElementById('file-upload').addEventListener('change', (e) => {
    const files = e.target.files;
    const formData = new FormData();
    formData.append('file', files[0]);
    
    fetch('/uploader', {
        method: 'POST',
        body: formData
    }).then((res) => {
        console.log(res);
        try{
            return res.json();
        }catch(e){
            alert('Error: '+e);
        }
    }).then((data) => {
        console.log(data);
        highchartsinit(data.filename, data.gernes);
    }).catch(
        error => console.log(error) // Handle the error response object
    );
}, false);