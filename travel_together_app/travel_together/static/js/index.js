$(document).ready(function() {
    $("#openFormPopup").click(function() {
        $("#formPopupModal").show();
        $("#formPopupOverlay").show();
    });

    $("#closeFormPopup, #formPopupOverlay").click(function() {
        $("#formPopupModal").hide();
        $("#formPopupOverlay").hide();
    });
});
