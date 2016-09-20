/**
 * Created by fcl on 03-09-2016.
 */
$(document).ready(function() {
    $('#table-pager').DataTable({
  "columnDefs": [
    { "orderable": false, "targets": -1},
    { "searchable": false, "targets": -1 }
  ]
});
} );

$(document).ready(function() {
    $('#table-pager-radio-dash').DataTable({
  "columnDefs": [
    { "orderable": false, "targets": [1,2,3,4,5,6,7]},
    { "searchable": false, "targets":[1,2,3,4,5,6,7] }
  ]
});
} );