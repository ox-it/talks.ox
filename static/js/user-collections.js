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
                switch (response.item.class_name) {
                    case 'Event':
                        $('.js-your-talks').append(
                            document.collectionConfig.yourTalkTemplate({event: response.item})
                        );
                        break;
                    case 'EventGroup':
                        $('.js-your-groups').append(
                            document.collectionConfig.yourGroupTemplate({group: response.item})
                        );
                        break;
                }
            },
            error: function(err) {
                console.log(err);
            },
        });
    });
    $('.js-your-collection').on('click', '.js-remove-from-collection', function(ev) {
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
                switch (response.class_name) {
                    case 'Event':
                        $('.js-upcoming-events [data-event="'+response.id+'"].hidden').removeClass('hidden');
                        break;
                    case 'EventGroup':
                        $('.js-upcoming-events [data-group="'+response.id+'"].hidden').removeClass('hidden');
                        break;
                }
            },
            error: function(err) {
                console.log(err);
            },
        });
    });
});
