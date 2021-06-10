// material design
// nav bar
const MDCTopAppBar = mdc.topAppBar.MDCTopAppBar;
const MDCRipple = mdc.ripple.MDCRipple;
const MDCSnackbar = mdc.snackbar.MDCSnackbar;

MDCTopAppBar.attachTo(document.getElementById('app-bar'));

const mySnackBar = MDCSnackbar.attachTo(document.querySelector('.mdc-snackbar'));
const uploadButton = new MDCRipple(document.getElementById('uploader'));
document.getElementById('uploader').addEventListener('click', ()=>{
    let fileDOM = document.createElement('input');
    fileDOM.setAttribute('type', 'file');
    fileDOM.setAttribute('accepct', 'audio/*');
    fileDOM.addEventListener('change', (e) => {
        const files = e.target.files;
        const formData = new FormData();
        formData.append('file', files[0]);
        document.getElementById('chart').innerHTML = '<div class="loader"></div>';
        document.getElementById('center-wrapper').style.display = 'none';
        fetch('/uploader', {
            method: 'POST',
            body: formData
        }).then((res) => {
            console.log(res);
            if(res.status == 413){
                throw new Error("HTTP 413 檔案太大惹 (´◓Д◔`)");
            }else if(res.status != 200){
                throw new Error(`Error HTTP ${res.status}`);
            }else{
                try {
                    return res.json();
                } catch (e) {
                    alert('Error: ' + e);
                }
            }
        }).then((data) => {
            console.log(data);
            highchartsinit(data.filename, data.gernes);
        }).catch((error) => {
            mySnackBar.labelText = `Error ${error}`;
            mySnackBar.open();
            console.log(error);
        });
    }, false);
    fileDOM.click();
}, false);

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