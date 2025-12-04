$(function() {
    const $fileInput = $('#profile_pic');
    const $label = $('.profile-pic-button');
    const $fileText = $label.find('.file-text');
    const $fileClear = $label.find('.file-clear');

    $fileInput.on('change', function() {
        if (this.files.length > 0) {
            $fileText.text(this.files[0].name);
            $fileClear.show();
        } else {
            $fileText.text('Choose a file');
            $fileClear.hide();
        }
    });

    $fileClear.on('click', function(e) {
        e.stopPropagation();
        e.preventDefault();
        $fileInput.val('');
        $fileText.text('Choose a file');
        $fileClear.hide();
    });
});

// Preview selected profile picture
$(document).ready(function() {
    const originalSrc = $('#pfp-preview').attr('src'); // store original image

    $('#profile-pic').on('change', function() {
        const file = this.files[0];
        if (file) {
            // Update preview to selected file
            $('#pfp-preview').attr('src', URL.createObjectURL(file));
        } else {
            // No file selected, reset preview
            $('#pfp-preview').attr('src', originalSrc);
        }
    });
});