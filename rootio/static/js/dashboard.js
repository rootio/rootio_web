$(document).ready(function() {
    $('.sparkline').each(function() {
        //strip python [] from the values
        var cleaned = $(this).html().replace('[','').replace(']','');
        $(this).html(cleaned);

        //setup  sparkline options
        var type = $(this).data('type');
        var options = {type:type};
        if (type === 'boolean') {
            //really a bar with a special color
            options.type = 'bar';
            options.colorMap = $.range_map({
                0: 'red',
                1: '#009688'
            });
            options.chartRangeMin = 0;
            options.chartRangeMax = 1;
        }
        else if(type === 'line') {
            options.type = 'line';
            options.lineColor = '#009688',
            options.fillColor =  '#70d8ce';
            options.highlightSpotColor =  '#000000';
            options.highlightLineColor =  '#000000';
            options.tooltipFormat = $.spformat('<span style="color: {{color}}; width: auto; height: auto;">&#9679;</span> {{prefix}}{{y}}{{suffix}}', 'tooltip-class')
        }

        $(this).sparkline('html',options);
    });
});