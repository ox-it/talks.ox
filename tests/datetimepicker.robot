*** Keywords ***
Datetimepicker current values
    click on ${modal datetime active day}
    ${modal datetime active hour} should appear
    click on ${modal datetime active hour}
    ${modal datetime active minute} should appear
    click on ${modal datetime active minute}
