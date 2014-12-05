*** Settings ***
Documentation    Suite description
Library  fixtures
Library  Selenium2Library
Library  server
Resource  keywords.robot
Variables  pages.py
Variables  events.py
Suite Setup  suite setup
Suite teardown  suite teardown
Test Setup  test edit setup
Test teardown  test teardown

*** Test Cases ***
Scenario: edit a simple talk
    go to ${edit_talk_page('${event2_slug}')}
    page should contain text "Edit"
    page should contain text "${event2_title}"

Scenario: change location
    go to ${edit_talk_page('${event2_slug}')}
    page should contain text "Banbury"
    click on ${remove item('event-location')}
    page should not contain text "Banbury"
    click on ${button done}
    page should not contain text "Banbury"

Scenario: initialise with correct data
    go to ${edit_talk_page('a-maths-talk')}
    #set up the speakers, topics etc here, rather than creating programmatically
    page should contain text "Banbury Road"
    page should contain text "James Bond"
    page should contain text "Oxford Centre for Industrial and Applied Mathematics"
    page should contain text "A maths conference"
    page should contain text "Mathematics"
    page should contain text "Numbers, Ordinal"
    page should contain text "contrib.user@users.com"

Scenario: remove speaker
    go to ${edit_talk_page('a-maths-talk')}
    page should contain text "James Bond"
    click on ${remove item('event-speaker')}
    page should not contain text "James Bond"
    click on ${button done}
    page should not contain text "James Bond"

Scenario: remove topic
    go to ${edit_talk_page('a-maths-talk')}
    page should contain text "Mathematics"
    page should contain text "Numbers, Ordinal"
    click on ${remove item('event-topics')}
    #assuming 'click on' clicks on the first element found by the locator, so do it again
    click on ${remove item('event-topics')}
    page should not contain text "Mathematics"
    page should not contain text "Numbers, Ordinal"
    click on ${button done}
    page should not contain text "Mathematics"
    page should not contain text "Numbers, Ordinal"
