//Colors 

var chartGreen = 'rgba(140, 193, 82,1)'
var chartRed = 'rgba(218, 68, 83,1)'
var chartBlue = 'rgba(74, 137, 220,1)'
var chartMagenta = 'rgba(150, 122, 220,1)'
var chartBrown = 'rgba(170, 142, 105,1)'
var chartOrange = 'rgba(233, 87, 63,1)'
var chartMint = 'rgba(55, 188, 155,1)'


//Exchange Page Chart
//BTC Chart
var options = {
	series: [{
		name: 'series1',
		data: [41, 58, 98, 79]
	}],
	colors:['#8CC152'],
	chart: {
		toolbar: {show: false},
		height: 80,
		width:150,
		type: 'area'
	},
	grid:{show:false },
	xaxis: {
		labels: {show: false,},
		axisBorder: {show: false},
		axisTicks: {show: false,}	
	},
	yaxis: {labels: {show: false}},
	dataLabels: {enabled: false},
	stroke: {width:1},
	tooltip: {enabled:false},
};

var chart = new ApexCharts(document.querySelector("#chart-btc"), options);
chart.render();

//ETH Chart
var options = {
	series: [{
		name: 'series1',
		data: [92, 93, 92, 91]
	}],
	colors:['#BF263C'],
	chart: {
		toolbar: {show: false},
		height: 80,
		width:150,
		type: 'area'
	},
	grid:{show:false },
	xaxis: {
		labels: {show: false,},
		axisBorder: {show: false},
		axisTicks: {show: false,}	
	},
	yaxis: {labels: {show: false}},
	dataLabels: {enabled: false},
	stroke: {width:1},
	tooltip: {enabled:false},
};

var chart = new ApexCharts(document.querySelector("#chart-eth"), options);
chart.render();

//EUR Chart
var options = {
	series: [{
		name: 'series1',
		data: [192, 150, 170, 170]
	}],
	colors:['#5D9CEC'],
	chart: {
		toolbar: {show: false},
		height: 80,
		width:150,
		type: 'area'
	},
	grid:{show:false },
	xaxis: {
		labels: {show: false,},
		axisBorder: {show: false},
		axisTicks: {show: false,}	
	},
	yaxis: {labels: {show: false}},
	dataLabels: {enabled: false},
	stroke: {width:1},
	tooltip: {enabled:false},
};

var chart = new ApexCharts(document.querySelector("#chart-eur"), options);
chart.render();

//Main Chart
var chartActivityOptions = {
	series: [14, 73, 31, 17, 15],
	colors:[chartRed, chartGreen, chartBlue, chartMint, chartMagenta],
	chart: {
		width:'320px',
		animations: {enabled: false},
		toolbar: {show: false},
		type: 'donut'
	},
	legend: {
		show:false,
		position: 'bottom'
	},
	grid:{show:false },
	xaxis: {
		labels: {show: false,},
		axisBorder: {show: false},
		axisTicks: {show: false,}	
	},
	yaxis: {labels: {show: false}},
	dataLabels: {enabled: false},
	stroke: {width:0},
	tooltip: {enabled:false},
};

var chart = new ApexCharts(document.querySelector("#chart-activity"), chartActivityOptions);
chart.render();


//Component Demo Charts
//Chart 1
var optionsChart1 = {
	chart: {
		type: 'area',
		toolbar: {
			show: false
		},
		animations: {
			enabled: false,
		}
	},
	series: [{
		name: 'Mobile',
		data: [30, 40, 45, 50, 49, 60, 70],
	}, {
		name: 'PWA',
		data: [40, 50, 65, 70, 89, 90, 95],
	}],
	fill: {
		type: "gradient",
		gradient: {
			shadeIntensity: 1,
			opacityFrom: 0.7,
			opacityTo: 0.9,
			stops: [0, 90, 100]
		}
	},
	xaxis: {
		categories: [1991, 1992, 1993, 1994, 1995, 1996, 1997]
	}
}

var chartDemo1 = new ApexCharts(document.querySelectorAll("#charts-demo-1")[0], optionsChart1);
chartDemo1.render();



