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

    $('.js-speakers-typeahead').typeahead(null, {
        name: 'speakers',
        displayKey: 'name',
        source: speakersBH.ttAdapter()
    });
});
