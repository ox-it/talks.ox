$(function() {
    var speakersBH = new Bloodhound({
        datumTokenizer: Bloodhound.tokenizers.obj.whitespace('name'),
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        remote: {
            url: '/events/speakers/suggest?q=%QUERY',
            filter: function(response) {
                return response.speakers;
            },
        }
    });
    speakersBH.initialize();

    var speakerTemplate = _.template('<a href="#" data-id="<%= id %>" class="js-speaker-suggestion list-group-item"><span class="badge">+</span><%= name %></a>');
    var $suggestedSpeakers = $('.js-suggested-speakers-list');
    var cachedSuggestions = {};
    $('.js-speakers-typeahead').on('keyup', function(ev) {
        var query = ev.target.value;
        speakersBH.get(query, function(suggestions) {
            $suggestedSpeakers.html('');
            _.each(suggestions, function(suggestion) {
                cachedSuggestions[suggestion.id] = suggestion;
                $suggestedSpeakers.append(speakerTemplate(suggestion));
            });
        });
    });
    $suggestedSpeakers.on('click', '.js-speaker-suggestion', function(ev) {
        ev.preventDefault();
        var $suggestion = $(ev.target);
        $suggestion.addClass('disabled');
        var speakerID = $suggestion.data('id');
        var speaker = cachedSuggestions[speakerID];
        document.addSpeaker(speaker);
    });
    document.listenForRemoval(function(id) {
        $suggestedSpeakers.find("[data-id='"+id+"']").removeClass('disabled');
    });
});
