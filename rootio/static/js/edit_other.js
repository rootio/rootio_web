/**
 * Created by vmcb on 02-09-2016.
 */
function addElements() {
    submit = $('fieldset').children().last();
    $('fieldset').children().last().remove();
    $('fieldset').append(program_data);
    $('fieldset').append(cont_type);
    $('fieldset').append(aggregators);
    $('fieldset').append(media);
    $('fieldset').append(sortables);
    /*$('fieldset').append(durationHTML);*/
    $('fieldset').append(submit);
}

function hideElements() {
    $('#program_data').hide();
    $('#aggregator').hide();
    $('#media').hide();
}


$(function() {
    console.log(moment.duration(8.005,'s'));
    addElements();
    hideElements();
    est_time = moment.duration(time_prog,'s');
    tts = description.tts;
    media = description.Media;
    interlude = description.Interlude;
    jingle = description.Jingle;
    components = [];
    for(i in tts) {
        tts[i].type = 'tts';
        components.push(tts[i]);
    }
    for(i in media) {
        media[i].type = 'media';
        components.push(media[i]);
    }
    for(i in interlude) {
        interlude[i].type = 'interlude';
        components.push(interlude[i]);
    }
    for(i in jingle) {
        jingle[i].type = 'jingle';
        components.push(jingle[i]);
    }
    components.sort(function(a,b) {
        return moment.duration(a.start_time).asSeconds() - moment.duration(b.start_time).asSeconds();
    });
    console.log(components);
    for (i in components) {
        console.log(i);
        if (components[i].type == 'jingle') {
            requestName(components[i].argument,'jingle',components[i].duration);
        }
        else if (components[i].type == 'media') {
            requestName(components[i].argument,'media',components[i].duration);
        }
        else if (components[i].type == 'interlude') {
            requestName(components[i].argument,'interlude',components[i].duration);
        }
        else {
            $('#sortable2').append(
                '<li class="ui-state-default"><input type="hidden" value="tts">' + components[i].argument + '</li>'
            );
        }

    }

    function requestName(path,type,duration) {
        console.log(path);
        $.ajax({
            method: 'POST',
            url: '/radio/media/find',
            data: {'path':path,'csrf_token':token},
            async: false,
            success: function (data) {
                namefun(data,type,duration,path);
            },
            error: function (error) {
                console.log(errors)
            }
        });
    }

    function namefun(name,type,duration,path) {
        $('#sortable2').append(
            '<li class="ui-state-default">' +
            '<input type="hidden" value="'+type+'">' +
            '<input type="hidden" name ="duration" value="' + duration + '">' +
            '<input type="hidden" name ="path" value="' + path + '">' +  name + '</li>'
        );
    }
});