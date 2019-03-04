$( function() {
  $('.button-delete').click(function(){
    var el = this;
    var id = this.id;
    var splitid = id.split("-");

    // Delete id
    var deleteid = splitid[1];

    // Confirm box
    bootbox.confirm("Are you sure want to delete?", function(result) {
      if(result){
        // AJAX Request
        $.ajax({
          url: deleteid+'/delete',
          type: 'GET',
          success: function(response){
            $(el).closest('tr').css('background','tomato');
            $(el).closest('tr').fadeOut(500, function(){
              $(this).remove();
            });
          }
        });
      }
    });
  });
});
