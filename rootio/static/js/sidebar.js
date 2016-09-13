/**
 * Created by fcl on 30-08-2016.
 */

/*
$(document).ready(function () {

        var listItems = $(".navside-tabs li");

        $(".navside-tabs li").each(function () {

            if($.trim($(this).children().first().text()) == localStorage.getItem("dropHead")){

                $(this).children().children("i").css({
                        color: "#009688",
                });
                $(this).css({backgroundColor:"white"})
                $(this).addClass("open")

                $(this).each(function () {
                    console.log($(this).children()[1])
                    console.log(localStorage.getItem("dropContent"))
                })

            }else{
                console.log("Not found")
            }


        })


    }*/
/*
    $(".side-nav .dropdown-menu li a").click(function (e) {
        e.stopPropagation();

        localStorage.setItem("dropContent", $(this).text());
        localStorage.setItem("dropHead", $.trim($(this).parent().parent().parent().children("a").text()) );

    })
})*/


/*Handle th nav bar operations close and open*/
$(".toggle-nav").click(function () {
    if ( $(".side-nav").css("width") == "250px") {
        /*console.log("Close Bar" + $(".side-nav").css("width"))*/
        closeSideBar()
    }
    else{
        /*console.log("Open Bar"+ $(".side-nav").css("width"))*/
        openSideBar()

    }
})

$(".side-nav .dropdown").click(function () {
    if($(".side-nav").css("width") == "50px") {
        openSideBar()
    }
})

/*APPLY CSS to close the nav bar*/
function closeSideBar(){
    $(".side-nav .navside-tabs a span, .side-nav .navside-tabs a .fa-chevron-down").css({
        display:"none"
    })
    $(".side-nav").css({
        width: "50px"
    })
    $(".content-container").css({
       marginLeft: "50px"
    })
    $(".header-content-header").css({
       marginLeft: "50px"
    })
    $(".button-form-row").css({
       marginLeft: "50px"
    })
    closed = true
}

/*APPLY css to open the nav bar*/
function openSideBar(){
    $(".side-nav").css({
        width: "250px"
    })
    $(".side-nav .navside-tabs a span, .side-nav .navside-tabs a .fa-chevron-down").css({
        display: "inline"
    })
    $(".content-container").css({
        marginLeft: "250px"
    })
    $(".header-content-header").css({
        marginLeft: "250px"
    })
    $(".button-form-row").css({
       marginLeft: "250px"
    })
    closed = false;
}

/*Hover events CSS*/
$(".side-nav .dropdown,.side-nav .no-dropdown").mouseover(function(){
    $(this).children("a").children("i").css({
        color: "#009688"
    })
}).mouseout(function () {
    $(this).children("a").children("i").css({
        color: "#3c3c3c"
    })
})

$(".side-nav .dropdown-menu li a").mouseover(function () {
    $(this).children("i").css({
        color: "#009688"
    })
}).mouseout(function () {
    $(this).children("i").css({
        color: "#3c3c3c"
    })
})
/*End Hover and CSS Events*/