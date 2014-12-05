*** Settings ***
Documentation    Suite description
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
Scenario: edit a simple talk
    Create sample event
    go to ${edit_talk_page('${event_slug}')}
    page should contain text "Edit"
    page should contain text "${event_name}"
    capture page screenshot

Scenario: change location
    Create sample event
    go to ${edit_talk_page('${event_slug}')}
    page should contain text "Banbury"
    go to ${edit_talk_page('${event_slug}')}
    click on ${remove item('event-location')}
    page should not contain     Banbury
    click on ${button done}
    page should not contain     Banbury

Scenario: initialise with correct data
    create test data
    go to ${edit_talk_page('a-maths-talk')}
    #set up the speakers, topics etc here, rather than creating programmatically
    capture page screenshot  filename=edit_page.png
    page should contain text "Banbury Road"
    page should contain text "James Bond"
    page should contain text "Oxford Centre for Industrial and Applied Mathematics"
    page should contain text "A maths conference"
    page should contain text "Mathematics"
    page should contain text "Numbers, Ordinal"
    page should contain text "contrib.user@users.com"

Scenario: remove speaker
    create test data
    go to ${edit_talk_page('a-maths-talk')}
    click on ${remove item('event-speaker')}
    page should not contain     James Bond
    click on ${button done}
    page should not contain     James Bond

Scenario: remove topic
    create test data
    go to ${edit_talk_page('a-maths-talk')}
    click on ${remove item('event-topics')}
    #assuming 'click on' clicks on the first element found by the locator, so do it again
    click on ${remove item('event-topics')}
    capture page screenshot  filename=removed_topic.png
    page should not contain  Mathematics
    page should not contain  Numbers, Ordinal
    click on ${button done}
    page should not contain  Mathematics
    page should not contain  Numbers, Ordinal

*** Keywords ***
Create sample event
    create  event   title=${event_name}     slug=${event_slug}      description=${event_description}    location=oxpoints:40002001   department_organiser=oxpoints:23232596
