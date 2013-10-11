$(document).ready(function() {    
    //set up recurrence presets
    $('input[name=preset-recurrence]').change(function(event) {
        var value = $(event.target).val();
        if (value == "custom") {
            $('#recurringinput').show();
        } else {
            $('#recurringinput').hide();
            $('form input[name=recurrence]').val(value);
        }
    });

    //init recurring input fieldset for custom schedules
    $('#recurringinput').recurringinput().hide();
    //and watch for updates
    $('#recurringinput').on('rrule-update',function(event) {
        var rrule = $('#recurringinput #rrule-output').html();
        $('form input[name=recurrence]').val(rrule);
    });  


    //shim html5 input types
    if (!Modernizr.inputtypes.date) {
        $('input[type=date]').datepicker();
    }
    
});

