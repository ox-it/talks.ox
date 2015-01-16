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
Scenario: Add a simple series
    go to ${add series page}
    type "something" into ${series title field}
    type "something else" into ${series description field}
    type "whenever" into ${series occurence field}
    click on ${button done}
    current page should be ${series page}

Scenario: Create Person inline
    go to ${add series page}
    type "something" into ${series title field}
    click on ${series create person}
    ${series create person name} should appear
    type "James Bond" into ${series create person name}
    type "MI5" into ${series create person bio}
    click on ${series create person submit}
    ${list group item("James Bond, MI5")} should appear
    click on ${button done}
    page should contain text "James Bond (MI5)"


*** Keywords ***
