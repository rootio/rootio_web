function addMessages(username,date,message){
    if(username == "Bot") {
        $(".chatBoxBody table").append(
            "<tr>" +
            "<td>" +
            "<div class='msg-row'>" +
            "<div class='avatar-left'></div>" +
            "<div class='message'>" +
            "<span class='user-label''><a href='#' style='color: #6D84B4;'></a>" + username +
            "<span class='msg-time'>" + date + "</span></span><br/><span class='msg-text'>" + message +
            "</span></div>" +
            "</div>" +
            "</td>" +
            "</tr>"
        )
    }
    else{
        var user = $('.user-name').text();
       if(user != "")
       {
           username = user;
       }

        $(".chatBoxBody table").append(
            "<tr>" +
            "<td>" +
            "<div class='msg-row'>" +
            "<div class='avatar-user'> <img width='24' height='24' src='/static/img/avatar.png'/></div>" +
            "<div class='message'>" +
            "<span class='user-label''><a href='#' style='color: #6D84B4;'></a>" + username +
            "<span class='msg-time'>" + date + "</span></span><br/><span class='msg-text'>" + message +
            "</span></div>" +
            "</div>" +
            "</td>" +
            "</tr>"
        )
    }
        $('.chatBoxBody').animate({
            scrollTop: $('.chatBoxBody').get(0).scrollHeight
        });
}
/*
$('.fa-question-circle').one("click", function(){
        $('#chatBox').css({
            'display' : 'block'
        });
        addMessages("Bot",date(), "Hi it's me the Bot. Type help to know more about my help system.")
});*/
var clicks = 0
$('.fa-question-circle').click(function() {
  if (clicks == 0) {
    $('#chatBox').css({
            'display' : 'block'
        });
        addMessages("Bot",date(), "Hi it's me the Bot. Type help to know more about my help system.");
      clicks = clicks + 1;
  } else {
    $('#chatBox').css({
            'display' : 'block'
        });
  }
});



$('#minimizeChat').click(
    function(){
        $('#chatBox').css({
            'display' : 'none'
        });
    });

/*Chat Ajax*/
$('#chatBoxText input').keypress(function(e){
    if(e.keyCode == 13){
        var getCmd = $('#helpCmd').val()
        if(getCmd == ""){
        }
        else
        {
            addMessages("User",date(),getCmd)
            sendCommand(getCmd);
            $('#helpCmd').val('');
        }
    }
});


/*Ajax request*/
function sendCommand(message){
    //alert(message);
    $('#helpCmd').val('');
    $.ajax({
        url:'/bot/savechat',
        method: 'POST',
        data:{msg: message},
        success:function(data){
            for(first in data){
                break;
            }
            console.log(first)

            /*This is a way to check if the object returned has object inside. Every first member of an array of arrays will be a number
            * and that number is their respective id on the database.*/
            if( $.isNumeric(first)){
                /*Compose the codes that a user is able to use*/
                var message = "";
                count = 0;
                for(index in data){
                    if(data[index].description == null) {
                        message = message + data[index].code + "<br>"
                    }
                    else {
                        if (count == 0) {
                            message = 'Hi! <br>These are the commands you can use to receive my help.<br>' + message + data[index].code + " -> " + data[index].description + "<br>"
                        }else {
                            message = message + data[index].code + " -> " + data[index].description + "<br>"
                        }
                        count++;
                    }
                }
                addMessages("Bot",date(),message)
            }
            else{
                addMessages("Bot",date(),data.answer)
            }

        },
        error: function(error){
            console.log(errors)
        }
    })
}

function date(){
    var d = new Date();
    return  d.toLocaleString();
}