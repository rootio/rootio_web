/**
 * Created by vmcbaptista on 02-09-2016.
 * Prepares the form for editing other programs than Call-In shows
 */

/**
 * Add elements to the form
 */
function addElements() {
    submit = $('fieldset').children().last();
    $('fieldset').children().last().remove();
    $('fieldset').append(program_data);
    $('fieldset').append(cont_type);
    $('fieldset').append(aggregators);
    $('fieldset').append(media);
    $('fieldset').append(sortables);
    $('fieldset').append(submit);
}

/**
 * Hide some elements that aren't necessary initially
 */
function hideElements() {
    $('#program_data').hide();
    $('#aggregator').hide();
    $('#media').hide();
}

/**
 * Prepares the form for the edition
 */
$(function() {
    addElements();
    hideElements();
    est_time = moment.duration(time_prog,'s');
    // The following lines of code creates an array with all the components of an existing program that then is
    // sorted by their sequence along the program
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

    /**
     * Get's the name of the file using AJAX
     * @param path
     * @param type
     * @param duration
     */
    function requestName(path,type,duration) {
        console.log(path);
        $.ajax({
            method: 'POST',
            url: '/radio/media/find',
            data: {'path':path,'csrf_token':token},
            async: false,
            success: function (data) {
                addMedia(data,type,duration,path);
            },
            error: function (error) {namefun
                console.log(errors)
            }
        });
    }

    /**
     * Add a new file entry in the right list
     * @param name
     * @param type
     * @param duration
     * @param path
     */
    function addMedia(name,type,duration,path) {
        $('#sortable2').append(
            '<li class="ui-state-default">' +
            '<input type="hidden" value="'+type+'">' +
            '<input type="hidden" name ="duration" value="' + duration + '">' +
            '<input type="hidden" name ="path" value="' + path + '">' +  name + '</li>'
        );
    }
});