function addMessages(username,date,message){
    //alert(username +" "+ date + " "+message)
        $(".chatBoxBody").append(
            "<tr>"+
             "<td>" +
                "<div class='msg-row'>" +
                    "<div class='avatar-left'></div>" +
                        "<div class='message'>" +
                            "<span class='user-label''><a href='#' style='color: #6D84B4;'></a>"+ username +
                            "<span class='msg-time'>"+date+"</span></span><br/>"+ message +
                        "</div>" +
                    "</div>" +
                "</td>" +
            "</tr>"
        )
    $(".chatBoxBody").animate({ scrollTop: $(document).height() }, "slow");
}

$('.fa-question-circle').click(
    function(){
        $('#chatBox').css({
            'display' : 'block'
        });
        addMessages("Bot","14:00:00", "Hi it's me the Bot.")
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
            addMessages("User","14:00:00",getCmd)
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
        url:'bot/savechat',
        method: 'POST',
        data:{msg: message},
        success:function(data){
            //console.log(data)
             addMessages("Bot","14:00:00",data)
        },
        error: function(error){
            console.log(errors)
        }
    })
}
