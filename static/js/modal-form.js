$(function () {
    var $modal = $('<div class="modal fade" id="form-modal" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true"><div class="modal-dialog modal-lg"><div class="modal-content"></div></div></div>');
    $(document.body).append($modal);
    var successCallback;

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
    }

    onShow = function(e) {
        var url = $(e.relatedTarget).data('url');
        successCallback = $(e.relatedTarget).data('successCallback');
        $('.modal-content', $modal).load(url, interceptForm);
    }

    $modal.on('show.bs.modal', onShow);


})
