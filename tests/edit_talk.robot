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
    create  event   title=Geography primer      slug=geography-primer
    go to ${edit_talk_page('geography-primer')}
    page should contain text "Edit"
    page should contain text "Geography"
    capture page screenshot

*** Keywords ***
Provided precondition
    Setup system under test