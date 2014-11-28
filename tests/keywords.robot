*** Keywords ***
Suite setup
    Open browser  ${HOST}  browser=${BROWSER}
    Set window size  ${1024}  ${768}
    server_command  migrate

Suite teardown
    Close browser

test setup
    start server
    server_command  dumpdata  format=yaml
    create superuser  test     test
    Login as test test

test teardown
    stop server
    server_command  flush  interactive=${False}

go to ${page}
    go to  ${page.url}

type "${text}" into ${element}
    Element should be visible  ${element.locator}
    Input text  ${element.locator}  ${text}

click on ${element}
    Element should be visible  ${element.locator}
    Click element  ${element.locator} 

current page should be ${page}
    log  TODO

${element} should be displayed
    Element should be visible  ${element.locator}

${element} should not be displayed
    Element should not be visible  ${element.locator}

${element} should appear
    Wait until keyword succeeds  5s  0.2s  Element should be visible  ${element.locator}

${element} should disappear
    Wait until keyword succeeds  5s  0.2s  Element should not be visible  ${element.locator}

${element} should contain text "${text}"
    Run keyword if  ${element=='page'}  page should contain  ${text}   ELSE  Element should contain  ${element.locator}  ${text}

${element} selected item should be "${label}"
    Element should be visible  ${element.locator}
    ${v}=  get selected list label  ${element.locator}
    should be equal  ${v}  ${label}

Select current date and time for ${widget}
    ${widget} should appear
    click on ${datetimepicker current day.in_('widget')}
    click on ${datetimepicker current hour.in_('widget')}
    click on ${datetimepicker current minute.in_('widget')}

Login as ${username} ${password}
    go to ${login_page}
    type "${username}" into ${username field}
    type "${password}" into ${password field}
    click on ${button login}
