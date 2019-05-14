function deleteTableItem(el, deleteid) {
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
  };
