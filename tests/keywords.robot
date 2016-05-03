*** Keywords ***
Suite setup
    Open browser  ${HOST}  browser=${BROWSER}
    Set window size  ${1024}  ${768}
    server_command  migrate

Suite teardown
    Close browser

test setup
    start server
    # use dumpdata if you want to check what is
    # in the database, disabled by default
    #server_command  dumpdata  format=yaml
    create superuser  test     test
    Login as test test

test teardown
    stop server
    server_command  flush  interactive=${False}

test edit setup
    test setup
    create test data

go to ${page}
    go to  ${page.url}

type "${text}" into ${element}
    Element should be visible  ${element.locator}
    Input text  ${element.locator}  ${text}

click on ${element}
    Element should be visible  ${element.locator}
    Click element  ${element.locator} 

current page should be ${page}
    # TODO this should use a regular expression
    # e.g. when redirecting after creating an event
    Location should contain     ${page.url}

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

${element} should not contain text "${text}"
    Run keyword if  ${element=='page'}   page should not contain  ${text}    ELSE    Element should not contain  ${element.locator}  ${text}

${element} should appear text "${text}"
    Wait until keyword succeeds     3s   0.2s    ${element} should contain text "${text}"

${element} should be present ${n} times
    Selenium2Library.Xpath Should Match X Times     ${element.locator}  ${n}

${element} selected item should be "${label}"
    Element should be visible  ${element.locator}
    ${v}=  get selected list label  ${element.locator}
    should be equal  ${v}  ${label}

Select current date and time for ${widget}
    click on ${datetimepicker current day.in_('widget')}
    click on ${body}

Login as ${username} ${password}
    go to ${login_page}
    type "${username}" into ${username field}
    type "${password}" into ${password field}
    click on ${button login}
