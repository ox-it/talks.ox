$(function() {

    function Suggester(queryUrl, targetSuggestion, typeaheadBox, callbackTypeahead, cachedSuggestions, documentAdd) {
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
            var elementID = $suggestion.data('id');
            var element = cachedSuggestions[elementID];
            documentAdd(element);
        }
        targetSuggestion.on('click', '.js-suggestion', function(ev) {
            ev.preventDefault();
            addElement(ev.target);
        });
        targetSuggestion.on('click', '.js-suggestion span', function(ev) {
            ev.preventDefault();
            ev.stopPropagation();
            addElement(ev.target.parentNode);
        });
        document.listenForRemoval(function(id) {
            targetSuggestion.find("[data-id='"+id+"']").removeClass('hidden');
        });
    }

    var speakerQueryUrl = document.speakerConfig.suggestURL+"?q=%QUERY";
    var speakerTemplate = _.template('<a href="#" data-id="<%= id %>" class="js-suggestion list-group-item"><span class="badge">+</span><%= name %> - <%= email_address %></a>');
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

    new Suggester(speakerQueryUrl, suggestedSpeakers, typeaheadSpeakers, cbSpeakerSuggest, cachedSpeakers, document.addSpeaker);

    var topicQueryUrl = document.topicConfig.suggestURL + "/suggest?count=10&q=%QUERY";
    var topicTemplate = _.template('<a href="#" data-id="<%= uri %>" class="js-suggestion list-group-item"><span class="badge">+</span><%= prefLabel %></a>');
    var suggestedTopics = $('.js-suggested-topics-list');
    var typeaheadTopics = $('.js-topics-typeahead');
    var cachedTopics = {};
    var cbTopicSuggest = function(suggestions) {
        suggestedTopics.html('');
        _.each(suggestions[1].concepts, function(suggestion) {
            cachedTopics[suggestion.uri] = suggestion;
            suggestedTopics.append(topicTemplate(suggestion));
        });
    };

    new Suggester(topicQueryUrl, suggestedTopics, typeaheadTopics, cbTopicSuggest, cachedTopics, document.addTopic);
});
