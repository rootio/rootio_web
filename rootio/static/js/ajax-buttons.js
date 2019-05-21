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



function toggleTableItem(el, state, toggleid) {
  // Replacement text
  var toggledText = '';
  if (state === 'enable') {
    toggledText = 'Approved';
    toggledText += ' <a href="#" onclick="toggleTableItem(this, \'disable\', '+toggleid+')">';
    toggledText += '(discard)</a>';
  } else {
    toggledText = 'Not approved';
    toggledText += ' <a href="#" onclick="toggleTableItem(this, \'enable\', '+toggleid+')">';
    toggledText += '(approve)</a>';
  }


  // Confirm box
  bootbox.confirm("Are you sure want to " + state + "?", function(result) {
    if(result){
      // AJAX Request
      $.ajax({
        url: toggleid+'/'+state,
        type: 'GET',
        success: function(response){
          $(el).closest('td').fadeOut();
          $(el).closest('td').fadeIn();
          $(el).closest('td').html('<small>'+toggledText+'</small>');
        }
      });
    }
  });
};
