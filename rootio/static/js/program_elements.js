/**
 * Created by vmcb on 02-09-2016.
 */
var est_time = moment.duration(0,'s');

program_data ='' +
    '<div id="program_data">' +
    '<label>Number of the host</label>' +
    '<input id="host_number" name="host_number" type="text">' +
    '<label>Duration</label>' +
    '<input id="duration" name="duration" type="text">' +
    '</div>';

cont_type = '' +
    '<div id="cont_type">' +
    '<label>Please select the type of the content you want to add: </label>' +
    '<select id="content_type">' +
    '<option></option>' +
    '<option>Audio Files</option>' +
    '<option>SMS</option>' +
    '<option>Aggregators</option>' +
    '</select>' +
    '<!-- Trigger the modal with a button -->' +
    '<button type="button" class="btn btn-info btn-lg" data-toggle="modal" data-target="#myModal">Add New Text</button>' +
    '<!-- Modal -->' +
    '<div id="myModal" class="modal fade" role="dialog">' +
    '   <div class="modal-dialog">' +
    '      <!-- Modal content-->' +
    '      <div class="modal-content">' +
    '        <div class="modal-header">' +
    '        <button type="button" class="close" data-dismiss="modal">&times;</button>' +
    '        <h4 class="modal-title">Add New Text</h4>' +
    '      </div>' +
    '      <div class="modal-body">' +
    '        <textarea id="new_text"></textarea>' +
    '      </div>' +
    '      <div class="modal-footer">' +
    '        <button id="text_submit" type="button" class="btn btn-default" data-dismiss="modal">Add</button>' +
    '      </div>' +
    '    </div>' +
    '  </div>' +
    '</div>' +
    '</div>';

aggregators = '' +
    '<select id="aggregator">' +
    '<option></option>' +
    '</select>';

media = '' +
    '<select id="media">' +
    '<option></option>' +
    '<option>Jingle</option>' +
    '<option>Interlude</option>' +
    '<option>Other Audio Files</option>' +
    '</select>';

sortables = '' +
    '<div id="sortables">' +
    '<ul id="sortable1" class="connectedSortable">' +
    '</ul>' +
    '<ul id="sortable2" class="connectedSortable">' +
    '</ul>' +
    '</div>';

durationHTML = '<p>Estimated time of the program:<span id="est_time">0</span></p>';

function adjustForm() {
    if ($('#program_type option:selected').text() == '') {
        $('#cont_type').hide();
        $('#program_data').hide();
        $('#sortables').hide();
    }
    else if ($('#program_type option:selected').text() == 'Call-in Show') {
        $('#sortables').hide();
        $('#cont_type').hide();
        $('#program_data').show();
    }
    else {
        $('#cont_type').show();
        $('#program_data').hide();
        $('#sortables').hide();
    }
}