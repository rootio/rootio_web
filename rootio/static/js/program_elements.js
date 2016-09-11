/**
 * Created by vmcb on 02-09-2016.
 */
var est_time = moment.duration(0,'s');

program_data ='' +
    '<div class="form-group">' +
        '<div id="program_data">' +
            '<label class="control-label" >Number of the host</label>' +
            '<input class="form-control" id="host_number" name="host_number" type="text">' +
            '<label>Duration</label>' +
            '<input class="form-control" id="duration" name="duration" type="text">' +
        '</div>'+
    '</div>';

cont_type = '' +
    '<div class="form-group">' +
        '<div id="cont_type">' +
            '<label class="control-label">Please select the type of the content you want to add: </label>' +
            '<select class="form-control" id="content_type" >' +
            '<option></option>' +
            '<option>Audio Files</option>' +
            '<option>SMS</option>' +
            '<option>Aggregators </option>' +
            '</select>' +
        '</div>'+
    '</div>';

aggregators = '' +
    '<select  class="form-control"  id="aggregator">' +
        '<option></option>' +
    '</select>';

media = '' +
    '<select  class="form-control"  id="media">' +
        '<option></option>' +
        '<option>Jingle</option>' +
        '<option>Interlude</option>' +
        '<option>Other Audio Files</option>' +
    '</select>';

sortables = '' +
    '<div class="row">' +
        '<div id="sortables">' +
            '<div class="col-md-4">' +
                '<label class="control-label">Existing Content: </label>' +
                '<ul id="sortable1" class="connectedSortable" style="width: 100%; min-height: 45px; border: 1px solid #ccc; border-radius: 4px;">' +
                '</ul>' +
            '</div>'+
            '<div class="col-md-4">' +
                '<label class="control-label">New Program Content : </label>' +
                '<ul id="sortable2" class="connectedSortable" style="width: 100%; min-height: 45px; border: 1px solid #ccc; border-radius: 4px;">' +
                '</ul>' +
            '</div>'+

            '<div class="col-md-4">' +
                '<!-- Trigger the modal with a button -->' +
                '<p>Estimated time of the program:<span id="est_time">0</span></p>' +
                '<button type="button" class="btn btn-success" style="margin-bottom: 10px; background-color: #009688; border-color: white;"data-toggle="modal" data-target="#myModal">Add Text Section</button>' +
                '<!-- Modal -->' +
                    '<div id="myModal" class="modal fade" role="dialog">' +
                        '<div class="modal-dialog">-->' +
                        '<!-- Modal content-->' +
                            '<div class="modal-content">' +
                                '<div class="modal-header">' +
                                    '<button type="button" class="close" data-dismiss="modal">&times;</button>' +
                                    '<h4 class="modal-title">Add new text section</h4>' +
                                    '<h6 class="modal-title"> In this box you can add text that you want, the TTS synthesizer will convert the text to speech, this can be useful to make kind of separators</h6>'+
                                '</div>'+
                                '<div class="modal-body">' +
                                    '<textarea id="new_text" style="width:100%; min-height: 100px;"></textarea>' +
                                '</div>' +
                                '<div class="modal-footer">' +
                                    '<button id="text_submit" type="button" class="btn btn-success" style="background-color: #009688; border-color: white; resize: none;" data-dismiss="modal">Add New Section</button>' +
                                '</div>' +
                            '</div>' +
                        '</div>' +
                    '</div>' +
            '</div>'+
        '</div>'+
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
        $('#aggregator').hide();
        $('#media').hide();
        $('#program_data').show();
    }
    else {
        $('#cont_type').show();
        $('#program_data').hide();
        $('#sortables').hide();
    }
}