$(function() {
    function dataFromEl(el) {
        var data = {};
        var eventID = $(el).data('event');
        var groupID = $(el).data('group');
        var collectionID = $(el).data('collection');
        if (eventID) { data.event = eventID; }
        if (groupID) { data.group = groupID; }
        if (collectionID) { data.collection = collectionID; }
        return data;
    }
    var csrftoken = $.cookie('csrftoken');
    $('.js-add-to-collection').click( function(ev) {
        var data = dataFromEl(ev.target);
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
                $(ev.target).addClass('hidden');
                $(ev.target).siblings('.js-remove-from-collection').removeClass('hidden');
            },
            error: function(err) {
                console.log(err);
                $('#collection-alert-container').html('<div class="alert alert-warning alert-dismissible" role="alert">' +
                    'Error: ' + err.statusText +
                    '<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span>' +
                    '</button></div>');
            },
        });
        $(ev.stopPropagation());  // Stop the bootstrap dropdown list from auto-closing
    });

    $('.js-remove-from-collection').click( function(ev) {
        var data = dataFromEl(ev.target);
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
                $(ev.target).addClass('hidden');
                $(ev.target).siblings('.js-add-to-collection').removeClass('hidden');
            },
            error: function(err) {
                console.log(err);
                $('#collection-alert-container').html('<div class="alert alert-warning alert-dismissible" role="alert">' +
                        'Error: ' + err.statusText +
                    '<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span>' +
                    '</button></div>');
            },
        });
        $(ev.stopPropagation());  // Stop the bootstrap dropdown list from auto-closing
    });

    // Subscribe to collection (as a reader)
    $('.js-add-collection').click( function(ev) {
        var data = dataFromEl(ev.target);
        $.ajax({
            type: 'POST',
            url: document.collectionConfig.addListDefault,
            data: JSON.stringify(data),
            headers: {
                "X-CSRFToken": csrftoken,
            },
            contentType: "application/json; charset=utf-8",
            dataType: 'json',
            success: function(response) {
                // Hide the <a>
                $(ev.target).addClass('hidden');
                $(ev.target).siblings('.js-remove-collection').removeClass('hidden');
            },
            error: function(err) {
                console.log(err);
                $('#collection-alert-container').html('<div class="alert alert-warning alert-dismissible" role="alert">' +
                    '"Error: ' + err.statusText +
                    '<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span>' +
                    '</button></div>');
            },
        });
    });

    // Unsubscribe from collection (as a reader)
    $('.js-remove-collection').click( function(ev) {
        var data = dataFromEl(ev.target);
        $.ajax({
            type: 'POST',
            url: document.collectionConfig.removeListDefault,
            data: JSON.stringify(data),
            headers: {
                "X-CSRFToken": csrftoken,
            },
            contentType: "application/json; charset=utf-8",
            dataType: 'json',
            success: function(response) {
                // Hide the <a>
                $(ev.target).addClass('hidden');
                $(ev.target).siblings('.js-add-collection').removeClass('hidden');
            },
            error: function(err) {
                console.log(err);
                $('#collection-alert-container').html('<div class="alert alert-warning alert-dismissible" role="alert">' +
                    'Error: ' + err.statusText +
                    '<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span>' +
                    '</button></div>');
            },
        });
    });

});
