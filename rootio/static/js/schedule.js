$(document).ready(function() {
    var date = new Date();
    var d = date.getDate();
    var m = date.getMonth();
    var y = date.getFullYear();
    
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
    
});

