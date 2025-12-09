$(document).ready(function () {

    const steps = $(".form-step");
    let currentStep = 0;
    showStep(currentStep);

    function showStep(i) {
        steps.removeClass("active-step").hide();
        $(steps[i]).addClass("active-step").show();
    }


    // Next/Prev button logic
    $(document).on("click", "#nextStep", function () {
        if (currentStep < steps.length - 1) {
            currentStep++;
            showStep(currentStep);
        }
    });
    $(document).on("click", "#prevStep", function () {
        if (currentStep > 0) {
            currentStep--;
            showStep(currentStep);
        }
    });

    // Open popup
    $("#openFormPopup").click(function () {
        $("#formPopupOverlay").show();
        $("#formPopupModal").show();
    });

    // Close popup
    $("#closeFormPopup", "#formPopupModal").click(function () {
        $("#formPopupOverlay").hide();
        $("#formPopupModal").hide();
    });


    // Add new destination field
    $('#add-destination').click(function () {
        const count = $('.destination').length;
        console.log("Add destination clicked");
        if (count >= 5) {
            alert('You can only add up to 5 destinations.');
            return;
        }

        $('#destination-container').append(`
            <div class="destination-entry">
                <input type="text" class="destination additional-destination" name="destination" placeholder="Destination">
                <button type="button" class="remove-destination">✕</button>
            </div>
        `);
    });

    // Remove a destination field
    $(document).on('click', '.remove-destination', function () {
        $(this).closest('.destination-entry').remove();
    });

    // Merge all destinations into string - referenced ChatGPT for help
    $('#trip-form').submit(function () {
        const dests = $('.single-destination').map(function () {
            return $(this).val().trim();
        }).get().filter(v => v.length > 0);

        $('#destination').val(dests.join(','));
    });


    let step = 1;
    const range = document.querySelector(".double-range .range-fill");
    const range_input = document.querySelectorAll(".double-range .range-input input");
    const text_input = document.querySelectorAll(".double-range .text-input input");

    dRange(range, range_input, text_input, step);

    //to avoid minimum age and maximum age from crossing over on the slider
    function preventSliderCrossing() {
        const sliderMin = document.querySelector(".range-input .min");
        const sliderMax = document.querySelector(".range-input .max");
        const minAge = document.getElementById("min-age");
        const maxAge = document.getElementById("max-age");

        function sliderUpdate() {
            let min = parseInt(sliderMin.value);
            let max = parseInt(sliderMax.value);

            if (min > max) {
                min = max;
                sliderMin.value = min;
            }

            minAge.value = min;
            maxAge.value = max;
        }

        function numUpdate() {
            let min = parseInt(minAge.value);
            let max = parseInt(maxAge.value);

            if (min > max) {
                min = max;
                minAge.value = min;
            }

            sliderMin.value = min;
            sliderMax.value = max;
        }

        sliderMin.addEventListener("input", sliderUpdate);
        sliderMax.addEventListener("input", sliderUpdate);
        minAge.addEventListener("input", numUpdate);
        maxAge.addEventListener("input", numUpdate);

    }

    preventSliderCrossing();

    const controls = [
        { checkbox: "#budgetToggle", inputs: ["#budget"] },
        { checkbox: "#maxMembersToggle", inputs: ["#max_members"] },
        {
            checkbox: "#ageToJoinToggle",
            inputs: [
                "#min-age",
                "#max-age",
                ".range-input .min",
                ".range-input .max"
            ]
        }
    ];

    controls.forEach(control => {
        const $checkbox = $(control.checkbox);
        const $inputs = control.inputs.map(selector => $(selector));

        const toggleInputs = () => {
            $inputs.forEach($input => {
                $input.prop("disabled", !$checkbox.is(":checked"));
                $input.toggleClass("disabled", !$checkbox.is(":checked"));
            });
        };

        toggleInputs();
        $checkbox.on("change", toggleInputs);
    });


    // Additional form validation
    $("#submit-button").click(function (e) {
        let missingFields = [];
        invalidInput = false;

        if ($("#title").val().trim() === "") missingFields.push("Trip Title");
        if ($("#description").val().trim() === "") missingFields.push("Trip Description");

        if ($(".destination").val().trim() === "") missingFields.push("Destination(s)")
        if ($("#start").val() === "") missingFields.push("Start Date");
        if ($("#end").val() === "") missingFields.push("End Date");

        // Check checked optional fields as well
        if ($("#budgetToggle").is(":checked") && $("#budget").val().trim() === "") {
            missingFields.push("Budget");
        }
        if ($("#maxMembersToggle").is(":checked") && $("#max_members").val().trim() === "") {
            missingFields.push("Maximum Trip Members");
        }
        if ($("#ageToJoinToggle").is(":checked")) {
            if ($("#min-age").val().trim() === "" || $("#max-age").val().trim() === "") {
                missingFields.push("Age to Join range");
            }
        }

        if ($("#budgetToggle").is(":checked") && parseFloat($("#budget").val()) < 0) {
            invalidInput = true;
        }
        if ($("#maxMembersToggle").is(":checked") && parseInt($("#max_members").val()) <= 0) {
            invalidInput = true;
        }

        if ($("#ageToJoinToggle").is(":checked")) {
            const minAge = parseInt($("#min-age").val());
            const maxAge = parseInt($("#max-age").val());
            if (minAge > maxAge) {
                invalidInput = true;
            }
        }

        const startDate = new Date($("#start").val());
        const endDate = new Date($("#end").val());
        const today = new Date();
        today.setHours(0, 0, 0, 0); //to handle time zone fix

        if (startDate < today || endDate < today || endDate < startDate) {
            invalidInput = true;
        }

        if (invalidInput || missingFields.length > 0) {
            e.preventDefault();
            alert("One or more of your inputs is invalid. Please correct them before resubmitting.")
        }
    });

    //makes sure trips are in the future and end date is after start date
    const todayDate = new Date().toISOString().split("T")[0];
    $("#start").attr("min", todayDate);
    $("#end").attr("min", todayDate);

    $("#start").on("change", function () {
        $("#end").attr("min", $(this).val());
    });
});
