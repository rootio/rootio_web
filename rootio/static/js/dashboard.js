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
                1: 'blue'
            });
            options.chartRangeMin = 0;
            options.chartRangeMax = 1;
        }
        $(this).sparkline('html',options);
    });
});