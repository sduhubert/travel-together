// const e = require("express"); // REMOVED - require() doesn't work in browser and this wasn't used anyway

$(document).ready(function () {
    $('.original').on("mouseenter", function () {
        let link = $("<a>")
            .attr("href", "#")
            .addClass("reply")
            .text("Reply to this trip");
        $(this).append(link);
        link.on("click", function () {
            trip_id = parseInt(
                $(this)
                    .parent()
                    .attr("data-trip-id")
            );
            form = create_response_form(trip_id);
            $(this).parent().append(form);
            $(this).remove();
        });
    }).on("mouseleave", function () {
        $(this)
            .find("a.reply")
            .remove();
    });
});

let create_response_form = function (trip_id) {
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
    textarea.on("click", function (e) {
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

// Only run if elements exist on the page
if (minRange && maxRange && minValue && maxValue) {
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
}

// Ensures that all mandatory fields are filled out in form
// Also ensures that creator's age is within age range, and that max_members and budget are non-negative integers
$(document).ready(function () {
    $('#new-trip-form').on('submit', function (event) {
        let userAge = parseInt($('#new-trip-form').data('user-age'));
        let title = $('#title').val().trim();
        let description = $('#description').val().trim();
        let destination = $('textarea[name="destination"]').val().trim();
        let start = $('#start').val();
        let end = $('#end').val();
        let budget = parseInt($('#budget').val());
        let maxMembers = parseInt($('#max_members').val());
        let minAge = parseInt($('#minRange').val());
        let maxAge = parseInt($('#maxRange').val());


        // 1. Required fields
        if (!title || !description || !destination || !start || !end) {
            alert("Please fill in all mandatory fields.");
            event.preventDefault();
            return;
        }

        // 2. Start date in future
        let today = new Date();
        let startDate = new Date(start);
        let endDate = new Date(end);
        if (startDate <= today) {
            alert("Start date must be in the future.");
            event.preventDefault();
            return;
        }

        // 3. End date after start
        if (endDate <= startDate) {
            alert("End date must be after the start date.");
            event.preventDefault();
            return;
        }

        // 4. Budget positive if supplied
        if (!isNaN(budget) && budget < 0) {
            alert("Budget must be a positive number.");
            event.preventDefault();
            return;
        }

        // 5. Max members positive if supplied
        if (!isNaN(maxMembers) && maxMembers < 1) {
            alert("Maximum trip members must be greater than 0.");
            event.preventDefault();
            return;
        }

        // 6. Age range makes sense
        if (minAge > maxAge) {
            alert("Minimum age cannot be greater than maximum age.");
            event.preventDefault();
            return;
        }

        // 7. Creator age in range
        if (userAge < minAge || userAge > maxAge) {
            alert("Your age does not fall within the selected age range.");
            event.preventDefault();
            return;
        }
    });

});

$(document).ready(function() {
    // Check if we need to apply joinable filter on page load
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('show_joinable') === 'true') {
        filterJoinableTrips();
    }
});

//referenced Claude to figure out how properly show ALL joinable trips after a filter was previously applied
$(document).on("click", "#show-joinable-trips", function(e) {
    e.preventDefault();
    
    // Reload page with joinable flag
    const baseUrl = window.SHOW_ALL_TRIPS_URL.split('#')[0].split('?')[0];
    window.location.href = baseUrl + '?show_joinable=true#trip-list';
});

$(document).on("click", "#show-all-trips", function(e){
    e.preventDefault();
    //reload page to remove any filters applied, and have it scroll down to trip-list automatically
    window.location.href = window.SHOW_ALL_TRIPS_URL;

    $(".trip-link").show();

    // Clear other filters
    $("#max-budget-filter, #start-date-filter, #end-date-filter, #min-age-filter, #max-age-filter, #origin-filter, #destination-filter").val('');

});

function filterJoinableTrips() {
    const userAge = parseInt(window.USER_AGE);
    
    $(".trip-link").each(function() {
        const tripItem = $(this).find(".trip-item");

        const minAge = parseInt(tripItem.data("min-age")) || 0;
        const maxAge = parseInt(tripItem.data("max-age")) || 999999;
        const currentParticipants = parseInt(tripItem.data("current-participants")) || 0;
        const maxTravelers = parseInt(tripItem.data("max-travelers")) || 999999;
        const status = parseInt(tripItem.data("status")) || 0;

        const member = tripItem.attr("data-is-member") === "true";

        const inAgeRange = userAge >= minAge && userAge <= maxAge;
        const full = currentParticipants >= maxTravelers;
        const open = status === 0;

        $(this).toggle(!member && inAgeRange && !full && open);
    });
}



