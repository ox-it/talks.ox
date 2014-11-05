*** Keywords ***
Select current values for ${widget}
    ${widget} should appear
    click on ${datetimepicker current day.in_('widget')}
    click on ${datetimepicker current hour.in_('widget')}
    click on ${datetimepicker current minute.in_('widget')}
