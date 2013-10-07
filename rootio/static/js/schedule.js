$(document).ready(function() {    
    $('#calendar').fullCalendar({
        header: {
            left: 'prev,next today',
            center: 'title',
            right: 'month,agendaWeek,agendaDay'
        },
        allDayDefault: false,
        defaultView: 'agendaWeek',
        editable: false,
        events: {
            url: '/radio/station/schedule.json'
        }
    });

//init recurring input fieldset
    $('#recurringinput').recurringinput();

//shim html5 input types
    if (!Modernizr.inputtypes.date) {
        $('input[type=date]').datepicker();
    }
    
});

