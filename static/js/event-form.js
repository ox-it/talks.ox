var animationTime = 200; // ms

$(function() {
    // Register event to show event group forms
    $('#id_event-group-enabled').on('change', function(ev) {
        if (ev.target.checked) {
            $('#id_event-group').prop('disabled', false)
            $('.event-group').slideDown(animationTime);
        } else {
            $('.event-group').slideUp(animationTime);
            $('#id_event-group').prop('disabled', true)
        }
    });

    // Initialise datetimepicker's
    $('.js-datetimepicker').datetimepicker({
        format: 'dd/mm/yyyy hh:ii',
        autoclose: true,
    });
    $('#event-start.js-datetimepicker').on('changeDate', function(ev) {
        //set the end time to 1 hour later
        hours = ev.date.getHours();
        var date = new Date(ev.date);
        date.setHours(date.getHours()+1, date.getMinutes());
        $('#event-end.js-datetimepicker').data('datetimepicker').setDate(date);
    });

    $('#create-group-button').data('successCallback', function(newGroup) {
        $('<option>').attr('value', newGroup.id).text(newGroup.title).appendTo('#id_event-group').prop('selected', true);

        //update the event's department, if the newly created group has it set
        if (newGroup.department_organiser != null) {
            updateEventDepartment(newGroup.department_organiser);
        }
    })

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
                        bio: biofield.val()
                    },

                    success: function(response) {
                        $target.trigger("addPerson", response);
                        namefield.val("");
                        biofield.val("");
                        //clear error classes
                        setErrorStateForInput($control, 'name', false);
                        setErrorStateForInput($control, 'bio', false);
                        //clear and hide error message
                        $errorMessage.addClass("hidden");
                    },
                    error: function(response) {
                        setErrorStateForInput($control, 'name', false);
                        setErrorStateForInput($control, 'bio', false)
                        for(key in response.responseJSON) {
                            setErrorStateForInput($control, key, true)
                        }
                        $errorMessage.removeClass("hidden");
                        $errorMessage.html("Missing required field");
                    }
                }
            );
        })
    });

    function setErrorStateForInput(control, id, on) {
        var el = control.find("#id_"+id).parent().parent();
        if(on) {
            el.addClass("has-error");
        }
        else {
            el.removeClass("has-error");
        }
    }

    function updateEventDepartment(location_id) {
        if(!location_id) { return; }
        $.ajax({
                    type:'GET',
                    url: '//api.m.ox.ac.uk/places/' + location_id,
                    success: function(response) {
                        $('#id_event-department_organiser').trigger("eventGroupChanged", response);
                    },
                    error: function(err) {
                        console.log(err);
                    }
                })
    }

    //On picking a new event group, retrieve the information and set the value of the department organiser field
    $('#id_event-group').change( function() {
        var groupID = this.value;
        if(!groupID) {
            //User has probably selected the 'Please select' option
            return;
        }
        var url = '/api/series/id/' + groupID

        //retrieve the ID of the event organiser and apply that to the department field of the form
        $.ajax({
            type: 'GET',
            url: url,
            success: function(response) {
                //retrieve the name of the location in question
                updateEventDepartment(response.department_organiser);
            },
            error: function(err) {
                console.log(err);
            }
        });

    })
});
