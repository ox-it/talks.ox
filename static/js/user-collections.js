$(function() {
    var csrftoken = $.cookie('csrftoken');
    $('.js-add-to-collection').on('click', function(ev) {
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
                console.log(response);
            },
            error: function(err) {
                console.log(err);
            },
        });
    });
});
