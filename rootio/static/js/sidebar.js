/**
 * Created by fcl on 30-08-2016.
 */
$(".toggle-nav").click(function () {
    if ( $(".side-nav").css("width") == "250px") {
        console.log("Close Bar" + $(".side-nav").css("width"))
        closeSideBar()
    }
    else{
        console.log("Open Bar"+ $(".side-nav").css("width"))
        openSideBar()

    }
})


function closeSideBar(){
    $(".side-nav").css({
        width: "0px"
    })
    $(".content-container").css({
       marginLeft: "0px"
    })
    $(".header-content-header").css({
       marginLeft: "0px"
    })
    closed = true
}

function openSideBar(){
    $(".side-nav").css({
        width: "250px"
    })
    $(".content-container").css({
        marginLeft: "250px"
    })
    $(".header-content-header").css({
        marginLeft: "250px"
    })
    closed = false;
}