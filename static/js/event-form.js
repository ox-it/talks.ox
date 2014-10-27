var animationTime = 200; // ms

$(function() {
    // Register event to show event group forms
    $('#id_event-group-enabled').on('change', function(ev) {
        if (ev.target.checked) {
            $('#id_group').prop('disabled', false)
            $('.event-group').slideDown(animationTime);
        } else {
            $('.event-group').slideUp(animationTime);
            $('#id_group').prop('disabled', true)
        }
    });

    // Initialise datetimepicker's
    $('.js-datetimepicker').datetimepicker({
        format: 'dd/mm/yyyy hh:ii',
        autoclose: true,
    });

    // Set the default end-date to the start date when it is picked
    var startDateTimePicker = $('.js-datetimepicker.event-start');
    startDateTimePicker.datetimepicker().on('changeDate', function(ev){
        utcDate = startDateTimePicker.datetimepicker('getUTCDate');
        // Set the StartDate to the current DAY -- don't specify hours
        //
        // Seems like the hours on start dates can cause some TZ issues
        $('.js-datetimepicker.event-end').datetimepicker('setStartDate',
            new Date(utcDate.getFullYear(), utcDate.getMonth(), utcDate.getDate())
        );
    });

    $('.js-open-calendar').on('click', function(ev) {
        $(ev.target).parent().siblings('.js-datetimepicker').datetimepicker('show');
    });

});
