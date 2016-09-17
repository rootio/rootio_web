$(document).ready(function() {
    var csrftoken = $('meta[name=csrf-token]').attr('content');
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
    //sitewide customizations here

  /*  $('form#language-selector select').on('change',function() {
        console.log('language changed');
        this.form.submit();
    });*/
});
