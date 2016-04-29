var animationTime = 200; // ms

$(function() {
    
    var today_eleven_am = new Date();
    today_eleven_am.setHours(11);
    
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
        format: 'DD/MM/YYYY HH:mm',
        sideBySide : true,
        allowInputToggle : true,
        stepping : 5
    }).each(function(i,v){
        $(v).data("DateTimePicker").ignoreReadonly(true);
        if (typeof $('input', v).attr('value') !== 'undefined') {
			$(v).data("DateTimePicker").defaultDate(moment($('input', v).attr('value')));
		}
		else {
			
		}
    });

    $('#event-start.js-datetimepicker').on("dp.change", function(e) { 
        var date = new Date(e.date);
        var endDate = date.setHours(date.getHours()+1, date.getMinutes());
		
        $('#event-end.js-datetimepicker').data('DateTimePicker').minDate(e.date).date(moment(endDate));
    });

    //prepend a message div to the given element, containing the given text.
    // type is 'warning', 'error', 'info', 'success' as specified in Bootstrap.
    var addMessage = function($el, type, text) {
        $el.prepend($("<div class='alert alert-" + type + "'>" + text + "</div>"));
    };

    $('#create-group-button').data('successCallback', function(newGroup) {
        $('<option>').attr('value', newGroup.id).text(newGroup.title).appendTo('#id_event-group').prop('selected', true);

        //update the event's department, if the newly created group has it set
        if (newGroup.department_organiser != null) {
            updateEventDepartment(newGroup.department_organiser);
        }

        var messageEl = $('.event-group');
        //tell the user that the series was created
        addMessage(messageEl, 'success', "New series created");

        //if the push to old talks failed. Warn the user
        if(newGroup.push_to_old_talks_error) {
            addMessage(messageEl, 'warning', "Timed out connecting to old talks. The new series will not appear on the old site until it is edited again here.");
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
                        $('#id_event-department_organiser').trigger("eventDepartmentChanged", response);
                    },
                    error: function(err) {
                        console.log(err);
                    }
                })
    }

    function updateEventOrganisers(organisers) {
        if(!organisers) { return; }
        $('#id_event-organisers').trigger("eventOrganisersChanged", organisers);
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
                updateEventOrganisers([response.organisers]);
            },
            error: function(err) {
                console.log(err);
            }
        });

    })
});
