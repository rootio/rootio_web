/**
 * Created by vmcbaptista on 02-09-2016.
 * This file contains all the logic behind the form used to add and edit programs
 */
$( function() {
    // est_time is a variable defined previously on the JS files that are invoked after this one
    $('#est_time').text(moment.utc(est_time.asMilliseconds()).format("HH:mm:ss"));

    /**
     * Prepares the two sortable lists
     */
    $( "#sortable1" ).sortable({
        connectWith: ".connectedSortable",
        forcePlaceholderSize: false,
        // Mantains the components in the left list after being dragged to the right one
        helper: function(e,li) {
            copyHelper= li.clone().insertAfter(li);
            return li.clone();
        },
        stop: function() {
            copyHelper && copyHelper.hide();
        }
    });
    $(".connectedSortable").sortable({
        receive: function(e,ui) {
            copyHelper= null;
        }
    });
    $( "#sortable2" ).sortable({
        connectWith: ".connectedSortable"
    });

    /**
     * Adds a delete button to all the elements in the right list.
     * Used in the editing form.
     */
    $('#sortable2 li').each(function(){
        $(this).prepend('<i class="fa fa-times" aria-hidden="true"></i>');
    });

    /**
     * Contains all logic needed after dropping a component on the right list
     */
    $('#sortable2').on( "sortreceive", function( event, ui ) {
        element = ui['item'];
        // Adds a delete button to the component dropped and the actions that should be done when the button is clicked
        $(ui.item).prepend('<i class="fa fa-times" aria-hidden="true"></i>').click(function(){
            element = $(this);
            // Updates the estimate time of the program after removing the component
            if (element.children().next().val() == 'tts') {
                $('#est_time').text(function () {
                    est_time.subtract(moment.duration(calculate_time(element.text()), 's'));
                    return moment.utc(est_time.asMilliseconds()).format("HH:mm:ss");
                });
            }
            else {
                $('#est_time').text(function () {
                    est_time.subtract(moment.duration(parseFloat(element.children().next().next().val()),'s'));
                    return moment.utc(est_time.asMilliseconds()).format("HH:mm:ss");
                });
            }
            element.remove();
        });
        // Updates the estimate time of the program after adding the component
        if (element.children().next().val() == 'tts') {
            $('#est_time').text(function () {
                est_time.add(moment.duration(calculate_time(element.text()), 's'));
                return moment.utc(est_time.asMilliseconds()).format("HH:mm:ss");
            });
        }
        else {
            $('#est_time').text(function () {
                est_time.add(moment.duration(parseFloat(element.children().next().next().val()),'s'));
                return moment.utc(est_time.asMilliseconds()).format("HH:mm:ss");
            });
        }
    });

    /**
     * Actions that should be done when the delete button is clicked
     */
    $('.fa-times').click(function(){
        element = $(this).parent();
        // Updates the estimate time of the program after removing the component
        if (element.children().next().val() == 'tts') {
            $('#est_time').text(function () {
                est_time.subtract(moment.duration(calculate_time(element.text()), 's'));
                return moment.utc(est_time.asMilliseconds()).format("HH:mm:ss");
            });
        }
        else {
            $('#est_time').text(function () {
                est_time.subtract(moment.duration(parseFloat(element.children().next().next().val()),'s'));
                return moment.utc(est_time.asMilliseconds()).format("HH:mm:ss");
            });
        }
        element.remove();

    });

    /**
     * Adjusts the form according with the contetn type selected by the user
     */
    $('#content_type').change(function() {
        if ($(this).val() == '') {
            $('#sortable1').empty();
            $('#aggregator').hide();
            $('#media').hide();
        }
        else if ($(this).val() == 'Aggregators') {
            $('#media').hide();
            $('#sortable1').empty();
            $('#aggregator').empty();
            $('#aggregator').append(
                '<option></option>'
            );
            $('#aggregator').show();
            // Gets all the aggregators that exists on the DB and put them as options in a selectbox
            $.ajax({
                url:'/bot/list',
                success:function(data) {
                    for (var d in data) {
                        $('#aggregator').append(
                            '<option value="'+ data[d]['station_id'] + '-' + data[d]['function_id'] + '">' + data[d]['station_name'] + '-' + data[d]['function_name'] + '</option>'
                        );

                    }
                },
                error: function(error) {
                    console.log(errors)
                }
            });
        }
        else if ($(this).val() == 'Audio Files') {
            $('#sortable1').empty();
            $('#aggregator').hide();
            $('#media').val('');
            $('#media').show();
        }
        else if ($(this).val() == 'SMS') {
            $('#sortables').show();
            $('#sortable1').empty();
            $('#aggregator').hide();
            $('#media').hide();
            // Gets all the SMS that exists on the DB and put them in the right sortable list
            $.ajax({
                url:'/radio/sms',
                success:function(data) {
                    for (var d in data) {
                        for (var m in data[d]) {
                            if (m == 'text') {
                                $('#sortable1').append(
                                    '<li class="ui-state-default"><input type="hidden" value="tts">' + data[d][m] + '</li>'
                                );
                            }
                        }
                    }
                },
                error: function(error) {
                    console.log(error)
                }
            });
        }
    });

    /**
     * Changes the content in the left sortable list according with the aggregator selected
     */
    $('#aggregator').change(function() {
        $('#sortables').show();
        $('#sortable1').empty();
        $.ajax({
            method: 'POST',
            url:'/bot/getinfo',
            data: {'station_id':$(this).val().split('-')[0],'function_id':$(this).val().split('-')[1],'csrf_token':token},
            success:function(data) {
                for (var d in data) {
                    $('#sortable1').append(
                        '<li class="ui-state-default"><input type="hidden" value="tts">' + data[d] + '</li>'
                    );
                }
            },
            error: function(error) {
                console.log(error)
            }
        });
    });

    /**
     * Changes the content in the left sortable list according with the media type selected
     */
    $('#media').change(function() {
        if ($(this).val() == '') {
            $('#sortable1').empty();
        }
        else if ($(this).val() == 'Jingle') {
            $('#sortable1').empty();
            $.ajax({
                url:'/radio/media/list',
                success:function(data) {
                    for (var d in data){
                        for (var m in data[d]) {
                            if (m == 'type' && data[d][m] == 'Jingle') {
                                $('#sortables').show();
                                $('#sortable1').append(
                                    '<li class="ui-state-default">' +
                                    '<input type="hidden" value="jingle">' +
                                    '<input type="hidden" name ="duration" value="' + moment.duration(data[d]['duration']).asSeconds() + '">' +
                                    '<input type="hidden" name ="path" value="' + data[d]['path'] + '">' + data[d]['name'] + '</li>'
                                );
                            }
                        }
                    }
                },
                error: function(error) {
                    console.log(errors)
                }
            })
        }
        else if ($(this).val() == 'Interlude') {
            $('#sortable1').empty();
            $.ajax({
                url:'/radio/media/list',
                success:function(data) {
                    for (var d in data){
                        for (var m in data[d]) {
                            if (m == 'type' && data[d][m] == 'Interlude') {
                                $('#sortables').show();
                                $('#sortable1').append(
                                    '<li class="ui-state-default">' +
                                    '<input type="hidden" value="interlude">' +
                                    '<input type="hidden" name ="duration" value="' + moment.duration(data[d]['duration']).asSeconds() + '">' +
                                    '<input type="hidden" name ="path" value="' + data[d]['path'] + '">' + data[d]['name'] + '</li>'
                                );
                            }
                        }
                    }
                },
                error: function(error) {
                    console.log(errors)
                }
            })
        }
        else {
            $('#sortable1').empty();
            $.ajax({
                url:'/radio/media/list',
                success:function(data) {
                    for (var d in data){
                        for (var m in data[d]) {
                            if (m == 'type' && data[d][m] == 'Other') {
                                $('#sortables').show();
                                $('#sortable1').append(
                                    '<li class="ui-state-default">' +
                                    '<input type="hidden" value="media">' +
                                    '<input type="hidden" name ="duration" value="' + moment.duration(data[d]['duration']).asSeconds() + '">' +
                                    '<input type="hidden" name ="path" value="' + data[d]['path'] + '">' + data[d]['name'] + '</li>'
                                );
                            }
                        }
                    }
                },
                error: function(error) {
                    console.log(errors)
                }
            })
        }
    });

    /**
     * Adjust the form according with the type of the program
     */
    $('#program_type').change(function () {
        adjustForm();
    });

    /**
     * Appends to the submited data some custom information
     */
    $("form").submit(function(e){
        description = generateDescription();
        $('fieldset').append("<input type='hidden' name='description' value='"+description+"'>");
        if ($('#program_type option:selected').text() == 'Call-in Show') {
            $('fieldset').append("<input type='hidden' name='est_time' value='"+$('#duration').val()+"'>");
        }
        else {
            $('fieldset').append("<input type='hidden' name='est_time' value='"+moment.utc(est_time.asMilliseconds()).format("HH:mm:ss.SSS")+"'>");
        }
    });

    /**
     * Generates the JSON with the description of the program
     */
    function generateDescription() {
        var newProgram = {};
        var start_time = moment.duration('0','s');
        if ($('#program_type option:selected').text() == 'Call-in Show') {
            var outCall = [];
            var callInObj = {};
            callInObj.argument = $('#host_number').val();
            callInObj.start_time = moment.utc(start_time.asMilliseconds()).format("HH:mm:ss");
            callInObj.duration = parseFloat(moment.duration($('#duration').val()).asSeconds());
            callInObj.warning_time = parseFloat(callInObj.duration) - 60;
            callInObj.is_streamed = false;
            callInObj.hangup_on_complete = true;
            outCall.push(callInObj);
            start_time.add(moment.duration(callInObj.duration, 's'));
            newProgram.Outcall = outCall;
        }
        else {
            var tts = [];
            var jingle = [];
            var interlude = [];
            var media = [];
            var count = 0;
            var num_comp = $('#sortable2').children().length;
            $('#sortable2').children().each(function () {
                if($(this).children().next().val() == 'tts') {
                    var ttsOb = {};
                    ttsOb.argument = $(this).text();
                    ttsOb.start_time = moment.utc(start_time.asMilliseconds()).format("HH:mm:ss");
                    ttsOb.duration = calculate_time($(this).text());
                    ttsOb.is_streamed = true;
                    if (count + 1 == num_comp) {
                        ttsOb.hangup_on_complete = true;
                    }
                    else {
                        ttsOb.hangup_on_complete = false;
                    }
                    tts.push(ttsOb);
                    start_time.add(moment.duration(ttsOb.duration, 's'));
                }
                else if ($(this).children().next().val() == 'interlude') {
                    var intOb = {};
                    intOb.argument = $(this).children().next().next().next().val();
                    intOb.start_time = moment.utc(start_time.asMilliseconds()).format("HH:mm:ss");
                    intOb.duration = parseFloat($(this).children().next().next().val());
                    intOb.is_streamed = true;
                    if (count + 1 == num_comp) {
                        intOb.hangup_on_complete = true;
                    }
                    else {
                        intOb.hangup_on_complete = false;
                    }
                    interlude.push(intOb);
                    start_time.add(moment.duration(intOb.duration, 's'));
                }
                else if ($(this).children().next().val() == 'media') {
                    var mediaOb = {}
                    mediaOb.argument = [$(this).children().next().next().next().val()];
                    mediaOb.start_time = moment.utc(start_time.asMilliseconds()).format("HH:mm:ss");
                    mediaOb.duration = parseFloat($(this).children().next().next().val());
                    mediaOb.is_streamed = true;
                    if (count + 1 == num_comp) {
                        mediaOb.hangup_on_complete = true;
                    }
                    else {
                        mediaOb.hangup_on_complete = false;
                    }
                    media.push(mediaOb);
                    start_time.add(moment.duration(mediaOb.duration, 's'));
                }
                else if ($(this).children().next().val() == 'jingle') {
                    var jingOb = {};
                    jingOb.argument = $(this).children().next().next().next().val();
                    jingOb.start_time = moment.utc(start_time.asMilliseconds()).format("HH:mm:ss");
                    jingOb.duration = parseFloat($(this).children().next().next().val());
                    jingOb.is_streamed = true;
                    if (count + 1 == num_comp) {
                        jingOb.hangup_on_complete = true;
                    }
                    else {
                        jingOb.hangup_on_complete = false;
                    }
                    jingle.push(jingOb);
                    start_time.add(moment.duration(jingOb.duration, 's'));
                }
                count++;
            });
            newProgram.tts = tts;
            newProgram.Media = media;
            newProgram.Jingle = jingle;
            newProgram.Interlude = interlude;
        }
        return JSON.stringify(newProgram);
    }

    /**
     * Adds a text component to the right list with the text written in the modal
     */
    $("#text_submit").click(function() {
        $('#sortable2').prepend(
            '<li class="ui-state-default"><input type="hidden" value="tts">' + $("#new_text").val() + '</li>'
        );
        $('#est_time').text(function () {
            est_time.add(moment.duration(calculate_time($("#new_text").val()), 's'));
            return moment.utc(est_time.asMilliseconds()).format("HH:mm:ss");
        });
        $("#new_text").val('');
        $('#sortables').show();
        $('#sortable2').show();
    })
});

/**
 * Estimates the time the TTS synthesizer will take to speak a text
 * @param sentence -> the text will be synthesized by the TTS engine
 * @returns {number}
 */
function calculate_time(sentence) {
    var words = sentence.split(' ');
    return words.length * 0.44 + 2;
}