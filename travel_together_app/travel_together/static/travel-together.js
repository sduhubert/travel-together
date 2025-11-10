$(document).ready(function() {
    $('.original').on("mouseenter", function() {
        let link = $("<a>")
            .attr("href", "#")
            .addClass("reply")
            .text("Reply to this trip");
        $(this).append(link);
        link.on("click", function() {
            trip_id = parseInt(
                $(this)
                    .parent()
                    .attr("data-trip-id")
            );
            form = create_response_form(trip_id);
            $(this).parent().append(form);
            $(this).remove();
        });
    }).on("mouseleave", function() {
        $(this)
            .find("a.reply")
            .remove();
    });
});

let create_response_form = function(trip_id) {
    let form = $("<form>")
        .attr("method", "post")
        .attr("action", "/new_trip")
        .addClass("reply-form");
    let hidden = $("<input>")
        .attr("type", "hidden")
        .attr("name", "response_to")
        .attr("value", trip_id);
    let textarea = $("<textarea>")
        .attr("name", "text")
        .attr("rows", 4)
        .attr("cols", 50)
        .attr("placeholder", "Reply...");
    let submit = $("<button>")
        .attr("type", "submit")
        .text("Publish");
    form.append(hidden)
        .append(textarea)
        .append(submit);
    textarea.on("click", function(e) {
        //e.stopPropagation();
        e.preventDefault();
    });
    return form;
}