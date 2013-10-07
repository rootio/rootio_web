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

    $('#recurringinput').recurringinput();

    if (!Modernizr.inputtypes.date) {
        $('input[type=date]').datepicker();
    }
    
});

