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

    //alert edit log
    alertEditLog = function(event, text) {
        alert = $('<li class="alert alert-info" style="display:none;">'+text+'</li>');
        $('#addable-programs #schedule-edit-log').prepend(alert);
        alert.fadeIn();
        $('#addable-programs #unsaved-changes').show();
    };

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
        drop: function(date, allDay) {
            //copied from fullcalendar/demos/external-dragging.html

            // retrieve the dropped element's stored Event Object
            var originalEvent = $(this).data('eventObject');
            
            // we need to copy it, so that multiple events don't have a reference to the same object
            var newEvent = $.extend({}, originalEvent);
            
            // assign it the date that was reported
            newEvent.start = date;
            newEvent.allDay = allDay;

            //pull data from DOM
            newEvent.program = $(this).data('program-id');
            newEvent.station = $(this).data('station-id');
            duration = $(this).data('duration-sec'); //in seconds
            newEvent.end = new Date(date.getTime() + duration*1000); //create new js Date

            // render the event on the calendar
            // the last `true` argument determines if the event "sticks" (http://arshaw.com/fullcalendar/docs/event_rendering/renderEvent/)
            $('#calendar').fullCalendar('renderEvent', newEvent, true);
            
            // alert schedule edited
            alertEditLog(newEvent, newEvent.title+' added on '+newEvent.start);
            newEvent.edited = 'added'; //set edited flag
            
        },
        events: [], //add these in schedule.html
        annotations: [], //where we have access to the template

        editable: true,
        eventDurationEditable: false,
        eventStartEditable: true,

        eventClick: function(event, jsEvent, view) {
            if (event.isBackground) {
                return false;
            }

            $.ajax({
                url:'/api/scheduledprogram/'+event.id,
                context: this, //so that the success callback gets a reference
                success: function(data) {
                    program = data['program'];
                    popover_content = "<ul>";
                    if (program['description'] !== null) {
                        popover_content += "<li>"+program['description']+"</li>";
                    }
                    popover_content += "<li>Start: "+event.start.format("L LT")+"</li>";
                    popover_content += "<li>End: "+event.end.format("L LT")+"</li>";
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
        },
        eventDrop: function(event) {
            // alert schedule edited
            alertEditLog(event, event.title+' moved to '+event.start);
            event.edited = 'edited'; //set edited flag
        }

    });

    
    $('button#save-schedule').click(function() {
        //query clientside events by edited flag
        editedEvents = $('#calendar').fullCalendar('clientEvents',function(event) {
            if (event.edited !== undefined && event.saved !== true ) { return true; }
        });

        for (var key in editedEvents) {
            var event = editedEvents[key];

            //serialize edited event to json
            //manually, because we only need a subset of fields
            cleaned_data = {program:event.program,
                        station:event.station,
                        start:event.start};
            action_url = '/radio/scheduleprogram/add/ajax/';

            if (event.edited === 'edited') {
                //there's already an existing ScheduledProgram in the db
                cleaned_data.scheduledprogram = event.id;
                action_url = '/radio/scheduleprogram/edit/ajax/';
            }

            //post to flask
            $.ajax(action_url,
                  { type: 'POST',
                    data: JSON.stringify(cleaned_data, null, '\t'),
                    dataType: 'json',
                    contentType: 'application/json;charset=UTF-8',
                    context: this
                }).success(function(data) {
                    //console.log('saved ScheduledProgram '+data['result']['id']);
                    this.saved = true;
                });

        }

        //clear editlog
        $('#addable-programs #schedule-edit-log').empty();
        $('#addable-programs #unsaved-changes').hide();

        //rerender the calendar
        $('#calendar').fullCalendar('refresh');
    });
});
