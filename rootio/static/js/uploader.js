$(function() {
  $('#btnApiStart').on('click', function(evt) {
    evt.preventDefault();
    $('#drag-and-drop-zone').dmUploader('start');
  });

  $('#btnApiCancel').on('click', function(evt) {
    evt.preventDefault();
    $('#drag-and-drop-zone').dmUploader('cancel');
  });

  // Creates a new file and add it to our list
  function ui_multi_add_file(id, file) {
    var template = $('#files-template').text();
    template = template.replace('%%filename%%', file.name);

    template = $(template);
    template.prop('id', 'uploaderFile' + id);
    template.data('file-id', id);

    $('#files').find('li.empty').fadeOut(); // remove the 'no files yet'
    $('#files').prepend(template);
  }

  // Removes a file from the queue (if auto upload is set to false)
  function ui_multi_remove_file(id, file) {
    $('#files').find('li#uploaderFile' + id).fadeOut(); // remove the file from the list
  }

  // Changes the status messages on our list
  function ui_multi_update_file_status(id, status, message) {
    $('#uploaderFile' + id).find('span').html(message).prop('class', 'status text-' + status);
  }

  // Updates a file progress, depending on the parameters it may animate it or change the color.
  function ui_multi_update_file_progress(id, percent, color, active) {
    color = (typeof color === 'undefined' ? false : color);
    active = (typeof active === 'undefined' ? true : active);

    var bar = $('#uploaderFile' + id).find('div.progress-bar');

    bar.width(percent + '%').attr('aria-valuenow', percent);
    bar.toggleClass('progress-bar-striped progress-bar-animated', active);

    if (percent === 0) {
      bar.html('');
    } else {
      bar.html(percent + '%');
    }

    if (color !== false) {
      bar.removeClass('bg-success bg-info bg-warning bg-danger');
      bar.addClass('bg-' + color);
    }
  }

  // Toggles the disabled status of Star/Cancel buttons on one particual file
  function ui_multi_update_file_controls(id, start, cancel, wasError) {
    wasError = (typeof wasError === 'undefined' ? false : wasError);

    $('#uploaderFile' + id).find('button.start').prop('disabled', !start);
    $('#uploaderFile' + id).find('button.cancel').prop('disabled', !cancel);

    if (!start && !cancel) {
      $('#uploaderFile' + id).find('.controls').fadeOut();
    } else {
      $('#uploaderFile' + id).find('.controls').fadeIn();
    }

    if (wasError) {
      $('#uploaderFile' + id).find('button.start').html('Retry');
    }
  }


  $('#drag-and-drop-zone').dmUploader({
    url: '/api/upload/media',
    dnd: true,
    auto: true,
    queue: true,
    extraData: function() {
      return {
        "track_id": $('#track').val()
      };
    },
    onDragEnter: function() {
      this.addClass('active');
    },
    onDragLeave: function() {
      this.removeClass('active');
    },
    onInit: function() {
    },
    onComplete: function() {
    },
    onNewFile: function(id, file) {
      ui_multi_add_file(id, file);
    },
    onBeforeUpload: function(id) {
      ui_multi_update_file_status(id, 'uploading', 'Uploading...');
      // ui_multi_update_file_progress(id, 0, '', true);
    },
    // onUploadProgress: function(id, percent) {
    //   ui_multi_update_file_progress(id, percent);
    // },
    onUploadSuccess: function(id, data) {
      ui_multi_update_file_status(id, 'success', 'Upload Complete');
      // ui_multi_update_file_progress(id, 100, 'success', false);
    },
    onUploadCanceled: function(id) {
      ui_multi_update_file_status(id, 'warning', 'Canceled by User');
      // ui_multi_update_file_progress(id, 0, 'warning', false);
      ui_multi_update_file_controls(id, true, false);
    },
    onUploadError: function(id, xhr, status, message) {
      if (xhr.responseJSON && xhr.responseJSON.message) {
        ui_multi_update_file_status(id, 'danger', xhr.responseJSON.message);
      } else {
        ui_multi_update_file_status(id, 'danger', message);
      }
      // ui_multi_update_file_progress(id, 0, 'danger', false);
    },
    onFallbackMode: function() {
    },
    onFileSizeError: function(file) {
    }
  });
});
