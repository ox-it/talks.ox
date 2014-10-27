$(function() {
    var $modal = $('<div class="modal fade" id="form-modal" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true"><div class="modal-dialog modal-lg"><div class="modal-content"></div></div></div>');
    $(document.body).append($modal)
    
    onComplete = function(jqXHR) {
        hideThrobber()
        if(jqXHR.status == 200 || jqXHR.status == 201)  {
            $modal.modal('hide')
        } else {
            $('.modal-content', $modal).html(jqXHR.responseText)
            interceptForm.call($modal)
        }
    }
    showThrobber = function() { $modal.addClass('throbber'); }
    hideThrobber = function() { $modal.removeClass('throbber'); }
    submitForm = function(e) {
        e.preventDefault()
        showThrobber()
        $.ajax({
            method: 'POST',
            url: $(this).prop('action'), 
            data: $(this).serialize(), 
            complete: onComplete,
        })
    }
    
    interceptForm = function(e) {
        $('form', this).on('submit', submitForm)
    }

    onShow = function(e) {
        var url = $(e.relatedTarget).data('url')
        $('.modal-content', $modal).load(url, interceptForm)
    }

    $modal.on('show.bs.modal', onShow)


})
