$(function () {
    const universities = JSON.parse(
        document.getElementById("universities-json").textContent
    );

    const homeUniSelect = $('#home_uni');
    const homeUniCountrySelect = $('#home_uni_country');

    function populateUniversities(countryCode) {
        homeUniSelect.html('<option value="" disabled selected>Home University</option>');

        const filtered = universities.filter(uni => uni.country === countryCode);

        filtered.forEach(uni => {
            homeUniSelect.append(
                $('<option>', {
                    value: uni.university,
                    text: uni.university
                })
            );
        });

        homeUniSelect.prop('disabled', filtered.length === 0);
    }

    homeUniCountrySelect.on('change', function () {
        populateUniversities($(this).val());
    });

    if (homeUniCountrySelect.val()) {
        populateUniversities(homeUniCountrySelect.val());
    }
});
