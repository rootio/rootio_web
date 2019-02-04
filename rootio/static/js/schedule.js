$(document).ready(function() {
  //lock to prevent rapid save button click resulting in multiple processing
  var is_saving = false;

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
  $('#recurringinput').on('rrule-update', function(event) {
    var rrule = $('#recurringinput #rrule-output').html();
    $('form input[name=recurrence]').val(rrule);
  });

  //bind program selector to display information from API
  $('.modal-body #program').on('change', function(event) {
    val = this.value;
    program_extra = $('.modal-body ul#program_extra');
    if (val !== '__None') {
      new_program = $.getJSON('/api/program/' + val, function(data) {
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
    $(document).ajaxComplete(function(event, request, settings) {
      if (settings.type == 'POST') {
        $('#calendar').fullCalendar('refetchEvents');
        $('#calendar').fullCalendar('refresh');
        $('.modal').hide();
        $('.modal-backdrop').fadeOut();
      }
    });
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
      revert: true, // will cause the event to go back to its
      revertDuration: 0 //  original position after the drag
    });

  });

  popoverPlacement = function(eventDate, calendarView) {
    var position = "right";
    if (calendarView.name === "agendaDay") {
      position = "bottom";
    } else if (calendarView.name === "agendaWeek") {
      if (eventDate.isoWeekday() > 5) {
        position = "left";
      }
    }
    return position;
  };

  getDefaultView = function() {
    return localStorage.getItem("fcDefaultView") ?
      localStorage.getItem("fcDefaultView") :
      "month";
  };

  getDefaultDate = function() {
    var defaultDate = localStorage.getItem("fcDefaultDate") ?
      localStorage.getItem("fcDefaultDate") :
      moment();
    var defaultView = getDefaultView();
    var m = moment(defaultDate);

    if (parseInt(m.year()) < parseInt(moment().year())) {
      return moment();
    }

    if (defaultView == "month"
        && parseInt(m.format('M')) < parseInt(moment().format('M'))) {
      return moment();
    }

    if (defaultView == "agendaWeek"
        && parseInt(m.week()) < parseInt(moment().week())
       ) {
      return moment();
    }

    if (defaultView == "agendaDay" && m.format < moment()) {
      return moment();
    }


    return defaultDate;
  };

  //set up calendar
  $('#calendar').fullCalendar({
    defaultView: getDefaultView(),
    defaultDate: getDefaultDate(),
    viewRender: function(view, element) {
      localStorage.setItem("fcDefaultView", view.name);
      localStorage.setItem("fcDefaultDate", view.intervalStart.format());
    },
    header: {
      left: 'prev,next today',
      center: 'title',
      right: 'month,agendaWeek,agendaDay'
    },
    firstDay: 1,
    allDayDefault: false,
    timezone: $('#calendar').data('timezone'),

    droppable: true,
    drop: function(date, allDay) {
      //copied from fullcalendar/demos/external-dragging.html

      // retrieve the dropped element's stored Event Object
      var originalEvent = $(this).data('eventObject');

      // we need to copy it, so that multiple events don't have a reference to the same object
      var newEvent = $.extend({}, originalEvent);

      // assign it the date that was reported
      newEvent.start = date;
      newEvent.allDay = false;

      //pull data from DOM
      newEvent.program = $(this).data('program-id');
      newEvent.station = $(this).data('station-id');
      newEvent.program_type_id = $(this).data('program-type-id');
      duration = $(this).data('duration-sec'); //in seconds
      newEvent.end = moment(date).add('seconds', duration); //create new js moment
      newEvent.edited = 'added'; //set edited flag

      save_event(newEvent);
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

      if (event.id === undefined) {
        //don't allow click popover until saved
        return false;
      }

      $.ajax({
        url: '/api/scheduledprogram/' + event.id,
        context: this, //so that the success callback gets a reference
        success: function(data) {
          setEventStart = function(id) {
            return update_event(id, $('input#newStart_' + id).val());
          };
          program = data['program'];
          popover_content = "<ul>";
          if (program['description']) {
            popover_content += "<li>" + program['description'] + "</li>";
          }
          popover_content += "<li>Start: " + event.start.format("L LT") + "</li>";
          popover_content += "<li>End: " + event.end.format("L LT") + "</li>";
          popover_content += "</ul>";
          popover_content += "<p>Modify start time (HH:mm): ";
          popover_content += "<input id='newStart_" + event.id + "' type='text' value='" + event.start.format('LT') + "' placeholder='HH:MM'></p>";
          popover_content += "<button id='update_event' onclick='setEventStart(" + event.id + ")'>Update</button>";
          popover_content += "<button id='delete_event' onclick='delete_event(" + event.id + ")'>Delete</button>";
          $(this).popover({
              trigger: 'manual',
              placement: popoverPlacement(event.start, view),
              title: event.title,
              content: popover_content,
              html: true
            })
            .popover('toggle');

          //hide any tooltips
          $(this).tooltip('hide');
        }
      });
      return true;
    },

    eventMouseover: function(event, jsEvent, view) {
      eventDuration = (event.end - event.start) / (1000 * 60); // in minutes
      if (eventDuration < 30 && view.name !== 'month') {
        //title probably not visible, show in tooltip
        $(this).tooltip({
          trigger: 'manual',
          placement: popoverPlacement(event.start, view),
          title: event.title
        }).tooltip('show');
      }
    },
    eventMouseout: function(event, jsEvent, view) {
      $(this).tooltip('hide');
    },
    eventDrop: function(event) {
      save_event(event);
    }

  });
});

function save_event(event) {

  cleaned_data = {
    start: event.start,
    end: event.end
  }; //moment json-ifies to iso8601 natively

  if (event.program) {
    cleaned_data.program = event.program;
    action_url = '/radio/scheduleprogram/add/ajax/';
  } else {
    action_url = '/radio/scheduleprogram/edit/ajax/';
  }

  if (event.station) {
    cleaned_data.station = event.station;
  }

  if (event.id) {
    cleaned_data.scheduledprogram = event.id;
  }



  //post to flask
  $.ajax(action_url, {
      type: 'POST',
      data: JSON.stringify(cleaned_data, null, '\t'),
      dataType: 'json',
      contentType: 'application/json;charset=UTF-8',
      context: this,
      async: false
    })
    .success(function(data) {
      toastr["success"]("Saved!");
      event.saved = true;
    });

  //rerender the calendar
  $('#calendar').fullCalendar('refetchEvents');
  // $('#calendar').fullCalendar('refresh');
}

function remove_from_log(elem) {
  $(elem).closest('li').remove();
  return false;
}

function delete_event(id) {
  if (confirm("Are you sure you want to delete this program?")) {
    ask_to_delete(id);
    $('#calendar').fullCalendar('removeEvents', id);
  }
}

function update_event(id, start) {
  var e = $("#calendar").fullCalendar('clientEvents', id)[0];
  var oldStart = e.start;
  var oldEnd = e.end;
  var duration = moment.duration(oldEnd.diff(oldStart)).as('minutes');
  e.start = moment(oldStart.format('YYYYMMDD') + start + '+00:00', 'YYYYMMDDh:mm AZ');
  e.end = e.start.clone().add(duration, 'm');
  $('#calendar').fullCalendar('updateEvent', e);
  $('#calendar').fullCalendar('refresh');
  save_event(e);
}

function ask_to_delete(id) {
  $.post('/radio/scheduleprogram/delete/' + id + '/')
}
