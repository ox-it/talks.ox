*** Settings ***
Library  fixtures
Library  Selenium2Library
Library  server
Resource  keywords.robot
Variables  pages.py
Suite Setup  suite setup
Suite teardown  suite teardown
Test Setup  test setup
Test teardown  test teardown

*** Test Cases ***
Scenario: Add the simplest talk
    go to ${add_talk_page}
    type "something" into ${title field}
    type "something else" into ${abstract field}
    click on ${button done}
    current page should be ${talk page}
    ${success message} should be displayed
    ${success message} should contain text "New event has been created"
    page should contain text "something"
    page should contain text "something else"

Scenario: Add talk to existing group of talks
    create  event group  title=foo

    go to ${add_talk_page}
    type "something" into ${title field}
    ${group field} should not be displayed
    click on ${checkbox in group section}
    ${group field} should be displayed
    ${create group button} should be displayed
    Select from list  ${group field.locator}  foo
    click on ${button done}
    ${success message} should be displayed
    ${success message} should contain text "New event has been created"
    page should contain text "something"
    page should contain text "Part of: foo" 

Scenario: Title not announced
    go to ${add talk page}
    click on ${button done}
    current page should be ${add talk page}
    ${error message[0]} should be displayed
    ${error message[1]} should be displayed
    ${error message[0]} should contain text "Please correct errors below"
    ${error message[1]} should contain text "Either provide title or mark it as not announced"

Scenario: Create new group on the go
    go to ${add_talk_page}
    type "something" into ${field('Title')}
    ${group field} should not be displayed
    click on ${checkbox in group section}
    ${group field} should be displayed
    ${group field} selected item should be "-- select a group --"
    ${create group button} should be displayed
    click on ${create group button}
    ${modal dialog} should appear
    ${modal dialog title} should contain text "Add a new event group"
    type "new group" into ${modal dialog field('Title')}
    type "group description" into ${modal dialog field('Description')}
    click on ${modal dialog submit button}
    ${modal dialog} should disappear
    ${group field} selected item should be "new group"

Scenario: Lookup venue
    go to ${add_talk_page}
    type "oucs" into ${venue field}
    ${suggestion popup} should appear
    ${suggestion popup} should contain text "Banbury Road"

Scenario: Lookup department
    [Tags]  todo
Scenario: Lookup topic
    [Tags]  todo
Scenario: Lookup speaker
    create  person  name=James Bond
    go to ${add_talk_page}
    type "bon" into ${speaker field}
    ${suggestion list} should appear
    ${suggestion list} should contain text "James Bond"
    click on ${suggested item('James Bond')}

Scenario: Create speaker on the go
    [Tags]  todo
Scenario: Save and add another
    [Tags]  todo
Scenario: Preserve form data after validation
    [Tags]  todo

