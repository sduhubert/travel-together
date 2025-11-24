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

//referenced ChatGPT to build a double ended slider for age range, as seen below
const minRange = document.getElementById("minRange");
const maxRange = document.getElementById("maxRange");
const minValue = document.getElementById("minValue");
const maxValue = document.getElementById("maxValue");

function update() {
    if (parseInt(minRange.value) > parseInt(maxRange.value)) {
        //this makes it so that values swap if the user crosses sliders
        const temp = minRange.value;
        minRange.value = maxRange.value;
        maxRange.value = temp;
    }

    minValue.textContent = minRange.value;
    maxValue.textContent = maxRange.value;
}

minRange.oninput = update;
maxRange.oninput = update;
update();