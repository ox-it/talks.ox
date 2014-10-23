var animationTime = 200; // ms

$(function() {
    // Register event to show event group forms
    $('#id_event-group-enabled').on('change', function(ev) {
        if (ev.target.checked) {
            $('.event-group').slideDown(animationTime);
        } else {
            $('.event-group').slideUp(animationTime);
        }
    });

    // Register event to show create event group form
    $('.event-group input:radio').on('change', function(ev) {
        var $target = $(ev.target);
        if (ev.target.value==="CRE") {
            $('.event-group-create .panel-body').slideDown(animationTime);
            $('.event-group-create .form-control').prop("disabled", false);
            $('.event-group-select .form-control').prop("disabled", true);
        } else {
            $('.event-group-create .form-control').prop("disabled", true);
            $('.event-group-select .form-control').prop("disabled", false);
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
