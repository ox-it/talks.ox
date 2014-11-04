$(function() {
    function getSuggestionById(mainInput, id, idKey) {
        var bloodhound = $(mainInput).data('bloodhound')
        if (!bloodhound.storage) {
            var fieldName = $(mainInput).attr('name');
            if(bloodhound.prefetch) {
                throw Error("Data not prefetched for field " + name)
            } else {
                throw Error("Prefetch config is missing for field " + name)
            }
        }
        var data = bloodhound.storage.get('data');
        for(i in data.datums) {
            if(data.datums[i][idKey] == id) {
                return data.datums[i]
            }
        }
    }
    function removeItem(e) {
        e.preventDefault()
        $(this).parents('.list-group-item').prev('input').remove()
        $(this).parents('.list-group-item').remove()
    }
    function showSelectedValue(mainInput, input, suggestion) {
        var valueKey = $(mainInput).data('valueKey');
        var labelKey = $(mainInput).data('labelKey');
        suggestion = suggestion || $(input).data('suggestion') || getSuggestionById(mainInput, $(input).prop('value'), valueKey)
        var t = _.template('<div data-id="<%= ' + valueKey + ' %>" class="list-group-item list-group-item-info fade in"><a href="#"><span class="glyphicon glyphicon-remove"></span></a><%= ' + labelKey + ' %></div>');
        var item = $(t(suggestion)).insertAfter(input);
        $('a', item).click(removeItem).click(function() { $(mainInput).show().focus().val('') })
        $(mainInput).val('')
        if(!$(mainInput).prop('multiple'))
            $(mainInput).hide();
    }
    function showSelectedValuesForInput() {
        var $this = $(this);
        var name = $(this).data('name');
        var $inputs = $('input[name="' + name + '"]', $this.parents('form'));
        $inputs.each(function() { 
            showSelectedValue($this, this) 
        });
    }
    function onChange(e, suggestion, datasetName) {
        e.preventDefault();
        e.stopPropagation();
        var value = suggestion[$(e.target).data('valueKey')];
        var name = $(e.target).data('name')
        var isMultiple = $(e.target).prop('multiple');
        var $input = $('input[name="' + name + '"]', $(e.target).parents('form'));
        $input = makeInput(e.target, name, value)
        showSelectedValue($(e.target), $input, suggestion)
    }
    function makeInput(sourceInput, name, value) {
        return $('<input>').
            insertBefore(sourceInput).
            attr('type', 'hidden').
            attr('name', name).
            attr('value', value)
    }
    $('.typeahead').each(function() {
        $this = $(this)
        options = {
            hint: true,
            highlight: true,
            minLength: 1
        }
        var sourceConfig = $this.data('source') || null;
        if(!sourceConfig) {
            throw Error("Missing data-source attribute")
        }
        var prefetchUrl = $this.data('prefetch-url')
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
            }
        });
        var name = $this.attr('name')
        var isMultiple = $this.prop('multiple');
        $this.data('name', name)
        $this.data('valueKey', sourceConfig.valueKey)
        $this.data('labelKey', sourceConfig.displayKey)
        $this.data('bloodhound', bloodhound)
        $this.removeAttr('name')
        dataSource = {
            displayKey: sourceConfig.displayKey,
            source: bloodhound.ttAdapter(),
            templates: {
                empty: '&nbsp;Nothing matches your query&nbsp;'
            }
        }
        if(sourceConfig.templates) {
            for(k in sourceConfig.templates) {
                dataSource.templates[k] = _.template(sourceConfig.templates[k])
            }
        }
        bloodhound.initialize().done((function($this) { 
            return function(e) {
                showSelectedValuesForInput.apply($this)
            }
        })($this)
        )

        $this.typeahead(options, dataSource).on('typeahead:selected', onChange)
    })
})
