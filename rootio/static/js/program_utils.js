/**
 * Created by vmcb on 02-09-2016.
 */
$( function() {
    $('#est_time').text(moment.utc(est_time.asMilliseconds()).format("HH:mm:ss"));


    $( "#sortable1" ).sortable({
        connectWith: ".connectedSortable",
        forcePlaceholderSize: false,
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
        connectWith: ".connectedSortable",
        remove: function(e, ui) {
            ui.item.hide();
        }
    });

    $('#sortable2').on( "sortreceive", function( event, ui ) {
        element = ui['item'];
        if (element.children().val() == 'tts') {
            $('#est_time').text(function () {
                est_time.add(moment.duration(calculate_time(element.text()), 's'));
                return moment.utc(est_time.asMilliseconds()).format("HH:mm:ss");
            });
        }
        else {
            $('#est_time').text(function () {
                est_time.add(moment.duration(parseFloat(element.children().next().val()),'s'));
                return moment.utc(est_time.asMilliseconds()).format("HH:mm:ss");
            });
        }
    });

    $('#sortable2').on( "sortremove", function( event, ui ) {
        element = ui['item'];
        if (element.children().val() == 'tts') {
            $('#est_time').text(function () {
                est_time.subtract(moment.duration(calculate_time(element.text()), 's'));
                return moment.utc(est_time.asMilliseconds()).format("HH:mm:ss");
            });
        }
        else {
            $('#est_time').text(function () {
                est_time.subtract(moment.duration(parseFloat(element.children().next().val()),'s'));
                return moment.utc(est_time.asMilliseconds()).format("HH:mm:ss");
            });
        }
    });

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
                    console.log(errors)
                }
            });
        }
    });

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
                console.log(errors)
            }
        });
    });

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

    $('#duration').change(function () {
        $('#est_time').text(function () {
            return moment.utc(moment.duration($('#duration').val()).asMilliseconds()).format("HH:mm:ss");
        });
    });

    $('#program_type').change(function () {
        adjustForm();
    });

    $('#cancel').click(function () {
        $(this).closest('form').find("input[type=text], textarea, select").val("");
        $('#est_time').text('00:00:00');
        est_time = moment.duration(0,'s');
        $('#sortable1').empty();
        $('#sortable2').empty();
    });

    $("form").submit(function(e){
        description = generateDescription();
        console.log(description);
        $('fieldset').append("<input type='hidden' name='description' value='"+description+"'>");
        if ($('#program_type option:selected').text() == 'Call-in Show') {
            $('fieldset').append("<input type='hidden' name='est_time' value='"+$('#duration').val()+"'>");
        }
        else {
            $('fieldset').append("<input type='hidden' name='est_time' value='"+$('#est_time').text()+"'>");
        }
    });

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
                if($(this).children().val() == 'tts') {
                    var ttsOb = {};
                    ttsOb.argument = $(this).text();
                    console.log(start_time);
                    console.log(start_time.asMilliseconds());
                    console.log(moment.utc(start_time.asMilliseconds()));
                    ttsOb.start_time = moment.utc(start_time.asMilliseconds()).format("HH:mm:ss");
                    console.log( ttsOb.start_time);
                    ttsOb.duration = calculate_time($(this).text());
                    ttsOb.is_streamed = true;
                    if (count + 1 == num_comp) {
                        ttsOb.hangup_on_complete = true;
                    }
                    else {
                        ttsOb.hangup_on_complete = false;
                    }
                    tts.push(ttsOb);
                    console.log(start_time);
                    console.log(ttsOb.duration);
                    console.log(moment.duration(ttsOb.duration),'s');
                    start_time.add(moment.duration(ttsOb.duration, 's'));
                    console.log(start_time);
                }
                else if ($(this).children().val() == 'interlude') {
                    var intOb = {};
                    intOb.argument = $(this).children().next().next().val();
                    console.log(start_time);
                    intOb.start_time = moment.utc(start_time.asMilliseconds()).format("HH:mm:ss");
                    console.log( intOb.start_time);
                    intOb.duration = parseFloat($(this).children().next().val());
                    intOb.is_streamed = true;
                    if (count + 1 == num_comp) {
                        intOb.hangup_on_complete = true;
                    }
                    else {
                        intOb.hangup_on_complete = false;
                    }
                    interlude.push(intOb);
                    console.log(start_time);
                    console.log(intOb.duration);
                    console.log(moment.duration(intOb.duration),'s');
                    start_time.add(moment.duration(intOb.duration, 's'));
                    console.log(start_time);
                }
                else if ($(this).children().val() == 'media') {
                    var mediaOb = {}
                    mediaOb.argument = [$(this).children().next().next().val()];
                    console.log(start_time);
                    mediaOb.start_time = moment.utc(start_time.asMilliseconds()).format("HH:mm:ss");
                    console.log( mediaOb.start_time);
                    mediaOb.duration = parseFloat($(this).children().next().val());
                    mediaOb.is_streamed = true;
                    if (count + 1 == num_comp) {
                        mediaOb.hangup_on_complete = true;
                    }
                    else {
                        mediaOb.hangup_on_complete = false;
                    }
                    media.push(mediaOb);
                    console.log(start_time);
                    console.log(mediaOb.duration);
                    console.log(moment.duration(mediaOb.duration),'s');
                    start_time.add(moment.duration(mediaOb.duration, 's'));
                    console.log(start_time);
                }
                else if ($(this).children().val() == 'jingle') {
                    var jingOb = {};
                    jingOb.argument = $(this).children().next().next().val();
                    console.log(start_time);
                    jingOb.start_time = moment.utc(start_time.asMilliseconds()).format("HH:mm:ss");
                    console.log( jingOb.start_time);
                    jingOb.duration = parseFloat($(this).children().next().val());
                    jingOb.is_streamed = true;
                    if (count + 1 == num_comp) {
                        jingOb.hangup_on_complete = true;
                    }
                    else {
                        jingOb.hangup_on_complete = false;
                    }
                    jingle.push(jingOb);
                    console.log(start_time);
                    console.log(jingOb.duration);
                    console.log(moment.duration(jingOb.duration),'s');
                    start_time.add(moment.duration(jingOb.duration, 's'));
                    console.log(start_time);
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

function calculate_time(sentence) {
    var words = sentence.split(' ');
    return words.length * 0.44 + 2;
}