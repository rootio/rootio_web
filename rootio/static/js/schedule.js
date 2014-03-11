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

    //bind program selector to display information from API
    $('.modal-body select#program').on('change',function(event) {
        val = this.value;
        program_extra = $('.modal-body ul#program_extra');
        if (val !== '__None') {
            new_program = $.getJSON('/api/program/'+val,function(data) {
                program_extra.find('span#description').html(data['description']);
                program_extra.find('span#program_type').html(data['program_type']['name']);
                program_extra.find('span#duration').html(data['duration']);
                program_extra.find('span#update_frequency').html(data['update_recurrence']);
                //TODO, parse this to be human readable with rrule.js?
                program_extra.slideDown();
            });
        } else {
            program_extra.slideUp();
            program_extra.find('span').html('');
        }
    });

    //close modal on recurring submit
    $('button#modal-save').click(function() {
        $('.modal').hide();
        $('.modal-backdrop').fadeOut();
        $('#calendar').fullCalendar('refetchEvents');
    });


    //set up program drag and drop
    $('#addable-programs li.external-event').each(function() {
        
            // create an Event Object (http://arshaw.com/fullcalendar/docs/event_data/Event_Object/)
            // it doesn't need to have a start or end
            var eventObject = {
                title: $.trim($(this).text()) // use the element's text as the event title
            };
            
            // store the Event Object in the DOM element so we can get to it later
            $(this).data('eventObject', eventObject);
            
            // make the event draggable using jQuery UI
            $(this).draggable({
                zIndex: 999,
                revert: true,      // will cause the event to go back to its
                revertDuration: 0  //  original position after the drag
            });
            
        });

    //set up calendar
    $('#calendar').fullCalendar({
        header: {
            left: 'prev,next today',
            center: 'title',
            right: 'month,agendaWeek,agendaDay'
        },
        allDayDefault: false,
        defaultView: 'agendaWeek',

        droppable: true,
        drop: function(date, allDay) { // this function is called when something is dropped
            //copied from fullcalendar/demos/external-dragging.html

            // retrieve the dropped element's stored Event Object
            var originalEventObject = $(this).data('eventObject');
            
            // we need to copy it, so that multiple events don't have a reference to the same object
            var copiedEventObject = $.extend({}, originalEventObject);
            
            // assign it the date that was reported
            copiedEventObject.start = date;
            copiedEventObject.allDay = allDay;
            
            // render the event on the calendar
            // the last `true` argument determines if the event "sticks" (http://arshaw.com/fullcalendar/docs/event_rendering/renderEvent/)
            $('#calendar').fullCalendar('renderEvent', copiedEventObject, true);
            
            // is the "remove after drop" checkbox checked?
            if ($('#drop-remove').is(':checked')) {
                // if so, remove the element from the "Draggable Events" list
                $(this).remove();
            }
        },
        events: [], //add these in schedule.html
        annotations: [], //where we have access to the template

        editable: true,
        eventDurationEditable: false,
        eventStartEditable: true,

        eventClick: function(event, jsEvent, view) {
            $.ajax({
                url:'/api/scheduledprogram/'+event.id,
                context: this, //so that the success callback gets a reference
                success: function(data) {
                    program = data['program'];
                    popover_content = "<ul>";
                    if (program['description'] !== null) {
                        popover_content += "<li>"+program['description']+"</li>";
                    }
                    popover_content += "<li>"+event.start+" - "+event.end+"</li>";
                    popover_content += "</ul>";
                    $(this).popover({
                                trigger:'manual',
                                placement: view.name === "agendaDay" ? "bottom": "right",
                                title:event.title,
                                content:popover_content,
                                html:true
                            })
                    .popover('toggle');

                    //hide any tooltips
                    $(this).tooltip('hide');
                }
            });
        },
        eventMouseover: function(event, jsEvent, view) {
            eventDuration = (event.end - event.start) / (1000*60); // in minutes
            if (eventDuration < 30 && view.name !== 'month') {
                //title probably not visible, show in tooltip
                $(this).tooltip({
                    trigger: 'manual',
                    placement: view.name === "agendaDay" ? "bottom": "right",
                    title:event.title
                }).tooltip('show');
            }
        },
        eventMouseout: function(event, jsEvent, view) {
            $(this).tooltip('hide');
        }

    });

    
    $('button#save-schedule').click(function() {
        //TODO, serialize added events to json,
        //post to /radio/scheduleprogram/add/ajax/

        // $('#calendar').fullCalendar('refetchEvents');
    });
});
