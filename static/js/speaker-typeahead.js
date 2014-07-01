$(function() {

    function Suggester(queryUrl, targetSuggestion, typeaheadBox, callbackTypeahead, cachedSuggestions) {
        var bh = new Bloodhound({
            datumTokenizer: Bloodhound.tokenizers.obj.whitespace('name'),
            queryTokenizer: Bloodhound.tokenizers.whitespace,
            remote: {
                url: queryUrl
            }
        });
        bh.initialize();

        typeaheadBox.on('keyup', function(ev) {
            bh.get(ev.target.value, callbackTypeahead);
        });

        function addElement(el) {
            var $suggestion = $(el);
            $suggestion.addClass('hidden');
            var speakerID = $suggestion.data('id');
            var speaker = cachedSuggestions[speakerID];
            document.addSpeaker(speaker);
        }
        targetSuggestion.on('click', '.js-speaker-suggestion', function(ev) {
            ev.preventDefault();
            addElement(ev.target);
        });
        targetSuggestion.on('click', '.js-speaker-suggestion span', function(ev) {
            ev.preventDefault();
            ev.stopPropagation();
            addElement(ev.target.parentNode);
        });
        document.listenForRemoval(function(id) {
            targetSuggestion.find("[data-id='"+id+"']").removeClass('hidden');
        });
    }

    var speakerQueryUrl = document.speakerConfig.suggestURL+"?q=%QUERY";
    var speakerTemplate = _.template('<a href="#" data-id="<%= id %>" class="js-speaker-suggestion list-group-item"><span class="badge">+</span><%= name %> - <%= email_address %></a>');
    var suggestedSpeakers = $('.js-suggested-speakers-list');
    var typeaheadSpeakers = $('.js-speakers-typeahead');
    var cachedSpeakers = {};
    var cbSpeakerSuggest = function(suggestions) {
        suggestedSpeakers.html('');
        _.each(suggestions, function(suggestion) {
            cachedSpeakers[suggestion.id] = suggestion;
            suggestedSpeakers.append(speakerTemplate(suggestion));
        });
    };

    new Suggester(speakerQueryUrl, suggestedSpeakers, typeaheadSpeakers, cbSpeakerSuggest, cachedSpeakers);

    var topicQueryUrl = "http://talks-dev.oucs.ox.ac.uk/topics/suggest?q=%QUERY";
    var topicTemplate = _.template('<a href="#" data-id="<%= uri %>" class="js-speaker-suggestion list-group-item"><span class="badge">+</span><%= prefLabel %></a>');
    var suggestedTopics = $('.js-suggested-topics-list');
    var typeaheadTopics = $('.js-topics-typeahead');
    var cachedTopics = {};
    var cbTopicSuggest = function(suggestions) {
        suggestedSpeakers.html('');
        _.each(suggestions[1].concepts, function(suggestion) {
            cachedTopics[suggestion.uri] = suggestion;
            suggestedSpeakers.append(topicTemplate(suggestion));
        });
    };

    new Suggester(topicQueryUrl, suggestedTopics, typeaheadTopics, cbTopicSuggest, cachedTopics);
});
