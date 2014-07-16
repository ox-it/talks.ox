$(function() {
    function dataFromEl(el) {
        var data = {};
        var eventID = $(el).data('event');
        var groupID = $(el).data('group');
        if (eventID) { data.event = eventID; }
        if (groupID) { data.group = groupID; }
        return data;
    }
    var csrftoken = $.cookie('csrftoken');
    $('.js-upcoming-events').on('click', '.js-add-to-collection', function(ev) {
        var data = dataFromEl(ev.target.parentNode);
        $.ajax({
            type: 'POST',
            url: document.collectionConfig.saveItemDefault,
            data: JSON.stringify(data),
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
    $('.js-your-talks').on('click', '.js-remove-from-collection', function(ev) {
        var data = dataFromEl(ev.target.parentNode);
        $.ajax({
            type: 'POST',
            url: document.collectionConfig.removeItemDefault,
            data: JSON.stringify(data),
            headers: {
                "X-CSRFToken": csrftoken,
            },
            contentType: "application/json; charset=utf-8",
            dataType: 'json',
            success: function(response) {
                // Remove the <li>
                $(ev.target.parentNode.parentNode).remove();
                if (response.id) {
                    $('.js-upcoming-events [data-event="'+response.id+'"].hidden').removeClass('hidden');
                    $('.js-upcoming-events [data-group="'+response.id+'"].hidden').removeClass('hidden');
                }
            },
            error: function(err) {
                console.log(err);
            },
        });
    });
});
