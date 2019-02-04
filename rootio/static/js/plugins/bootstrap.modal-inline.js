/*
 * Helper script to submit flask forms from a Bootstrap modal dialog
 * Author: Josh Levinger, 2013
 */

$(document).ready(function() {
    $('.modal-dialog.inline-form button[data-submit]').click(function(event) {
        event.preventDefault();

        //get the parent .inline-form element
        var inline_form = $(event.target).parents('.inline-form');

        //pull the data attributes we need
        var post_url = inline_form.data('url');
        var input_prefix = inline_form.data('prefix');

        //serialize the form inputs
        var form_inputs = inline_form.find('input, select');
        var form_data = form_inputs.serializeArray();

        //remove prefix
        var cleaned_data = {};
        for (var i in form_data) {
            var name = form_data[i].name;
            var cleaned_name = name.replace(input_prefix,'');
            cleaned_data[cleaned_name] = form_data[i].value;
        }

        //clear previous errors
        inline_form.find('.help-block.error').remove();
        inline_form.find('.control-group.error').removeClass('error');

        //submit via ajax
        $.ajax(post_url, {
            type: 'POST',
            data: JSON.stringify(cleaned_data, null, '\t'),
            dataType: 'json',
            contentType: 'application/json;charset=UTF-8',
            success: function(data, status, xhr) {
                //insert new option into the appropriate select
                new_option = $('<option value='+data.result.id+'>'+data.result.string+'</option>');
                main_input_id = input_prefix.replace('_inline-','');
                if (main_input_id) {
                  $('select#'+main_input_id).append(new_option);
                  $('select#'+main_input_id).children('option').last().attr('selected','selected');
                }

                //clear fields
                form_inputs.val('');

                //and close modal
                inline_form.parents('.modal').modal('hide');
            },
            error: function(xhr, status, err) {
              if (xhr.responseJSON && xhr.responseJSON.errors) {
                var errors = xhr.responseJSON.errors;

                //show user field validation
                for (var field in errors) {
                  var sel = input_prefix+field;
                  var label = inline_form.find('label[for='+sel+']');
                  label.parents('.control-group').addClass('error');
                  //error goes on control-group
                  var msg = $('<span class="help-block error">'+errors[field]+'</span>');
                  label.siblings('.controls').append(msg);
                  //message goes at end of controls
                }
              }
            },
        });

    });
})
