<?php
//http_response_code(500);
//http_response_code(404);
echo "hello There crazy world!!";
echo "\nThis is the post data";
print_r($_POST)
?>



<?php
  if( $_POST["name"] || $_POST["food"] )
  {
     echo "Welcome $_POST['name'] \n";
     echo "Favorite food is  $_POST['food'] ";
     exit();
  }
?>
<html>
<body>
  <form action="<?php $_PHP_SELF ?>" method="POST">

  Name: <input type="text" name="name" />
  Food: <input type="text" name="food" />

  </form>
</body>
</html>



 
