function filterListItems(input) {
  var query = $(input).val();
  var ul = $("ul[data-filtered-by='"+$(input).attr('id')+"']");
  $(ul).children('li').each(function() {
    var title = $(this).text();
    if (title.toUpperCase().includes(query.toUpperCase())) {
      $(this).removeClass('hidden');
    } else {
      $(this).addClass('hidden');
    }
  });
};
