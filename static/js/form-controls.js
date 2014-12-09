$(function() {
    function getSuggestionById(mainInput, id, idKey) {
        var bloodhound = $(mainInput).data('bloodhound');
        if (!bloodhound.storage) {
            var name = $(mainInput).attr('name');
            if(bloodhound.prefetch) {
                throw Error("Data not prefetched for field " + name);
            } else {
                throw Error("Prefetch config is missing for field " + name);
            }
        }
        var data = bloodhound.storage.get('data');
        for(var i in data.datums) {
            if(data.datums[i][idKey] == id) {
                return data.datums[i];
            }
        }
    }
    function removeItem(e) {
        e.preventDefault();
        var input = $(this).parents('.list-group-item').prev('input')
        var removed_data_id = input.val();
        var mainInput = input.siblings(".tt-input");
        input.remove();
        $(this).parents('.list-group-item').remove();

        //remove from the local list
        var currentValues = mainInput.data('currentValues');
        var index = currentValues.indexOf(removed_data_id);
        currentValues.splice(index, 1);
        console.log(currentValues);
    }
    function showSelectedValue(mainInput, input, suggestion) {
        var valueKey = $(mainInput).data('valueKey');
        var labelKey = $(mainInput).data('labelKey');
        suggestion = suggestion || $(input).data('suggestion') || getSuggestionById(mainInput, $(input).prop('value'), valueKey);
        var t = _.template('<div data-id="<%= ' + valueKey + ' %>" class="list-group-item list-group-item-info fade in"><a href="#"><span class="glyphicon glyphicon-remove"></span></a><%= ' + labelKey + ' %></div>');
        var item = $(t(suggestion)).insertAfter(input);
        $('a', item).click(removeItem).click(function() { $(mainInput).show().focus().val('') });
        $(mainInput).val('');
        if(!$(mainInput).prop('multiple')) {
            $(mainInput).hide();
        }
        //add the value to the local list
        var currentValues = $(mainInput).data('currentValues');
        var value = String(suggestion[valueKey]);
        currentValues.push(value);
        console.log(currentValues);
    }
    function showSelectedValuesForInput() {
        var $this = $(this);
        var name = $(this).data('name');
        var $inputs = $('input[name="' + name + '"]', $this.parents('form'));
        $inputs.each(function() { 
            showSelectedValue($this, this);
        });
    }
    function onChange(e, suggestion, datasetName) {
        e.preventDefault();
        e.stopPropagation();
        var value = suggestion[$(e.target).data('valueKey')];
        var name = $(e.target).data('name');
        var $input = $('input[name="' + name + '"]', $(e.target).parents('form'));
        $input = makeInput(e.target, name, value);
        showSelectedValue($(e.target), $input, suggestion);
    }
    function onEventGroupChanged(e, department) {
        //update to use the supplied department ID, if it doesn't currently have one set
        existingValues = $(this).siblings('.list-group-item');
        if(existingValues.length==0) {
            e.preventDefault();
            e.stopPropagation();
            var value = department;
            var name = $(e.target).data('name');
            var $input = $('input[name="' + name + '"]', $(e.target).parents('form'));
            $input = makeInput(e.target, name, value.id);
            showSelectedValue($(e.target), $input, department);
        }
    }

    function onAddPerson(e, person) {
        e.preventDefault();
        e.stopPropagation();
        var name = $(e.target).data('name');
        var $input = $('input[name="' + name + '"]', $(e.target).parent('form'));
        $input = makeInput(e.target, name, person.id);
        showSelectedValue($(e.target), $input, person);
    }

    function makeInput(sourceInput, name, value) {
        return $('<input>').
            insertBefore(sourceInput).
            attr('type', 'hidden').
            attr('name', name).
            attr('value', value);
    }

    var filter = function(suggestions, currentValues) {
        //Filter the given suggestions, removing any already in the element's list of chosen values
        var filtered = $.grep(suggestions, function(suggestion) {
            return $.inArray(String(suggestion.id), currentValues) === -1;
        });
        return filtered;
    }


    //Select and initialise all typeaheads in the original document. Note that multiple new '.typeahead' elements are created.
    //Those from the original document lack the tt-hint or tt-input classes, so exclude these from the selection
    var typeaheads = $('.typeahead:not(.tt-hint):not(.tt-input)');
    typeaheads.each(function() {
        $this = $(this);
        options = {
            hint: true,
            highlight: true,
            minLength: 1
        }
        var sourceConfig = $this.data('source') || null;
        if(!sourceConfig) {
            throw Error("Missing data-source attribute");
        }

        //This function may be called again when a modal form opens.
        //Don't re-initialise typeaheads which have already been initialised
        if($this.data('bloodhound') != null) {
            return;
        }

        //Keep track of current selected values, to enable filtering them out of suggestions
        var currentValues = [];
        $this.data('currentValues', currentValues);

        var prefetchUrl = $this.data('prefetch-url');
        var bloodhound = new Bloodhound({
            datumTokenizer: Bloodhound.tokenizers.obj.whitespace(sourceConfig.displayKey),
            queryTokenizer: Bloodhound.tokenizers.whitespace,
            prefetch: prefetchUrl ? {
                url: prefetchUrl,
                filter: sourceConfig.prefetchResponseExpression && eval("(function(response) { return " + sourceConfig.prefetchResponseExpression + ";})")
            } : null,
            remote: {
                url: sourceConfig.url,
                filter: sourceConfig.responseExpression && eval("(function(response) { return " + sourceConfig.responseExpression + ";})")
            },
            dupDetector: function(remoteMatch, localMatch) {
                return remoteMatch.id == localMatch.id;
            }
        });
        var name = $this.attr('name');
        
        $this.data('name', name);
        $this.data('valueKey', sourceConfig.valueKey);
        $this.data('labelKey', sourceConfig.displayKey);
        $this.data('bloodhound', bloodhound);
        $this.removeAttr('name');
        dataSource = {
            displayKey: sourceConfig.displayKey,
            //source: bloodhound.ttAdapter(),
            source: function(query, cb) {
                bloodhound.get(query, function (suggestions) {
                    cb(filter(suggestions, currentValues));
                });
            },
            templates: {
                empty: '&nbsp;Nothing matches your query&nbsp;'
            }
        }
        if(sourceConfig.templates) {
            for(k in sourceConfig.templates) {
                dataSource.templates[k] = _.template(sourceConfig.templates[k]);
            }
        }
        bloodhound.initialize().done((function($this) { 
            return function(e) {
                showSelectedValuesForInput.apply($this);
            }
        })($this)
        );

        var typeahead = $this.typeahead(options, dataSource);
        typeahead.on('typeahead:selected', onChange);
        typeahead.on('eventGroupChanged', onEventGroupChanged);
        typeahead.on('addPerson', onAddPerson);
    });

});
