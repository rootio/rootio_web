/*
 * Helper script to submit flask forms from a Bootstrap modal dialog
 * Author: Josh Levinger, 2013
 */

$(document).ready(function() {
    $('.modal-dialog.inline-form button[data-submit').click(function(event) {
        event.preventDefault();

        //get the parent .inline-form element
        inline_form = $(event.target).parents('.inline-form');

        //pull the data attributes we need
        var post_url = inline_form.data('url');
        var input_prefix = inline_form.data('prefix');

        //serialize the form inputs
        var form_inputs = inline_form.find('input');
        var form_data = form_inputs.serializeArray();

        //remove prefix
        var cleaned_data = {};
        for (var i in form_data) {
            var name = form_data[i].name;
            var cleaned_name = name.replace(input_prefix,'');
            cleaned_data[cleaned_name] = form_data[i].value;
        }

        //submit them via ajax
        $.post(post_url, {
            data:JSON.stringify(cleaned_data, null, '\t'),
            dataType:'json',
            contentType: 'application/json;charset=UTF-8',
            success: function(data, status, xhr) {
                console.log('success data',data);
                console.log('status',status);
                //insert new option into the appropriate select

                //and close modal
                
            },
            error: function(xhr, status, err) {
                console.log('error status',status);
                console.log('code',err);
                //show user field validation
                
            },
        });

        console.log('submitted');
    });
})
