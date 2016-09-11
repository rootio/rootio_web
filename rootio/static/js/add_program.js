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
    $('#cont_type').hide();
    $('#program_data').hide();
    $('#aggregator').hide();
    $('#media').hide();
    $('#sortables').hide();
}

$( function() {
    addElements();
    hideElements();
    adjustForm();
});