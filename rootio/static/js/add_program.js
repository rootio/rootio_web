/**
 * Created by vmcbaptista on 02-09-2016.
 * Prepares the form for adding a program
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
    $('#cont_type').hide();
    $('#program_data').hide();
    $('#aggregator').hide();
    $('#media').hide();
    $('#sortables').hide();
}

/**
 * Prepares the form for the addition
 */
$( function() {
    addElements();
    hideElements();
    adjustForm();
});