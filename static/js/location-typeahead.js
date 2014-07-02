$(function() {


    function TypeaheadListener() {
        this.listen = function(typeaheadEl, targetEl, formGroupEl) {
            var $targetEl = $(targetEl);
            var $typeaheadEl = $(typeaheadEl);
            var $typeaheadFormGroup = $(formGroupEl);
            var suggestedName = '';
            $typeaheadEl.on('typeahead:selected typeahead:autocompleted', function(ev, suggestion) {
                suggestedName = suggestion.name;
                $targetEl.val(suggestion.id);
            });
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
        };
    }
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
    $locationTypeahead = $('.js-location-typeahead');
    $locationTypeahead.typeahead({
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
    var locationListener = new TypeaheadListener();
    locationListener.listen($locationTypeahead, $('.js-location'), $locationTypeahead.parent().parent().parent());

    var organisationBH = new Bloodhound({
        datumTokenizer: Bloodhound.tokenizers.obj.whitespace('name'),
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        remote: {
            url: document.organisationConfig.suggestURL+"q=%QUERY",
            filter: function(response) {
                return response._embedded.pois;
            }
        }
    });
    organisationBH.initialize();
    $organisationTypeahead = $('.js-organisation-typeahead');
    $organisationTypeahead.typeahead({
        hint: true,
        highlight: true,
        minLength: 1
    },
    {
        name: 'location',
        displayKey: 'name',
        source: organisationBH.ttAdapter(),
        templates: {
            suggestion: _.template('<p><%= name %></p>'),
        },
    });
    var organisationListener = new TypeaheadListener();
    organisationListener.listen($organisationTypeahead, $('.js-organisation'), $organisationTypeahead.parent().parent().parent());
});
