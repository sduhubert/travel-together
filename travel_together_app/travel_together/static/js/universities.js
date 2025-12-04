$(function () {
    const universities = JSON.parse(
        document.getElementById("universities-json").textContent
    );

    const homeUniSelect = $('#home_uni');
    const homeUniCountrySelect = $('#home_uni_country');
    const visitingUniSelect = $('#visiting_uni');
    const visitingUniCountrySelect = $('#visiting_uni_country');

    function populateUniversities(selectElem, countryCode) {
        selectElem.html('<option value="" disabled selected>University</option>');

        const filtered = universities.filter(uni => uni.country === countryCode);

        filtered.forEach(uni => {
            selectElem.append(
                $('<option>', {
                    value: uni.university,
                    text: uni.university
                })
            );
        });

        selectElem.prop('disabled', filtered.length === 0);
    }

    homeUniCountrySelect.on('change', function () {
        populateUniversities(homeUniSelect, $(this).val());
    });

    visitingUniCountrySelect.on('change', function () {
        populateUniversities(visitingUniSelect, $(this).val());
    });

    if (homeUniCountrySelect.val()) {
        populateUniversities(homeUniSelect, homeUniCountrySelect.val());
    }

    if (visitingUniCountrySelect.val()) {
        populateUniversities(visitingUniSelect, visitingUniCountrySelect.val());
    }
});
