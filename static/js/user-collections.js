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


    // Add or remove a talk/series to/from a collection
    $('.js-toggle-collection-item').click( function(ev) {
        var data = dataFromEl(ev.target);
        var action = $(ev.target).data('action');
        var action_url = document.collectionConfig.saveItemDefault;
        if (action == 'remove') {
            action_url = document.collectionConfig.removeItemDefault;
        }
        $.ajax({
            type: 'POST',
            url: action_url,
            data: JSON.stringify(data),
            headers: {
                "X-CSRFToken": csrftoken,
            },
            contentType: "application/json; charset=utf-8",
            dataType: 'json',
            success: function(response) {
                if (action == 'remove') {
                    $(ev.target).children('.first').addClass('fade-check');
                    $(ev.target).children('.second').removeClass('fa-times');
                    $(ev.target).removeClass('active');
                    $(ev.target).data('action', 'add');

                } else {
                    //$(ev.target).children('i').addClass('fa-check');
                    $(ev.target).children('.first').removeClass('fade-check');
                    $(ev.target).children('.second').addClass('fa-times');
                    $(ev.target).addClass('active');
                    $(ev.target).data('action', 'remove');
                }
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
