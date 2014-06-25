$(function() {
    // Lifted directly from Django docs
    // using jQuery
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');

    function addSpeaker(speaker) {
        var $speakers = $('#id_event-speakers');
        var currentSpeakers = $speakers.val();
        $speakers.val(currentSpeakers + " " + speaker.id);
    }

    $speakerForm = $('.js-speaker-form');
    $speakerForm.on('submit', function(ev) {
        $.ajax({
            type: 'POST',
            url: '/events/speakers/new',
            data: JSON.stringify({
                name: $speakerForm.find('#id_name').val(),
            }),
            headers: {
                "X-CSRFToken": csrftoken,
            },
            contentType: "application/json; charset=utf-8",
            dataType: 'json',
            success: function(response) {
                addSpeaker(response);
                $('.js-speaker-form-errors').addClass('hidden');
            },
            error: function(err) {
                $('.js-speaker-form-errors').html("Error creating speaker, please try again.").removeClass('hidden');
            },
        });
        ev.preventDefault();
    });
});
