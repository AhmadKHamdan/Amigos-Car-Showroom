$(document).ready(function () {
    $("#options").select2({
        placeholder: "Select options",
        allowClear: true,
    });

    $(document).on('click', '.btn-close', function() {
        $(this).parent('.addNewCar-alert').fadeOut();
    });
});