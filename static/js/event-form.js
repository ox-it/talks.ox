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
    $('#id_event-start.js-datetimepicker').on('changeDate', function(ev) {
        //set the end time to 1 hour later
        hours = ev.date.getHours();
        var date = new Date(ev.date);
        date.setHours(date.getHours()+1, date.getMinutes());
        $('#id_event-end.js-datetimepicker').data('datetimepicker').setDate(date);
    });


    //// Set the default end-date to the start date when it is picked
    //var startDateTimePicker = $('.js-datetimepicker.event-start');
    //startDateTimePicker.datetimepicker().on('changeDate', function(ev){
    //    utcDate = startDateTimePicker.datetimepicker('getUTCDate');
    //    // Set the StartDate to the current DAY -- don't specify hours
    //    //
    //    // Seems like the hours on start dates can cause some TZ issues
    //    $('.js-datetimepicker.event-end').datetimepicker('setStartDate',
    //        new Date(utcDate.getFullYear(), utcDate.getMonth(), utcDate.getDate())
    //    );
    //});

    $('.js-open-calendar').on('click', function(ev) {
        $(ev.target).parent().siblings('.js-datetimepicker').datetimepicker('show');
    });

    $('#create-group-button').data('successCallback', function(newGroup) {
        $('<option>').attr('value', newGroup.id).text(newGroup.title).appendTo('#id_event-group').prop('selected', true);

        //update the event's department, if the newly created group has it set
        if (newGroup.department_organiser != null) {
            updateEventDepartment(newGroup.department_organiser);
        }
    })

    $('#create-person-button').data('successCallback', function(newPerson) {
        $('#id_event-speakers').trigger("addSpeaker", newPerson);
    })

    //reveal the speaker quick-add form on clicking the link
    $('.js-create-speaker').on('click', function(ev) {
       ev.preventDefault();
        $('.js-speaker-panel').slideDown(animationTime);
    });

    //add the speaker
    $('.js-submit-speaker').on('click', function(ev) {
        var namefield = $('#id_name');
        var emailfield = $('#id_email_address');
        var csrftoken = $.cookie('csrftoken');
        $.ajax({
                type: 'POST',
                url: '/api/persons/new',
                headers: {
                    "X-CSRFToken": csrftoken,
                },
                data: {
                    name: namefield.val(),
                    email_address: emailfield.val()
                },

                success: function(response) {
                    $('#id_event-speakers').trigger("addSpeaker", response);
                    namefield.val("");
                    emailfield.val("");
                },
                error: function(response) {
                    //todo explain any form errors to the user
                    console.log(response);
                }
            }
        );
    });

    function updateEventDepartment(location_id) {
        $.ajax({
                    type:'GET',
                    url: 'http://api.m.ox.ac.uk/places/' + location_id,
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
        var url = '/api/eventgroups/id/' + groupID

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
