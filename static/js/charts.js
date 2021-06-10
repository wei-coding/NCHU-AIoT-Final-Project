filename = ''
gernes = []

function highchartsinit() {
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
				name: filename,
				data: gernes,
			}
		]
	})
}

$(function () {
	$.ajax({
		url: '/getpredict',
		data: '{}',
		dataType: 'json',
		success: function (data) {
			filename = data['filename'];
			gernes = data['gernes'];
			highchartsinit();
		}
	})
})