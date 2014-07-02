$(function() {
    var locationBH = new Bloodhound({
        datumTokenizer: Bloodhound.tokenizers.obj.whitespace('name'),
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        remote: {
            url: document.locationConfig.suggestURL+"q=%QUERY",
            filter: function(response) {
                return response._embedded.pois;
            }
        }
    });
    locationBH.initialize();

    $typeaheadEl = $('.js-location-typeahead');
    $typeaheadEl.typeahead({
        hint: true,
        highlight: true,
        minLength: 1
    },
    {
        name: 'location',
        displayKey: 'name',
        source: locationBH.ttAdapter(),
        templates: {
            suggestion: _.template('<p><%= name %></p>'),
        },
    });
    var suggestedName = '';
    $typeaheadEl.on('typeahead:selected typeahead:autocompleted', function(ev, suggestion) {
        suggestedName = suggestion.name;
        $('.js-location').val(suggestion.id);
    });
    $typeaheadFormGroup = $typeaheadEl.parentsUntil('.form-group');
    $typeaheadEl.on('change', function(ev) {
        if (ev.target.value===suggestedName) {
            $typeaheadFormGroup.removeClass('has-error');
            $typeaheadFormGroup.addClass('has-success');
        } else if (ev.target.value==="") {
            $typeaheadFormGroup.removeClass('has-success');
            $typeaheadFormGroup.removeClass('has-error');
        } else {
            $typeaheadFormGroup.removeClass('has-success');
            $typeaheadFormGroup.addClass('has-error');
        }
    });

});
