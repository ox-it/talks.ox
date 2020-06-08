$(function () {
    var $modal = $('<div class="modal fade" id="form-modal" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true"><div class="modal-dialog modal-lg"><div class="modal-content"></div></div></div>');
    $(document.body).append($modal);
    var successCallback;

    setErrorStateForInput = function (control, id, on) {
        var el = control.find("#id_"+id).parent().parent();
        if(on) {
            el.addClass("has-error");
        }
        else {
            el.removeClass("has-error");
        }
    }

    onComplete = function (jqXHR, statusText) {
        hideThrobber();
        if (jqXHR.status === 200 || jqXHR.status === 201) {
            $modal.modal('hide');
            if (successCallback && jqXHR.responseJSON) {
                successCallback(jqXHR.responseJSON);
            }
        } else {
            if (jqXHR.status > 0 ) {
                $('.modal-content', $modal).html(jqXHR.responseText);
                interceptForm.call($modal);
            } else {
                $('.modal-body', $modal).prepend($('<div class="alert alert-danger">Network error...</div>'));
            }
        }
    }
    showThrobber = function() { $modal.addClass('throbber'); }
    hideThrobber = function() { $modal.removeClass('throbber'); }
    submitForm = function(e) {
        e.preventDefault();
        showThrobber();
        $.ajax({
            method: 'POST',
            url: $(this).prop('action'), 
            data: $(this).serialize(), 
            complete: onComplete,
        })
    }
    
    interceptForm = function(e) {
        $('form', this).on('submit', submitForm);
	$('.js-create-person-control').each( function() {
            //reveal the form panel on clicking the reveal link
            $(this).find('.js-create-person').on('click', function(ev) {
                ev.preventDefault();
                var $control = $(ev.target).parent().parent();
                $control.find('.js-person-panel').slideDown(animationTime);
            })

            //capture the click on 'Add' and update the relevant control
            $(this).find('.js-submit-person').on('click', function(ev) {
                var $control = $(ev.target).parent().parent();

                var namefield = $control.find('#id_name');
                var biofield = $control.find('#id_bio');
                var webaddressfield = $control.find('#id_web_address')
                var csrftoken = $.cookie('csrftoken');
                var $errorMessage = $control.find('.js-person-form-errors');
                var target = $(this).attr('data-input-target');
                var $target = $(target);
                $.ajax({
                        type: 'POST',
                        url: '/api/persons/new',
                        headers: {
                            "X-CSRFToken": csrftoken,
                        },
                        data: {
                            name: namefield.val(),
                            bio: biofield.val(),
                            web_address: webaddressfield.val()
                        },

                        success: function(response) {
                            $target.trigger("addPerson", response);
                            namefield.val("");
                            biofield.val("");
                            webaddressfield.val("");
                            //clear error classes
                            setErrorStateForInput($control, 'name', false);
                            setErrorStateForInput($control, 'bio', false);
                            setErrorStateForInput($control, 'web_address', false);
                            //clear and hide error message
                            $errorMessage.addClass("hidden");
                        },
                        error: function(response) {
                            setErrorStateForInput($control, 'name', false);
                            setErrorStateForInput($control, 'bio', false)
                            setErrorStateForInput($control, 'web_address', false);
                            for(var key in response.responseJSON) {
                                setErrorStateForInput($control, key, true)
                            }
                            $errorMessage.removeClass("hidden");
                            $errorMessage.html("Missing required field");
                        }
                    }
                );
            })
        });
    }

    onShow = function(e) {
        var url = $(e.relatedTarget).data('url');
        successCallback = $(e.relatedTarget).data('successCallback');
        $('.modal-content', $modal).load(url, interceptForm);
    }

    $modal.on('show.bs.modal', onShow);

})
