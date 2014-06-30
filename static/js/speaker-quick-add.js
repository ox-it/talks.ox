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

    // Give a default radix of 10
    function toInt(i) { return parseInt(i, 10); }

    // Add speaker and update the UI
    var speakerTemplate = _.template('<a href="#" data-id="<%= id %>" class="list-group-item list-group-item-info fade in"><span class="badge">-</span><%= name %> - <%= email %></a>');
    var separator = ', ';
    var $speakers = $('#id_event-speakers');
    var $speakersList = $('.js-speakers-list');
    function addSpeaker(speaker) {
        var speakerIDs = $speakers.val();
        speakerIDs = speakerIDs!=='' ? _.map(speakerIDs.split(separator), toInt) : [];
        if (!_.contains(speakerIDs, speaker.id)) {
            speakerIDs.push(speaker.id);
            $speakers.val(speakerIDs.join(separator));
            $speakersList.append(speakerTemplate(speaker));
            return true;
        } else {
            return false;
        }
    }
    // Export this as it's used by speaker-typeahead.js
    document.addSpeaker = addSpeaker;

    var removalCallbacks = [];
    function listenForRemoval(fn) {
        removalCallbacks.push(fn);
    }
    // Export this as it's used by speaker-typeahead.js
    document.listenForRemoval = listenForRemoval;

    // Remove speaker and update the UI
    function removeSpeaker(id) {
        var speakerIDs = $speakers.val();
        speakerIDs = speakerIDs!=='' ? _.map(speakerIDs.split(separator), toInt) : [];
        speakerIDs = _.without(speakerIDs, id);
        $speakers.val(speakerIDs.join(separator));
        _.each(removalCallbacks, function(cb) {
            cb.apply(this, [id]);
        });
    }

    $speakersList.on('click', 'a', function(ev) {
        ev.preventDefault();
        $speaker = $(ev.target);
        removeSpeaker($speaker.data('id'));
        $speaker.remove();
    });

    $('.js-create-speaker').on('click', function(ev) {
        ev.preventDefault();
        $('.js-speaker-panel').removeClass('hidden');
    });

    $speakerForm = $('.js-speaker-form');
    $speakerSubmit = $('.js-submit-speaker');
    $speakerSubmit.on('click', function(ev) {
        $.ajax({
            type: 'POST',
            url: '/events/speakers/new',
            data: JSON.stringify({
                name: $speakerForm.find('#id_name').val(),
                email_address: $speakerForm.find('#id_email_address').val(),
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
