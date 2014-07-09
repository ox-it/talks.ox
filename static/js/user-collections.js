$(function() {
    var csrftoken = $.cookie('csrftoken');
    $('.js-upcoming-events').on('click', '.js-add-to-collection', function(ev) {
        var eventID = $(ev.target.parentNode).data('event');
        $.ajax({
            type: 'POST',
            url: document.collectionConfig.saveDefault,
            data: JSON.stringify({
                event: eventID,
            }),
            headers: {
                "X-CSRFToken": csrftoken,
            },
            contentType: "application/json; charset=utf-8",
            dataType: 'json',
            success: function(response) {
                // Hide the <a>
                $(ev.target.parentNode).addClass('hidden');
                $('.js-your-events').append(
                    document.collectionConfig.yourTalkTemplate({event: response.item})
                );
            },
            error: function(err) {
                console.log(err);
            },
        });
    });
    $('.js-your-events').on('click', '.js-remove-from-collection', function(ev) {
        var eventID = $(ev.target.parentNode).data('event');
        $.ajax({
            type: 'POST',
            url: document.collectionConfig.removeDefault,
            data: JSON.stringify({
                event: eventID,
            }),
            headers: {
                "X-CSRFToken": csrftoken,
            },
            contentType: "application/json; charset=utf-8",
            dataType: 'json',
            success: function(response) {
                // Remove the <li>
                $(ev.target.parentNode.parentNode).remove();
                if (response.happening_today) {
                    $('.js-upcoming-events [data-event="'+response.id+'"].hidden').removeClass('hidden');
                }
            },
            error: function(err) {
                console.log(err);
            },
        });
    });
});
